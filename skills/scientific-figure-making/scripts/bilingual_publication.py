from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import matplotlib as mpl
import matplotlib.pyplot as plt


LATIN_FONT_STACK: tuple[str, ...] = (
    "Arial",
    "Helvetica",
    "DejaVu Sans",
    "sans-serif",
)

CJK_FONT_STACK: tuple[str, ...] = (
    "Microsoft YaHei",
    "SimHei",
    "Noto Sans CJK SC",
    "Source Han Sans SC",
    "WenQuanYi Zen Hei",
    "PingFang SC",
    "Heiti SC",
)


def contains_cjk(text: str) -> bool:
    for char in text:
        code = ord(char)
        if 0x3400 <= code <= 0x9FFF or 0xF900 <= code <= 0xFAFF:
            return True
    return False


def choose_font_family(
    language: str = "auto",
    sample_text: str | None = None,
    preferred_cjk_fonts: Sequence[str] | None = None,
    preferred_latin_fonts: Sequence[str] | None = None,
) -> tuple[str, ...]:
    latin_fonts = tuple(preferred_latin_fonts or LATIN_FONT_STACK)
    cjk_fonts = tuple(preferred_cjk_fonts or CJK_FONT_STACK)

    if language not in {"auto", "en", "zh", "mixed"}:
        raise ValueError("language must be one of: auto, en, zh, mixed")

    if language == "en":
        return latin_fonts
    if language in {"zh", "mixed"}:
        return cjk_fonts + latin_fonts
    if sample_text and contains_cjk(sample_text):
        return cjk_fonts + latin_fonts
    return latin_fonts


@dataclass(frozen=True)
class FigureStyle:
    font_size: int = 16
    axes_linewidth: float = 2.5
    use_tex: bool = False
    language: str = "auto"
    sample_text: str | None = None
    font_family: tuple[str, ...] | None = None


def apply_publication_style(style: FigureStyle | None = None) -> None:
    style = style or FigureStyle()
    font_family = style.font_family or choose_font_family(
        language=style.language,
        sample_text=style.sample_text,
    )

    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": list(font_family),
            "font.size": style.font_size,
            "axes.labelsize": style.font_size,
            "axes.titlesize": style.font_size + 1,
            "xtick.labelsize": style.font_size - 1,
            "ytick.labelsize": style.font_size - 1,
            "legend.fontsize": style.font_size - 1,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": style.axes_linewidth,
            "legend.frameon": False,
            "figure.dpi": 100,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "svg.fonttype": "none",
            "axes.unicode_minus": False,
            "text.usetex": style.use_tex,
        }
    )


def finalize_figure(
    fig: plt.Figure,
    out_path: str | Path,
    formats: Iterable[str] | None = None,
    dpi: int = 300,
    close: bool = True,
    pad: float = 0.05,
    transparent: bool = False,
) -> list[Path]:
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if formats is None:
        formats = [path.suffix.lstrip(".")] if path.suffix else ["png", "pdf"]

    saved_paths: list[Path] = []
    stem = path.with_suffix("")
    for fmt in formats:
        fmt = fmt.lower()
        output = stem.with_suffix(f".{fmt}")
        fig.savefig(
            output,
            dpi=dpi,
            bbox_inches="tight",
            pad_inches=pad,
            transparent=transparent,
            facecolor="white",
        )
        saved_paths.append(output)

    if close:
        plt.close(fig)

    return saved_paths
