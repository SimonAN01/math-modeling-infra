# 数学建模 Infra 设计哲学与架构方案

> 本文件回答一个问题：这个仓库是"一堆好用文件的堆叠"，还是"一套可演进的系统"？
> 设计哲学综合自：Anthropic Agent Skills 官方规范、skill-authoring 社区最佳实践、
> "Building Claude Code" 技能使用经验分析，以及同类数模仓库（BZD-review-paper、MathModel-Skill）的实际架构。
> 来源链接见文末。

## 〇、一句话定位

**教科书 + 工具箱 + 状态分离**：

- 教科书——教 Agent "怎么写"（写作指南、评审要点、方法选型）；
- 工具箱——给它"能跑的东西"（init/setup/build 脚本），因为"最强大的不是知识，而是运行时能组合的代码"；
- 状态分离——"如何做"（本仓库）与"做到哪"（每个比赛项目的 AGENTS.md/handoff.md）永不混放。

## 一、设计哲学（8 条原则）

每条原则给：定义 → 对本文库的含义 → 现状自查。

### 1. Delta 原则——只写模型会错、不知道的东西

> 问自己：删掉这一行，模型还能答对吗？能 → 删。

- 含义：模板不解释"MAE 是什么"（模型本来就会），只写模型会翻车的点（"可行性先于最优性""自证式验证不算验证""Pearson 要先检验适用性"）。
- 现状：基本符合；`paper-outline.md` 里"公式用 equation/align 环境"这类常识可以继续瘦身。

### 2. 渐进披露——三层加载，一条引用深度

> L1 触发描述 → L2 SKILL.md 路由表 → L3 按需加载。禁止 A→B→C 引用链。

- 含义：SKILL.md 是路由器不是百科全书；细则全部外移到 playbooks/，按任务加载。
- 现状：⚠️ 有百科化倾向——硬规矩 8 条 + 警示 7 条把细则吸进本体；playbooks 间存在隐式链（paper-outline → modeling-chapter → judge-view），需要显式路由表（见第三节）。

### 3. 激活优于存储——规则必须挂在执行路径上

> 写在 references 里但从不出现在执行路径上的规则 = 死规则。

- 含义：新知识入库时必须同步挂到执行路径：AGENTS.md 的"先读什么"、SKILL.md 路由表、或 paper-review/checklist 的自查项。
- 现状：已做到（judge-view 挂进了 paper-review 自审清单）；入库流程要固化这条。

### 4. 过程优于声明——教动作，不教结果

> "输出必须有效"是声明；"跑校验器 → 修第一个错误 → 重跑，最多 3 轮"是过程。

- 含义：硬规矩逐条配过程。"六维审查不过不进 code/" → 过程是"填 model-review 表 → 逐维打分 → 不过回 question-map，三轮不过强制重拆题"（已有）。
- 现状：已有雏形，但部分规矩仍是声明态（"论文、结果文件、支撑材料三者一致"缺可执行步骤 → 脚本化候选）。

### 5. 默认值优于菜单——每个决策点一个默认

- 含义：模板默认 CUMCMThesis、编译默认 XeLaTeX、依赖默认 uv、算法呈现默认"算法框/Step 文字段二选一"（已有选择规则）。
- 现状：较好；继续审计"method-selection 12 张表"是否每个题型都有默认路径与最终判断句。

### 6. 结构服务内容——目录按信号生长

> 出现 ≥3 个独立主题 / ≥2 条任务路由 / 反复踩坑，才新增目录。禁止空目录脚手架。

- 含义：`assets/templates/` 现在 16 个文件混了两类东西——**骨架模板**（AGENTS.md、handoff.md 等带 {{占位符}} 的生成物）与**作战手册**（modeling-chapter、judge-view 等写作指南）。是时候分层，但只分这两层，不造第三层。
- 现状：⚠️ 需要分层（见第二节）。

### 7. 行动优先于知识的平衡——脚本化一切"机器可判"

> Anthropic 经验："最强大的技能是工具箱，不是教科书"；知识型技能的最高信号内容是 Gotchas（坑）。

- 含义：凡是"规则明确、机器可判"的检查都应变成脚本，而不是让 Agent 读 20 页手册逐条人工核对：
  - AI 套话扫描（"综上所述""值得注意的是"词表扫描）
  - 数字三方对账（摘要/正文/结果文件关键数字一致性）
  - 模板残留检查（{{占位符}}、示例标题未替换）
  - 结果命名规则校验（禁止 test2/final_v2）
- 现状：⚠️ scripts/ 只有 init/setup/build 三个，检查类全部靠人肉——这是最大的工具箱缺口（roadmap V2）。

### 8. 反漂移——第二次踩坑才入库

- 含义：同一坑第一次出现 → 记进 handoff；第二次出现 → 才写进 playbooks/警示。每次赛后复盘，把新坑蒸馏成"一条一句 + 锚点"。
- 现状：已有"警示"节；缺"赛后复盘 → 蒸馏 → 入库 → 挂执行路径"的固化流程（roadmap V3）。

## 二、目标架构：三层分离

```
math-modeling-infra/              ← 框架层（只放"如何做"，版本化、可安装）
├── SKILL.md                      ← L2 路由表（≤150 行，不存细则）
├── assets/
│   ├── playbooks/                ← 作战手册：写作指南与评审知识（paper-outline、
│   │                                modeling-chapter、judge-view、abstract、
│   │                                data-profile、validation-sensitivity、
│   │                                model-evaluation、method-selection…）
│   └── templates/                ← 项目骨架模板：带 {{占位符}} 的生成物
│                                    （AGENTS.md、handoff.md、problem-brief、
│                                    question-map、submission-rule、data-log、
│                                    model-review、results、paper-review、checklist）
├── scripts/                      ← 工具箱（幂等 CLI）：init-project / setup-env /
│   │                                build-paper / install-skills / paper-check ✅
│   │                                （待办：new-result）
├── skills/                       ← 打包的第三方 skill（humanizer-zh、
│                                    scientific-figure-making）
├── templates/CUMCMThesis         ← 外部资产（LaTeX 模板，原样）
└── docs/ARCHITECTURE.md          ← 本文件

<比赛项目>/                        ← 状态层（只放"做到哪"，不进框架仓库）
├── AGENTS.md + handoff.md        ← 状态与交接（每个新窗口前两读）
└── 01-problem … 06-submission

（未来可选）calibrations/         ← 证据层：每道题一条评审校准记录
                                    （仿 BZD-review-paper，赛后把官方评阅材料
                                    蒸馏成"本题扣分点"，供下届同题训练）
```

**关键判断**：骨架模板（生成物）与作战手册（知识）必须分目录——仓库侧 `templates/` 只放带 {{占位符}} 的生成物，`playbooks/` 只放写作知识。打包规则（2026-08-14 起）：`init-project` 把 `templates/` 全量拷入项目对应目录、把 `playbooks/` 的论文手册拷入 `05-paper/`——**项目保持自包含**（比赛期间无网络、队友未装 skill 也能工作），分层的收益在仓库侧：人和 Agent 一眼分清"生成物"与"知识"。

## 三、SKILL.md 目标形态（路由表）

参照 skill-authoring 的成熟形状（Always Read / Common Tasks / Known Gotchas）：

```markdown
---
name: math-modeling-infra
description: >-
  （触发词不变：开新坑/拆题/数据处理/建模/写论文/提交，
   以及"接着上次的做"这类省略语）
---

# 数学建模工作流

## 先读什么（每个窗口，按顺序）
1. AGENTS.md → 2. handoff.md → 3. 按任务读下表

## 任务路由表
| 任务 | 读什么（playbooks/） | 跑什么（scripts/） |
|---|---|---|
| 开新项目 | 问三件事 → init-project | init-project.sh/ps1 |
| 拆题 | problem-brief + question-map 模板 | — |
| 动数据 | data-log 模板 + data-profile 手册 | — |
| 选模型 | method-selection + model-review | — |
| 写某章 | 对应章节手册（paper-outline 是总纲） | — |
| 写论文环境 | — | setup-env |
| 编译论文 | paper-outline 的 LaTeX 硬规则 | build-paper |
| 提交前 | judge-view + paper-review + checklist | paper-check（V2） |

## 已知坑（一条一句 + 锚点）
（现有"警示"7 条搬到这里，每条加指向 playbooks 的锚点）

## 硬规矩（8 条不变，每条配过程句）
（"六维审查不过不进 code/" + "过程：填表→逐维打分→三轮不过重拆题"）
```

路由表是"激活优于存储"的落点：任何新 playbook 入库，必须同时出现在这张表里。

## 四、同类仓库架构对照（调研结论）

| 仓库 | 架构 | 可借鉴 | 不学 |
|---|---|---|---|
| [BZD-review-paper](https://github.com/BZDmathclub/BZD-review-paper) | SKILL.md=11 步编号流程，每步指名读哪个 references/；校准记录按题一条 | ①编号流程+固定读清单 ②"冻结评分细则再读论文"（过程优于声明）③calibrations 证据层 | SKILL.md 里大量输出格式细节（HTML 模板字段级），该外移 |
| [MathModel-Skill](https://github.com/yushui2022/MathModel-Skill) | 多技能拆分（paper-formal-writer 等），每技能 references/ | references 按主题命名（cumcm-paper-standard 等） | 多技能拆分——我们的流程是单链条（拆题→提交），拆开徒增路由开销 |
| [shuxue-jianmo-lunwen-pingshen](https://github.com/landawang-star/shuxue-jianmo-lunwen-pingshen) | 单 SKILL.md 百科型（16KB）+ 一个 references | 触发条件/输入规范/输出规范三段式清晰 | SKILL.md 过重，正是"百科化"反例 |
| 本仓库现状 | 单 skill + 混放 templates | — | 见第一节自查的 ⚠️ 项 |

**结论：保持"单 skill 多 playbook"**——不做多 skill 拆分（流程是一根链），学 BZD 的"编号流程 + 路由表 + 证据库"，避免 landawang 的百科化。

## 五、演进路线（分阶段，每步可独立验证）

- **V1（结构分层）** ✅ 已执行（2026-08-14）：`assets/templates/` 拆为 `playbooks/`（知识）+ `templates/`（骨架）；SKILL.md 收敛为路由表；init 脚本与交叉引用同步；冒烟测试通过。
- **V2（工具箱补缺）** ✅ 已完成（2026-08-14）：`scripts/paper-check`（占位符/AI 套话/命名/模板残留）+ `scripts/new-result`（结果命名生成器）均已上线（ps1 + sh）。
- **V3（证据层与复盘）** 🔶 部分完成：`calibrations/2023C.md`（官方评分细则蒸馏）已入库；赛后复盘 → 蒸馏新校准记录的流程待固化。

## 六、反模式清单（写作规范自警）

1. 过早脚手架——内容没到 3 个文件就建目录
2. 声明代替过程——"必须一致"写成"跑对账脚本"
3. 引用链 A→B→C——一条引用深度是硬约束
4. 百科式 SKILL.md——细则进本体，路由表失效
5. 只加知识不挂执行路径——playbook 入库不上路由表
6. 演示型脚本——能看不能跑（必须幂等 + 冒烟测试）
7. 未经真实比赛验证的规则入库——模板内容应来自真实论文与官方评阅材料，不来自想象

## 参考来源

- Anthropic Agent Skills 官方规范：https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills
- agentskills.io 规范：https://agentskills.io
- skill-authoring（技能设计六原则、质量关卡）：https://github.com/Ronifue/skill-authoring
- "Building Claude Code" 技能使用经验分析：https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering
- Claude Skills 渐进披露指南：https://skywork.ai/blog/claude-skills-progressive-disclosure-ultimate-guide/
- BZD-review-paper：https://github.com/BZDmathclub/BZD-review-paper
- MathModel-Skill：https://github.com/yushui2022/MathModel-Skill
- 国赛评审标准整理：https://github.com/landawang-star/shuxue-jianmo-lunwen-pingshen
