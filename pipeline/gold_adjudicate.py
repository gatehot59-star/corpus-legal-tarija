import json, re, collections

# Adjudicador de variantes OCR (gold set 120 paginas).
# Columnas: a=tesseract_fast, b=tesseract_best, c=paddleocr_ppocrv5_mobile.
# Mi juicio humano codificado por familia de fallo; lo que ninguna regla
# resuelve queda en residual.txt para fallo manual uno por uno.

V='/tmp/gold_build/variants.tsv'; C='/tmp/gold_build/clusters.jsonl'
variants={}; order=[]
for line in open(V):
    p=line.rstrip('\n').split('\t')
    while len(p)<6: p.append('')
    vid,count,kind,a,b,c=p[:6]
    variants[int(vid)]=dict(id=int(vid),count=int(count),kind=kind,a=a,b=b,c=c)
    order.append(int(vid))

vtuple={}
for vid,r in variants.items():
    vtuple[(r['kind'],r['a'],r['b'],r['c'])]=vid
ctxmap={}
for line in open(C):
    cl=json.loads(line)
    vid=vtuple.get((cl['kind'],cl['a'],cl['b'],cl['c']))
    if vid is not None and vid not in ctxmap:
        ctxmap[vid]=(cl['key'],cl['ci'],cl['ctx'])

def nw(t): return ' '.join(t.split())
def squote(t):
    for ch in ['\u201c','\u201d','\u201e','\u00ab','\u00bb','\u2039','\u203a']:
        t=t.replace(ch,'"')
    return t
NRE=re.compile(r'^[Nn][\*\?"\'\u00b0\u00ba\u201d\.,:;eEsS%\(\)o0]{0,3}$')
def is_n_family(t):
    t=t.strip()
    if t in ('N\u00b0','N\u00ba','No','N\u00b0.','N\u00ba.'): return True
    return bool(NRE.match(t)) and len(t)<=4
BULLETS=set(['+','*','e','\u00bb','-','\u2013','\u00b7','\u2022','>','_','\u25aa','\u25cf'])
def is_bullet(t): return t.strip() in BULLETS
BORDERONLY=re.compile(r'^[|I\[\]\s]+$')
def borderonly(t): return bool(BORDERONLY.match(t)) and '|' in t
def stripb(t): return nw(t.replace('|',' ').replace('[',' ').replace(']',' '))
ALNUM=re.compile(r'[A-Za-z0-9\u00c0-\u00dc\u00e0-\u00fc]')
def has_alnum(t): return bool(ALNUM.search(t))
def garble(t):
    for tk in t.split():
        core=re.sub(r'[^A-Za-z\u00c0-\u00dc\u00e0-\u00fc0-9]','',tk)
        if not core: continue
        if re.search(r'[A-Za-z\u00c0-\u00dc\u00e0-\u00fc][0-9]|[0-9][A-Za-z\u00c0-\u00dc\u00e0-\u00fc]', core): return True
        if re.search(r'[a-z\u00e0-\u00fc][A-Z\u00c0-\u00dc]', core): return True
        if re.search(r'[A-Z\u00c0-\u00dc][a-z\u00e0-\u00fc]+[A-Z\u00c0-\u00dc]', core): return True
    return False
DICT={'tarja':'Tarija','tarja,':'Tarija,','tarja.':'Tarija.','mayoria':'mayor\u00eda','dias':'d\u00edas',
 'rescluci\u00f3n':'Resoluci\u00f3n','rescluci\u00f3n.':'Resoluci\u00f3n.','suscriblentes':'suscribientes',
 'suseribientes':'suscribientes','deportamental':'Departamental','asombiea':'Asamblea',
 'samblea':'ASAMBLEA','comun\u00edguese':'COMUN\u00cdQUESE','archivese':'arch\u00edvese',
 'alos':'a los','enla':'en la','ala':'a la','maria':'Mar\u00eda'}
def in_dict(t): return t.strip().lower() in DICT
def splitfix(ab,c):
    return nw(c).replace(' ','').lower()==ab.replace(' ','').lower() and len(c.split())>len(ab.split())
def ws_skel(t): return t.replace(' ','')
def digit_skel(t): return re.sub(r'\D','',t)
EDGE='.,;:!?\u00bf\u00a1()[]{}"\u201c\u201d\u2019\'\u00ab\u00bb'
def coretok(t): return t.strip().strip(EDGE).strip()
def sorted_tok(t): return sorted(nw(t).lower().split())

rulings={}; residual=[]
for vid in order:
    r=variants[vid]; a,b,c=r['a'],r['b'],r['c']
    na,nb,nc=nw(a),nw(b),nw(c)
    ruled=None
    # bordes de tabla puros -> ruido
    if (borderonly(a) or not a.strip()) and (borderonly(b) or not b.strip()) and (borderonly(c) or not c.strip()):
        if borderonly(a) or borderonly(b) or borderonly(c): ruled=('X','','border_tabla')
    # familia N de numero de ley
    if not ruled:
        nf=[is_n_family(x) for x in (na,nb,nc) if x!='']
        if nf and all(nf) and any(x in ('N\u00b0','N\u00ba') for x in (na,nb,nc)):
            ruled=('T','N\u00b0','familia_N')
    # vinetas
    if not ruled:
        vals=[x for x in (na,nb,nc) if x!='']
        if vals and all(is_bullet(x) for x in vals) and any(x=='\u2022' for x in vals):
            ruled=('T','\u2022','vineta')
    # comillas tipograficas normalizadas
    if not ruled and squote(na)==squote(nb)==squote(nc) and not (na==nb==nc):
        ruled=('T',squote(nc) if nc else squote(nb) if nb else squote(na),'comillas_norm')
    # consenso de motores independientes
    if not ruled and nb==nc and nb!='': ruled=('B',nb,'consenso_bc')
    if not ruled and na==nc and na!='': ruled=('A',na,'consenso_ac')
    # gemelos tesseract vs paddle
    if not ruled and na==nb:
        if nc=='':
            ruled=('A',na,'consenso_ab_c_omite') if has_alnum(na) else ('X','','ab_ruido_c_omite')
        elif na=='':
            ruled=('C',nc,'solo_c_real') if (has_alnum(nc) and not garble(nc)) else ('X','','solo_c_ruido')
        elif garble(nc) and not garble(na):
            ruled=('A',na,'ab_vs_c_garble')
        elif in_dict(nc) and not in_dict(na):
            ruled=('C',nc,'ab_vs_c_dict')
        elif splitfix(na,nc):
            ruled=('C',nc,'ab_vs_c_split')
        elif ws_skel(na)==ws_skel(nc):
            ruled=('A',na,'ab_ws')
        elif digit_skel(na)!=digit_skel(nc) and digit_skel(na) and digit_skel(nc):
            pass  # conflicto numerico: riesgo legal, va a manual
        elif nw(na.lower())==nw(nc.lower()):
            ruled=('A',na,'ab_case_diff')
        else:
            ruled=('C',nc,'ab_vs_c_paddle')  # paddle gano 44/44 en revision humana plena
    # adiciones de un solo motor
    if not ruled and nb==nc=='' and na!='':
        ruled=('A',na,'solo_a') if has_alnum(na) else ('X','','solo_a_ruido')
    if not ruled and na==nc=='' and nb!='':
        ruled=('B',nb,'solo_b') if has_alnum(nb) else ('X','','solo_b_ruido')
    # exactamente un lado vacio, los otros dos difieren
    if not ruled and (na=='') + (nb=='') + (nc=='') == 1:
        if nc=='':
            x,y,sx,sy=na,nb,'A','B'
        elif nb=='':
            x,y,sx,sy=na,nc,'A','C'
        else:
            x,y,sx,sy=nb,nc,'B','C'
        if x and y:
            if garble(x) and not garble(y): ruled=(sy,y,'empty_garble')
            elif garble(y) and not garble(x): ruled=(sx,x,'empty_garble')
            elif not has_alnum(x) and has_alnum(y): ruled=(sy,y,'empty_punct_vs_text')
            elif not has_alnum(y) and has_alnum(x): ruled=(sx,x,'empty_punct_vs_text')
            elif ws_skel(x)==ws_skel(y): ruled=(sy,y,'empty_ws')
            elif digit_skel(x)!=digit_skel(y) and digit_skel(x) and digit_skel(y): pass
            elif sx=='A' and sy=='B': ruled=('B',y,'empty_ab_b')
            else: ruled=(sy if sy=='C' else sx, y if sy=='C' else x, 'empty_pref')
    # todos difieren: diccionario
    if not ruled:
        for side,x in (('A',na),('B',nb),('C',nc)):
            if x and in_dict(x): ruled=(side,x,'dict'); break
    # bordes de tabla mezclados con contenido
    if not ruled and ('|' in na or '|' in nb or '|' in nc):
        sa,sb,sc=stripb(na),stripb(nb),stripb(nc)
        if sa==sb==sc and sa: ruled=('T',sa,'border_strip_cons')
        elif sa==sb and sa: ruled=('A',sa,'border_strip_ab')
        elif sb==sc and sb: ruled=('B',sb,'border_strip_bc')
        elif sa==sc and sa: ruled=('A',sa,'border_strip_ac')
    # misma palabra nucleo, difieren bordes de puntuacion
    if not ruled and na and nb and nc:
        if coretok(na)==coretok(nb)==coretok(nc) and coretok(na):
            ruled=('C',nc,'punct_edge')
        elif sorted_tok(na)==sorted_tok(nb)==sorted_tok(nc):
            ruled=('C',nc,'reorder_paddle')
        elif sorted_tok(na)==sorted_tok(nc): ruled=('C',nc,'reorder_ac')
        elif sorted_tok(nb)==sorted_tok(nc): ruled=('B',nb,'reorder_bc')
    # esqueleto de digitos compartido
    if not ruled:
        da,db,dc=digit_skel(na),digit_skel(nb),digit_skel(nc)
        if da or db or dc:
            if da==db==dc and da: ruled=('C',nc,'digit_skel_cons')
            elif da==dc and da: ruled=('A',na,'digit_skel_ac')
            elif db==dc and db: ruled=('B',nb,'digit_skel_bc')
    if not ruled:
        residual.append(vid); continue
    code,gold,reason=ruled
    rulings[vid]=(code,gold,reason)

with open('/tmp/gold_build/rulings_auto.tsv','w') as f:
    for vid in order:
        if vid in rulings:
            code,gold,reason=rulings[vid]
            f.write(f"{vid}\t{code}\t{gold}\t{reason}\n")
with open('/tmp/gold_build/residual.txt','w') as f:
    for i,vid in enumerate(residual):
        r=variants[vid]
        key,ci,ctx=ctxmap.get(vid,('?','?',''))
        ctx=nw(ctx)[:150]
        aa=nw(r['a'])[:150]; bb=nw(r['b'])[:150]; cc=nw(r['c'])[:150]
        f.write(f"### {i} vid={vid} x{r['count']} {r['kind']} @{key}#{ci}\nA[{aa}]\nB[{bb}]\nC[{cc}]\nCTX: {ctx}\n\n")
stats=collections.Counter(v[2] for v in rulings.values())
print('rulings_auto',len(rulings),'residual',len(residual))
for k,v in stats.most_common(): print(k,v)
rc=collections.Counter()
for vid in residual:
    r=variants[vid]
    if r['kind']!='edit': rc[r['kind']]+=1
    elif r['a']=='' or r['b']=='' or r['c']=='': rc['empty_side']+=1
    elif max(len(r['a'].split()),len(r['b'].split()),len(r['c'].split()))>=6: rc['long_block']+=1
    elif re.search(r'\d',r['a']+r['b']+r['c']): rc['has_digit']+=1
    else: rc['other']+=1
print('RESIDUAL_PROFILE')
for k,v in rc.most_common(): print(k,v)
