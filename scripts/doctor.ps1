# 只读检查；不安装软件，不修改项目，不代表提交审查通过。
param([string]$Dest = ".")
$ErrorActionPreference = "Stop"
if (-not (Test-Path -LiteralPath $Dest -PathType Container)) {
  Write-Host "[缺少] 项目目录不存在：$Dest"; exit 1
}
$missing = 0
foreach ($item in @(@("uv", "Python 求解与 AI 详情校验"), @("xelatex", "论文和 AI 详情 PDF 编译"))) {
  if (Get-Command $item[0] -ErrorAction SilentlyContinue) {
    Write-Host "[可用] $($item[0])：$($item[1])"
  } else { Write-Host "[缺少] $($item[0])：$($item[1])；仍可先读题和整理资料"; $missing++ }
}
foreach ($rel in @("AGENTS.md", "handoff.md", "01-problem", "02-data/raw", "05-paper/main.tex", "05-paper/cumcmthesis.cls", "06-submission/ai-usage.json")) {
  if (Test-Path -LiteralPath (Join-Path $Dest $rel)) { Write-Host "[已有] $rel" }
  else { Write-Host "[缺少] $rel；运行 init-project 补齐，已有文件不会覆盖"; $missing++ }
}
$raw = Join-Path $Dest "02-data/raw"
if ((Test-Path -LiteralPath $raw) -and -not (Get-ChildItem -LiteralPath $raw -File -Recurse | Select-Object -First 1)) {
  Write-Host "[待准备] 原始附件目录为空；赛前可暂留空"
}
$ledger = Join-Path $Dest "06-submission/ai-usage.json"
if (Test-Path -LiteralPath $ledger) {
  try {
    $data = Get-Content -LiteralPath $ledger -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($data.status -eq "template") { Write-Host "[模板] AI 台账尚未记录正式竞赛使用情况，这不是环境错误" }
    else { Write-Host "[台账] 当前状态：$($data.status)；是否满足提交条件需另行检查" }
  } catch { Write-Host "[需修复] AI 台账格式无法读取"; $missing++ }
}
Write-Host "下一步：打开 开始使用.md。环境检查仅确认入口和工具存在，不验证模型、宏包或提交内容。"
if ($missing) { exit 1 }
exit 0
