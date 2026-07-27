import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PluginContractTest(unittest.TestCase):
    def test_mode_control_is_explicit_only_and_uses_the_mode_cli(self) -> None:
        skill_dir = ROOT / "skills" / "diverter-mode"
        skill = (skill_dir / "SKILL.md").read_text()
        metadata = (skill_dir / "agents" / "openai.yaml").read_text()

        self.assertIn("allow_implicit_invocation: false", metadata)
        self.assertIn("scripts/diverter-mode.py", skill)
        self.assertIn("`auto`", skill)
        self.assertIn("`ask`", skill)
        self.assertIn("`status`", skill)
        self.assertIn("Diverter mode changed to", skill)
        self.assertIn("Restart or reopen the task", skill)
        self.assertIn("Never invoke `$diverter`", skill)

    def test_session_start_loads_persisted_delegation_policy(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            codex_home = Path(temp_dir) / "codex-home"
            config = codex_home / "diverter" / "config.json"
            config.parent.mkdir(parents=True)
            config.write_text('{"delegation_policy": "auto"}\n')

            result = subprocess.run(
                [sys.executable, ROOT / "hooks" / "session_start.py"],
                input='{"source":"startup"}',
                env={**os.environ, "CODEX_HOME": str(codex_home)},
                text=True,
                capture_output=True,
                check=True,
            )

            self.assertIn("## Diverter Delegation Gate", result.stdout)
            self.assertIn("delegation_policy: auto", result.stdout)
            self.assertIn("$diverter-mode", result.stdout)

    def test_session_start_expands_tilde_in_codex_home(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir) / "home"
            config = home / "hook-home" / "diverter" / "config.json"
            config.parent.mkdir(parents=True)
            config.write_text('{"delegation_policy": "auto"}\n')

            result = subprocess.run(
                [sys.executable, ROOT / "hooks" / "session_start.py"],
                env={**os.environ, "HOME": str(home), "CODEX_HOME": "~/hook-home"},
                cwd=temp_dir,
                text=True,
                capture_output=True,
                check=True,
            )

            self.assertIn("delegation_policy: auto", result.stdout)

    def test_session_start_falls_back_to_ask_for_missing_or_invalid_config(self) -> None:
        for invalid_content in (None, "not json\n", '{"delegation_policy":"fast"}\n'):
            with (
                self.subTest(invalid_content=invalid_content),
                tempfile.TemporaryDirectory() as temp_dir,
            ):
                codex_home = Path(temp_dir) / "codex-home"
                if invalid_content is not None:
                    config = codex_home / "diverter" / "config.json"
                    config.parent.mkdir(parents=True)
                    config.write_text(invalid_content)

                result = subprocess.run(
                    [sys.executable, ROOT / "hooks" / "session_start.py"],
                    input='{"source":"compact"}',
                    env={**os.environ, "CODEX_HOME": str(codex_home)},
                    text=True,
                    capture_output=True,
                    check=True,
                )

                self.assertIn("delegation_policy: ask", result.stdout)

    def test_session_start_defers_to_native_before_triggering_diverter(self) -> None:
        result = subprocess.run(
            [sys.executable, ROOT / "hooks" / "session_start.py"],
            text=True,
            capture_output=True,
            check=True,
        )

        native_stop = result.stdout.index("proactive multi-agent delegation is active")
        trigger = result.stdout.index("invoke `$diverter` first")
        self.assertLess(native_stop, trigger)
        self.assertIn("Do not invoke or mention Diverter", result.stdout)

    def test_session_start_exposes_coarse_eligibility_and_sanitized_failures(
        self,
    ) -> None:
        result = subprocess.run(
            [sys.executable, ROOT / "hooks" / "session_start.py"],
            text=True,
            capture_output=True,
            check=True,
        )

        gate = result.stdout
        self.assertIn("at least two separable work or evidence lanes", gate)
        self.assertIn("one concrete high-risk specialist boundary", gate)
        self.assertIn("explicit request to use subagents", gate)
        self.assertIn("explicitly selected focused skill", gate)
        self.assertIn("Sanitized Failure Reporting", gate)
        self.assertIn("internal failure recovers successfully", gate)
        self.assertIn("continuing in the main thread", gate)
        self.assertIn("ask whether to continue in the main thread", gate)
        for internal_detail in (
            "skill aliases",
            "plugin cache paths",
            "`SKILL.md` loading",
            "retry steps",
        ):
            self.assertIn(internal_detail, gate)

    def test_plugin_package_and_session_start_hook_are_discoverable(self) -> None:
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text())
        marketplace = json.loads(
            (ROOT / ".agents" / "plugins" / "marketplace.json").read_text()
        )
        hooks = json.loads((ROOT / "hooks" / "hooks.json").read_text())

        self.assertEqual(manifest["name"], "diverter")
        self.assertEqual(manifest["version"], "0.3.1")
        self.assertEqual(manifest["interface"]["displayName"], "Diverter")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertNotIn("hooks", manifest)

        self.assertEqual(marketplace["name"], "diverter")
        self.assertEqual(marketplace["interface"]["displayName"], "Diverter")
        entry = marketplace["plugins"]
        self.assertEqual(len(entry), 1)
        self.assertEqual(entry[0]["name"], "diverter")
        self.assertEqual(entry[0]["source"]["source"], "url")
        self.assertEqual(
            entry[0]["source"]["url"],
            "https://github.com/GML-MMGroup/Diverter.git",
        )
        self.assertEqual(entry[0]["source"]["ref"], "main")
        self.assertEqual(entry[0]["policy"]["installation"], "AVAILABLE")
        self.assertEqual(entry[0]["policy"]["authentication"], "ON_INSTALL")

        self.assertEqual(set(hooks["hooks"]), {"SessionStart"})
        group = hooks["hooks"]["SessionStart"][0]
        self.assertEqual(group["matcher"], "startup|resume|clear|compact")
        handler = group["hooks"][0]
        self.assertEqual(handler["type"], "command")
        self.assertIn("${PLUGIN_ROOT}/hooks/session_start.py", handler["command"])
        self.assertIn("$env:PLUGIN_ROOT", handler["commandWindows"])
        self.assertEqual(handler["timeout"], 5)
        self.assertEqual(handler["statusMessage"], "Loading Diverter Delegation Gate...")

        result = subprocess.run(
            [sys.executable, ROOT / "hooks" / "session_start.py"],
            input='{"source":"startup"}',
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("Diverter Delegation Gate", result.stdout)
        self.assertIn("delegation_context: delegated-subagent", result.stdout)
        self.assertIn("invoke `$diverter` first", result.stdout)

    def test_core_skill_selects_policy_and_backend(self) -> None:
        skill_path = ROOT / "skills" / "diverter" / "SKILL.md"
        skill = skill_path.read_text()

        self.assertTrue(skill_path.is_file())
        self.assertFalse((ROOT / "SKILL.md").exists())
        for name in (
            "decision-rules.md",
            "role-lineups.md",
            "handoff-schema.md",
            "delegation-contract.md",
            "examples-positive.md",
            "examples-negative.md",
        ):
            self.assertTrue((skill_path.parent / "references" / name).is_file(), name)

        self.assertFalse(
            (skill_path.parent / "references" / "suggestion-contract.md").exists()
        )
        self.assertIn("Delegation Policy", skill)
        self.assertIn("Dispatch Authorization", skill)
        self.assertIn("Dispatch Announcement", skill)
        self.assertIn("delegation_policy: ask", skill)
        self.assertIn("delegation_policy: auto", skill)
        self.assertIn("regardless of Work Mode", skill)
        self.assertIn("Backend Capability Check", skill)
        self.assertIn("Native Subagent Backend", skill)
        self.assertIn("CLI Worker Backend", skill)
        self.assertIn("agent_type", skill)
        self.assertIn("model", skill)
        self.assertIn("reasoning_effort", skill)
        self.assertIn("scripts/run-cli-agent.py", skill)
        self.assertIn("command-level approval", skill)
        self.assertIn("command-level runtime approval is governed below", skill)
        self.assertIn("attempt to write a readonly database", skill)
        self.assertIn("retry the same runner command once", skill)
        self.assertIn("do not switch the CLI Worker to full access", skill)
        self.assertIn("delegation_context: delegated-subagent", skill)

    def test_core_skill_refines_eligibility_and_sanitizes_failures(self) -> None:
        skill = (ROOT / "skills" / "diverter" / "SKILL.md").read_text()
        rules = (
            ROOT / "skills" / "diverter" / "references" / "decision-rules.md"
        ).read_text()

        for phrase in (
            "at least two separable work or evidence lanes",
            "one concrete high-risk specialist boundary",
            "explicit request to use subagents",
            "explicitly selected focused skill",
            "Sanitized Failure Reporting",
            "internal failure recovers successfully",
            "ask whether to continue in the Root Session",
        ):
            self.assertIn(phrase, skill)

        self.assertIn("Explicit delegation request", rules)
        self.assertIn("Focused skill ownership", rules)
        self.assertIn("Vague risk language", rules)

    def test_native_role_spawn_uses_no_history_or_model_overrides(self) -> None:
        skill = (ROOT / "skills" / "diverter" / "SKILL.md").read_text()
        handoff_schema = (
            ROOT / "skills" / "diverter" / "references" / "handoff-schema.md"
        ).read_text()
        spawn_policy = skill.split("Spawn call policy:", 1)[1].split(
            "Every handoff", 1
        )[0]

        self.assertIn("`agent_type`", spawn_policy)
        self.assertIn('`fork_turns: "none"`', spawn_policy)
        self.assertNotIn("fork_context", spawn_policy)
        self.assertNotIn("`model`", spawn_policy)
        self.assertNotIn("`reasoning_effort`", spawn_policy)
        self.assertIn('fork_turns: "none"', handoff_schema)
        self.assertNotIn("fork_context", handoff_schema)

    def test_bundled_skill_silently_defers_to_native_proactive_delegation(self) -> None:
        skill = (ROOT / "skills" / "diverter" / "SKILL.md").read_text()

        start = skill.index("<NATIVE-PROACTIVE-DELEGATION-STOP>")
        end = skill.index("</NATIVE-PROACTIVE-DELEGATION-STOP>")
        stop = skill[start:end]

        self.assertLess(start, skill.index("<SUBAGENT-STOP>"))
        self.assertIn("higher-priority session instructions", stop)
        self.assertIn("proactive multi-agent delegation is active", stop)
        self.assertIn("even when explicitly invoked", stop)
        self.assertIn("Do not mention Diverter", stop)
        self.assertIn("Continue the current task under the native policy", stop)
        self.assertNotIn("gpt-5.6-sol", stop)
        self.assertNotIn("Ultra", stop)

    def test_bundled_skill_resolves_cli_runner_from_its_file_path(self) -> None:
        skill_path = ROOT / "skills" / "diverter" / "SKILL.md"
        skill = skill_path.read_text()
        plugin_root = skill_path.parents[2]

        self.assertTrue((plugin_root / ".codex-plugin" / "plugin.json").is_file())
        self.assertTrue((plugin_root / "scripts" / "run-cli-agent.py").is_file())
        self.assertIn("plugin_root = Path(skill_file).parents[2]", skill)
        self.assertIn("${plugin_root}/scripts/run-cli-agent.py", skill)

    def test_install_guide_has_one_plugin_only_flow(self) -> None:
        guide = (ROOT / ".codex" / "INSTALL.md").read_text()

        self.assertIn("codex plugin marketplace add GML-MMGroup/Diverter", guide)
        self.assertIn("codex plugin add diverter@diverter", guide)
        self.assertIn("DIVERTER_PLUGIN", guide)
        self.assertIn("/hooks", guide)
        self.assertIn("install-agent-roles.py", guide)
        self.assertIn("scripts/diverter-mode.py\" init", guide)
        self.assertIn("$diverter-mode auto", guide)
        self.assertIn("$diverter-mode ask", guide)
        self.assertIn("$diverter-mode status", guide)
        self.assertIn("Diverter is installed in `<policy>` mode.", guide)
        self.assertIn("Python 3.11", guide)
        self.assertIn("$MARKETPLACE_NAME/$PLUGIN_NAME/$VERSION", guide)
        self.assertIn("repeated directory names are valid", guide)
        self.assertNotIn("npx skills", guide)
        self.assertNotIn("install-agents-gate.py", guide)
        self.assertNotIn("--scope", guide)

        install_order = (
            "### 2. Install the plugin",
            "### 3. Choose the global Bundled Subagents",
            "### 4. Run the Role Installer for the user",
            "### 5. Initialize the Delegation Policy",
            "### 6. Trust the SessionStart Hook",
            "### 7. Verify and finish",
        )
        positions = [guide.index(heading) for heading in install_order]
        self.assertEqual(positions, sorted(positions))

        updating = guide.split("## Updating", 1)[1]
        self.assertLess(updating.index("Role Installer"), updating.index("/hooks"))

        for readme_name in ("README.md", "README.zh.md"):
            readme = (ROOT / readme_name).read_text()
            self.assertNotIn("npx skills", readme, readme_name)
            self.assertNotIn("install-agents-gate.py", readme, readme_name)
            self.assertNotIn("AGENTS.md gate", readme, readme_name)

        self.assertFalse((ROOT / "scripts" / "install-agents-gate.py").exists())

    def test_auto_smoke_covers_required_policy_boundaries(self) -> None:
        prompts = (ROOT / "evals" / "prompts.yaml").read_text()
        for case_id in (
            "auto-pos-01",
            "auto-pos-02",
            "auto-neg-01",
            "auto-neg-02",
            "auto-override-ask",
            "auto-mode-bypass",
            "auto-native-bypass",
            "auto-failure-recovery",
            "auto-idempotency",
            "gate-neg-focused-ui",
            "gate-pos-ui-audit",
            "gate-neg-vague-web-performance",
            "gate-neg-vague-regression",
            "gate-neg-vague-release",
            "failure-recovered-silent",
            "failure-implicit-fallback",
            "failure-explicit-choice",
            "failure-user-action",
        ):
            self.assertIn(f"id: {case_id}", prompts)

        scenarios = (ROOT / "evals" / "scenarios.md").read_text()
        rubric = (ROOT / "evals" / "rubric.md").read_text()
        results_template = (ROOT / "evals" / "results-template.md").read_text()
        self.assertIn("hooks/session_start.py", scenarios)
        self.assertIn("DIVERTER_PLUGIN_ROOT", scenarios)
        self.assertIn(
            'prompt: "Review this branch against origin/main for correctness and maintainability regressions."',
            prompts,
        )
        self.assertIn("AUTO_WRITE_WORKSPACE", scenarios)
        self.assertIn("-s workspace-write", scenarios)
        self.assertIn("--add-dir /tmp/codex-subagent-eval/skill", scenarios)
        self.assertIn("evals/fixtures/settings-save/settings_save.py", prompts)
        self.assertTrue(
            (ROOT / "evals" / "fixtures" / "settings-save" / "settings_save.py").is_file()
        )
        self.assertIn("sanitized_failure_reporting", rubric)
        self.assertIn("Score / 6", results_template)

    def test_readmes_explain_native_proactive_delegation_boundary(self) -> None:
        english = (ROOT / "README.md").read_text()
        chinese = (ROOT / "README.zh.md").read_text()

        self.assertIn("native proactive delegation", english.lower())
        self.assertIn("silently steps aside", english.lower())
        self.assertIn("原生主动委派", chinese)
        self.assertIn("静默让路", chinese)


if __name__ == "__main__":
    unittest.main()
