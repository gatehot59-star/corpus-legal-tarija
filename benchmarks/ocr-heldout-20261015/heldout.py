#!/usr/bin/env python3
"""Held-out Corpus: materializar PNG, verificar integridad y puntuar sólo gold adjudicado."""
import argparse, copy, hashlib, json, pathlib, subprocess, sys, tempfile, unicodedata, urllib.request

class InvalidBenchmark(ValueError):
    """El banco o la evidencia no cumplen el contrato."""

def require(condition, message):
    """Validación activa incluso con Python -O."""
    if not condition: raise InvalidBenchmark(message)

def sha(data):
    """SHA-256 de bytes exactos."""
    return hashlib.sha256(data).hexdigest()

def read(path):
    """Lee JSON UTF-8 completo."""
    return json.loads(pathlib.Path(path).read_text(encoding='utf-8'))

def normalize(text):
    """NFC y blancos: no corregir tildes, números ni orden."""
    return ' '.join(unicodedata.normalize('NFC',text).split())

def distance(a,b):
    """Levenshtein con memoria lineal."""
    previous=list(range(len(b)+1))
    for i,x in enumerate(a,1):
        current=[i]
        for j,y in enumerate(b,1):
            current.append(min(previous[j]+1,current[j-1]+1,previous[j-1]+(x!=y)))
        previous=current
    return previous[-1]

def validate_manifest(m):
    """Verifica identidad de páginas, separación documental y gold aún reservado."""
    require(m['schema']==1,'schema desconocido')
    ids=[p['id'] for p in m['pages']]
    require(ids and len(ids)==len(set(ids)),'páginas repetidas o ausentes')
    docs={d['id']:d for d in m['documents']}
    require(len(docs)==len(m['documents']),'documentos duplicados')
    excluded=set(m['overlap_evidence']['excluded_pdf_sha256'])
    require(not excluded.intersection(d['pdf_sha256'] for d in docs.values()),'fuga documental desde banco anterior')
    images=[p['image_sha256'] for p in m['pages']]
    require(len(images)==len(set(images)),'imágenes duplicadas')
    require(not set(images).intersection(m['overlap_evidence']['excluded_previous_bank_image_sha256']),'imagen del banco anterior')
    for p in m['pages']:
        require(p['document_id'] in docs,'documento desconocido')
        require(isinstance(p['page'],int) and p['page']>0,'número de página inválido')
        require(p['image']=='images/'+p['id']+'.png','ruta inesperada')
    return docs

def verify_files(m,root):
    """Comprueba PDF y PNG locales contra hashes sellados."""
    docs=validate_manifest(m);root=pathlib.Path(root)
    for d in docs.values():
        path=root/('source-'+d['id'][-2:]+'.pdf')
        require(path.is_file() and sha(path.read_bytes())==d['pdf_sha256'],'PDF distinto o ausente: '+d['id'])
    for p in m['pages']:
        path=root/p['image']
        require(path.is_file() and sha(path.read_bytes())==p['image_sha256'],'PNG distinto o ausente: '+p['id'])
    return {'verified_documents':len(docs),'verified_pages':len(m['pages']),'gold_status':m['gold_status'],'candidate_ocr_runs_in_this_tool':0}

def materialize(m,destination):
    """Descarga fuentes oficiales y reproduce PNG, sin OCR ni sobrescritura."""
    docs=validate_manifest(m);root=pathlib.Path(destination)
    require(not root.exists(),'destino existente: no se sobrescribe')
    root.mkdir(parents=True);(root/'images').mkdir()
    v=subprocess.run(['pdftoppm','-v'],capture_output=True,text=True,check=True)
    require('pdftoppm version 24.02.0' in v.stderr+v.stdout,'requiere Poppler 24.02.0 para reproducir bytes')
    events=[]
    for d in docs.values():
        require(d['url'].startswith('https://www.tarija.gob.bo/'),'fuente no autorizada')
        with urllib.request.urlopen(d['url'],timeout=60) as response:
            require(response.geturl().startswith('https://www.tarija.gob.bo/'),'redirección fuera de fuente')
            body=response.read(20_000_001)
        require(len(body)<=20_000_000 and body.startswith(b'%PDF-'),'PDF inválido o demasiado grande')
        require(sha(body)==d['pdf_sha256'],'fuente cambió: no reemplazar silenciosamente')
        (root/('source-'+d['id'][-2:]+'.pdf')).write_bytes(body)
    for p in m['pages']:
        source=root/('source-'+p['document_id'][-2:]+'.pdf');out=root/p['image']
        command=['pdftoppm','-f',str(p['page']),'-l',str(p['page']),'-r','300','-gray','-singlefile','-png',str(source),str(out.with_suffix(''))]
        result=subprocess.run(command,capture_output=True,text=True,timeout=120)
        events.append({'id':p['id'],'command':command,'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
        (root/'materialize-log.json').write_text(json.dumps(events,ensure_ascii=False,indent=2))
        require(result.returncode==0,'falló rasterización')
    return verify_files(m,root)

def score(m,gold,predictions):
    """Puntúa todas las páginas; metadata de revisión es declarativa, no prueba de autoría."""
    validate_manifest(m)
    require(gold.get('benchmark_id')==m['benchmark_id'],'gold de otro banco')
    require(gold.get('status')=='adjudicated','gold pendiente: no emitir precisión')
    require(gold.get('origin')=='independent_visual_transcription','gold no visual')
    people=gold.get('transcribers',[])
    require(len(people)==2 and all(isinstance(x,str) and x.strip() for x in people) and len(set(people))==2,'dos transcriptores distintos obligatorios')
    require(isinstance(gold.get('adjudicator'),str) and gold['adjudicator'].strip(),'falta adjudicador')
    require(predictions.get('benchmark_id')==m['benchmark_id'],'predicciones de otro banco')
    require(isinstance(predictions.get('engine_author'),str) and predictions['engine_author'].strip(),'falta autor del motor')
    require(predictions['engine_author'] not in people,'transcriptores no independientes del autor declarado')
    ids={p['id'] for p in m['pages']};refs=gold.get('pages',{});outputs=predictions.get('pages',{})
    require(set(refs)==set(outputs)==ids,'cobertura incompleta o páginas extra')
    rows=[]
    for p in m['pages']:
        ref,out=refs[p['id']],outputs[p['id']]
        require(ref.get('image_sha256')==out.get('image_sha256')==p['image_sha256'],'hash de imagen incorrecto')
        require(ref.get('status')=='adjudicated' and ref.get('unresolved_regions')==[],'regiones o revisión pendientes')
        require(isinstance(ref.get('scope_notes'),str) and ref['scope_notes'].strip(),'falta alcance de transcripción')
        require(isinstance(ref.get('text'),str) and normalize(ref['text']),'referencia vacía')
        require(isinstance(out.get('text'),str),'salida no textual')
        a,b=normalize(ref['text']),normalize(out['text']);aw,bw=a.split(),b.split()
        ce,we=distance(a,b),distance(aw,bw)
        rows.append({'id':p['id'],'document_id':p['document_id'],'reference_chars':len(a),'reference_words':len(aw),'character_edits':ce,'word_edits':we,'cer':ce/len(a),'wer':we/len(aw)})
    ce=sum(x['character_edits'] for x in rows);we=sum(x['word_edits'] for x in rows)
    documents=[]
    for doc in sorted(set(x['document_id'] for x in rows)):
        subset=[x for x in rows if x['document_id']==doc]
        documents.append({'id':doc,'cer':sum(x['character_edits'] for x in subset)/sum(x['reference_chars'] for x in subset),'wer':sum(x['word_edits'] for x in subset)/sum(x['reference_words'] for x in subset)})
    return {'pages':rows,'documents':documents,'micro_cer':ce/sum(x['reference_chars'] for x in rows),'micro_wer':we/sum(x['reference_words'] for x in rows),'document_macro_cer':sum(x['cer'] for x in documents)/len(documents),'document_macro_wer':sum(x['wer'] for x in documents)/len(documents),'not_claimed':'representatividad general, precisión jurídica o verificación de identidad de los anotadores'}

def selftest(m):
    """Falsadores con textos artificiales; NO son anotaciones ni OCR de las cinco páginas."""
    validate_manifest(m);g={'benchmark_id':m['benchmark_id'],'status':'adjudicated','origin':'independent_visual_transcription','transcribers':['test-A','test-B'],'adjudicator':'test-C','pages':{}}
    o={'benchmark_id':m['benchmark_id'],'engine_author':'test-engine','pages':{}}
    for p in m['pages']:
        g['pages'][p['id']]={'status':'adjudicated','unresolved_regions':[],'scope_notes':'fixture artificial, nunca usar como gold real','image_sha256':p['image_sha256'],'text':'No pagará 439.'}
        o['pages'][p['id']]={'image_sha256':p['image_sha256'],'text':'No pagará 439.'}
    tests=[]
    require(score(m,g,o)['micro_cer']==0,'identidad falló');tests.append('identical_zero')
    bad=copy.deepcopy(o)
    for p in bad['pages'].values():p['text']='pagará 438.'
    require(score(m,g,bad)['micro_cer']>0,'número/negación invisibles');tests.append('number_and_negation_detected')
    for p in bad['pages'].values():p['text']=''
    require(score(m,g,bad)['micro_cer']==1,'salida vacía no penalizada');tests.append('empty_output_full_deletion')
    for p in bad['pages'].values():p['text']='No pagará 439. '*4
    require(score(m,g,bad)['micro_cer']>1,'duplicaciones no penalizadas');tests.append('duplication_can_exceed_100pct')
    for kind in ['pending_gold','same_transcriber','ocr_reference','missing_page','changed_image','unresolved_region','engine_author_transcriber']:
        gg,oo=copy.deepcopy(g),copy.deepcopy(o);key=next(iter(gg['pages']))
        if kind=='pending_gold':gg['status']='pending'
        elif kind=='same_transcriber':gg['transcribers']=['test-A','test-A']
        elif kind=='ocr_reference':gg['origin']='tesseract'
        elif kind=='missing_page':oo['pages'].pop(key)
        elif kind=='changed_image':oo['pages'][key]['image_sha256']='0'*64
        elif kind=='unresolved_region':gg['pages'][key]['unresolved_regions']=['ilegible']
        else:oo['engine_author']='test-A'
        try:score(m,gg,oo)
        except InvalidBenchmark:tests.append(kind+'_rejected')
        else:raise InvalidBenchmark('mutación aceptada: '+kind)
    mm=copy.deepcopy(m);mm['overlap_evidence']['excluded_pdf_sha256'].append(mm['documents'][0]['pdf_sha256'])
    try:validate_manifest(mm)
    except InvalidBenchmark:tests.append('prior_document_rejected')
    else:raise InvalidBenchmark('documento contaminado aceptado')
    return {'checks':tests,'passed':len(tests),'real_ocr_runs':0,'real_gold_created':0,'test_data':'artificial only, not benchmark annotations'}

def main():
    """CLI fail-closed: el estado pendiente devuelve 2 y no genera métricas."""
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['status','verify','materialize','selftest','score']);ap.add_argument('manifest',type=pathlib.Path);ap.add_argument('--root',type=pathlib.Path);ap.add_argument('--gold',type=pathlib.Path);ap.add_argument('--gold-sha256');ap.add_argument('--predictions',type=pathlib.Path);a=ap.parse_args();m=read(a.manifest)
    try:
        if a.action=='status':
            validate_manifest(m);print(json.dumps({'state':m['state'],'pages':len(m['pages']),'gold_status':m['gold_status'],'ready_for_accuracy_scoring':False}));return 2
        if a.action in ('verify','materialize'):
            require(a.root is not None,'falta --root');out=verify_files(m,a.root) if a.action=='verify' else materialize(m,a.root)
        elif a.action=='selftest':out=selftest(m)
        else:
            require(a.gold is not None and a.predictions is not None and a.gold_sha256 is not None,'falta gold sellado o predicciones')
            require(sha(a.gold.read_bytes())==a.gold_sha256,'gold cambió después del sello')
            out=score(m,read(a.gold),read(a.predictions));out['gold_sha256']=a.gold_sha256
        print(json.dumps(out,ensure_ascii=False,indent=2));return 0
    except (InvalidBenchmark,OSError,KeyError,TypeError,ValueError,subprocess.SubprocessError) as error:
        print(json.dumps({'error':str(error),'metrics_emitted':False},ensure_ascii=False),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
