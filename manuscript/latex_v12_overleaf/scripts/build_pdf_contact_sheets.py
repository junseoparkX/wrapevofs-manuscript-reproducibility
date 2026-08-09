"""Build legible four-page contact sheets from rendered PDF page PNGs."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def build(input_dir: Path, output_dir: Path, prefix: str) -> None:
    pages = sorted(input_dir.glob("page-*.png"))
    if not pages:
        raise FileNotFoundError(f"No rendered pages found in {input_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype("C:/WINDOWS/Fonts/arial.ttf", 24)
    thumb_width = 816
    gutter = 36
    label_height = 42
    for sheet_index in range(math.ceil(len(pages) / 4)):
        group = pages[sheet_index * 4 : (sheet_index + 1) * 4]
        thumbnails: list[tuple[Path, Image.Image]] = []
        for path in group:
            with Image.open(path) as image:
                height = round(image.height * thumb_width / image.width)
                thumbnails.append((path, image.convert("RGB").resize((thumb_width, height))))
        cell_height = max(image.height for _, image in thumbnails) + label_height
        sheet = Image.new(
            "RGB",
            (2 * thumb_width + 3 * gutter, 2 * cell_height + 3 * gutter),
            "#d9d9d9",
        )
        draw = ImageDraw.Draw(sheet)
        for item_index, (path, image) in enumerate(thumbnails):
            row, column = divmod(item_index, 2)
            x = gutter + column * (thumb_width + gutter)
            y = gutter + row * (cell_height + gutter)
            sheet.paste(image, (x, y + label_height))
            draw.text((x, y + 6), path.stem, fill="black", font=font)
        destination = output_dir / f"{prefix}-sheet-{sheet_index + 1:02d}.png"
        sheet.save(destination, optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("prefix")
    args = parser.parse_args()
    build(args.input_dir, args.output_dir, args.prefix)


if __name__ == "__main__":
    main()
