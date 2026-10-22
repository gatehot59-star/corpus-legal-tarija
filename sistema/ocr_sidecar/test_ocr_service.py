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
import time
import subprocess
import sys
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

    def test_amount_prefix_is_not_equal(self):
        self.assertTrue(s.check_reference("Bs20.000.000", ["Bs20.000.000"])["pass"])
        self.assertFalse(s.check_reference("Bs20.000.000.000.0", ["Bs20.000.000"])["pass"])

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
        self.jobs.ready = lambda: True
        self.jobs.runtime_seal = "test_double_not_a_runtime"

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

    def test_direct_limits(self):
        for size, mode in [(0, "ocr"), (s.MAX_BYTES + 1, "ocr"), (5, "wrong")]:
            with self.assertRaises(ValueError):
                self.jobs.admit(io.BytesIO(b"%PDF-"), size, mode)
        self.jobs.ready = lambda: False
        with self.assertRaises(ValueError):
            self.jobs.admit(io.BytesIO(b"%PDF-"), 5, "ocr")


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "pipeline.yaml").write_text("test")
        self.manifest = []
        for repo, (folder, revision) in s.MODEL_REVISIONS.items():
            directory = self.root / "models" / folder
            directory.mkdir(parents=True)
            (directory / "weights").write_bytes(b"test-model-fixture")
            self.manifest.append({"repo": repo, "revision": revision,
                                  "files": [{"path": "weights", "sha256": s.digest(directory / "weights")}]})
        s.atomic(self.root / "models.json", self.manifest)
        self.pins = patch.object(s.importlib.metadata, "version", side_effect=lambda n: s.PINS[n])
        self.pins.start()
        self.addCleanup(self.pins.stop)

    def test_valid_and_changed_model(self):
        initial = s.verify_runtime(self.root)
        request = {"runtime_seal": s.canonical_hash(initial)}
        self.assertEqual(s.verify_job_runtime(self.root, request), initial)
        target = self.root / "models/vl/weights"
        st = target.stat()
        target.write_bytes(b"evil-model-fixture")
        os.utime(target, ns=(st.st_atime_ns, st.st_mtime_ns))
        with self.assertRaisesRegex(ValueError, "model_hash"):
            s.verify_job_runtime(self.root, request)

    def test_changed_config_same_stat(self):
        initial = s.verify_runtime(self.root)
        path = self.root / "pipeline.yaml"
        st = path.stat()
        path.write_text("evil")
        os.utime(path, ns=(st.st_atime_ns, st.st_mtime_ns))
        with self.assertRaisesRegex(ValueError, "runtime_changed"):
            s.verify_job_runtime(self.root, {"runtime_seal": s.canonical_hash(initial)})

    def test_paths_and_revisions(self):
        for name in ("/etc/passwd", "../weights", "sub/../../weights"):
            manifest = copy.deepcopy(self.manifest)
            manifest[0]["files"][0]["path"] = name
            with self.assertRaises(ValueError):
                s.model_paths(self.root, manifest)
        manifest = copy.deepcopy(self.manifest)
        manifest[0]["revision"] = "wrong"
        with self.assertRaises(ValueError):
            s.model_paths(self.root, manifest)
        with self.assertRaises(ValueError):
            s.model_paths(self.root, [self.manifest[0]] * 2)

    def test_symlink_file_and_parent(self):
        folder = self.root / "models/vl"
        (folder / "link").symlink_to(folder / "weights")
        manifest = copy.deepcopy(self.manifest)
        manifest[0]["files"][0]["path"] = "link"
        with self.assertRaisesRegex(ValueError, "symlink"):
            s.model_paths(self.root, manifest)
        (folder / "dirlink").symlink_to(folder, target_is_directory=True)
        manifest[0]["files"][0]["path"] = "dirlink/weights"
        with self.assertRaisesRegex(ValueError, "symlink"):
            s.model_paths(self.root, manifest)

    def test_package_pin(self):
        with patch.object(s.importlib.metadata, "version", return_value="wrong"):
            with self.assertRaisesRegex(ValueError, "package_pin"):
                s.verify_runtime(self.root)

    def test_restart_interrupts_old_jobs(self):
        state = self.root / "state"
        job = state / ("a" * 32)
        job.mkdir(parents=True)
        s.atomic(job / "state.json", {"status": "running"})
        jobs = s.Jobs(state, self.root)
        self.addCleanup(lambda: setattr(jobs, "stopping", True))
        self.assertEqual(s.read_json(job / "state.json")["status"], "interrupted")
        self.assertTrue(jobs.ready())
        path = self.root / "pipeline.yaml"
        st = path.stat()
        path.write_text("evil")
        os.utime(path, ns=(st.st_atime_ns, st.st_mtime_ns))
        self.assertFalse(jobs.ready())

    def test_block_schema(self):
        valid = {"block_label": "text", "block_content": "UNO", "block_bbox": [0, 1, 20, 30]}
        self.assertEqual(s.blocks_from_raw({"parsing_res_list": [valid]})[0]["bbox"], [0, 1, 20, 30])
        for key, value in [("block_label", None), ("block_bbox", [1, 2]),
                           ("block_bbox", [0, 0, float("nan"), 1]),
                           ("block_bbox", [10, 0, 1, 3]), ("block_bbox", [-1, 0, 1, 3])]:
            block = dict(valid, **{key: value})
            with self.assertRaises(ValueError):
                s.blocks_from_raw({"parsing_res_list": [block]})


class ParserTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_tiff_all_pages_and_page_limit(self):
        from PIL import Image
        images = [Image.new("RGB", (64, 32), color) for color in ("red", "green", "blue", "black", "white")]
        source = self.root / "input.tiff"
        images[0].save(source, save_all=True, append_images=images[1:2])
        self.assertEqual(len(s.prepare_pages(source, "tiff", "ocr", self.root)), 2)
        images[0].save(source, save_all=True, append_images=images[1:])
        with self.assertRaisesRegex(ValueError, "page_limit"):
            s.prepare_pages(source, "tiff", "ocr", self.root)

    def test_truncated_image_and_pixels(self):
        from PIL import Image
        source = self.root / "input.png"
        source.write_bytes(b"\x89PNG\r\n\x1a\nbroken")
        with self.assertRaises(Exception):
            s.prepare_pages(source, "png", "ocr", self.root)
        Image.new("RGB", (100, 100), "white").save(source)
        with patch.object(s, "MAX_PIXELS", 100):
            with self.assertRaises(Exception):
                s.prepare_pages(source, "png", "ocr", self.root)

    def test_pdf_limits_and_encryption(self):
        for text, error in [("Pages: 5\n", "page_limit"),
                            ("Pages: 1\nEncrypted: yes\n", "encrypted_pdf")]:
            with patch.object(s, "run_command", return_value=text):
                with self.assertRaisesRegex(ValueError, error):
                    s.prepare_pages(self.root / "input", "pdf", "auto", self.root)

    def test_txt_rejects_image(self):
        with self.assertRaisesRegex(ValueError, "txt_requires_pdf"):
            s.prepare_pages(self.root / "input", "png", "txt", self.root)


class SupervisorTests(unittest.TestCase):
    def test_timeout_kills_process_group(self):
        with tempfile.TemporaryDirectory() as tmp:
            jobs = object.__new__(s.Jobs)
            jobs.root, jobs.runtime = Path(tmp), Path(tmp)
            jobs.timeout, jobs.stopping, jobs.failure = .2, False, None
            jobs.queue = queue.Queue()
            ident = "a" * 32
            job = jobs.root / ident
            job.mkdir()
            created = []
            real_popen = subprocess.Popen

            def fake_worker(*args, **kwargs):
                code = ("import subprocess,sys,time; "
                        "p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)']); "
                        "print(p.pid,flush=True); time.sleep(60)")
                process = real_popen([sys.executable, "-c", code], **kwargs)
                created.append(process)
                return process

            with patch.object(s.subprocess, "Popen", side_effect=fake_worker):
                thread = threading.Thread(target=jobs.loop, daemon=True)
                thread.start()
                jobs.queue.put(ident)
                jobs.queue.join()
                jobs.stopping = True
                thread.join(2)
            state = s.read_json(job / "state.json")
            self.assertEqual(state["error"], "timeout")
            self.assertEqual(created[0].poll(), -9)
            child = int((job / "worker.log").read_text().strip())
            stat = Path(f"/proc/{child}/stat")
            self.assertTrue(not stat.exists() or stat.read_text().split()[2] == "Z")


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
        self.jobs.runtime_seal = "test_double_not_a_runtime"
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
