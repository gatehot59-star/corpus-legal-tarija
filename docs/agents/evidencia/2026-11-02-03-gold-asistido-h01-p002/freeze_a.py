# freeze_a.py
# Congela la pagina A (h01-p002, Ley 524 p. 2) como gold asistido: referencia IA
# con la correccion de A16 confirmada por Abraham. No lee ninguna salida OCR.
import json, hashlib, os

REF = '/workspace/ocr-heldout-20261015/gold-ai-v1.json'
REF_SHA = '36097a8dcb63e601cf3a3108d63fb9178a3d57067019c5b9c9e4d4c3331806d7'
OUT = '/workspace/ocr-gold-humano-4p-20261102/gold-asistido-v1-h01-p002.json'
PID = 'h01-p002'
LINE_INDEX = 25
BEFORE, AFTER = 'veintis\u00e9is', 'veintiseis'
IDS = ['A%02d' % (n + 1) for n in range(25)]


def sha256(b):
    return hashlib.sha256(b).hexdigest()


raw = open(REF, 'rb').read()
if sha256(raw) != REF_SHA:
    raise SystemExit('reference hash mismatch')
ref = json.loads(raw.decode('utf-8'))
text = ref['pages'][PID]['text']
lines = text.split('\n')
nonempty = [i for i, l in enumerate(lines) if l.strip()]
if len(nonempty) != 25 or nonempty[15] != LINE_INDEX:
    raise SystemExit('line map mismatch')
if lines[LINE_INDEX].count(BEFORE) != 1 or text.count(BEFORE) != 1:
    raise SystemExit('correction anchor not unique')
new = list(lines)
new[LINE_INDEX] = lines[LINE_INDEX].replace(BEFORE, AFTER)
new_text = '\n'.join(new)
changed = [k for k, (x, y) in enumerate(zip(text, new_text)) if x != y]
if len(new_text) != len(text) or len(changed) != 1:
    raise SystemExit('expected exactly one changed character')
k = changed[0]
gold = dict(
    schema='corpus-gold-asistido-v1', page_id=PID, sheet='A',
    document='Ley Departamental N\u00b0 524', page=2, status='congelado',
    review=dict(
        level='asistida', human_review='parcial',
        ai_visual_pass=dict(by='BRAIN', lines_checked=25, lines_matching=24, blind=False,
                            receipt='docs/agents/respuestas/2026-11-02-02-planilla-a-pase-ia-24-de-25-error-de-referencia-en-a16.md',
                            commit='86bdce93896fb22838e558a81c07a93bda6dd070'),
        human_confirmation=dict(reviewer='Jorge Abraham Mendieta', scope=['A16'], reply='esta sin tilde',
                                received_at='2026-11-02T11:29-03:00',
                                evidence_seen='recorte ampliado de A16 del escaneo oficial, mostrado en el chat y en el Doc espejo'),
        lines_without_human_review=[x for x in IDS if x != 'A16']),
    source=dict(reference='benchmarks/ocr-heldout-20261015/gold-ai-v1.json',
                reference_commit='05ecc45c4beca50cd28ca45f2d4bfc371b0c6049', reference_sha256=REF_SHA,
                reference_text_sha256=sha256(text.encode('utf-8')),
                sheet_manifest='docs/agents/evidencia/2026-11-02-01-planillas-revision-4-paginas/manifest4.json',
                sheet_commit='2d095c3b4b95ab656d0fa768ac9100d6b1ad6734'),
    scan=dict(pdf_sha256='29085b9662453ccd51daea02c10bde124b8e0c91adc712d9d6f3f88c8c92b946', page=2,
              pixel_sha256_rgb='b621ebffffe3f280b33fe029f3f67b924b98f2ead0563f3e995640d49c320a24'),
    corrections=[dict(line_id='A16', line_index=LINE_INDEX, before=BEFORE, after=AFTER, char_offset=k,
                      char_before=text[k], char_after=new_text[k],
                      reason='el impreso no tiene tilde; convencion: respetar lo impreso aunque tenga errores propios')],
    text_chars=len(new_text), text_sha256=sha256(new_text.encode('utf-8')), text=new_text)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(gold, f, ensure_ascii=False, indent=1)
    f.write('\n')
print('FROZEN', PID, 'chars', len(new_text), 'changed_offset', k, repr(text[k]), '->', repr(new_text[k]))
print('TEXT_SHA256', gold['text_sha256'])
print('REF_TEXT_SHA256', gold['source']['reference_text_sha256'])
