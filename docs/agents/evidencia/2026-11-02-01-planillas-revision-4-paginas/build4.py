import json, hashlib, html, re, os, subprocess
from PIL import Image, ImageDraw, ImageFont
import matplotlib, weasyprint

def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p):
    with open(p, 'rb') as f: return sha_bytes(f.read())

EXP_REF = '36097a8dcb63e601cf3a3108d63fb9178a3d57067019c5b9c9e4d4c3331806d7'
PDFS = {'524': ('ley524.pdf', '29085b9662453ccd51daea02c10bde124b8e0c91adc712d9d6f3f88c8c92b946'),
        '523': ('ley523.pdf', 'dd85855e5e0d3134e29998776d7c3eb347d3e1ebde24ef890b37fc0c7c4d7d04')}
RAW_DIR = '/workspace/paddle-vl16-gpu-20261016/snapshot-v4-final/corpus-vl16-results'
SIG = 'La firma manuscrita sobre el nombre de la gobernadora.'
TAB = 'En las tablas, que la categoría (SUPERIOR, EJECUTIVO, OPERATIVO) figure sólo en la primera fila de su grupo: en el impreso es una celda combinada.'
PAGES = [
 dict(pid='h01-p002', law='524', page=2, prefix='A', size=(2526, 3915),
      pix='b621ebffffe3f280b33fe029f3f67b924b98f2ead0563f3e995640d49c320a24',
      raw_sha='9593676353e2fcd680c20dba37c519dd5c826184806411467796aced00b39f9a',
      name='Ley Departamental N° 524, página 2', out='revision-humana-ley-524-p2.pdf', minutes='entre 10 y 20',
      scope='Incluye todo lo impreso: encabezado, artículo, disposiciones, lista numerada, fechas, nombre y cargo bajo la firma, y pie de página.',
      skip=[SIG],
      bands=[('Encabezado', 0, 630, [0, 1, 2]), ('Artículo 7', 630, 942, [4]),
             ('Disposición transitoria primera', 942, 1289, [6]), ('Lista numerada', 1289, 1576, [8, 9, 10, 11]),
             ('Disposición transitoria segunda', 1576, 1895, [13]), ('Disposición final', 1895, 2343, [15, 17]),
             ('Sanción', 2343, 2533, [19]), ('Remisión y promulgación', 2533, 2790, [21, 23]),
             ('Fecha de promulgación', 2790, 3018, [25]), ('Nombre y cargo de la gobernadora', 3018, 3594, [27, 28, 29]),
             ('Pie de página', 3594, 3915, [31, 32, 33, 34, 35, 36])]),
 dict(pid='h02-p001', law='523', page=1, prefix='B', size=(2523, 3915),
      pix='5f811b7ac878ad8597c70a3323d79cd59a10f9102bdbec8feff7ee79986e2924',
      raw_sha='fb0d6be4ca4e1b5dadfc12a9f1ee72ee19eb8a0cd34ed305247f1e703fdf717f',
      name='Ley Departamental N° 523, página 1', out='revision-humana-ley-523-p1.pdf', minutes='entre 20 y 30',
      scope='Incluye todo lo impreso: encabezado, título, artículos, datos de financiamiento, la tabla de escala salarial y pie de página.',
      skip=[TAB],
      bands=[('Encabezado, número de ley, fecha y gobernadora', 0, 1014, [0, 1, 2, 4, 5, 7, 8]),
             ('Promulgación y título de la ley', 1014, 1430, [10, 11, 13, 14]), ('Artículo 1', 1430, 1832, [16]),
             ('Título de la tabla y datos de financiamiento', 1832, 2341, [18, 19, 20, 22, 23, 24, 25, 26]),
             ('Tabla de escala salarial', 2341, 3430, list(range(28, 48))), ('Artículo 2, comienzo', 3430, 3664, [49]),
             ('Pie de página', 3664, 3915, [51, 52, 53, 54, 55, 56])]),
 dict(pid='h02-p002', law='523', page=2, prefix='C', size=(2523, 3918),
      pix='dd6bf1526aff0547507934c603ba75582235e246c7ba3082e33ced44fa06ff83',
      raw_sha='94b8fffe9684dfc25de86c82c87883cb632e7d98ced8decde5e079eb52ab84d0',
      name='Ley Departamental N° 523, página 2', out='revision-humana-ley-523-p2.pdf', minutes='entre 20 y 30',
      scope='Incluye todo lo impreso: encabezado, continuación de artículos, dos tablas y pie de página.',
      skip=[TAB],
      bands=[('Encabezado', 0, 626, [0, 1, 2]), ('Final del Artículo 2', 626, 869, [4]),
             ('Tabla de la Asamblea Legislativa', 869, 1904, [6, 7, 8] + list(range(10, 26))),
             ('Artículo 3', 1904, 2296, [27]),
             ('Tabla del Órgano Ejecutivo', 2296, 3439, [29, 30, 31] + list(range(33, 51))),
             ('Artículo 4, comienzo', 3439, 3667, [52]), ('Pie de página', 3667, 3918, [54, 55, 56, 57, 58, 59])]),
 dict(pid='h02-p003', law='523', page=3, prefix='D', size=(2523, 3918),
      pix='e9ff4f7c1f8e3a4047722f97110d7389d2291118672c64e95390ab58a913d6c6',
      raw_sha='8ddb030f98a1c91dc97632dd4754f2f1e9f72b564aeaac27e006bb1f8bf3cfa2',
      name='Ley Departamental N° 523, página 3', out='revision-humana-ley-523-p3.pdf', minutes='entre 10 y 20',
      scope='Incluye todo lo impreso: encabezado, disposiciones, fechas, nombre y cargo bajo la firma, y pie de página.',
      skip=[SIG],
      bands=[('Encabezado', 0, 625, [0, 1, 2]), ('Final del Artículo 4', 625, 803, [4]),
             ('Disposición transitoria primera', 803, 1251, [6, 8]), ('Disposición transitoria segunda', 1251, 1574, [10]),
             ('Disposición transitoria tercera', 1574, 1898, [12]), ('Disposición abrogatoria', 1898, 2409, [14, 16]),
             ('Sanción', 2409, 2600, [18]), ('Remisión y promulgación', 2600, 2856, [20, 22]),
             ('Fecha de promulgación', 2856, 3050, [24]), ('Nombre y cargo de la gobernadora', 3050, 3599, [26, 27, 28]),
             ('Pie de página', 3599, 3918, [30, 31, 32, 33, 34, 35])]),
]
PAD = 20
CONVENTIONS = ['Se respeta lo impreso tal cual, incluso erratas propias de la ley; no se corrige ortografía ni aritmética.',
               'Incluye todo texto impreso, encabezado y pie; excluye escudo, firmas y trazos manuscritos.',
               'Cuentan letras, tildes, mayúsculas, dígitos, signos de puntuación, palabras faltantes o sobrantes y espacios entre palabras; en las tablas, además, que cada valor esté en su columna.',
               'No cuentan el corte de renglón dentro de un párrafo, la cantidad de espacios seguidos ni variantes tipográficas: comillas rectas o curvas, largo del guion, ° frente a º; se conservan en la forma ya usada por la referencia.',
               'En las tablas, la categoría de una celda combinada va sólo en la primera fila de su grupo, como en la referencia.']

ref_sha = sha_file('ref.json')
if ref_sha != EXP_REF: raise SystemExit('reference hash mismatch ' + ref_sha)
ref = json.load(open('ref.json', encoding='utf-8'))
if ref.get('human_review') is not False: raise SystemExit('unexpected human_review flag')
pdf_info = {}
for law, (fn, exp) in PDFS.items():
    h = sha_file(fn)
    if h != exp: raise SystemExit('PDF hash mismatch %s %s' % (law, h))
    n = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', fn], capture_output=True, text=True, check=True).stdout).group(1))
    pdf_info[law] = dict(sha256=h, pages=n)

fontdir = os.path.join(matplotlib.get_data_path(), 'fonts', 'ttf')
FR = os.path.join(fontdir, 'DejaVuSans.ttf'); FB = os.path.join(fontdir, 'DejaVuSans-Bold.ttf')
build_sha = sha_file(os.path.abspath(__file__))

def esc(s): return html.escape(s, quote=True)
NUM = re.compile(r'\d[\d.,/]*\d|\d')
def fmt(s):
    out = []; pos = 0
    for m in NUM.finditer(s):
        out.append(esc(s[pos:m.start()])); out.append('<span class="n">' + esc(m.group()) + '</span>'); pos = m.end()
    out.append(esc(s[pos:])); return ''.join(out)

CSS = """
@font-face { font-family: 'DV'; src: url('file://FR_PATH'); font-weight: normal; }
@font-face { font-family: 'DV'; src: url('file://FB_PATH'); font-weight: bold; }
@page { size: A4; margin: 11mm 10mm 13mm 10mm;
  @bottom-center { content: "FOOTER_TEXT · hoja " counter(page) " de " counter(pages);
                   font-family: 'DV'; font-size: 7.5pt; color: #666; } }
html { font-family: 'DV'; font-size: 11pt; color: #111; font-variant-ligatures: none; hyphens: manual; }
h1 { font-size: 18pt; margin: 0 0 2mm; }
.sub { color: #555; margin: 0 0 4mm; }
h2 { font-size: 13pt; margin: 3.6mm 0 1.6mm; }
p { margin: 0 0 2mm; line-height: 1.38; }
ol, ul { margin: 0 0 2mm 6mm; padding: 0; }
li { margin: 0 0 1.6mm; line-height: 1.38; }
.box { border: 0.4mm solid #222; padding: 3mm 4mm; margin: 2mm 0 3mm; }
.seg { break-inside: avoid; margin: 0 0 7mm; }
.seg.tall { break-inside: auto; }
.seg h3 { font-size: 12.5pt; margin: 0 0 1.5mm; break-after: avoid; }
.seg img { width: 100%; border: 0.3mm solid #888; display: block; break-inside: avoid; }
table.r { width: 100%; border-collapse: collapse; margin-top: 2mm; }
table.r tr { break-inside: avoid; }
table.r td { vertical-align: top; padding: 1.4mm 1.6mm; border-bottom: 0.25mm solid #ccc; font-size: 13pt; line-height: 1.42; white-space: pre-wrap; }
table.r td.id { width: 12mm; font-weight: bold; font-size: 11pt; color: #333; white-space: nowrap; }
table.r.tab td { font-size: 9.5pt; line-height: 1.3; padding: 0.8mm 1.1mm; border: 0.2mm solid #bbb; }
table.r.tab td.id { font-size: 9pt; border: none; border-bottom: 0.25mm solid #ccc; }
.n { background: #ffe680; font-weight: bold; }
.ctl p { font-size: 8.5pt; line-height: 1.35; word-break: break-all; }
.pb { break-before: page; }
.ov img { height: 236mm; width: auto; display: block; margin: 0 auto; border: 0.3mm solid #888; }
""".replace('FR_PATH', FR).replace('FB_PATH', FB)

def band_table(idx, lines, rid):
    ncols = max(len(lines[i].split('\t')) for i in idx)
    rows = []
    for i in idx:
        cs = lines[i].split('\t')
        if len(cs) == 1:
            span = ' colspan="%d"' % ncols if ncols > 1 else ''
            rows.append('<tr><td class="id">%s</td><td%s>%s</td></tr>' % (rid[i], span, fmt(lines[i])))
        else:
            cs = cs + [''] * (ncols - len(cs))
            rows.append('<tr><td class="id">%s</td>%s</tr>' % (rid[i], ''.join('<td class="c">%s</td>' % fmt(c) for c in cs)))
    return '<table class="%s">%s</table>' % ('r tab' if ncols > 1 else 'r', ''.join(rows))

pages_out = []
for P in PAGES:
    pg = ref['pages'][P['pid']]
    text = pg['text']; lines = text.split('\n')
    nonempty = [i for i, l in enumerate(lines) if l.strip()]
    rid = {i: '%s%02d' % (P['prefix'], n + 1) for n, i in enumerate(nonempty)}
    if [i for b in P['bands'] for i in b[3]] != nonempty: raise SystemExit(P['pid'] + ': lines not covered once and in order')
    W, H = P['size']
    if P['bands'][0][1] != 0 or P['bands'][-1][2] != H or any(P['bands'][k][2] != P['bands'][k + 1][1] for k in range(len(P['bands']) - 1)):
        raise SystemExit(P['pid'] + ': bands do not tile the page')
    stem = P['pid']; fn = PDFS[P['law']][0]
    subprocess.run(['pdftoppm', '-f', str(P['page']), '-l', str(P['page']), '-r', '300', '-gray', '-singlefile', '-png', fn, stem], check=True)
    im = Image.open(stem + '.png')
    if im.size != (W, H): raise SystemExit('%s: unexpected render size %r' % (stem, im.size))
    pix = sha_bytes(im.convert('RGB').tobytes()); pix_same = (pix == P['pix'])
    gray = im.convert('L')
    bands = []
    for k, (title, y0, y1, idx) in enumerate(P['bands']):
        c0, c1 = max(0, y0 - PAD), min(H, y1 + PAD)
        crop = gray.crop((0, c0, W, c1)); cfn = '%s-F%d.png' % (stem, k + 1); crop.save(cfn, optimize=True)
        bands.append(dict(id='F%d' % (k + 1), title=title, cut_y=[y0, y1], crop_box=[0, c0, W, c1],
                          lines=[rid[i] for i in idx], line_index=idx, png=cfn, pixel_sha256_gray=sha_bytes(crop.tobytes())))
    ov = gray.convert('RGB'); d = ImageDraw.Draw(ov); font = ImageFont.truetype(FB, 64)
    for k, b in enumerate(bands):
        y0, y1 = b['cut_y']
        if k > 0:
            for x in range(0, W, 40): d.line([(x, y0), (x + 22, y0)], fill=(205, 30, 30), width=5)
        d.text((W - 175, (y0 + y1) // 2 - 36), b['id'], fill=(205, 30, 30), font=font)
    ovf = stem + '-overview.jpg'; ov.save(ovf, quality=90, optimize=True)
    pre = P['prefix']; first, last = rid[nonempty[0]], rid[nonempty[-1]]; nb = len(bands)
    has_tab = any('\t' in lines[i] for i in nonempty)
    reply = ('<p>Si está todo bien: <b>«%s: sin cambios»</b>. Si no, una línea por corrección:</p>'
             '<p style="margin-left:6mm"><b>%s05:</b> dice «…», debe decir «…»</p>'
             '<p>Si algo es más fácil de señalar con una captura, mandala con el número de franja.</p>') % (pre, pre)
    css = CSS.replace('FOOTER_TEXT', esc(P['name']) + ' · planilla ' + pre + ' de revisión humana')
    parts = ['<!doctype html><html lang="es"><head><meta charset="utf-8"><title>%s · planilla %s de revisión humana</title><style>' % (esc(P['name']), pre), css, '</style></head><body>']
    parts.append('<h1>Revisión humana · %s</h1>' % esc(P['name']))
    parts.append('<p class="sub" style="margin-bottom:1.5mm">Planilla %s para validar la referencia contra el escaneo oficial · 2 de noviembre de 2026</p>' % pre)
    parts.append('<p style="margin-bottom:3mm"><b>Tiempo estimado:</b> %s minutos.</p>' % P['minutes'])
    steps = ['En cada franja, de <b>F1</b> a <b>F%d</b>, mirá el escaneo y leé debajo los renglones de la referencia, de <b>%s</b> a <b>%s</b>.' % (nb, first, last),
             'Marcá todo lo que no coincida con lo impreso: letras, tildes, mayúsculas, números, puntos y comas, palabras que falten o sobren, y espacios entre palabras.']
    if has_tab: steps.append('En las tablas, cada renglón de la referencia es una fila de la grilla: revisá cada valor y que esté en su columna.')
    steps += ['Respetá lo impreso tal cual, aunque la ley tenga errores propios: no corrijas ortografía ni cuentas.',
              'Al final, mirá la página completa por si hay texto impreso que no figura en ningún renglón.']
    parts.append('<div class="box"><h2 style="margin-top:0">Qué tenés que hacer</h2><ol>' + ''.join('<li>%s</li>' % s for s in steps) + '</ol></div>')
    parts.append('<h2>Qué incluye la referencia</h2><p>%s</p>' % esc(P['scope']))
    parts.append('<h2>Cómo me respondés</h2>' + reply)
    parts.append('<h2>Lo que más importa</h2><p>Montos, número de ley, números de artículo, fechas y nombres propios. Los números están <span class="n">resaltados</span> para que no se te pasen.</p>')
    skip = ['El escudo y cualquier marca hecha a mano.'] + P['skip'] + [
            'Dónde se corta cada renglón dentro de un párrafo: en la referencia cada párrafo va en un solo renglón.',
            'La cantidad de espacios seguidos, si las comillas son rectas o curvas, el largo de un guion, o si el signo de «N°» es ° u º.']
    parts.append('<h2>No hace falta revisar</h2><ul>' + ''.join('<li>%s</li>' % esc(s) for s in skip) + '</ul>')
    parts.append('<h2>Por qué no ves ningún OCR</h2><p>Para que tu revisión sirva como referencia humana independiente, esta planilla no muestra la salida de ningún OCR. Una corrida anterior se usó solo para ubicar: dónde cortar las franjas en los espacios en blanco y en qué franja va cada renglón. Su texto no aparece acá.</p>')
    parts.append('<div class="pb ov"><h2 style="margin-top:0">Página completa</h2><p>Las franjas F1 a F%d cubren toda la hoja, de arriba abajo, sin huecos. Ampliá con los dedos para ver detalle.</p><img src="%s"></div>' % (nb, ovf))
    parts.append('<div class="pb"></div>')
    for b in bands:
        ids = b['lines']; rng = ids[0] if len(ids) == 1 else ids[0] + ' a ' + ids[-1]
        tall = (b['crop_box'][3] - b['crop_box'][1]) > 1000 or len(ids) > 12
        parts.append('<div class="seg%s"><h3>%s · %s · %s</h3><img src="%s">%s</div>' % (' tall' if tall else '', b['id'], esc(b['title']), rng, b['png'], band_table(b['line_index'], lines, rid)))
    ranges = ' · '.join('%s: %d a %d' % (b['id'], b['cut_y'][0], b['cut_y'][1]) for b in bands)
    tsha = sha_bytes(text.encode('utf-8'))
    parts.append('<div class="pb"><h2 style="margin-top:0">Cómo me respondés</h2>' + reply + '<h2>Datos de control</h2><div class="ctl">'
                 '<p>Referencia: gold-ai-v1.json, SHA-256 %s; página %s; %d caracteres; texto SHA-256 %s; %d renglones, %d con texto; revisión humana previa: no.</p>' % (ref_sha, P['pid'], len(text), tsha, len(lines), len(nonempty)) +
                 '<p>Escaneo: PDF oficial de la Ley %s (%d páginas), SHA-256 %s; página %d renderizada con pdftoppm a 300 dpi en grises; %d × %d píxeles; píxeles idénticos a la imagen del banco: %s.</p>' % (P['law'], pdf_info[P['law']]['pages'], pdf_info[P['law']]['sha256'], P['page'], W, H, 'sí' if pix_same else 'no') +
                 '<p>Cortes: punto medio del espacio en blanco entre bloques, según las cajas de diseño de la corrida GPU del 16-oct (%s-raw.json, SHA-256 %s); cada franja suma %d píxeles de margen arriba y abajo. Ningún texto de OCR se muestra.</p>' % (P['pid'], P['raw_sha'], PAD) +
                 '<p>Franjas en píxeles verticales: %s.</p>' % ranges +
                 '<p>Generador: build4.py, SHA-256 %s.</p></div></div>' % build_sha)
    parts.append('</body></html>')
    weasyprint.HTML(string=''.join(parts), base_url=os.getcwd()).write_pdf(P['out'])
    pages_out.append(dict(pid=P['pid'], law=P['law'], page=P['page'], prefix=pre, name=P['name'],
                          reference=dict(text_chars=len(text), text_sha256=tsha, lines_total=len(lines), lines_nonempty=len(nonempty)),
                          lines=[[rid[i], i] for i in nonempty],
                          scan=dict(pdf_sha256=pdf_info[P['law']]['sha256'], pdf_pages=pdf_info[P['law']]['pages'],
                                    render='pdftoppm -f %d -l %d -r 300 -gray -singlefile -png' % (P['page'], P['page']),
                                    size=[W, H], pixel_sha256_rgb=pix, pixel_identical_to_benchmark_image=pix_same),
                          band_cut_source=dict(file=P['pid'] + '-raw.json', sha256=P['raw_sha']),
                          bands=[{k: v for k, v in b.items() if k != 'png'} for b in bands],
                          output=dict(file=P['out'])))
    print('BUILD_OK', P['pid'], P['out'], 'pixel_identical', pix_same, 'bands', nb, 'lines', len(nonempty))

manifest = dict(schema='corpus-human-review-sheet-v2', status='pendiente de revisión humana',
    purpose='Revisión humana de la referencia IA de las otras cuatro páginas del banco held-out (Ley 524 p. 2 y Ley 523 pp. 1 a 3) para congelar gold humano',
    reference=dict(file='benchmarks/ocr-heldout-20261015/gold-ai-v1.json', git_commit='05ecc45c4beca50cd28ca45f2d4bfc371b0c6049', file_sha256=ref_sha, human_review=False),
    band_cut_source=dict(dir=RAW_DIR, use='cajas de diseño y texto de la corrida GPU del 16-oct, sólo para cortar franjas en espacios en blanco y asignar cada renglón a su franja; ningún texto OCR se muestra'),
    display=dict(ocr_text_shown=False, numbers_highlighted_regex=NUM.pattern,
                 tables='cada renglón con tabulaciones se muestra como una fila de grilla, una celda por campo; espacios visibles tal como están en la referencia'),
    review_conventions=CONVENTIONS,
    contamination='En este chat no se le mostró al revisor ninguna diferencia del OCR en estas cuatro páginas. Existe un informe del 16-oct sobre la corrida GPU de las cinco páginas que pudo haber leído; las planillas no lo muestran.',
    reply_and_application='Respuesta por planilla: «X: sin cambios» o «Xnn: dice ..., debe decir ...». Cada corrección se aplica a su renglón; cada página se congela como gold humano con human_review=true, revisor y fecha.',
    generator=dict(file='build4.py', sha256=build_sha), pages=pages_out)
json.dump(manifest, open('manifest4.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
