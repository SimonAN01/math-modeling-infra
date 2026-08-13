#!/bin/bash
# 提交前自动检查：占位符残留 / AI 套话 / 结果命名 / 模板残留。
#
#   ./paper-check.sh ~/Code/cumcm-2026-c
#   ./paper-check.sh .                     # 当前目录
#
# 退出码：0 = 无硬伤；1 = 存在必须修复的问题。

set -u

DEST="${1:?用法: paper-check.sh <项目目录>}"
fail=0
say() { echo "[$1] $2"; }

[ -d "$DEST" ] || { echo "项目目录不存在: $DEST"; exit 1; }

grep_files() { # 排除 .git 与 CUMCMThesis 模板
  grep -rn --include='*.md' --include='*.tex' "$1" "$DEST" 2>/dev/null | grep -v '/.git/' | grep -v 'CUMCMThesis' || true
}

say CHECK "1/4 占位符残留"
if grep_files '{{' | grep -q .; then
  grep_files '{{'
  fail=1
else
  say PASS "无 {{占位符}} 残留"
fi

say CHECK "2/4 AI 套话扫描"
words=(综上所述 在此基础上 值得注意的是 总而言之 由此可见 显而易见 毋庸置疑 众所周知 不可否认 拭目以待 未来已来 本文提出 本文将 科学合理 具有良好 里程碑)
total=0
for w in "${words[@]}"; do
  c=$(grep_files "$w" | wc -l)
  if [ "$c" -gt 0 ]; then say WARN "$w × $c"; total=$((total+c)); fi
done
if [ "$total" -eq 0 ]; then say PASS "无 AI 套话"; else say INFO "共 $total 处，对照 05-paper/modeling-chapter.md 第十节处理"; fi

say CHECK "3/4 结果命名"
if [ -f "$DEST/04-results/results.md" ]; then
  if grep -nE '^\s*\|?\s*(test|final|new)[0-9]*' "$DEST/04-results/results.md"; then
    say FAIL "禁用命名（test/final/new）见上"
    fail=1
  else
    say PASS "results.md 无 test/final/new 命名"
  fi
else
  say WARN "未找到 04-results/results.md（还没跑结果？）"
fi

say CHECK "4/4 模板残留"
if grep_files 'TODO|FIXME|示例标题|Lorem|待填' | grep -q .; then
  grep_files 'TODO|FIXME|示例标题|Lorem|待填'
  say WARN "模板残留见上"
else
  say PASS "无 TODO/示例残留"
fi

echo ""
if [ "$fail" -eq 1 ]; then say RESULT "存在必须修复的问题（占位符残留 / 禁用命名）。"; exit 1; fi
say RESULT "无硬伤。软伤提示请人工过一遍，然后走 paper-review 自审与 checklist。"
exit 0
