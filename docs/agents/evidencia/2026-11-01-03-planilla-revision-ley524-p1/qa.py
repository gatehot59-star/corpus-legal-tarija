import subprocess, json, re, hashlib
def ws(s): return re.sub(r'\s+', ' ', s).strip()
def sha_file(p):
    with open(p, 'rb') as f: return hashlib.sha256(f.read()).hexdigest()
OUT = 'revision-humana-ley-524-p1.pdf'
man = json.load(open('manifest.json', encoding='utf-8'))
info = subprocess.run(['pdfinfo', OUT], capture_output=True, text=True, check=True).stdout
pages = int(re.search(r'Pages:\s+(\d+)', info).group(1))
t = subprocess.run(['pdftotext', '-enc', 'UTF-8', OUT, '-'], capture_output=True, text=True, check=True).stdout
T = ws(t)
def mutate(s):
    for k, ch in enumerate(s):
        if ch.isdigit(): return s[:k] + str((int(ch) + 1) % 10) + s[k + 1:]
    k = len(s) // 2
    while not s[k].isalpha(): k += 1
    return s[:k] + (s[k].lower() if s[k].isupper() else s[k].upper()) + s[k + 1:]
rows = []
ids = [L['id'] for L in man['lines']]
for n, L in enumerate(man['lines']):
    m = mutate(L['text']); wrong_id = ids[(n + 1) % len(ids)]
    rows.append(dict(id=L['id'], present_with_id=ws(L['id'] + ' ' + L['text']) in T,
                     mutant_rejected=(m != L['text']) and (ws(L['id'] + ' ' + m) not in T),
                     wrong_id_rejected=ws(wrong_id + ' ' + L['text']) not in T))
qa = dict(instrument='pdftotext (poppler) sobre el PDF final; cada renglón buscado como «Rnn + texto» con espacios normalizados',
          pdf_pages=pages,
          lines_present_with_id=sum(r['present_with_id'] for r in rows), lines_total=len(rows),
          mutant_controls_rejected=sum(r['mutant_rejected'] for r in rows),
          wrong_id_controls_rejected=sum(r['wrong_id_rejected'] for r in rows),
          ocr_only_variant_absent=('Presupuestó' not in t),
          failing_rows=[r['id'] for r in rows if not (r['present_with_id'] and r['mutant_rejected'] and r['wrong_id_rejected'])])
man['qa'] = qa
man['output'] = dict(file=OUT, sha256=sha_file(OUT), bytes=len(open(OUT, 'rb').read()))
json.dump(man, open('manifest.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('QA', json.dumps(qa, ensure_ascii=False))
if qa['failing_rows'] or qa['lines_present_with_id'] != 24 or not qa['ocr_only_variant_absent']: raise SystemExit('QA_FAILED')
