# 拆题机校验门：problem-mining 挖掘表 + problem-brief + question-map（小问级十要素）。
#
#   powershell .\dismantle.ps1 C:\cumcm-2026-c
#   powershell .\dismantle.ps1 .        # 当前目录
#
# 退出码：0 = 拆题产物全 PASS；1 = 有未填/残留（按 playbooks/dismantle.md 修复循环补格）。

param([string]$Dir = ".")

$ErrorActionPreference = "Stop"
$fail = $false
function Say([string]$tag, [string]$msg) { Write-Host "[$tag] $msg" }

$pm = Join-Path $Dir "01-problem\problem-mining.md"
$brief = Join-Path $Dir "01-problem\problem-brief.md"
$map = Join-Path $Dir "01-problem\question-map.md"

Say "CHECK" "1/4 problem-mining.md（逐句挖掘表）"
if (-not (Test-Path $pm)) {
  Say "FAIL" "缺 01-problem\problem-mining.md"
  $fail = $true
} else {
  $p = [System.IO.File]::ReadAllText($pm, [System.Text.Encoding]::UTF8)
  $sentences = [regex]::Matches($p, '^\|\s*(\d+)\s*\|', 'Multiline').Count
  if ($sentences -eq 0) { Say "FAIL" "逐句挖掘表没有任何行"; $fail = $true }
  else { Say "PASS" ("逐句挖掘表 {0} 行" -f $sentences) }
  $typed = [regex]::Matches($p, '^\|\s*\d+\s*\|[^|]*\|\s*(背景|任务|数据|约束|评分线索|干扰|提示词|无需处理)\s*\|', 'Multiline').Count
  if ($typed -eq 0) { Say "FAIL" "没有一行完成类型归类（背景/任务/数据/约束/评分线索/干扰）"; $fail = $true }
  else { Say "PASS" ("已归类 {0} 行" -f $typed) }
  if ($p -match '\{\{') { Say "WARN" "仍有 {{占位符}} 行未处理（未挖到的句子要标注，别留模板痕）" } else { Say "PASS" "无占位符残留" }
  $struct = [regex]::Matches($p, '^\|\s*Q(\d+)\s*\|\s*(Q\1\.\d+|—|-)\s*\|', 'Multiline').Count
  if ($struct -eq 0) { Say "FAIL" "主问×小问结构表无行"; $fail = $true }
  else { Say "PASS" ("主问×小问结构表 {0} 行" -f $struct) }
}

Say "CHECK" "2/4 problem-brief.md"
if (-not (Test-Path $brief)) {
  Say "FAIL" "缺 01-problem\problem-brief.md"
  $fail = $true
} else {
  $b = [System.IO.File]::ReadAllText($brief, [System.Text.Encoding]::UTF8)
  if ($b -match '\{\{') { Say "FAIL" "有 {{占位符}} 残留"; $fail = $true } else { Say "PASS" "无占位符残留" }
  $rows = [regex]::Matches($b, '^\|\s*Q(\d+)\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]*)\|\s*$', 'Multiline')
  if ($rows.Count -eq 0) { Say "FAIL" "题型判断表无 Q 行"; $fail = $true }
  else {
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

Say "CHECK" "3/4 question-map.md（小问级十要素）"
if (-not (Test-Path $map)) {
  Say "FAIL" "缺 01-problem\question-map.md"
  $fail = $true
} else {
  $m = [System.IO.File]::ReadAllText($map, [System.Text.Encoding]::UTF8)
  if ($m -match '\{\{') { Say "FAIL" "有 {{占位符}} 残留"; $fail = $true } else { Say "PASS" "无占位符残留" }
  $subs = [regex]::Matches($m, '###\s*Q(\d+)\.(\d+)')
  $units = New-Object System.Collections.Generic.List[object]
  if ($subs.Count -gt 0) {
    Say "INFO" ("有小问结构：共 {0} 个小问" -f $subs.Count)
    foreach ($q in $subs) {
      $units.Add([pscustomobject]@{ Id = ("Q{0}.{1}" -f $q.Groups[1].Value, $q.Groups[2].Value); Index = $q.Index })
    }
  } else {
    $mains = [regex]::Matches($m, '##\s*Q(\d+)')
    if ($mains.Count -eq 0) { Say "FAIL" "既没有 ### Qx.y 小问，也没有 ## Q 主问小节"; $fail = $true }
    else {
      Say "INFO" ("无小问结构：共 {0} 个主问（按主问填表）" -f $mains.Count)
      foreach ($q in $mains) {
        $units.Add([pscustomobject]@{ Id = "Q{0}" -f $q.Groups[1].Value; Index = $q.Index })
      }
    }
  }
  if ($units.Count -gt 0) {
    $keys = @("输入","输出","决策变量","约束条件","可用方法","验证方式","隐含目标","隐含约束","链条关系","创新候选")
    foreach ($u in $units) {
      $start = $u.Index
      $next = $m.IndexOf('##', $start + 3)
      $block = if ($next -lt 0) { $m.Substring($start) } else { $m.Substring($start, $next - $start) }
      $qid = $u.Id
      foreach ($key in $keys) {
        $rm = [regex]::Match($block, '^\|\s*' + $key + '\s*\|\s*(.*?)\s*\|\s*$', 'Multiline')
        $val = $rm.Groups[1].Value.Trim()
        if (-not $val -or $val -match '\{\{' -or $val.Length -lt 1) {
          Say "FAIL" ("{0} 的[{1}]未填" -f $qid, $key)
          $fail = $true
        }
      }
      if ($block -notmatch '一句话建模思路：\s*\*\*\s*\S') {
        Say "FAIL" ("{0} 缺一句话建模思路" -f $qid)
        $fail = $true
      }
    }
    if (-not $fail) { Say "PASS" "所有建模单元十要素齐全" }
  }
}

Say "CHECK" "4/4 汇总"
if ($fail) { Say "RESULT" "拆题未完成，按 playbooks/dismantle.md 修复循环补格（最多 3 轮）。"; exit 1 }
Say "RESULT" "拆题产物全 PASS，可以进入数据 / 建模阶段。"
exit 0
