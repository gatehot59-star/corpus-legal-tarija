import json, hashlib, re, sys, difflib, collections
# Uso: python3 measure.py <gold-humano.json> <terminal-selected-capture.json>
# Mide la salida CPU (ubicada por su SHA-256 dentro de la captura) contra el gold humano de h01-p001.
EXP_CPU = 'fc072bac865c7951fb687e77a9340696e7c0c2a3575705c79f6534e57b4e0451'
NUM = re.compile(r'\d[\d.,/]*\d|\d')
def sha_s(s): return hashlib.sha256(s.encode('utf-8')).hexdigest()
def ws(s): return re.sub(r'\s+', ' ', s).strip()
def find_text(o, exp):
    if isinstance(o, dict):
        for v in o.values():
            r = find_text(v, exp)
            if r is not None: return r
    elif isinstance(o, list):
        for v in o:
            r = find_text(v, exp)
            if r is not None: return r
    elif isinstance(o, str):
        if sha_s(o) == exp: return o
        if o.lstrip()[:1] in ('{', '['):
            try: return find_text(json.loads(o), exp)
            except ValueError: return None
    return None
def lev(a, b):
    if len(a) < len(b): a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            x = prev[j] + 1; y = cur[j - 1] + 1; z = prev[j - 1] + (ca != cb)
            cur[j] = x if x < y and x < z else (y if y < z else z)
        prev = cur
    return prev[-1]
def measure(gold, hyp):
    g, h = ws(gold), ws(hyp)
    gw, hw = g.split(' '), h.split(' ')
    e_raw, e_ws, e_w = lev(gold, hyp), lev(g, h), lev(gw, hw)
    ng, nh = collections.Counter(NUM.findall(gold)), collections.Counter(NUM.findall(hyp))
    raw_ops = [(gold[i1:i2], hyp[j1:j2]) for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, gold, hyp, autojunk=False).get_opcodes() if op != 'equal']
    diffs = [dict(op=op, gold=g[i1:i2], hyp=h[j1:j2], context=g[max(0, i1 - 30):i2 + 30])
             for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, g, h, autojunk=False).get_opcodes() if op != 'equal']
    return dict(chars_gold=len(gold), chars_hyp=len(hyp), char_edits_raw=e_raw, cer_raw_pct=round(100 * e_raw / len(gold), 4),
                chars_gold_ws=len(g), char_edits_ws=e_ws, cer_ws_pct=round(100 * e_ws / len(g), 4),
                words_gold=len(gw), word_edits=e_w, wer_pct=round(100 * e_w / len(gw), 4),
                numbers_gold=sum(ng.values()), numbers_matched=sum((ng & nh).values()),
                numbers_missing=dict(ng - nh), numbers_extra=dict(nh - ng),
                raw_diff_spans=len(raw_ops), raw_diff_spans_whitespace_only=sum(1 for a, b in raw_ops if not a.strip() and not b.strip()),
                diffs_ws=diffs)
gold_doc = json.load(open(sys.argv[1], encoding='utf-8'))
if gold_doc.get('human_review') is not True: raise SystemExit('gold is not human-reviewed')
page = gold_doc['pages']['h01-p001']; gold = page['text']
if sha_s(gold) != page['text_sha256']: raise SystemExit('gold text hash mismatch')
cpu = find_text(json.load(open(sys.argv[2], encoding='utf-8')), EXP_CPU)
if cpu is None: raise SystemExit('CPU text not found by hash')
res = dict(subject='salida CPU del job 4eb6c147c31d45b3b57c8a95669e8ac5, texto SHA-256 ' + EXP_CPU,
           reference='gold humano de h01-p001, texto SHA-256 ' + page['text_sha256'],
           cpu_vs_gold=measure(gold, cpu))
same = measure(gold, gold)
res['control_gold_vs_itself'] = dict(char_edits_raw=same['char_edits_raw'], char_edits_ws=same['char_edits_ws'], word_edits=same['word_edits'], numbers_matched=same['numbers_matched'])
mut = cpu.replace('595.477.378', '595.477.379', 1)
if mut == cpu: raise SystemExit('mutation target not found')
m = measure(gold, mut)
res['control_one_digit_mutation'] = dict(char_edits_ws=m['char_edits_ws'], numbers_missing=m['numbers_missing'], numbers_extra=m['numbers_extra'])
print(json.dumps(res, ensure_ascii=False, indent=1))
