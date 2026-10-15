#!/usr/bin/env python3
"""Recalcula CER/WER publicados sin dependencias externas. No valida exactitud real."""
import array, copy, hashlib, json, pathlib, sys, unicodedata

def normalize(text):
    """Aplica únicamente NFC y colapso de blancos."""
    return ' '.join(unicodedata.normalize('NFC',text).split())

def distance(a,b):
    """Levenshtein mediante matriz completa."""
    matrix=[array.array('I',range(len(b)+1))]
    for i,x in enumerate(a,1):
        row=array.array('I',[i]+[0]*len(b))
        for j,y in enumerate(b,1):
            row[j]=min(matrix[i-1][j]+1,row[j-1]+1,matrix[i-1][j-1]+(x!=y))
        matrix.append(row)
    return matrix[-1][-1]

def verify(data):
    """Rechaza cambios en textos, scores, cobertura y códigos de salida."""
    assert data['complete'] and data['execution_exit']==0
    rows=data['runs'];assert len(rows)==20
    assert len({(r['id'],r['arm']) for r in rows})==20
    assert sum(len(r['exits']) for r in rows)==170
    scored=0
    for row in rows:
        assert all(x==0 for x in row['exits'])
        if row['score'] is None:
            assert 'text' not in row
            continue
        scored+=1
        assert hashlib.sha256(row['text'].encode()).hexdigest()==row['text_sha256']
        a,b=normalize(data['reference']),normalize(row['text'])
        ce,we=distance(a,b),distance(a.split(),b.split())
        assert (ce,we)==(row['score']['character_edits'],row['score']['word_edits'])
        assert ce/len(a)==row['score']['cer']
        assert we/len(a.split())==row['score']['wer']
    assert scored==8
    return {'runs':20,'calls':170,'scores_recomputed':8}

def main():
    """Verificación positiva y control negativo de score alterado."""
    data=json.loads(pathlib.Path(sys.argv[1]).read_text())
    result=verify(data)
    bad=copy.deepcopy(data)
    next(r for r in bad['runs'] if r['score'])['score']['character_edits']+=1
    try:verify(bad)
    except AssertionError:result['altered_score_rejected']=True
    else:raise AssertionError('el verificador aceptó un score falso')
    print(json.dumps(result))

if __name__=='__main__':main()
