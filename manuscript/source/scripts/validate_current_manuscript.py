"""Verify the frozen current public manuscript and its local build dependencies."""
from pathlib import Path
import hashlib,json,re
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
def main():
    m=json.loads((ROOT/'CURRENT_MANUSCRIPT.json').read_text())
    for name,expected in m['files_sha256'].items():
        p=ROOT/name
        assert p.is_file(),name
        value=p.read_bytes()
        if p.suffix in {'.tex','.bib','.bbl'}:value=value.replace(b'\r\n',b'\n')
        assert hashlib.sha256(value).hexdigest()==expected,name
    for name,key in [('main.pdf','main_pages'),('supplementary_information.pdf','supplementary_pages')]:
        assert len(PdfReader(ROOT/name).pages)==m[key],name
    visited=set()
    def check(name):
        if name in visited:return
        visited.add(name);text=(ROOT/name).read_text(encoding='utf-8')
        for cmd,target in re.findall(r'\\(input|includegraphics)(?:\[[^\]]*\])?\{([^{}]+)\}',text):
            p=ROOT/target
            if cmd=='input' and not p.suffix:p=p.with_suffix('.tex')
            assert p.is_file(),(name,target)
            if cmd=='input':check(p.relative_to(ROOT).as_posix())
    check('main.tex');check('supplementary_information.tex')
    cv=ROOT/'supplementary_data/cv_score_sensitivity'
    cm=json.loads((cv/'source_integrity_manifest.json').read_text())
    for name,record in cm['files'].items():
        assert hashlib.sha256((cv/name).read_bytes()).hexdigest()==record['sha256'],name
    print(json.dumps({'status':'PASS','version':m['version'],'frozen_files':len(m['files_sha256']),'tex_sources_checked':len(visited),'cv_source_files_verified':len(cm['files']),'main_pages':m['main_pages'],'supplementary_pages':m['supplementary_pages']}))
if __name__=='__main__':main()
