"""Worker contract tests use an explicit model double, not an accuracy benchmark."""
import io
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image
import ocr_service as s


class WorkerContract(unittest.TestCase):
    def test_hybrid_worker_and_all_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job, runtime = root / "job", root / "runtime"
            job.mkdir()
            runtime.mkdir()
            source = job / "input"
            source.write_bytes(b"%PDF-test-double")
            s.atomic(job / "request.json", {"input_sha256": s.digest(source),
                     "kind": "pdf", "mode": "auto", "runtime_seal": "unit-test-double"})
            (runtime / "pipeline.yaml").write_text(
                "SubModules:\n  LayoutDetection: {}\n  VLRecognition: {}\n")
            image = root / "image.png"
            Image.new("RGB", (64, 64), "black").save(image)
            raw = {"parsing_res_list": [
                {"block_label": "text", "block_content": "NO PAGAR Bs20.000.000",
                 "block_bbox": [0, 0, 60, 20]},
                {"block_label": "footer", "block_content": "FINAL", "block_bbox": [0, 25, 60, 40]}]}

            class Double:
                def __init__(self, **kwargs):
                    self.configuration = kwargs

                def predict(self, *args, **kwargs):
                    return [types.SimpleNamespace(json=raw)]

            with patch.object(s, "verify_job_runtime", return_value={"models": [], "config_sha256": "double"}), \
                 patch.object(s, "prepare_pages", return_value=[
                     (1, "NATIVE PAGE", True, None), (2, "", False, image)]), \
                 patch.dict("sys.modules", {
                     "paddleocr": types.SimpleNamespace(PaddleOCRVL=Double),
                     "yaml": types.SimpleNamespace(safe_load=lambda _: {
                         "SubModules": {"LayoutDetection": {}, "VLRecognition": {}}})}):
                s.worker(job, runtime)
            result = s.read_json(job / "result.json")
            self.assertEqual(result["completed_pages"], 2)
            self.assertIn("NO PAGAR", result["text"])
            self.assertEqual(len(result["pages"][1]["blocks"]), 2)
            self.assertEqual(result["provenance"]["engine"], "PaddleOCR-VL-1.6")
            self.assertEqual(s.read_json(job / "raw-0002.json"), raw)
            self.assertFalse((job / "work").exists())

    def test_parser_pagewise_selection_and_txt_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            native = "Documento legal con contenido nativo verificable. " * 10

            def command(args, timeout=30):
                if "pdfinfo" in args[0]:
                    return "Pages: 2\nEncrypted: no\n"
                if "pdfimages" in args[0]:
                    return "page num type width height\n--------------------------\n"
                if "pdftotext" in args[0]:
                    return native if args[2] == "1" else ""
                Image.new("RGB", (64, 64), "black").save(args[-1] + ".png")
                return ""

            with patch.object(s, "run_command", side_effect=command):
                plan = s.prepare_pages(root / "input", "pdf", "auto", root)
                self.assertTrue(plan[0][2])
                self.assertFalse(plan[1][2])
                with self.assertRaisesRegex(ValueError, "native_text_not_usable"):
                    s.prepare_pages(root / "input", "pdf", "txt", root)
                plan = s.prepare_pages(root / "input", "pdf", "ocr", root)
                self.assertFalse(any(p[2] for p in plan))

    def test_parser_subprocess_errors(self):
        with patch.object(s.subprocess, "run", return_value=types.SimpleNamespace(returncode=1)):
            with self.assertRaisesRegex(ValueError, "parser_failed"):
                s.run_command(["test-double"])
        with patch.object(s.subprocess, "run", return_value=types.SimpleNamespace(
                returncode=0, stdout=b"x" * (1024 * 1024 + 1))):
            with self.assertRaisesRegex(ValueError, "parser_output_limit"):
                s.run_command(["test-double"])
        with patch.object(s.subprocess, "run", return_value=types.SimpleNamespace(
                returncode=0, stdout=b"valid")):
            self.assertEqual(s.run_command(["test-double"]), "valid")


if __name__ == "__main__":
    unittest.main()
