#!/usr/bin/env python3
"""scripts/ocr/resolution_probe_20261024.py: one four-page job at 2500 pixels.
Compare against the sealed historical 5000-pixel timeout, not a fresh paired A/B.
No changes to timeout, CPU, model, decoding, page count or production.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
import traceback

HELPER_SHA='a2ee42bcc8df2fa1afa2bce1b0c6cd1180fcaa1238627a20662ab95aa38a7c53'
HELPER=Path(__file__).with_name('reported125_20261023.py')
if hashlib.sha256(HELPER.read_bytes()).hexdigest()!=HELPER_SHA:
    raise RuntimeError('helper_hash_mismatch')
SPEC=importlib.util.spec_from_file_location('sealed_reported125',HELPER)
H=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(H)


def assess(state: dict, result: dict, batch: dict, provenance: dict, raw_pages: dict) -> dict:
    """Return a bounded completion verdict or raise on timeout/missing evidence.
    This checks extraction coverage and integrity, not transcription accuracy.
    """
    H.require(state['status']=='requires_review' and state['worker_exit']==0
              and state['timed_out'] is False and state['signal'] is None,'worker_not_success')
    seconds=state['job_wall_seconds']
    H.require(type(seconds) in (int,float) and math.isfinite(seconds) and 0<seconds<7200,'deadline_not_avoided')
    H.require(state['progress']['phase']=='completed' and state['progress']['completed_pages']==4,'terminal_coverage')
    H.require(len(batch['pages'])==4 and [p['source_page'] for p in batch['pages']]==[1,2,3,4],'scope_changed')
    H.validate_result(result,batch,provenance)
    H.require(set(raw_pages)=={1,2,3,4},'raw_page_coverage')
    for page in result['pages']:
        H.require(page['blank_by_pixels'] is False,'unexpected_blank')
        raw=raw_pages[page['page']];inner=raw.get('res',raw)
        H.require([b['block_content'] for b in inner['parsing_res_list']]==[b['text'] for b in page['blocks']],'raw_text_disagreement')
    return {'timeout_avoided_this_job':'PASS','four_pages_completed':True,
            'job_wall_seconds':seconds,'seconds_below_deadline':7200-seconds,
            'accuracy':'NO MEDIDO','repeatability':'NO MEDIDO',
            'causal_effect_generalization':'NO MEDIDO: one new run versus historical unseeded control'}


def self_test() -> dict:
    """Exercise the completion judge with a positive and eight falsifying mutants."""
    batch={'sha256':'a'*64,'pages':[{'local_page':p,'source_page':p,'image_sha256':str(p)*64} for p in range(1,5)]}
    provenance={'mode':'ocr','device':'cpu','code_sha256':'b'*64}
    pages=[];raw={}
    for p in range(1,5):
        text=f'NO PAGAR 20.000.000, control {p}'
        pages.append({'page':p,'status':'requires_review','method':'PaddleOCR-VL-1.6','selection_reason':'forced_ocr',
            'blank_by_pixels':False,'image_sha256':str(p)*64,'blocks':[{'index':0,'text':text}],'text':text,
            'text_sha256':hashlib.sha256(text.encode()).hexdigest(),'extraction_seconds':1.0})
        raw[p]={'res':{'parsing_res_list':[{'block_content':text}]}}
    result={'schema':'corpus-ocr/1','status':'requires_review','fidelity_certified':False,'expected_pages':4,'completed_pages':4,
            'pages':pages,'text':'\n\f\n'.join(p['text'] for p in pages),
            'markdown':'\n\n'.join(f"<!-- page:{p['page']} -->\n"+p['text'] for p in pages),
            'provenance':{**provenance,'source_sha256':'a'*64,'timings':{'preparation_seconds':1.,'load_seconds':1.,
            'warmup_seconds':1.,'extraction_sum_seconds':4.,'worker_wall_seconds':7.}}}
    state={'status':'requires_review','worker_exit':0,'timed_out':False,'signal':None,'job_wall_seconds':8.,
           'progress':{'phase':'completed','completed_pages':4}}
    positive=assess(state,result,batch,provenance,raw);controls=[]
    for name in ['timeout_flag','deadline_overrun','missing_page','wrong_image','false_fidelity','native_bypass','raw_disagreement','raw_missing']:
        s=copy.deepcopy(state);r=copy.deepcopy(result);rr=copy.deepcopy(raw)
        if name=='timeout_flag':s.update(timed_out=True,worker_exit=-9,signal=9,status='failed')
        elif name=='deadline_overrun':s['job_wall_seconds']=7200.1
        elif name=='missing_page':r['pages'].pop()
        elif name=='wrong_image':r['pages'][0]['image_sha256']='0'*64
        elif name=='false_fidelity':r['fidelity_certified']=True
        elif name=='native_bypass':r['provenance']['mode']='auto'
        elif name=='raw_disagreement':rr[1]['res']['parsing_res_list'][0]['block_content']='PAGAR'
        else:rr.pop(4)
        try:assess(s,r,batch,provenance,rr)
        except (ValueError,KeyError) as error:controls.append({'name':name,'rejected':str(error)})
        else:raise ValueError('missed_mutant:'+name)
    return {'status':'PASS','positive':positive,'negative_controls':controls,'synthetic_not_ocr':True}


def run(base: Path, expected_seal: str) -> int:
    """Submit one fresh four-page job and preserve all results without retry.
    Kill only owned experimental processes on error, deadline or product demand.
    """
    base=base.resolve();H.require(H.digest(base/'seal.json')==expected_seal,'seal_changed')
    seal=json.loads((base/'seal.json').read_bytes());root=base/'state/run';root.mkdir(mode=0o700,exist_ok=False)
    subject=base/'subject';jobs=root/'jobs';sock=root/'candidate.sock';server=None;job=None
    record={'status':'running','started_utc':H.utc(),'seal_sha256':expected_seal,'job_count':1,'expected_pages':4,
            'timeout_avoided_this_job':'EN CURSO','completed_pages':0,'accuracy':'NO MEDIDO','workers':[]}
    start=time.monotonic();H.save(root/'measurement.json',record)
    def stop_signal(signum, frame):
        """Make an external stop visible in the final measurement record."""
        raise RuntimeError('external_signal_'+str(signum))
    signal.signal(signal.SIGTERM,stop_signal)
    try:
        for relative,digest in seal['files_sha256'].items():H.require(H.digest(base/relative)==digest,'sealed_file_changed:'+relative)
        H.require(not H.production_busy(),'production_demand')
        H.save(root/'instrument-tests.json',self_test())
        freeze=subprocess.run([sys.executable,'-m','pip','freeze','--all'],capture_output=True,text=True,timeout=30)
        H.save(root/'environment.json',{'utc':H.utc(),'python':sys.version,'uname':list(os.uname()),
            'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text(),'freeze':{'exit':freeze.returncode,'stdout':freeze.stdout,'stderr':freeze.stderr}})
        H.require(freeze.returncode==0 and hashlib.sha256(freeze.stdout.encode()).hexdigest()==seal['pip_freeze_sha256'],'runtime_freeze_changed')
        sys.path.insert(0,str(subject));from ocr_client import request
        command=[sys.executable,str(subject/'ocr_service.py'),'serve','--runtime',seal['runtime'],'--state',str(jobs),'--socket',str(sock)]
        H.save(root/'server-command.json',{'argv':command,'utc':H.utc()})
        with (root/'server.log').open('wb') as log:server=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        deadline=time.monotonic()+240
        while time.monotonic()<deadline:
            H.require(server.poll() is None,'server_exited');H.require(not H.production_busy(),'production_demand')
            if sock.exists():
                status,ready=request(str(sock),'GET','/ready')
                if status==200:H.save(root/'ready.json',ready);break
            time.sleep(2)
        else:raise TimeoutError('readiness_timeout')
        H.require(not H.worker_processes(subject,jobs),'existing_worker')
        H.require(not H.production_busy(),'production_demand')
        submitted=time.monotonic();status,admission=request(str(sock),'POST','/v1/jobs?mode=ocr',(base/'input.pdf').read_bytes())
        H.require(status==202,'admission_failed');job=jobs/admission['job'];record.update(job=job.name,submitted_utc=H.utc(),admission=admission)
        H.save(root/'measurement.json',record)
        with (root/'polls.jsonl').open('w',encoding='utf-8') as polls:
            while time.monotonic()-submitted<7260:
                H.require(server.poll() is None,'server_exited');H.require(not H.production_busy(),'production_demand')
                status,state=request(str(sock),'GET','/v1/jobs/'+job.name);H.require(status==200,'poll_failed')
                workers=H.worker_processes(subject,jobs)
                for worker in workers:
                    H.require(worker['job']==job.name,'wrong_worker')
                    if worker not in record['workers']:record['workers'].append(worker);H.save(root/'measurement.json',record)
                sample={'utc':H.utc(),'state':state,'workers':workers,'resources':H.cgroup_snapshot()}
                polls.write(json.dumps(sample)+'\n');polls.flush();H.save(root/'checkpoint.json',sample)
                if state['status'] in ('requires_review','failed','interrupted'):break
                time.sleep(5)
            else:raise TimeoutError('observer_deadline')
        record.update(terminal_state=state,job_observed_wall_seconds=time.monotonic()-submitted)
        H.archive_job(job,root/'archive')
        if state['status']!='requires_review':
            record.update(status='failed',timeout_avoided_this_job='FAIL_TIMEOUT' if state.get('timed_out') is True else 'NO MEDIDO: worker failed for another reason')
            if (job/'partial.json').exists():record['partial_pages_preserved']=len(json.loads((job/'partial.json').read_bytes())['pages'])
        else:
            H.require(len(record['workers'])==1 and not H.worker_processes(subject,jobs),'worker_identity_or_not_reaped')
            status,result=request(str(sock),'GET','/v1/jobs/'+job.name+'/result');H.require(status==200,'result_unavailable');H.save(root/'result.json',result)
            H.require(result==json.loads((job/'result.json').read_bytes()),'api_result_mismatch')
            raw={p:json.loads((job/f'raw-{p:04d}.json').read_bytes()) for p in range(1,5)}
            assessment=assess(state,result,seal['batch'],seal['provenance'],raw)
            previous=json.loads((base/'reference-partial.json').read_bytes())
            comparisons=[]
            for page in result['pages']:
                data=page['text'].encode('utf-8');(root/f"page-{page['page']:04d}.utf8.txt").write_bytes(data)
                ref=next((p for p in previous['pages'] if p['page']==page['page']),None)
                comparisons.append({'page':page['page'],'text_sha256':page['text_sha256'],'utf8_bytes':len(data),
                    'extraction_seconds':page['extraction_seconds'],'historical_5000px_extraction_seconds':ref['extraction_seconds'] if ref else None,
                    'literal_text_equal_historical':page['text']==ref['text'] if ref else None,
                    'accuracy':'NO MEDIDO: equality or difference does not establish correctness'})
            record.update(status='complete_requires_review',completed_pages=4,assessment=assessment,
                          timeout_avoided_this_job=assessment['timeout_avoided_this_job'],page_comparisons=comparisons)
    except BaseException as error:
        record.update(status='interrupted',timeout_avoided_this_job='NO MEDIDO',error_type=type(error).__name__,error=str(error));traceback.print_exc()
    finally:
        record['resources_before_teardown']=H.cgroup_snapshot()
        record['teardown']=H.stop_owned(server,subject,jobs)
        if job is not None and job.exists():H.archive_job(job,root/'archive')
        record.update(finished_utc=H.utc(),continuous_wall_seconds=time.monotonic()-start)
        H.save(root/'measurement.json',record);print(json.dumps(record,ensure_ascii=False),flush=True)
    return 0 if record['status']=='complete_requires_review' else 1


def main() -> int:
    """Run synthetic checks or one explicitly sealed live measurement."""
    p=argparse.ArgumentParser();p.add_argument('--self-test',action='store_true');p.add_argument('--base',type=Path);p.add_argument('--seal-sha256');a=p.parse_args()
    if a.self_test:print(json.dumps(self_test(),indent=2));return 0
    if a.base is None or a.seal_sha256 is None:p.error('--base and --seal-sha256 required')
    return run(a.base,a.seal_sha256)

if __name__=='__main__':raise SystemExit(main())
