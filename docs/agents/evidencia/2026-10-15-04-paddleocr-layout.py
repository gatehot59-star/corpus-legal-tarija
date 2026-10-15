"""Run native PPStructureV3 reading-order reconstruction on the frozen OCR pilot."""
import datetime
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import pathlib
import resource
import sys
import time
import traceback

OLD = pathlib.Path('/tmp/ocr-ab-v2-20261015-bkeba6f_')
ROOT = pathlib.Path(sys.argv[1])


def now():
    """Return an ISO UTC timestamp."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(path):
    """Hash actual bytes, not a path or metadata."""
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def save(name, obj):
    """Persist a complete UTF-8 JSON record."""
    (ROOT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def run():
    """Execute once in a new directory, preserve raw outputs and fail visibly."""
    ROOT.mkdir(exist_ok=False)
    bank = json.loads((OLD / 'bank.json').read_text())
    baseline = json.loads((OLD / 'evidence.json').read_text())
    assert sha(OLD / 'bank.json') == 'cc8abf3c3f26674fe3547fa3687ec4f9e7796ce4051bf8f406a5f6aad49e31ab'
    assert sha(OLD / 'benchmark.py') == 'becb1312ce876e7de2101178f8b51fd8eb0de87d45ec465a41d2279647db422a'
    for case in bank['cases']:
        assert sha(case['image']) == case['image_sha256']
    base = pathlib.Path.home() / '.paddlex/official_models'
    config = {
        'layout_detection_model_name': 'PP-DocLayout_plus-L',
        'region_detection_model_name': 'PP-DocBlockLayout',
        'text_detection_model_name': 'PP-OCRv5_mobile_det',
        'text_detection_model_dir': str(base / 'PP-OCRv5_mobile_det'),
        'text_recognition_model_name': 'latin_PP-OCRv5_mobile_rec',
        'text_recognition_model_dir': str(base / 'latin_PP-OCRv5_mobile_rec'),
        'use_doc_orientation_classify': False,
        'use_doc_unwarping': False,
        'use_textline_orientation': False,
        'use_table_recognition': False,
        'use_formula_recognition': False,
        'use_seal_recognition': False,
        'use_chart_recognition': False,
        'use_region_detection': True,
        'format_block_content': False,
        'markdown_ignore_labels': [],
        'text_det_limit_side_len': 960,
        'text_det_limit_type': 'max',
        'device': 'cpu',
        'cpu_threads': 1,
        'enable_mkldnn': False,
    }
    save('seal.json', {'utc': now(), 'script_sha256': sha(__file__),
        'baseline_bank_sha256': sha(OLD / 'bank.json'), 'config': config,
        'text_extraction': 'Concatenate every block_content in native parsing_res_list order; no reference-aware reordering, correction, or filtering.',
        'scope': 'Layout and region detection plus original mobile Latin OCR; specialized table/formula/seal/chart recognizers disabled.',
        'in_sample_warning': 'These controls were already observed; this is a regression rerun, not a fresh blind test.',
        'inputs': [{'id': c['id'], 'sha256': c['image_sha256']} for c in bank['cases']]})
    for key in ('OMP_NUM_THREADS', 'OMP_THREAD_LIMIT', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
        os.environ[key] = '1'
    os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'
    from paddleocr import PPStructureV3
    import paddlex
    spec = importlib.util.spec_from_file_location('frozen_benchmark', OLD / 'benchmark.py')
    bench = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bench)
    record = {'start_utc': now(), 'runs': [], 'config': config,
        'versions': {n: importlib.metadata.version(n) for n in ('paddleocr', 'paddlepaddle', 'paddlex')},
        'cpu_count': os.cpu_count(), 'load_start': os.getloadavg()}
    save('record.json', record)
    start = time.perf_counter()
    engine = PPStructureV3(**config)
    record['init_seconds_including_any_download'] = time.perf_counter() - start
    record['model_files'] = []
    for name in ('PP-DocLayout_plus-L', 'PP-DocBlockLayout', 'PP-OCRv5_mobile_det', 'latin_PP-OCRv5_mobile_rec'):
        for p in sorted((base / name).glob('*')):
            if p.is_file() and p.name in ('inference.json', 'inference.pdiparams', 'inference.yml', 'config.json'):
                record['model_files'].append({'path': str(p), 'bytes': p.stat().st_size, 'sha256': sha(p)})
    config_path = pathlib.Path(paddlex.__file__).parent / 'configs/pipelines/PP-StructureV3.yaml'
    record['installed_pipeline_config_sha256'] = sha(config_path)
    (ROOT / 'installed-pipeline.yaml').write_bytes(config_path.read_bytes())
    start = time.perf_counter()
    warm = list(engine.predict(str(OLD / 'warmup.png')))
    record['warmup_seconds'] = time.perf_counter() - start
    assert len(warm) == 1
    save('record.json', record)
    for case in bank['cases']:
        start = time.perf_counter()
        results = list(engine.predict(case['image']))
        elapsed = time.perf_counter() - start
        assert len(results) == 1, (case['id'], len(results))
        raw = results[0].json
        if callable(raw):
            raw = raw()
        if isinstance(raw, str):
            raw = json.loads(raw)
        save(case['id'] + '.raw.json', raw)
        body = raw.get('res', raw)
        blocks = body['parsing_res_list']
        text = '\n'.join(b['block_content'] for b in blocks)
        (ROOT / (case['id'] + '.txt')).write_text(text)
        markdown = results[0].markdown
        if callable(markdown):
            markdown = markdown()
        (ROOT / (case['id'] + '.md')).write_text(markdown['markdown_texts'])
        row = {'id': case['id'], 'kind': case['kind'], 'exit': 0, 'seconds': elapsed,
            'text': text, 'blocks': blocks, 'chars': len(text),
            'input_sha256': sha(case['image']), 'raw_sha256': sha(ROOT / (case['id'] + '.raw.json')),
            'text_sha256': sha(ROOT / (case['id'] + '.txt')),
            'score': bench.score(case['reference'], text, case['fields']) if case['reference'] is not None else None}
        record['runs'].append(row)
        save('record.json', record)
        print(json.dumps({k: row[k] for k in ('id', 'exit', 'seconds', 'chars', 'score')}), flush=True)
    record['finish_utc'] = now()
    record['peak_self_rss_kib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    record['load_end'] = os.getloadavg()
    record['input_hashes_unchanged'] = all(sha(c['image']) == c['image_sha256'] for c in bank['cases'])
    record['models_unchanged'] = all(sha(m['path']) == m['sha256'] for m in record['model_files'])
    record['previous_ocr_models_unchanged'] = all(sha(m['path']) == m['sha256'] for m in baseline['engines']['paddleocr']['model_files'] if pathlib.Path(m['path']).name in ('inference.json', 'inference.pdiparams', 'inference.yml'))
    assert record['input_hashes_unchanged'] and record['models_unchanged'] and record['previous_ocr_models_unchanged']
    record['real_seconds'] = sum(r['seconds'] for r in record['runs'] if r['kind'] == 'real_scan_unscored')
    save('record.json', record)
    save('completion.json', {'utc': now(), 'exit': 0, 'completed': len(record['runs']), 'record_sha256': sha(ROOT / 'record.json')})


if __name__ == '__main__':
    try:
        run()
    except Exception:
        if ROOT.exists():
            save('failure.json', {'utc': now(), 'traceback': traceback.format_exc()})
        raise
