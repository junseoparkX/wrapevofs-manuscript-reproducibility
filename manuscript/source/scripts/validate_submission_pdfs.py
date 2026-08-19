"""Validate submission-PDF page bounds and Supplementary display numbering."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pdfplumber


def inspect_pdf(path: Path, tolerance_pt: float = 1.0) -> dict[str, object]:
    pages: list[dict[str, object]] = []
    text_parts: list[str] = []
    with pdfplumber.open(path) as document:
        for page_number, page in enumerate(document.pages, start=1):
            text = page.extract_text() or ""
            text_parts.append(text)
            violations: list[dict[str, object]] = []
            for char in page.chars:
                if (
                    char["x0"] < -tolerance_pt
                    or char["x1"] > page.width + tolerance_pt
                    or char["top"] < -tolerance_pt
                    or char["bottom"] > page.height + tolerance_pt
                ):
                    violations.append(
                        {
                            "text": char.get("text", ""),
                            "x0": char["x0"],
                            "x1": char["x1"],
                            "top": char["top"],
                            "bottom": char["bottom"],
                        }
                    )
            pages.append(
                {
                    "page": page_number,
                    "characters": len(page.chars),
                    "images": len(page.images),
                    "blank": not text.strip() and not page.images,
                    "out_of_bounds_characters": violations,
                }
            )
    return {
        "path": str(path.resolve()),
        "page_count": len(pages),
        "blank_pages": [item["page"] for item in pages if item["blank"]],
        "pages_with_out_of_bounds_text": [
            item["page"] for item in pages if item["out_of_bounds_characters"]
        ],
        "pages": pages,
        "text": "\n".join(text_parts),
    }


def exact_numbered_labels(text: str, label: str, count: int) -> dict[str, object]:
    compact_text = re.sub(r"\s+", "", text)
    compact_label = re.sub(r"\s+", "", label)
    observed = {
        index: len(re.findall(rf"{re.escape(compact_label)}S{index}\.", compact_text))
        for index in range(1, count + 1)
    }
    return {
        "expected": count,
        "missing": [index for index, occurrences in observed.items() if occurrences == 0],
        "multiple_occurrences": [
            index for index, occurrences in observed.items() if occurrences > 1
        ],
        "occurrences": observed,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("main_pdf", type=Path)
    parser.add_argument("supplementary_pdf", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    main_report = inspect_pdf(args.main_pdf)
    supplementary_report = inspect_pdf(args.supplementary_pdf)
    supplementary_text = str(supplementary_report.pop("text"))
    main_report.pop("text")
    supplementary_report["figure_captions"] = exact_numbered_labels(
        supplementary_text, "Supplementary Figure", 28
    )
    supplementary_report["table_captions"] = exact_numbered_labels(
        supplementary_text, "Supplementary Table", 28
    )
    report = {"main": main_report, "supplementary": supplementary_report}

    failures = []
    for name, item in (("main", main_report), ("supplementary", supplementary_report)):
        if item["blank_pages"]:
            failures.append(f"{name}: blank pages {item['blank_pages']}")
        if item["pages_with_out_of_bounds_text"]:
            failures.append(
                f"{name}: out-of-bounds text on pages {item['pages_with_out_of_bounds_text']}"
            )
    for label in ("figure_captions", "table_captions"):
        item = supplementary_report[label]
        if item["missing"]:
            failures.append(
                f"supplementary {label}: missing={item['missing']}"
            )

    report["status"] = "PASS" if not failures else "FAIL"
    report["failures"] = failures
    payload = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
