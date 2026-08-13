# 结果版本命名生成器：读 results.md 现有最大序号，输出下一个合规名字。
#
#   powershell .\new-result.ps1 "加滞后特征"                # 当前目录
#   powershell .\new-result.ps1 "换XGBoost" C:\cumcm-2026-c
#
# 命名规则见 04-results/results.md：v<序号>_<改动的核心>，禁止 test/final/new/日期。

param(
  [Parameter(Mandatory=$true)][string]$Name,
  [string]$Dir = "."
)

$ErrorActionPreference = "Stop"
$resFile = Join-Path $Dir "04-results\results.md"
$max = 0
if (Test-Path $resFile) {
  $found = Select-String -Path $resFile -Pattern '^\|\s*v(\d+)[_\s]'
  foreach ($m in $found) {
    $n = [int]$m.Matches[0].Groups[1].Value
    if ($n -gt $max) { $max = $n }
  }
}
$next = $max + 1
$name = "v$next`_$Name"
Write-Host "下一版名: $name"
Write-Host "追加行:   | $name | <改了什么> | <问题号> | <指标1> | <指标2> | <结论> |"
