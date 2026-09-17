"""B04 source fixtures: preserve provisions, not just count article labels."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('legal_html', ROOT / 'pipeline/legal_html.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
TITLE = 'Ley sintética 1'


def page(body, before='<nav>MENU_ARTICULO_999</nav>', after='<aside>RELATED_ARTICULO_888</aside>'):
    return (before + '<div id="normTxtId" class="norma"><h1>' + TITLE + '</h1>' + body + '</div>' + after).encode()


def run(raw):
    return m.extract(raw, hashlib.sha256(raw).hexdigest(), TITLE)


class ExtractionTests(unittest.TestCase):
    def test_navigation_and_related_excluded(self):
        out = run(page('<p>Artículo 1. No se deroga esta disposición.</p>'))
        self.assertIn('No se deroga', out['text'])
        self.assertNotIn('MENU_ARTICULO_999', out['text']); self.assertNotIn('RELATED_ARTICULO_888', out['text'])

    def test_no_keyword_blacklist(self):
        text = 'Artículo 2. Contenido: navegación, referencias y disposiciones finales.'
        self.assertIn(text, run(page('<p>' + text + '</p>'))['text'])

    def test_repeated_numbers_and_transitory_provisions_retained(self):
        raw = page('<p>Artículo 1. Regla.</p><h3>Disposiciones transitorias</h3><p>Artículo 1. Excepción.</p><p>Disposición final única: no cobrar.</p>')
        out = run(raw)
        self.assertEqual(out['text'].count('Artículo 1.'), 2)
        self.assertIn('Excepción.', out['text']); self.assertIn('no cobrar.', out['text'])

    def test_inline_anchor_and_entities(self):
        out = run(page('<p>Pro<strong>hibido</strong> pagar &lt; 10 &amp; más de&nbsp;20; <a href="/norma">Ley 603</a>.</p>'))
        self.assertIn('Prohibido pagar < 10 & más de 20; Ley 603.', out['text'])

    def test_table_cells_and_spans_preserved(self):
        body = '<table><tr><th>Cargo</th><th>Costo</th></tr><tr><td rowspan="2">A</td><td>390.000</td></tr><tr><td>13.000</td></tr></table>'
        out = run(page(body))
        self.assertIn('A\t390.000', out['text']); self.assertIn('rowspan="2"', out['legal_html'])
        self.assertEqual(sum(x['tag'] == 'tr' for x in out['structure']), 3)

    def test_list_numbering_attributes_and_nested_lists_retained(self):
        body = '<ol type="a" start="3"><li value="5">No permitido<ol><li>Salvo autorización</li></ol></li></ol>'
        out = run(page(body))
        self.assertIn(body, out['legal_html']); self.assertIn('No permitido', out['text']); self.assertIn('Salvo autorización', out['text'])

    def test_exact_source_span_and_distinct_digests(self):
        raw = page('<p>Artículo 1. &#241;.</p>'); out = run(raw)
        a, b = out['source_char_span']; self.assertEqual(raw.decode()[a:b], out['legal_html'])
        self.assertNotEqual(out['source_sha256'], out['text_sha256']); self.assertFalse(out['safe_to_render_html'])

    def test_no_fallback_when_container_missing(self):
        with self.assertRaises(m.ExtractionError): run(b'<p>Articulo 1: no container</p>')

    def test_duplicate_or_nested_container_rejected(self):
        for raw in [page('<p>x</p>') * 2, page('<div id="normTxtId"><p>x</p></div>')]:
            with self.subTest(raw=raw), self.assertRaises(m.ExtractionError): run(raw)

    def test_wrong_title_rejected(self):
        raw = page('<p>x</p>')
        with self.assertRaises(m.ExtractionError): m.extract(raw, hashlib.sha256(raw).hexdigest(), 'Wrong law')

    def test_unclosed_and_mismatched_markup_rejected(self):
        for raw in [b'<div id="normTxtId"><h1>Ley sint</h1>', page('<p>one</div>')]:
            with self.subTest(raw=raw), self.assertRaises(m.ExtractionError): run(raw)

    def test_active_or_image_content_requires_review(self):
        for body in ['<script>bad()</script>', '<img src="annex.png">', '<nav>Maybe legal</nav>', '<iframe src="/x"></iframe>']:
            with self.subTest(body=body), self.assertRaises(m.ExtractionError): run(page(body))

    def test_hidden_body_content_not_silently_removed(self):
        for attrs in ['hidden', 'aria-hidden="true"', 'style="display:none"']:
            with self.subTest(attrs=attrs), self.assertRaises(m.ExtractionError): run(page('<p ' + attrs + '>provision</p>'))

    def test_bad_hash_and_utf8(self):
        raw = page('<p>x</p>')
        for digest in [None, '', '0'*64, 'a'*12]:
            with self.subTest(digest=digest), self.assertRaises(m.ExtractionError): m.extract(raw, digest, TITLE)
        with self.assertRaises(m.ExtractionError): run(b'\xff')

    def test_depth_limit(self):
        with self.assertRaises(m.ExtractionError): run(page('<div>'*130 + 'text' + '</div>'*130))

    def test_hidden_root_rejected(self):
        raw = page('<p>x</p>').replace(b'class="norma"', b'hidden')
        with self.assertRaises(m.ExtractionError): run(raw)

    def test_duplicate_title_rejected(self):
        with self.assertRaises(m.ExtractionError): run(page('<h1>Otro titulo</h1><p>x</p>'))

    def test_comment_not_search_text_but_retained_in_html(self):
        out = run(page('<p>Regla<!-- metadata --> aplicable.</p>'))
        self.assertNotIn('metadata', out['text'])
        self.assertIn('<!-- metadata -->', out['legal_html'])

    def test_rejection_produces_no_destination(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td); raw = b'<html>no source container</html>'; (p/'in.html').write_bytes(raw)
            cmd=[sys.executable,str(ROOT/'pipeline/legal_html.py'),'--input',str(p/'in.html'),'--output',str(p/'out.json'),'--sha256',hashlib.sha256(raw).hexdigest(),'--title',TITLE]
            result=subprocess.run(cmd,capture_output=True)
            self.assertEqual(result.returncode,2); self.assertFalse((p/'out.json').exists())

    def test_cli_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td); raw = page('<p>Artículo 1. Vigencia desconocida.</p>'); (p/'in.html').write_bytes(raw)
            cmd=[sys.executable,str(ROOT/'pipeline/legal_html.py'),'--input',str(p/'in.html'),'--output',str(p/'out.json'),'--sha256',hashlib.sha256(raw).hexdigest(),'--title',TITLE]
            r=subprocess.run(cmd,capture_output=True);self.assertEqual(r.returncode,0)
            before=(p/'out.json').read_bytes();r=subprocess.run(cmd,capture_output=True);self.assertEqual(r.returncode,2)
            self.assertEqual((p/'out.json').read_bytes(),before);self.assertEqual((p/'in.html').read_bytes(),raw)


if __name__ == '__main__': unittest.main(verbosity=2)
