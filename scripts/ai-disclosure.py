# /// script
# requires-python = ">=3.11"
# dependencies = ["pymupdf>=1.26,<2"]
# ///
"""Generate AI disclosure from an honest ledger; verify compiled submission artifacts."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from ai_disclosure_layout import render, validate_layout

USED = "本参赛队在竞赛过程中使用了AI工具，主要用于{purpose}，详细使用情况见支撑材料。"
UNUSED = "本参赛队在竞赛过程中未使用任何AI工具。"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tex(value):
    chars = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
             "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
             "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(chars.get(c, c) for c in str(value)).replace("\n", "\n\n")


def filled(value):
    return isinstance(value, str) and value.strip() and not re.search(r"待填|待核|未知|\{\{|TODO", value)


def validate(data):
    if data.get("status") not in ("used", "unused"):
        raise ValueError("台账 status 须按实际情况设为 used / unused；template 只能预览")
    if data.get("team_confirmed") is not True:
        raise ValueError("须由团队确认完整性后设置 team_confirmed=true，AI 不得代填")
    records = data.get("records", [])
    if not isinstance(records, list):
        raise ValueError("records 必须为列表")
    if data["status"] == "unused":
        if records:
            raise ValueError("未使用声明与非空 AI 记录矛盾")
        return
    if not filled(data.get("summary_purpose")) or not records:
        raise ValueError("已使用 AI 必须填写用途和实际记录")
    ids = set()
    for rec in records:
        for key in ("id", "date", "tool", "model", "stage", "purpose", "prompt", "process", "output"):
            if not filled(rec.get(key)):
                raise ValueError(f"记录 {rec.get('id')} 缺少有效字段 {key}")
        if rec["id"] in ids:
            raise ValueError("记录 ID 重复")
        ids.add(rec["id"])
        if rec.get("language_only") is not True:
            for key in ("adoption", "modification", "verification", "evidence", "reviewer_role"):
                if not filled(rec.get(key)):
                    raise ValueError(f"记录 {rec['id']} 缺少 {key}")
            if rec.get("human_verified") is not True:
                raise ValueError(f"记录 {rec['id']} 尚未人工核验")

    validate_layout(data, filled)


def declaration(data):
    return UNUSED if data["status"] == "unused" else USED.format(purpose=data["summary_purpose"])


def build(root, data, preview):
    if not preview:
        validate(data)
    target = root / "06-submission" / ("preview/table-format" if preview else "support")
    target.mkdir(parents=True, exist_ok=True)
    statement = "模板预览：尚未依据实际竞赛使用情况生成声明。" if preview else declaration(data)
    source = render(data, preview, statement, tex)
    outputs = {}
    if preview or data["status"] == "used":
        engine = shutil.which("xelatex")
        if not engine:
            raise ValueError("未找到 XeLaTeX；请安装 MiKTeX / TeX Live")
        # A fresh temporary directory prevents stale PDF success after compile failure.
        with tempfile.TemporaryDirectory(prefix="ai-disclosure-") as temp:
            folder = Path(temp)
            (folder / "detail.tex").write_text(source, encoding="utf-8")
            for _ in range(2):
                run = subprocess.run([engine, "-no-shell-escape", "-interaction=nonstopmode", "-halt-on-error", "detail.tex"],
                                     cwd=folder, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                if run.returncode:
                    raise ValueError("XeLaTeX 编译失败：" + run.stdout.decode(errors="replace")[-2500:])
            shutil.copyfile(folder / "detail.pdf", target / "AI工具使用详情.pdf")
        (target / "AI工具使用详情.tex").write_text(source, encoding="utf-8")
        outputs["pdf_sha256"] = digest(target / "AI工具使用详情.pdf")
    elif (target / "AI工具使用详情.pdf").exists():
        raise ValueError("存在旧的详情 PDF；请核实 used/unused 选择并移出过期材料后重试")
    if not preview:
        statement_path = root / "05-paper" / "ai-statement.tex"
        statement_path.write_text(r"\section*{AI工具使用声明}" + "\n" + tex(statement) + "\n", encoding="utf-8")
        outputs.update(ledger_sha256=digest(root / "06-submission" / "ai-usage.json"),
                       statement_sha256=digest(statement_path))
        (target / "ai-disclosure-manifest.json").write_text(json.dumps(outputs, indent=2), encoding="utf-8")
    print("OK: " + str(target))


def compact(text):
    return re.sub(r"\s+", "", text)


def check(root, data, paper):
    import pymupdf
    validate(data)
    support = root / "06-submission" / "support"
    manifest = json.loads((support / "ai-disclosure-manifest.json").read_text(encoding="utf-8"))
    for key, path in [("ledger_sha256", root / "06-submission" / "ai-usage.json"),
                      ("statement_sha256", root / "05-paper" / "ai-statement.tex")]:
        if manifest.get(key) != digest(path):
            raise ValueError("台账或声明已变化，请重新生成详情并编译论文")
    if not paper.is_file():
        raise ValueError(f"缺少编译后的论文 PDF: {paper}")
    with pymupdf.open(paper) as document:
        content = compact("\n".join(p.get_text() for p in document))
    if re.search(r"待填写|模板预览|TODO|FIXME|\{\{", content):
        raise ValueError("论文 PDF 仍含占位符或模板内容")
    expected = compact(declaration(data))
    title = "AI工具使用声明"
    start = content.find(title)
    pos = content.find(expected, start)
    refs = content.find("参考文献")
    if content.count(title) != 1 or start < 0 or pos < start or refs < pos + len(expected):
        raise ValueError("论文 PDF 须含唯一 AI工具使用声明、对应原文，并位于参考文献之前；请人工确认实际章节位置")
    opposite = UNUSED if data["status"] == "used" else "本参赛队在竞赛过程中使用了AI工具"
    if opposite in content:
        raise ValueError("论文包含互相矛盾的 AI 声明")
    if data["status"] == "used":
        detail = support / "AI工具使用详情.pdf"
        if manifest.get("pdf_sha256") != digest(detail):
            raise ValueError("详情 PDF 与最近生成记录不一致")
        with pymupdf.open(detail) as document:
            detail_text = compact("\n".join(p.get_text() for p in document))
        if "模板预览" in detail_text or expected not in detail_text:
            raise ValueError("详情 PDF 仍为模板或用途不一致")
    elif (support / "AI工具使用详情.pdf").exists():
        raise ValueError("未使用 AI 但仍有详情 PDF，请人工核实")
    print("PASS: AI 声明、台账与详情一致。人工仍须审查事实、匿名信息、PDF 排版及实际压缩包。")


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["build", "check"])
    parser.add_argument("root", type=Path)
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--paper", type=Path, help="待提交的论文 PDF；默认 05-paper/main.pdf")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        data = json.loads((root / "06-submission" / "ai-usage.json").read_text(encoding="utf-8-sig"))
        if args.action == "build":
            build(root, data, args.preview)
        else:
            check(root, data, args.paper.resolve() if args.paper else root / "05-paper" / "main.pdf")
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(1, f"FAIL: {exc}\n")


if __name__ == "__main__":
    main()
