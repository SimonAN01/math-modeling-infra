#!/bin/bash
# 把框架及自带的两个配套 skill 装到 Agent 的 skills 目录。
#
#   ./install-skills.sh ~/.claude/skills     # Claude Code / opencode / Cursor
#   ./install-skills.sh ~/.codex/skills      # Codex
#   ./install-skills.sh                      # 默认 ~/.claude/skills
#
# 幂等：重复执行会覆盖同名文件，不会留旧文件。

set -euo pipefail

DEST="${1:-$HOME/.claude/skills}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

mkdir -p "$DEST/math-modeling-infra"
cp -f "$ROOT/SKILL.md" "$ROOT/README.md" "$DEST/math-modeling-infra/"
cp -rf "$ROOT/assets" "$ROOT/scripts" "$DEST/math-modeling-infra/"

for s in scientific-figure-making humanizer-zh; do
  cp -rf "$ROOT/skills/$s" "$DEST/"
done

echo "已安装到 $DEST:"
echo "  - math-modeling-infra（数模工作流）"
echo "  - scientific-figure-making（出图规范）"
echo "  - humanizer-zh（去 AI 味）"
