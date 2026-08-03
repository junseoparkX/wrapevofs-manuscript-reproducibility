# WrapEvoFS manuscript V9 -- Overleaf package

This V9 folder is the publication-style LaTeX revision of the WrapEvoFS manuscript. It incorporates the development-only regret-constrained locking revision, the untruncated recommended GA mode, the associated aggregate reanalysis, and the limited prospective development-only AMP-AD Rush objective sensitivity.

Project repository (scheduled for public release upon publication): <https://github.com/junseoparkX/wrapevofs-package>

## Overleaf

1. Upload the complete folder as a ZIP or create a new blank Overleaf project and upload all files.
2. Set `main.tex` as the main document.
3. Set the compiler to **LuaLaTeX**.
4. Recompile. Overleaf runs the required LaTeX/BibTeX passes automatically.

## Local build

```sh
latexmk -lualatex main.tex
```

## Structure

- `main.tex`: document class, packages, title, abstract, bibliography, and section inputs.
- `sections/main_text.tex`: main manuscript text.
- `sections/supplementary.tex`: supplementary methods, figures, and tables.
- `tables/`: 39 table source files, including the algorithm table and all multipanel supplementary tables.
- `figures/`: 5 main figures and 18 supplementary figures, including development-only regret, locking-sensitivity, penalty-flattening diagnostics, and the AMP-AD Rush recommended-mode sensitivity.
- `supplementary_data/`: publication tables in CSV, Markdown, and LaTeX plus provenance for Supplementary Figure S18 and Supplementary Table S16.
- `references.bib`: 36 numbered references.

The manuscript uses a conventional monochrome journal style: TeX Gyre Termes text and math, one-inch margins, black section headings and captions, plain page numbers, and unshaded `booktabs`/`longtable` tables without vertical rules.

V9 retains the V8 Algorithm 1 hierarchy and adds the completed development-only AMP-AD Rush sensitivity without changing Main Figures 1--5. Every supplementary figure caption describes its displayed a), b), c), and, where present, d) panels individually.

All figures, tables, equations, and sections are numbered automatically. Continuous review line numbering is enabled with `lineno` (`\modulolinenumbers[1]`); change the value to `5` if a target journal requests numbering every fifth line. Use `\label{...}` with `\cref{...}` for future cross-references and `\citep{...}` for numeric citations.

The package uses a portable `article`-based layout so it compiles immediately on Overleaf. When a target journal is selected, its official class/template can replace the document class while the modular text, figures, tables, BibTeX database, labels, and citations remain reusable.
