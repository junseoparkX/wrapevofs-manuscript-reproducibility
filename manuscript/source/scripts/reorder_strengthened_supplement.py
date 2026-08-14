"""Reorder current Supplementary displays by first main-text citation.

This is an editorial-only transformation. It moves complete figure/table
blocks and updates their printed labels and citations simultaneously. It does
not modify a figure asset, table value, selected mask, or empirical result.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "sections" / "main_text.tex"
SUPP = ROOT / "sections" / "supplementary.tex"
TABLES = ROOT / "tables"
OUTPUT = ROOT / "documentation" / "validation" / "SUPPLEMENTARY_STRENGTHENED_RENUMBERING.json"

# Current printed numbers in order of first explicit main-text citation.
FIGURE_ORDER = [1, 2, 3, 4, 16, 17, 18, 28, 10, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 19, 20, 21, 22, 23, 24, 25, 26, 27]
TABLE_ORDER = [1, 2, 3, 4, 5, 28, 11, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]
FIGURE_MAP = {old: new for new, old in enumerate(FIGURE_ORDER, 1)}
TABLE_MAP = {old: new for new, old in enumerate(TABLE_ORDER, 1)}

# Historical table fragments and the first renumbering map identify every
# fragment's current printed table without relying on visual table content.
HISTORICAL_GROUPS = {
    1: range(5, 6), 2: range(6, 7), 3: range(7, 9), 4: range(9, 13),
    5: range(13, 16), 6: range(16, 21), 7: range(21, 22), 8: range(22, 23),
    9: range(23, 24), 10: range(24, 27), 11: range(27, 29), 12: range(29, 33),
    13: range(33, 35), 14: range(35, 37), 15: range(37, 38), 16: range(38, 39),
    17: range(39, 40), 18: range(40, 41), 19: range(41, 42), 20: range(42, 43),
    21: range(43, 44), 22: range(44, 45), 23: range(45, 46), 24: range(46, 47),
    25: range(47, 48), 26: range(48, 49),
}
FIRST_MAP_PATH = ROOT / "documentation" / "validation" / "SUPPLEMENTARY_FIRST_CITATION_RENUMBERING.json"


def simultaneous_tokens(text: str, prefix: str, mapping: dict[int, int]) -> str:
    placeholders: dict[str, str] = {}
    for old, new in mapping.items():
        token = f"{prefix}{old}"
        placeholder = f"@@{prefix.replace(':', '_').replace(' ', '_').upper()}_{old}@@"
        text = re.sub(re.escape(token) + r"(?!\d)", placeholder, text)
        placeholders[placeholder] = f"{prefix}{new}"
    for placeholder, replacement in placeholders.items():
        text = text.replace(placeholder, replacement)
    return text


def expand_sequence(sequence: str) -> list[int]:
    values: list[int] = []
    for start, end in re.findall(r"S(\d+)(?:(?:--|–)S(\d+))?", sequence):
        first = int(start)
        values.extend(range(first, int(end) + 1) if end else [first])
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
    r"(?P<seq>S\d+(?:(?:--|–|, | and )S\d+)*)"
)


def remap_citations(text: str, *, figures: bool) -> str:
    mapping = FIGURE_MAP if figures else TABLE_MAP

    def replace(match: re.Match[str]) -> str:
        kind = match.group("kind")
        is_figure = kind.startswith("Fig")
        if is_figure != figures:
            return match.group(0)
        mapped = [mapping[value] for value in expand_sequence(match.group("seq"))]
        if figures:
            normalized = ("Fig." if kind in {"Fig.", "Figs."} else "Figure") if len(mapped) == 1 else ("Figs." if kind in {"Fig.", "Figs."} else "Figures")
        else:
            normalized = "Table" if len(mapped) == 1 else "Tables"
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
            raise RuntimeError("Unlabelled figure appears before any labelled figure")
    if set(groups) != set(range(1, 29)):
        raise RuntimeError(f"Unexpected figure groups: {sorted(groups)}")
    return {number: "".join(parts) for number, parts in groups.items()}


def reorder_figures(supplementary: str) -> str:
    start = "\\section{Supplementary Figures}"
    end = "\\section{Supplementary Tables}"
    before, remainder = supplementary.split(start, 1)
    figure_section, after = remainder.split(end, 1)
    groups = figure_groups(figure_section)
    rendered = []
    for old in FIGURE_ORDER:
        block = groups[old]
        block = block.replace(f"Supplementary Figure S{old}", f"Supplementary Figure S{FIGURE_MAP[old]}")
        rendered.append(block.strip() + "\n")
    return before + start + "\n\n" + "\n".join(rendered) + "\n" + end + after


def current_file_to_table() -> dict[int, int]:
    first = json.loads(FIRST_MAP_PATH.read_text(encoding="utf-8"))
    historical_to_current = {int(old[1:]): int(new[1:]) for old, new in first["table_old_to_new"].items()}
    result: dict[int, int] = {}
    for historical, files in HISTORICAL_GROUPS.items():
        for file_number in files:
            result[file_number] = historical_to_current[historical]
    # Tables 49 and 50 were added after the historical renumbering pass.
    result[49] = 27
    result[50] = 28
    return result


def table_groups(section: str) -> dict[int, str]:
    file_map = current_file_to_table()
    lines = section.splitlines(keepends=True)
    groups: dict[int, list[str]] = {}
    current: int | None = None
    current_lines: list[str] = []
    pending: list[str] = []
    pattern = re.compile(r"\\input\{tables/table_(\d+)\.tex\}")
    for line in lines:
        match = pattern.search(line)
        if not match:
            pending.append(line)
            continue
        current_table = file_map[int(match.group(1))]
        if current is None:
            current = current_table
            current_lines = pending + [line]
        elif current_table == current:
            current_lines.extend(pending + [line])
        else:
            groups[current] = current_lines
            current = current_table
            current_lines = pending + [line]
        pending = []
    if current is None:
        raise RuntimeError("No table inputs found")
    current_lines.extend(pending)
    groups[current] = current_lines
    if set(groups) != set(range(1, 29)):
        raise RuntimeError(f"Unexpected table groups: {sorted(groups)}")
    return {number: "".join(parts) for number, parts in groups.items()}


def reorder_tables(supplementary: str) -> str:
    start = "\\section{Supplementary Tables}"
    before, section = supplementary.split(start, 1)
    groups = table_groups(section)
    rendered = [groups[old].strip() + "\n" for old in TABLE_ORDER]
    return before + start + "\n\n" + "\n".join(rendered)


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError("Strengthened Supplementary renumbering already applied")
    main_text = MAIN.read_text(encoding="utf-8")
    supplementary = SUPP.read_text(encoding="utf-8")

    main_text = remap_citations(main_text, figures=True)
    main_text = remap_citations(main_text, figures=False)
    main_text = simultaneous_tokens(main_text, "fig:supp", FIGURE_MAP)
    main_text = simultaneous_tokens(main_text, "tab:supp", TABLE_MAP)

    supplementary = reorder_figures(supplementary)
    supplementary = reorder_tables(supplementary)
    supplementary = remap_citations(supplementary, figures=True)
    supplementary = remap_citations(supplementary, figures=False)
    supplementary = simultaneous_tokens(supplementary, "fig:supp", FIGURE_MAP)
    supplementary = simultaneous_tokens(supplementary, "tab:supp", TABLE_MAP)

    for path in sorted(TABLES.glob("table_*.tex")):
        text = path.read_text(encoding="utf-8")
        updated = simultaneous_tokens(text, "tab:supp", TABLE_MAP)
        if updated != text:
            path.write_text(updated, encoding="utf-8")

    MAIN.write_text(main_text, encoding="utf-8")
    SUPP.write_text(supplementary, encoding="utf-8")
    OUTPUT.write_text(json.dumps({
        "basis": "first explicit citation in strengthened sections/main_text.tex",
        "figure_current_to_new": {f"S{k}": f"S{v}" for k, v in FIGURE_MAP.items()},
        "table_current_to_new": {f"S{k}": f"S{v}" for k, v in TABLE_MAP.items()},
        "scientific_content_changed": False,
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "figures": 28, "tables": 28}))


if __name__ == "__main__":
    main()
