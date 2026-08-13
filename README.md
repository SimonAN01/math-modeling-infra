# math-modeling-infra

用 Agent 协作做数学建模竞赛的项目工作流（skill）。每个文档职责单一，每个新开的 Agent 窗口都知道先读什么、往哪写。

参考 [research-workflow](https://github.com/skJack/research-workflow) 的设计，适配国赛 C 题场景：拆题 → 数据处理 → 建模审查 → 求解 → 写论文 → 提交。

## 快速开始

在自己建好的项目目录里执行一条命令（下载框架 + 建好项目骨架，10 个模板文件一次生成）：

**Windows（PowerShell）：**

```powershell
git clone https://github.com/SimonAN01/math-modeling-infra.git math-modeling-infra; powershell -NoProfile -ExecutionPolicy Bypass -File .\math-modeling-infra\scripts\init-project.ps1 .
```

**Linux / macOS：**

```bash
git clone https://github.com/SimonAN01/math-modeling-infra.git math-modeling-infra && bash math-modeling-infra/scripts/init-project.sh .
```

然后按 `AGENTS.md` 里的提示填好赛题信息，对 Agent 说「开始拆题」即可。

> 依赖：git；求解环境需 [uv](https://astral.sh/uv/)；论文编译需 XeLaTeX + ctex 宏包（MiKTeX / TeX Live / mactex）。

## 安装为 skill

框架**自带**两个配套 skill：`scientific-figure-making`（出图规范）、`humanizer-zh`（定稿前去 AI 味），都打包在仓库 `skills/` 子目录里——装一次就是三个：

```bash
# 克隆后一条命令装齐（含自带的两个配套 skill）
bash math-modeling-infra/scripts/install-skills.sh ~/.claude/skills      # Claude Code / opencode
bash math-modeling-infra/scripts/install-skills.sh ~/.codex/skills       # Codex
```

```powershell
# Windows
git clone https://github.com/SimonAN01/math-modeling-infra.git "$env:USERPROFILE\.claude\skills\math-modeling-infra"
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.claude\skills\math-modeling-infra\scripts\install-skills.ps1" "$env:USERPROFILE\.claude\skills"
```

装完对 Agent 说「开个新坑，国赛 C 题」，它会问你三件事（赛制题号、时间分工、数据位置），然后把整套结构建好。

## 项目结构

```
你的项目/
├── AGENTS.md                项目总纲：赛题、分工、硬规矩 —— 每个新窗口第一个读
├── handoff.md               进度交接 —— 每个窗口结束前更新
├── 01-problem/              拆题：problem-brief / question-map / submission-rule
├── 02-data/                 raw/（原始数据，不覆盖）+ processed/ + data-log.md 留痕
├── 03-models/               model-review.md 六维审查（不过审不进 code/）+ method-selection.md（12 张方法选型表）+ code/（uv 项目）
├── 04-results/              results.md 每版结果一行 + figures/ 论文用图
├── 05-paper/                paper-outline.md（八股结构 + LaTeX 硬规则）+ 章节模板（abstract / data-profile / validation-sensitivity / model-evaluation）+ judge-view.md（评委视角与评审要点）+ paper-review.md（自审/收口）+ CUMCMThesis 模板（建骨架时自动拷入）
├── 06-submission/           checklist.md 赛前 48h + 提交前检查
```

> CUMCMThesis 模板随仓库自带（`templates/CUMCMThesis`，原样未改），
> 微软字体（simsun.ttc / simkai.ttf）不随仓库分发——Windows 下 `build-paper`
> 会从系统字体目录自动补齐，Linux / macOS 需自行放入字体。

## 脚本

| 脚本 | 作用 | Windows | Linux / macOS |
|---|---|---|---|
| `init-project` | 建骨架（幂等） | `powershell scripts\init-project.ps1 <目录>` | `bash scripts/init-project.sh <目录>` |
| `setup-env` | uv 建环境 + 装依赖 | `powershell scripts\setup-env.ps1 <目录>` | `bash scripts/setup-env.sh <目录>` |
| `build-paper` | XeLaTeX 编译论文 | `powershell scripts\build-paper.ps1 <目录>` | `bash scripts/build-paper.sh <目录>` |
| `paper-check` | 提交前自动检查（占位符残留 / AI 套话 / 结果命名 / 模板残留） | `powershell scripts\paper-check.ps1 <目录>` | `bash scripts/paper-check.sh <目录>` |

> 以上命令**不必手动记**——对 Agent 说「初始化环境」「编译论文」即可，它会自动执行对应脚本。`init-project` 已包含在快速开始的一条命令里，不用再跑。三个脚本均幂等，重复运行安全。

## 工作节奏

```
拆题 → 数据处理 → 建模审查 → 求解 → 写论文 → 提交
```

**六维审查在写代码之前。** 模型不过审不许写代码。

## 警示

- 效果突然变好，先查数据泄漏（标准化用了全量均值 / 验证集参与训练）
- 先精确解后启发式：能 LP/IP/MIP 就别一上来模拟退火、遗传
- 先判题型再选模型：预测 / 评价 / 优化，组合题别误判成纯优化题
- 数据每步留痕，不为了结果好看乱删数据
- 提交件与论文数字对不上 = 判负风险，走 checklist 核对

## License

- 框架本体：Apache License 2.0
- 自带 `humanizer-zh`：MIT（原作者 歸藏）
- 自带 `scientific-figure-making`：MIT（源自 [figures4papers](https://github.com/SimonAN01/figures4papers)）
