# 拆题机校验门：检查 problem-brief 与 question-map 是否填完整、无占位符残留。
#
#   powershell .\dismantle.ps1 C:\cumcm-2026-c
#   powershell .\dismantle.ps1 .        # 当前目录
#
# 退出码：0 = 拆题产物全 PASS；1 = 有未填/残留（按 playbooks/dismantle.md 修复循环补格）。

param([string]$Dir = ".")

$ErrorActionPreference = "Stop"
$fail = $false
function Say([string]$tag, [string]$msg) { Write-Host "[$tag] $msg" }

$brief = Join-Path $Dir "01-problem\problem-brief.md"
$map = Join-Path $Dir "01-problem\question-map.md"

Say "CHECK" "1/3 problem-brief.md"
if (-not (Test-Path $brief)) {
  Say "FAIL" "缺 01-problem\problem-brief.md"
  $fail = $true
} else {
  $b = [System.IO.File]::ReadAllText($brief, [System.Text.Encoding]::UTF8)
  if ($b -match '\{\{') { Say "FAIL" "有 {{占位符}} 残留"; $fail = $true } else { Say "PASS" "无占位符残留" }
  $rows = [regex]::Matches($b, '^\|\s*Q(\d+)\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]*)\|\s*$', 'Multiline')
  if ($rows.Count -eq 0) {
    Say "FAIL" "题型判断表无 Q 行"
    $fail = $true
  } else {
    foreach ($r in $rows) {
      $type = $r.Groups[2].Value.Trim()
      $method = $r.Groups[3].Value.Trim()
      if (-not $type -or $type -match '\{\{' -or -not $method -or $method -match '\{\{') {
        Say "FAIL" ("Q{0} 题型判断未填" -f $r.Groups[1].Value)
        $fail = $true
      }
    }
    Say "PASS" ("题型判断 {0} 行已填" -f $rows.Count)
  }
  $unchecked = [regex]::Matches($b, '^\s*-\s*\[\s\]\s+', 'Multiline').Count
  if ($unchecked -gt 0) { Say "FAIL" ("隐含信息检查还有 {0} 项未打勾" -f $unchecked); $fail = $true }
  else { Say "PASS" "隐含四查全打勾" }
}

Say "CHECK" "2/3 question-map.md"
if (-not (Test-Path $map)) {
  Say "FAIL" "缺 01-problem\question-map.md"
  $fail = $true
} else {
  $m = [System.IO.File]::ReadAllText($map, [System.Text.Encoding]::UTF8)
  if ($m -match '\{\{') { Say "FAIL" "有 {{占位符}} 残留"; $fail = $true } else { Say "PASS" "无占位符残留" }
  $qs = [regex]::Matches($m, '##\s*Q(\d+)')
  if ($qs.Count -eq 0) {
    Say "FAIL" "没有 ## Q 小节"
    $fail = $true
  } else {
    Say "INFO" ("共 {0} 个问题小节" -f $qs.Count)
    $keys = @("输入","输出","决策变量","约束条件","可用方法","验证方式","隐含目标","隐含约束","链条关系","创新候选")
    foreach ($q in $qs) {
      $start = $q.Index
      $next = $m.IndexOf('##', $start + 2)
      $block = if ($next -lt 0) { $m.Substring($start) } else { $m.Substring($start, $next - $start) }
      $qid = $q.Groups[1].Value
      foreach ($key in $keys) {
        $rm = [regex]::Match($block, '^\|\s*' + $key + '\s*\|\s*(.*?)\s*\|\s*$', 'Multiline')
        $val = $rm.Groups[1].Value.Trim()
        if (-not $val -or $val -match '\{\{' -or $val.Length -lt 1) {
          Say "FAIL" ("Q{0} 的[{1}]未填" -f $qid, $key)
          $fail = $true
        }
      }
      if ($block -notmatch '一句话建模思路：\s*\*\*\s*\S') {
        Say "FAIL" ("Q{0} 缺一句话建模思路" -f $qid)
        $fail = $true
      }
    }
    if (-not $fail) { Say "PASS" "所有小节十要素齐全" }
  }
}

Say "CHECK" "3/3 汇总"
if ($fail) { Say "RESULT" "拆题未完成，按 playbooks/dismantle.md 修复循环补格（最多 3 轮）。"; exit 1 }
Say "RESULT" "拆题产物全 PASS，可以进入数据 / 建模阶段。"
exit 0
