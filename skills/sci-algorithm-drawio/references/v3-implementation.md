> v4 沿用本文件的数据结构与端口实现，但正式 CLI 另要求 `--references references.json`；新增关卡见 `reference-gate-schema.md`。旧命令仅有 --topology 已不完整。

# v3 脚本与场景约定

## 文件职责

`topology.json` 是先于坐标确认的关系表，`scene.json` 是几何、样式与命名端口映射，`figure.drawio` 是可编辑输出。三个文件分别核对；不从已经画错的图倒推“正确关系表”。

图种简单时可手写XML，但为同样的静态审核仍保留scene侧文件，或自行实现等价审计；不能只运行XML解析就称关系检查完成。

## topology 数据结构

见 `templates/topology-template.json` 和 `tests/fixtures/contract-topology.json`。每页使用与scene相同的id/name。nodes列出参与关系的节点：id、role、ports。port有direction(in/out/inout)与channel。edges有id、source/target、source_port/target_port、kind、meaning、condition、label、evidence、status。label可以为空，但来自decision的control／feedback分支必须有非空条件及可见短标签。

`evidence`为真实来源字符串；程序不能判断字符串是否真实，必须人工／模型读材料。`status=confirmed`只表示按材料审核，不代表用户手动审批。

## scene 数据结构

沿用旧版 nodes／edges 与相对父组坐标。新增：
- 页面 `paper.width_mm`（默认160），`paper.export_width_units`（选填，必须是实际完整导出范围）；`paper.min_text_pt`等纸面预算。
- 页面 `base_font_size` 与 `edge_font_size`；节点style可覆盖，但不得违反最终字号。
- 节点 `ports`：命名键对应 `{x,y,perimeter}`，x/y∈[0,1]。普通矩形默认perimeter=1。
- 边 `source_port/target_port`：引用真实节点端口。不能仅写style固定点而不登记逻辑端口。
- 边可有 `label_position`：`x`∈[-1,1]沿线相对位置，`y`为偏移，`dx/dy`为额外偏移。先小幅偏移，仍需渲染。
- `layout.adjacencies`：`{a,b,axis:"x"或"y",max_gap_em,reason}`。明确要检查的相邻对象。
- `layout.exceptions`：人工记录必要大空白、重合与跨线的原因；记录本身不自动消除告警。
- 节点 `allow_overlap_with`：仅经确认的真实层叠结构才可列对象id。

默认CLI构建需要`--topology`。`--draft`仅用于未完成的草案，并打印未做语义门控。低层Python函数build(scene)为旧结构测试保留非严格调用，不表示正式流程可跳过核验。

## 固定点写入

端口映射自动生成exitX/Y、entryX/Y，显式设置Dx/Dy=0、perimeter。边style若试图覆盖为不一致的固定点，构建器报错。默认startArrow=none、endArrow=block；annotation不显示箭头。不能把双向箭头用作两个单向语义。

## 审计边界

`audit_contracts.py`核对语义表、场景及输出XML的关系集合、端点、固定点、标签、方向；不是算法证明器。

`audit_layout.py`读取scene而非真实渲染。重叠与穿节点是几何风险检查；文字宽度采用Unicode字符宽度估计；自动路由不能确定的路径标为待渲染。它不运行Draw.io，不做OCR，不靠黑像素比例验密度。

真实渲染后必要时修正 `paper.export_width_units` 与标签几何，再跑检查。渲染图片不等于已目视检查；静态检查不等于已拖动交互测试。
