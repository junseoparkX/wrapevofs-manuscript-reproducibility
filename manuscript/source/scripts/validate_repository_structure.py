"""Check consolidated source paths and portable current renderer imports."""
from pathlib import Path
import hashlib,json,py_compile,tempfile

ROOT=Path(__file__).resolve().parents[1]
def main():
    data=json.loads((ROOT/'documentation/AGGREGATE_PATH_ALIASES.json').read_text())
    assert data['hash_policy']=='sha256_after_crlf_to_lf'
    for old,new in data['aliases'].items():
        content=(ROOT/new).read_bytes().replace(b'\r\n',b'\n')
        assert hashlib.sha256(content).hexdigest()==data['sha256'][old],(old,new)
    renderers=['scripts/v19_build_figures23.py','scripts/v19_build_figures45.py',
               'v19_work/supplement_polish_20261105/modern/build_s29_vector.py',
               'v19_work/supplement_polish_20261105/modern/build_modern.py']
    with tempfile.TemporaryDirectory() as directory:
        for i,name in enumerate(renderers):
            text=(ROOT/name).read_text(encoding='utf-8')
            assert 'C:\\Users' not in text and '.codex' not in text,name
            py_compile.compile(str(ROOT/name),cfile=str(Path(directory)/f'{i}.pyc'),doraise=True)
    assert (ROOT/'scripts/audit_panel_alignment.py').is_file()
    assert (ROOT/'supplementary_data/cv_score_sensitivity/results').is_dir()
    print(json.dumps({'status':'PASS','canonical_aliases_verified':len(data['aliases']),'portable_renderer_sources':len(renderers)}))
if __name__=='__main__':main()
