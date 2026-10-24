#!/usr/bin/env python3
"""scripts/ocr/reported125_20261023.py: isolated serial candidate extraction.
No legal fidelity claim, no production write, no retries and no prior text input.
"""
from __future__ import annotations
import argparse, copy, fcntl, hashlib, json, math, os, shutil, signal
import subprocess, sys, time, traceback
from datetime import datetime, timezone
from pathlib import Path

def utc():
    """Return a timezone-qualified timestamp."""
    return datetime.now(timezone.utc).isoformat()

def digest(path):
    """Hash a file without allocating it all in RAM."""
    value = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()

def save(path, data):
    """Atomically save one owned record, including intermediate failures."""
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".new")
    with temporary.open("w", encoding="utf-8") as output:
        json.dump(data, output, ensure_ascii=False, allow_nan=False, indent=2)
        output.write("\n")
        output.flush()
        os.fsync(output.fileno())
    temporary.replace(path)

def require(condition, message):
    """Fail regardless of Python optimization flags."""
    if not condition:
        raise ValueError(message)

def worker_processes(subject, job_root):
    """Find only this candidate's workers, never production or unrelated processes."""
    found = []
    for process in Path("/proc").iterdir():
        if not process.name.isdigit():
            continue
        try:
            argv = [v.decode() for v in (process / "cmdline").read_bytes().split(b"\0") if v]
            if len(argv) < 4 or argv[1:3] != [str(subject / "ocr_service.py"), "worker"]:
                continue
            require("--job" in argv, "worker_job_argument_missing")
            job = Path(argv[argv.index("--job") + 1])
            if job.parent != job_root:
                continue
            stat = (process / "stat").read_text().rsplit(") ", 1)[1].split()
            found.append({"pid": int(process.name), "start_ticks": int(stat[19]),
                          "job": job.name, "argv": argv,
                          "cgroup": (process / "cgroup").read_text()})
        except FileNotFoundError:
            continue
    return found

def cgroup_snapshot():
    """Read the experiment cgroup while it still exists, preserving missing fields."""
    lines = Path("/proc/self/cgroup").read_text().splitlines()
    relative = next((line[3:] for line in lines if line.startswith("0::")), None)
    if relative is None:
        return {"unavailable": "no_cgroup_v2"}
    directory = Path("/sys/fs/cgroup") / relative.lstrip("/")
    result = {"path": str(directory)}
    for name in ("memory.current", "memory.peak", "memory.swap.current",
                 "memory.swap.peak", "memory.events", "cpu.stat"):
        path = directory / name
        try:
            result[name] = path.read_text()
        except OSError as error:
            result[name] = {"unavailable": type(error).__name__}
    return result

def production_busy():
    """Yield to actual production OCR demand without changing production state."""
    directory = Path("/var/lib/corpus-ocr")
    require(directory.is_dir(), "production_state_unavailable")
    active = []
    for item in directory.iterdir():
        state = item / "state.json"
        if not item.is_dir() or not state.is_file():
            continue
        value = json.loads(state.read_bytes())
        if value.get("status") in ("queued", "running"):
            active.append({"job": item.name, "status": value["status"]})
    return active

def stop_owned(server, subject, jobs):
    """Terminate only processes belonging to this experiment on exit or deadline."""
    actions = []
    for sig in (signal.SIGTERM, signal.SIGKILL):
        workers = worker_processes(subject, jobs)
        for worker in workers:
            try:
                os.killpg(worker["pid"], sig)
                actions.append({"worker": worker, "signal": sig.name})
            except ProcessLookupError:
                pass
        if workers:
            time.sleep(2)
        else:
            break
    if server is not None and server.poll() is None:
        os.killpg(server.pid, signal.SIGTERM)
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(server.pid, signal.SIGKILL)
            server.wait(timeout=10)
    remaining = worker_processes(subject, jobs)
    return {"actions": actions, "server_exit": server.returncode if server else None,
            "remaining_workers": remaining}

def validate_schedule(seal):
    """Reject missing, duplicate, reordered or out-of-budget page mappings."""
    documents=seal['documents']; batches=seal['batches']
    require(len(documents)==4 and [d['pages'] for d in documents]==[44,24,39,18], 'document_scope')
    require(len({d['sha256'] for d in documents})==4, 'duplicate_source')
    expected=[(d['sha256'], p) for d in documents for p in range(1,d['pages']+1)]
    actual=[]
    require(len(batches)==32, 'batch_count')
    for number,b in enumerate(batches,1):
        require(b['number']==number and 1<=len(b['pages'])<=4, 'batch_order_or_limit')
        require([p['local_page'] for p in b['pages']]==list(range(1,len(b['pages'])+1)), 'local_page_order')
        actual.extend((b['source_sha256'],p['source_page']) for p in b['pages'])
        require(0<b['bytes']<=20*1024*1024, 'input_size')
    require(actual==expected and len(set(actual))==125,'source_page_coverage')

def validate_result(result, batch, provenance):
    """Validate full per-page coverage and candidate identity, not legal accuracy."""
    n=len(batch['pages'])
    require(result['schema']=='corpus-ocr/1' and result['status']=='requires_review', 'result_state')
    require(result['fidelity_certified'] is False,'false_certification')
    require(result['expected_pages']==result['completed_pages']==n, 'page_count')
    require([p['page'] for p in result['pages']]==list(range(1,n+1)), 'page_order')
    for p,m in zip(result['pages'],batch['pages']):
        require(p['method']=='PaddleOCR-VL-1.6' and p['status']=='requires_review','wrong_method')
        require(p['selection_reason']=='forced_ocr','not_forced_ocr')
        require(type(p['blank_by_pixels']) is bool,'blank_flag')
        require(p['image_sha256']==m['image_sha256'],'render_changed')
        require([b['index'] for b in p['blocks']]==list(range(len(p['blocks']))),'block_order')
        require(p['text']=='\n'.join(b['text'] for b in p['blocks']),'block_text')
        require(hashlib.sha256(p['text'].encode()).hexdigest()==p['text_sha256'],'text_hash')
        require((p['blank_by_pixels'] and not p['text'] and not p['blocks']) or
                (not p['blank_by_pixels'] and bool(p['text'].strip())), 'empty_nonblank')
        require(type(p['extraction_seconds']) in (int,float) and math.isfinite(p['extraction_seconds']) and p['extraction_seconds']>0,'page_time')
    require(result['text']=='\n\f\n'.join(p['text'] for p in result['pages']),'aggregate_text')
    require(result['markdown']=='\n\n'.join(f"<!-- page:{p['page']} -->\n".replace('\n','\n')+p['text'] for p in result['pages']),'aggregate_markdown')
    for k,v in provenance.items():
        require(result['provenance'][k]==v,'provenance:'+k)
    require(result['provenance']['source_sha256']==batch['sha256'],'input_hash')
    t=result['provenance']['timings']
    for k in ('preparation_seconds','load_seconds','warmup_seconds','extraction_sum_seconds','worker_wall_seconds'):
        require(type(t[k]) in (int,float) and math.isfinite(t[k]) and t[k]>0,'timing:'+k)
    require(math.isclose(t['extraction_sum_seconds'],sum(p['extraction_seconds'] for p in result['pages']),rel_tol=1e-12),'time_sum')

def self_test():
    """Use positive fixtures and explicit mutants; these are not OCR inferences."""
    docs=[{'sha256':str(i)*64,'pages':n} for i,n in enumerate([44,24,39,18],1)]
    batches=[]
    for d in docs:
        for start in range(1,d['pages']+1,4):
            batches.append({'number':len(batches)+1,'source_sha256':d['sha256'],'sha256':'a'*64,'bytes':100,
                'pages':[{'local_page':i+1,'source_page':p,'image_sha256':'b'*64} for i,p in enumerate(range(start,min(start+4,d['pages']+1)))]})
    seal={'documents':docs,'batches':batches};validate_schedule(seal)
    outcomes={'schedule_positive':'accepted'}
    for name in ['missing_batch','duplicate_source_page','reordered','too_many_pages','oversized','duplicate_source']:
        x=copy.deepcopy(seal)
        if name=='missing_batch': x['batches'].pop()
        elif name=='duplicate_source_page': x['batches'][0]['pages'][1]['source_page']=1
        elif name=='reordered': x['batches'][0],x['batches'][1]=x['batches'][1],x['batches'][0]
        elif name=='too_many_pages': x['batches'][0]['pages'].append(x['batches'][0]['pages'][0])
        elif name=='oversized': x['batches'][0]['bytes']=21*1024*1024
        else: x['documents'][1]['sha256']=x['documents'][0]['sha256']
        try: validate_schedule(x)
        except ValueError as e: outcomes[name]={'rejected':str(e)}
        else: raise ValueError('missed_mutant:'+name)
    batch=batches[-1];prov={'mode':'ocr','device':'cpu','code_sha256':'c'*64}
    pages=[]
    for m in batch['pages']:
        text='NO PAGAR 20.000.000'
        pages.append({'page':m['local_page'],'status':'requires_review','method':'PaddleOCR-VL-1.6','selection_reason':'forced_ocr',
            'blank_by_pixels':False,'image_sha256':'b'*64,'blocks':[{'index':0,'text':text}], 'text':text,
            'text_sha256':hashlib.sha256(text.encode()).hexdigest(),'extraction_seconds':1.0})
    result={'schema':'corpus-ocr/1','status':'requires_review','fidelity_certified':False,'expected_pages':2,'completed_pages':2,
        'pages':pages,'text':'\n\f\n'.join(p['text'] for p in pages),'markdown':'\n\n'.join(f"<!-- page:{p['page']} -->\n".replace('\n','\n')+p['text'] for p in pages),
        'provenance':{**prov,'source_sha256':'a'*64,'timings':{'preparation_seconds':1.0,'load_seconds':1.0,'warmup_seconds':1.0,'extraction_sum_seconds':2.0,'worker_wall_seconds':5.0}}}
    validate_result(result,batch,prov);outcomes['result_positive']='accepted'
    blank=copy.deepcopy(result)
    for p in blank['pages']: p.update(blank_by_pixels=True,blocks=[],text='',text_sha256=hashlib.sha256(b'').hexdigest())
    blank['text']='\n\f\n';blank['markdown']='<!-- page:1 -->\n\n\n<!-- page:2 -->\n'
    validate_result(blank,batch,prov);outcomes['blank_positive']='accepted_not_inference'
    for name in ['missing_page','false_fidelity','wrong_image','native_bypass','changed_text','wrong_source','wrong_code','negative_time','nonblank_empty']:
        x=copy.deepcopy(result)
        if name=='missing_page': x['pages'].pop()
        elif name=='false_fidelity': x['fidelity_certified']=True
        elif name=='wrong_image': x['pages'][0]['image_sha256']='d'*64
        elif name=='native_bypass': x['pages'][0]['method']='pdftotext'
        elif name=='changed_text': x['text']+=' '
        elif name=='wrong_source': x['provenance']['source_sha256']='d'*64
        elif name=='wrong_code': x['provenance']['code_sha256']='d'*64
        elif name=='negative_time': x['pages'][0]['extraction_seconds']=-1
        else:
            x=copy.deepcopy(blank);x['pages'][0]['blank_by_pixels']=False
        try: validate_result(x,batch,prov)
        except ValueError as e: outcomes[name]={'rejected':str(e)}
        else: raise ValueError('missed_mutant:'+name)
    return {'status':'PASS','controls':outcomes,'synthetic_not_ocr':True}

def archive_job(job, target):
    """Copy all durable job evidence before the service's 24-hour cleanup can run."""
    target.mkdir(parents=True,exist_ok=True)
    for p in job.iterdir():
        if p.is_file(): shutil.copy2(p,target/p.name)
    save(target/'archive-manifest.json',[{'path':p.name,'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(target.iterdir()) if p.is_file() and p.name!='archive-manifest.json'])

def run(base):
    """Execute exactly one sealed batch; preserve partials and abort without retry."""
    base=base.resolve();seal=json.loads((base/'seal.json').read_bytes());validate_schedule(seal)
    root=base/'state/run';root.mkdir(mode=0o700,exist_ok=False)
    jobs=root/'jobs';subject=base/'subject';sock=root/'candidate.sock'
    server=None;current=None;records=[];start=time.monotonic()
    v={'status':'running','started_utc':utc(),'expected_pages':125,'completed_pages':0,'vl_inferences':0,'blank_pages':0,
       'completed_jobs':0,'legal_fidelity':'NO MEDIDO','runs':records,'seal_sha256':digest(base/'seal.json'),'instrument_sha256':digest(__file__)}
    save(root/'verdict.json',v)
    lock=(base/'state/batch.lock').open('a')
    try:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        for rel,h in seal['source_sha256'].items(): require(digest(base/rel)==h,'source_changed:'+rel)
        for b in seal['batches']: require(digest(base/b['input'])==b['sha256'],'batch_input_changed')
        save(root/'self-test.json',self_test())
        freeze=subprocess.run([sys.executable,'-m','pip','freeze','--all'],capture_output=True,text=True,timeout=30)
        save(root/'environment.json',{'utc':utc(),'python':sys.version,'uname':list(os.uname()),'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text(),'pip_freeze':{'exit':freeze.returncode,'stdout':freeze.stdout,'stderr':freeze.stderr}})
        require(freeze.returncode==0 and hashlib.sha256(freeze.stdout.encode()).hexdigest()==seal['pip_freeze_sha256'],'freeze_changed')
        sys.path.insert(0,str(subject));from ocr_client import request
        command=[sys.executable,str(subject/'ocr_service.py'),'serve','--runtime',seal['runtime'],'--state',str(jobs),'--socket',str(sock)]
        save(root/'server-command.json',{'argv':command,'utc':utc()})
        with (root/'server.log').open('wb') as log: server=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        ready_deadline=time.monotonic()+240
        while time.monotonic()<ready_deadline:
            require(server.poll() is None,'server_exited')
            if sock.exists():
                status,ready=request(str(sock),'GET','/ready')
                if status==200: save(root/'ready.json',ready);break
            time.sleep(2)
        else: raise TimeoutError('readiness')
        for batch in seal['batches']:
            require(not production_busy(),'production_demand')
            require(not worker_processes(subject,jobs),'overlapping_workers')
            require(time.monotonic()-start<seal['batch_timeout_seconds'],'global_deadline')
            require(digest(base/batch['input'])==batch['sha256'],'input_changed')
            submitted=time.monotonic();status,admission=request(str(sock),'POST','/v1/jobs?mode=ocr',(base/batch['input']).read_bytes())
            require(status==202,'admission_failed:'+json.dumps(admission));ident=admission['job']
            require(ident not in [r['job'] for r in records],'duplicate_job')
            current=jobs/ident
            record={'number':batch['number'],'job':ident,'submitted_utc':utc(),'submitted_monotonic':submitted,'workers':[],'page_map':batch['pages'],'source_sha256':batch['source_sha256']}
            records.append(record);save(root/'runs.json',records)
            deadline=submitted+seal['per_job_timeout_seconds']
            with (root/f"batch-{batch['number']:02d}-polls.jsonl").open('w') as polls:
                while time.monotonic()<deadline:
                    require(time.monotonic()-start<seal['batch_timeout_seconds'],'global_deadline')
                    require(not production_busy(),'production_demand')
                    require(server.poll() is None,'server_exited')
                    status,state=request(str(sock),'GET','/v1/jobs/'+ident);require(status==200,'poll_failed')
                    workers=worker_processes(subject,jobs)
                    for w in workers:
                        require(w['job']==ident,'wrong_worker')
                        if w not in record['workers']: record['workers'].append(w);save(root/'runs.json',records)
                    sample={'utc':utc(),'state':state,'workers':workers,'resources':cgroup_snapshot()}
                    polls.write(json.dumps(sample)+'\n');polls.flush()
                    save(root/'checkpoint.json',{'utc':sample['utc'],'batch':batch['number'],'job':ident,'completed_jobs':v['completed_jobs'],
                        'completed_pages_committed':v['completed_pages'],'partial_pages_current_job':state.get('progress',{}).get('completed_pages',0),'state':state,'workers':workers})
                    if state['status'] in ('requires_review','failed','interrupted'): break
                    time.sleep(5)
                else: raise TimeoutError('job_deadline')
            record.update(state=state,finished_utc=utc(),wall_seconds=time.monotonic()-submitted);save(root/'runs.json',records)
            archive_job(current,root/'archive'/f"batch-{batch['number']:02d}")
            require(state['status']=='requires_review' and state['worker_exit']==0 and state['timed_out'] is False and state['signal'] is None,'worker_failed')
            require(len(record['workers'])==1 and not worker_processes(subject,jobs),'worker_identity_or_not_reaped')
            require(state['progress']['phase']=='completed' and state['progress']['completed_pages']==len(batch['pages']),'terminal_progress')
            status,result=request(str(sock),'GET','/v1/jobs/'+ident+'/result');save(root/f"batch-{batch['number']:02d}-result.json",result)
            require(status==200,'result_unavailable');validate_result(result,batch,seal['provenance'])
            require(result==json.loads((current/'result.json').read_bytes()),'api_result_differs')
            for page,mapping in zip(result['pages'],batch['pages']):
                if not page['blank_by_pixels']:
                    raw=json.loads((current/f"raw-{page['page']:04d}.json").read_bytes());raw=raw.get('res',raw)
                    require([b['block_content'] for b in raw['parsing_res_list']]==[b['text'] for b in page['blocks']],'raw_text_differs')
                target=root/'pages'/batch['source_sha256'];target.mkdir(parents=True,exist_ok=True)
                (target/f"page-{mapping['source_page']:04d}.utf8.txt").write_bytes(page['text'].encode('utf-8'))
                save(target/f"page-{mapping['source_page']:04d}.json",{'source_sha256':batch['source_sha256'],'source_page':mapping['source_page'],'job':ident,'candidate':page,'review_status':'pending'})
                v['completed_pages']+=1;v['blank_pages']+=int(page['blank_by_pixels']);v['vl_inferences']+=int(not page['blank_by_pixels'])
            v['completed_jobs']+=1;save(root/'verdict.json',v);current=None
        require(v['completed_pages']==125 and v['completed_jobs']==32,'final_coverage')
        identities=[(w['pid'],w['start_ticks']) for r in records for w in r['workers']]
        require(len(identities)==32 and len(set(identities))==32,'fresh_workers')
        v['status']='complete_requires_review'
    except BaseException as e:
        v.update(status='stopped_incomplete',error_type=type(e).__name__,error=str(e));traceback.print_exc()
    finally:
        v['resources_before_teardown']=cgroup_snapshot();v['teardown']=stop_owned(server,subject,jobs)
        if current is not None and current.exists(): archive_job(current,root/'archive'/f"batch-{records[-1]['number']:02d}")
        v['finished_utc']=utc();v['wall_seconds']=time.monotonic()-start;save(root/'verdict.json',v);lock.close();print(json.dumps(v),flush=True)
    return 0 if v['status']=='complete_requires_review' else 1

def main():
    """Only explicit --base performs OCR; --self-test uses synthetic records."""
    p=argparse.ArgumentParser();p.add_argument('--self-test',action='store_true');p.add_argument('--base',type=Path);a=p.parse_args()
    if a.self_test: print(json.dumps(self_test(),indent=2));return 0
    if a.base is None: p.error('--base required')
    return run(a.base)

if __name__=='__main__': raise SystemExit(main())
