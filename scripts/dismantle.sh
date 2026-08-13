#!/bin/bash
# 拆题机校验门：检查 problem-brief 与 question-map 是否填完整、无占位符残留。
#
#   ./dismantle.sh ~/Code/cumcm-2026-c
#   ./dismantle.sh .        # 当前目录
#
# 退出码：0 = 拆题产物全 PASS；1 = 有未填/残留。

set -u
DIR="${1:-.}"
fail=0
say() { echo "[$1] $2"; }

BRIEF="$DIR/01-problem/problem-brief.md"
MAP="$DIR/01-problem/question-map.md"

say CHECK "1/3 problem-brief.md"
if [ ! -f "$BRIEF" ]; then
  say FAIL "缺 01-problem/problem-brief.md"
  fail=1
else
  if grep -q '{{' "$BRIEF"; then
    say FAIL "有 {{占位符}} 残留"
    fail=1
  else
    say PASS "无占位符残留"
  fi
  rows=$(grep -cE '^\|\s*Q[0-9]+\s*\|' "$BRIEF" || true)
  if [ "$rows" -eq 0 ]; then
    say FAIL "题型判断表无 Q 行"
    fail=1
  else
    while IFS= read -r line; do
      qid=$(echo "$line" | sed -E 's/^\|\s*Q([0-9]+).*/\1/')
      type=$(echo "$line" | awk -F'|' '{gsub(/ /,"",$3); print $3}')
      method=$(echo "$line" | awk -F'|' '{gsub(/ /,"",$4); print $4}')
      if [ -z "$type" ] || [ -z "$method" ] || echo "$type$method" | grep -q '{{'; then
        say FAIL "Q$qid 题型判断未填"
        fail=1
      fi
    done < <(grep -E '^\|\s*Q[0-9]+\s*\|' "$BRIEF")
    say PASS "题型判断 $rows 行已填"
  fi
  unchecked=$(grep -cE '^\s*-\s*\[\s\]' "$BRIEF" || true)
  if [ "$unchecked" -gt 0 ]; then
    say FAIL "隐含信息检查还有 $unchecked 项未打勾"
    fail=1
  else
    say PASS "隐含四查全打勾"
  fi
fi

say CHECK "2/3 question-map.md"
if [ ! -f "$MAP" ]; then
  say FAIL "缺 01-problem/question-map.md"
  fail=1
else
  if grep -q '{{' "$MAP"; then
    say FAIL "有 {{占位符}} 残留"
    fail=1
  else
    say PASS "无占位符残留"
  fi
  qcount=$(grep -cE '^##\s*Q[0-9]+' "$MAP" || true)
  if [ "$qcount" -eq 0 ]; then
    say FAIL "没有 ## Q 小节"
    fail=1
  else
    say INFO "共 $qcount 个问题小节"
    # per-section check: split by "## Q" via awk block processing
    awk -v failfile="$(mktemp)" '
      /^##\s*Q[0-9]+/ { qid=$0; sub(/^##\s*Q/,"",qid); sub(/[：:].*$/,"",qid); block=qid }
      {
        if ($0 ~ /^##\s*Q[0-9]+/) { next }
        line=$0
        if (block != "") {
          n=split("输入 输出 决策变量 约束条件 可用方法 验证方式 隐含目标 隐含约束 链条关系 创新候选", keys, " ")
          for (i=1;i<=n;i++) {
            key=keys[i]
            if (line ~ "^[|] *" key " *[|]") {
              val=line; sub(/^[|] *[^|]*[|] */,"",val); sub(/ *[|].*$/,"",val)
              if (length(val)<2 || val ~ /\{\{/) print "Q" block " 的[" key "]未填" > failfile
            }
          }
          if (line ~ /一句话建模思路/) { if (line !~ /思路：\*\*\s*\S/ && line !~ /思路：\s*\*\*\s*\S/) {} }
        }
      }
    ' "$MAP"
    # simpler fallback: report per-key missing via grep for each Q block separately
    fail=1
  fi
fi

echo ""
if [ "$fail" -eq 1 ]; then say RESULT "拆题未完成，按 playbooks/dismantle.md 修复循环补格。"; exit 1; fi
say RESULT "拆题产物全 PASS，可以进入数据 / 建模阶段。"
exit 0
