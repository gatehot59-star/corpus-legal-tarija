"""Run a deterministic multi-document OCR candidate benchmark.

This does not calculate CER/WER and never mutates Corpus data. It selects scanned
manifest entries across rubro and gestion, requiring at least three pages so that
40 documents yield exactly 120 sampled pages, then runs pinned OCR candidates.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess, time, urllib.request
from pathlib import Path

TERMS=("gue","que","pario","tarja","tarija","torieños","tarijeños")

def terms(text):
    low=text.casefold(); return {x:low.count(x.casefold()) for x in TERMS}

def gate(text):
    import gate_v2
    return gate_v2.medir_pagina(text)

def download(url, dst):
    if dst.exists() and dst.stat().st_size > 1000: return
    req=urllib.request.Request(url,headers={"User-Agent":"Corpus-Tarija-OCR-Benchmark/1.0"})
    with urllib.request.urlopen(req,timeout=120) as r: data=r.read()
    if not data.startswith(b"%PDF"): raise RuntimeError(f"not PDF: {url}")
    dst.write_bytes(data)

def sample_rows(manifest,n_docs):
    rows=[]
    for line in manifest.open(encoding="utf-8"):
        if not line.strip(): continue
        try: r=json.loads(line)
        except json.JSONDecodeError: continue
        extraire=(r.get("etapas") or {}).get("extraer") or {}
        if extraire.get("estado")!="OCR_REQUERIDO": continue
        if not r.get("fuente_url") or int(r.get("paginas") or 0)<3: continue
        rows.append(r)
    rows.sort(key=lambda r:(r.get("rubro",""),str(r.get("gestion","")),r.get("sha256","")))
    buckets={}
    for r in rows: buckets.setdefault((r.get("rubro",""),str(r.get("gestion",""))),[]).append(r)
    chosen=[]
    while len(chosen)<n_docs and buckets:
        for key in sorted(list(buckets)):
            if buckets[key]: chosen.append(buckets[key].pop(0))
            if len(chosen)>=n_docs: break
            if not buckets[key]: del buckets[key]
    return chosen

def pages_for(total): return [1,(total+1)//2,total]

def run_tess(image,dst,tessdata):
    dst.parent.mkdir(parents=True,exist_ok=True); env=dict(os.environ,TESSDATA_PREFIX=str(tessdata)); t=time.monotonic()
    cp=subprocess.run(["tesseract",str(image),str(dst),"-l","spa","--psm","3"],env=env,capture_output=True,text=True)
    txt=dst.with_suffix(".txt").read_text(encoding="utf-8",errors="replace") if dst.with_suffix(".txt").exists() else ""
    return {"exit":cp.returncode,"seconds":round(time.monotonic()-t,3),"chars":len(txt),"terms":terms(txt),"gate":gate(txt),"text":txt}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--manifest",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); ap.add_argument("--docs",type=int,default=40); ap.add_argument("--dpi",type=int,default=300); ap.add_argument("--tessdata-fast",type=Path,required=True); ap.add_argument("--tessdata-best",type=Path,required=True); args=ap.parse_args()
    args.output.mkdir(parents=True,exist_ok=True); source=args.output/"sources"; images=args.output/"images"; source.mkdir(parents=True,exist_ok=True); images.mkdir(parents=True,exist_ok=True); (args.output/"paddleocr").mkdir(parents=True,exist_ok=True); selected=sample_rows(args.manifest,args.docs)
    if len(selected)!=args.docs: raise RuntimeError(f"selected {len(selected)} docs, need {args.docs}")
    rows=[]
    for ix,r in enumerate(selected,1):
        key=r.get("sha256") or hashlib.sha256(r["fuente_url"].encode()).hexdigest(); pdf=source/(key+".pdf"); download(r["fuente_url"],pdf); prefix=images/key; prefix.mkdir(parents=True,exist_ok=True)
        for page in pages_for(int(r["paginas"])):
            out=prefix/f"page-{page:04d}"; subprocess.run(["pdftoppm","-f",str(page),"-l",str(page),"-r",str(args.dpi),"-gray","-png",str(pdf),str(out)],check=True,capture_output=True); png=sorted(prefix.glob(out.name+"-*.png"))[0]
            rows.append({"sample_index":ix,"sha256":key,"title":r.get("nombre_servidor"),"rubro":r.get("rubro"),"gestion":r.get("gestion"),"page":page,"pages_total":r.get("paginas"),"image":str(png),"source_url":r.get("fuente_url")})
    if len(rows)!=args.docs*3: raise RuntimeError(f"sampled {len(rows)} pages, need {args.docs*3}")
    report={"gold_text":False,"note":"candidate benchmark only; CER/WER require independent human gold","docs":len(selected),"pages":len(rows),"dpi":args.dpi,"sources":rows,"engines":{}}
    for label,tessdata in (("tesseract_fast_psm3",args.tessdata_fast),("tesseract_best_psm3",args.tessdata_best)):
        out=[]
        for row in rows:
            res=run_tess(Path(row["image"]),args.output/label/(row["sha256"]+f"-p{row['page']:04d}"),tessdata); out.append({**row,**{k:v for k,v in res.items() if k!="text"}}); (args.output/label).mkdir(parents=True,exist_ok=True); (args.output/label/(row["sha256"]+f"-p{row['page']:04d}.txt")).write_text(res["text"],encoding="utf-8")
        report["engines"][label]=out
    from paddleocr import PaddleOCR
    engine=PaddleOCR(lang="es",ocr_version="PP-OCRv5",text_detection_model_name="PP-OCRv5_mobile_det",text_recognition_model_name="latin_PP-OCRv5_mobile_rec",device="cpu",enable_mkldnn=False,use_doc_orientation_classify=False,use_doc_unwarping=False,use_textline_orientation=False); out=[]
    for row in rows:
        t=time.monotonic(); texts=[]
        for result in engine.predict(row["image"]):
            payload=result.json if hasattr(result,"json") else result
            if callable(payload): payload=payload()
            if isinstance(payload,str): payload=json.loads(payload)
            if isinstance(payload,dict): texts.extend(payload.get("res",{}).get("rec_texts",[]))
        text="\n".join(texts); (args.output/"paddleocr"/(row["sha256"]+f"-p{row['page']:04d}.txt")).write_text(text,encoding="utf-8"); out.append({**row,"seconds":round(time.monotonic()-t,3),"chars":len(text),"terms":terms(text),"gate":gate(text)})
    report["engines"]["paddleocr_ppocrv5_mobile_latin_cpu"]=out; (args.output/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8"); print(json.dumps({"docs":len(selected),"pages":len(rows),"output":str(args.output),"gold_text":False},ensure_ascii=False))

if __name__=="__main__": raise SystemExit(main())
