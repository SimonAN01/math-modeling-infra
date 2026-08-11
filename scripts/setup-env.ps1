# 初始化求解环境（Windows PowerShell）：uv 建项目 + 装常用依赖。
#
#   powershell .\setup-env.ps1 C:\Users\me\cumcm-2026-c
#
# 依赖统一用 uv 管理，不裸用全局 pip。幂等：已有 code 目录则跳过 uv init。

param([Parameter(Mandatory=$true)][string]$Dest)

$ErrorActionPreference = "Stop"

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
  Write-Host "未找到 uv。安装: powershell -c `"irm https://astral.sh/uv/install.ps1 | iex`""
  exit 1
}

$CodeDir = Join-Path $Dest "03-models\code"
New-Item -ItemType Directory -Path $CodeDir -Force | Out-Null

if (-not (Test-Path (Join-Path $CodeDir "pyproject.toml"))) {
  Push-Location $CodeDir
  try {
    uv init --no-workspace 2>&1 | Out-Host
    uv add pandas numpy scipy scikit-learn matplotlib statsmodels pulp ortools deap 2>&1 | Out-Host
  } finally {
    Pop-Location
  }
} else {
  Push-Location $CodeDir
  try {
    uv add pandas numpy scipy scikit-learn matplotlib statsmodels pulp ortools deap 2>&1 | Out-Host
  } finally {
    Pop-Location
  }
}

Write-Host ""
Write-Host "环境就绪: $CodeDir"
Write-Host "运行示例: uv run python main.py"
Write-Host "代码按功能分文件: data_prep.py / model_solve.py / result_output.py"
