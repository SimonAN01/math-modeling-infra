# math-modeling-infra

> A Claude Code / Codex skill that organizes a math modeling competition project
> into a fixed file structure, so both you and every fresh agent window know
> where to read context and where to write results. **中文说明如下。**

用 Agent 协作做数学建模竞赛的项目工作流，做成了 skill。

核心想法和 [research-workflow](https://github.com/skJack/research-workflow) 一样：
**竞赛里人和 Agent 的协作，靠一套固定的文件结构来承载**——每个文档职责单一，
每个新开的 Agent 窗口都知道先读什么、往哪写。

## 学生快速开始（一条命令下载）

> 适用：学生自己建一个项目目录，进入目录后**执行一条命令**即可完成整个框架的下载，
> 框架会装进当前目录下的 `math-modeling-infra/` 子文件夹。

**Windows（PowerShell，推荐 git 版）：**

```powershell
git clone https://github.com/SimonAN01/math-modeling-infra.git math-modeling-infra
```

没有 git 的 Windows 备选（zip 下载，一条命令）：

```powershell
Invoke-WebRequest https://github.com/SimonAN01/math-modeling-infra/archive/refs/heads/main.zip -OutFile mm.zip; Expand-Archive mm.zip; Move-Item math-modeling-infra-main math-modeling-infra; Remove-Item mm.zip
```

**Linux / macOS（bash，推荐 git 版）：**

```bash
git clone https://github.com/SimonAN01/math-modeling-infra.git math-modeling-infra
```

没有 git 的 Linux/macOS 备选（zip 下载，一条命令）：

```bash
curl -L https://github.com/SimonAN01/math-modeling-infra/archive/refs/heads/main.zip -o mm.zip && unzip mm.zip && mv math-modeling-infra-main math-modeling-infra && rm mm.zip
```

下载完，仍在当前目录执行**一条命令**即可建好项目骨架（10 个模板文件 + 目录结构一次生成）：

```powershell
# Windows
powershell .\math-modeling-infra\scripts\init-project.ps1 .
```

```bash
# Linux / macOS
bash math-modeling-infra/scripts/init-project.sh .
```

## 安装

装完对 Agent 说「开个新坑，国赛 C 题」，它会问你三件事
（赛制题号、时间分工、数据位置），然后把整套结构建好。

建议同时安装配套的另外两个 skill：

- `scientific-figure-making` —— 论文出图规范
- `humanizer-zh` —— 定稿前去 AI 味

### Windows

```powershell
# PowerShell 7 或 5.1 均可；若脚本中文乱码，确认文件带 UTF-8 BOM（本仓库脚本已内置）
git clone https://github.com/SimonAN01/math-modeling-infra.git "$env:USERPROFILE\.claude\skills\math-modeling-infra"
# 用 Codex 则装到这里：
git clone https://github.com/SimonAN01/math-modeling-infra.git "$env:USERPROFILE\.codex\skills\math-modeling-infra"
```

开新项目（PowerShell 下必须用 ps1 版脚本）：

```powershell
powershell "$env:USERPROFILE\.claude\skills\math-modeling-infra\scripts\init-project.ps1" D:\competitions\cumcm-2026-c
powershell "$env:USERPROFILE\.claude\skills\math-modeling-infra\scripts\setup-env.ps1"  D:\competitions\cumcm-2026-c
powershell "$env:USERPROFILE\.claude\skills\math-modeling-infra\scripts\build-paper.ps1" D:\competitions\cumcm-2026-c
```

> 提示：Windows 上若已装 PowerShell 7（`pwsh`），建议改用 `pwsh` 代替 `powershell`，
> UTF-8 兼容性更好（无需依赖 BOM）。

### Linux

```bash
git clone https://github.com/SimonAN01/math-modeling-infra.git ~/.claude/skills/math-modeling-infra
# 用 Codex 则装到这里：
git clone https://github.com/SimonAN01/math-modeling-infra.git ~/.codex/skills/math-modeling-infra
```

开新项目：

```bash
bash ~/.claude/skills/math-modeling-infra/scripts/init-project.sh ~/Code/cumcm-2026-c
bash ~/.claude/skills/math-modeling-infra/scripts/setup-env.sh  ~/Code/cumcm-2026-c
bash ~/.claude/skills/math-modeling-infra/scripts/build-paper.sh ~/Code/cumcm-2026-c
```

> 提示：求解环境依赖 `uv`（`curl -LsSf https://astral.sh/uv/install.sh | sh`）；
> 论文编译依赖 XeLaTeX + ctex 宏包（`sudo apt install texlive-xetex texlive-lang-chinese` 或 TeX Live full）。

### macOS

```bash
git clone https://github.com/SimonAN01/math-modeling-infra.git ~/.claude/skills/math-modeling-infra
# 用 Codex 则装到这里：
git clone https://github.com/SimonAN01/math-modeling-infra.git ~/.codex/skills/math-modeling-infra
```

开新项目（与 Linux 同为 bash 脚本）：

```bash
bash ~/.claude/skills/math-modeling-infra/scripts/init-project.sh ~/Code/cumcm-2026-c
bash ~/.claude/skills/math-modeling-infra/scripts/setup-env.sh  ~/Code/cumcm-2026-c
bash ~/.claude/skills/math-modeling-infra/scripts/build-paper.sh ~/Code/cumcm-2026-c
```

> 提示：求解环境依赖 `uv`（`curl -LsSf https://astral.sh/uv/install.sh | sh`）；
> 论文编译依赖 XeLaTeX + ctex 宏包（`brew install --cask mactex-no-gui` 或 BasicTeX + ctex）。
> macOS 用 `.sh` 脚本即可；若装了 pwsh 也可用 `.ps1` 版。

## 项目结构

```
你的项目/
├── AGENTS.md                项目总纲：赛题、分工、硬规矩 —— 每个新窗口第一个读
├── handoff.md               进度交接 —— 每个窗口结束前更新
├── 01-problem/              拆题
│   ├── problem-brief.md     赛题总纲：目标、子问题、输出要求
│   ├── question-map.md      每问的输入 / 输出 / 变量 / 约束 / 验证
│   └── submission-rule.md   提交规则：格式、命名、附件
├── 02-data/
│   ├── raw/                 原始附件数据（永不覆盖）
│   ├── processed/           处理后数据
│   └── data-log.md          预处理留痕，论文「数据侧写」的素材
├── 03-models/
│   ├── model-review.md      六维审查矩阵（不过审不进 code/）
│   └── code/                uv 管理的 Python 求解项目
├── 04-results/
│   ├── results.md           每版结果一行，不覆盖不删
│   └── figures/             论文用图
├── 05-paper/
│   ├── paper-outline.md     论文骨架（国赛八股结构）
│   └── main.tex 等           CUMCMThesis 模板
└── 06-submission/
    └── checklist.md         赛前 48h + 提交前检查清单
```

## 脚本

**建骨架**（幂等，已有文件不覆盖）：

```bash
bash <skill>/scripts/init-project.sh ~/Code/cumcm-2026-c          # Linux / macOS
powershell <skill>/scripts/init-project.ps1 C:\Users\me\cumcm-2026-c   # Windows
```

**初始化求解环境**（uv 建项目 + 装常用依赖）：

```bash
bash <skill>/scripts/setup-env.sh <项目目录>                      # Linux / macOS
powershell <skill>/scripts/setup-env.ps1 <项目目录>               # Windows
```

**编译论文**（XeLaTeX 跑两遍 + 检查 PDF 是否生成）：

```bash
bash <skill>/scripts/build-paper.sh <项目目录>                    # Linux / macOS
powershell <skill>/scripts/build-paper.ps1 <项目目录>             # Windows
```

> 三个脚本均为幂等设计：已在项目里跑过、或项目文件已存在时，只会补缺，不会覆盖。

## 工作节奏

```
拆题 → 数据处理 → 建模审查 → 求解 → 写论文 → 提交
```

**六维审查在写代码之前。** 模型不过审不许写代码——先想清楚再动手，
让 AI 写的每一行代码都服务一个过过审的模型。

## 内置的几条警示

- 效果突然变好，先查数据泄漏（标准化用了全量均值和方差 / 验证集参与训练）
- 先精确解后启发式：能 LP/IP/MIP 就别一上来模拟退火、遗传
- 先判题型再选模型：预测 / 评价 / 优化，组合题别误判成纯优化题
- 数据每步留痕，不为了结果好看乱删数据
- 提交件与论文数字对不上 = 判负风险，走 checklist 核对

## License

Apache License 2.0
