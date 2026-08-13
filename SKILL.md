---
name: math-modeling-infra
description: 用 Agent 协作做数学建模竞赛的项目工作流——建标准文件结构、拆题（problem-brief/question-map）、记数据处理留痕、六维审查、管结果版本、写 LaTeX 论文、打包提交。任何涉及开新赛题、搭数模项目、处理附件数据、建立模型、写论文、整理提交件的请求都用它——包括用户只说「开个新坑」「把这道题拆一下」「数据先处理了」「结果记一下」「接着上次的做」而没提「数模」两个字的时候。
---

# 数学建模工作流

把一场数学建模竞赛组织成固定的文件结构，让人和每一个新开的 Agent 窗口都知道：
去哪读上下文、往哪写结果。

## 每个窗口，先按顺序读

1. 项目的 `AGENTS.md` —— 赛题、分工、目录说明、硬规矩
2. 项目的 `handoff.md` —— 上一个窗口做到哪、下一步是什么
3. 按下面的任务表，只读你这件事需要的文件。**不要通读全仓库，上下文很贵。**

## 任务路由表

| 任务 | 读什么 | 跑什么 |
|---|---|---|
| 开新项目 | 先问三件事（见下），再建骨架 | `scripts/init-project <目录>`（幂等，只补缺不覆盖） |
| 拆题 | `templates/problem-brief.md`、`templates/question-map.md`、`templates/submission-rule.md` | — |
| 动数据 | `templates/data-log.md`（留痕）；写数据侧写章前读 `playbooks/data-profile.md` | — |
| 选模型 | `templates/method-selection.md`（12 张表 + 最终判断句）、`templates/model-review.md`（六维审查） | — |
| 求解 | 审查通过 → `03-models/code/`（uv 项目） | `scripts/setup-env <目录>` |
| 论文总纲 | `playbooks/paper-outline.md`（先读，八股结构与 LaTeX 硬规则） | — |
| 写"问题 X 的建立与求解" | `playbooks/modeling-chapter.md`（叙事链/依据三来源/去 AI 味清单） | — |
| 写数据侧写 | `playbooks/data-profile.md` | — |
| 写检验与灵敏度 | `playbooks/validation-sensitivity.md` | — |
| 写评价与推广 | `playbooks/model-evaluation.md` | — |
| 写摘要（最后写） | `playbooks/abstract.md` | — |
| 自审 | `playbooks/judge-view.md`（评委视角）+ `templates/paper-review.md` | `scripts/paper-check <目录>` |
| 编译论文 | `playbooks/paper-outline.md` 的 LaTeX 硬规则 | `scripts/build-paper <目录>` |
| 提交 | `templates/checklist.md` 逐项打勾 | `scripts/paper-check <目录>` |

> 路由表是唯一入口：任何新手册入库，必须同时出现在这张表里（激活优于存储）。

## 开新项目：先问，再建

先问用户三件事（不要多问）：

1. 赛制与题号（如国赛 C 题）+ 一句话说题目在做什么
2. 时间（开赛时间 / 剩余小时）+ 团队分工（建模 / 编程 / 写作）
3. 附件数据在哪、有没有官方提交模板（xlsx 结果表、承诺书等）

然后跑 `init-project` 建骨架，并把答案填进 `AGENTS.md` 的 `{{占位符}}`。
已有项目里跑也安全——只补缺的文件，不覆盖。

## 工作节奏

```
拆题 → 数据处理 → 建模审查 → 求解 → 写论文 → 自审 → 提交
```

- **六维审查在写代码之前。** 模型不过审不许进 `code/`。
- **选型先翻表。** 建任何模型前先翻 `method-selection.md` 的 12 张表，并回答最终选型判断句——为什么是它、前提是否成立、结果怎么验证、答辩守不守得住。
- **建模前先想清结果长什么样。** 每问先答：最终要数值、表格、曲线还是方案；哪些结果必须进正文、哪些是中间变量、哪些会被下一问继续调用。
- **Review Lane 在提交之前。** 先过 `paper-review.md`（质量），再过 `checklist.md`（合规）。

## 已知坑（第二次踩到才写进来）

1. **效果突然变好，先查数据泄漏，再庆祝。** 常见泄漏：标准化用了全量均值和方差、验证集参与训练、测试信息混进特征。
2. **先精确解，后启发式。** 能 LP / IP / MIP 求解别一上来模拟退火、遗传——精确解答辩好守得多。
3. **先判题型，再选模型。** 预测 / 评价 / 优化，组合题别误判成纯优化题。
4. **别把子问题机械套同一种方法。** 每一问都要独立回答"为什么这样建模"。
5. **验证中间过程，不只是看结果。** 逐块问输入、输出、数据怎么处理的，配合代码对一遍——小问题都藏在中间过程里。
6. **AI 输出必须逐项人工核验，核心建模与分析由人主导。** 隐瞒 AI 使用、虚假声明、未核验内容直接提交 = 取消评奖资格。
7. **提交前三方对账。** 论文、结果文件、支撑材料的数字、单位、命名必须完全一致；支撑材料与论文不符同样可能取消评奖资格。

## 硬规矩（每条都配了过程）

1. **决策在人，执行在 AI。** 模型选择、假设设定、结论判断必须人来定；AI 负责写代码、查报错、出图、润色、审逻辑。
2. **六维审查不过，不进 code/。** 过程：填 `model-review.md` 表格 → 逐维打分 → 不过回 `question-map.md` 重查；连续三轮不过，强制重新拆题。
3. **数据每步留痕。** 过程：每一步写 `data-log.md`（做了什么、为什么、影响多少样本）；原始数据不许覆盖。
4. **每版结果都有名字。** 过程：跑完就按 `results.md` 的 `v<序号>_<改动的核心>` 追加一行；禁止 `test2` / `final_v2` / 日期当名字。
5. **论文只用 LaTeX，依赖只用 uv。** 不裸用全局 pip，不 Word 成稿。
6. **摘要最后反写，定稿前过 humanizer-zh。** 过程：先写正文与结论 → 摘要从正文结果表抄数字 → 外行可读测试（`playbooks/abstract.md`）→ humanizer-zh 清 AI 味。
7. **提交前走 checklist。** 过程：`paper-check` 脚本先扫 → `paper-review.md` 自审 → `checklist.md` 逐项打勾。
8. **遵守 2026 国赛规则**（详见 `templates/submission-rule.md`）：电子版第一页为摘要专用页；正文 ≤ 30 页、不要目录；论文与支撑材料各 ≤ 20MB；全文无身份信息；参考文献之前写 AI 工具使用声明；用了 AI 就在支撑材料附 `AI工具使用详情.pdf`；核心建模由人主导。

## 装到 Agent

框架自带两个配套 skill（`scientific-figure-making` 出图规范、`humanizer-zh` 去 AI 味），装一次就是三个：

```bash
scripts/install-skills.sh ~/.claude/skills     # Claude Code / opencode
```
```powershell
powershell scripts\install-skills.ps1 "$env:USERPROFILE\.claude\skills"
```

装完对 Agent 说「开个新坑，国赛 C 题」即可。
