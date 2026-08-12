#!/usr/bin/env python3
"""Run one real, isolated Diverter native-lifecycle evaluation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "scripts" / "verify-native-lifecycle.py"


def require_empty(path: Path, label: str) -> None:
    if path.exists() and any(path.iterdir()):
        raise ValueError(f"{label} must be absent or empty: {path}")
    path.mkdir(parents=True, exist_ok=True)


def snapshot(workspace: Path) -> dict[str, str]:
    hashes = {}
    for path in sorted(workspace.rglob("*")):
        if not path.is_file() or ".git" in path.relative_to(workspace).parts:
            continue
        relative = path.relative_to(workspace).as_posix()
        hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def run_logged(
    command: list[str], env: dict[str, str], log_path: Path
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, text=True, capture_output=True, env=env)
    log_path.write_text(
        json.dumps(
            {
                "argv": command,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    if result.returncode:
        raise RuntimeError(f"command failed; see {log_path}")
    return result


def json_stdout(result: subprocess.CompletedProcess[str], label: str) -> dict[str, Any]:
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise ValueError(f"{label} did not return JSON") from error
    if not isinstance(data, dict):
        raise ValueError(f"{label} did not return a JSON object")
    return data


def first_session_meta(path: Path) -> dict[str, Any] | None:
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("type") == "session_meta" and isinstance(record.get("payload"), dict):
            return record["payload"]
    return None


def child_role(meta: dict[str, Any]) -> str | None:
    source = meta.get("source")
    if not isinstance(source, dict):
        return None
    subagent = source.get("subagent")
    if not isinstance(subagent, dict):
        return None
    spawn = subagent.get("thread_spawn")
    return spawn.get("agent_role") if isinstance(spawn, dict) else None


def discover_rollouts(
    codex_home: Path, expected_role: str | None
) -> tuple[Path, Path | None, dict[str, Any], dict[str, Any] | None]:
    candidates = []
    for path in codex_home.glob("sessions/**/*.jsonl"):
        meta = first_session_meta(path)
        if meta:
            candidates.append((path, meta))
    roots = [(path, meta) for path, meta in candidates if child_role(meta) is None]
    if not roots:
        raise ValueError("no persisted Root rollout found")
    root_path, root_meta = max(roots, key=lambda item: item[0].stat().st_mtime_ns)
    root_ids = {root_meta.get("id"), root_meta.get("session_id")}
    children = [
        (path, meta)
        for path, meta in candidates
        if meta.get("parent_thread_id") in root_ids
        and (expected_role is None or child_role(meta) == expected_role)
    ]
    if not children:
        return root_path, None, root_meta, None
    child_path, child_meta = max(children, key=lambda item: item[0].stat().st_mtime_ns)
    return root_path, child_path, root_meta, child_meta


def write_local_marketplace(directory: Path, revision: str) -> Path:
    marketplace = directory / "local-marketplace"
    manifest = marketplace / ".agents" / "plugins" / "marketplace.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(
        json.dumps(
            {
                "name": "diverter-lifecycle-eval",
                "plugins": [
                    {
                        "name": "diverter",
                        "source": {
                            "source": "url",
                            "url": ROOT.as_uri(),
                            "ref": revision,
                        },
                        "policy": {
                            "installation": "AVAILABLE",
                            "authentication": "ON_INSTALL",
                        },
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return marketplace


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install the current revision into a clean home and run one real native lifecycle scenario."
    )
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--prompt-file", type=Path, required=True)
    parser.add_argument("--resume-prompt-file", type=Path)
    parser.add_argument("--codex-home", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--expected-role")
    parser.add_argument("--policy", choices=("auto", "ask"), required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--reasoning-effort", default="high")
    parser.add_argument(
        "--scenario",
        choices=("normal", "failure", "ask-refused", "native-absence", "missing-role"),
        default="normal",
    )
    parser.add_argument("--require-followup", action="store_true")
    parser.add_argument("--root-progress-scope", required=True)
    parser.add_argument("--verification-scope")
    parser.add_argument("--root-write-scope")
    parser.add_argument("--child-write-scope")
    parser.add_argument("--failure-report-marker", default="Affected Child Lane")
    parser.add_argument("--prepare-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        workspace = args.workspace.resolve()
        codex_home = args.codex_home.resolve()
        evidence = args.evidence_dir.resolve()
        if not workspace.is_dir() or not snapshot(workspace):
            raise ValueError("workspace must be a non-empty directory")
        if codex_home.is_relative_to(workspace) or evidence.is_relative_to(workspace):
            raise ValueError("codex home and evidence directory must be outside the workspace")
        require_empty(codex_home, "Codex home")
        require_empty(evidence, "evidence directory")
        prompt = args.prompt_file.read_text(encoding="utf-8").strip()
        if not prompt:
            raise ValueError("prompt file must not be empty")
        if not args.expected_role:
            raise ValueError("--expected-role is required for the controlled role matrix")

        env = os.environ.copy()
        env["CODEX_HOME"] = str(codex_home)
        revision = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
        marketplace = write_local_marketplace(codex_home, revision)
        add_marketplace = run_logged(
            ["codex", "plugin", "marketplace", "add", str(marketplace), "--json"],
            env,
            evidence / "01-marketplace.json",
        )
        marketplace_data = json_stdout(add_marketplace, "marketplace add")
        marketplace_name = marketplace_data.get("marketplaceName")
        if not isinstance(marketplace_name, str):
            raise ValueError("marketplace add omitted marketplaceName")
        add_plugin = run_logged(
            ["codex", "plugin", "add", f"diverter@{marketplace_name}", "--json"],
            env,
            evidence / "02-plugin-install.json",
        )
        plugin_data = json_stdout(add_plugin, "plugin add")
        installed_path_value = plugin_data.get("installedPath")
        if not isinstance(installed_path_value, str):
            raise ValueError("plugin add omitted installedPath")
        installed_path = Path(installed_path_value)

        if args.scenario != "missing-role":
            run_logged(
                [
                    sys.executable,
                    str(installed_path / "scripts" / "install-agent-roles.py"),
                    "--overwrite",
                    "--role",
                    args.expected_role,
                ],
                env,
                evidence / "03-role-install.json",
            )
        run_logged(
            [
                sys.executable,
                str(installed_path / "scripts" / "diverter-mode.py"),
                args.policy,
            ],
            env,
            evidence / "04-policy.json",
        )
        metadata = {
            "plugin_revision": revision,
            "installed_path": str(installed_path),
            "policy": args.policy,
            "scenario": args.scenario,
            "root_model": args.model,
            "root_reasoning_effort": args.reasoning_effort,
        }
        if args.prepare_only:
            (evidence / "run-metadata.json").write_text(
                json.dumps(metadata, indent=2), encoding="utf-8"
            )
            print(json.dumps({"ok": True, "prepared": True, **metadata}, sort_keys=True))
            return 0

        before = snapshot(workspace)
        codex_command = [
            "codex",
            "exec",
            "--json",
            "--dangerously-bypass-hook-trust",
            "--skip-git-repo-check",
            "--sandbox",
            "workspace-write",
            "--cd",
            str(workspace),
            "--model",
            args.model,
            "--config",
            f'model_reasoning_effort="{args.reasoning_effort}"',
        ]
        if args.scenario == "native-absence":
            codex_command.extend(["--disable", "multi_agent", "--disable", "multi_agent_v2"])
        codex_command.append(prompt)
        run_logged(codex_command, env, evidence / "05-root-exec.json")

        root_path, child_path, root_meta, child_meta = discover_rollouts(
            codex_home, args.expected_role
        )
        if args.resume_prompt_file:
            resume_prompt = args.resume_prompt_file.read_text(encoding="utf-8").strip()
            if not resume_prompt:
                raise ValueError("resume prompt file must not be empty")
            session_id = root_meta.get("session_id", root_meta.get("id"))
            if not isinstance(session_id, str):
                raise ValueError("Root rollout omitted session identity")
            run_logged(
                [
                    "codex",
                    "exec",
                    "resume",
                    "--json",
                    "--dangerously-bypass-hook-trust",
                    "--model",
                    args.model,
                    session_id,
                    resume_prompt,
                ],
                env,
                evidence / "06-root-resume.json",
            )
            root_path, child_path, root_meta, child_meta = discover_rollouts(
                codex_home, args.expected_role
            )

        manifest_path = evidence / "ownership-manifest.json"
        manifest_path.write_text(
            json.dumps({"before": before, "after": snapshot(workspace)}, indent=2),
            encoding="utf-8",
        )
        root_copy = evidence / "root-rollout.jsonl"
        shutil.copy2(root_path, root_copy)
        child_copy = None
        if child_path:
            child_copy = evidence / "child-rollout.jsonl"
            shutil.copy2(child_path, child_copy)

        verifier = [
            sys.executable,
            str(VERIFIER),
            "--root-rollout",
            str(root_copy),
            "--scenario",
            args.scenario,
            "--root-progress-scope",
            args.root_progress_scope,
        ]
        if child_copy:
            verifier.extend(
                [
                    "--child-rollout",
                    str(child_copy),
                    "--expected-role",
                    args.expected_role,
                    "--verification-scope",
                    args.verification_scope or "",
                ]
            )
            if args.policy == "auto":
                verifier.extend(["--policy", "auto"])
            elif args.scenario == "normal":
                verifier.extend(["--policy", "ask-approved"])
        if args.require_followup:
            verifier.append("--require-followup")
        if args.root_write_scope or args.child_write_scope:
            verifier.extend(
                [
                    "--root-write-scope",
                    args.root_write_scope or "",
                    "--child-write-scope",
                    args.child_write_scope or "",
                    "--ownership-manifest",
                    str(manifest_path),
                ]
            )
        if args.scenario == "failure":
            verifier.extend(["--failure-report-marker", args.failure_report_marker])
        verification = run_logged(verifier, env, evidence / "07-verifier.json")
        report = json_stdout(verification, "lifecycle verifier")
        metadata.update(
            {
                "root_session_id": root_meta.get("session_id", root_meta.get("id")),
                "child_session_id": child_meta.get("id") if child_meta else None,
                "verifier_ok": report.get("ok"),
            }
        )
        (evidence / "run-metadata.json").write_text(
            json.dumps(metadata, indent=2), encoding="utf-8"
        )
        print(json.dumps({"ok": True, **metadata}, sort_keys=True))
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
