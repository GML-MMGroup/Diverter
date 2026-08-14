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


def load_prepared_run(
    metadata_path: Path, expected: dict[str, Any]
) -> tuple[dict[str, Any], Path]:
    if not metadata_path.is_file():
        raise ValueError(f"prepared metadata not found: {metadata_path}")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if not isinstance(metadata, dict):
        raise ValueError("prepared metadata must be a JSON object")
    for key, value in expected.items():
        if metadata.get(key) != value:
            raise ValueError(f"prepared metadata mismatch: {key}")
    installed_path_value = metadata.get("installed_path")
    if not isinstance(installed_path_value, str):
        raise ValueError("prepared metadata omitted installed_path")
    installed_path = Path(installed_path_value)
    if not installed_path.is_dir():
        raise ValueError("prepared installed plugin path is missing")
    return metadata, installed_path


def require_prepared_freshness(codex_home: Path, evidence: Path) -> None:
    if any((codex_home / "sessions").glob("**/*.jsonl")):
        raise ValueError("prepared Codex home already contains lifecycle sessions")
    setup_files = {
        "01-marketplace.json",
        "02-plugin-install.json",
        "03-role-install.json",
        "04-policy.json",
        "run-metadata.json",
    }
    unexpected = [
        path
        for path in evidence.rglob("*")
        if path.is_file() and path.name not in setup_files
    ]
    if unexpected:
        raise ValueError("prepared evidence directory contains prior execution output")


def snapshot(workspace: Path) -> dict[str, str]:
    hashes = {}
    for path in sorted(workspace.rglob("*")):
        if not path.is_file() or ".git" in path.relative_to(workspace).parts:
            continue
        relative = path.relative_to(workspace).as_posix()
        hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def stable_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def runtime_hash(codex_home: Path, installed_path: Path) -> str:
    files: dict[str, str] = {}
    for label, root in (("plugin", installed_path), ("agents", codex_home / "agents")):
        for path in sorted(root.rglob("*")):
            if path.is_file():
                files[f"{label}/{path.relative_to(root).as_posix()}"] = hashlib.sha256(
                    path.read_bytes()
                ).hexdigest()
    for label, path in (
        ("policy", codex_home / "diverter" / "config.json"),
        (
            "marketplace",
            codex_home
            / "local-marketplace"
            / ".agents"
            / "plugins"
            / "marketplace.json",
        ),
    ):
        if not path.is_file():
            raise ValueError(f"prepared runtime file is missing: {path}")
        files[label] = hashlib.sha256(path.read_bytes()).hexdigest()
    files["plugin-config"] = hashlib.sha256(
        (codex_home / "config.toml").read_bytes()
    ).hexdigest()
    return stable_hash(files)


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


def read_codex_version(env: dict[str, str]) -> str:
    return subprocess.run(
        ["codex", "--version"],
        env=env,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()


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
    ]
    if len(children) > 1:
        raise ValueError("expected exactly one native child session")
    if not children:
        return root_path, None, root_meta, None
    child_path, child_meta = children[0]
    if expected_role is not None and child_role(child_meta) != expected_role:
        raise ValueError(f"unexpected child role: {child_role(child_meta)}")
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
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--prepare-only", action="store_true")
    mode.add_argument("--run-prepared", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        workspace = args.workspace.resolve()
        codex_home = args.codex_home.resolve()
        evidence = args.evidence_dir.resolve()
        initial_snapshot = snapshot(workspace) if workspace.is_dir() else {}
        if not workspace.is_dir() or not initial_snapshot:
            raise ValueError("workspace must be a non-empty directory")
        if codex_home.is_relative_to(workspace) or evidence.is_relative_to(workspace):
            raise ValueError("codex home and evidence directory must be outside the workspace")
        prompt = args.prompt_file.read_text(encoding="utf-8").strip()
        if not prompt:
            raise ValueError("prompt file must not be empty")
        resume_prompt = None
        if args.resume_prompt_file:
            resume_prompt = args.resume_prompt_file.read_text(encoding="utf-8").strip()
            if not resume_prompt:
                raise ValueError("resume prompt file must not be empty")
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
        fixture_hash = hashlib.sha256(
            json.dumps(initial_snapshot, sort_keys=True).encode("utf-8")
        ).hexdigest()
        contract_hash = stable_hash(
            {
                "prompt": prompt,
                "resume_prompt": resume_prompt,
                "expected_role": args.expected_role,
                "policy": args.policy,
                "model": args.model,
                "reasoning_effort": args.reasoning_effort,
                "scenario": args.scenario,
                "require_followup": args.require_followup,
                "root_progress_scope": args.root_progress_scope,
                "verification_scope": args.verification_scope,
                "root_write_scope": args.root_write_scope,
                "child_write_scope": args.child_write_scope,
                "failure_report_marker": args.failure_report_marker,
            }
        )
        if args.run_prepared:
            current_codex_version = read_codex_version(env)
            require_prepared_freshness(codex_home, evidence)
            metadata, installed_path = load_prepared_run(
                evidence / "run-metadata.json",
                {
                    "plugin_revision": revision,
                    "policy": args.policy,
                    "scenario": args.scenario,
                    "root_model": args.model,
                    "root_reasoning_effort": args.reasoning_effort,
                    "workspace_fixture_hash": fixture_hash,
                    "run_contract_hash": contract_hash,
                    "codex_version": current_codex_version,
                    "installed_roles": sorted(
                        path.stem for path in (codex_home / "agents").glob("*.toml")
                    ),
                },
            )
            if not installed_path.resolve().is_relative_to(codex_home):
                raise ValueError("prepared installed plugin path is outside Codex home")
            if metadata.get("runtime_hash") != runtime_hash(codex_home, installed_path):
                raise ValueError("prepared runtime hash mismatch")
            codex_version = current_codex_version
        else:
            require_empty(codex_home, "Codex home")
            require_empty(evidence, "evidence directory")
            current_codex_version = read_codex_version(env)
            codex_version = current_codex_version
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
            "codex_version": codex_version,
            "installed_path": str(installed_path),
            "installed_roles": sorted(
                path.stem for path in (codex_home / "agents").glob("*.toml")
            ),
            "policy": args.policy,
            "scenario": args.scenario,
            "root_model": args.model,
            "root_reasoning_effort": args.reasoning_effort,
            "workspace_fixture_hash": fixture_hash,
            "run_contract_hash": contract_hash,
            "runtime_hash": runtime_hash(codex_home, installed_path),
        }
        if args.prepare_only:
            (evidence / "run-metadata.json").write_text(
                json.dumps(metadata, indent=2), encoding="utf-8"
            )
            print(json.dumps({"ok": True, "prepared": True, **metadata}, sort_keys=True))
            return 0

        before = initial_snapshot
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
        if resume_prompt is not None:
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
                    "--config",
                    f'model_reasoning_effort="{args.reasoning_effort}"',
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
            "--expected-root-model",
            args.model,
            "--expected-root-effort",
            args.reasoning_effort,
        ]
        if child_copy or args.scenario == "failure":
            verifier.extend(
                [
                    "--expected-role",
                    args.expected_role,
                    "--verification-scope",
                    args.verification_scope or "",
                ]
            )
            if child_copy:
                verifier.extend(["--child-rollout", str(child_copy)])
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
                "observed_root_models": report.get("root_models"),
                "observed_root_reasoning_efforts": report.get("root_reasoning_efforts"),
                "observed_child_model": report.get("child_model"),
                "observed_child_reasoning_effort": report.get("child_reasoning_effort"),
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
