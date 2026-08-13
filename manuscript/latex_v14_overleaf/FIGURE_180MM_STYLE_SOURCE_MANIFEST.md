# V12 main-figure style and source manifest

| Item | Printed asset | SHA-256 | Final placement | Editable/vector source | Reproduction/source route |
|---|---|---|---:|---|---|
| Figure 1 | `figures/figure_1.pdf` | `eb5b604c5c6aa53f92cab46381edbc408101cc9488afc092bb1cf5daf4c9767c` | 180 mm | Yes: supplied `figure_1.svg` | Supplied author artwork; a) and b) normalized to the same 37.5-px bold label size; scientific content and geometry unchanged |
| Figure 2 | `figures/figure_2.pdf` | `c459317e526ad8b031ac1702993531198d6c07d54f6492dbefe2c53801e9e8d4` | 180 mm | Yes: `figure_2.svg` | `scripts/build_v12_main_figure2.py` + frozen V11 source tables |
| Figure 3 | `figures/figure_3.png` | `65762100331d70284ec4148c4c7359f748029cf0f3f34d83fabed1cd7cc2ba45` | 180 mm | Editable provenance source retained as `figures/figure_3_panel_label_source.svg` | Frozen ADNI publication asset; deterministic grid-free presentation transform |
| Figure 4 | `figures/figure_4.png` | `28de9e146acdc1c9b5431db6d677186716bf1a5d4cc8a1fca6ff077006cf7616` | 180 mm | Yes: cleaned `figure_4.svg`; preserved source `figure_4_v11_source.svg` | `scripts/build_gridfree_figure4_svg.py` + `scripts/render_v12_figure4_from_svg.ps1`; presentation-only removal of 63 grid groups and one empty annotation box |
| Figure 5 | `figures/figure_5.pdf` | `976b993cee26635ccdb65f341384462e6febac936012c6f4ea02b94292eb3913` | 170 mm | Yes: `figure_5.svg` | `scripts/build_cgga_figure5.py` + frozen aggregate CGGA tables |

All five main figures use white backgrounds, no background plotting grid, bold lowercase panel labels, and redundant marker/shape encoding where applicable. Figure 5 is a native 170-mm vector/raster build; Figure 3 remains a raster archival publication asset, with its editable pre-raster source retained only for provenance and typography validation.
