#!/bin/bash
# 建一个数学建模竞赛项目的骨架。
#
#   ./init-project.sh ~/Code/cumcm-2026-c
#   ./init-project.sh .                     # 在当前目录建
#
# 已存在的文件不会被覆盖——在已有项目里跑也安全，只补缺的。

set -euo pipefail

DEST="${1:?用法: init-project.sh <项目目录>}"
TPL="$(cd "$(dirname "${BASH_SOURCE[0]}")/../assets/templates" && pwd)"

mkdir -p "$DEST"/{01-problem,02-data/{raw,processed},03-models/code,04-results/figures,05-paper,06-submission}
cd "$DEST"

put() { # $1=模板名 $2=目标路径
  if [ -e "$2" ]; then
    echo "  ·  $2  已存在，跳过"
  else
    cp "$TPL/$1" "$2"
    echo "  +  $2"
  fi
}

put AGENTS.md          AGENTS.md
put handoff.md         handoff.md
put problem-brief.md   01-problem/problem-brief.md
put question-map.md    01-problem/question-map.md
put submission-rule.md 01-problem/submission-rule.md
put data-log.md        02-data/data-log.md
put model-review.md    03-models/model-review.md
put results.md         04-results/results.md
put paper-outline.md   05-paper/paper-outline.md
put checklist.md       06-submission/checklist.md

# CUMCMThesis 模板（不含微软字体）自动拷入 05-paper/，幂等
TPL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../templates/CUMCMThesis" && pwd)"
if [ -d "$TPL_DIR" ] && [ ! -d "$DEST/05-paper/CUMCMThesis" ]; then
  cp -r "$TPL_DIR" "$DEST/05-paper/"
  echo "  +  05-paper/CUMCMThesis  (LaTeX 模板)"
fi

if [ ! -e .gitignore ]; then
  cat > .gitignore <<'EOF'
02-data/raw/
02-data/processed/
03-models/code/.venv/
04-results/figures/
05-paper/*.aux
05-paper/*.log
05-paper/*.out
05-paper/*.toc
06-submission/*.zip
__pycache__/
EOF
  echo "  +  .gitignore"
fi

cat <<EOF

骨架建好了：$(pwd)

下一步按顺序：

  1. 填 AGENTS.md 的 {{占位符}} —— 尤其是赛题、分工和提交规则速记

  2. 拆题：填 01-problem/problem-brief.md 和 question-map.md，
     先判题型（预测 / 评价 / 优化 / 组合）

  3. 数据放 02-data/raw/，处理留痕写 data-log.md，原始数据不覆盖

  4. 建模先过 03-models/model-review.md 六维审查，全过再进 code/ 写代码

  5. 求解环境：
       bash $(dirname "${BASH_SOURCE[0]}")/setup-env.sh $(pwd)

  6. 写论文：05-paper/（CUMCMThesis 模板，XeLaTeX），摘要最后写

  7. 提交前：06-submission/checklist.md 逐项打勾，三方数字对账

每个窗口结束前更新 handoff.md。
EOF
