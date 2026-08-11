# 编译论文（Windows PowerShell）：XeLaTeX 跑两遍 + 检查 PDF。
#
#   powershell .\build-paper.ps1 C:\Users\me\cumcm-2026-c
#
# 在 05-paper/ 下找入口：main.tex > example.tex（CUMCMThesis 原型）。

param([Parameter(Mandatory=$true)][string]$Dest)

$ErrorActionPreference = "Stop"

if (-not (Get-Command xelatex -ErrorAction SilentlyContinue)) {
  Write-Host "未找到 xelatex。请安装 MiKTeX / TeX Live（含 XeLaTeX 与 ctex 宏包）。"
  exit 1
}

$Paper = Join-Path $Dest "05-paper"
if (-not (Test-Path $Paper)) { Write-Host "没有 05-paper 目录: $Paper"; exit 1 }

$Entry = $null
foreach ($cand in @("main.tex", "example.tex")) {
  if (Test-Path (Join-Path $Paper $cand)) { $Entry = $cand; break }
}
if (-not $Entry) { Write-Host "没找到入口 (main.tex / example.tex)"; exit 1 }

Push-Location $Paper
try {
  xelatex -interaction=nonstopmode -halt-on-error $Entry | Out-Null
  xelatex -interaction=nonstopmode -halt-on-error $Entry | Out-Null
} finally {
  Pop-Location
}

$pdf = Join-Path $Paper ($Entry -replace '\.tex$', '.pdf')
if (Test-Path $pdf) {
  $size = (Get-Item $pdf).Length / 1KB
  Write-Host "OK: $pdf ($([math]::Round($size,1)) KB)"
  Write-Host "记得检查: 目录 / 页码 / 交叉引用 / 图片路径。"
} else {
  Write-Host "编译失败，没有生成 PDF。把 xelatex 报错丢给 AI 修。"
  exit 1
}
