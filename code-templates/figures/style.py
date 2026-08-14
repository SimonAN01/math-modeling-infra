# -*- coding: utf-8 -*-
"""数模论文统一绘图样式（与 skills/scientific-figure-making 的 api.md 约定一致）。

用法（在 03-models/code/ 下，uv 环境里）:
    from figures import style
    style.apply()          # 全局 rcParams：中文、去右/上边框、字号
    ...
    style.save(fig, "04-results/figures/corr-heatmap")   # 同时存 png + pdf

自包含实现：不依赖 skill 安装路径；字体栈/调色板与 scientific-figure-making 保持一致。
"""
from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

# ---- 字体栈（与 skill 约定一致）----
LATIN_FONT_STACK = ("Arial", "Helvetica", "DejaVu Sans", "sans-serif")
CJK_FONT_STACK = (
    "Microsoft YaHei", "SimHei", "Noto Sans CJK SC",
    "Source Han Sans SC", "WenQuanYi Zen Hei", "PingFang SC", "Heiti SC",
)

# ---- 调色板（与 skill 约定一致）----
PALETTE = {
    "blue_main": "#0F4D92", "blue_secondary": "#3775BA",
    "green_1": "#DDF3DE", "green_2": "#AADCA9", "green_3": "#8BCF8B",
    "red_1": "#F6CFCB", "red_2": "#E9A6A1", "red_strong": "#B64342",
    "neutral": "#CFCECE", "highlight": "#FFD700",
    "teal": "#42949E", "violet": "#9A4D8E",
}
DEFAULT_COLORS = [
    PALETTE["blue_main"], PALETTE["green_3"], PALETTE["red_strong"],
    PALETTE["teal"], PALETTE["violet"], PALETTE["neutral"],
]


def apply(language: str = "zh", font_size: float = 11.0,
          axes_linewidth: float = 1.2, use_tex: bool = False) -> None:
    """应用出版物级全局样式。language: 'zh' | 'en' | 'mixed'。"""
    fonts = CJK_FONT_STACK + LATIN_FONT_STACK if language in ("zh", "mixed") else LATIN_FONT_STACK
    matplotlib.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": list(fonts),
        "font.size": font_size,
        "axes.linewidth": axes_linewidth,
        "axes.unicode_minus": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "legend.frameon": False,
        "svg.fonttype": "none",
        "savefig.bbox": "tight",
        "savefig.dpi": 300,
    })
    if use_tex:
        matplotlib.rcParams["text.usetex"] = True


def save(fig, out_path: str, formats=("png", "pdf"), dpi: int = 300,
         close: bool = True, pad: float = 0.05) -> None:
    """导出多格式（默认 png + pdf，投稿要求双格式），自动建目录。"""
    import os
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    for fmt in formats:
        fig.savefig(f"{out_path}.{fmt}", dpi=dpi, bbox_inches="tight", pad_inches=pad)
    if close:
        plt.close(fig)


def annotate_bars(ax, fmt: str = "{:.2f}", fontsize: float = 9.0) -> None:
    """柱顶直接标数值（评委可复算的锚点）。"""
    for rect in ax.patches:
        h = rect.get_height()
        if h == h and h != 0:  # 跳过 nan 与零值
            ax.annotate(fmt.format(h), (rect.get_x() + rect.get_width() / 2, h),
                        ha="center", va="bottom", fontsize=fontsize)


def as_array(x):
    return np.asarray(x, dtype=float)
