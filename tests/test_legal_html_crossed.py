"""Crossed-closing-tag regressions; use the unchanged PR6 baseline helpers."""
import hashlib
import unittest
from test_legal_html import m, page, run


class CrossedClosingTests(unittest.TestCase):
    def test_crossed_outer_closes_rejected(self):
        """SOL's exact ASCII body cannot escape hidden table/template/object."""
        body = '<div id="normTxtId"><h1>Ley sintetica 1</h1><p>No pagar 390000.</p></div>'
        for tag in ('table', 'template', 'object'):
            raw = ('<div hidden><' + tag + '></div>' + body + '</' + tag + '></div>').encode()
            with self.subTest(tag=tag), self.assertRaises(m.ExtractionError):
                m.extract(raw, hashlib.sha256(raw).hexdigest(), 'Ley sintetica 1')

    def test_crossed_visible_outer_closes_also_rejected(self):
        raw = page('<p>No pagar.</p>', before='<div><table></div>', after='</table></div>')
        with self.assertRaises(m.ExtractionError):
            run(raw)

    def test_unmatched_outer_close_rejected(self):
        with self.assertRaises(m.ExtractionError):
            run(page('<p>No pagar.</p>', before='</section>'))

    def test_balanced_visible_wrapper_and_closed_hidden_sibling_preserved(self):
        plain = run(page('<p>No pagar 390000.</p>', before='', after=''))
        wrapped = run(page('<p>No pagar 390000.</p>', before='<div hidden>irrelevante</div><section>', after='</section>'))
        self.assertEqual(plain['text'], wrapped['text'])
        self.assertEqual(plain['legal_html'], wrapped['legal_html'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
