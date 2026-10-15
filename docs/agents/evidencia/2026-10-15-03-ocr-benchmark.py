#!/usr/bin/env python3
"""Bounded OCR pilot: six real scans (unscored), four synthetic known-text controls."""
import argparse
import collections
import datetime
import hashlib
import importlib.metadata
import json
import os
import pathlib
import platform
import random
import re
import resource
import subprocess
import sys
import time
import unicodedata

PARAGRAPHS = [
    "Ley Nº 439",
    "19 de noviembre de 2013",
    "Artículo 3°.- (Buena fe y lealtad procesal).",
    "I. Las autoridades judiciales están en la obligación de impedir y sancionar toda forma de fraude procesal, colusión, dilación, y en suma cualquier manifestación de inconducta procesal.",
    "II. Las partes y en general quienes intervienen en el proceso, deben actuar en forma honesta, de buena fe, con lealtad y veracidad sobre la base del conocimiento cierto de los hechos y el entender racional del derecho aplicable, respetando a la autoridad judicial y los derechos del adversario.",
    "Artículo 29°.- (Capacidad e incapacidad).",
    "I. Toda persona natural o colectiva que tenga capacidad de obrar, podrá intervenir en el proceso en calidad de parte actora, demandada o tercero, ya sea directamente o por representación.",
    "II. Las y los incapaces no podrán intervenir por sí mismos en el proceso, debiendo actuar por medio de sus representantes.",
]
FIELDS = [
    "439",
    "19 de noviembre de 2013",
    "Artículo 3",
    "Artículo 29",
    "fraude procesal",
    "buena fe",
    "no podrán",
    "por sí mismos",
]
SOURCE = "https://www.lexivox.org/norms/BO-L-N439.xhtml"


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha_file(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def save(path, value):
    pathlib.Path(path).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def norm(text):
    return " ".join(unicodedata.normalize("NFC", text).split())


def distance(a, b):
    if len(a) < len(b):
        a, b = b, a
    row = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        new = [i]
        for j, y in enumerate(b, 1):
            new.append(min(row[j] + 1, new[j - 1] + 1, row[j - 1] + (x != y)))
        row = new
    return row[-1]


def independent_distance(a, b):
    grid = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        grid[i][0] = i
    for j in range(len(b) + 1):
        grid[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            grid[i][j] = min(
                grid[i - 1][j] + 1,
                grid[i][j - 1] + 1,
                grid[i - 1][j - 1] + (a[i - 1] != b[j - 1]),
            )
    return grid[-1][-1]


def score(reference, output, fields):
    a, b = norm(reference), norm(output)
    aw, bw = a.split(), b.split()
    ca, cb = collections.Counter(aw), collections.Counter(bw)
    overlap = sum((ca & cb).values())
    field_results = {
        f: bool(re.search(r"(?<!\w)" + re.escape(norm(f).casefold()) + r"(?!\w)", b.casefold()))
        for f in fields
    }
    edits, word_edits = distance(a, b), distance(aw, bw)
    return {
        "reference_chars": len(a),
        "reference_words": len(aw),
        "character_edits": edits,
        "word_edits": word_edits,
        "cer": edits / len(a),
        "wer": word_edits / len(aw),
        "word_bag_f1": 2 * overlap / (len(aw) + len(bw)) if aw or bw else 1,
        "fields": field_results,
        "fields_present": sum(field_results.values()),
        "fields_total": len(fields),
    }


def selftest():
    checks = {}
    checks["identical"] = score("no podrá 439", "no podrá 439", ["no podrá", "439"])["cer"] == 0
    checks["substitution"] = score("abc", "adc", [])["cer"] == 1 / 3
    checks["blank_is_total_deletion"] = score("abc def", "", [])["cer"] == 1
    mutation = score("no podrá 439", "podrá 438", ["no podrá", "439"])
    checks["removed_negation_and_changed_number_rejected"] = mutation["fields_present"] == 0
    checks["number_boundary_1439_not_439"] = not score("439", "1439", ["439"])["fields"]["439"]
    reordered = score("artículo uno artículo dos", "artículo dos artículo uno", [])
    checks["reading_order_matters"] = reordered["cer"] > 0 and reordered["word_bag_f1"] == 1
    checks["whitespace_only_ignored"] = score("a b", "a\n\nb", [])["cer"] == 0
    checks["accent_retained"] = score("sí", "si", [])["cer"] == 0.5
    checks["case_retained"] = score("Ley", "ley", [])["cer"] == 1 / 3
    rng = random.Random(439)
    pairs = []
    for _ in range(200):
        a = "".join(rng.choice("ab ñ1") for _ in range(rng.randrange(12)))
        b = "".join(rng.choice("ab ñ1") for _ in range(rng.randrange(12)))
        pairs.append(distance(a, b) == independent_distance(a, b))
    checks["200_pairs_crosschecked_against_full_matrix"] = all(pairs)
    assert all(checks.values()), checks
    return {"utc": utc(), "checks": checks, "mutant_score": mutation, "reordered_score": reordered}


def version_command(command):
    p = subprocess.run(command, capture_output=True, text=True, timeout=20)
    return {"command": command, "exit": p.returncode, "stdout": p.stdout, "stderr": p.stderr}


def prepare(root):
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    import numpy as np

    if (root / "seal.json").exists():
        raise RuntimeError("Existing seal: do not overwrite a frozen bank")
    discovery = json.loads((root / "discovery.json").read_text())
    (root / "controls").mkdir(exist_ok=True)
    font_path = pathlib.Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf")
    font = ImageFont.truetype(str(font_path), 32)

    def draw_paragraphs(im, paragraphs, x, y, width):
        draw = ImageDraw.Draw(im)
        for paragraph in paragraphs:
            line = ""
            for word in paragraph.split():
                candidate = (line + " " + word).strip()
                if line and draw.textlength(candidate, font=font) > width:
                    draw.text((x, y), line, fill=0, font=font)
                    y += 46
                    line = word
                else:
                    line = candidate
            draw.text((x, y), line, fill=0, font=font)
            y += 64
        if y >= im.height - 35:
            raise RuntimeError("Control text overflow")
        return y

    clean = Image.new("L", (2200, 1600), 255)
    draw_paragraphs(clean, PARAGRAPHS, 90, 80, 2020)
    clean.save(root / "controls" / "c01-clean.png", dpi=(300, 300))
    skew = clean.rotate(2, resample=Image.Resampling.BICUBIC, expand=True, fillcolor=255)
    skew = skew.filter(ImageFilter.GaussianBlur(0.65))
    rng = np.random.default_rng(20261015)
    arr = np.asarray(skew).astype(np.float32)
    arr = np.clip(arr * 0.78 + 42 + rng.normal(0, 3, arr.shape), 0, 255).astype(np.uint8)
    Image.fromarray(arr).save(root / "controls" / "c02-skew-blur.png", dpi=(300, 300))
    clean.resize((1100, 800), Image.Resampling.LANCZOS).save(
        root / "controls" / "c03-150dpi.png", dpi=(150, 150)
    )
    columns = Image.new("L", (2200, 1600), 255)
    draw_paragraphs(columns, PARAGRAPHS[:5], 70, 80, 960)
    draw_paragraphs(columns, PARAGRAPHS[5:], 1170, 80, 960)
    columns.save(root / "controls" / "c04-two-columns.png", dpi=(300, 300))
    warmup = Image.new("L", (900, 160), 255)
    ImageDraw.Draw(warmup).text((30, 45), "Control de inicio 439", font=font, fill=0)
    warmup.save(root / "warmup.png", dpi=(300, 300))
    reference = "\n\n".join(PARAGRAPHS)
    cases = []
    for row in discovery["rows"]:
        if sha_file(row["image"]) != row["image_sha256"]:
            raise RuntimeError("Real-image hash mismatch")
        cases.append({
            "id": row["id"], "kind": "real_scan_unscored", "image": row["image"],
            "image_sha256": row["image_sha256"], "reference": None, "fields": [],
        })
    for path in sorted((root / "controls").glob("*.png")):
        cases.append({
            "id": path.stem, "kind": "synthetic_control", "image": str(path),
            "image_sha256": sha_file(path), "reference": reference, "fields": FIELDS,
        })
    bank = {
        "created_utc": utc(),
        "scope": "6 real pages from 3 PDFs for runtime/output only; 4 synthetic variants of one known text for accuracy. No independent real-scan gold.",
        "normalization": "Unicode NFC and whitespace collapse only; case, accents, punctuation retained.",
        "metrics": "Levenshtein CER/WER; word-bag F1 diagnostic; case-insensitive exact field presence with token boundaries (not legal accuracy).",
        "control_source": SOURCE,
        "control_source_note": "Native public HTML excerpt read before inference, rendered by this script. Typography spacing around headings normalized. Not a scanned original or independent legal validation.",
        "font_path": str(font_path), "font_sha256": sha_file(font_path),
        "control_generation": {"font_px": 32, "line_step_px": 46, "random_seed": 20261015,
                               "skew_deg": 2, "blur_sigma": 0.65, "noise_sigma": 3},
        "configuration": {
            "threads": 1, "device": "cpu", "tesseract": ["--tessdata-dir", "/tmp/tessdata", "-l", "spa", "--oem", "1", "--psm", "3"],
            "paddleocr": {"lang": "es", "ocr_version": "PP-OCRv5",
                "text_detection_model_name": "PP-OCRv5_mobile_det",
                "text_recognition_model_name": "latin_PP-OCRv5_mobile_rec",
                "use_doc_orientation_classify": False, "use_doc_unwarping": False,
                "use_textline_orientation": False, "enable_mkldnn": False,
                "text_det_limit_side_len": 960, "text_det_limit_type": "max", "cpu_threads": 1},
            "order": "Tesseract then PaddleOCR, sequential, one warmup each, one timed pass, no tuning after scoring.",
        },
        "cases": cases,
        "selftest": selftest(),
    }
    save(root / "bank.json", bank)
    save(root / "seal.json", {"utc": utc(), "bank_sha256": sha_file(root / "bank.json"),
                              "script_sha256": sha_file(__file__)})
    print(json.dumps({"prepared": len(cases), "seal": json.loads((root / "seal.json").read_text())}))


def verify_bank(root):
    seal = json.loads((root / "seal.json").read_text())
    if sha_file(root / "bank.json") != seal["bank_sha256"] or sha_file(__file__) != seal["script_sha256"]:
        raise RuntimeError("Frozen bank/script modified")
    bank = json.loads((root / "bank.json").read_text())
    for row in bank["cases"]:
        if sha_file(row["image"]) != row["image_sha256"]:
            raise RuntimeError("Input hash mismatch: " + row["id"])
    return bank


def run(root, engine):
    bank = verify_bank(root)
    output_dir = root / ("output-" + engine)
    output_dir.mkdir(exist_ok=False)
    record = {"engine": engine, "start_utc": utc(), "host": platform.platform(),
              "cpu_count": os.cpu_count(), "loadavg_start": os.getloadavg(),
              "python": sys.version, "runs": []}
    for key in ("OMP_NUM_THREADS", "OMP_THREAD_LIMIT", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
        os.environ[key] = "1"
    os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
    if engine == "tesseract":
        record["version"] = version_command(["tesseract", "--version"])
        record["languages"] = version_command(["tesseract", "--tessdata-dir", "/tmp/tessdata", "--list-langs"])
        tessdata = pathlib.Path("/tmp/tessdata/spa.traineddata")
        record["spanish_model"] = {"path": str(tessdata), "sha256": sha_file(tessdata)}

        def infer(path):
            cmd = ["tesseract", str(path), "stdout"] + bank["configuration"]["tesseract"]
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            return p.stdout, {"command": cmd, "exit": p.returncode, "stderr": p.stderr}
        record["init_seconds"] = 0
    else:
        start = time.perf_counter()
        from paddleocr import PaddleOCR
        kwargs = dict(bank["configuration"]["paddleocr"])
        model_base = pathlib.Path.home() / ".paddlex/official_models"
        kwargs["text_detection_model_dir"] = str(model_base / kwargs["text_detection_model_name"])
        kwargs["text_recognition_model_dir"] = str(model_base / kwargs["text_recognition_model_name"])
        kwargs["device"] = "cpu"
        record["model_files"] = []
        for directory in (kwargs["text_detection_model_dir"], kwargs["text_recognition_model_dir"]):
            for f in sorted(pathlib.Path(directory).rglob("*")):
                if f.is_file():
                    record["model_files"].append({"path": str(f), "bytes": f.stat().st_size, "sha256": sha_file(f)})
        record["constructor"] = kwargs
        ocr = PaddleOCR(**kwargs)
        record["init_seconds"] = time.perf_counter() - start
        record["versions"] = {n: importlib.metadata.version(n) for n in ("paddlepaddle", "paddleocr", "paddlex")}

        def infer(path):
            result = ocr.predict(str(path))
            data_list, texts = [], []
            for res in result:
                data = res.json if hasattr(res, "json") else res
                if callable(data):
                    data = data()
                if isinstance(data, str):
                    data = json.loads(data)
                body = data.get("res", data)
                if "rec_texts" not in body:
                    raise RuntimeError("No recognized-text field in response")
                texts.extend(body["rec_texts"])
                data_list.append(data)
            return "\n".join(texts), {"exit": 0, "raw": data_list}
    t = time.perf_counter()
    warm_text, warm_raw = infer(root / "warmup.png")
    record["warmup"] = {"seconds": time.perf_counter() - t, "text": warm_text, "exit": warm_raw["exit"]}
    if warm_raw["exit"] != 0:
        raise RuntimeError("Warmup failed")
    for case in bank["cases"]:
        t = time.perf_counter()
        try:
            text, raw = infer(case["image"])
            elapsed = time.perf_counter() - t
            (output_dir / (case["id"] + ".txt")).write_text(text, encoding="utf-8")
            save(output_dir / (case["id"] + ".raw.json"), raw)
            row = {"id": case["id"], "kind": case["kind"], "seconds": elapsed,
                   "exit": raw["exit"], "chars": len(text), "words": len(text.split()),
                   "text": text, "text_sha256": sha_file(output_dir / (case["id"] + ".txt")),
                   "raw_sha256": sha_file(output_dir / (case["id"] + ".raw.json")),
                   "input_sha256": sha_file(case["image"])}
        except Exception as exc:
            row = {"id": case["id"], "kind": case["kind"], "seconds": time.perf_counter() - t,
                   "exit": None, "error": repr(exc), "text": None}
        record["runs"].append(row)
        save(root / (engine + ".json"), record)
        print(json.dumps({"engine": engine, "id": case["id"], "seconds": row["seconds"],
                          "exit": row["exit"], "chars": row.get("chars")}), flush=True)
    record["finish_utc"] = utc()
    record["loadavg_end"] = os.getloadavg()
    record["peak_self_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    record["peak_child_rss_kib"] = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    save(root / (engine + ".json"), record)


def summarize(root):
    bank = verify_bank(root)
    evidence = {"created_utc": utc(), "bank": bank, "seal": json.loads((root / "seal.json").read_text()),
                "sources": json.loads((root / "discovery.json").read_text()),
                "engines": {}, "summary": {}, "instrument_tests": selftest()}
    index = {c["id"]: c for c in bank["cases"]}
    for engine in ("tesseract", "paddleocr"):
        record = json.loads((root / (engine + ".json")).read_text())
        if len(record["runs"]) != len(index) or {r["id"] for r in record["runs"]} != set(index):
            raise RuntimeError("Missing or unexpected input")
        controls = []
        for row in record["runs"]:
            case = index[row["id"]]
            if case["reference"] is not None:
                row["score"] = score(case["reference"], row["text"] or "", case["fields"])
                controls.append(row["score"])
        real = [r for r in record["runs"] if r["kind"] == "real_scan_unscored"]
        summary = {
            "completed": sum(r["exit"] == 0 for r in record["runs"]), "attempted": len(record["runs"]),
            "real_scan_pages": len(real), "real_seconds": sum(r["seconds"] for r in real),
            "real_output_chars": sum(r.get("chars", 0) for r in real),
            "synthetic_variants": len(controls), "synthetic_unique_texts": 1,
            "reference_chars_total": sum(s["reference_chars"] for s in controls),
            "reference_words_total": sum(s["reference_words"] for s in controls),
            "character_edits": sum(s["character_edits"] for s in controls),
            "word_edits": sum(s["word_edits"] for s in controls),
            "field_hits": sum(s["fields_present"] for s in controls),
            "field_total": sum(s["fields_total"] for s in controls),
            "accuracy_on_real_scans": None,
        }
        summary["cer"] = summary["character_edits"] / summary["reference_chars_total"]
        summary["wer"] = summary["word_edits"] / summary["reference_words_total"]
        evidence["engines"][engine], evidence["summary"][engine] = record, summary
    evidence["script"] = pathlib.Path(__file__).read_text()
    save(root / "evidence.json", evidence)
    save(root / "summary.json", evidence["summary"])
    print(json.dumps(evidence["summary"], ensure_ascii=False, indent=2))


def orchestrate(root):
    chain = {"start_utc": utc(), "steps": []}
    for engine in ("tesseract", "paddleocr"):
        t = time.perf_counter()
        p = subprocess.run([sys.executable, __file__, "run", str(root), engine], timeout=900)
        chain["steps"].append({"engine": engine, "exit": p.returncode, "seconds": time.perf_counter() - t})
        save(root / "chain.json", chain)
        if p.returncode != 0:
            raise RuntimeError("Engine process failed: " + engine)
    summarize(root)
    chain["finish_utc"] = utc()
    save(root / "chain.json", chain)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["selftest", "prepare", "run", "summarize", "orchestrate"])
    parser.add_argument("root", nargs="?", type=pathlib.Path)
    parser.add_argument("engine", nargs="?", choices=["tesseract", "paddleocr"])
    args = parser.parse_args()
    if args.mode == "selftest":
        print(json.dumps(selftest(), ensure_ascii=False, indent=2))
    elif args.mode == "run":
        run(args.root, args.engine)
    else:
        globals()[args.mode](args.root)
