#!/usr/bin/env python3
"""Prueba sellada PaddleOCR-VL-1.6: cinco PNG, sin referencias en inferencia."""
import argparse, datetime, hashlib, importlib.metadata, json, os, pathlib, resource, signal, subprocess, sys, time, traceback
from html.parser import HTMLParser
ROOT=pathlib.Path('/tmp/paddle-vl16-heldout-20261015')
BANK=pathlib.Path('/tmp/ocr-heldout-20261015')
GOLD_SHA='36097a8dcb63e601cf3a3108d63fb9178a3d57067019c5b9c9e4d4c3331806d7'

def sha(path):
    """Hash de un archivo sin cargarlo íntegramente en memoria."""
    h=hashlib.sha256()
    with pathlib.Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
    return h.hexdigest()

def now():
    """Hora UTC explícita."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def write(name,obj):
    """Guarda JSON y reemplaza sólo el archivo de estado propio."""
    p=ROOT/name; p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')

class TableText(HTMLParser):
    """Extrae texto de tabla en orden DOM; no expande celdas combinadas."""
    def __init__(self):
        super().__init__(convert_charrefs=True); self.parts=[]
    def handle_starttag(self,tag,attrs):
        if tag in ('tr','td','th','br','p'):self.parts.append(' ')
    def handle_endtag(self,tag):
        if tag in ('tr','td','th','p'):self.parts.append(' ')
    def handle_data(self,data):self.parts.append(data)

def plain(blocks):
    """Conserva todos los bloques en orden nativo; sólo elimina markup de tablas."""
    texts=[]
    for b in blocks:
        text=b['block_content']
        if not isinstance(text,str):raise TypeError('contenido no textual')
        if b['block_label']=='table' and '<' in text:
            p=TableText();p.feed(text);p.close();text=''.join(p.parts)
        texts.append(text)
    return '\n'.join(texts)

def selftest():
    """Falsadores del adaptador con fixtures ajenos al banco."""
    cases=[([{'block_label':'text','block_content':'No pagará 439.'}],'No pagará 439.'),([{'block_label':'header','block_content':'Título'},{'block_label':'footer','block_content':'Pie'}],'Título Pie'),([{'block_label':'table','block_content':'<table><tr><td rowspan="2">A</td><td>12</td></tr><tr><td>13</td></tr></table>'}],'A 12 13'),([{'block_label':'text','block_content':'3 < 4 & 8'}],'3 < 4 & 8'),([{'block_label':'table','block_content':'<table><tr><td>Á &amp; Ñ</td></tr></table>'}],'Á & Ñ')]
    for blocks,expected in cases:
        if ' '.join(plain(blocks).split())!=expected:raise RuntimeError('adapter fixture failed')
    print(json.dumps({'adapter_checks':len(cases),'passed':True}),flush=True)

def fail_timeout(signum,frame):
    """Interrumpe un caso excesivamente largo sin inventar una predicción."""
    raise TimeoutError('page or warmup exceeded 1800 seconds')

def run():
    """Ejecuta una sola pasada; la evaluación ocurre sólo tras completar los cinco casos."""
    selftest()
    if (ROOT/'run-started.json').exists():raise RuntimeError('run already started; refusing duplicate')
    manifest=json.loads((BANK/'manifest.json').read_text())
    if sha(ROOT/'gold-ai-v1.json')!=GOLD_SHA:raise RuntimeError('gold hash mismatch')
    for page in manifest['pages']:
        if sha(BANK/page['image'])!=page['image_sha256']:raise RuntimeError('image hash mismatch')
    import paddle, numpy as np
    from PIL import Image, ImageDraw, ImageFont
    from paddleocr import PaddleOCRVL
    import yaml
    np.random.seed(20261015);paddle.seed(20261015)
    config=yaml.safe_load(pathlib.Path('/tmp/paddle-ocr-venv/lib/python3.12/site-packages/paddlex/configs/pipelines/PaddleOCR-VL-1.6.yaml').read_text())
    config['batch_size']=1;config['use_queues']=False
    config['SubModules']['LayoutDetection']['batch_size']=1
    config['SubModules']['VLRecognition']['batch_size']=1
    config['SubModules']['LayoutDetection']['model_dir']=str(ROOT/'models/layout')
    config['SubModules']['VLRecognition']['model_dir']=str(ROOT/'models/vl')
    config['markdown_ignore_labels']=[]
    config['use_ocr_for_image_block']=False
    (ROOT/'pipeline.yaml').write_text(yaml.safe_dump(config,sort_keys=False))
    prediction_config={'max_new_tokens':4096}
    seal={'sealed_utc':now(),'runner_sha256':sha(__file__),'manifest_sha256':sha(BANK/'manifest.json'),'gold_sha256':GOLD_SHA,'gold_type':'AI visual adjudication; not human certified','pipeline_sha256':sha(ROOT/'pipeline.yaml'),'pipeline':config,'predict':prediction_config,'model_hashes':json.loads((ROOT/'models.json').read_text()),'packages':{d.metadata['Name']:d.version for d in importlib.metadata.distributions()},'device':'cpu','cpu_threads':1,'MKLDNN':False,'image_preprocessing':'original frozen PNG, internal pipeline defaults; no manual masks/crops','adapter':'all parsing_res_list block_content in native order; HTML table markup removed in DOM order; no text correction or label exclusion','timeout_seconds_per_page':1800,'warmup':'one synthetic image, same pipeline, at most 128 new tokens','cpu_info':pathlib.Path('/proc/cpuinfo').read_text(),'meminfo':pathlib.Path('/proc/meminfo').read_text(),'loadavg':pathlib.Path('/proc/loadavg').read_text()}
    write('seal.json',seal);write('run-started.json',{'started_utc':now(),'pid':os.getpid()})
    print('SEALED',seal['runner_sha256'],flush=True)
    t=time.monotonic()
    pipeline=PaddleOCRVL(pipeline_version='v1.6',paddlex_config=config,device='cpu',cpu_threads=1,enable_mkldnn=False)
    write('loaded.json',{'loaded_utc':now(),'load_seconds':time.monotonic()-t})
    image=Image.new('RGB',(800,220),'white');d=ImageDraw.Draw(image);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',28)
    d.text((30,40),'Prueba de lectura. No pagar 123 pesos.',font=font,fill='black');image.save(ROOT/'warmup.png')
    signal.signal(signal.SIGALRM,fail_timeout);signal.alarm(1800)
    t=time.monotonic();warm=pipeline.predict(str(ROOT/'warmup.png'),max_new_tokens=128);warm_seconds=time.monotonic()-t;signal.alarm(0)
    write('warmup.json',{'seconds':warm_seconds,'results':[x.json for x in warm]});print('WARMUP_DONE',warm_seconds,flush=True)
    predictions={'benchmark_id':manifest['benchmark_id'],'engine_author':'PaddlePaddle','engine':'PaddleOCR-VL-1.6','pages':{}}
    times=[]
    for page in manifest['pages']:
        write('status.json',{'phase':'inference','page':page['id'],'started_utc':now(),'completed_pages':len(predictions['pages'])})
        signal.alarm(1800);t=time.monotonic();results=pipeline.predict(str(BANK/page['image']),**prediction_config);seconds=time.monotonic()-t;signal.alarm(0)
        if len(results)!=1:raise RuntimeError('expected one result per PNG')
        raw=results[0].json
        if isinstance(raw,str):raw=json.loads(raw)
        obj=raw.get('res',raw)
        text=plain(obj['parsing_res_list'])
        write(page['id']+'-raw.json',raw)
        predictions['pages'][page['id']]={'image_sha256':page['image_sha256'],'text':text}
        times.append({'id':page['id'],'seconds':seconds,'characters':len(text),'blocks':len(obj['parsing_res_list']),'raw_sha256':sha(ROOT/(page['id']+'-raw.json')),'rss_peak_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
        write('predictions.json',predictions);write('timings.json',times)
        print('PAGE_DONE',page['id'],round(seconds,3),len(text),flush=True)
    command=[sys.executable,str(BANK/'heldout.py'),'score',str(BANK/'manifest.json'),'--gold',str(ROOT/'gold-ai-v1.json'),'--gold-sha256',GOLD_SHA,'--predictions',str(ROOT/'predictions.json')]
    result=subprocess.run(command,capture_output=True,text=True,timeout=180)
    write('score-receipt.json',{'command':command,'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
    if result.returncode!=0:raise RuntimeError('score failed')
    write('scores.json',json.loads(result.stdout));write('status.json',{'phase':'completed','completed_utc':now(),'completed_pages':5})
    print('RUN_COMPLETED',flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--selftest',action='store_true');a=ap.parse_args()
    if a.selftest:selftest()
    else:
        try:run()
        except Exception:
            error=traceback.format_exc();write('failure.json',{'utc':now(),'traceback':error});print(error,file=sys.stderr,flush=True);sys.exit(1)
