# -*- coding: utf-8 -*-
"""数模标准图型：填数据就出图（中文 + png/pdf 双格式 + 数值标注）。

在 03-models/code/ 下使用：
    from figures import plots
    plots.hist_dist([...], bins=20, title="销量分布", xlabel="销量(kg)", ylabel="频数",
                    out="04-results/figures/sales-hist")

每种图型对应 playbooks/figures.md 里的清单条目；风格统一由 figures/style.py 负责。
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from figures import style
from figures.style import PALETTE, DEFAULT_COLORS
# 默认中文论文图：全模块统一应用出版样式（自定义脚本可再调 style.apply 覆盖）
style.apply("zh")


def hist_dist(series, bins: int = 20, *, title: str = "", xlabel: str = "",
              ylabel: str = "频数", out: str = "figures/hist", show_stats: bool = True):
    """直方图（数据侧写常用）。可选叠加均值/中位数竖线。"""
    x = style.as_array(series)
    fig, ax = plt.subplots(figsize=(6, 3.8))
    ax.hist(x, bins=bins, color=PALETTE["blue_main"], edgecolor="white", alpha=0.9)
    if show_stats:
        for v, lab, c in ((x.mean(), "均值", PALETTE["red_strong"]),
                          (np.median(x), "中位数", PALETTE["teal"])):
            ax.axvline(v, color=c, ls="--", lw=1.2)
            ax.text(v, ax.get_ylim()[1] * 0.92, f"{lab}{v:.2f}", color=c,
                    fontsize=9, rotation=90, va="top")
    ax.set_title(title); ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    style.save(fig, out)
    return out


def trend(x, series: dict, *, title: str = "", xlabel: str = "", ylabel: str = "",
          uncertainty: dict | None = None, out: str = "figures/trend",
          annotate_last: bool = True):
    """趋势/预测曲线。series: {图例名: y}；uncertainty: {图例名: (下界, 上界)} 画不确定性带。"""
    x = style.as_array(x)
    fig, ax = plt.subplots(figsize=(6, 3.8))
    for i, (label, y) in enumerate(series.items()):
        y = style.as_array(y)
        color = DEFAULT_COLORS[i % len(DEFAULT_COLORS)]
        ax.plot(x, y, color=color, lw=1.6, label=label)
        if uncertainty and label in uncertainty:
            lo, hi = style.as_array(uncertainty[label][0]), style.as_array(uncertainty[label][1])
            ax.fill_between(x, lo, hi, color=color, alpha=0.18)
        if annotate_last and len(y):
            ax.annotate(f"{y[-1]:.2f}", (x[-1], y[-1]), color=color, fontsize=8.5,
                        xytext=(4, 0), textcoords="offset points", va="center")
    ax.set_title(title); ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    if series: ax.legend()
    style.save(fig, out)
    return out


def heatmap(matrix, row_labels=None, col_labels=None, *, title: str = "",
            colorbar_label: str = "", out: str = "figures/heatmap", fmt: str = ".2f"):
    """相关性/混淆矩阵热力图。matrix: 2D；labels 与维度对齐。"""
    m = style.as_array(matrix)
    fig, ax = plt.subplots(figsize=(max(4.5, m.shape[1] * 0.7), max(4, m.shape[0] * 0.7)))
    im = ax.imshow(m, cmap="RdBu_r" if m.min() < 0 < m.max() else "Blues", aspect="auto")
    cb = fig.colorbar(im, ax=ax, shrink=0.9)
    if colorbar_label: cb.set_label(colorbar_label)
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            ax.text(j, i, fmt.format(m[i, j]), ha="center", va="center",
                    fontsize=9, color="white" if abs(m[i, j]) > (m.max() - m.min()) / 2 + m.min() else "black")
    if row_labels is not None: ax.set_yticks(range(m.shape[0]), row_labels)
    if col_labels is not None: ax.set_xticks(range(m.shape[1]), col_labels, rotation=45, ha="right")
    ax.set_title(title)
    style.save(fig, out)
    return out


def sensitivity_lines(perturb, curves: dict, *, baseline: float | None = None,
                      title: str = "灵敏度分析", xlabel: str = "参数扰动幅度(%)",
                      ylabel: str = "目标值", out: str = "figures/sensitivity"):
    """灵敏度折线：x=扰动幅度，每条线一个参数；baseline 画参考横线。"""
    x = style.as_array(perturb)
    fig, ax = plt.subplots(figsize=(6, 3.8))
    for i, (label, y) in enumerate(curves.items()):
        y = style.as_array(y)
        color = DEFAULT_COLORS[i % len(DEFAULT_COLORS)]
        ax.plot(x, y, marker="o", ms=3.5, color=color, lw=1.6, label=label)
    if baseline is not None:
        ax.axhline(baseline, color="grey", ls=":", lw=1.2)
        ax.text(x[0], baseline, f"基准 {baseline:.2f}", color="grey", fontsize=8.5, va="bottom")
    ax.axvline(0, color="grey", ls=":", lw=1.0)
    ax.set_title(title); ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    ax.legend()
    style.save(fig, out)
    return out


def grouped_bars(categories, series: dict, *, title: str = "", ylabel: str = "",
                 out: str = "figures/bars", annotate: bool = True, rotate: int = 0):
    """分组柱状图（方法对比/指标对比）。series: {组名: 值列表}。"""
    cats = list(categories)
    x = np.arange(len(cats))
    width = 0.8 / max(1, len(series))
    fig, ax = plt.subplots(figsize=(max(5, len(cats) * 0.9), 3.8))
    for i, (label, vals) in enumerate(series.items()):
        v = style.as_array(vals)
        bars = ax.bar(x + (i - (len(series) - 1) / 2) * width, v, width,
                      color=DEFAULT_COLORS[i % len(DEFAULT_COLORS)], label=label)
        if annotate:
            for b in bars:
                ax.annotate(f"{b.get_height():.2f}", (b.get_x() + b.get_width() / 2, b.get_height()),
                            ha="center", va="bottom", fontsize=8)
    ax.set_xticks(x, cats, rotation=rotate)
    ax.set_title(title); ax.set_ylabel(ylabel)
    if series: ax.legend()
    style.save(fig, out)
    return out


def scatter_fit(x, y, *, title: str = "", xlabel: str = "", ylabel: str = "",
                fit: bool = True, out: str = "figures/scatter"):
    """散点 + 线性拟合 + r/P 注释（相关性分析标配）。"""
    xa, ya = style.as_array(x), style.as_array(y)
    fig, ax = plt.subplots(figsize=(6, 3.8))
    ax.scatter(xa, ya, s=14, color=PALETTE["blue_main"], alpha=0.75, edgecolors="white", lw=0.4)
    note = ""
    if fit and len(xa) > 2:
        k, b = np.polyfit(xa, ya, 1)
        xs = np.linspace(xa.min(), xa.max(), 50)
        ax.plot(xs, k * xs + b, color=PALETTE["red_strong"], lw=1.6)
        r = np.corrcoef(xa, ya)[0, 1]
        note = f"y = {k:.3f}x + {b:.3f}\nr = {r:.3f}"
        ax.text(0.03, 0.97, note, transform=ax.transAxes, va="top", fontsize=9,
                bbox=dict(fc="white", ec="none", alpha=0.8))
    ax.set_title(title); ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    style.save(fig, out)
    return out
