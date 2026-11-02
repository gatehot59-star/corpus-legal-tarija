import json, subprocess, hashlib, re, html, os, io
import matplotlib, weasyprint
os.chdir('/home/user/work/rev4')
src = io.open('build4.py', encoding='utf-8').read()
css = re.search(r'CSS = """(.*?)"""', src, re.S).group(1)
fd = os.path.join(matplotlib.get_data_path(), 'fonts', 'ttf')
css = css.replace('FR_PATH', os.path.join(fd, 'DejaVuSans.ttf')).replace('FB_PATH', os.path.join(fd, 'DejaVuSans-Bold.ttf')).replace('FOOTER_TEXT', 'control positivo')
NUM = re.compile(r'\d[\d.,/]*\d|\d')
def fmt(s):
    out = []; pos = 0
    for m in NUM.finditer(s):
        out.append(html.escape(s[pos:m.start()])); out.append('<span class="n">' + html.escape(m.group()) + '</span>'); pos = m.end()
    out.append(html.escape(s[pos:])); return ''.join(out)
lk = json.load(io.open('leak-tokens.json', encoding='utf-8'))
toks = [t for v in lk.values() for t in v]
def check(body, tag):
    fn = '/home/user/work/leak-positive-%s.pdf' % tag
    weasyprint.HTML(string='<html><head><meta charset="utf-8"><style>' + css + '</style></head><body>' + body + '</body></html>').write_pdf(fn)
    t = subprocess.run(['pdftotext', '-raw', '-enc', 'UTF-8', fn, '-'], capture_output=True, text=True, check=True).stdout
    T = re.sub(r'\s+', ' ', t).strip()
    found = [x for x in toks if x in t or x in T]
    print('LEAK_POSITIVE_CONTROL', tag, 'found', len(found), 'of', len(toks))
check(''.join('<p>Texto de prueba %s y sigue.</p>' % fmt(x) for x in toks), 'parrafo')
check('<table class="r">' + ''.join('<tr><td class="id">X%02d</td><td>Antes %s despues</td></tr>' % (k + 1, fmt(x)) for k, x in enumerate(toks)) + '</table>', 'renglon')
check('<table class="r tab">' + ''.join('<tr><td class="id">Y%02d</td><td class="c">uno</td><td class="c">%s</td><td class="c">3.300</td></tr>' % (k + 1, fmt(x)) for k, x in enumerate(toks)) + '</table>', 'tabla')
