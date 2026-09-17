"""B04 mutation checks against the unchanged synthetic regression suite."""
from pathlib import Path
import subprocess
import tempfile
import sys
import json


def main() -> int:
    """Require baseline pass and targeted assertion failures in every mutant."""
    root = Path(__file__).resolve().parents[1]
    source = (root/'pipeline/legal_html.py').read_text()
    test = (root/'tests/test_legal_html.py').read_text()
    baseline = subprocess.run([sys.executable,str(root/'tests/test_legal_html.py')],capture_output=True,text=True,timeout=30)
    if baseline.returncode:
        print(baseline.stderr)
        return 1
    changes = [
        ('drop_tail', "text = '\\n'.join(lines) + '\\n'", "text = ('\\n'.join(lines) + '\\n').split('Disposiciones transitorias')[0]", 'test_repeated_numbers_and_transitory_provisions_retained'),
        ('leak_navigation', "'text': text, 'legal_html': fragment", "'text': text + 'MENU_ARTICULO_999', 'legal_html': fragment", 'test_navigation_and_related_excluded'),
        ('drop_negation', "'text': text, 'legal_html': fragment", "'text': text.replace('No se deroga', 'Se deroga'), 'legal_html': fragment", 'test_navigation_and_related_excluded'),
        ('erase_table_span', "'text': text, 'legal_html': fragment", "'text': text, 'legal_html': fragment.replace('rowspan=\"2\"', '')", 'test_table_cells_and_spans_preserved'),
    ]
    results = []
    for name, old, new, case in changes:
        if source.count(old) != 1:
            raise RuntimeError('mutation target changed: '+name)
        altered = source.replace(old,new)
        compile(altered,name,'exec')
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);(p/'pipeline').mkdir();(p/'tests').mkdir()
            (p/'pipeline/legal_html.py').write_text(altered);(p/'tests/test_legal_html.py').write_text(test)
            r=subprocess.run([sys.executable,str(p/'tests/test_legal_html.py'),'ExtractionTests.'+case],capture_output=True,text=True,timeout=30)
            detected=r.returncode!=0 and 'FAIL: '+case in r.stderr
            results.append({'name':name,'exit':r.returncode,'detected':detected,'stdout':r.stdout,'stderr':r.stderr})
    print(json.dumps({'baseline_exit':0,'mutations':results},indent=2))
    return 0 if all(r['detected'] for r in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
