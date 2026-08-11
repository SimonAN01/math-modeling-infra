# API Reference

This reference defines the recommended conventions for publication-style figures in `scientific-figure-making`. Reuse the helper functions in [../scripts/bilingual_publication.py](../scripts/bilingual_publication.py) when you need deterministic font handling and export behavior for either an English figure or a Chinese figure.

## Typography and Language

### Language modes

- `en`: English-only labels and annotations.
- `zh`: Chinese-only labels and annotations.
- `mixed`: Chinese and English appear in the same figure. Use only when explicitly requested.
- `auto`: Detect CJK characters from a sample string and select the font stack automatically.

### Recommended font stacks

```python
LATIN_FONT_STACK = (
    "Arial",
    "Helvetica",
    "DejaVu Sans",
    "sans-serif",
)

CJK_FONT_STACK = (
    "Microsoft YaHei",
    "SimHei",
    "Noto Sans CJK SC",
    "Source Han Sans SC",
    "WenQuanYi Zen Hei",
    "PingFang SC",
    "Heiti SC",
)
```

For Chinese figures, prepend the CJK stack and keep the Latin stack as fallback. For English-only figures, keep the Latin stack only. Always set `axes.unicode_minus = False` so minus signs render correctly in Chinese-capable configurations.

## Constants

### PALETTE

```python
PALETTE = {
    "blue_main": "#0F4D92",
    "blue_secondary": "#3775BA",
    "green_1": "#DDF3DE",
    "green_2": "#AADCA9",
    "green_3": "#8BCF8B",
    "red_1": "#F6CFCB",
    "red_2": "#E9A6A1",
    "red_strong": "#B64342",
    "neutral": "#CFCECE",
    "highlight": "#FFD700",
    "teal": "#42949E",
    "violet": "#9A4D8E",
}
```

### DEFAULT_COLORS

```python
DEFAULT_COLORS = [
    PALETTE["blue_main"],
    PALETTE["green_3"],
    PALETTE["red_strong"],
    PALETTE["teal"],
    PALETTE["violet"],
    PALETTE["neutral"],
]
```

## FigureStyle

```python
@dataclass(frozen=True)
class FigureStyle:
    font_size: int = 16
    axes_linewidth: float = 2.5
    use_tex: bool = False
    language: str = "auto"
    sample_text: str | None = None
    font_family: tuple[str, ...] | None = None
```

- `font_size`: Use `24` for large comparison bars, `15-16` for compact subfigures.
- `axes_linewidth`: Use `3` for dense bar panels, `2-2.5` for compact plots.
- `use_tex`: Enable only for math-heavy labels in a known-good TeX environment.
- `language`: One of `auto`, `en`, `zh`, `mixed`.
- `sample_text`: Optional text snippet used for `auto` language detection.
- `font_family`: Override the computed fallback chain when the target machine has known fonts installed.

## Style and Export

### choose_font_family(language="auto", sample_text=None, ...)

Return the appropriate font fallback chain for English-only, Chinese-only, or explicitly mixed-language figures.

```python
font_family = choose_font_family(language="mixed", sample_text="Accuracy 准确率")
```

### apply_publication_style(style=None)

Configure matplotlib `rcParams` for publication output:

- top/right spines off
- frameless legends
- language-appropriate sans-serif fallback chain
- `svg.fonttype = "none"`
- `axes.unicode_minus = False`
- `savefig.bbox = "tight"`

```python
apply_publication_style(FigureStyle(language="zh", sample_text="能源消费"))
```

### finalize_figure(fig, out_path, formats=None, dpi=300, close=True, pad=0.05)

Save one or more outputs with tight bounding box and parent directory creation.

```python
finalize_figure(fig, "output/result", formats=["png", "pdf"], dpi=300, pad=0.06)
```

## Plot Helpers

Implement or adapt these helpers in figure scripts as needed:

- `make_grouped_bar`
- `annotate_bars`
- `make_trend`
- `make_heatmap`
- `make_scatter`
- `make_dual_axis`
- `make_sphere_illustration`

The important rule is consistency: use the same palette, font logic, export helper, and axis cleanup across all figures in a project.

## Validation Rules

- Convert numeric sequences to numpy arrays before plotting.
- `make_grouped_bar`: `len(categories)` must match the series width.
- `make_trend`: each `y` series must have the same length as `x`.
- `make_dual_axis`: both series must align to the same shared `x`.
- Export formats should normally be `png` plus `pdf`; add `svg` when editable vector text is needed.

## Usage Note

If the user explicitly asks for a Chinese version, an English version, or cross-machine font reliability, load the script at [../scripts/bilingual_publication.py](../scripts/bilingual_publication.py) before writing plotting code.
