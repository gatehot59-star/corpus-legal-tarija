# check_cuts.py
# Verifica que cada corte de franja de las planillas A a D caiga en un espacio en blanco
# entre cajas de diseno de la corrida GPU del 16-oct. Lee solo cajas y etiquetas: no lee
# ni imprime el texto OCR (block_content).
import json, hashlib, os, sys

RAW_DIR = '/workspace/paddle-vl16-gpu-20261016/snapshot-v4-final/corpus-vl16-results'
OUT = '/workspace/ocr-gold-humano-4p-20261102/check-cuts-output.json'
PAD = 20
PAGES = [
    ('A', 'h01-p002', '9593676353e2fcd680c20dba37c519dd5c826184806411467796aced00b39f9a', 2526, 3915,
     [0, 630, 942, 1289, 1576, 1895, 2343, 2533, 2790, 3018, 3594, 3915]),
    ('B', 'h02-p001', 'fb0d6be4ca4e1b5dadfc12a9f1ee72ee19eb8a0cd34ed305247f1e703fdf717f', 2523, 3915,
     [0, 1014, 1430, 1832, 2341, 3430, 3664, 3915]),
    ('C', 'h02-p002', '94b8fffe9684dfc25de86c82c87883cb632e7d98ced8decde5e079eb52ab84d0', 2523, 3918,
     [0, 626, 869, 1904, 2296, 3439, 3667, 3918]),
    ('D', 'h02-p003', '8ddb030f98a1c91dc97632dd4754f2f1e9f72b564aeaac27e006bb1f8bf3cfa2', 2523, 3918,
     [0, 625, 803, 1251, 1574, 1898, 2409, 2600, 2856, 3050, 3599, 3918]),
]


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def crossing(boxes, c):
    return sum(1 for b in boxes if b[1] < c < b[3])


def cut_rows(boxes, cuts, H):
    rows = []
    for c in cuts[1:-1]:
        above = [b[3] for b in boxes if b[3] <= c]
        below = [b[1] for b in boxes if b[1] >= c]
        a = max(above) if above else 0
        z = min(below) if below else H
        mid = (a + z) / 2
        rows.append(dict(cut=c, crossing_parsing_boxes=crossing(boxes, c), gap=[a, z], gap_px=z - a,
                         midpoint=mid, offset_from_midpoint=c - mid,
                         padded_crops_touch_a_box=(c - PAD < a) or (c + PAD > z)))
    return rows


report = dict(instrument='check_cuts.py', script_sha256=sha256(open(os.path.abspath(__file__), 'rb').read()),
              raw_dir=RAW_DIR, pad_px=PAD, pages=[])
ok = True
for prefix, pid, exp_sha, W, H, cuts in PAGES:
    raw = open(os.path.join(RAW_DIR, pid + '-raw.json'), 'rb').read()
    res = json.loads(raw.decode('utf-8'))['res']
    p_boxes = [tuple(float(v) for v in blk['block_bbox']) for blk in res['parsing_res_list']]
    l_boxes = [tuple(float(v) for v in bx['coordinate']) for bx in res['layout_det_res']['boxes']]
    labels = [blk['block_label'] for blk in res['parsing_res_list']]
    rows = cut_rows(p_boxes, cuts, H)
    for r in rows:
        r['crossing_layout_boxes'] = crossing(l_boxes, r['cut'])
    per_band = [sum(1 for b in p_boxes if cuts[k] <= (b[1] + b[3]) / 2 < cuts[k + 1]) for k in range(len(cuts) - 1)]
    tallest = max(p_boxes, key=lambda b: b[3] - b[1])
    neg_cut = (tallest[1] + tallest[3]) / 2
    neg = crossing(p_boxes, neg_cut)
    max_off = max(abs(r['offset_from_midpoint']) for r in rows)
    page_ok = (sha256(raw) == exp_sha and res['width'] == W and res['height'] == H
               and all(r['crossing_parsing_boxes'] == 0 and r['crossing_layout_boxes'] == 0 for r in rows)
               and all(n > 0 for n in per_band) and neg >= 1)
    ok = ok and page_ok
    report['pages'].append(dict(sheet=prefix, pid=pid, raw_sha256=sha256(raw), raw_sha256_expected=exp_sha,
                                size=[res['width'], res['height']], size_expected=[W, H],
                                parsing_boxes=len(p_boxes), layout_boxes=len(l_boxes),
                                labels=sorted(set(labels)), boxes_per_band=per_band, cuts=rows,
                                negative_control=dict(cut=neg_cut, crossing_parsing_boxes=neg),
                                max_abs_offset_from_midpoint=max_off, midpoint_claim_ok=max_off <= 0.5,
                                min_gap_px=min(r['gap_px'] for r in rows), page_ok=page_ok))
report['all_ok'] = ok
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
    f.write('\n')
print('CUTS_OK', ok)
sys.exit(0 if ok else 1)
