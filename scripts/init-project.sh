#!/bin/bash
# 建一个数学建模竞赛项目的骨架。
#
#   ./init-project.sh ~/Code/cumcm-2026-c
#   ./init-project.sh .                     # 在当前目录建
#
# 已存在的文件不会被覆盖——在已有项目里跑也安全，只补缺的。

set -euo pipefail

DEST="${1:?用法: init-project.sh <项目目录>}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TPL="$(cd "$(dirname "${BASH_SOURCE[0]}")/../assets/templates" && pwd)"
PLB="$(cd "$(dirname "${BASH_SOURCE[0]}")/../assets/playbooks" && pwd)"

mkdir -p "$DEST"/{01-problem,02-data/{raw,processed},03-models/code,04-results/figures,05-paper/guides,06-submission}
cd "$DEST"
DEST="$(pwd)"

put() { # $1=模板名 $2=目标路径
  if [ -e "$2" ]; then
    echo "  ·  $2  已存在，跳过"
  else
    cp "$TPL/$1" "$2"
    echo "  +  $2"
  fi
}

putp() { # 从 playbooks 拷入（论文写作手册）
  if [ "$1" != "ai-disclosure.md" ]; then set -- "$1" "05-paper/guides/$1"; fi
  if [ -e "$2" ]; then
    echo "  ·  $2  已存在，跳过"
  else
    cp "$PLB/$1" "$2"
    echo "  +  $2"
  fi
}

put AGENTS.md          AGENTS.md
put 开始使用.md        开始使用.md
put handoff.md         handoff.md
put problem-brief.md   01-problem/problem-brief.md
put question-map.md    01-problem/question-map.md
put problem-mining.md   01-problem/problem-mining.md
put submission-rule.md 01-problem/submission-rule.md
put data-log.md        02-data/data-log.md
put model-review.md    03-models/model-review.md
put method-selection.md 03-models/method-selection.md
put results.md         04-results/results.md
putp judge-view.md      05-paper/judge-view.md
putp innovation.md       05-paper/innovation.md
putp dismantle.md        05-paper/dismantle.md
putp race-day.md         05-paper/race-day.md
putp paper-outline.md   05-paper/paper-outline.md
putp modeling-chapter.md 05-paper/modeling-chapter.md
putp abstract.md         05-paper/abstract.md
putp data-profile.md     05-paper/data-profile.md
putp validation-sensitivity.md 05-paper/validation-sensitivity.md
putp model-evaluation.md 05-paper/model-evaluation.md
put paper-review.md    05-paper/paper-review.md
put checklist.md       06-submission/checklist.md
put ai-usage.json      06-submission/ai-usage.json
put ai-statement.tex   05-paper/ai-statement.tex
put main.tex           05-paper/main.tex
put evidence-map.md    05-paper/evidence-map.md
putp ai-disclosure.md  05-paper/ai-disclosure.md

# 章节写作与证据记录
putp writing-workflow.md 05-paper/guides/writing-workflow.md
putp problem-restatement.md 05-paper/guides/problem-restatement.md
putp problem-analysis.md 05-paper/guides/problem-analysis.md
putp assumptions.md 05-paper/guides/assumptions.md
putp symbols.md 05-paper/guides/symbols.md
putp references-appendix.md 05-paper/guides/references-appendix.md
putp review-rubric.md 05-paper/guides/review-rubric.md
put assumption-register.md 03-models/assumption-register.md
put symbol-register.md 05-paper/symbol-register.md
put reference-register.md 05-paper/reference-register.md
put support-inventory.md 06-submission/support-inventory.md
put review-rubric.md 05-paper/review-rubric.md

# 绘图代码库（figures/style.py + plots.py）拷入 03-models/code/，幂等
FIG_DIR="$SCRIPT_DIR/../code-templates/figures"
if [ -d "$FIG_DIR" ] && [ ! -d "$DEST/03-models/code/figures" ]; then
  cp -r "$FIG_DIR" "$DEST/03-models/code/"
  echo "  +  03-models/code/figures  (绘图代码库)"
fi

# CUMCMThesis 模板（不含微软字体）自动拷入 05-paper/，幂等
TPL_DIR="$SCRIPT_DIR/../templates/CUMCMThesis"
if [ -d "$TPL_DIR" ] && [ ! -d "$DEST/05-paper/CUMCMThesis" ]; then
  cp -r "$TPL_DIR" "$DEST/05-paper/"
  echo "  +  05-paper/CUMCMThesis  (LaTeX 模板)"
fi

if [ ! -e "$DEST/05-paper/cumcmthesis.cls" ]; then
  cp "$TPL_DIR/cumcmthesis.cls" "$DEST/05-paper/cumcmthesis.cls"
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
03-models/references/bzd/
05-paper/*.ttf
05-paper/*.ttc
EOF
  echo "  +  .gitignore"
fi

cat <<EOF

骨架建好了：$DEST
下一步：打开 开始使用.md，把第一次使用的那段话发给 AI。
题面放入 01-problem，附件放入 02-data/raw；赛前可留空。
写作手册集中在 05-paper/guides，需要时再读。
EOF
