#!/usr/bin/env python3
"""Seal and launch one approved OCR batch only after successful full preparation."""
import pathlib,json,subprocess,time,hashlib,os,pwd,importlib.util,traceback,sys
from datetime import datetime,timezone
b=pathlib.Path(sys.argv[1]);old=pathlib.Path('/home/ubuntu/ocr-pr33-repeats-20261023-28egapd3');python='/opt/corpus-ocr-vl/runtime/venv/bin/python'
def save(name,value):
    """Persist complete command records on the owned experimental directory."""
    p=b/name;q=p.with_suffix('.new');q.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');q.replace(p)
def sha(p):
    """Hash one full input or source file."""
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def command(argv,env=None,timeout=60):
    """Capture a real subprocess without treating nonzero as success."""
    r=subprocess.run(argv,capture_output=True,text=True,env=env,timeout=timeout)
    return {'argv':argv,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
try:
    deadline=time.monotonic()+1800
    while time.monotonic()<deadline:
        p=json.loads((b/'preparation-status.json').read_text())
        if p['state']=='failed': raise RuntimeError('preparation_failed')
        if p['state']=='prepared': break
        time.sleep(5)
    else: raise TimeoutError('preparation_wait_deadline')
    prepunit='corpus-prepare125-v2-'+b.name.rsplit('-',1)[1]+'.service'
    for attempt in range(10):
        prepstatus=command(['systemctl','show',prepunit,'-p','MainPID','-p','ExecMainStatus','-p','Result','-p','ActiveState'])
        if 'MainPID=0\n' in prepstatus['stdout']: break
        time.sleep(1)
    if prepstatus['exit'] or 'ExecMainStatus=0\n' not in prepstatus['stdout'] or 'Result=success\n' not in prepstatus['stdout'] or 'MainPID=0\n' not in prepstatus['stdout']: raise RuntimeError('preparation_unit_not_success')
    save('preparation-unit-final.json',prepstatus)
    if (b/'seal.json').exists() or (b/'launch.json').exists() or (b/'state/run').exists(): raise RuntimeError('already_sealed_or_started')
    spec=importlib.util.spec_from_file_location('batch_runner',b/'reported125-v2.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    manifest=json.loads((b/'prepared-manifest.json').read_text());m.validate_schedule(manifest)
    if p['pages_verified']!=125: raise RuntimeError('preparation_coverage')
    for d in manifest['documents']:
        if sha(b/d['input'])!=d['sha256']: raise RuntimeError('original_changed')
    for batch in manifest['batches']:
        if sha(b/batch['input'])!=batch['sha256']: raise RuntimeError('subset_changed')
    if m.production_busy(): raise RuntimeError('production_demand')
    oldseal=json.loads((old/'seal.json').read_text())
    for rel,expected in oldseal['source_sha256'].items():
        if rel.startswith('subject/') and sha(b/rel)!=expected: raise RuntimeError('candidate_changed')
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(b/'subject'),CORPUS_OCR_LOW_MEMORY='0')
    checks={'self_test':command([python,'-B',str(b/'reported125-v2.py'),'--self-test'],env),
            'orchestration':command([python,'-B',str(b/'test_orchestration.py'),str(b/'reported125-v2.py')],env),
            'runtime_verify':command([python,'-B',str(b/'subject/ocr_service.py'),'verify','--runtime',oldseal['runtime']],env,120),
            'freeze':command([python,'-m','pip','freeze','--all'],env)}
    save('prelaunch-checks.json',checks)
    if any(c['exit'] for c in checks.values()): raise RuntimeError('prelaunch_check_failed')
    if hashlib.sha256(checks['freeze']['stdout'].encode()).hexdigest()!=oldseal['pip_freeze_sha256']: raise RuntimeError('freeze_changed')
    if m.production_busy(): raise RuntimeError('production_demand')
    provenance=dict(oldseal['provenance']);provenance.pop('source_sha256');provenance['mode']='ocr'
    seal={**manifest,'created_utc':datetime.now(timezone.utc).isoformat(),'candidate_commit':oldseal['candidate_commit'],
        'runtime':oldseal['runtime'],'source_sha256':{rel:sha(b/rel) for rel in ['reported125-v2.py','prepare125.py','test_orchestration.py','launch_once.py','subject/ocr_service.py','subject/ocr_client.py','subject/sitecustomize.py']},
        'pip_freeze_sha256':oldseal['pip_freeze_sha256'],'provenance':provenance,'seed_policy':oldseal['seed_policy'],
        'per_job_timeout_seconds':7260,'product_worker_timeout_seconds':7200,'batch_timeout_seconds':232920,'unit_runtime_max_seconds':233100,
        'worker_policy':'32 fresh sequential workers; model and warmup per job; no automatic retries',
        'production_yield_policy':'abort experiment if a product job is queued/running; poll five seconds',
        'resolution':'pdftoppm 300dpi scale-to5000 gray PNG; 125/125 source/subset byte and pixel parity',
        'fidelity':'not measured; all candidate text requires review','human_adjudication':False,
        'baseline_sha256':sha(b/'baseline-before-ocr.json'),'baseline_not_sent_to_ocr':True,
        'candidate_only':True,'production_replacement':False,'paid_gpu':False,'latency_threshold':None,
        'resources':oldseal['resources'],'failure_policy':'stop incomplete, preserve partials, no silent skip, no retries',
        'archive_policy':'copy job files outside jobs before admitting next batch; protect against 24h service cleanup'}
    save('seal.json',seal)
    newunit='corpus-ocr-reported125-'+b.name.rsplit('-',1)[1]
    argv=json.loads((old/'launch.json').read_text())['command']
    argv=[x.replace(str(old),str(b)).replace('corpus-ocr-pr33-repeats-28egapd3',newunit).replace('run_repeats.py','reported125-v2.py').replace('RuntimeMaxSec=8100','RuntimeMaxSec=233100') for x in argv]
    # Already running with explicit root authorization; no nested credential handling.
    argv=argv[2:] if argv[:2]==['sudo','-n'] else argv
    probe=command(['systemctl','show',newunit+'.service','-p','LoadState','-p','ActiveState'])
    if 'LoadState=not-found\n' not in probe['stdout']: raise RuntimeError('unit_already_exists')
    if m.production_busy(): raise RuntimeError('production_demand')
    record={'created_utc':datetime.now(timezone.utc).isoformat(),'base':str(b),'unit':newunit+'.service','command':argv,'seal_sha256':sha(b/'seal.json'),'pre_unit_probe':probe,'status':'launch_attempt'}
    with (b/'launch.json').open('x') as f: json.dump(record,f,indent=2)
    result=command(argv);record.update(result=result,status='submitted' if result['exit']==0 else 'launch_failed');save('launch.json',record)
    if result['exit']: raise RuntimeError('systemd_launch_failed')
    save('launch-watcher-status.json',{'status':'submitted','unit':newunit+'.service','utc':datetime.now(timezone.utc).isoformat()})
    print(json.dumps(record),flush=True)
except BaseException as e:
    save('launch-watcher-status.json',{'status':'failed','error_type':type(e).__name__,'error':str(e),'utc':datetime.now(timezone.utc).isoformat()});traceback.print_exc();sys.exit(1)
