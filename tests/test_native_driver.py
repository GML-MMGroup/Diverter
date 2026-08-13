from pathlib import Path
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
DRIVER = ROOT / "scripts" / "run-native-lifecycle.py"


def load_driver_module():
    spec = importlib.util.spec_from_file_location("native_lifecycle_driver", DRIVER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class NativeLifecycleDriverTest(unittest.TestCase):
    def test_accepts_only_matching_prepared_metadata(self) -> None:
        driver = load_driver_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            installed_path = base / "codex-home" / "plugins" / "diverter"
            installed_path.mkdir(parents=True)
            metadata_path = base / "evidence" / "run-metadata.json"
            metadata_path.parent.mkdir()
            expected = {
                "plugin_revision": "revision-1",
                "policy": "auto",
                "scenario": "normal",
            }
            metadata_path.write_text(
                json.dumps({**expected, "installed_path": str(installed_path)})
            )

            metadata, actual_path = driver.load_prepared_run(metadata_path, expected)
            self.assertEqual(metadata["plugin_revision"], "revision-1")
            self.assertEqual(actual_path, installed_path)

            with self.assertRaisesRegex(ValueError, "prepared metadata mismatch: policy"):
                driver.load_prepared_run(metadata_path, {**expected, "policy": "ask"})

    def test_runtime_hash_excludes_auth_but_detects_role_changes(self) -> None:
        driver = load_driver_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir) / "home"
            installed_path = home / "plugins" / "diverter"
            installed_path.mkdir(parents=True)
            (installed_path / "SKILL.md").write_text("plugin")
            (home / "agents").mkdir()
            role = home / "agents" / "docs-researcher.toml"
            role.write_text("role-v1")
            (home / "diverter").mkdir()
            (home / "diverter" / "config.json").write_text('{"policy":"auto"}')
            marketplace = home / "local-marketplace" / ".agents" / "plugins"
            marketplace.mkdir(parents=True)
            (marketplace / "marketplace.json").write_text('{"ref":"revision-1"}')
            (home / "config.toml").write_text(
                '[plugins."diverter@test"]\nenabled = true\n'
            )
            auth = home / "auth.json"
            auth.write_text("login-v1")

            prepared = driver.runtime_hash(home, installed_path)
            auth.write_text("login-v2")
            self.assertEqual(driver.runtime_hash(home, installed_path), prepared)

            role.write_text("role-v2")
            self.assertNotEqual(driver.runtime_hash(home, installed_path), prepared)

    def test_runtime_hash_detects_behavior_config_changes(self) -> None:
        driver = load_driver_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir) / "home"
            installed_path = home / "plugins" / "diverter"
            installed_path.mkdir(parents=True)
            (installed_path / "SKILL.md").write_text("plugin")
            (home / "agents").mkdir()
            (home / "diverter").mkdir()
            (home / "diverter" / "config.json").write_text('{"policy":"auto"}')
            marketplace = home / "local-marketplace" / ".agents" / "plugins"
            marketplace.mkdir(parents=True)
            (marketplace / "marketplace.json").write_text('{"ref":"revision-1"}')
            config = home / "config.toml"
            config.write_text('[features]\nmulti_agent = true\n')
            prepared = driver.runtime_hash(home, installed_path)

            config.write_text('[features]\nmulti_agent = false\n')

            self.assertNotEqual(driver.runtime_hash(home, installed_path), prepared)

    def test_rejects_prepared_home_with_prior_lifecycle_evidence(self) -> None:
        driver = load_driver_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            home = base / "home"
            session = home / "sessions" / "2026" / "rollout.jsonl"
            session.parent.mkdir(parents=True)
            session.write_text("{}")
            evidence = base / "evidence"
            evidence.mkdir()

            with self.assertRaisesRegex(ValueError, "already contains lifecycle sessions"):
                driver.require_prepared_freshness(home, evidence)

            session.unlink()
            (evidence / "05-root-exec.json").write_text("{}")
            with self.assertRaisesRegex(ValueError, "prior execution output"):
                driver.require_prepared_freshness(home, evidence)

    def test_run_contract_hash_changes_with_prompt_or_verifier_scope(self) -> None:
        driver = load_driver_module()
        contract = {"prompt": "first", "verification_scope": "verify-a"}

        prepared = driver.stable_hash(contract)

        self.assertNotEqual(driver.stable_hash({**contract, "prompt": "second"}), prepared)
        self.assertNotEqual(
            driver.stable_hash({**contract, "verification_scope": "verify-b"}), prepared
        )

    def test_freezes_matrix_metadata_and_resume_effort(self) -> None:
        driver = DRIVER.read_text()

        self.assertGreaterEqual(driver.count("model_reasoning_effort"), 2)
        self.assertIn('"codex_version"', driver)
        self.assertIn('"installed_roles"', driver)
        self.assertIn('"workspace_fixture_hash"', driver)
        self.assertIn("expected exactly one native child session", driver)

    def test_rejects_contaminated_codex_home_before_running_codex(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            workspace = base / "workspace"
            workspace.mkdir()
            (workspace / "brief.md").write_text("fixture")
            prompt = base / "prompt.txt"
            prompt.write_text("Run the lifecycle fixture.")
            codex_home = base / "codex-home"
            codex_home.mkdir()
            (codex_home / "unrelated-agent.toml").write_text("contamination")

            result = subprocess.run(
                [
                    sys.executable,
                    DRIVER,
                    "--workspace",
                    workspace,
                    "--prompt-file",
                    prompt,
                    "--codex-home",
                    codex_home,
                    "--evidence-dir",
                    base / "evidence",
                    "--expected-role",
                    "docs-researcher",
                    "--policy",
                    "auto",
                    "--model",
                    "gpt-5.6-terra",
                    "--root-progress-scope",
                    "brief.md",
                ],
                text=True,
                capture_output=True,
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("Codex home must be absent or empty", result.stdout)


if __name__ == "__main__":
    unittest.main()
