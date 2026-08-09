"""Report reproducible submission-facing word and display counts for V12."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def words(value: str) -> list[str]:
    value = re.sub(
        r"\\(?:citep|Cref|cref|ref|label|url|path|texttt|textbf|emph|keywords)\{([^{}]*)\}",
        r" \1 ",
        value,
    )
    value = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^]]*\])?", " ", value)
    value = re.sub(r"[{}$\\^_~]", " ", value)
    return re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*", value)


main = (ROOT / "main.tex").read_text(encoding="utf-8")
body = (ROOT / "sections" / "main_text.tex").read_text(encoding="utf-8")
abstract = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", main, re.S)
title = re.search(r"\\title\{(.*?)\}", main, re.S)
captions = re.findall(r"\\caption\{(.*?)\}\s*\\label", body, re.S)


def prose_slice(start_heading: str, end_heading: str | None) -> str:
    """Return a submission-facing prose slice without figures or table bodies."""

    start = body.index(start_heading)
    end = body.index(end_heading, start) if end_heading else len(body)
    value = body[start:end]
    value = re.sub(r"(?m)%.*$", " ", value)
    value = re.sub(r"\\begin\{figure\}.*?\\end\{figure\}", " ", value, flags=re.S)
    value = re.sub(r"\\input\{tables/[^{}]+\}", " ", value)
    return value

assert abstract and title
print(f"title_words={len(words(title.group(1)))}")
print(f"abstract_words={len(words(abstract.group(1))) - len(words(re.search(r'\\keywords\{(.*?)\}', abstract.group(1), re.S).group(1)))}")
ird = " ".join(
    [
        prose_slice(r"\section{Introduction}", r"\section{Results}"),
        prose_slice(r"\section{Results}", r"\section{Discussion}"),
        prose_slice(r"\section{Discussion}", r"\section{Methods}"),
    ]
)
methods = prose_slice(r"\section{Methods}", r"\section{Data availability}")
print(f"introduction_results_discussion_words={len(words(ird))}")
print(f"methods_words={len(words(methods))}")
for index, caption in enumerate(captions, start=1):
    print(f"figure_{index}_legend_words={len(words(caption))}")
print(f"main_figures={len(re.findall(r'\\begin\{figure\}', body))}")
print(f"main_tables={len(re.findall(r'\\input\{tables/table_', body))}")
