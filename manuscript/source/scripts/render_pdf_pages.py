"""Render every PDF page to a numbered PNG for visual quality assurance."""

from __future__ import annotations

import argparse
from pathlib import Path

import pypdfium2 as pdfium


def render(pdf_path: Path, output_dir: Path, scale: float) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    existing = list(output_dir.glob("page-*.png"))
    if existing:
        raise FileExistsError(
            f"Refusing to mix renders with {len(existing)} existing page PNGs in {output_dir}"
        )
    document = pdfium.PdfDocument(pdf_path)
    for page_index in range(len(document)):
        image = document[page_index].render(scale=scale).to_pil()
        image.save(output_dir / f"page-{page_index + 1:03d}.png", optimize=True)
    return len(document)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--scale", type=float, default=1.6)
    args = parser.parse_args()
    page_count = render(args.pdf, args.output_dir, args.scale)
    print(f"Rendered {page_count} pages from {args.pdf} to {args.output_dir}")


if __name__ == "__main__":
    main()
