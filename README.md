# 数模工作流

帮你把题目、数据、模型、结果和论文放在同一个项目里，按阶段推进。模型、假设与结论由团队决定，AI负责执行和整理。

## 已经有项目

打开项目根目录的 **开始使用.md**。先让 AI 读 `AGENTS.md` 和 `handoff.md`，报告当前进度与下一步；不用再克隆框架，也不用先安装技能。

[预览新手指南](assets/templates/开始使用.md) · [AI详情表格说明](assets/playbooks/ai-disclosure.md)

## 创建另一个比赛项目

从本框架目录运行以下任一命令。目标目录可以包含中文和空格；只补缺失文件，不覆盖已有资料。

Windows：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/init-project.ps1 "C:/你的比赛项目"
```

macOS / Linux：

```bash
bash scripts/init-project.sh "$HOME/你的比赛项目"
```

然后在 AI 助手中打开新建项目，把题面放入 `01-problem/`，附件放入 `02-data/raw/`，按“开始使用”中的示例提问。AI整理过程记录；团队确认模型选择和核验结果。

## 文件分工

| 位置 | 用途 |
|---|---|
| 比赛项目根目录 | 当前赛题的工作区，日常在这里操作 |
| `01-problem` 至 `06-submission` | 题目、数据、模型、结果、论文、提交件 |
| 项目中的 `05-paper/guides/` | 写作参考手册，按需打开 |
| 本框架的 `assets/`、`scripts/`、`templates/` | 可复用的母版与工具；修改后用于以后新建的项目 |
| `SKILL.md` | 给 AI 的任务入口，新手不必通读 |

框架模板与项目记录有意分开：比赛中填写项目文件；框架升级不会自动覆盖已填写资料。

## 需要时才用的工具

以下路径相对本框架目录。命令由 AI执行即可，不要求新手背下来。

| 想做什么 | 脚本 | 使用时机 |
|---|---|---|
| 看环境是否准备好 | `doctor.ps1` / `doctor.sh` | 第一次使用；只读，不安装软件 |
| 准备 Python 环境 | `setup-env.ps1` / `setup-env.sh` | 开始求解前，依赖用 uv |
| 编译论文 | `build-paper.ps1` / `build-paper.sh` | `05-paper/main.tex` 已有正文后 |
| 生成 AI 声明和详情 | `ai-disclosure.py build` | 团队完成记录核验后；先看 AI使用说明 |
| 提交检查 | `paper-check.ps1` / `paper-check.sh` | 内容接近完成时，空骨架失败是正常的 |
| 拆题完整性检查 | `dismantle.ps1` / `dismantle.sh` | 拆题后 |
| 给结果版本命名 | `new-result.ps1` / `new-result.sh` | 一次求解结束后 |

只读检查示例：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/doctor.ps1 "C:/你的比赛项目"
```

阅读和整理材料不依赖求解环境；运行Python需要 uv，生成PDF需要 XeLaTeX 与中文宏包。工具存在不代表宏包齐全，赛前实际编译一次。CUMCMThesis 的微软字体不随框架分发；Windows 编译脚本可从系统字体目录补齐，其他系统需提供模板所需字体。

## 可选 安装为技能

在多个项目重复使用时再安装。安装会更新目标目录中的同名文件，保留其他文件；本项目直接使用无需此步。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/install-skills.ps1 "$env:USERPROFILE/.codex/skills"
```

```bash
bash scripts/install-skills.sh "$HOME/.codex/skills"
```

目标目录可换为所用助手的技能目录。安装包括数模框架、出图规范、算法图、三线表、正文衔接和语言润色技能；框架所需模板与代码资源一并复制。

## 维护与来源

竞赛要求维护在项目 `01-problem/submission-rule.md`，执行核对维护在 `06-submission/checklist.md`；其他页面只提供入口。详细任务路由见 [SKILL.md](SKILL.md)，本轮外部参考与取舍见 [GitHub调研](docs/github-skills-review.md)。规则以当届官方通知为准。

框架本体：Apache License 2.0；humanizer-zh：MIT（原作者歸藏）；scientific-figure-making：MIT（源自 figures4papers）。具体范围以各目录许可证为准。

## 章节写作与质量核查

本轮整合20份写作材料，新增重述、分析、假设、符号、文献附录和证据评分指南。项目入口是 `05-paper/guides/writing-workflow.md`，每章提供输入、提示词和验收项；Windows/Bash初始化自动分发。材料来源与规则取舍见 [整合记录](docs/writing-materials-integration.md)。
