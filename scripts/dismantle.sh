#!/bin/bash
# 拆题机校验门：problem-mining 挖掘表 + problem-brief + question-map（小问级十要素）。
#
#   ./dismantle.sh ~/Code/cumcm-2026-c
#   ./dismantle.sh .        # 当前目录
#
# 退出码：0 = 拆题产物全 PASS；1 = 有未填/残留。

set -u
DIR="${1:-.}"
fail=0
say() { echo "[$1] $2"; }

PM="$DIR/01-problem/problem-mining.md"
BRIEF="$DIR/01-problem/problem-brief.md"
MAP="$DIR/01-problem/question-map.md"

say CHECK "1/4 problem-mining.md（逐句挖掘表）"
if [ ! -f "$PM" ]; then
  say FAIL "缺 01-problem/problem-mining.md"
  fail=1
else
  sentences=$(grep -cE '^\|\s*[0-9]+\s*\|' "$PM" || true)
  [ "$sentences" -eq 0 ] && { say FAIL "逐句挖掘表没有任何行"; fail=1; } || say PASS "逐句挖掘表 $sentences 行"
  typed=$(grep -cE '^\|\s*[0-9]+\s*\|[^|]*\|\s*(背景|任务|数据|约束|评分线索|干扰|提示词|无需处理)\s*\|' "$PM" || true)
  [ "$typed" -eq 0 ] && { say FAIL "没有一行完成类型归类"; fail=1; } || say PASS "已归类 $typed 行"
  grep -q '{{' "$PM" && say WARN "仍有 {{占位符}} 行未处理" || say PASS "无占位符残留"
  struct=$(grep -cE '^\|\s*Q[0-9]+\s*\|\s*Q[0-9]+\.[0-9]+\s*\|' "$PM" || true)
  [ "$struct" -eq 0 ] && { say FAIL "主问×小问结构表无行"; fail=1; } || say PASS "主问×小问结构表 $struct 行"
fi

say CHECK "2/4 problem-brief.md"
if [ ! -f "$BRIEF" ]; then
  say FAIL "缺 01-problem/problem-brief.md"
  fail=1
else
  grep -q '{{' "$BRIEF" && { say FAIL "有 {{占位符}} 残留"; fail=1; } || say PASS "无占位符残留"
  rows=$(grep -cE '^\|\s*Q[0-9]+\s*\|' "$BRIEF" || true)
  [ "$rows" -eq 0 ] && { say FAIL "题型判断表无 Q 行"; fail=1; } || say PASS "题型判断 $rows 行已填"
  unchecked=$(grep -cE '^\s*-\s*\[\s\]' "$BRIEF" || true)
  [ "$unchecked" -gt 0 ] && { say FAIL "隐含信息检查还有 $unchecked 项未打勾"; fail=1; } || say PASS "隐含四查全打勾"
fi

say CHECK "3/4 question-map.md（小问级十要素）"
if [ ! -f "$MAP" ]; then
  say FAIL "缺 01-problem/question-map.md"
  fail=1
else
  grep -q '{{' "$MAP" && { say FAIL "有 {{占位符}} 残留"; fail=1; } || say PASS "无占位符残留"
  qcount=$(grep -cE '^###\s*Q[0-9]+\.[0-9]+' "$MAP" || true)
  [ "$qcount" -eq 0 ] && { say FAIL "没有 ### Qx.y 小问小节"; fail=1; } || say INFO "共 $qcount 个小问小节"
  # per-key check: for each sub-question block, all ten keys must have non-empty values
  missing=0
  for key in 输入 输出 决策变量 约束条件 可用方法 验证方式 隐含目标 隐含约束 链条关系 创新候选; do
    # lines with this key and empty/placeholder value
    bad=$(grep -E "^\|\s*${key}\s*\|\s*(\{\{|\s*)\|" "$MAP" | wc -l)
    [ "$bad" -gt 0 ] && { say FAIL "[$key] 有 $bad 处未填"; missing=1; }
  done
  [ "$missing" -eq 0 ] && say PASS "所有小问十要素齐全"
fi

say CHECK "4/4 汇总"
if [ "$fail" -eq 1 ] || [ "${missing:-0}" -eq 1 ]; then say RESULT "拆题未完成，按 playbooks/dismantle.md 修复循环补格。"; exit 1; fi
say RESULT "拆题产物全 PASS，可以进入数据 / 建模阶段。"
exit 0
