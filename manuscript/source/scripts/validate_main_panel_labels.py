"""Check actual v19 PDF panel labels, including approved Figure 1."""
from pathlib import Path
from collections import Counter
import pdfplumber
ROOT=Path(__file__).resolve().parents[1]
SOURCES={
    "Figure 1":("figure_1_v19_figma","ab"),
    "Figure 2":("figure_2","abcd"),
    "Figure 3":("figure_4_strengthened","abcd"),
    "Figure 4":("figure_3_strengthened","abcd"),
    "Figure 5":("figure_5_strengthened","abc"),
}
def main():
    for name,(stem,letters) in SOURCES.items():
        with pdfplumber.open(ROOT/"figures"/(stem+".pdf")) as doc:
            words=doc.pages[0].extract_words(extra_attrs=["fontname","size"])
            labels=[w for w in words if w["text"] in letters and "bold" in w["fontname"].lower()]
        assert Counter(w["text"] for w in labels)==Counter(letters),(name,labels)
        sizes={round(w["size"],3) for w in labels}
        assert len(sizes)==1,(name,sizes)
        assert min(sizes)>=7,(name,sizes)
        print(f"{name}: PASS; labels={letters}; size={next(iter(sizes))} pt")
if __name__=="__main__":main()
