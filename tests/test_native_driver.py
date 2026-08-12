from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
DRIVER = ROOT / "scripts" / "run-native-lifecycle.py"


class NativeLifecycleDriverTest(unittest.TestCase):
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
