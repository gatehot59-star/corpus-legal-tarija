#!/usr/bin/env python3
"""Prepare a new reported-document experiment; split and compare every rendered page.
This does not run OCR or open the Corpus database. Intermediate files are retained.
"""
import json,sys,subprocess,hashlib,re,shutil,urllib.request,traceback,time
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image

def sha(p):
    """Return a full SHA256 digest."""
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,value):
    """Write an owned preparation record atomically."""
    p=Path(p);q=p.with_suffix('.new');q.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');q.replace(p)
def run(argv,timeout=90):
    """Run a real command and fail loudly on any nonzero exit."""
    r=subprocess.run(argv,capture_output=True,text=True,timeout=timeout)
    logs.append({'argv':argv,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
    save(base/'preparation-commands.json',logs)
    if r.returncode: raise RuntimeError(str(argv)+':'+r.stderr)
    return r.stdout
def info(path):
    """Read the page count using Poppler, rejecting encrypted/unknown documents."""
    s=run(['/usr/bin/pdfinfo',str(path)])
    m=re.search(r'^Pages:\s+(\d+)',s,re.M)
    if not m or re.search(r'^Encrypted:\s+yes',s,re.M): raise ValueError('pdf_info')
    return int(m.group(1))
def render(pdf,page,prefix):
    """Render with exactly the candidate's Poppler arguments."""
    run(['/usr/bin/pdftoppm','-f',str(page),'-l',str(page),'-singlefile','-r','300','-scale-to','5000','-gray','-png',str(pdf),str(prefix)],60)
    path=prefix.with_suffix('.png')
    with Image.open(path) as image:
        image.load()
        if image.width*image.height>24000000: raise ValueError('pixel_limit')
        return {'sha256':sha(path),'width':image.width,'height':image.height,'mode':image.mode,'pixel_sha256':hashlib.sha256(image.tobytes()).hexdigest()}
base=Path(sys.argv[1]);logs=[];started=time.monotonic()
status={'state':'preparing','started_utc':datetime.now(timezone.utc).isoformat(),'pages_verified':0}
save(base/'preparation-status.json',status)
try:
    docs=json.loads((base/'sources.json').read_bytes());batches=[]
    for di,d in enumerate(docs,1):
        directory=base/f'document-{di}';directory.mkdir()
        source=directory/'original.pdf'
        if d['existing'] and Path(d['existing']).is_file(): shutil.copy2(d['existing'],source)
        else:
            with urllib.request.urlopen(d['url'],timeout=60) as response: data=response.read(20*1024*1024+1)
            source.write_bytes(data)
        if source.stat().st_size!=d['bytes'] or sha(source)!=d['sha256'] or info(source)!=d['pages']: raise ValueError('source_mismatch:'+d['uid'])
        d['input']=str(source.relative_to(base))
        run(['/usr/bin/pdfseparate',str(source),str(directory/'single-%04d.pdf')])
        for first in range(1,d['pages']+1,4):
            pages=list(range(first,min(first+4,d['pages']+1)))
            number=len(batches)+1;subset=directory/f'batch-{number:02d}.pdf'
            run(['/usr/bin/pdfunite']+[str(directory/f'single-{p:04d}.pdf') for p in pages]+[str(subset)])
            if info(subset)!=len(pages) or subset.stat().st_size>20*1024*1024: raise ValueError('subset_limit')
            batch={'number':number,'source_sha256':d['sha256'],'input':str(subset.relative_to(base)),'sha256':sha(subset),'bytes':subset.stat().st_size,'pages':[]}
            for local,original in enumerate(pages,1):
                a=render(source,original,directory/f'original-{original:04d}')
                b=render(subset,local,directory/f'subset-{original:04d}')
                if a!=b: raise ValueError('render_parity:'+str((di,original,a,b)))
                batch['pages'].append({'local_page':local,'source_page':original,'image_sha256':a['sha256'],'pixel_sha256':a['pixel_sha256'],'width':a['width'],'height':a['height'],'mode':a['mode']})
                status.update(document=di,source_page=original,pages_verified=status['pages_verified']+1,updated_utc=datetime.now(timezone.utc).isoformat())
                save(base/'preparation-status.json',status)
            batches.append(batch)
            save(base/'prepared-manifest.json',{'documents':docs,'batches':batches})
    if len(batches)!=32 or status['pages_verified']!=125: raise ValueError('coverage')
    status['state']='prepared'
except BaseException as error:
    status.update(state='failed',error_type=type(error).__name__,error=str(error));traceback.print_exc()
finally:
    status['wall_seconds']=time.monotonic()-started;status['finished_utc']=datetime.now(timezone.utc).isoformat();save(base/'preparation-status.json',status)
print(json.dumps(status),flush=True)
if status['state']!='prepared': sys.exit(1)
