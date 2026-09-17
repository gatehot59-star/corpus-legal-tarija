"""SOL regressions plus exact-version fixed oracles. Synthetic data only."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'sistema/api'))
from version_text import read_version, VersionReadError
from test_clean_snapshot import CleanCopyTests


class InputTests(CleanCopyTests):
    def test_nonobject_mapping_items_return_json(self):
        for value in [None,7,[],True,'bad']:
            self.mapping=[value]
            with self.subTest(value=value):
                self.assertEqual(self.invoke()[0],2)
                self.assertFalse(self.out.exists())

    def test_wrong_required_types_return_json(self):
        baseline=dict(self.mapping[0])
        for field in baseline:
            self.mapping=[dict(baseline,**{field:[]})]
            with self.subTest(field=field):
                self.assertEqual(self.invoke()[0],2)
                self.assertFalse(self.out.exists())

    def test_fifo_html_rejected_under_timeout(self):
        os.mkfifo(self.p/'pipe')
        self.mapping[0]['html_file']='pipe'
        self.assertEqual(self.invoke()[0],2)
        self.assertFalse(self.out.exists())

    def test_fifo_mapping_rejected_under_timeout(self):
        os.mkfifo(self.p/'pipe')
        r=subprocess.run([sys.executable,str(ROOT/'pipeline/clean_snapshot.py'),'--source-db',str(self.db),'--output',str(self.out),'--mapping',str(self.p/'pipe'),'--mapping-sha256','0'*64,'--expected-count','2','--expected-uid-sha256',self.digest],capture_output=True,text=True,timeout=3)
        self.assertEqual(r.returncode,2);self.assertFalse(json.loads(r.stdout)['ok']);self.assertFalse(self.out.exists())

    def test_exact_repeated_text_after_real_build(self):
        phrase='El pago no procede sin autorizacion judicial.'
        expected='Ley 1\n'+(phrase+'\n')*150
        raw=('<div id="normTxtId"><h1>Ley 1</h1>'+('<p>'+phrase+'</p>')*150+'</div>').encode()
        (self.p/'law.html').write_bytes(raw);self.mapping[0]['original_sha256']=hashlib.sha256(raw).hexdigest()
        self.assertEqual(self.invoke()[0],0)
        with sqlite3.connect(self.out) as c:
            result=read_version(c,self.ids[0],limit=10000)
            self.assertEqual(result['text'],expected)
            self.assertEqual(result['text'].count(phrase),150)
            self.assertEqual(result['total_characters'],6906)
            self.assertFalse(result['oficial'])


class VersionTests(unittest.TestCase):
    def setUp(self):
        self.c=sqlite3.connect(':memory:');self.addCleanup(self.c.close)
        self.c.executescript('CREATE TABLE documentos(uid TEXT,sha256 TEXT,fuente_id TEXT,fuente_url TEXT); CREATE TABLE corpus_cleanup_versions(uid TEXT,version_sha256 TEXT,extraction_json TEXT);')
        self.text='Ley 1\nNo pagar.\n';self.sha=hashlib.sha256(self.text.encode()).hexdigest()
        self.c.execute('INSERT INTO documentos VALUES(?,?,?,?)',('uid',self.sha,'lexivox_nacional','https://example.org/law'))
        self.c.execute('INSERT INTO corpus_cleanup_versions VALUES(?,?,?)',('uid',self.sha,json.dumps({'text':self.text,'text_sha256':self.sha,'source_sha256':'a'*64,'authority':'secondary'})))

    def test_exact_slice_and_versioned_next(self):
        first=read_version(self.c,'uid',limit=4);n=first['next']
        rest=read_version(self.c,'uid',version=n['version'],start=n['start'])
        self.assertEqual(first['text']+rest['text'],self.text)

    def test_offset_requires_version(self):
        with self.assertRaisesRegex(VersionReadError,'VERSION_REQUIRED'):read_version(self.c,'uid',start=4)

    def test_unknown_version_no_fallback(self):
        with self.assertRaisesRegex(VersionReadError,'UNAVAILABLE'):read_version(self.c,'uid','0'*64)

    def test_tampered_ledger_rejected(self):
        self.c.execute('UPDATE corpus_cleanup_versions SET extraction_json=?',(json.dumps({'text':'changed','text_sha256':self.sha}),))
        with self.assertRaisesRegex(VersionReadError,'INTEGRITY'):read_version(self.c,'uid')

    def test_prior_exact_version_stays_accessible(self):
        self.c.execute("UPDATE documentos SET sha256=?",('b'*64,))
        result=read_version(self.c,'uid',self.sha)
        self.assertEqual(result['text'],self.text);self.assertFalse(result['is_current'])

    def test_unsupported_legacy_record_rejected(self):
        self.c.execute('DELETE FROM corpus_cleanup_versions')
        with self.assertRaisesRegex(VersionReadError,'UNAVAILABLE'):read_version(self.c,'uid')


if __name__=='__main__':unittest.main(verbosity=2)
