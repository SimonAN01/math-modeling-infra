# v4 参考记录字段与构建关卡

`references.json` 在写坐标前完成。它是实际研究的记录，不是让脚本代为搜索或自动推断科学关系。空模板见 `templates/references-template.json`；测试 fixture 只是合成数据，不能复制其中的链接与查看声明作为真实任务资料。

## 顶层

- `schema_version`：`4.0`。
- `task`：`algorithm`、`variant`、`figure_purpose` 非空。没有特别变体应写明，而不是空置。
- `search`：状态与实际查询记录。
- `sources`：已打开并查看的网上原始图示来源。
- `coverage`：本图关键机制及其拓扑对象／关系与参考的对应。
- `review`：对照当前材料的复核结果与拓扑指纹。

## search

`status=completed` 必须对应已经执行的检索。`runs` 每项：

```json
{
  "id": "S01",
  "query": "填写真正执行的检索词",
  "target_ids": ["M01"],
  "searched_at": "2026-09-25",
  "tool_record": "填写可追溯的搜索工具记录或本地浏览日志位置",
  "result_summary": "哪些来源被找到；哪些搜索失败；不是抄摘要"
}
```

M01 等是事先定义的机制需求 ID，也是 coverage 的 ID。一条查询可以覆盖多个有关机制，一份参考也可以覆盖一组对象；不用每根线单独检索。相同引用经过同一查询找到即可复用，无须复制查询凑数。

## sources

每个来源有 `id/title/url/figure_locator/source_type/roles/search_ids/inspection/reuse_note`。

- `url`：可追溯的原始 HTTP(S) 来源，不写含凭据的 URL。图像 CDN 可作附加定位，正文来源不能省略。
- `figure_locator`：实际图号、PDF 文件页码／印刷页码，或网页小节；多张图分别记录，避免含糊“见论文”。
- `source_type`：`primary_paper`、`author_resource`、`official_documentation`、`academic_teaching`。`secondary_source` 只作风格／发现记录，不用来通过机制关卡。
- `roles`：`mechanism`（内部机制）、`structure`（与本方法匹配的整体结构）、`style`（只借鉴表现风格）。纯 style 不满足机制覆盖。
- `search_ids`：该来源实际由哪些已记录查询发现。
- `reuse_note`：仅阅读参考、独立重绘还是改绘；需要进一步核实的许可／署名问题如实写，不默认“公开就能复制”。

`inspection`：

```json
{
  "status": "viewed",
  "method": "pdf_page_screenshot",
  "inspected_at": "2026-09-25",
  "visual_record": "实际查看图片／页面的工具记录或审阅日志位置",
  "visual_notes": "图中具体可见的对象、操作、箭头与汇合，不写空泛的已查看",
  "caption_notes": "图注说明的范围、对象或省略约定",
  "context_notes": "对应正文对版本、作用和适用条件的说明"
}
```

`method` 允许 `pdf_page_screenshot`、`web_image_view`、`local_image_view`、`browser_view`；只有下载、文本提取或缩略图不合格。若保留本地必要截图，可额外写 `local_evidence: {"path":"ref-cache/fig.png","sha256":"实际文件哈希"}`。路径必须在记录所在任务目录内；没有本地复制时保留真实工具查看记录即可。哈希只能证明文件未改变，不证明它是图片、看过了或支持本算法。

## coverage

每项：

```json
{
  "id": "M01",
  "page_id": "p1",
  "name": "填写当前机制名",
  "node_ids": ["实际拓扑节点ID"],
  "edge_ids": ["实际拓扑关系ID"],
  "source_ids": ["R01"],
  "match": "same_mechanism",
  "mapping_notes": "参考的哪些对象／关系对应本图的哪些对象／关系",
  "material_evidence": "当前论文小节或代码函数／行号支持本图范围",
  "excluded_details": ["具体不能照搬项；确无差异也必须说明核查范围"],
  "adaptation_notes": "中文标签、无公式呈现、紧凑组织如何改变且不改语义",
  "status": "verified"
}
```

`match` 可为 `same_mechanism`、`compatible_submechanism`、`custom_composition`。局部匹配的范围不能夸大；自定义组合还须 `custom_spec` 记录当前方法的组合依据，不假称来源本身包含组合关系。

所有 topology 中的语义节点和边都必须被一个或多个机制范围覆盖。辅助标题、纯装饰框不应混入语义 topology；简单输入输出可归入整体范围，不需要单独找图片。整张图贴一个不相干的来源不能通过实际人工核对，即使填表在技术上可满足字段。

## review 与指纹

```json
{
  "status": "complete",
  "topology_sha256": "当前拓扑的规范化JSON SHA-256",
  "notes": "实际核对的内容和差异处置，不是用户批准的替代声明"
}
```

获取指纹（只打印，不会自动改文件或宣称批准）：

```bash
python3 "$SKILL_DIR/scripts/audit_references.py"   --topology topology.json --print-fingerprint
```

核对完后手动／由代理明确写入。几何变化不影响指纹；拓扑中的语义、条件、证据等变化后需重新复核，不写自动刷指纹的脚本。

## 正式执行

```bash
python3 "$SKILL_DIR/scripts/audit_references.py" references.json   --topology topology.json --report qa-references.json
python3 "$SKILL_DIR/scripts/build_drawio.py" scene.json   --topology topology.json --references references.json --out figure.drawio
```

正式 CLI 同时要求这两个记录。`--draft` 只能用于明确待核对草案；提供了但无效的记录仍会报错，不会被此参数忽略。低层 `build(scene)` 是用于序列化与单元测试的函数，没有研究判断能力，正式任务不通过直接调用它绕开前置步骤。

手写 XML 仍须先审计相同记录；脚本不可能禁止用户或模型在别处另写文件，工作流必须同时遵守。无网络验证代码、无 OCR、无自动阅读真假判定；不要把 `reference_record_pass=true` 改称“参考真实性／科学正确性已证明”。
