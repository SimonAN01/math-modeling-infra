# /// script
# requires-python = ">=3.11"
# dependencies = ["pymupdf>=1.26,<2"]
# ///
"""Isolated regression fixtures, never written to the actual contest ledger."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from ai_disclosure_layout import CORE, STAGES, MODES, CATEGORIES

spec = importlib.util.spec_from_file_location("disclosure", Path(__file__).with_name("ai-disclosure.py"))
ai = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ai)


class DisclosureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "05-paper").mkdir()
        (self.root / "06-submission").mkdir()
        self.data = {"status": "used", "summary_purpose": "测试用代码检查", "team_confirmed": True,
                     "records": [{"id": "TEST-001", "date": "2026-09-07", "tool": "测试工具", "model": "测试型号",
                                  "stage": "隔离测试", "purpose": "验证披露生成", "prompt": "检查 a_b & 5% #1",
                                  "process": "仅为自动测试构造数据", "output": "test.py",
                                  "language_only": False, "adoption": "测试记录", "modification": "测试记录",
                                  "verification": "测试记录", "evidence": "tests", "reviewer_role": "测试角色",
                                  "human_verified": True}]}
        self.data["records"][0].update(stage_group=STAGES[3], interaction_modes=[MODES[3]],
                                       response="自动测试用回复，不是实际使用记录。", output_category=CATEGORIES[2])
        self.data["core_leadership"] = [dict(stage=s, team_led=True, contribution="隔离测试用贡献描述") for s in CORE]
        self.data["example_ids"] = ["TEST-001"]

    def save(self):
        (self.root / "06-submission/ai-usage.json").write_text(json.dumps(self.data, ensure_ascii=False), encoding="utf-8")

    def paper(self, wrong_order=False):
        folder = self.root / "05-paper"
        pieces = [r"\input{ai-statement.tex}", r"\section*{参考文献}测试文献。"]
        if wrong_order:
            pieces.reverse()
        (folder / "main.tex").write_text("\n".join([
            r"\documentclass[UTF8,fontset=fandol]{ctexart}", r"\begin{document}", *pieces, r"\end{document}"]), encoding="utf-8")
        subprocess.run(["xelatex", "-no-shell-escape", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
                       cwd=folder, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return folder / "main.pdf"

    def test_incomplete_and_unverified(self):
        for change in [{"status": "template"}, {"team_confirmed": False}, {"records": []}]:
            data = copy.deepcopy(self.data)
            data.update(change)
            with self.assertRaises(ValueError):
                ai.validate(data)
        self.data["records"][0]["human_verified"] = False
        with self.assertRaises(ValueError):
            ai.validate(self.data)
        self.data["records"][0]["language_only"] = True
        ai.validate(self.data)

    def test_used_pdf_order_and_stale_ledger(self):
        self.save()
        ai.build(self.root, self.data, False)
        ai.check(self.root, self.data, self.paper())
        statement = self.root / "05-paper/ai-statement.tex"
        original = statement.read_text(encoding="utf-8")
        statement.write_text("无声明", encoding="utf-8")
        missing_paper = self.paper()
        statement.write_text(original, encoding="utf-8")
        with self.assertRaises(ValueError):
            ai.check(self.root, self.data, missing_paper)
        with self.assertRaises(ValueError):
            ai.check(self.root, self.data, self.paper(wrong_order=True))
        correct_paper = self.paper()
        detail = self.root / "06-submission/support/AI工具使用详情.pdf"
        original_pdf = detail.read_bytes()
        detail.write_bytes(original_pdf + b"\nchanged")
        with self.assertRaises(ValueError):
            ai.check(self.root, self.data, correct_paper)
        detail.write_bytes(original_pdf)
        self.data["summary_purpose"] = "用途已变化"
        self.save()
        with self.assertRaises(ValueError):
            ai.check(self.root, self.data, self.root / "05-paper/main.pdf")

    def test_unused_and_conflict(self):
        self.data.update(status="unused", records=[])
        self.save()
        ai.build(self.root, self.data, False)
        ai.check(self.root, self.data, self.paper())
        self.assertFalse((self.root / "06-submission/support/AI工具使用详情.pdf").exists())
        self.data["records"] = [{}]
        with self.assertRaises(ValueError):
            ai.validate(self.data)

    def test_reference_table_fields(self):
        for key, value in [("stage_group", "无效环节"), ("interaction_modes", []), ("response", "")]:
            data = copy.deepcopy(self.data)
            data["records"][0][key] = value
            with self.assertRaises(ValueError):
                ai.validate(data)
        self.data["core_leadership"][0]["team_led"] = None
        with self.assertRaises(ValueError):
            ai.validate(self.data)


if __name__ == "__main__":
    unittest.main()
