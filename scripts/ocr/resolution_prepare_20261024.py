#!/usr/bin/env python3
"""scripts/ocr/resolution_prepare_20261024.py: prepare and launch one isolated probe.
Only the PDF render scale changes, 5000 to 2500; no product files are written.
The original four-page subset and historical result stay unmodified.
"""
import ast
import difflib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import pwd
import shutil
import subprocess
import sys
from datetime import datetime,timezone
from PIL import Image

BASELINE=Path('/home/ubuntu/ocr-reported125-20261023-_la5lozi')
PYTHON='/opt/corpus-ocr-vl/runtime/venv/bin/python'


def sha(path):
    """Return a full file digest for sealed inputs, code and outputs."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    """Persist an owned preparation record before moving to the next step."""
    path=Path(path);temporary=path.with_suffix(path.suffix+'.new')
    temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');temporary.replace(path)


def require(condition, message):
    """Reject a preparation discrepancy instead of launching a different test."""
    if not condition:raise ValueError(message)


def image_record(path):
    """Measure actual dimensions, encoded bytes, pixels and blank status."""
    with Image.open(path) as image:
        image.load()
        return {'sha256':sha(path),'width':image.width,'height':image.height,'mode':image.mode,
                'pixel_sha256':hashlib.sha256(image.tobytes()).hexdigest(),
                'blank':image.convert('L').getextrema()==(255,255)}


def main():
    """Make one new sealed experiment, perform real render checks and launch once."""
    require(len(sys.argv)==2,'one_existing_base_directory_required');base=Path(sys.argv[1]).resolve()
    require(base.is_dir() and base.parent==Path('/home/ubuntu'),'invalid_base')
    require(not (base/'seal.json').exists() and not (base/'state').exists(),'already_prepared')
    evidence={'started_utc':datetime.now(timezone.utc).isoformat(),'commands':[],'status':'preparing'}
    save(base/'preparation.json',evidence)
    def command(argv, timeout=60):
        """Record exact subprocess outputs, without treating exit failure as success."""
        result=subprocess.run(argv,capture_output=True,text=True,timeout=timeout)
        entry={'argv':argv,'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr}
        evidence['commands'].append(entry);save(base/'preparation.json',evidence)
        require(result.returncode==0,'command_failed:'+argv[0])
        return result.stdout
    try:
        previous=json.loads((BASELINE/'seal.json').read_bytes());batch=dict(previous['batches'][0])
        oldsource=(BASELINE/'subject/ocr_service.py').read_text()
        require(sha(BASELINE/'subject/ocr_service.py')=='90df955df6edec61cc2c27876997848ba25c014d8dc5661fc2f1e91c6cf69a97','baseline_candidate_changed')
        old='"-scale-to", "5000"';new='"-scale-to", "2500"'
        require(oldsource.count(old)==1,'ambiguous_scale_change');changed=oldsource.replace(old,new,1)
        compile(changed,'ocr_service.py','exec')
        (base/'subject').mkdir(mode=0o700)
        for name in ['ocr_client.py','sitecustomize.py']:shutil.copy2(BASELINE/'subject'/name,base/'subject'/name)
        (base/'subject/ocr_service.py').write_text(changed)
        evidence['service_diff']=''.join(difflib.unified_diff(oldsource.splitlines(True),changed.splitlines(True),fromfile='baseline/ocr_service.py',tofile='probe2500/ocr_service.py'))
        evidence['baseline_code_sha256']=sha(BASELINE/'subject/ocr_service.py');evidence['probe_code_sha256']=sha(base/'subject/ocr_service.py')
        constants={n.targets[0].id:ast.literal_eval(n.value) for n in ast.parse(changed).body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ['MAX_PAGES','JOB_TIMEOUT']}
        require(constants=={'MAX_PAGES':4,'JOB_TIMEOUT':7200},'limits_changed');evidence['unchanged_limits']=constants
        shutil.copy2(BASELINE/batch['input'],base/'input.pdf');require(sha(base/'input.pdf')==batch['sha256'],'input_changed')
        historic=BASELINE/'state/run/jobs/8cbfcde8623a4827aa679acde29fbcca'
        shutil.copy2(historic/'partial.json',base/'reference-partial.json');shutil.copy2(historic/'state.json',base/'reference-state.json')
        reference=json.loads((base/'reference-state.json').read_bytes())
        require(reference['timed_out'] is True and reference['status']=='failed','historical_control_not_timeout')
        spec=importlib.util.spec_from_file_location('probe_subject',base/'subject/ocr_service.py');candidate=importlib.util.module_from_spec(spec);spec.loader.exec_module(candidate)
        work=base/'render-subset';work.mkdir();rendered=candidate.prepare_pages(base/'input.pdf','pdf','ocr',work)
        require(len(rendered)==4,'render_coverage');records=[];batch['pages']=[];batch['input']='input.pdf'
        independent=base/'render-original';independent.mkdir()
        for page,native,native_ok,path in rendered:
            require(native_ok is False and native=='','native_bypass')
            prefix=independent/f'page-{page:04d}'
            command(['/usr/bin/pdftoppm','-f',str(page),'-l',str(page),'-singlefile','-r','300','-scale-to','2500','-gray','-png',str(BASELINE/previous['documents'][0]['input']),str(prefix)])
            a=image_record(path);b=image_record(prefix.with_suffix('.png'));high=previous['batches'][0]['pages'][page-1]
            require(a==b,'original_subset_render_disagreement')
            require(max(a['width'],a['height'])==2500 and max(high['width'],high['height'])==5000,'scale_not_halved')
            require(a['sha256']!=high['image_sha256'] and not a['blank'],'input_unchanged_or_blank')
            records.append({'page':page,'low':a,'high':high,'original_subset_equal':True,
                            'pixel_ratio':(a['width']*a['height'])/(high['width']*high['height'])})
            batch['pages'].append({'local_page':page,'source_page':page,'image_sha256':a['sha256'],
                                   'width':a['width'],'height':a['height'],'mode':a['mode']})
        evidence['render_checks']=records
        test=command([PYTHON,'-B',str(base/'resolution_probe_20261024.py'),'--self-test'])
        require(json.loads(test)['status']=='PASS','instrument_selftest')
        installation=json.loads(command([PYTHON,'-B',str(base/'subject/ocr_service.py'),'verify','--runtime',previous['runtime']],120))
        freeze=command([PYTHON,'-m','pip','freeze','--all'])
        require(hashlib.sha256(freeze.encode()).hexdigest()==previous['pip_freeze_sha256'],'freeze_changed')
        require(installation['config_sha256']==previous['provenance']['template_configuration_sha256'],'config_changed')
        require(installation['models']==previous['provenance']['models'],'model_revision_changed')
        helper_spec=importlib.util.spec_from_file_location('helper',base/'reported125_20261023.py');helper=importlib.util.module_from_spec(helper_spec);helper_spec.loader.exec_module(helper)
        require(not helper.production_busy(),'production_demand')
        (base/'state').mkdir(mode=0o700);(base/'state/home').mkdir(mode=0o700)
        provenance=dict(previous['provenance']);provenance['code_sha256']=evidence['probe_code_sha256']
        files=['resolution_probe_20261024.py','resolution_prepare_20261024.py','reported125_20261023.py','subject/ocr_service.py','subject/ocr_client.py','subject/sitecustomize.py','input.pdf','reference-partial.json','reference-state.json']
        seal={'created_utc':datetime.now(timezone.utc).isoformat(),'runtime':previous['runtime'],'files_sha256':{n:sha(base/n) for n in files},
              'batch':batch,'provenance':provenance,'pip_freeze_sha256':previous['pip_freeze_sha256'],
              'baseline_seal_sha256':sha(BASELINE/'seal.json'),'historical_control':reference,
              'independent_variable':'pdftoppm scale-to: 5000 to 2500; -r 300 unchanged; actual output dimensions measured',
              'worker_timeout_seconds':7200,'observer_timeout_seconds':7260,'unit_runtime_max_seconds':7800,
              'resources':previous['resources'],'seed_policy':previous['seed_policy'],
              'per_page_max_new_tokens':4096,'warmup_max_new_tokens':128,'inference_pages':[1,2,3,4],
              'success_rule':'same four nonblank pages, expected image hashes, full raw outputs and worker success in <7200 seconds',
              'quality_rule':'completion is not accuracy; all outputs require review',
              'scope':'one diagnostic trial, historical control, no repeats and no general causal claim',
              'production_changed':False,'paid_gpu':False,'source_original':previous['documents'][0]}
        save(base/'seal.json',seal);evidence.update(status='prepared',seal_sha256=sha(base/'seal.json'))
        save(base/'preparation.json',evidence)
        user=pwd.getpwnam('ubuntu')
        for p in [base]+list(base.rglob('*')):os.chown(p,user.pw_uid,user.pw_gid)
        base.chmod(0o700)
        original=json.loads((BASELINE/'launch.json').read_bytes())['command'];unit='corpus-ocr-res2500-'+base.name.rsplit('-',1)[1]
        args=[s.replace(str(BASELINE),str(base)).replace('corpus-ocr-reported125-_la5lozi',unit).replace('reported125-v2.py','resolution_probe_20261024.py').replace('RuntimeMaxSec=233100','RuntimeMaxSec=7800') for s in original]
        args+=['--seal-sha256',sha(base/'seal.json')]
        probe=command(['systemctl','show',unit+'.service','-p','LoadState','-p','MainPID','-p','ActiveState'])
        require('LoadState=not-found\n' in probe,'existing_unit')
        require(not helper.production_busy(),'production_demand')
        launch={'utc':datetime.now(timezone.utc).isoformat(),'base':str(base),'unit':unit+'.service','command':args,'seal_sha256':sha(base/'seal.json'),'status':'attempt'}
        save(base/'launch.json',launch)
        output=command(args);launch.update(status='submitted',stdout=output);save(base/'launch.json',launch)
        evidence.update(status='submitted',finished_utc=datetime.now(timezone.utc).isoformat());save(base/'preparation.json',evidence)
        print(json.dumps({'preparation':evidence,'launch':launch}),flush=True);return 0
    except BaseException as error:
        import traceback
        evidence.update(status='failed',error_type=type(error).__name__,error=str(error));save(base/'preparation.json',evidence);traceback.print_exc();return 1

if __name__=='__main__':raise SystemExit(main())
