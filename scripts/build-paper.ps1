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

# 模板可能在 05-paper/ 或 05-paper/CUMCMThesis/ 子目录，两处都找入口
$Entry = $null
$PaperDir = $Paper
foreach ($dir in @($Paper, (Join-Path $Paper "CUMCMThesis"))) {
  foreach ($cand in @("main.tex", "example.tex")) {
    if (Test-Path (Join-Path $dir $cand)) { $Entry = $cand; $PaperDir = $dir; break }
  }
  if ($Entry) { break }
}
if (-not $Entry) { Write-Host "没找到入口 (main.tex / example.tex)"; exit 1 }

# CUMCMThesis 模板依赖 simsun.ttc / simkai.ttf（微软字体，仓库不携带）。
# Windows 下自动从系统字体目录补到论文目录，保证 cls 按文件名能找到。
foreach ($f in @("simsun.ttc", "simkai.ttf")) {
  $target = Join-Path $PaperDir $f
  if (-not (Test-Path $target)) {
    $src = Join-Path $env:WINDIR "Fonts\$f"
    if (Test-Path $src) {
      Copy-Item $src $PaperDir
      Write-Host "  +  补字体: $f"
    } else {
      Write-Host "  !  缺少字体 $f（非 Windows 系统请自行放入 $PaperDir）"
    }
  }
}

Push-Location $PaperDir
try {
  xelatex -interaction=nonstopmode -halt-on-error $Entry | Out-Null
  xelatex -interaction=nonstopmode -halt-on-error $Entry | Out-Null
} finally {
  Pop-Location
}

$pdf = Join-Path $PaperDir ($Entry -replace '\.tex$', '.pdf')
if (Test-Path $pdf) {
  $size = (Get-Item $pdf).Length / 1KB
  Write-Host "OK: $pdf ($([math]::Round($size,1)) KB)"
  Write-Host "记得检查: 页码 / 交叉引用 / 图片路径（2026 规范正文不要目录）。"
} else {
  Write-Host "编译失败，没有生成 PDF。把 xelatex 报错丢给 AI 修。"
  exit 1
}
