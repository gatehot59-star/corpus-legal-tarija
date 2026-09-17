"""Falsify the no-partial-candidate guarantee using a disposable source tree."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile


def main() -> int:
    """Return nonzero if the acceptance test cannot detect skipped rejections."""
    root = Path(__file__).resolve().parents[1]
    baseline = subprocess.run([sys.executable, str(root / 'tests/test_ingesta_nacional_segura.py')], capture_output=True, text=True, timeout=40)
    if baseline.returncode:
        print(baseline.stdout + baseline.stderr)
        return 1
    with tempfile.TemporaryDirectory(prefix='batch-falsifier-') as td:
        p = Path(td)
        shutil.copytree(root / 'sistema/api', p / 'sistema/api')
        (p / 'tests').mkdir()
        shutil.copy2(root / 'tests/test_ingesta_nacional_segura.py', p / 'tests')
        target = p / 'sistema/api/ingesta_nacional_segura.py'
        code = target.read_text()
        replacements = [
            ("raise BatchRejected(f'row {number}: text rejected')", 'continue'),
            ("if len(documents) != expected_count or source.faltantes:", 'if False:'),
        ]
        for before, after in replacements:
            if code.count(before) != 1:
                raise RuntimeError('mutation anchor changed')
            code = code.replace(before, after)
        compile(code, str(target), 'exec')
        target.write_text(code)
        r = subprocess.run([sys.executable, str(p / 'tests/test_ingesta_nacional_segura.py'),
                            'BatchTests.test_one_bad_record_does_not_publish_partial_candidate'], capture_output=True, text=True, timeout=20)
        detected = r.returncode != 0 and 'FAIL: test_one_bad_record_does_not_publish_partial_candidate' in r.stderr
        print(json.dumps({'baseline_exit': baseline.returncode, 'mutant_exit': r.returncode,
                          'mutant_changes': ['skip rejected row', 'remove full-count guard'],
                          'detected': detected, 'stdout': r.stdout, 'stderr': r.stderr}, indent=2))
        return 0 if detected else 1


if __name__ == '__main__':
    raise SystemExit(main())
