#!/bin/bash
# Read-only environment and project entry checks, not a submission verdict.
set -u
DEST="${1:-.}"
[ -d "$DEST" ] || { echo "[缺少] 项目目录不存在：$DEST"; exit 1; }
missing=0
for tool in uv xelatex; do
  if command -v "$tool" >/dev/null 2>&1; then echo "[可用] $tool";
  else echo "[缺少] $tool；仍可先读题和整理资料"; missing=1; fi
done
for rel in AGENTS.md handoff.md 01-problem 02-data/raw 05-paper/main.tex 05-paper/cumcmthesis.cls 06-submission/ai-usage.json; do
  if [ -e "$DEST/$rel" ]; then echo "[已有] $rel";
  else echo "[缺少] $rel；运行 init-project 补齐，已有文件不会覆盖"; missing=1; fi
done
echo "下一步：打开 开始使用.md。此检查不验证模型、宏包或提交内容；空台账和待填论文属正常初始状态。"
exit "$missing"
