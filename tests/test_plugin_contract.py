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

    def test_session_start_injects_canonical_contract_with_policy(self) -> None:
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

            contract = (
                ROOT
                / "skills"
                / "diverter"
                / "references"
                / "session-contract.md"
            ).read_text()
            self.assertEqual(
                result.stdout,
                f"{contract.rstrip()}\n\ndelegation_policy: auto\n",
            )

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
        contract = (
            ROOT
            / "skills"
            / "diverter"
            / "references"
            / "session-contract.md"
        ).read_text()
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

                self.assertEqual(
                    result.stdout,
                    f"{contract.rstrip()}\n\ndelegation_policy: ask\n",
                )

    def test_user_prompt_submit_injects_only_the_root_turn_reminder(self) -> None:
        result = subprocess.run(
            [sys.executable, ROOT / "hooks" / "user_prompt_submit.py"],
            input='{"turn_id":"root-turn","prompt":"Inspect the repository"}',
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertEqual(
            result.stdout,
            "Mandatory turn preflight: Before task work, apply the active Diverter "
            "Session Contract to this prompt and deliberate the task shape before "
            "deciding. If eligible or the Contract is missing, load $diverter first. "
            "For an ordinary ROOT_ONLY decision, emit exactly one "
            "`Routing: ROOT_ONLY — <one task-shape reason>` receipt; keep bypass, "
            "explicit opt-out, and native unavailability silent.\n",
        )
        self.assertNotIn("Implicit eligibility", result.stdout)

    def test_user_prompt_submit_is_silent_when_agent_id_is_present(self) -> None:
        for agent_id in (None, "child-123"):
            with self.subTest(agent_id=agent_id):
                result = subprocess.run(
                    [sys.executable, ROOT / "hooks" / "user_prompt_submit.py"],
                    input=json.dumps(
                        {
                            "turn_id": "child-turn",
                            "prompt": "Execute the assigned handoff",
                            "agent_id": agent_id,
                            "agent_type": "reviewer",
                        }
                    ),
                    text=True,
                    capture_output=True,
                    check=True,
                )

                self.assertEqual(result.stdout, "")
                self.assertEqual(result.stderr, "")

    def test_session_start_defers_to_native_before_triggering_diverter(self) -> None:
        result = subprocess.run(
            [sys.executable, ROOT / "hooks" / "session_start.py"],
            text=True,
            capture_output=True,
            check=True,
        )

        native_stop = result.stdout.index("proactive multi-agent delegation is active")
        trigger = result.stdout.index("load `$diverter` before any task work")
        self.assertLess(native_stop, trigger)
        self.assertIn("Do not evaluate, load, or mention Diverter", result.stdout)

    def test_session_start_exposes_root_child_eligibility_and_native_absence(
        self,
    ) -> None:
        result = subprocess.run(
            [sys.executable, ROOT / "hooks" / "session_start.py"],
            text=True,
            capture_output=True,
            check=True,
        )

        gate = result.stdout
        self.assertIn("One bounded, independently executable Child Lane", gate)
        self.assertIn("One distinct, useful Root Lane", gate)
        self.assertIn("Waiting, supervision", gate)
        self.assertIn("An affirmative request", gate)
        self.assertIn(
            "`$diverter`, `subagent`, `delegate`, `委派`, `子代理`, or a named installed agent role",
            gate,
        )
        self.assertIn("scheduling language", gate)
        self.assertIn("explicitly selected focused skill", gate)
        self.assertIn("Supporting Child", gate)
        self.assertIn("native role-specific subagent dispatch", gate)
        self.assertIn("continue silently in the Root Session", gate)
        self.assertIn("`BYPASS`", gate)
        self.assertIn("`ROOT_ONLY`", gate)
        self.assertIn("`ELIGIBLE`", gate)
        self.assertIn("Task-shape Deliberation", gate)
        self.assertIn("strongest plausible split", gate)
        self.assertIn("absence of user-written lanes", gate)
        self.assertIn("Keep this deliberation private", gate)
        self.assertIn("Routing: ROOT_ONLY", gate)
        self.assertIn("Emit at most one receipt", gate)
        self.assertNotIn("Sanitized Failure Reporting", gate)

    def test_plugin_package_and_root_preflight_hooks_are_discoverable(self) -> None:
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text())
        marketplace = json.loads(
            (ROOT / ".agents" / "plugins" / "marketplace.json").read_text()
        )
        hooks = json.loads((ROOT / "hooks" / "hooks.json").read_text())

        self.assertEqual(manifest["name"], "diverter")
        self.assertEqual(manifest["version"], "0.4.3")
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

        self.assertEqual(
            set(hooks["hooks"]),
            {"SessionStart", "UserPromptSubmit"},
        )
        group = hooks["hooks"]["SessionStart"][0]
        self.assertEqual(group["matcher"], "startup|resume|clear|compact")
        handler = group["hooks"][0]
        self.assertEqual(handler["type"], "command")
        self.assertIn("${PLUGIN_ROOT}/hooks/session_start.py", handler["command"])
        self.assertIn("$env:PLUGIN_ROOT", handler["commandWindows"])
        self.assertEqual(handler["timeout"], 5)
        self.assertEqual(handler["statusMessage"], "Loading Diverter Session Contract...")

        prompt_group = hooks["hooks"]["UserPromptSubmit"][0]
        self.assertNotIn("matcher", prompt_group)
        prompt_handler = prompt_group["hooks"][0]
        self.assertEqual(prompt_handler["type"], "command")
        self.assertIn(
            "${PLUGIN_ROOT}/hooks/user_prompt_submit.py",
            prompt_handler["command"],
        )
        self.assertIn("$env:PLUGIN_ROOT", prompt_handler["commandWindows"])
        self.assertEqual(prompt_handler["timeout"], 5)
        self.assertNotIn("statusMessage", prompt_handler)

        result = subprocess.run(
            [sys.executable, ROOT / "hooks" / "session_start.py"],
            input='{"source":"startup"}',
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("Diverter Session Contract", result.stdout)
        self.assertIn("delegation_context: delegated-subagent", result.stdout)
        self.assertIn("load `$diverter` before any task work", result.stdout)

    def test_core_skill_selects_policy_and_native_lifecycle(self) -> None:
        skill_path = ROOT / "skills" / "diverter" / "SKILL.md"
        skill = skill_path.read_text()

        self.assertTrue(skill_path.is_file())
        self.assertFalse((ROOT / "SKILL.md").exists())
        for name in (
            "session-contract.md",
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
        self.assertIn("Native Capability Check", skill)
        self.assertIn("Native Subagent Backend", skill)
        self.assertIn("agent_type", skill)
        self.assertIn("Root Lane", skill)
        self.assertIn("Child Lane", skill)
        self.assertIn("Supporting Child", skill)
        self.assertIn("Smallest Sufficient Lineup", skill)
        self.assertIn("Child Reuse", skill)
        self.assertIn("Write Ownership", skill)
        self.assertNotIn("CLI Worker Backend", skill)
        self.assertNotIn("scripts/run-cli-agent.py", skill)
        self.assertIn("delegation_context: delegated-subagent", skill)

    def test_core_skill_uses_session_contract_as_the_preflight_authority(self) -> None:
        skill = (ROOT / "skills" / "diverter" / "SKILL.md").read_text()
        contract = (
            ROOT / "skills" / "diverter" / "references" / "session-contract.md"
        ).read_text()
        rules = (
            ROOT / "skills" / "diverter" / "references" / "decision-rules.md"
        ).read_text()

        for phrase in (
            "Session Contract is the sole normative authority",
            "completed Preflight",
            "Missing-Contract fallback",
            "references/session-contract.md",
            "Sanitized Failure Reporting",
            "internal failure recovers successfully",
            "ask whether to continue in the Root Session",
        ):
            self.assertIn(phrase, skill)

        self.assertNotIn("## Eligibility", skill)
        self.assertNotIn("CLARIFY", contract)
        self.assertIn("Non-normative examples", rules)
        self.assertIn("cannot override the Session Contract", rules)
        self.assertNotIn("Practical tie-breakers", rules)

        capability_table = skill.split("## Capability Selection", 1)[1].split(
            "Smallest Sufficient Lineup rules:", 1
        )[0]
        self.assertIn("Role write capability", capability_table)
        self.assertNotIn("Default mode", capability_table)

        self.assertIn("complete Root-and-Child workflow", skill)
        self.assertIn("no active lane may write", skill)
        self.assertIn("only some active lanes may write", skill)
        self.assertIn("every active lane may write", skill)

        child_reuse = skill.split("## Child Reuse", 1)[1].split(
            "## Write Ownership", 1
        )[0]
        self.assertIn("integrate and verify a received child result immediately", child_reuse)
        self.assertIn("terminal or idle", child_reuse)
        self.assertIn("before sending a related follow-up", child_reuse)

        self.assertIn("Explicit delegation request", rules)
        self.assertIn("Focused skill ownership", rules)
        self.assertIn("Vague risk language", rules)

    def test_explicit_dispatch_does_not_require_an_implicit_root_lane(self) -> None:
        skill = (ROOT / "skills" / "diverter" / "SKILL.md").read_text()
        message_contract = (
            ROOT
            / "skills"
            / "diverter"
            / "references"
            / "delegation-contract.md"
        ).read_text()
        rubric = (ROOT / "evals" / "rubric.md").read_text()
        scenarios = (ROOT / "evals" / "scenarios.md").read_text()

        self.assertIn("Only implicit eligibility requires", skill)
        self.assertIn(
            "An Explicit Delegation Request may have no distinct Root Lane",
            skill,
        )
        self.assertIn("for implicit eligibility, declare", skill)
        self.assertIn("for implicit eligibility", message_contract)
        self.assertIn("for explicit eligibility", message_contract)
        self.assertIn("Implicit eligibility", rubric)
        self.assertIn("explicit eligibility", rubric)
        self.assertIn("Explicit-lane implicit positives", scenarios)
        self.assertIn("Latent positives", scenarios)
        self.assertIn("Explicit delegation positives", scenarios)
        self.assertIn("For implicit eligibility, the Root Lane", scenarios)
        self.assertIn("For explicit eligibility, Root coordination", scenarios)

    def test_routing_receipt_is_one_external_result_without_a_new_score(self) -> None:
        contract = (
            ROOT / "skills" / "diverter" / "references" / "session-contract.md"
        ).read_text()
        skill = (ROOT / "skills" / "diverter" / "SKILL.md").read_text()
        message_contract = (
            ROOT / "skills" / "diverter" / "references" / "delegation-contract.md"
        ).read_text()
        rubric = (ROOT / "evals" / "rubric.md").read_text()
        results = (ROOT / "evals" / "results-template.md").read_text()
        english = (ROOT / "README.md").read_text()
        chinese = (ROOT / "README.zh.md").read_text()
        adr = (
            ROOT
            / "docs"
            / "adr"
            / "0013-deliberate-task-shape-and-emit-routing-receipts.md"
        ).read_text()

        self.assertIn("ordinary eligibility adjudication", contract)
        self.assertIn("Dispatch Recommendation or Dispatch Announcement", contract)
        self.assertIn("Routing Receipt and silence rules", skill)
        self.assertIn("## Root-only Receipt", message_contract)
        self.assertIn("status: accepted", adr)
        self.assertIn("Task-shape", adr)
        self.assertIn("Routing Receipt", adr)
        self.assertIn("does not introduce a routing-discovery phase", adr)
        self.assertIn("Routing Receipt violations", rubric)
        self.assertIn("Routing Receipt valid?", results)
        self.assertIn("Router Score / 7", results)
        self.assertIn("Routing: ROOT_ONLY", english)
        self.assertIn("Routing: ROOT_ONLY", chinese)

    def test_eligible_receipt_templates_are_user_facing_and_skill_owned(self) -> None:
        skill = (ROOT / "skills" / "diverter" / "SKILL.md").read_text()
        message_contract = (
            ROOT / "skills" / "diverter" / "references" / "delegation-contract.md"
        ).read_text()
        rubric = (ROOT / "evals" / "rubric.md").read_text()
        adr = (
            ROOT
            / "docs"
            / "adr"
            / "0013-deliberate-task-shape-and-emit-routing-receipts.md"
        ).read_text()

        self.assertEqual(skill.count("Routing: ELIGIBLE"), 2)
        self.assertEqual(
            skill.count("Child: `<exact-role>` — <concise task summary>"),
            2,
        )
        self.assertEqual(skill.count("Root: <concise task summary>"), 2)
        self.assertEqual(
            skill.count(
                "Work Mode: <read-only | mixed | write-capable>",
            ),
            2,
        )
        self.assertIn("Repeat `Child:` once per selected role", skill)
        self.assertIn("➡️ Dispatch Authorization: <direct approval question>", skill)
        self.assertIn("➡️ Dispatch: <immediate-start statement>", skill)
        self.assertNotIn("Why:", skill)
        self.assertNotIn("Routing: ELIGIBLE", message_contract)
        self.assertNotIn("This splits cleanly", message_contract)
        self.assertIn("owned only by `../SKILL.md`", message_contract)
        self.assertIn("`assignment_clarity`", rubric)
        self.assertNotIn("`rationale_quality`", rubric)
        self.assertIn("literal templates are owned only", adr)

        scenarios = (ROOT / "evals" / "scenarios.md").read_text()
        self.assertIn("literal policy template", scenarios)
        self.assertIn("Reject a `Why:` field", scenarios)

    def test_positive_examples_do_not_restore_single_lane_implicit_routes(self) -> None:
        examples = (
            ROOT / "skills" / "diverter" / "references" / "examples-positive.md"
        ).read_text()
        numbered = {
            int(line.split(".", 1)[0]): line
            for line in examples.splitlines()
            if line.split(".", 1)[0].isdigit()
        }

        for number in range(9, 15):
            self.assertIn(" while ", numbered[number].lower())
            self.assertIn("Root", numbered[number])

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

    def test_active_product_contract_has_no_cli_worker_backend(self) -> None:
        active_paths = [
            ROOT / "skills" / "diverter" / "SKILL.md",
            *sorted((ROOT / "skills" / "diverter" / "references").glob("*.md")),
            ROOT / ".codex" / "INSTALL.md",
            ROOT / "README.md",
            ROOT / "README.zh.md",
            ROOT / "evals" / "scenarios.md",
        ]

        self.assertFalse((ROOT / "scripts" / "run-cli-agent.py").exists())
        self.assertFalse((ROOT / "tests" / "test_cli_runner.py").exists())
        for path in active_paths:
            text = path.read_text()
            self.assertNotIn("CLI Worker Backend", text, path)
            self.assertNotIn("run-cli-agent.py", text, path)
            self.assertNotIn("ephemeral CLI", text, path)

    def test_install_guide_has_one_plugin_only_flow(self) -> None:
        guide = (ROOT / ".codex" / "INSTALL.md").read_text()

        self.assertIn("codex plugin marketplace add GML-MMGroup/Diverter", guide)
        self.assertIn("codex plugin add diverter@diverter", guide)
        self.assertIn("DIVERTER_PLUGIN", guide)
        self.assertIn("/hooks", guide)
        self.assertIn("install-agent-roles.py", guide)
        self.assertIn("Recommended: `auto`", guide)
        self.assertIn("Ask the user to choose", guide)
        self.assertIn("scripts/diverter-mode.py\" auto", guide)
        self.assertIn("scripts/diverter-mode.py\" ask", guide)
        self.assertIn("$diverter-mode auto", guide)
        self.assertIn("$diverter-mode ask", guide)
        self.assertIn("$diverter-mode status", guide)
        self.assertIn("Diverter is installed in the selected `<policy>` mode.", guide)
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
            "### 5. Choose the Delegation Policy",
            "### 6. Trust the SessionStart and UserPromptSubmit Hooks",
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
            self.assertNotIn("temporary leaf `codex exec`", readme, readme_name)

        self.assertFalse((ROOT / "scripts" / "install-agents-gate.py").exists())

    def test_docs_define_the_two_hook_preflight_architecture(self) -> None:
        english = (ROOT / "README.md").read_text()
        chinese = (ROOT / "README.zh.md").read_text()
        guide = (ROOT / ".codex" / "INSTALL.md").read_text()
        adr = ROOT / "docs" / "adr" / "0012-run-preflight-on-every-root-turn.md"

        for document in (english, chinese, guide):
            self.assertIn("SessionStart", document)
            self.assertIn("UserPromptSubmit", document)
            self.assertIn("Session Contract", document)

        self.assertIn("agent_id", guide)
        self.assertIn("Codex CLI `0.145.0`", guide)
        self.assertIn("For implicit routing", english)
        self.assertIn("对于隐式路由", chinese)
        self.assertIn("Explicit delegation may coordinate and wait", english)
        self.assertIn("显式委派可以协调并等待", chinese)
        self.assertTrue(adr.is_file())
        adr_text = adr.read_text()
        for term in (
            "**Session Contract**:",
            "**Turn Reminder**:",
            "**Preflight**:",
            "**Dispatch Workflow**:",
        ):
            self.assertIn(term, adr_text)

        self.assertIn("status: accepted", adr_text)

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
            "gate-pos-named-role",
            "gate-neg-scheduling-only",
            "gate-neg-quoted-delegation",
            "gate-neg-explanatory-delegation",
            "gate-neg-vague-web-performance",
            "gate-neg-vague-regression",
            "gate-neg-vague-release",
            "failure-recovered-silent",
            "failure-implicit-fallback",
            "failure-explicit-choice",
            "failure-user-action",
            "latent-pos-doc-contract",
            "latent-pos-regression",
            "latent-pos-web-audit",
            "ultra-pos-ui-root-continues",
            "ultra-pos-focused-skill-support",
            "ultra-pos-regression-root-continues",
            "ultra-pos-disjoint-write",
            "ultra-pos-same-file-readonly",
            "ultra-pos-doc-check",
            "ultra-reuse-same-scope",
            "ultra-neg-no-root-lane",
            "ultra-neg-readonly-laundering",
            "ultra-ownership-conflict",
        ):
            self.assertIn(f"id: {case_id}", prompts)

        scenarios = (ROOT / "evals" / "scenarios.md").read_text()
        rubric = (ROOT / "evals" / "rubric.md").read_text()
        results_template = (ROOT / "evals" / "results-template.md").read_text()
        self.assertIn("hooks/session_start.py", scenarios)
        self.assertIn("hooks/user_prompt_submit.py", scenarios)
        self.assertIn("agent_id", scenarios)
        self.assertIn("second Root prompt", scenarios)
        self.assertIn(
            'prompt: "While you map the changed execution path and integrate the final review, use one independent reviewer for correctness and maintainability regressions against origin/main."',
            prompts,
        )
        self.assertIn("newly created temporary `CODEX_HOME`", scenarios)
        self.assertIn("real non-empty workspace", scenarios)
        self.assertIn("Physically omit or remove the requested role", scenarios)
        self.assertIn("evals/fixtures/settings-save/settings_save.py", prompts)
        self.assertTrue(
            (ROOT / "evals" / "fixtures" / "settings-save" / "settings_save.py").is_file()
        )
        self.assertIn("sanitized_failure_reporting", rubric)
        self.assertIn("root_lane_quality", rubric)
        self.assertIn("Routing Receipt violations", rubric)
        self.assertIn("lifecycle_evidence", rubric)
        self.assertIn("Router Score / 7", results_template)
        self.assertIn("Native Lifecycle Evidence", results_template)
        self.assertIn("verify-native-lifecycle.py", scenarios)
        self.assertIn("run-native-lifecycle.py", scenarios)
        self.assertIn("three independent fresh sessions", scenarios)
        self.assertIn("deterministic nonzero operation", scenarios)
        self.assertIn("`test-automator`", scenarios)
        self.assertIn("does not rely on role-level sandbox isolation", scenarios)
        for mode_expectation in (
            "announce read-only work",
            "announce mixed work",
            "announce write-capable work",
        ):
            self.assertIn(mode_expectation, prompts)
        for metadata in (
            "root_continuation:",
            "child_scope:",
            "root_scope:",
            "benefit_claim:",
            "max_active_children:",
            "expected_reuse:",
        ):
            self.assertIn(metadata, prompts)

    def test_latent_positive_prompts_require_inference_not_lane_copying(self) -> None:
        prompts = (ROOT / "evals" / "prompts.yaml").read_text()
        for case_id in (
            "latent-pos-doc-contract",
            "latent-pos-regression",
            "latent-pos-web-audit",
        ):
            block = prompts.split(f"  - id: {case_id}\n", 1)[1].split(
                "\n  - id:", 1
            )[0]
            prompt = next(
                line.split('prompt: "', 1)[1].rsplit('"', 1)[0]
                for line in block.splitlines()
                if line.startswith("    prompt: ")
            ).lower()
            for forbidden in (
                "root",
                "child",
                "subagent",
                "子代理",
                "while",
                "independently",
                "同时",
            ):
                self.assertNotIn(forbidden, prompt, case_id)
            self.assertIn("expected_should_suggest: true", block)
            self.assertIn("latent_task_shape: true", block)

    def test_readmes_explain_native_proactive_delegation_boundary(self) -> None:
        english = (ROOT / "README.md").read_text()
        chinese = (ROOT / "README.zh.md").read_text()

        self.assertIn("native proactive delegation", english.lower())
        self.assertIn("silently steps aside", english.lower())
        self.assertIn("原生主动委派", chinese)
        self.assertIn("静默让路", chinese)


if __name__ == "__main__":
    unittest.main()
