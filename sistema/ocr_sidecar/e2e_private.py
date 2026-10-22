#!/usr/bin/env python3
"""Real HTTP/model smoke test. Synthetic fixtures are NOT legal accuracy certification."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
import time

from PIL import Image, ImageDraw
from ocr_client import request


def pdf(pages):
    """Create a deterministic PDF with native or image-only pages, without extra libraries."""
    objects = [b"", b"<< /Type /Catalog /Pages 2 0 R >>", b""]
    page_ids = []
    for kind, payload in pages:
        page_id = len(objects)
        page_ids.append(page_id)
        objects.append(b"")
        content_id = len(objects)
        objects.append(b"")
        if kind == "image":
            image_id = len(objects)
            stream = io.BytesIO()
            payload.convert("RGB").save(stream, "JPEG", quality=95)
            data = stream.getvalue()
            objects.append((f"<< /Type /XObject /Subtype /Image /Width {payload.width} "
                            f"/Height {payload.height} /ColorSpace /DeviceRGB /BitsPerComponent 8 "
                            f"/Filter /DCTDecode /Length {len(data)} >>\nstream\n").encode()
                           + data + b"\nendstream")
            resources = f"<< /XObject << /Im0 {image_id} 0 R >> >>"
            content = b"q 288 0 0 108 0 0 cm /Im0 Do Q"
        else:
            resources = "<< /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >>"
            lines = payload.splitlines()
            content = b"BT /F1 7 Tf 10 98 Td 9 TL\n"
            for line in lines:
                escaped = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
                content += ("(" + escaped + ") Tj T*\n").encode("ascii")
            content += b"ET"
        objects[content_id] = f"<< /Length {len(content)} >>\nstream\n".encode() + content + b"\nendstream"
        objects[page_id] = (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 288 108] "
                            f"/Resources {resources} /Contents {content_id} 0 R >>").encode()
    kids = " ".join(f"{i} 0 R" for i in page_ids)
    objects[2] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode()
    result, offsets = b"%PDF-1.4\n", [0]
    for i, obj in enumerate(objects[1:], 1):
        offsets.append(len(result))
        result += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"
    xref = len(result)
    result += f"xref\n0 {len(objects)}\n0000000000 65535 f \n".encode()
    result += b"".join(f"{offset:010} 00000 n \n".encode() for offset in offsets[1:])
    result += (f"trailer << /Size {len(objects)} /Root 1 0 R >>\n"
               f"startxref\n{xref}\n%%EOF\n").encode()
    return result


def fixtures(root):
    """Write two-page scanned, hybrid and over-limit inputs with explicit reference strings."""
    images = []
    for lines in (["PRIMERA PAGINA", "Contrato de prueba."],
                  ["SEGUNDA PAGINA", "NO PAGAR Bs20.000.000"]):
        image = Image.new("RGB", (1200, 450), "white")
        draw = ImageDraw.Draw(image)
        for row, line in enumerate(lines):
            draw.text((60, 100 + row * 100), line, fill="black", font_size=42)
        images.append(image)
    native = "\n".join(["DOCUMENTO NATIVO DE PRUEBA"] +
                      ["La parte conserva derechos y obligaciones del contrato."] * 7)
    samples = {
        "scanned": (pdf([("image", im) for im in images]), "ocr", 2),
        "hybrid": (pdf([("native", native), ("image", images[1])]), "auto", 2),
        "overlimit": (pdf([("native", native)] * 5), "auto", None),
    }
    for name, (data, _, _) in samples.items():
        (root / (name + ".pdf")).write_bytes(data)
    return samples


def main():
    """Submit genuine jobs, preserve complete replies, and fail on page/negation/method loss."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--socket", default="/run/corpus-ocr/ocr.sock")
    parser.add_argument("--fixtures-only", action="store_true")
    args = parser.parse_args()
    args.root.mkdir(parents=True, exist_ok=True)
    samples = fixtures(args.root)
    if args.fixtures_only:
        return
    records = {}
    for name, (body, mode, count) in samples.items():
        status, admitted = request(args.socket, "POST", "/v1/jobs?mode=" + mode, body)
        assert status == 202, (status, admitted)
        records[name] = {"admitted": admitted, "input_sha256": hashlib.sha256(body).hexdigest()}
    (args.root / "submitted.json").write_text(json.dumps(records, indent=2))
    for name, (_, _, count) in samples.items():
        ident = records[name]["admitted"]["job"]
        deadline = time.monotonic() + 14400
        while time.monotonic() < deadline:
            status, state = request(args.socket, "GET", "/v1/jobs/" + ident)
            records[name]["state"] = state
            (args.root / "progress.json").write_text(json.dumps(records, indent=2))
            if state["status"] in ("failed", "interrupted", "requires_review"):
                break
            time.sleep(5)
        if count is None:
            assert state["status"] == "failed" and state["error"] == "page_limit", state
            continue
        assert state["status"] == "requires_review", state
        status, result = request(args.socket, "GET", "/v1/jobs/" + ident + "/result")
        (args.root / (name + "-result.json")).write_text(json.dumps(result, ensure_ascii=False, indent=2))
        assert status == 200 and result["completed_pages"] == count
        assert result["fidelity_certified"] is False
        assert "NO PAGAR" in result["pages"][1]["text"], result["pages"][1]["text"]
        assert "20.000.000" in result["pages"][1]["text"], result["pages"][1]["text"]
        expected = ["pdftotext", "PaddleOCR-VL-1.6"] if name == "hybrid" else ["PaddleOCR-VL-1.6"] * 2
        assert [p["method"] for p in result["pages"]] == expected
        records[name]["pass"] = True
    (args.root / "complete.json").write_text(json.dumps(records, ensure_ascii=False, indent=2))
    print(json.dumps({"pass": True, "scope": "private_service_synthetic_e2e",
                      "accuracy_certified": False, "jobs": records}))


if __name__ == "__main__":
    main()
