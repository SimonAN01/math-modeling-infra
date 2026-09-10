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
$Plb = Join-Path $Root "assets\playbooks"

New-Item -ItemType Directory -Path $Dest -Force | Out-Null

$Dirs = @(
  "01-problem", "02-data\raw", "02-data\processed",
  "03-models\code", "04-results\figures", "05-paper", "05-paper\guides", "06-submission"
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

function Put-Playbook([string]$name, [string]$rel) {
  if ($name -ne "ai-disclosure.md") { $rel = "05-paper\guides\$name" }
  $target = Join-Path $Dest $rel
  if (Test-Path $target) {
    Write-Host "  .  $rel  已存在，跳过"
  } else {
    Copy-Item (Join-Path $Plb $name) $target
    Write-Host "  +  $rel"
  }
}

Put-Template "AGENTS.md"        "AGENTS.md"
Put-Template "开始使用.md"       "开始使用.md"
Put-Template "handoff.md"       "handoff.md"
Put-Template "problem-brief.md" "01-problem\problem-brief.md"
Put-Template "question-map.md"  "01-problem\question-map.md"
Put-Template "problem-mining.md" "01-problem\problem-mining.md"
Put-Template "submission-rule.md" "01-problem\submission-rule.md"
Put-Template "data-log.md"      "02-data\data-log.md"
Put-Template "model-review.md"  "03-models\model-review.md"
Put-Template "method-selection.md" "03-models\method-selection.md"
Put-Template "results.md"       "04-results\results.md"
Put-Playbook "judge-view.md"      "05-paper\judge-view.md"
Put-Playbook "innovation.md"     "05-paper\innovation.md"
Put-Playbook "dismantle.md"      "05-paper\dismantle.md"
Put-Playbook "race-day.md"       "05-paper\race-day.md"
Put-Playbook "paper-outline.md"   "05-paper\paper-outline.md"
Put-Playbook "modeling-chapter.md" "05-paper\modeling-chapter.md"
Put-Playbook "abstract.md"         "05-paper\abstract.md"
Put-Playbook "data-profile.md"     "05-paper\data-profile.md"
Put-Playbook "validation-sensitivity.md" "05-paper\validation-sensitivity.md"
Put-Playbook "model-evaluation.md" "05-paper\model-evaluation.md"
Put-Template "paper-review.md"    "05-paper\paper-review.md"
Put-Template "checklist.md"     "06-submission\checklist.md"
Put-Template "ai-usage.json"    "06-submission\ai-usage.json"
Put-Template "ai-statement.tex" "05-paper\ai-statement.tex"
Put-Template "main.tex"         "05-paper\main.tex"
Put-Template "evidence-map.md"  "05-paper\evidence-map.md"
Put-Playbook "ai-disclosure.md" "05-paper\ai-disclosure.md"

# 章节写作与证据记录
Put-Playbook "writing-workflow.md" "05-paper\guides\writing-workflow.md"
Put-Playbook "problem-restatement.md" "05-paper\guides\problem-restatement.md"
Put-Playbook "problem-analysis.md" "05-paper\guides\problem-analysis.md"
Put-Playbook "assumptions.md" "05-paper\guides\assumptions.md"
Put-Playbook "symbols.md" "05-paper\guides\symbols.md"
Put-Playbook "references-appendix.md" "05-paper\guides\references-appendix.md"
Put-Playbook "review-rubric.md" "05-paper\guides\review-rubric.md"
Put-Template "assumption-register.md" "03-models\assumption-register.md"
Put-Template "symbol-register.md" "05-paper\symbol-register.md"
Put-Template "reference-register.md" "05-paper\reference-register.md"
Put-Template "support-inventory.md" "06-submission\support-inventory.md"
Put-Template "review-rubric.md" "05-paper\review-rubric.md"

# 绘图代码库（figures/style.py + plots.py）拷入 03-models/code/，幂等
$FigDir = Join-Path $Root "code-templates\figures"
$FigTarget = Join-Path $Dest "03-models\code\figures"
if ((Test-Path $FigDir) -and -not (Test-Path $FigTarget)) {
  Copy-Item $FigDir $FigTarget -Recurse
  Write-Host "  +  03-models\code\figures  (绘图代码库)"
}

# CUMCMThesis 模板（不含微软字体）自动拷入 05-paper/，幂等
$TplDir = Join-Path $Root "templates\CUMCMThesis"
$TplTarget = Join-Path $Dest "05-paper\CUMCMThesis"
if ((Test-Path $TplDir) -and -not (Test-Path $TplTarget)) {
  Copy-Item $TplDir $TplTarget -Recurse
  Write-Host "  +  05-paper\CUMCMThesis  (LaTeX 模板)"
}

$ClassTarget = Join-Path $Dest "05-paper\cumcmthesis.cls"
if (-not (Test-Path $ClassTarget)) {
  Copy-Item (Join-Path $TplDir "cumcmthesis.cls") $ClassTarget
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
03-models/references/bzd/
05-paper/*.ttf
05-paper/*.ttc
'@ | Set-Content -Path $gitignore -Encoding UTF8
  Write-Host "  +  .gitignore"
}

Write-Host ""
Write-Host "骨架建好了: $Dest"
Write-Host ""
Write-Host '下一步：打开 开始使用.md，把第一次使用的那段话发给 AI。'
Write-Host '题面放入 01-problem，原始附件放入 02-data/raw；赛前可留空。'
Write-Host '写作手册集中在 05-paper/guides，需要时再读。'
Write-Host ""
Write-Host '每个窗口结束前更新 handoff.md。'
