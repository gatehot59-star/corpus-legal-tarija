#!/usr/bin/env python3
"""Boundary-mocked orchestration tests, not OCR or legal fidelity evidence."""
import importlib.util,sys,tempfile,json,hashlib,types,contextlib,io
from pathlib import Path
from unittest.mock import patch
runner=Path(sys.argv[1]);spec=importlib.util.spec_from_file_location('candidate_runner',runner)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def exercise(case):
    """Execute the real batch runner against synthetic API/process boundaries."""
    with tempfile.TemporaryDirectory() as tmp:
        b=Path(tmp);(b/'state').mkdir();(b/'subject').mkdir();(b/'runner.py').write_bytes(runner.read_bytes())
        docs=[{'sha256':str(i)*64,'pages':n} for i,n in enumerate([44,24,39,18],1)]
        batches=[]
        for d in docs:
            for first in range(1,d['pages']+1,4):
                number=len(batches)+1;data=f'fixture batch {number}'.encode();name=f'batch-{number}.pdf';(b/name).write_bytes(data)
                batches.append({'number':number,'source_sha256':d['sha256'],'input':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),
                    'pages':[{'local_page':i+1,'source_page':p,'image_sha256':'b'*64} for i,p in enumerate(range(first,min(first+4,d['pages']+1)))]})
        prov={'mode':'ocr','device':'cpu','code_sha256':'c'*64}
        seal={'documents':docs,'batches':batches,'source_sha256':{'runner.py':hashlib.sha256(runner.read_bytes()).hexdigest()},'runtime':'/synthetic-runtime',
            'pip_freeze_sha256':hashlib.sha256(b'synthetic-freeze\n').hexdigest(),'provenance':prov,'per_job_timeout_seconds':7260,'batch_timeout_seconds':232920}
        (b/'seal.json').write_text(json.dumps(seal))
        if case=='changed_source': (b/'runner.py').write_text('wrong source')
        active={'index':0,'worker_observed':False,'job':None,'state':None,'result':None}
        class Server:
            pid=999999
            returncode=None
            def poll(self): return None
        def fake_popen(*args,**kwargs):
            (b/'state/run/candidate.sock').touch();return Server()
        def api(sock,method,path,data=None):
            if path=='/ready': return 200,{'synthetic':True}
            if method=='POST':
                assert path.endswith('mode=ocr');batch=batches[active['index']];active['index']+=1
                ident=f"synthetic-job-{active['index']}";job=b/'state/run/jobs'/ident;job.mkdir(parents=True)
                pages=[]
                for mapping in batch['pages']:
                    text='synthetic page '+str(mapping['source_page']);local=mapping['local_page']
                    pages.append({'page':local,'status':'requires_review','method':'PaddleOCR-VL-1.6','selection_reason':'forced_ocr','blank_by_pixels':False,
                        'image_sha256':'b'*64,'blocks':[{'index':0,'text':text}],'text':text,'text_sha256':hashlib.sha256(text.encode()).hexdigest(),'extraction_seconds':1.0})
                    rawtext='corrupt' if case=='raw_disagreement' else text
                    (job/f'raw-{local:04d}.json').write_text(json.dumps({'res':{'parsing_res_list':[{'block_content':rawtext}]}}))
                result={'schema':'corpus-ocr/1','status':'requires_review','fidelity_certified':False,'expected_pages':len(pages),'completed_pages':len(pages),'pages':pages,
                    'text':'\n\f\n'.join(p['text'] for p in pages),'markdown':'\n\n'.join(f"<!-- page:{p['page']} -->\n"+p['text'] for p in pages),
                    'provenance':{**prov,'source_sha256':batch['sha256'],'timings':{'preparation_seconds':1.0,'load_seconds':1.0,'warmup_seconds':1.0,'extraction_sum_seconds':float(len(pages)),'worker_wall_seconds':float(len(pages)+3)}}}
                state={'status':'failed' if case=='worker_failed' else 'requires_review','worker_exit':1 if case=='worker_failed' else 0,'timed_out':False,'signal':None,'progress':{'phase':'completed','completed_pages':len(pages)}}
                (job/'result.json').write_text(json.dumps(result));(job/'state.json').write_text(json.dumps(state));(job/'partial.json').write_text(json.dumps({'pages':pages,'status':'incomplete'}))
                active.update(job=ident,result=result,state=state,worker_observed=False)
                return 202,{'job':ident}
            if path.endswith('/result'): return 200,active['result']
            return 200,active['state']
        def workers(subject,jobs):
            if active['job'] and not active['worker_observed']:
                active['worker_observed']=True
                return [{'pid':100000+active['index'],'start_ticks':active['index'],'job':active['job'],'synthetic':True}]
            return []
        fake_module=types.ModuleType('ocr_client');fake_module.request=api
        capture=io.StringIO()
        with patch.dict(sys.modules,{'ocr_client':fake_module}),patch.object(m.subprocess,'Popen',fake_popen),patch.object(m.subprocess,'run',return_value=types.SimpleNamespace(returncode=0,stdout='synthetic-freeze\n',stderr='')),patch.object(m,'worker_processes',workers),patch.object(m,'production_busy',return_value=[{'job':'synthetic-production'}] if case=='production_busy' else []),patch.object(m,'cgroup_snapshot',return_value={'synthetic':True}),patch.object(m,'stop_owned',return_value={'synthetic':True,'remaining_workers':[]}),patch.object(m.time,'sleep',return_value=None),contextlib.redirect_stdout(capture),contextlib.redirect_stderr(capture):
            exit_code=m.run(b)
        v=json.loads((b/'state/run/verdict.json').read_bytes())
        if case=='positive':
            assert exit_code==0 and v['completed_pages']==125 and v['completed_jobs']==32 and v['vl_inferences']==125
            assert len(list((b/'state/run/archive').glob('batch-*')))==32
            assert len(list((b/'state/run/pages').glob('*/*.utf8.txt')))==125
        else:
            assert exit_code==1 and v['status']=='stopped_incomplete' and v['completed_pages']==0
            if case in ('worker_failed','raw_disagreement'): assert (b/'state/run/archive/batch-01/partial.json').is_file()
        return {'case':case,'exit':exit_code,'verdict':v,'stdout_stderr':capture.getvalue(),'boundary_mocks_not_ocr':True}
results=[exercise(case) for case in ['positive','worker_failed','raw_disagreement','production_busy','changed_source']]
print(json.dumps({'status':'PASS','cases':results,'not_a_runtime_ocr_test':True},indent=2))
