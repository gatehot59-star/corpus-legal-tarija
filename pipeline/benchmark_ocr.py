"""Benchmark isolated OCR engines on identical rendered pages.

The harness writes raw per-engine text and metrics. It never mutates the corpus,
its manifest, or a production database. It deliberately does not calculate CER/WER
without human gold text: engine disagreement is not ground truth.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from pathlib import Path


TERMS = ("gue", "que", "pario", "tarja", "tarija", "torieños", "tarijeños")


def render(pdf: Path, pages: list[int], out: Path, dpi: int) -> list[Path]:
    """Render the requested pages once so every engine receives identical PNGs."""
    out.mkdir(parents=True, exist_ok=True)
    images = []
    for page in pages:
        prefix = out / f"page-{page:04d}"
        subprocess.run(["pdftoppm", "-f", str(page), "-l", str(page), "-r", str(dpi),
                        "-gray", "-png", str(pdf), str(prefix)], check=True,
                       capture_output=True, text=True)
        images.extend(sorted(out.glob(prefix.name + "-*.png")))
    return images


def tesseract(image: Path, destination: Path, tessdata: Path, psm: int) -> dict:
    """Run one pinned Tesseract variant and return raw text plus timing."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    env = dict(os.environ, TESSDATA_PREFIX=str(tessdata))
    completed = subprocess.run(["tesseract", str(image), str(destination), "-l", "spa",
                               "--psm", str(psm)], env=env, capture_output=True, text=True)
    text_path = destination.with_suffix(".txt")
    text = text_path.read_text(encoding="utf-8", errors="replace") if text_path.exists() else ""
    return {"exit": completed.returncode, "seconds": round(time.monotonic() - started, 3),
            "text": text, "stderr": completed.stderr[-500:]}


def terms(text: str) -> dict[str, int]:
    """Count disputed OCR tokens for comparison only, never as correctness labels."""
    lowered = text.casefold()
    return {term: lowered.count(term.casefold()) for term in TERMS}


def gate_metrics(text: str) -> dict:
    """Apply the repository gate to one page without turning it into ground truth."""
    import gate_v2
    return gate_v2.medir_pagina(text)


def paddle(images: list[Path], destination: Path) -> list[dict]:
    """Run PaddleOCR PP-OCRv5 mobile Latin on the same page images."""
    from paddleocr import PaddleOCR

    destination.mkdir(parents=True, exist_ok=True)
    engine = PaddleOCR(
        lang="es", ocr_version="PP-OCRv5",
        text_detection_model_name="PP-OCRv5_mobile_det",
        text_recognition_model_name="latin_PP-OCRv5_mobile_rec",
        device="cpu", enable_mkldnn=False,
        use_doc_orientation_classify=False, use_doc_unwarping=False,
        use_textline_orientation=False,
    )
    rows = []
    for image in images:
        started = time.monotonic()
        texts = []
        for result in engine.predict(str(image)):
            payload = result.json if hasattr(result, "json") else result
            if callable(payload):
                payload = payload()
            if isinstance(payload, str):
                payload = json.loads(payload)
            if isinstance(payload, dict):
                texts.extend(payload.get("res", {}).get("rec_texts", []))
        text = "\n".join(texts)
        (destination / (image.stem + ".txt")).write_text(text, encoding="utf-8")
        rows.append({"image": image.name, "seconds": round(time.monotonic() - started, 3),
                     "chars": len(text), "terms": terms(text),
                     "gate": gate_metrics(text), "text": text})
    return rows


def main() -> int:
    """Run the isolated benchmark and emit a JSON report with raw text paths."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--pages", required=True, help="comma-separated 1-indexed pages")
    parser.add_argument("--tessdata-fast", type=Path, required=True)
    parser.add_argument("--tessdata-best", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=300)
    args = parser.parse_args()
    pages = [int(value) for value in args.pages.split(",")]
    args.output.mkdir(parents=True, exist_ok=True)
    images = render(args.pdf, pages, args.output / "images", args.dpi)
    report = {"pdf": str(args.pdf), "pages": pages, "dpi": args.dpi,
              "engines": {}, "gold_text": False,
              "note": "CER/WER are intentionally absent: no human gold transcription was supplied."}
    for label, tessdata in (("tesseract_fast_psm3", args.tessdata_fast),
                            ("tesseract_best_psm3", args.tessdata_best)):
        rows = []
        for image in images:
            result = tesseract(image, args.output / label / image.stem, tessdata, 3)
            result.update({"image": image.name, "chars": len(result["text"]),
                           "terms": terms(result["text"]),
                           "gate": gate_metrics(result["text"])})
            rows.append(result)
            (args.output / label / (image.stem + ".txt")).write_text(result["text"], encoding="utf-8")
        report["engines"][label] = rows
    report["engines"]["paddleocr_ppocrv5_mobile_latin_cpu"] = paddle(images, args.output / "paddleocr")
    (args.output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"pages": len(images), "engines": list(report["engines"]),
                      "output": str(args.output), "gold_text": False}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
