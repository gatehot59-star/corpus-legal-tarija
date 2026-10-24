#!/usr/bin/env python3
"""Verify captured first-batch facts without importing candidate/runner validators.
This checks preservation and lifecycle, not visual or legal OCR accuracy.
"""
import copy, hashlib, json, math, sys
from pathlib import Path

def demand(ok, message):
    """Raise for a contradicted claim even under Python -O."""
    if not ok: raise ValueError(message)

def verify(data):
    """Validate two captured partial pages, raw blocks, images and timeout status."""
    files={f['path'].rsplit('/',1)[-1]:f for f in data['files']}
    for f in data['files']:
        raw=f['content'].encode('utf-8')
        demand(len(raw)==f['bytes'] and hashlib.sha256(raw).hexdigest()==f['sha256'],'capture_hash')
    partial=json.loads(files['partial.json']['content'])
    state=json.loads(files['state.json']['content'])
    request=json.loads(files['request.json']['content'])
    verdict=json.loads(files['verdict.json']['content'])
    batch=data['batch']
    demand(partial['status']=='incomplete' and partial['fidelity_certified'] is False,'partial_status')
    demand(partial['expected_pages']==4 and [p['page'] for p in partial['pages']]==[1,2],'partial_coverage')
    demand(state['status']=='failed' and state['error']=='timeout' and state['timed_out'] is True and state['worker_exit']==-9 and state['signal']==9,'timeout_evidence')
    demand(verdict['completed_jobs']==0 and len(verdict['runs'])==1 and verdict['status']=='stopped_incomplete','batch_outcome')
    demand(request['mode']=='ocr' and data['input_sha256']==batch['sha256']==request['input_sha256'],'request_source')
    demand(data['source_sha256']==batch['source_sha256'],'original_source')
    demand(len(data['archive_comparison'])==8,'archive_coverage')
    for f in data['archive_comparison']:
        demand(f['byte_equal'] is True and f['job_sha256']==f['archive_sha256'],'archive_changed')
    pages=[]
    for page in partial['pages']:
        n=page['page'];raw=json.loads(files[f'raw-{n:04d}.json']['content']);raw=raw.get('res',raw)
        blocks=page['blocks'];text=page['text'].encode('utf-8')
        demand(page['status']=='requires_review' and page['method']=='PaddleOCR-VL-1.6' and page['selection_reason']=='forced_ocr','page_origin')
        demand(page['blank_by_pixels'] is False and bool(page['text'].strip()),'not_an_inference')
        demand([b['index'] for b in blocks]==list(range(len(blocks))),'block_order')
        demand([b['block_content'] for b in raw['parsing_res_list']]==[b['text'] for b in blocks],'raw_disagreement')
        demand(page['text']=='\n'.join(b['text'] for b in blocks),'aggregate_text')
        demand(hashlib.sha256(text).hexdigest()==page['text_sha256'],'text_hash')
        demand(page['image_sha256']==data['image_hashes'][str(n)]==batch['pages'][n-1]['image_sha256'],'page_image')
        demand(type(page['extraction_seconds']) in (int,float) and math.isfinite(page['extraction_seconds']) and page['extraction_seconds']>0,'page_time')
        pages.append({'source_page':n,'utf8_bytes':len(text),'characters':len(page['text']),'blocks':len(blocks),'text_sha256':page['text_sha256'],'extraction_seconds':page['extraction_seconds'],'review':'pending'})
    return {'integrity':'PASS','execution':'FAIL_TIMEOUT','completed_jobs':0,'partial_pages_preserved':2,'pages':pages,'legal_fidelity':'NO MEDIDO','visual_comparison_performed':False}

def mutate_json(data, name, change):
    """Change one captured JSON record and update its container hashes."""
    f=next(f for f in data['files'] if f['path'].rsplit('/',1)[-1]==name)
    obj=json.loads(f['content']);change(obj);f['content']=json.dumps(obj,ensure_ascii=False)
    raw=f['content'].encode();f['bytes']=len(raw);f['sha256']=hashlib.sha256(raw).hexdigest()

def main():
    """Run the positive capture plus five falsifying mutations; never run OCR."""
    data=json.loads(Path(sys.argv[1]).read_bytes());result=verify(data);controls=[]
    for name in ['missing_partial_page','wrong_raw_text','false_timeout','changed_archive','fidelity_certified']:
        value=copy.deepcopy(data)
        if name=='missing_partial_page': mutate_json(value,'partial.json',lambda x:x['pages'].pop())
        elif name=='wrong_raw_text': mutate_json(value,'raw-0001.json',lambda x:x.get('res',x)['parsing_res_list'][0].update(block_content='altered'))
        elif name=='false_timeout': mutate_json(value,'state.json',lambda x:x.update(timed_out=False))
        elif name=='changed_archive': value['archive_comparison'][0]['byte_equal']=False
        else: mutate_json(value,'partial.json',lambda x:x.update(fidelity_certified=True))
        try: verify(value)
        except ValueError as error: controls.append({'mutant':name,'rejected':str(error)})
        else: raise ValueError('missed_mutant:'+name)
    print(json.dumps({'positive':result,'negative_controls':controls,'operator':'same operator; independent of candidate validation code, not external audit'},ensure_ascii=False,indent=2))

if __name__=='__main__': main()
