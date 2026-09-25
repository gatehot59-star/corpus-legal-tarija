import json, re, sys

# Lector compacto del residual de adjudicacion gold.
# Uso: gold_review.py [N]   -> imprime los primeros N pendientes (default 60)
# Pendiente = variante sin fallo en rulings_auto.tsv ni rulings_manual.tsv.
# Los bloques largos se imprimen multilinea; el resto en una linea.

GB='/tmp/gold_build/'
variants={}; order=[]
for line in open(GB+'variants.tsv'):
    p=line.rstrip('\n').split('\t')
    while len(p)<6: p.append('')
    vid,count,kind,a,b,c=p[:6]
    variants[int(vid)]=dict(id=int(vid),count=int(count),kind=kind,a=a,b=b,c=c)
    order.append(int(vid))

done=set()
for fn in ('rulings_auto.tsv','rulings_manual.tsv'):
    try:
        for line in open(GB+fn):
            p=line.rstrip('\n').split('\t')
            if p and p[0].isdigit(): done.add(int(p[0]))
    except FileNotFoundError:
        pass

vtuple={}
for vid,r in variants.items():
    vtuple[(r['kind'],r['a'],r['b'],r['c'])]=vid
ctxmap={}
for line in open(GB+'clusters.jsonl'):
    cl=json.loads(line)
    vid=vtuple.get((cl['kind'],cl['a'],cl['b'],cl['c']))
    if vid is not None and vid not in ctxmap:
        ctxmap[vid]=(cl['key'],cl['ci'],cl['ctx'])

def nw(t): return ' '.join(t.split())

pending=[vid for vid in order if vid not in done]
N=int(sys.argv[1]) if len(sys.argv)>1 else 60
print('PENDIENTES_TOTAL',len(pending))
for i,vid in enumerate(pending[:N]):
    r=variants[vid]
    key,ci,ctx=ctxmap.get(vid,('?','?',''))
    ctx=nw(ctx)[:110]
    aa,bb,cc=nw(r['a']),nw(r['b']),nw(r['c'])
    if max(len(aa),len(bb),len(cc))<=55:
        print(f"{vid}|x{r['count']}|{r['kind']}|A[{aa}]|B[{bb}]|C[{cc}]|{ctx}")
    else:
        print(f"### {vid} x{r['count']} {r['kind']} @{key}#{ci}")
        print(f"A[{aa[:280]}]")
        print(f"B[{bb[:280]}]")
        print(f"C[{cc[:280]}]")
        print(f"CTX: {ctx}")
