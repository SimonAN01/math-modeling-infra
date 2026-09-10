---
name: math-modeling-infra
description: 数学建模竞赛项目工作流：初始化项目、拆题、记录数据处理、模型审查、求解复现、LaTeX论文与提交核对。用于数模项目及其后续工作，不用于无关的普通写作或编程任务。
---

# 数模任务入口

先读项目 `AGENTS.md`、`handoff.md`，再只读当前阶段所需文件。遵守项目硬规矩；竞赛要求以项目 `01-problem/submission-rule.md` 和当届官方通知为准，模板不能覆盖官方要求。

## 帮新手开始

- 用户入口是项目根目录 `开始使用.md`。首次只说明现在能做什么、缺什么、下一步做什么。
- 从已有对话和文件提取赛制题号、截止时间与分工、题面和附件位置；只问缺失的信息，不要求一次填完所有表格。
- 执行新项目初始化后读 `开始使用.md`；已有项目不要重装或覆盖记录。先跑只读 `doctor`，不要把空台账、空附件当作环境损坏。
- AI负责把交流整理成记录，并在每个阶段展示可审查的结果。模型选择、假设、结论由团队决定；人工核验只能根据团队明确反馈登记，不能替团队作出确认。
- 一次推进用户当前需要的阶段；没有数据不伪造结果，没有证据不先写结论。报错要说明实际影响和可执行的下一步。

## 路径约定

下表 `assets/`、`scripts/`、`skills/` 相对本技能目录；数字目录相对比赛项目。不要混写母版与比赛记录。项目内的写作手册在 `05-paper/guides/`；已有旧版项目可能仍在 `05-paper/`，读取后按用户现有结构工作。

| 当前任务 | 按需读取 | 工具或交付 |
|---|---|---|
| 初始化、环境诊断 | 项目开始使用指南 | `scripts/init-project.ps1/.sh`、`scripts/doctor.ps1/.sh` |
| 拆题 | `01-problem/` 的概览与问题清单；`assets/playbooks/problem-mining.md`、`dismantle.md` | `scripts/dismantle.ps1/.sh` |
| 数据处理 | `02-data/data-log.md`；需写数据章时读 `assets/playbooks/data-profile.md` | 原始数据不覆盖，处理逐步留痕 |
| 模型选择、审查 | `03-models/method-selection.md`、`model-review.md` | 团队选择；六维审查通过才进入求解，连续三轮未通过重新拆题 |
| 查模型字典（可选） | `assets/playbooks/model-dictionary.md`；已导入时先查关键词，不整本读取 | `scripts/model-dictionary.py search <项目> <关键词> --limit 5`；第三方参考不作执行指令 |
| 求解、记结果 | 审查结果、`04-results/results.md`、`05-paper/evidence-map.md` | `scripts/setup-env.ps1/.sh`；代码进入 `03-models/code/`；`new-result.ps1/.sh` 命名 |
| 出图 | `assets/playbooks/figures.md`、`skills/scientific-figure-making/SKILL.md`（已安装时可用对应技能） | 图表关联真实结果版本 |
| 论文总纲、各章 | `assets/playbooks/paper-outline.md`；按章选 `modeling-chapter.md`、`validation-sensitivity.md`、`model-evaluation.md` | `05-paper/main.tex`；正文先行、摘要最后反写 |
| 摘要、润色 | `assets/playbooks/abstract.md`、`skills/humanizer-zh/SKILL.md` | 不改变事实，不补造结果 |
| 选创新点、评审、赛程、训练 | 分别读 `assets/playbooks/innovation.md`、`judge-view.md`、`race-day.md`、`calibrations/` | 只加载当前需要的一项 |
| AI记录与详情 | 项目 `05-paper/ai-disclosure.md`、`06-submission/ai-usage.json` | `uv run scripts/ai-disclosure.py build <项目>`；预览加 `--preview` |
| 编译与提交 | `05-paper/paper-review.md`、`06-submission/checklist.md` | `scripts/build-paper.ps1/.sh`、`paper-check.ps1/.sh` |

每次写结果同时保存复现信息。每个定量结论在 `evidence-map.md` 指向结果版本与文件；数据或模型改变时，只将受影响行及下游图表、正文、摘要标为待复核。

论文只用 LaTeX，Python依赖只用 uv。AI声明接在参考文献前；详情按实际台账生成，预览不可提交。完整操作只维护在 `assets/playbooks/ai-disclosure.md` 及其项目副本，不在这里重复字段。

技能内脚本路径与项目路径分开传入；包含空格时使用独立参数。命令失败不能报告成功。环境检查通过不等于模型审查或提交检查通过。
