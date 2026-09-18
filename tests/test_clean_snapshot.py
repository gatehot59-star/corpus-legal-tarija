"""Use an actual legacy SQLite corpus and the real cleanup CLI, all synthetic."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'sistema/api'))
from ingesta import Corpus,Documento


class CleanCopyTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.p=Path(self.tmp.name);self.db=self.p/'source.db';self.out=self.p/'new.db'
        corpus=Corpus(str(self.db));corpus.registrar_fuente('lexivox_nacional','synthetic','nacional','','issuer','https://example.org')
        self.ids=[];self.old=[]
        for i in (1,2):
            old='NAVIGATION Old body '+str(i);h=hashlib.sha256(old.encode()).hexdigest()
            doc=Documento('lexivox_nacional','nacional','Ley',str(i),old,'https://example.org/'+str(i),sha256=h,titulo='Ley '+str(i))
            corpus.agregar(doc);self.ids.append(doc.uid());self.old.append(h)
        corpus.cerrar();corpus.con.close()
        self.raw=b'<nav>REMOVE_NAVIGATION</nav><div id="normTxtId"><h1>Ley 1</h1><p>Articulo 1. No pagar 390000.</p></div>'
        (self.p/'law.html').write_bytes(self.raw)
        self.mapping=[{'uid':self.ids[0],'old_text_sha256':self.old[0],'source_url':'https://example.org/1','expected_title':'Ley 1','original_sha256':hashlib.sha256(self.raw).hexdigest(),'html_file':'law.html'}]
        self.digest=hashlib.sha256('\n'.join(sorted(self.ids)).encode()).hexdigest()

    def invoke(self):
        raw=json.dumps(self.mapping).encode();(self.p/'mapping.json').write_bytes(raw)
        cmd=[sys.executable,str(ROOT/'pipeline/clean_snapshot.py'),'--source-db',str(self.db),'--output',str(self.out),'--mapping',str(self.p/'mapping.json'),'--mapping-sha256',hashlib.sha256(raw).hexdigest(),'--expected-count','2','--expected-uid-sha256',self.digest]
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
        self.assertNotIn('Traceback',r.stderr)
        return r.returncode,json.loads(r.stdout)

    def test_full_copy_keeps_ids_and_archives_old_text(self):
        before=self.db.read_bytes();code,r=self.invoke();self.assertEqual(code,0)
        self.assertEqual(self.db.read_bytes(),before)
        with sqlite3.connect(self.out) as c:
            self.assertEqual([r[0] for r in c.execute('select uid from documentos order by uid')],sorted(self.ids))
            text=''.join(r[0] for r in c.execute('select cuerpo from chunks where uid=?',(self.ids[0],)))
            self.assertIn('No pagar 390000.',text);self.assertNotIn('REMOVE_NAVIGATION',text)
            old=json.loads(c.execute('select prior_chunks_json from corpus_cleanup_versions').fetchone()[0])
            self.assertIn('NAVIGATION Old body',old[0]['cuerpo'])
            self.assertEqual(c.execute('select sha256 from documentos where uid=?',(self.ids[1],)).fetchone()[0],self.old[1])
        self.assertFalse(r['publication_authorized'])

    def test_stale_hash_rejects_without_output(self):
        self.mapping[0]['old_text_sha256']='0'*64
        self.assertEqual(self.invoke()[0],2);self.assertFalse(self.out.exists())

    def test_wrong_source_url_rejected(self):
        self.mapping[0]['source_url']='https://example.org/other'
        self.assertEqual(self.invoke()[0],2);self.assertFalse(self.out.exists())

    def test_unknown_uid_rejected(self):
        self.mapping[0]['uid']='missing'
        self.assertEqual(self.invoke()[0],2);self.assertFalse(self.out.exists())

    def test_tampered_html_rejected(self):
        (self.p/'law.html').write_bytes(self.raw+b'changed')
        self.assertEqual(self.invoke()[0],2);self.assertFalse(self.out.exists())

    def test_second_bad_mapping_leaves_no_partial_candidate(self):
        self.mapping.append(dict(self.mapping[0],uid=self.ids[1],old_text_sha256='wrong'))
        self.assertEqual(self.invoke()[0],2);self.assertFalse(self.out.exists())

    def test_duplicate_mapping_rejected(self):
        self.mapping.append(dict(self.mapping[0]))
        self.assertEqual(self.invoke()[0],2);self.assertFalse(self.out.exists())

    def test_wrong_uid_set_rejected(self):
        self.digest='0'*64;self.assertEqual(self.invoke()[0],2);self.assertFalse(self.out.exists())

    def test_existing_destination_untouched(self):
        self.out.write_bytes(b'keep');self.assertEqual(self.invoke()[0],2);self.assertEqual(self.out.read_bytes(),b'keep')

    def test_path_escape_rejected(self):
        self.mapping[0]['html_file']='../law.html';self.assertEqual(self.invoke()[0],2);self.assertFalse(self.out.exists())


if __name__=='__main__':unittest.main(verbosity=2)
