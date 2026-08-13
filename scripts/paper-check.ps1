# 提交前自动检查：占位符残留 / AI 套话 / 结果命名 / 模板残留（Windows PowerShell）。
#
#   powershell .\paper-check.ps1 C:\Users\me\cumcm-2026-c
#   powershell .\paper-check.ps1 .        # 当前目录
#
# 退出码：0 = 无硬伤；1 = 存在必须修复的问题（占位符残留、禁用命名）。
# 软伤（AI 套话 / 模板残留）只提示不拦截，对照 playbooks/modeling-chapter.md 第十节人工处理。

param([Parameter(Mandatory=$true)][string]$Dest)

$ErrorActionPreference = "Stop"
$fail = $false

function Say([string]$tag, [string]$msg) { Write-Host "[$tag] $msg" }

if (-not (Test-Path $Dest)) { Write-Host "项目目录不存在: $Dest"; exit 1 }

$scanFiles = Get-ChildItem $Dest -Recurse -Include *.md,*.tex -File |
  Where-Object { $_.FullName -notmatch '\\\.git\\|CUMCMThesis' }

# ---- 1. {{占位符}} 残留（硬伤） ----
Say "CHECK" "1/4 占位符残留"
$hits = $scanFiles | Select-String -Pattern '\{\{' -List
if ($hits) {
  $fail = $true
  foreach ($h in $hits) {
    $rel = $h.Path.Replace($Dest, ".").TrimEnd('\')
    $line = $h.Line.Trim()
    if ($line.Length -gt 60) { $line = $line.Substring(0, 60) }
    Say "FAIL" "$rel`:$($h.LineNumber)  $line"
  }
} else { Say "PASS" "无 {{占位符}} 残留" }

# ---- 2. AI 套话扫描（软伤，计数） ----
Say "CHECK" "2/4 AI 套话扫描"
$words = @("综上所述","在此基础上","值得注意的是","总而言之","由此可见","显而易见","毋庸置疑","众所周知","不可否认","拭目以待","未来已来","本文提出","本文将","科学合理","具有良好","里程碑")
$total = 0
foreach ($w in $words) {
  $count = ($scanFiles | Select-String -Pattern ([regex]::Escape($w))).Count
  if ($count -gt 0) { Say "WARN" ("{0} × {1}" -f $w, $count); $total += $count }
}
if ($total -eq 0) { Say "PASS" "无 AI 套话" }
else { Say "INFO" ("共 {0} 处，对照 05-paper/modeling-chapter.md 第十节逐条处理" -f $total) }

# ---- 3. 结果命名检查（硬伤） ----
Say "CHECK" "3/4 结果命名"
$resFile = Join-Path $Dest "04-results\results.md"
if (Test-Path $resFile) {
  $bad = Select-String -Path $resFile -Pattern '^\s*\|?\s*(test|final|new)[0-9]*'
  if ($bad) {
    $fail = $true
    foreach ($b in $bad) { Say "FAIL" ("禁用命名（test/final/new）: " + $b.Line.Trim()) }
  } else { Say "PASS" "results.md 无 test/final/new 命名" }
} else { Say "WARN" "未找到 04-results/results.md（还没跑结果？）" }

# ---- 4. 模板残留（软伤） ----
Say "CHECK" "4/4 模板残留"
$bad2 = $scanFiles | Select-String -Pattern 'TODO|FIXME|示例标题|Lorem|待填' -List
if ($bad2) {
  foreach ($b in $bad2) { Say "WARN" ("模板残留: " + $b.Path.Replace($Dest, ".") + ":" + $b.LineNumber) }
} else { Say "PASS" "无 TODO/示例残留" }

# ---- 汇总 ----
Write-Host ""
if ($fail) { Say "RESULT" "存在必须修复的问题（占位符残留 / 禁用命名）。"; exit 1 }
Say "RESULT" "无硬伤。软伤提示请人工过一遍，然后走 paper-review 自审与 checklist。"
exit 0
