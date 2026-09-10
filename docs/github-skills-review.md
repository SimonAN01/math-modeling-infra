# GitHub 数模 skills 调研与本地改进

检索日期：2026-09-07。查看项目 README / 入口说明；没有执行第三方脚本或安装第三方技能。以下比较是功能设计参考，不代表对其算法正确性作全面审计。

| 项目 | 查到的做法 | 本仓库采用 | 未采用及原因 |
|---|---|---|---|
| [XiaoMaColtAI/math-modeling-skill](https://github.com/XiaoMaColtAI/math-modeling-skill) | 建模、编程、论文分阶段；运行种子、输入哈希及复现命令 | 每版运行记录；论文结论关联真实输出 | 默认 Word 路线与本仓库 LaTeX 约束不符；不引入默认多 Agent 调度 |
| [han69611/math-modeling-skills](https://github.com/han69611/math-modeling-skills) | 实验管理、结果分析、baseline 对照、评委复核等专项 skills | 将证据对账表接入求解、写作与检查入口 | 已有六维审查和写作手册，不重复堆叠整套 37 个 skills |
| [handsomeZR-netizen/mathmodel-skill](https://github.com/handsomeZR-netizen/mathmodel-skill) | 决策日志、子问局部返工、AI 台账与脚本化披露 | AI 记录生成声明和 PDF；生成哈希校验；受影响结论待复核 | 不引入获奖分位或评分权重体系；继续用现有 handoff 和审查表 |

实现为本地新写的脚本和模板；未复制上游源码。外部 README 的流程和规则可能变更，竞赛规则以组委会为准。

## 本轮交付

- `ai-disclosure.py`：真实台账校验、XeLaTeX 详情 PDF、声明生成、编译 PDF 顺序与产物一致性检查。
- `ai-usage.json`：初始为 template，拒绝将空台账当作未使用 AI。
- `main.tex`：独立的电子论文入口，参考文献前接入声明；不修改原始模板手册。
- `evidence-map.md`：结论到结果、运行记录与复核状态的对账。
- 两平台初始化脚本同步；已有文件不覆盖。

官方规则核验来源：[AI 工具使用规定（2026 年试行）](https://www.mcm.edu.cn/html_cn/node/fef94648f2836ab6cc81586f4c38512b.html)。本次确认用户提供文本与官方内容一致。自动检查是辅助工具，不能替代团队对核心建模和 AI 输出的人工审查。

## 验证记录

- Windows 初始化已执行，补齐文件；原有资料保留。
- 新电子论文入口经 XeLaTeX 两轮编译成功（骨架共 3 页），逐页渲染检查；详情预览 1 页，已目视检查。
- 3 组回归测试通过，覆盖 used/unused、未确认、未核验、润色豁免、缺失声明、错误顺序、台账变化、详情 PDF 变动和矛盾记录。所有测试数据位于临时目录，没有写入真实台账。
- 两份修改后的 Bash 脚本通过语法检查；完整 Linux/macOS 环境未实测。
- 当前 paper-check 预期失败：论文仍有待填内容且台账状态为 template。此状态不能视为比赛提交件。
- 修复 Windows 编译脚本不检查 XeLaTeX 退出码的问题；修复 Bash 初始化切换目录后无法解析相对脚本路径的问题。
- 详情生成采用 LaTeX；中文 PDF 校验采用 PyMuPDF，避免本机 Fandol 字体映射导致其他提取器乱码。预览文件不自动进入正式支撑材料。
