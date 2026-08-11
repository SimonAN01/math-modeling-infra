# CUMCMThesis LaTeX 模板

全国大学生数学建模竞赛官方 LaTeX 模板（原样保留，未改动任何文件）。

## 字体说明（重要）

模板通过文件名加载中文字体：`simsun.ttc`（宋体）和 `simkai.ttf`（楷体）。
这两个是微软专有字体，**不随仓库分发**（版权原因），需要自行提供：

- **Windows**：`build-paper` 脚本会在编译前自动从 `C:\Windows\Fonts` 拷贝进
  `05-paper/` 目录，无需手动操作
- **Linux / macOS**：把字体文件放到与 `main.tex` 同目录即可
  （可从安装了微软字体的电脑拷贝，或改用 Fandol 字体族自行配置）

## 用法

- 入口：`example.tex`（`cumcmthesis` 文档类）；如需 `main.tex`，从 `example.tex` 复制改写
- 编译：XeLaTeX + UTF-8（用框架的 `build-paper` 脚本）
- 2026 国赛规范：正文不要目录、≤ 30 页；电子版第一页为摘要专用页（承诺书/编号页不放电子版）

## 文件清单

- `cumcmthesis.cls` 文档类（未改动）
- `example.tex` 示例论文（作为正式论文的起点）
- `figures/` 示例图片（cat.pdf / smokeblk.pdf / f1.png 为示例内容，正式论文请替换）

> 已移除：simsun.ttc / simkai.ttf（微软字体，见上）、example.pdf（编译产物）、
> 示例预览图与公众号推广图。
