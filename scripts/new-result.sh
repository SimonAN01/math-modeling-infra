#!/bin/bash
# 结果版本命名生成器：读 results.md 现有最大序号，输出下一个合规名字。
#
#   ./new-result.sh "加滞后特征"
#   ./new-result.sh "换XGBoost" ~/Code/cumcm-2026-c

set -euo pipefail

NAME="${1:?用法: new-result.sh <改动的核心> [项目目录]}"
DIR="${2:-.}"
RES="$DIR/04-results/results.md"

max=0
if [ -f "$RES" ]; then
  while IFS= read -r n; do
    [ "$n" -gt "$max" ] && max="$n"
  done < <(grep -oE '^\|\s*v[0-9]+' "$RES" | grep -oE '[0-9]+' || true)
fi

next=$((max + 1))
echo "下一版名: v${next}_${NAME}"
echo "追加行:   | v${next}_${NAME} | <改了什么> | <问题号> | <指标1> | <指标2> | <结论> |"
