# 把框架及自带的两个配套 skill 装到 Agent 的 skills 目录（Windows PowerShell）。
#
#   powershell .\install-skills.ps1 "$env:USERPROFILE\.claude\skills"   # Claude Code / opencode
#   powershell .\install-skills.ps1 "$env:USERPROFILE\.codex\skills"    # Codex
#   powershell .\install-skills.ps1                                      # 默认 ~/.claude/skills
#
# 幂等：重复执行会覆盖同名文件。

param([string]$Dest = "$env:USERPROFILE\.claude\skills")

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

New-Item -ItemType Directory -Path (Join-Path $Dest "math-modeling-infra") -Force | Out-Null
Copy-Item (Join-Path $Root "SKILL.md")  (Join-Path $Dest "math-modeling-infra\") -Force
Copy-Item (Join-Path $Root "README.md") (Join-Path $Dest "math-modeling-infra\") -Force
Copy-Item (Join-Path $Root "assets")    (Join-Path $Dest "math-modeling-infra\") -Recurse -Force
Copy-Item (Join-Path $Root "scripts")   (Join-Path $Dest "math-modeling-infra\") -Recurse -Force

foreach ($s in @("scientific-figure-making", "humanizer-zh")) {
  Copy-Item (Join-Path $Root "skills\$s") (Join-Path $Dest $s) -Recurse -Force
}

Write-Host "已安装到 $Dest:"
Write-Host "  - math-modeling-infra（数模工作流）"
Write-Host "  - scientific-figure-making（出图规范）"
Write-Host "  - humanizer-zh（去 AI 味）"
