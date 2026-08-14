# 论文图表清单与规范

> 绘图的三个层次各司其职：
> 1. **风格规范** → 用打包的 `scientific-figure-making` skill（字体/配色/导出约定）
> 2. **图型与代码** → 用 `03-models/code/figures/`（style.py 统一样式 + plots.py 标准图型，填数据出图）
> 3. **每章该有什么图** → 本手册的清单
> 出完图：图放 `04-results/figures/`，论文 `05-paper/figures/` 引用同一份 png/pdf。

## 〇、硬规范（所有图通用）

- [ ] 中文图（数模论文一律中文图）；字体走 CJK 栈（style.py 已配好，缺字体则 Windows 装 SimHei/Microsoft YaHei）
- [ ] 一律导出 **png + pdf** 双格式（style.save 默认）
- [ ] 每张图**先正文引用、后插入**，图后有 2--3 句解读（`modeling-chapter.md` 结果解读句）
- [ ] 图题格式 `图5.1.1 xxx`，按序编号；图中直接标数值（评委可复算）
- [ ] 右、上边框去掉；图例不压数据；300dpi
- [ ] 图不求多，信息密度低的不放；太简单的图改成表（三线表）

## 一、每章图清单（按需取用，不是每章都要画全）

| 章节 | 需要的图 | 图型函数 |
|---|---|---|
| 数据侧写（五章） | 直方/分布图、趋势图（含季节性）、相关性热力图 | `hist_dist` / `trend` / `heatmap` |
| 问题一（数据关系） | 散点+拟合+r 注释、聚类散点、饼→改柱状 | `scatter_fit` / `grouped_bars` |
| 问题二（预测+决策） | 预测曲线 + 不确定性带、真实 vs 预测对比折线 | `trend`（带 uncertainty） |
| 问题三（优化扩展） | 结果策略表为主；必要时方案对比柱状 | `grouped_bars` |
| 模型检验（十章） | **灵敏度折线图**（多参数各一条 + 基准线）、误差对比柱状 | `sensitivity_lines` / `grouped_bars` |
| 评价与推广（十一章） | 通常无图（用表） | — |
| 问题分析（二章） | 技术路线图/思路流程图（高信息密度，不铺空白） | 自行绘制（drawio/PPT 均可，导出 png） |

## 二、常用图型要点（对照 plots.py）

1. **趋势图**：线数 ≤ 4；预测区间用浅色不确定性带；末点标数值
2. **热力图**：色带选对方向（正负相关用 RdBu_r，全正用 Blues）；格内标数值；colorbar 有标签
3. **灵敏度折线**：x=扰动幅度(%)，**0 处画参考竖线**，baseline 画参考横线；每参数一条线——这是检验章的核心图
4. **对比柱状**：柱顶标数值；组数 ≤ 5 避免拥挤
5. **散点拟合**：拟合线 + 方程 + r 值写进图内（显著性的 P 值写进正文）
6. **技术路线图**：只画一张（问题分析章末尾），把各问方法与数据流串起来

## 三、与 scientific-figure-making 的分工

- 风格细节（字体栈、调色板、多面板布局、双语出版）→ 读该 skill 的 `references/api.md` 与 `references/demos.md`
- 数模图型与函数 → `03-models/code/figures/plots.py`（本仓库维护，可直接改）
- 风格一致性 → 只从 `figures/style.py` 的 `apply()` 入口配置，不要在散落脚本里各自 `rcParams`

## 四、出图工作流

```
数据（02-data/processed 或结果对象）
  → 选图型（本手册清单）→ 调 plots.py 函数（填数据、题注、轴标签、out 路径）
  → style.save 出 png+pdf 到 04-results/figures/
  → 拷入/引用到 05-paper/figures/ → 正文先引用后插图 → 图后 2-3 句解读
```

## 五、常见坑

| 坑 | 处理 |
|---|---|
| 中文豆腐块 | style.apply("zh") 已配字体栈；Linux/macOS 需装 Noto Sans CJK 或文泉驿 |
| 负号显示方框 | apply() 已设 unicode_minus=False，别在散落脚本里覆盖 |
| 图导出裁边 | style.save 已用 bbox_inches=tight；自行 savefig 时同样加 |
| 图例压数据 | 移到图外或右侧留白（trend/sensitivity 函数已处理） |
| 颜色不统一 | 只用 PALETTE/DEFAULT_COLORS，不随手取色 |
