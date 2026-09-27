# 技术来源与规则属性

检索日期：2026-09-25。下面为Draw.io官方说明；软件界面与版本差异仍以当前本机为准。此包离线构建XML，不要求在线访问文档。未将任何官方网页整篇打包。

1. 官方AI图生成入口：XML格式、验证与端点参考。
   https://www.drawio.com/docs/reference/diagram-generation/
2. 官方样式参考：source/target、fontSize像素语义、entry/exit坐标、perimeter、edgeStyle、groups。
   https://www.drawio.com/docs/reference/diagram-generation/style-reference/
3. Fixed与floating连接的区别：固定连接点在移动节点后保持对应点。
   https://www.drawio.com/doc/faq/connector-fixed-vs-floating
4. 自定义连接点：相对坐标points数组；显示连接点、人工固定点与实际绑定的区别。
   https://www.drawio.com/docs/manual/shapes/shape-connection-points-customise/
5. 基础流程图与连接、waypoint说明。
   https://www.drawio.com/docs/getting-started/basic-flowchart/

本技能的9.5–11pt目标、间距F比例、关系白名单、结构候选比较和验收门槛是针对用户任务制定的工作规则，不是声称顶刊顶会、数学建模国赛或Draw.io官方有此强制标准。

比例字号估计来自等比缩放几何，不代表字体度量或导出实现保证。自动审计不验证科学真实性；固定连接点不验证算法关系，也不保证自动路由无碰撞。

## v4 增量与来源边界

本次重新访问 Draw.io 官方 AI 生成入口与样式文档，确认原生 XML、对象 ID 与端点规则；这些文档仅作格式来源，不能充当算法机制参考。

本次参考研究方法示例实际查看 He 等的 arXiv:1512.03385v1，文件第2页图2及第3页3.2节；详情见 reference-review-example.md。它不是当前用户论文的算法依据，也未作为模板默认机制。

参考先行、适配记录、查不到不编画和构建前阻断是本任务制定的工作要求，不是声称所有期刊都实施这种流程。
