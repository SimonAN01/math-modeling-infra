#!/bin/bash
# 编译论文：XeLaTeX 跑两遍 + 检查 PDF。
#
#   ./build-paper.sh ~/Code/cumcm-2026-c
#
# 在 05-paper/ 下找入口：main.tex > example.tex（CUMCMThesis 原型）。

set -euo pipefail

DEST="${1:?用法: build-paper.sh <项目目录>}"
PAPER="$DEST/05-paper"

if ! command -v xelatex >/dev/null 2>&1; then
  echo "未找到 xelatex。请安装 TeX Live / MiKTeX（含 XeLaTeX 与 ctex 宏包）。"
  exit 1
fi
if [ ! -d "$PAPER" ]; then echo "没有 05-paper 目录: $PAPER"; exit 1; fi

ENTRY=""
for cand in main.tex example.tex; do
  if [ -f "$PAPER/$cand" ]; then ENTRY="$cand"; break; fi
done
if [ -z "$ENTRY" ]; then echo "没找到入口 (main.tex / example.tex)"; exit 1; fi

cd "$PAPER"
xelatex -interaction=nonstopmode -halt-on-error "$ENTRY" >/dev/null
xelatex -interaction=nonstopmode -halt-on-error "$ENTRY" >/dev/null

PDF="${ENTRY%.tex}.pdf"
if [ -f "$PDF" ]; then
  echo "OK: $PAPER/$PDF"
  echo "记得检查: 目录 / 页码 / 交叉引用 / 图片路径。"
else
  echo "编译失败，没有生成 PDF。把 xelatex 报错丢给 AI 修。"
  exit 1
fi
