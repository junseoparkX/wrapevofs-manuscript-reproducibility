"""Renumber Supplementary figures and tables by first main-text citation.

This is an editorial-only transformation.  Figure/table bodies and source
assets are not changed.  The script reorders LaTeX display blocks, updates all
numeric labels and citations simultaneously, and writes an explicit mapping.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "sections" / "main_text.tex"
SUPP = ROOT / "sections" / "supplementary.tex"
TABLES = ROOT / "tables"

FIGURE_ORDER = [17, 18, 15, 16, 1, 2, 3, 12, 13, 21, 7, 8, 19, 22, 23, 25, 26, 27, 20, 9, 10, 11, 4, 6, 5, 14, 24]
TABLE_ORDER = [16, 18, 19, 20, 15, 3, 4, 12, 13, 14, 22, 7, 8, 9, 10, 23, 24, 21, 5, 6, 11, 25, 26, 17, 1, 2]
FIGURE_MAP = {old: new for new, old in enumerate(FIGURE_ORDER, start=1)}
TABLE_MAP = {old: new for new, old in enumerate(TABLE_ORDER, start=1)}

TABLE_FILE_GROUPS = {
    1: range(5, 6),
    2: range(6, 7),
    3: range(7, 9),
    4: range(9, 13),
    5: range(13, 16),
    6: range(16, 21),
    7: range(21, 22),
    8: range(22, 23),
    9: range(23, 24),
    10: range(24, 27),
    11: range(27, 29),
    12: range(29, 33),
    13: range(33, 35),
    14: range(35, 37),
    15: range(37, 38),
    16: range(38, 39),
    17: range(39, 40),
    18: range(40, 41),
    19: range(41, 42),
    20: range(42, 43),
    21: range(43, 44),
    22: range(44, 45),
    23: range(45, 46),
    24: range(46, 47),
    25: range(47, 48),
    26: range(48, 49),
}
FILE_TO_TABLE = {number: old for old, numbers in TABLE_FILE_GROUPS.items() for number in numbers}


def simultaneous_tokens(text: str, prefix: str, mapping: dict[int, int]) -> str:
    placeholders: dict[str, str] = {}
    for old, new in mapping.items():
        token = f"{prefix}{old}"
        placeholder = f"@@{prefix.replace(':', '_').upper()}_{old}@@"
        text = re.sub(re.escape(token) + r"(?!\d)", placeholder, text)
        placeholders[placeholder] = f"{prefix}{new}"
    for placeholder, replacement in placeholders.items():
        text = text.replace(placeholder, replacement)
    return text


def expand_sequence(sequence: str) -> list[int]:
    values: list[int] = []
    for start, end in re.findall(r"S(\d+)(?:--S(\d+))?", sequence):
        first = int(start)
        if end:
            values.extend(range(first, int(end) + 1))
        else:
            values.append(first)
    return values


def format_sequence(values: list[int]) -> str:
    if len(values) == 1:
        return f"S{values[0]}"
    if values == list(range(values[0], values[-1] + 1)):
        return f"S{values[0]}--S{values[-1]}"
    if len(values) == 2:
        return f"S{values[0]} and S{values[1]}"
    return ", ".join(f"S{value}" for value in values[:-1]) + f", and S{values[-1]}"


CITATION = re.compile(
    r"Supplementary (?P<kind>Fig\.|Figs\.|Figure|Figures|Table|Tables)~"
    r"(?P<seq>S\d+(?:(?:--|, | and )S\d+)*)"
)


def remap_hardcoded_citations(text: str, *, figures: bool) -> str:
    mapping = FIGURE_MAP if figures else TABLE_MAP

    def replace(match: re.Match[str]) -> str:
        kind = match.group("kind")
        is_figure = kind.startswith("Fig")
        if is_figure != figures:
            return match.group(0)
        mapped = [mapping[value] for value in expand_sequence(match.group("seq"))]
        if len(mapped) == 1:
            normalized = "Fig." if kind in {"Fig.", "Figs."} else "Figure"
            if not figures:
                normalized = "Table"
        else:
            normalized = "Figs." if kind in {"Fig.", "Figs."} else "Figures"
            if not figures:
                normalized = "Tables"
        return f"Supplementary {normalized}~{format_sequence(mapped)}"

    return CITATION.sub(replace, text)


def figure_groups(section: str) -> dict[int, str]:
    blocks = re.findall(r"\\begin\{figure\}.*?\\end\{figure\}\s*", section, flags=re.S)
    groups: dict[int, list[str]] = {}
    current: int | None = None
    for block in blocks:
        label = re.search(r"\\label\{fig:supp(\d+)\}", block)
        if label:
            current = int(label.group(1))
            groups[current] = [block]
        elif current is not None:
            groups[current].append(block)
        else:
            raise RuntimeError("Unlabelled supplementary figure block is not a continuation")
    if set(groups) != set(range(1, 28)):
        raise RuntimeError(f"Unexpected figure groups: {sorted(groups)}")
    return {number: "".join(parts) for number, parts in groups.items()}


def reorder_figures(supplementary: str) -> str:
    start_token = "\\section{Supplementary Figures}"
    end_token = "\\section{Supplementary Tables}"
    before, remainder = supplementary.split(start_token, 1)
    figure_section, after = remainder.split(end_token, 1)
    groups = figure_groups(figure_section)
    rendered: list[str] = []
    for old in FIGURE_ORDER:
        block = groups[old]
        block = block.replace(f"Supplementary Figure S{old}", f"Supplementary Figure S{FIGURE_MAP[old]}")
        rendered.append(block.strip() + "\n")
    return before + start_token + "\n\n" + "\n".join(rendered) + "\n" + end_token + after


def table_groups(section: str) -> dict[int, str]:
    lines = section.splitlines(keepends=True)
    groups: dict[int, list[str]] = {}
    current: int | None = None
    current_lines: list[str] = []
    pending: list[str] = []
    input_pattern = re.compile(r"\\input\{tables/table_(\d+)\.tex\}")
    for line in lines:
        match = input_pattern.search(line)
        if not match:
            pending.append(line)
            continue
        table_file = int(match.group(1))
        old = FILE_TO_TABLE.get(table_file)
        if old is None:
            raise RuntimeError(f"Unmapped table fragment table_{table_file:02d}.tex")
        if current is None:
            current = old
            current_lines = pending + [line]
        elif old == current:
            current_lines.extend(pending + [line])
        else:
            groups[current] = current_lines
            current = old
            current_lines = pending + [line]
        pending = []
    if current is None:
        raise RuntimeError("No supplementary table inputs found")
    current_lines.extend(pending)
    groups[current] = current_lines
    if set(groups) != set(range(1, 27)):
        raise RuntimeError(f"Unexpected table groups: {sorted(groups)}")
    return {number: "".join(lines) for number, lines in groups.items()}


def reorder_tables(supplementary: str) -> str:
    start_token = "\\section{Supplementary Tables}"
    before, table_section = supplementary.split(start_token, 1)
    groups = table_groups(table_section)
    rendered = [groups[old].strip() + "\n" for old in TABLE_ORDER]
    return before + start_token + "\n\n" + "\n".join(rendered)


def update_table_labels() -> None:
    for path in sorted(TABLES.glob("table_*.tex")):
        text = path.read_text(encoding="utf-8")
        updated = simultaneous_tokens(text, "tab:supp", TABLE_MAP)
        if updated != text:
            path.write_text(updated, encoding="utf-8")


def main() -> None:
    output = ROOT / "documentation" / "validation" / "SUPPLEMENTARY_FIRST_CITATION_RENUMBERING.json"
    if output.exists():
        raise RuntimeError("Supplementary first-citation renumbering has already been applied")
    main_text = MAIN.read_text(encoding="utf-8")
    supplementary = SUPP.read_text(encoding="utf-8")

    main_text = remap_hardcoded_citations(main_text, figures=True)
    main_text = remap_hardcoded_citations(main_text, figures=False)
    main_text = simultaneous_tokens(main_text, "fig:supp", FIGURE_MAP)
    main_text = simultaneous_tokens(main_text, "tab:supp", TABLE_MAP)

    supplementary = reorder_figures(supplementary)
    supplementary = reorder_tables(supplementary)
    supplementary = remap_hardcoded_citations(supplementary, figures=True)
    supplementary = remap_hardcoded_citations(supplementary, figures=False)
    supplementary = simultaneous_tokens(supplementary, "fig:supp", FIGURE_MAP)
    supplementary = simultaneous_tokens(supplementary, "tab:supp", TABLE_MAP)

    update_table_labels()
    MAIN.write_text(main_text, encoding="utf-8")
    SUPP.write_text(supplementary, encoding="utf-8")

    payload = {
        "basis": "first explicit citation in sections/main_text.tex before renumbering",
        "figure_old_to_new": {f"S{old}": f"S{new}" for old, new in FIGURE_MAP.items()},
        "table_old_to_new": {f"S{old}": f"S{new}" for old, new in TABLE_MAP.items()},
        "scientific_content_changed": False,
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "figures": len(FIGURE_MAP), "tables": len(TABLE_MAP)}, sort_keys=True))


if __name__ == "__main__":
    main()
