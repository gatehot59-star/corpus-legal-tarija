"""Contract and boundary tests; no model doubles are presented as OCR accuracy."""
import copy
import io
import json
import os
from pathlib import Path
import queue
import socket
import tempfile
import threading
import unittest
from unittest.mock import patch

import ocr_service as s


def page(number, text):
    return {"page": number, "status": s.REVIEW, "blank_by_pixels": False,
            "blocks": [{"index": 0, "label": "text", "text": text}], "text": text}


class ContractTests(unittest.TestCase):
    def test_complete_two_pages(self):
        result = s.complete_document([page(1, "UNO"), page(2, "NO PAGAR Bs 20.000.000")], 2)
        self.assertEqual(result["text"], "UNO\n\f\nNO PAGAR Bs 20.000.000")
        self.assertIn("page:2", result["markdown"])
        self.assertFalse(result["fidelity_certified"])

    def test_missing_page_mutation(self):
        with self.assertRaisesRegex(ValueError, "incomplete"):
            s.complete_document([page(1, "UNO")], 2)

    def test_reordered_page_mutation(self):
        with self.assertRaises(ValueError):
            s.complete_document([page(2, "DOS"), page(1, "UNO")], 2)

    def test_duplicate_page_mutation(self):
        with self.assertRaises(ValueError):
            s.complete_document([page(1, "UNO"), page(1, "DOS")], 2)

    def test_missing_block_mutation(self):
        value = page(1, "NO PAGAR")
        value["blocks"] = []
        with self.assertRaises(ValueError):
            s.complete_document([value], 1)

    def test_corrupted_text_mutation(self):
        value = page(1, "NO PAGAR")
        value["text"] = "PAGAR"
        with self.assertRaisesRegex(ValueError, "mismatch"):
            s.complete_document([value], 1)

    def test_block_order_mutation(self):
        value = page(1, "UNO")
        value["blocks"][0]["index"] = 2
        with self.assertRaisesRegex(ValueError, "block_order"):
            s.complete_document([value], 1)

    def test_incomplete_status(self):
        value = page(1, "UNO")
        value["status"] = "incomplete"
        with self.assertRaises(ValueError):
            s.complete_document([value], 1)

    def test_blank_is_explicit(self):
        blank = {"page": 1, "status": s.REVIEW, "text": "", "blocks": [],
                 "blank_by_pixels": True}
        self.assertEqual(s.complete_document([blank], 1)["completed_pages"], 1)

    def test_empty_document(self):
        with self.assertRaises(ValueError):
            s.complete_document([], 0)

    def test_all_blocks_including_html(self):
        raw = {"res": {"parsing_res_list": [
            {"block_label": "header", "block_content": "CABECERA"},
            {"block_label": "table", "block_content": "<table><tr><td>20</td></tr></table>"},
            {"block_label": "footer", "block_content": "PIE"}]}}
        result = s.blocks_from_raw(raw)
        self.assertEqual([b["index"] for b in result], [0, 1, 2])
        self.assertEqual(result[1]["text"], raw["res"]["parsing_res_list"][1]["block_content"])
        self.assertEqual(s.blocks_from_raw(json.dumps(raw)), result)

    def test_missing_raw_or_nontext(self):
        for value in ({}, {"parsing_res_list": [{"block_content": None}]}):
            with self.assertRaises(ValueError):
                s.blocks_from_raw(value)

    def test_ley151_reference(self):
        fragments = ["Bs20.000.000", "(Bolivianos veinte millones 00/100) provenientes de las Regalías que percibe",
                     "el Departamento por concepto de explotación de Hidrocarburos."]
        correct = "\n".join(fragments)
        self.assertTrue(s.check_reference(correct, fragments)["pass"])
        broken = "I. El (FOPEDT) estará financiado con un capital inicial de Bs20.000.000.000.0"
        self.assertFalse(s.check_reference(broken, fragments)["pass"])
        self.assertTrue(s.legal_alerts(broken))
        self.assertFalse(s.legal_alerts("Bs20.000.000"))

    def test_negation_and_amount_mutations(self):
        reference = ["NO AUTORIZADO", "Bs20.000.000,"]
        positive = "NO AUTORIZADO Bs20.000.000, fin."
        self.assertTrue(s.check_reference(positive, reference)["pass"])
        for mutant in (positive.replace("NO ", ""), positive.replace("20.000.000", "200.000.000")):
            self.assertFalse(s.check_reference(mutant, reference)["pass"])

    def test_native_heuristic(self):
        self.assertTrue(s.eligible_native("Documento jurídico de prueba con texto. " * 12))
        for text in ("", "1234" * 100, "palabras " * 40 + "\ufffd"):
            self.assertFalse(s.eligible_native(text))

    def test_magic_allowlist(self):
        for header, expected in [(b"%PDF-1.4", "pdf"), (b"\x89PNG\r\n\x1a\n", "png"),
                                 (b"\xff\xd8\xff", "jpeg"), (b"II*\0", "tiff")]:
            self.assertEqual(s.input_kind(header), expected)
        with self.assertRaises(ValueError):
            s.input_kind(b"malware with image/png MIME")

    def test_atomic_and_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "result.json"
            s.atomic(path, {"x": "á"})
            self.assertEqual(s.read_json(path), {"x": "á"})
            self.assertEqual(len(s.digest(path)), 64)
            self.assertFalse(path.with_suffix(".json.new").exists())


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.jobs = object.__new__(s.Jobs)
        self.jobs.root = Path(self.temp.name)
        self.jobs.lock = threading.Lock()
        self.jobs.queue = queue.Queue(maxsize=1)

    def test_valid_queue(self):
        body = b"%PDF-1.4 test"
        ident = self.jobs.admit(io.BytesIO(body), len(body), "ocr")
        self.assertEqual(s.read_json(self.jobs.root / ident / "state.json")["status"], "queued")
        self.assertEqual((self.jobs.root / ident / "input").read_bytes(), body)

    def test_failed_copy_cleanup(self):
        with self.assertRaises(ValueError):
            self.jobs.admit(io.BytesIO(b"%PDF-"), 20, "ocr")
        self.assertEqual(list(self.jobs.root.iterdir()), [])

    def test_invalid_magic_cleanup(self):
        with self.assertRaises(ValueError):
            self.jobs.admit(io.BytesIO(b"hello"), 5, "auto")
        self.assertEqual(list(self.jobs.root.iterdir()), [])

    def test_queue_full(self):
        self.jobs.queue.put("occupied")
        with self.assertRaises(OverflowError):
            self.jobs.admit(io.BytesIO(b"%PDF-"), 5, "ocr")
        self.assertEqual(list(self.jobs.root.iterdir()), [])


class HttpTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.jobs = object.__new__(s.Jobs)
        self.jobs.root = self.root / "jobs"
        self.jobs.root.mkdir()
        self.jobs.lock = threading.Lock()
        self.jobs.queue = queue.Queue(maxsize=4)
        self.jobs.ready = lambda: True
        self.sock = self.root / "socket"
        self.server = s.Server(str(self.sock), self.jobs)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop)

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def request(self, method, path, body=b"", headers=""):
        connection = socket.socket(socket.AF_UNIX)
        connection.settimeout(5)
        connection.connect(str(self.sock))
        request = (f"{method} {path} HTTP/1.0\r\nHost: local\r\n"
                   f"Content-Length: {len(body)}\r\n{headers}\r\n").encode() + body
        connection.sendall(request)
        response = s.http.client.HTTPResponse(connection)
        response.begin()
        status, data = response.status, json.loads(response.read())
        connection.close()
        return status, data

    def test_liveness_readiness(self):
        self.assertEqual(self.request("GET", "/live")[0], 200)
        self.assertEqual(self.request("GET", "/ready")[0], 200)
        self.jobs.ready = lambda: False
        self.assertEqual(self.request("GET", "/ready")[0], 503)
        self.assertEqual(self.request("POST", "/v1/jobs", b"%PDF-")[0], 503)

    def test_auth_rejection(self):
        with patch.object(s.Handler, "authorized", return_value=False):
            self.assertEqual(self.request("GET", "/live")[0], 403)
            self.assertEqual(self.request("POST", "/v1/jobs", b"%PDF-")[0], 403)

    def test_mode_and_parameter_rejection(self):
        for path in ("/v1/jobs?mode=bad", "/v1/jobs?mode=ocr&mode=auto", "/v1/jobs?path=/etc/passwd"):
            self.assertEqual(self.request("POST", path, b"%PDF-")[0], 400)

    def test_invalid_magic_rejected(self):
        self.assertEqual(self.request("POST", "/v1/jobs", b"not a pdf",
                                      "Content-Type: application/pdf\r\n")[0], 400)

    def test_post_and_incomplete_result(self):
        status, data = self.request("POST", "/v1/jobs?mode=ocr", b"%PDF-1.4")
        self.assertEqual(status, 202)
        self.assertEqual(self.request("GET", data["status_url"])[1]["status"], "queued")
        self.assertEqual(self.request("GET", data["result_url"])[0], 409)
        result = s.complete_document([page(1, "UNO")], 1)
        job = self.jobs.root / data["job"]
        s.atomic(job / "state.json", {"status": s.REVIEW})
        s.atomic(job / "result.json", result)
        self.assertEqual(self.request("GET", data["result_url"])[1]["text"], "UNO")

    def test_traversal_and_unknown_routes(self):
        for path in ("/v1/jobs/../../etc/passwd", "/missing", "/v1/jobs/" + "f"*32,
                     "/live?x=1"):
            self.assertIn(self.request("GET", path)[0], (400, 404))

    def test_transfer_encoding_and_duplicate_length(self):
        for headers in ("Transfer-Encoding: chunked\r\n", "Content-Length: 1\r\n"):
            self.assertEqual(self.request("POST", "/v1/jobs", b"%PDF-", headers)[0], 411)

    def test_empty_body(self):
        self.assertEqual(self.request("POST", "/v1/jobs")[0], 413)


if __name__ == "__main__":
    unittest.main(verbosity=2)
