"""Smoke-test new-user setup in isolated temporary directories; no global installation."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BootstrapTests(unittest.TestCase):
    def exercise(self, engine, extension):
        with tempfile.TemporaryDirectory(prefix="infra-bootstrap-") as temp:
            folder = Path(temp)
            installed = folder / "技能 skills"
            project = folder / "比赛 project"

            def run(script, *args):
                command = [engine]
                if extension == "ps1":
                    command += ["-NoProfile", "-ExecutionPolicy", "Bypass", "-File"]
                command += [script.as_posix(), *(str(a).replace("\\", "/") for a in args)]
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                self.assertEqual(result.returncode, 0, result.stdout.decode("utf-8", errors="replace"))

            for _ in range(2):
                run(ROOT / f"scripts/install-skills.{extension}", installed)
            skill = installed / "math-modeling-infra"
            for rel in ["templates/CUMCMThesis/cumcmthesis.cls", "code-templates/figures/plots.py",
                        "scripts/ai_disclosure_layout.py", "assets/templates/开始使用.md",
                        "skills/humanizer-zh/SKILL.md", "skills/scientific-figure-making/SKILL.md"]:
                self.assertTrue((skill / rel).is_file(), rel)
            run(skill / f"scripts/init-project.{extension}", project)
            for rel in ["开始使用.md", "05-paper/guides/paper-outline.md", "05-paper/main.tex",
                        "05-paper/cumcmthesis.cls", "06-submission/ai-usage.json",
                        "05-paper/guides/writing-workflow.md", "05-paper/guides/problem-analysis.md",
                        "05-paper/guides/references-appendix.md", "05-paper/guides/review-rubric.md",
                        "03-models/assumption-register.md", "05-paper/symbol-register.md",
                        "05-paper/reference-register.md", "05-paper/review-rubric.md",
                        "06-submission/support-inventory.md"]:
                self.assertTrue((project / rel).is_file(), rel)
            self.assertFalse((project / "05-paper/paper-outline.md").exists())
            main = project / "05-paper/main.tex"
            main.write_text("团队已有内容，不得覆盖", encoding="utf-8")
            run(skill / f"scripts/init-project.{extension}", project)
            self.assertEqual(main.read_text(encoding="utf-8"), "团队已有内容，不得覆盖")

    @unittest.skipUnless(os.name == "nt", "Windows only")
    def test_powershell(self):
        self.exercise("powershell", "ps1")

    def test_bash(self):
        engine = shutil.which("bash")
        if not engine and Path("C:/Program Files/Git/bin/bash.exe").is_file():
            engine = "C:/Program Files/Git/bin/bash.exe"
        if not engine:
            self.skipTest("Bash is unavailable")
        self.exercise(engine, "sh")


if __name__ == "__main__":
    unittest.main()
