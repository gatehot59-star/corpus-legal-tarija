"""Execute the unchanged tests against three isolated broken implementations."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile


def main() -> int:
    """Return failure if any targeted mutation survives or fails to compile."""
    root = Path(__file__).resolve().parents[1]
    source = (root / 'contracts/provenance_v2.py').read_text()
    tests = (root / 'tests/test_provenance_v2.py').read_text()
    mutations = {
        'hash_ignored': ('if not hmac.compare_digest(actual, expected_sha256):', 'if False:'),
        'authority_inferred_from_method': (
            'require_id(self.version_id)\n        require_url(self.source_url)',
            'object.__setattr__(self, "authority", Authority.OFFICIAL if self.method == Method.HTML else Authority.SECONDARY)\n        require_id(self.version_id)\n        require_url(self.source_url)'),
        'duplicate_overwrite': ('if key in seen:', 'if False:'),
    }
    results = []
    baseline = subprocess.run([sys.executable, str(root / 'tests/test_provenance_v2.py')], capture_output=True, text=True, timeout=30)
    if baseline.returncode:
        print(baseline.stdout + baseline.stderr)
        return 1
    for name, (before, after) in mutations.items():
        if source.count(before) != 1:
            raise RuntimeError('mutation target changed: ' + name)
        candidate = source.replace(before, after)
        compile(candidate, name, 'exec')
        with tempfile.TemporaryDirectory(prefix='corpus-mutation-') as tmp:
            p = Path(tmp)
            (p / 'contracts').mkdir()
            (p / 'tests').mkdir()
            (p / 'contracts/provenance_v2.py').write_text(candidate)
            (p / 'tests/test_provenance_v2.py').write_text(tests)
            r = subprocess.run([sys.executable, str(p / 'tests/test_provenance_v2.py')], capture_output=True, text=True, timeout=30)
            results.append({'mutation': name, 'exit': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr,
                            'detected': r.returncode != 0 and 'FAIL:' in r.stderr})
    print(json.dumps({'baseline_exit': baseline.returncode, 'results': results}, indent=2))
    return 0 if all(r['detected'] for r in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
