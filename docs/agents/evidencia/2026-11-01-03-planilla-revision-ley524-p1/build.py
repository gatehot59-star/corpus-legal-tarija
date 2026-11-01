import json, hashlib, html, re, os
from PIL import Image, ImageDraw, ImageFont
import matplotlib, weasyprint

def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p):
    with open(p, 'rb') as f: return sha_bytes(f.read())

EXP_PDF = '29085b9662453ccd51daea02c10bde124b8e0c91adc712d9d6f3f88c8c92b946'
EXP_REF = '36097a8dcb63e601cf3a3108d63fb9178a3d57067019c5b9c9e4d4c3331806d7'
EXP_IMG = '669c89a75a4e3ad2ecc567f03a13e50c2552265b3baf4e4f547e362acbb9c3c4'
EXP_PIX = '7e71fb47a5464b0ad49ecd5d6f6f2b867e36492b8524b2a37887216e00d5a870'
RAW_SHA = 'f6c2890de753ecf6ebc882032e1b5f2e2287e93edd17ca39ed228d297552f3f0'
OUT = 'revision-humana-ley-524-p1.pdf'

pdf_sha = sha_file('ley524.pdf'); ref_sha = sha_file('ref.json')
if pdf_sha != EXP_PDF: raise SystemExit('PDF hash mismatch ' + pdf_sha)
if ref_sha != EXP_REF: raise SystemExit('reference hash mismatch ' + ref_sha)
ref = json.load(open('ref.json', encoding='utf-8'))
if ref.get('human_review') is not False: raise SystemExit('unexpected human_review flag')
page = ref['pages']['h01-p001']
if page.get('image_sha256') != EXP_IMG: raise SystemExit('page image id mismatch')
text = page['text']
if len(text) != 2854: raise SystemExit('unexpected reference length %d' % len(text))
text_sha = sha_bytes(text.encode('utf-8'))
lines = text.split('\n')
nonempty = [i for i, l in enumerate(lines) if l.strip()]
if len(lines) != 35 or len(nonempty) != 24: raise SystemExit('unexpected line structure')
rid = {i: 'R%02d' % (n + 1) for n, i in enumerate(nonempty)}

im = Image.open('p1.png'); W, H = im.size
if (W, H) != (2520, 3888): raise SystemExit('unexpected render size %r' % ((W, H),))
pix = sha_bytes(im.convert('RGB').tobytes()); pix_same = (pix == EXP_PIX)
gray = im.convert('L')

# Layout boxes of the CPU OCR raw (raw-0001.json): used ONLY to place cuts in white space.
B = [[1067,134,1412,204],[998,230,1495,459],[1055,470,1438,603],[901,648,1617,770],[656,842,1861,964],
     [271,1026,2246,1220],[277,1283,2242,1469],[276,1537,2254,1725],[275,1792,2255,2043],[275,2108,2256,2423],
     [277,2488,2256,2677],[278,2743,2257,3185],[280,3248,2261,3435],[360,3718,626,3806],[1109,3715,1417,3803],
     [1717,3707,2321,3799]]
G = [('F1', 'Encabezado, número de ley, fecha y gobernadora', [0,1,2,3,4], [0,1,2,4,5,7,8]),
     ('F2', 'Promulgación y título de la ley', [5,6], [10,11,13,14,15]),
     ('F3', 'Artículo 1', [7], [17]), ('F4', 'Artículo 2', [8], [19]), ('F5', 'Artículo 3', [9], [21]),
     ('F6', 'Artículo 4', [10], [23]), ('F7', 'Artículo 5', [11], [25]), ('F8', 'Artículo 6', [12], [27]),
     ('F9', 'Pie de página', [13,14,15], [29,30,31,32,33,34])]
if [i for g in G for i in g[3]] != nonempty: raise SystemExit('lines not covered once and in order')
if [b for g in G for b in g[2]] != list(range(len(B))): raise SystemExit('blocks not covered once and in order')
cuts = [0]
for k in range(len(G) - 1):
    lo = max(B[b][3] for b in G[k][2]); hi = min(B[b][1] for b in G[k + 1][2])
    if hi <= lo: raise SystemExit('bands overlap at ' + G[k][0])
    cuts.append((lo + hi) // 2)
cuts.append(H)
if any(cuts[i] >= cuts[i + 1] for i in range(len(cuts) - 1)): raise SystemExit('non-increasing cuts')
PAD = 20
bands = []
for k, g in enumerate(G):
    y0, y1 = cuts[k], cuts[k + 1]; c0, c1 = max(0, y0 - PAD), min(H, y1 + PAD)
    crop = gray.crop((0, c0, W, c1)); crop.save(g[0] + '.png', optimize=True)
    bands.append(dict(id=g[0], title=g[1], cut_y=[y0, y1], crop_box=[0, c0, W, c1], layout_blocks=g[2],
                      lines=[rid[i] for i in g[3]], line_index=g[3], pixel_sha256_gray=sha_bytes(crop.tobytes())))

fontdir = os.path.join(matplotlib.get_data_path(), 'fonts', 'ttf')
FR = os.path.join(fontdir, 'DejaVuSans.ttf'); FB = os.path.join(fontdir, 'DejaVuSans-Bold.ttf')
ov = gray.convert('RGB'); d = ImageDraw.Draw(ov); font = ImageFont.truetype(FB, 64)
for k, b in enumerate(bands):
    y0, y1 = b['cut_y']
    if k > 0:
        for x in range(0, W, 40): d.line([(x, y0), (x + 22, y0)], fill=(205, 30, 30), width=5)
    d.text((W - 150, (y0 + y1) // 2 - 36), b['id'], fill=(205, 30, 30), font=font)
ov.save('overview.jpg', quality=90, optimize=True)

def esc(s): return html.escape(s, quote=True)
NUM = re.compile(r'\d[\d.,/]*\d|\d')
def fmt(s):
    out = []; pos = 0
    for m in NUM.finditer(s):
        out.append(esc(s[pos:m.start()])); out.append('<span class="n">' + esc(m.group()) + '</span>'); pos = m.end()
    out.append(esc(s[pos:])); return ''.join(out)

css = """
@font-face { font-family: 'DV'; src: url('file://FR_PATH'); font-weight: normal; }
@font-face { font-family: 'DV'; src: url('file://FB_PATH'); font-weight: bold; }
@page { size: A4; margin: 11mm 10mm 13mm 10mm;
  @bottom-center { content: "Ley 524, página 1 · planilla de revisión humana · hoja " counter(page) " de " counter(pages);
                   font-family: 'DV'; font-size: 7.5pt; color: #666; } }
html { font-family: 'DV'; font-size: 11pt; color: #111; font-variant-ligatures: none; hyphens: manual; }
h1 { font-size: 18pt; margin: 0 0 2mm; }
.sub { color: #555; margin: 0 0 4mm; }
h2 { font-size: 13pt; margin: 5mm 0 2mm; }
p { margin: 0 0 2mm; line-height: 1.38; }
ol, ul { margin: 0 0 2mm 6mm; padding: 0; }
li { margin: 0 0 1.6mm; line-height: 1.38; }
.box { border: 0.4mm solid #222; padding: 3mm 4mm; margin: 2mm 0 3mm; }
.seg { break-inside: avoid; margin: 0 0 7mm; }
.seg h3 { font-size: 12.5pt; margin: 0 0 1.5mm; }
.seg img { width: 100%; border: 0.3mm solid #888; display: block; }
table.r { width: 100%; border-collapse: collapse; margin-top: 2mm; }
table.r td { vertical-align: top; padding: 1.4mm 1.6mm; border-bottom: 0.25mm solid #ccc; font-size: 13pt; line-height: 1.42; }
table.r td.id { width: 12mm; font-weight: bold; font-size: 11pt; color: #333; white-space: nowrap; }
.n { background: #ffe680; font-weight: bold; }
.ctl p { font-size: 8.5pt; line-height: 1.35; word-break: break-all; }
.pb { break-before: page; }
.ov img { height: 236mm; width: auto; display: block; margin: 0 auto; border: 0.3mm solid #888; }
""".replace('FR_PATH', FR).replace('FB_PATH', FB)

reply = ('<p>Si está todo bien: <b>«sin cambios»</b>. Si no, una línea por corrección:</p>'
         '<p style="margin-left:6mm"><b>R17:</b> dice «…», debe decir «…»</p>'
         '<p>Si algo es más fácil de señalar con una captura, mandala con el número de franja.</p>')
parts = ['<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Ley 524 p. 1 · planilla de revisión humana</title><style>', css, '</style></head><body>']
parts.append('<h1>Revisión humana · Ley Departamental N° 524, página 1</h1>')
parts.append('<p class="sub">Planilla para validar la referencia contra el escaneo oficial · 1 de noviembre de 2026</p>')
parts.append('<div class="box"><h2 style="margin-top:0">Qué tenés que hacer</h2><ol>'
             '<li>En cada franja, de <b>F1</b> a <b>F9</b>, mirá el escaneo y leé debajo los renglones de la referencia, de <b>R01</b> a <b>R24</b>.</li>'
             '<li>Marcá todo lo que no coincida con lo impreso: letras, tildes, mayúsculas, números, puntos y comas, palabras que falten o sobren, y espacios entre palabras.</li>'
             '<li>Respetá lo impreso tal cual, aunque la ley tenga errores propios: no corrijas ortografía ni cuentas.</li>'
             '<li>Al final, mirá la página completa por si hay texto impreso que no figura en ningún renglón.</li>'
             '</ol></div>')
parts.append('<h2>Cómo me respondés</h2>' + reply)
parts.append('<h2>Lo que más importa</h2><p>Montos, número de ley, números de artículo, fechas y nombres propios. Los números están <span class="n">resaltados</span> para que no se te pasen.</p>')
parts.append('<h2>No hace falta revisar</h2><ul>'
             '<li>El escudo, las firmas y las marcas hechas a mano, como el trazo del margen izquierdo junto al Artículo 5.</li>'
             '<li>Dónde se corta cada renglón dentro de un párrafo: en la referencia cada artículo va en un solo renglón.</li>'
             '<li>Si las comillas son rectas o curvas, el largo de un guion, o si el signo de «N°» es ° u º.</li></ul>')
parts.append('<h2>Por qué no ves ningún OCR</h2><p>Para que tu revisión sirva como referencia humana independiente, esta planilla no muestra la salida de ningún OCR. De la corrida solo se usaron las posiciones de los bloques, para cortar las franjas en los espacios en blanco.</p>')
parts.append('<p><b>Tiempo estimado:</b> entre 15 y 25 minutos.</p>')
parts.append('<div class="pb ov"><h2 style="margin-top:0">Página completa</h2><p>Las franjas F1 a F9 cubren toda la hoja, de arriba abajo, sin huecos. Ampliá con los dedos para ver detalle.</p><img src="overview.jpg"></div>')
parts.append('<div class="pb"></div>')
for b in bands:
    ids = b['lines']; rng = ids[0] if len(ids) == 1 else ids[0] + ' a ' + ids[-1]
    rows = ''.join('<tr><td class="id">%s</td><td>%s</td></tr>' % (rid[i], fmt(lines[i])) for i in b['line_index'])
    parts.append('<div class="seg"><h3>%s · %s · %s</h3><img src="%s.png"><table class="r">%s</table></div>' % (b['id'], esc(b['title']), rng, b['id'], rows))
ranges = ' · '.join('%s: %d a %d' % (b['id'], b['cut_y'][0], b['cut_y'][1]) for b in bands)
build_sha = sha_file(os.path.abspath(__file__))
parts.append('<div class="pb"><h2 style="margin-top:0">Cómo me respondés</h2>' + reply + '<h2>Datos de control</h2><div class="ctl">'
             '<p>Referencia: gold-ai-v1.json, SHA-256 %s; página h01-p001; 2.854 caracteres; texto SHA-256 %s; 35 renglones, 24 con texto; revisión humana previa: no.</p>' % (ref_sha, text_sha) +
             '<p>Escaneo: PDF oficial de la Ley 524 (2 páginas), SHA-256 %s; página 1 renderizada con pdftoppm a 300 dpi en grises; 2520 × 3888 píxeles; píxeles idénticos a la imagen del banco: %s.</p>' % (pdf_sha, 'sí' if pix_same else 'no') +
             '<p>Cortes: punto medio del espacio en blanco entre bloques, según las cajas de diseño de la corrida CPU (raw-0001.json, SHA-256 %s); cada franja suma %d píxeles de margen arriba y abajo. Ningún texto de OCR se usó ni se muestra.</p>' % (RAW_SHA, PAD) +
             '<p>Franjas en píxeles verticales: %s.</p>' % ranges +
             '<p>Generador: build.py, SHA-256 %s.</p></div></div>' % build_sha)
parts.append('</body></html>')
weasyprint.HTML(string=''.join(parts), base_url=os.getcwd()).write_pdf(OUT)

manifest = dict(
    schema='corpus-human-review-sheet-v1',
    status='pendiente de revisión humana',
    purpose='Revisión humana de la referencia IA de la Ley 524, página 1 (h01-p001), para congelar un gold humano',
    reference=dict(file='benchmarks/ocr-heldout-20261015/gold-ai-v1.json', git_commit='05ecc45c4beca50cd28ca45f2d4bfc371b0c6049',
                   file_sha256=ref_sha, page_id='h01-p001', human_review=False, text_chars=len(text), text_sha256=text_sha,
                   lines_total=len(lines), lines_nonempty=len(nonempty), empty_line_index=[i for i, l in enumerate(lines) if not l.strip()]),
    lines=[dict(id=rid[i], line_index=i, text=lines[i]) for i in nonempty],
    scan=dict(source='PDF oficial Ley 524 adjunto en ClickUp (attachment:1a7e60a8-3b63-4c22-acff-e4ff06a754c1.pdf)', pdf_sha256=pdf_sha,
              render='pdftoppm -f 1 -l 1 -r 300 -gray -singlefile -png', size=[W, H], pixel_sha256_rgb=pix,
              pixel_identical_to_benchmark_image=pix_same),
    bands=bands,
    band_cut_source=dict(file='state/4eb6c147c31d45b3b57c8a95669e8ac5/raw-0001.json', sha256=RAW_SHA, pad_px=PAD,
                         use='solo cajas de diseño para ubicar cortes en espacios en blanco; ningún texto OCR usado ni mostrado'),
    overview=dict(format='JPEG calidad 90', marks='cortes y etiquetas F1 a F9 en rojo, solo para ubicarse'),
    display=dict(ocr_text_shown=False, numbers_highlighted_regex=NUM.pattern,
                 wrapping='cada renglón de la referencia se muestra entero; el ajuste visual no altera el texto'),
    review_conventions=['Se respeta lo impreso tal cual, incluso erratas propias de la ley; no se corrige ortografía ni aritmética.',
                        'Incluye todo texto impreso, encabezado y pie; excluye escudo, firmas y trazos manuscritos, como el del margen izquierdo junto al Artículo 5.',
                        'Cuentan letras, tildes, mayúsculas, dígitos, signos de puntuación, palabras faltantes o sobrantes y espacios entre palabras.',
                        'No cuentan el corte de renglón dentro de un párrafo ni variantes tipográficas: comillas rectas o curvas, largo del guion, ° frente a º; se conservan en la forma simple ya usada por la referencia.'],
    contamination='Antes de recibir la planilla, el revisor supo por el chat que la única diferencia entre la salida CPU y la referencia IA, fuera de espacios, está en el título del Artículo 6 (Presupuesto frente a Presupuestó). La planilla no muestra ningún OCR.',
    reply_and_application='Respuesta: «sin cambios» o «Rnn: dice X, debe decir Y». Cada corrección se aplica al renglón Rnn de esta tabla; el resultado se congela como gold humano de h01-p001 con human_review=true, revisor y fecha; recién entonces se mide la salida CPU (CER, WER y números).',
    generator=dict(file='build.py', sha256=build_sha))
json.dump(manifest, open('manifest.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('BUILD_OK pdf', OUT, 'pixel_identical', pix_same, 'cuts', cuts, 'build_sha', build_sha)
