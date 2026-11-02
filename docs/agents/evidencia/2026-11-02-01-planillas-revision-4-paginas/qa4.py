import subprocess, json, re, hashlib, sys
def ws(s): return re.sub(r'\s+', ' ', s).strip()
def sha_file(p):
    with open(p, 'rb') as f: return hashlib.sha256(f.read()).hexdigest()
man = json.load(open('manifest4.json', encoding='utf-8'))
if sha_file('ref.json') != man['reference']['file_sha256']: raise SystemExit('reference changed')
ref = json.load(open('ref.json', encoding='utf-8'))
leaks = json.load(open(sys.argv[1], encoding='utf-8'))
man['ocr_only_tokens'] = dict(file_sha256=sha_file(sys.argv[1]), count_by_page={k: len(v) for k, v in leaks.items()},
                              note='Lista retenida fuera de Git hasta terminar la revisión, para no mostrar errores del OCR al revisor.')
def mutate(s):
    for k, ch in enumerate(s):
        if ch.isdigit(): return s[:k] + str((int(ch) + 1) % 10) + s[k + 1:]
    k = len(s) // 2
    while not s[k].isalpha(): k += 1
    return s[:k] + (s[k].lower() if s[k].isupper() else s[k].upper()) + s[k + 1:]
allok = True
for P in man['pages']:
    lines = ref['pages'][P['pid']]['text'].split('\n')
    out = P['output']['file']
    pages = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', out], capture_output=True, text=True, check=True).stdout).group(1))
    t = subprocess.run(['pdftotext', '-raw', '-enc', 'UTF-8', out, '-'], capture_output=True, text=True, check=True).stdout
    T = ws(t)
    ids = [x[0] for x in P['lines']]
    rows = []
    for n, (lid, li) in enumerate(P['lines']):
        s = lines[li]; m = mutate(s); wid = ids[(n + 1) % len(ids)]
        rows.append(dict(id=lid, present=ws(lid + ' ' + s) in T,
                         mutant_rejected=(m != s) and ws(lid + ' ' + m) not in T,
                         wrong_id_rejected=ws(wid + ' ' + s) not in T))
    lk = leaks[P['pid']]
    found = [x for x in lk if x in t or x in T]
    qa = dict(pdf_pages=pages, lines_present_with_id=sum(r['present'] for r in rows), lines_total=len(rows),
              mutant_controls_rejected=sum(r['mutant_rejected'] for r in rows),
              wrong_id_controls_rejected=sum(r['wrong_id_rejected'] for r in rows),
              ocr_only_tokens_checked=len(lk), ocr_only_tokens_found=len(found),
              failing_rows=[r['id'] for r in rows if not (r['present'] and r['mutant_rejected'] and r['wrong_id_rejected'])])
    P['qa'] = qa
    P['output']['sha256'] = sha_file(out); P['output']['bytes'] = len(open(out, 'rb').read())
    allok = allok and not qa['failing_rows'] and qa['ocr_only_tokens_found'] == 0 and len(lk) > 0
    print('QA', P['pid'], json.dumps(qa, ensure_ascii=False))
man['qa_instrument'] = 'pdftotext -raw (poppler) sobre cada PDF final; cada renglón buscado como «ID + texto» con espacios normalizados; mutantes de un carácter e IDs cruzados deben faltar; tokens exclusivos del OCR deben faltar'
json.dump(man, open('manifest4.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('ALL_OK', allok)
if not allok: raise SystemExit('QA_FAILED')
