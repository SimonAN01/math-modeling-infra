#!/bin/bash
# 初始化求解环境：uv 建项目 + 装常用依赖。
#
#   ./setup-env.sh ~/Code/cumcm-2026-c
#
# 依赖统一用 uv 管理，不裸用全局 pip。幂等：已有 pyproject.toml 则跳过 init。

set -euo pipefail

DEST="${1:?用法: setup-env.sh <项目目录>}"
CODE="$DEST/03-models/code"

if ! command -v uv >/dev/null 2>&1; then
  echo "未找到 uv。安装: curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 1
fi

mkdir -p "$CODE"
cd "$CODE"

if [ ! -f pyproject.toml ]; then
  uv init --no-workspace
fi
uv add pandas numpy scipy scikit-learn matplotlib statsmodels pulp ortools deap

echo ""
echo "环境就绪: $CODE"
echo "运行示例: uv run python main.py"
echo "代码按功能分文件: data_prep.py / model_solve.py / result_output.py"
