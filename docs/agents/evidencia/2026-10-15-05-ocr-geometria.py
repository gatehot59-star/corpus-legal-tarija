#!/usr/bin/env python3
"""Diagnóstico geométrico puro; stdlib, sin OCR ni texto al ordenar."""
import argparse, hashlib, json, math, pathlib, statistics, time, unicodedata
from datetime import datetime, timezone
CONFIG = {'vertical_gap_heights':1.5, 'horizontal_gap_heights':0.5,
          'row_tolerance_heights':0.5, 'max_deskew_degrees':15}

def digest(data):
    """SHA-256 de bytes."""
    return hashlib.sha256(data).hexdigest()

def norm(text):
    """NFC y colapso de blancos, sin corregir palabras."""
    return ' '.join(unicodedata.normalize('NFC',text).split())

def distance(a,b):
    """Levenshtein por dos filas."""
    row = list(range(len(b)+1))
    for i,x in enumerate(a,1):
        nxt = [i]
        for j,y in enumerate(b,1):
            nxt.append(min(nxt[-1]+1,row[j]+1,row[j-1]+(x!=y)))
        row = nxt
    return row[-1]

def order(polys):
    """Sólo índices: desinclinación y cortes XY por espacios vacíos."""
    if not polys:
        return [], {'angle_deg':0,'cuts':[]}
    if any(len(p)!=4 or any(len(v)!=2 or not all(math.isfinite(z) for z in v) for v in p) for p in polys):
        raise ValueError('Polígonos inválidos')
    angles = [math.atan2(p[1][1]-p[0][1],p[1][0]-p[0][0]) for p in polys]
    angle = statistics.median(angles)
    limited = abs(math.degrees(angle))>CONFIG['max_deskew_degrees']
    if limited:
        angle = 0.0
    c,s = math.cos(angle),math.sin(angle)
    boxes = []
    for p in polys:
        q = [(x*c+y*s,-x*s+y*c) for x,y in p]
        xs,ys = zip(*q)
        boxes.append((min(xs),min(ys),max(xs),max(ys)))
    h = statistics.median(b[3]-b[1] for b in boxes)
    if h<=0 or any(b[2]<=b[0] or b[3]<=b[1] for b in boxes):
        raise ValueError('Cajas degeneradas')
    cuts = []
    def gaps(ids,axis):
        intervals = sorted((boxes[i][axis],boxes[i][axis+2]) for i in ids)
        end = intervals[0][1]
        out = []
        for lo,hi in intervals[1:]:
            if lo>end:
                out.append((lo-end,(lo+end)/2))
            end = max(end,hi)
        return sorted(out,reverse=True)
    def visit(ids):
        if len(ids)<=1:
            return ids
        for axis,threshold in ((0,CONFIG['vertical_gap_heights']),(1,CONFIG['horizontal_gap_heights'])):
            for gap,cut in gaps(ids,axis):
                if gap<threshold*h:
                    continue
                left = [i for i in ids if boxes[i][axis+2]<=cut]
                right = [i for i in ids if boxes[i][axis]>=cut]
                if len(left)+len(right)!=len(ids) or not left or not right:
                    continue
                if axis==0 and min(len(left),len(right))<2:
                    continue
                cuts.append({'axis':axis,'at':cut,'gap':gap,'members':ids})
                return visit(left)+visit(right)
        pending = sorted(ids,key=lambda i:((boxes[i][1]+boxes[i][3])/2,boxes[i][0],i))
        result = []
        while pending:
            y = (boxes[pending[0]][1]+boxes[pending[0]][3])/2
            group = [i for i in pending if (boxes[i][1]+boxes[i][3])/2-y<=CONFIG['row_tolerance_heights']*h]
            result.extend(sorted(group,key=lambda i:(boxes[i][0],i)))
            selected = set(group)
            pending = [i for i in pending if i not in selected]
        return result
    return visit(list(range(len(polys)))), {'angle_deg':math.degrees(angle),'angle_outside_limit':limited,'height':h,'cuts':cuts}

def validate(texts,permutation,ordered):
    """Rechaza pérdidas, duplicados y cambios de texto."""
    if sorted(permutation)!=list(range(len(texts))):
        raise ValueError('No es una permutación')
    if ordered!=[texts[i] for i in permutation]:
        raise ValueError('Texto alterado')

def fixtures():
    """Geometrías construidas, no nuevos ensayos OCR ni gold real."""
    def box(x,y,w=80,h=10):
        return [[x,y],[x+w,y],[x+w,y+h],[x,y+h]]
    cases = [('una_columna',[box(0,40),box(0,0),box(0,20)],[1,2,0]),
             ('dos_columnas',[box(0,0),box(200,0),box(0,20),box(200,20)],[0,2,1,3]),
             ('titulo_ancho',[box(0,-40,280),box(0,0),box(200,0),box(0,20),box(200,20)],[0,1,3,2,4]),
             ('tres_columnas',[box(x,y) for y in (0,20) for x in (0,200,400)],[0,3,1,4,2,5]),
             ('vacio',[],[])]
    for deg in (-7,7):
        a = math.radians(deg)
        p = [[[x*math.cos(a)-y*math.sin(a),x*math.sin(a)+y*math.cos(a)] for x,y in q] for q in cases[1][1]]
        cases.append(('giro_'+str(deg),p,[0,2,1,3]))
    results = []
    for name,polys,expected in cases:
        actual,_ = order(polys)
        assert actual==expected,(name,actual,expected)
        results.append({'case':name,'expected':expected,'actual':actual,'pass':True})
    for perm,txt in [([0,0],['a','a']),([0],['a']),([0,1],['a','CAMBIO'])]:
        try:
            validate(['a','b'],perm,txt)
        except ValueError:
            results.append({'case':'mutacion','permutation':perm,'text':txt,'rejected':True})
        else:
            raise AssertionError('Mutación aceptada')
    return results

def run(source,output):
    """Sella antes de ordenar; conserva entradas/salidas para recomputar."""
    output.mkdir(parents=True,exist_ok=False)
    bank_path = source/'bank.json'
    bank = json.loads(bank_path.read_text())
    paths = {c['id']:source/'output-paddleocr'/(c['id']+'.raw.json') for c in bank['cases']}
    seal = {'utc':datetime.now(timezone.utc).isoformat(),'config':CONFIG,
            'script_sha256':digest(pathlib.Path(__file__).read_bytes()),
            'bank_sha256':digest(bank_path.read_bytes()),
            'inputs':{k:digest(v.read_bytes()) for k,v in paths.items()},
            'scope':'Regresión post hoc de diez salidas previas. No held-out OCR. Sin modificar Corpus.'}
    (output/'seal.json').write_text(json.dumps(seal,ensure_ascii=False,indent=2))
    tests = fixtures()
    records = []
    for case in bank['cases']:
        raw = json.loads(paths[case['id']].read_text())
        assert raw['exit']==0 and len(raw['raw'])==1
        res = raw['raw'][0]['res']
        texts,polys = res['rec_texts'],res['rec_polys']
        assert len(texts)==len(polys)==len(res['rec_scores'])
        start = time.perf_counter_ns()
        permutation,trace = order(polys)
        elapsed = (time.perf_counter_ns()-start)/1e9
        ordered = [texts[i] for i in permutation]
        validate(texts,permutation,ordered)
        text = '\n'.join(ordered)
        ref = case['reference']
        before,after = norm('\n'.join(texts)),norm(text)
        scores = None if ref is None else {'chars':len(norm(ref)),'words':len(norm(ref).split()),
            'before_char_edits':distance(norm(ref),before),'after_char_edits':distance(norm(ref),after),
            'before_word_edits':distance(norm(ref).split(),before.split()),
            'after_word_edits':distance(norm(ref).split(),after.split())}
        records.append({'id':case['id'],'input_sha256':seal['inputs'][case['id']],
            'texts':texts,'polys':polys,'permutation':permutation,'ordered_text':text,
            'text_sha256':digest(text.encode()),'seconds_geometry_only':elapsed,'trace':trace,
            'reference':ref,'scores':scores,'changed_order':permutation!=list(range(len(texts)))})
        (output/(case['id']+'.txt')).write_text(text)
    unchanged = all(digest(p.read_bytes())==seal['inputs'][k] for k,p in paths.items())
    assert unchanged and digest(bank_path.read_bytes())==seal['bank_sha256']
    record = {'seal':seal,'tests':tests,'cases':records,'inputs_unchanged':unchanged,
              'finished_utc':datetime.now(timezone.utc).isoformat()}
    (output/'record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
    print(json.dumps({'estado':'COMPLETADO','casos':len(records),'tests':tests,
          'resultados':[{'id':r['id'],'lines':len(r['texts']),'changed_order':r['changed_order'],
          'seconds':r['seconds_geometry_only'],'scores':r['scores']} for r in records]},ensure_ascii=False))

if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=pathlib.Path)
    parser.add_argument('output',type=pathlib.Path)
    args = parser.parse_args()
    run(args.source,args.output)
