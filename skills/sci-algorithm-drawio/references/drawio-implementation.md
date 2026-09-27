> v4 正式流程见 SKILL.md 和 reference-gate-schema.md。下文中的 XML／脚本片段仅说明底层格式，不能代替先找原图与 --topology、--references 前置核验。

# 直接生成Draw.io：原生实现

本包scene.json是自定义构建格式，不是Draw.io官方JSON接口。v3端口、关系表、字号和紧凑规则以SKILL.md和v3-implementation.md为准。

## 1. 文件结构

生成UTF-8未压缩XML：mxfile → diagram → mxGraphModel → root。每页必须有id=0的根与id=1、parent=0的默认层。形状vertex=1；关系edge=1；不可同时设置。页内id唯一，文字是可编辑value。

坐标向右、向下增大。子对象的x/y相对真实父组，不是全图坐标；组只在视觉上包住内容，不等于已建立parent关系。

不要手工拼接带未转义字符的属性；用XML库转义。标签在scene中为纯文本，换行使用JSON的\n。构建器先做HTML安全转义，再XML序列化；不要预先转义成&amp;，避免重复转义。图内无公式，math=0不等于已经移除了公式标签。

## 2. 实际构建格式

完整可运行字段样本在tests/fixtures/contract-scene.json和contract-topology.json，**仅为回归测试的虚构控制关系**，不是论文事实或优秀版式模板。正式任务先填自己的topology与layout-plan，再写scene。

nodes：id、kind、label、parent（默认1）、x/y/w/h、style、ports（见v3-implementation）。支持rect、roundrect、ellipse、diamond、text、group、container、dashed_group、image。更多经过验证的原生形状可在任务代码扩展，不能对未知kind静默回退。

edges：id、source、target、source_port、target_port、kind；可选label/style/points/label_position。source/target必须存在；构建器自动把边放到两端共同的合适祖先。points属于该祖先局部坐标，不要误当全图坐标。

容器默认不可连接；应连到真实模块或接口，而不是大框边缘。命名端口在节点上定义相对x/y，边自动写出固定entry/exit属性。固定点不能用style偷偷覆盖成另一个位置。

## 3. 分组与层级

group无可见边界，container实线，dashed_group虚线。按语义使用真实parent；框、标题、对象分别可编辑。移动父组的效果要在真实编辑器验证，不能只根据XML计数保证。

先确定分区与阅读顺序，但框的实际宽高由子内容包络反算；不要用任意巨大容器充满页面。调整尺寸时保留可读字号，不使用全图缩放让错误间距与文字一起缩小。

## 4. 连接与路由

所有真实关系使用绑定ID的edge，显式固定entry/exit。非矩形用对应perimeter：ellipsePerimeter、rhombusPerimeter等；不能默认接到外包矩形。

orthogonalEdgeStyle只是路由起点，不会证明算法，也不保证避开所有障碍。先规划主支路与专用反馈通道，再指定必要waypoint。需要精确分段时按官方支持扩展segmentEdgeStyle并实际渲染检查，不能猜不存在的样式。

边可以用value作为可编辑短标签。label_position控制沿线位置与偏移，分支标签靠近所属出口但不压字。标签位置与线型仍以实际导出为准。

本包annotation同样绑定两端，且不加箭头。自由注解或更复杂端口需要扩展实现与审计；不能混作真实拓扑箭头。

## 5. 图片与编辑能力

默认纯算法图不含image。仅必要的用户原始照片等可以独立保留，中文、关系、简单节点与条带重建为原生元素。支持嵌入data:image URI，不自动抓外链。

SVG作为image仍是图片；整图切成几块大图也不是原生重构。条带、节点图、框和文字可组合成复杂视觉对象，而不是一律放进写着算法名的矩形。

## 6. 执行与重建

```bash
python3 "$SKILL_DIR/scripts/build_drawio.py" scene.json --topology topology.json --out figure.drawio
python3 "$SKILL_DIR/scripts/validate_drawio.py" figure.drawio --report qa-structure.json
python3 "$SKILL_DIR/scripts/audit_contracts.py" figure.drawio --scene scene.json --topology topology.json --report qa-connections.json
python3 "$SKILL_DIR/scripts/audit_layout.py" scene.json --report qa-layout.json
```

默认不覆盖已有文件；确认修订后用新版本名或--force。scene修改必须重新生成。手动改XML后应同步scene几何与标签，但**不能为迁就错误图修改科学关系表**。

## 7. 实际导出

```bash
python3 "$SKILL_DIR/scripts/probe_runtime.py" --out runtime.json
python3 "$SKILL_DIR/scripts/render_drawio.py" figure.drawio --page 1 --out qa-render.png --scale 2
```

需要已有Draw.io Desktop；DRAWIO_BIN或--binary可指定已有程序。无DISPLAY时使用已有xvfb-run。先看真实--help，不自动安装、不默认关闭沙箱，不上传论文。可以导出SVG，但仍保留.drawio源文件。

PNG格式签名检查不代表已看图。实际查看字体、重叠、端点、路线与最终尺寸，再单独做拖动和改字测试。没有环境时写明未执行。
