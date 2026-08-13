# Main-figure panel-label audit

Date: 2026-08-09

## Scope and rule

The audit checks only whether the bold panel labels within each individual main figure use one font size. Different figures may use different sizes because they have different layouts and final widths. Plot-area geometry was not forced to be identical across scientifically different panels.

## Results

| Main figure | Labels | Within-figure source size | Result |
|---|---|---:|---|
| Figure 1 | a), b) | 37.5 px | Pass after normalizing a) from 37.795 px to 37.5 px |
| Figure 2 | a), b), c), d) | 9.0 px | Pass |
| Figure 3 | a), b), c) | 9.0 px | Pass; verified from the repository-local retained editable source used for the final raster |
| Figure 4 | a), b), c) | 9.0 px | Pass |
| Figure 5 | a), b), c) | 10.2 px | Pass |

All labels are bold. Figure 1 was the only mismatch. Its two editable SVG copies were changed identically, then the 180-mm vector PDF and PNG were regenerated through `scripts/render_v12_figure1_from_svg.ps1`. `figures/figure_3_panel_label_source.svg` is retained so the audit runs in an independent repository checkout without relying on an earlier manuscript-version directory. No data, panel geometry, caption, callout, or scientific result changed.
