# sci-algorithm-drawio v4.0

**读算法 → 上网找匹配原图 → 看原图、图注与正文 → 核对适配范围 → 冻结真实关系 → 设计整体结构 → 定字号和紧凑布局 → 原生 Draw.io → 检查与实际渲染。**

本版增加强制“参考先行”，保留 v3 对结构混乱、空白过多、小字号、乱连箭头与错误落点的全部主要约束。不调用生图，不经过 PPTX 或 Mermaid。

## 安装：备份旧版到技能目录之外

在压缩包所在目录执行。其他机器按实际路径调整。

```bash
set -e
ZIP=sci-algorithm-drawio-v4.zip
SKILLS=/home/zyl-zml/.codex/skills
BACKUPS=/home/zyl-zml/.codex/skill-backups
test -s "$ZIP"
unzip -t "$ZIP" >/dev/null
mkdir -p "$SKILLS" "$BACKUPS"
if [ -e "$SKILLS/sci-algorithm-drawio" ] || [ -L "$SKILLS/sci-algorithm-drawio" ]; then
  mv "$SKILLS/sci-algorithm-drawio" "$BACKUPS/sci-algorithm-drawio-$(date +%Y%m%d-%H%M%S)-$$"
fi
unzip "$ZIP" -d "$SKILLS"
```

主路径仍是 `/home/zyl-zml/.codex/skills/sci-algorithm-drawio/SKILL.md`。不要仅覆盖 SKILL 而遗留旧脚本。本包不修改其他技能，不安装全局依赖。

## 给 Codex 的调用文本

```text
读取 /home/zyl-zml/.codex/skills/sci-algorithm-drawio/SKILL.md，按 v4 执行。
先读我的论文／代码，再按具体算法、变体和关键操作上网找真实示意图。
必须打开原图、图注与相关说明核对，不得只看标题、摘要或缩略图。
先完成 references.json 和 reference-review.md，明确每个机制参考哪里、借鉴什么、哪些不能照搬。
我的 Draw.io 用来参考高信息密度的风格；本图关系仍以当前方法为准，不照抄网上别的变体。
没有关键参考或依据时先标缺口，不能凭印象补机制。原创组合分别查组件，组合边按当前方法核验。
然后冻结 topology、设计整体结构，按最终论文尺寸定字号，压缩无用间距与空白。
黑白灰主导，少量辅助色，中文优先，无公式。每条箭头有依据并绑定正确对象和固定端口。
直接输出可编辑 Draw.io，不调用生图，不经 PPTX。完成参考、结构、关系、版式和真实渲染检查。
未执行项目分别说明；记录检查不能代替实际看图与科学核验。
```

## 阅读与使用

主文件 `SKILL.md`。五项详细规范：`reference-first.md`、`structure-first.md`、`compact-layout.md`、`edge-contracts.md`、`qa-checklist.md`，都在 references/。

新增字段和命令见 `references/reference-gate-schema.md`；真实查阅方法示例见 `reference-review-example.md`。原始用户 Draw.io 与四张近似裁图保留，仍只作用户风格参考，不替代新算法的网上机制图。

`templates/` 有空参考记录与审阅表，`prompts/` 有生成与修改的完整调用文本。测试 fixture 全为合成场景与合成引用记录，不是科研案例，不要把 example 域名、查看声明或测试算法复制成真实依据。

## 脚本

| 脚本 | 用途 |
| --- | --- |
| audit_references.py / reference_gate.py | 检查记录、角色、机制覆盖与拓扑指纹；不联网、不看图、不证明科学真实性 |
| build_drawio.py | 按 scene 写原生 XML；正式 CLI 同时要求 --topology 与 --references |
| validate_drawio.py | 基础 XML／ID／几何检查 |
| audit_contracts.py | 关系表、scene 与 XML 的箭头、端点、标签和固定点核对 |
| audit_layout.py | 纸面字号估计、松散容器、间距、重叠与规划路线启发式检查 |
| inspect_drawio.py | 解析已有 Draw.io |
| probe_runtime.py / render_drawio.py | 探测和调用已有 Draw.io Desktop；导出不等于生图 |

Python 3.10+；基础脚本仅标准库。联网研究由当前代理的实际搜索／浏览工具执行；此包不假定某个联网插件存在，不自动安装，不上传论文。实际导出依赖可用 Draw.io Desktop，服务器可能需要已有 xvfb-run。

## 核验边界

见 `VALIDATION.md` 和 `tests/test-results-v4.txt`。本次交付技能升级，不是对当前论文某个算法做源图认证；没有收到新的具体算法与问题图，因此没有声称已替用户修复具体图片。网上来源和用户方法各自的真实内容仍须在实际任务中阅读。
