---
name: scientific-figure-making
description: Create or revise publication-ready scientific figures in Python/matplotlib for either an English version or a Chinese version. Use when building paper/report/slide figures such as bar charts, trend plots, scatter plots, heatmaps, dual-axis plots, or multi-panel layouts that need consistent styling, print-safe export, and reliable font handling for the chosen language.
---

# Scientific Figure Making

Use this skill for publication-ready matplotlib figures with a consistent house style and language-aware font support. In normal use, produce a pure English figure or a pure Chinese figure. Treat mixed-language labels as an exception that should be used only when the user explicitly asks for them.

Demos and style conventions come from the `figures4papers` repository. See [references/demos.md](references/demos.md) for project examples.

## Core workflow

1. Identify the figure goal, data structure, units, and target venue.
2. Choose the simplest figure type that answers the question clearly.
3. Apply publication style before creating axes.
4. Choose the language version first: pure English or pure Chinese.
5. If the chosen version is Chinese, switch to the CJK-capable font stack. Keep the Latin stack for English-only figures.
6. Export at publication quality, usually `png` plus `pdf`.

## Language handling

- Default to a single-language figure.
- If the user wants an English version, keep all labels, legends, and annotations in English.
- If the user wants a Chinese version, keep all labels, legends, and annotations in Chinese, while preserving units and standard symbols.
- Only use mixed Chinese and English text when the user explicitly requests it or when a term should remain untranslated.
- Keep labels short. Avoid long sentence-style titles in either language.
- Always preserve units and symbols exactly. Do not translate domain terms unless the user asks.
- Keep TeX disabled unless the environment is known-good and the figure needs math typesetting.

Read [references/api.md](references/api.md) for the style API and [references/design-theory.md](references/design-theory.md) for typography and layout rules. For bilingual font setup and export helpers, reuse [scripts/bilingual_publication.py](scripts/bilingual_publication.py).

## When to prefer this skill

- Final paper/report figures rather than exploratory plotting.
- Repeated figure production that must look consistent across a project.
- English-only or Chinese-only figures that must render reliably on different machines.
- Static matplotlib output that should be easy to export to vector and bitmap formats.

## When not to use it

- Interactive dashboards or browser-first charts.
- Heavy infographic or illustration work better handled in design tools.
- Complex 3D or GIS visualization.

## Common patterns

- Method comparison: grouped bars, tight y-range, direct value annotations if space allows.
- Trends over time or epochs: limited line count, restrained grid, optional uncertainty band.
- Correlation or matrix views: heatmap with explicit colorbar label.
- Composite figures: dedicate one panel to the legend instead of overlaying it on data.

## Common issues

| Issue | Fix |
| --- | --- |
| Chinese text shows as tofu or squares | Use the bilingual font stack and keep `axes.unicode_minus=False`. |
| English plot looks too heavy after enabling Chinese fonts | Keep the Latin fonts first for English-only figures; switch to CJK fallback only when needed. |
| Legend overlaps data | Move legend outside the axes or reserve a legend-only subplot. |
| Dense bars become unreadable | Widen the canvas, tighten the y-range, and reduce category count per row. |
| Export crops labels | Use the shared finalize helper with tight bounding box and small padding. |

## References

- [references/api.md](references/api.md)
- [references/design-theory.md](references/design-theory.md)
- [references/common-patterns.md](references/common-patterns.md)
- [references/tutorials.md](references/tutorials.md)
- [references/demos.md](references/demos.md)
