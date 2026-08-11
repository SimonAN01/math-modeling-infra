# 建一个数学建模竞赛项目的骨架（Windows PowerShell）。
#
#   powershell .\init-project.ps1 C:\Users\me\cumcm-2026-c
#   powershell .\init-project.ps1 .          # 在当前目录建
#
# 已存在的文件不会被覆盖——在已有项目里跑也安全，只补缺的。

param([Parameter(Mandatory=$true)][string]$Dest)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Tpl = Join-Path $Root "assets\templates"

New-Item -ItemType Directory -Path $Dest -Force | Out-Null

$Dirs = @(
  "01-problem", "02-data\raw", "02-data\processed",
  "03-models\code", "04-results\figures", "05-paper", "06-submission"
)
foreach ($d in $Dirs) {
  New-Item -ItemType Directory -Path (Join-Path $Dest $d) -Force | Out-Null
}

function Put-Template([string]$name, [string]$rel) {
  $target = Join-Path $Dest $rel
  if (Test-Path $target) {
    Write-Host "  .  $rel  已存在，跳过"
  } else {
    Copy-Item (Join-Path $Tpl $name) $target
    Write-Host "  +  $rel"
  }
}

Put-Template "AGENTS.md"        "AGENTS.md"
Put-Template "handoff.md"       "handoff.md"
Put-Template "problem-brief.md" "01-problem\problem-brief.md"
Put-Template "question-map.md"  "01-problem\question-map.md"
Put-Template "submission-rule.md" "01-problem\submission-rule.md"
Put-Template "data-log.md"      "02-data\data-log.md"
Put-Template "model-review.md"  "03-models\model-review.md"
Put-Template "method-selection.md" "03-models\method-selection.md"
Put-Template "results.md"       "04-results\results.md"
Put-Template "paper-outline.md" "05-paper\paper-outline.md"
Put-Template "paper-review.md"  "05-paper\paper-review.md"
Put-Template "checklist.md"     "06-submission\checklist.md"

# CUMCMThesis 模板（不含微软字体）自动拷入 05-paper/，幂等
$TplDir = Join-Path $Root "templates\CUMCMThesis"
$TplTarget = Join-Path $Dest "05-paper\CUMCMThesis"
if ((Test-Path $TplDir) -and -not (Test-Path $TplTarget)) {
  Copy-Item $TplDir $TplTarget -Recurse
  Write-Host "  +  05-paper\CUMCMThesis  (LaTeX 模板)"
}

$gitignore = Join-Path $Dest ".gitignore"
if (-not (Test-Path $gitignore)) {
  @'
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
'@ | Set-Content -Path $gitignore -Encoding UTF8
  Write-Host "  +  .gitignore"
}

Write-Host ""
Write-Host "骨架建好了: $Dest"
Write-Host ""
Write-Host '下一步按顺序:'
Write-Host '  1. 填 AGENTS.md 的 {{占位符}} —— 尤其是赛题、分工和提交规则速记'
Write-Host '  2. 拆题: 填 01-problem/problem-brief.md 和 question-map.md'
Write-Host '  3. 数据放 02-data/raw/, 处理留痕写 data-log.md'
Write-Host '  4. 建模先过 03-models/model-review.md 六维审查, 再进 code/ 写代码'
Write-Host "  5. 求解环境: powershell $(Join-Path $PSScriptRoot 'setup-env.ps1') $Dest"
Write-Host '  6. 写论文: 05-paper/ (CUMCMThesis 模板), 摘要最后写'
Write-Host '  7. 提交前: 06-submission/checklist.md 逐项打勾'
Write-Host ""
Write-Host '每个窗口结束前更新 handoff.md。'
