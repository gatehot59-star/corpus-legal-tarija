#!/usr/bin/env python3
"""Local-only Corpus OCR sidecar. No network listener, no corpus database writes."""
from __future__ import annotations

import argparse
import datetime
import hashlib
import http.client
import http.server
import importlib.metadata
import json
import math
import os
from pathlib import Path
import queue
import re
import resource
import shutil
import signal
import socket
import socketserver
import struct
import subprocess
import sys
import threading
import time
import uuid
from urllib.parse import parse_qs, urlsplit

MAX_BYTES = 20 * 1024 * 1024
MAX_PAGES = 4
MAX_PIXELS = 24_000_000
MAX_JOBS = 64
MAX_QUEUE = 4
JOB_TIMEOUT = 7200
RETENTION = 86400
PINS = {"paddleocr": "3.7.0", "paddlex": "3.7.2", "paddlepaddle": "3.3.1",
        "Pillow": "13.0.0"}
MODES = {"auto", "ocr", "txt"}
REVIEW = "requires_review"
ID_PATTERN = re.compile(r"^[0-9a-f]{32}$")
MODEL_REVISIONS = {
    "PaddlePaddle/PaddleOCR-VL-1.6": ("vl", "c5630abae1d940eafe0697512a0325494b02ab42"),
    "PaddlePaddle/PP-DocLayoutV3": ("layout", "241f8bdfc77a7c7bee915a5057aaee58c235a8d3"),
}


def canonical_hash(value):
    """Hash the effective JSON configuration, not its pre-rewrite YAML template."""
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    allow_nan=False, separators=(",", ":")).encode()).hexdigest()


def now():
    """Return an explicitly zoned UTC timestamp."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def digest(path):
    """Hash an input without loading model files into RAM."""
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def atomic(path, value):
    """Replace only an owned JSON output, never a source document."""
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".new")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, allow_nan=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(path)


def read_json(path):
    """Read a bounded server-owned JSON record."""
    if Path(path).stat().st_size > 16 * 1024 * 1024:
        raise ValueError("record_too_large")
    return json.loads(Path(path).read_text())


def input_kind(header):
    """Accept a narrow signature allowlist; parsers validate the full content."""
    if header.startswith(b"%PDF-"):
        return "pdf"
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if header.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if header.startswith((b"II*\0", b"MM\0*")):
        return "tiff"
    raise ValueError("unsupported_file_signature")


def eligible_native(text):
    """Conservative text-layer heuristic, never a certificate of correctness."""
    chars = [c for c in text if not c.isspace()]
    if len(chars) < 200 or "\ufffd" in text:
        return False
    return (sum(c.isalpha() for c in chars) / len(chars) >= .5
            and sum(c.isprintable() for c in chars) / len(chars) > .99)


def legal_alerts(text):
    """Flag suspect monetary formatting without correcting the legal source."""
    alerts = []
    for m in re.finditer(r"\bBs\.?\s*([0-9][0-9.,]*)", text, re.I):
        amount = m.group(1)
        if not re.fullmatch(r"(?:\d+|\d{1,3}(?:\.\d{3})+)(?:,\d{1,2})?", amount):
            alerts.append({"kind": "ambiguous_amount_format", "literal": m.group(0)})
    return alerts


def check_reference(text, expected):
    """Verify explicit anchored reference fragments; not a general OCR oracle."""
    absent = [fragment for fragment in expected
              if not re.search(r"(?<!\w)" + re.escape(fragment) + r"(?!\w|[.,]\d)", text)]
    return {"pass": not absent, "missing": absent}


def blocks_from_raw(raw):
    """Preserve every parsing block and native order, including table markup."""
    if isinstance(raw, str):
        raw = json.loads(raw)
    if not isinstance(raw, dict):
        raise ValueError("invalid_raw")
    obj = raw.get("res", raw)
    if not isinstance(obj, dict) or not isinstance(obj.get("parsing_res_list"), list):
        raise ValueError("missing_parsing_blocks")
    blocks = []
    for i, block in enumerate(obj["parsing_res_list"]):
        if not isinstance(block, dict):
            raise ValueError("invalid_block")
        content = block.get("block_content")
        if not isinstance(content, str):
            raise ValueError("invalid_block_text")
        label, bbox = block.get("block_label"), block.get("block_bbox")
        if not isinstance(label, str) or not label or len(label) > 128:
            raise ValueError("invalid_block_label")
        # Missing geometry is explicit, never invented. Present geometry is bounded.
        if bbox is not None:
            if (not isinstance(bbox, (list, tuple)) or len(bbox) != 4
                    or any(type(v) not in (int, float) or not math.isfinite(v)
                           or not 0 <= v <= MAX_PIXELS for v in bbox)
                    or bbox[0] > bbox[2] or bbox[1] > bbox[3]):
                raise ValueError("invalid_block_bbox")
        blocks.append({"index": i, "label": label,
                       "text": content, "bbox": bbox,
                       "source_block_id": block.get("block_id"),
                       "source_order": block.get("block_order")})
    return blocks


def complete_document(pages, expected):
    """Enforce page presence, order, block continuity and explicit review status."""
    if not expected or len(pages) != expected:
        raise ValueError("incomplete_document")
    if [p["page"] for p in pages] != list(range(1, expected + 1)):
        raise ValueError("page_order_or_duplicate")
    for page in pages:
        if page.get("status") != REVIEW:
            raise ValueError("page_not_completed")
        blocks = page["blocks"]
        if [b["index"] for b in blocks] != list(range(len(blocks))):
            raise ValueError("block_order")
        if (not blocks or not any(b["text"].strip() for b in blocks)) and not page.get("blank_by_pixels", False):
            raise ValueError("empty_nonblank_output")
        if page["text"] != "\n".join(b["text"] for b in blocks):
            raise ValueError("block_text_mismatch")
    return {"schema": "corpus-ocr/1", "status": REVIEW,
            "expected_pages": expected, "completed_pages": len(pages),
            "pages": pages, "text": "\n\f\n".join(p["text"] for p in pages),
            "markdown": "\n\n".join(
                f"<!-- page:{p['page']} -->\n" + p["text"] for p in pages),
            "fidelity_certified": False}


def validate_result(result):
    """Reject a worker envelope inconsistent with its validated pages."""
    try:
        if not isinstance(result, dict):
            raise ValueError("invalid_worker_result")
        expected = result["expected_pages"]
        if type(expected) is not int or not 1 <= expected <= MAX_PAGES:
            raise ValueError("invalid_worker_result")
        canonical = complete_document(result["pages"], expected)
        for key in ("schema", "status", "expected_pages", "completed_pages",
                    "text", "markdown", "fidelity_certified"):
            if type(result[key]) is not type(canonical[key]) or result[key] != canonical[key]:
                raise ValueError("invalid_worker_result")
    except (ValueError, KeyError, TypeError, AttributeError):
        raise ValueError("invalid_worker_result") from None
    return result


def terminal_progress(job, status, error=None, result=None):
    """Finalize progress without hiding a failure or counting unvalidated pages."""
    expected, completed = None, 0
    if result is not None:
        expected, completed = result["expected_pages"], result["completed_pages"]
    else:
        try:
            partial = read_json(job / "partial.json")
            count = partial["expected_pages"]
            pages = partial["pages"]
            if type(count) is int and 1 <= count <= MAX_PAGES and isinstance(pages, list):
                expected = count
                if 0 < len(pages) <= count:
                    complete_document(pages, len(pages))
                    completed = len(pages)
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            pass
    atomic(job / "progress.json", {
        "phase": "completed" if status == REVIEW else "failed",
        "expected_pages": expected, "completed_pages": completed,
        "error": error, "updated_utc": now()})


def run_command(args, timeout=30):
    """Bound a parser subprocess and discard its potentially sensitive errors."""
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            timeout=timeout, check=False)
    if result.returncode:
        raise ValueError("parser_failed")
    if len(result.stdout) > 1024 * 1024:
        raise ValueError("parser_output_limit")
    return result.stdout.decode("utf-8", errors="strict")


def page_has_raster(source, page):
    """Use Poppler's decoded image inventory; fail closed on unknown output."""
    listing = run_command(["/usr/bin/pdfimages", "-f", str(page), "-l", str(page),
                           "-list", str(source)])
    lines = [line.strip() for line in listing.splitlines() if line.strip()]
    if len(lines) < 2 or not re.match(r"page\s+num\s+type\b", lines[0]):
        raise ValueError("invalid_image_inventory")
    if not re.fullmatch(r"-+", lines[1]):
        raise ValueError("invalid_image_inventory")
    for line in lines[2:]:
        if not re.match(r"\d+\s+\d+\s+(?:image|mask|smask)\s", line):
            raise ValueError("invalid_image_inventory")
    return bool(lines[2:])


def prepare_pages(source, kind, mode, work):
    """Materialize each page separately; never trust a document-wide text average."""
    from PIL import Image, ImageSequence
    Image.MAX_IMAGE_PIXELS = MAX_PIXELS
    pages = []
    if kind == "pdf":
        info = run_command(["/usr/bin/pdfinfo", str(source)])
        match = re.search(r"^Pages:\s+(\d+)", info, re.M)
        count = int(match.group(1)) if match else 0
        if not 1 <= count <= MAX_PAGES:
            raise ValueError("page_limit")
        if re.search(r"^Encrypted:\s+yes", info, re.M):
            raise ValueError("encrypted_pdf")
        for page in range(1, count + 1):
            native = ""
            if mode != "ocr":
                native = run_command(["/usr/bin/pdftotext", "-f", str(page),
                                      "-l", str(page), "-enc", "UTF-8",
                                      str(source), "-"])
            # Any raster can contain a clause or signature. Do not silently prefer
            # a long native layer over it. Native text remains separately preserved.
            native_ok = eligible_native(native)
            if native_ok and page_has_raster(source, page):
                native_ok = False
            if mode == "txt" and not native_ok:
                raise ValueError("native_text_not_usable")
            image_path = None
            if mode == "ocr" or not native_ok:
                prefix = work / f"page-{page:04d}"
                run_command(["/usr/bin/pdftoppm", "-f", str(page), "-l", str(page),
                             "-singlefile", "-r", "300", "-scale-to", "5000",
                             "-gray", "-png", str(source), str(prefix)], timeout=60)
                image_path = prefix.with_suffix(".png")
            pages.append((page, native, native_ok and mode != "ocr", image_path))
    else:
        if mode == "txt":
            raise ValueError("txt_requires_pdf")
        with Image.open(source) as image:
            if getattr(image, "n_frames", 1) > MAX_PAGES:
                raise ValueError("page_limit")
            for number, frame in enumerate(ImageSequence.Iterator(image), 1):
                if number > MAX_PAGES:
                    raise ValueError("page_limit")
                if frame.width * frame.height > MAX_PIXELS:
                    raise ValueError("pixel_limit")
                frame.load()
                image_path = work / f"page-{number:04d}.png"
                frame.convert("RGB").save(image_path)
                pages.append((number, "", False, image_path))
    for _, _, _, image_path in pages:
        if image_path:
            with Image.open(image_path) as image:
                if image.width * image.height > MAX_PIXELS:
                    raise ValueError("pixel_limit")
                image.verify()
    if not pages:
        raise ValueError("no_pages")
    return pages


def model_paths(root, sealed):
    """Confine every sealed relative file to an exact model revision, without symlinks."""
    if not isinstance(sealed, list) or len(sealed) != len(MODEL_REVISIONS):
        raise ValueError("invalid_model_manifest")
    seen, paths = set(), []
    for model in sealed:
        repo = model.get("repo")
        if repo not in MODEL_REVISIONS or repo in seen:
            raise ValueError("invalid_model_manifest")
        seen.add(repo)
        folder, revision = MODEL_REVISIONS[repo]
        if model.get("revision") != revision or not model.get("files"):
            raise ValueError("invalid_model_revision")
        base = Path(root) / "models" / folder
        entries = set()
        for entry in model["files"]:
            relative = Path(entry["path"])
            if (relative.is_absolute() or ".." in relative.parts or not relative.parts
                    or str(relative) in entries
                    or not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"])):
                raise ValueError("unsafe_model_path")
            entries.add(str(relative))
            path = base / relative
            for component in (path, *path.parents):
                if component.is_symlink():
                    raise ValueError("unsafe_model_symlink")
            if not path.resolve().is_relative_to(base.resolve()) or not path.is_file():
                raise ValueError("unsafe_model_path")
            paths.append((path, entry["sha256"]))
    return paths


def verify_runtime(root):
    """Verify pinned packages and all sealed model files before admitting jobs."""
    for name, version in PINS.items():
        if importlib.metadata.version(name) != version:
            raise ValueError("package_pin_mismatch:" + name)
    for tool in ("pdfinfo", "pdftotext", "pdftoppm", "pdfimages"):
        if not Path("/usr/bin", tool).is_file():
            raise ValueError("missing_parser")
    sealed = read_json(root / "models.json")
    for path, expected in model_paths(root, sealed):
        if digest(path) != expected:
            raise ValueError("model_hash_mismatch")
    return {"packages": PINS, "models": [
        {"repo": m["repo"], "revision": m["revision"]} for m in sealed],
        "manifest_sha256": digest(root / "models.json"),
        "config_sha256": digest(root / "pipeline.yaml")}


def verify_job_runtime(runtime, request):
    """Rehash the installed models immediately before each job, against its admission seal."""
    installation = verify_runtime(runtime)
    if canonical_hash(installation) != request["runtime_seal"]:
        raise ValueError("runtime_changed")
    return installation


def worker(job, runtime):
    """Run one isolated job, preserving raw output and loading VL only when needed."""
    from PIL import Image, ImageDraw
    import yaml
    start = time.monotonic()
    resource.setrlimit(resource.RLIMIT_FSIZE, (64 * 1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_NOFILE, (256, 256))
    request = read_json(job / "request.json")
    installation = verify_job_runtime(runtime, request)
    source = job / "input"
    if digest(source) != request["input_sha256"]:
        raise ValueError("input_changed")
    work = job / "work"
    work.mkdir(mode=0o700, exist_ok=True)
    pages = []
    try:
        t = time.monotonic()
        plan = prepare_pages(source, request["kind"], request["mode"], work)
        preparation = time.monotonic() - t
        atomic(job / "progress.json", {"phase": "prepared", "expected_pages": len(plan),
                                       "completed_pages": 0})
        pipeline = None
        load_seconds = warmup_seconds = 0.0
        configuration = yaml.safe_load((runtime / "pipeline.yaml").read_text())
        for name, folder in (("LayoutDetection", "layout"), ("VLRecognition", "vl")):
            configuration["SubModules"][name]["model_dir"] = str(runtime / "models" / folder)
        if any(not native for _, _, native, _ in plan):
            atomic(job / "progress.json", {"phase": "loading", "expected_pages": len(plan),
                                           "completed_pages": 0})
            from paddleocr import PaddleOCRVL
            t = time.monotonic()
            pipeline = PaddleOCRVL(pipeline_version="v1.6", paddlex_config=configuration,
                                   device="cpu", cpu_threads=1, enable_mkldnn=False)
            load_seconds = time.monotonic() - t
            warm = Image.new("RGB", (600, 120), "white")
            ImageDraw.Draw(warm).text((20, 30), "Prueba OCR 123", fill="black", font_size=24)
            warm.save(work / "warmup.png")
            t = time.monotonic()
            list(pipeline.predict(str(work / "warmup.png"), max_new_tokens=128))
            warmup_seconds = time.monotonic() - t
        for number, native_text, native, image_path in plan:
            atomic(job / "progress.json", {"phase": "extraction", "page": number,
                                           "expected_pages": len(plan), "completed_pages": len(pages),
                                           "model_loaded": pipeline is not None})
            t = time.monotonic()
            blank = False
            if native:
                blocks = [{"index": 0, "label": "native_text", "text": native_text}]
                method = "pdftotext"
            else:
                with Image.open(image_path) as im:
                    blank = im.convert("L").getextrema() == (255, 255)
                if blank:
                    blocks = []
                else:
                    results = list(pipeline.predict(str(image_path), max_new_tokens=4096))
                    if len(results) != 1:
                        raise ValueError("unexpected_page_result_count")
                    raw = results[0].json
                    if isinstance(raw, str):
                        raw = json.loads(raw)
                    atomic(job / f"raw-{number:04d}.json", raw)
                    blocks = blocks_from_raw(raw)
                method = "PaddleOCR-VL-1.6"
            text = "\n".join(b["text"] for b in blocks)
            page = {"page": number, "status": REVIEW, "method": method,
                    "selection_reason": ("native_text_heuristic_not_fidelity" if native
                                         else "forced_ocr" if request["mode"] == "ocr"
                                         else "native_with_raster_requires_ocr" if eligible_native(native_text)
                                         else "native_missing_or_rejected"),
                    "native_text": native_text, "blocks": blocks, "text": text,
                    "text_sha256": hashlib.sha256(text.encode()).hexdigest(),
                    "blank_by_pixels": blank, "alerts": legal_alerts(text),
                    "extraction_seconds": time.monotonic() - t,
                    "image_sha256": digest(image_path) if image_path else None}
            pages.append(page)
            atomic(job / "partial.json", {"status": "incomplete", "pages": pages,
                                         "expected_pages": len(plan), "fidelity_certified": False})
        if digest(source) != request["input_sha256"]:
            raise ValueError("input_changed")
        result = complete_document(pages, len(plan))
        result["provenance"] = {
            "source_sha256": request["input_sha256"], "mode": request["mode"],
            "engine": "PaddleOCR-VL-1.6" if pipeline else "pdftotext",
            "device": "cpu" if pipeline else None, "packages": PINS,
            "configuration": configuration,
            "effective_configuration_sha256": canonical_hash(configuration),
            "template_configuration_sha256": installation["config_sha256"],
            "runtime_seal": request["runtime_seal"],
            "models": installation["models"],
            "code_sha256": digest(__file__), "completed_utc": now(),
            "timings": {"preparation_seconds": preparation, "load_seconds": load_seconds,
                        "warmup_seconds": warmup_seconds,
                        "extraction_sum_seconds": sum(p["extraction_seconds"] for p in pages),
                        "worker_wall_seconds": time.monotonic() - start}}
        atomic(job / "result.json", result)
        terminal_progress(job, REVIEW, result=result)
    finally:
        # Only the job's transient images are removed, never the submitted source.
        shutil.rmtree(work, ignore_errors=True)


class Jobs:
    """Single bounded execution queue with durable states and deadline enforcement."""
    def __init__(self, root, runtime, timeout=JOB_TIMEOUT):
        self.root, self.runtime, self.timeout = Path(root), Path(runtime), timeout
        self.root.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self.queue = queue.Queue(maxsize=MAX_QUEUE)
        self.failure = None
        self.stopping = False
        self.installation = verify_runtime(self.runtime)
        self.runtime_seal = canonical_hash(self.installation)
        self.config_stat = self.identity(self.runtime / "pipeline.yaml")
        self.model_stats = {str(p): self.identity(p) for p, _ in model_paths(
            self.runtime, read_json(self.runtime / "models.json"))}
        self.model_stats[str(self.runtime / "models.json")] = self.identity(self.runtime / "models.json")
        for directory in self.root.iterdir():
            if directory.is_dir() and ID_PATTERN.fullmatch(directory.name):
                state_path = directory / "state.json"
                if not state_path.exists() or read_json(state_path)["status"] in ("running", "queued"):
                    atomic(state_path, {"status": "interrupted", "error": "service_restarted",
                                        "updated_utc": now()})
                    shutil.rmtree(directory / "work", ignore_errors=True)
        self.thread = threading.Thread(target=self.loop, daemon=True)
        self.thread.start()

    @staticmethod
    def identity(path):
        """Detect runtime replacement after initial full hash validation."""
        s = Path(path).stat()
        return (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)

    def ready(self):
        """Report launch readiness, not a continuously resident/warmed model."""
        try:
            unchanged = self.identity(self.runtime / "pipeline.yaml") == self.config_stat
            unchanged &= all(self.identity(p) == value for p, value in self.model_stats.items())
            return unchanged and self.thread.is_alive() and not self.failure and not self.stopping
        except OSError:
            return False

    def expire(self):
        """Remove only terminal sidecar jobs after the documented retention period."""
        for path in self.root.iterdir():
            if not ID_PATTERN.fullmatch(path.name) or not path.is_dir() or path.is_symlink():
                continue
            state = path / "state.json"
            if state.exists() and time.time() - state.stat().st_mtime > RETENTION:
                if read_json(state)["status"] not in ("running", "queued"):
                    shutil.rmtree(path)

    def admit(self, stream, length, mode):
        """Copy a bounded body inside cleanup protection and admit only complete uploads."""
        with self.lock:
            if mode not in MODES or not 0 < length <= MAX_BYTES:
                raise ValueError("invalid_request")
            if not self.ready():
                raise ValueError("runtime_unavailable")
            self.expire()
            if self.queue.full() or len(list(self.root.iterdir())) >= MAX_JOBS:
                raise OverflowError("queue_or_storage_limit")
            ident = uuid.uuid4().hex
            directory = self.root / ident
            directory.mkdir(mode=0o700)
            try:
                remaining = length
                with (directory / "input").open("xb") as output:
                    while remaining:
                        block = stream.read(min(65536, remaining))
                        if not block:
                            raise ValueError("truncated_upload")
                        output.write(block)
                        remaining -= len(block)
                with (directory / "input").open("rb") as f:
                    kind = input_kind(f.read(16))
                atomic(directory / "request.json",
                       {"mode": mode, "kind": kind, "input_sha256": digest(directory / "input"),
                        "submitted_utc": now(), "bytes": length,
                        "runtime_seal": self.runtime_seal})
                atomic(directory / "state.json", {"status": "queued", "updated_utc": now()})
                self.queue.put_nowait(ident)
                return ident
            except Exception:
                shutil.rmtree(directory, ignore_errors=True)
                raise

    def loop(self):
        """Supervise an entire process group so parser children cannot outlive a timeout."""
        while not self.stopping:
            try:
                ident = self.queue.get(timeout=1)
            except queue.Empty:
                continue
            directory = self.root / ident
            process = None
            timed_out = False
            result = None
            try:
                atomic(directory / "state.json", {"status": "running", "updated_utc": now()})
                t = time.monotonic()
                with (directory / "worker.log").open("wb") as log:
                    process = subprocess.Popen(
                        [sys.executable, str(Path(__file__).resolve()), "worker",
                         "--job", str(directory), "--runtime", str(self.runtime)],
                        stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                    try:
                        code = process.wait(timeout=self.timeout)
                    except subprocess.TimeoutExpired:
                        timed_out = True
                        try:
                            os.killpg(process.pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                        process.wait()
                        code = process.returncode
                if code == 0 and not timed_out:
                    try:
                        result = validate_result(read_json(directory / "result.json"))
                        status, error = REVIEW, None
                    except (OSError, ValueError, KeyError, TypeError):
                        result = None
                        status, error = "failed", "invalid_worker_result"
                else:
                    status, error = "failed", ("timeout" if timed_out else
                                               "worker_signal" if code < 0 else "worker_failed")
                    if not timed_out and code > 0 and (directory / "error.json").exists():
                        error = read_json(directory / "error.json")["error"]
                    if error in ("ModuleNotFoundError", "ImportError", "FileNotFoundError",
                                 "runtime_changed", "model_hash_mismatch"):
                        self.failure = "runtime_unavailable"
                terminal_progress(directory, status, error, result)
                atomic(directory / "state.json", {
                    "status": status, "error": error, "worker_exit": code,
                    "timed_out": timed_out, "signal": -code if code < 0 else None,
                    "job_wall_seconds": time.monotonic() - t, "updated_utc": now()})
            except Exception:
                if process and process.poll() is None:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                self.failure = "supervisor_failure"
                terminal_progress(directory, "failed", self.failure)
                atomic(directory / "state.json", {"status": "failed",
                                                  "error": self.failure, "updated_utc": now()})
            finally:
                shutil.rmtree(directory / "work", ignore_errors=True)
                self.queue.task_done()


class Handler(http.server.BaseHTTPRequestHandler):
    """Raw-body internal API, authenticated with kernel peer UID and socket permissions."""
    server_version = "CorpusOCR/1"

    def setup(self):
        super().setup()
        self.connection.settimeout(20)

    def log_message(self, *args):
        """Never log document content, headers or credentials."""
        return

    def reply(self, status, obj):
        """Send bounded JSON with no browser trust or caching."""
        body = json.dumps(obj, ensure_ascii=False, allow_nan=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)
        self.close_connection = True

    def authorized(self):
        """Trust Linux peer credentials, never a supplied header or filename."""
        _, uid, _ = struct.unpack("3i", self.connection.getsockopt(
            socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i")))
        return uid == os.getuid()

    def do_GET(self):
        """Read lifecycle and result records only by opaque server-generated IDs."""
        if not self.authorized():
            return self.reply(403, {"error": "forbidden"})
        path = urlsplit(self.path)
        if path.query:
            return self.reply(400, {"error": "unknown_query"})
        jobs = self.server.jobs
        if path.path == "/live":
            return self.reply(200, {"status": "alive"})
        if path.path == "/ready":
            ready = bool(jobs.ready())
            return self.reply(200 if ready else 503, {
                "status": "ready_for_jobs" if ready else "unavailable",
                "engine": "PaddleOCR-VL-1.6", "device": "cpu",
                "execution": "isolated_process_per_job", "resident_model": False,
                "max_pages": MAX_PAGES, "max_bytes": MAX_BYTES,
                "queue_depth": jobs.queue.qsize(), "fidelity_certified": False})
        parts = path.path.strip("/").split("/")
        if len(parts) not in (3, 4) or parts[:2] != ["v1", "jobs"] or not ID_PATTERN.fullmatch(parts[2]):
            return self.reply(404, {"error": "not_found"})
        directory = jobs.root / parts[2]
        if not (directory / "state.json").is_file():
            return self.reply(404, {"error": "not_found"})
        state = read_json(directory / "state.json")
        if len(parts) == 4:
            if parts[3] != "result":
                return self.reply(404, {"error": "not_found"})
            if state["status"] != REVIEW:
                return self.reply(409, {"error": "result_not_complete", "state": state})
            try:
                result = validate_result(read_json(directory / "result.json"))
            except (OSError, ValueError, KeyError, TypeError):
                return self.reply(409, {"error": "invalid_worker_result"})
            return self.reply(200, result)
        if (directory / "progress.json").exists():
            state["progress"] = read_json(directory / "progress.json")
        return self.reply(200, state)

    def do_POST(self):
        """Accept raw PDF/image bytes, not paths, URLs, multipart or arbitrary options."""
        if not self.authorized():
            return self.reply(403, {"error": "forbidden"})
        path = urlsplit(self.path)
        params = parse_qs(path.query, keep_blank_values=True)
        if path.path != "/v1/jobs":
            return self.reply(404, {"error": "not_found"})
        if set(params) - {"mode"} or len(params.get("mode", ["auto"])) != 1:
            return self.reply(400, {"error": "invalid_parameters"})
        mode = params.get("mode", ["auto"])[0]
        if mode not in MODES:
            return self.reply(400, {"error": "invalid_mode"})
        if self.headers.get("Transfer-Encoding") or len(self.headers.get_all("Content-Length", [])) != 1:
            return self.reply(411, {"error": "content_length_required"})
        try:
            length = int(self.headers["Content-Length"])
        except ValueError:
            return self.reply(400, {"error": "invalid_length"})
        if not 0 < length <= MAX_BYTES:
            return self.reply(413, {"error": "size_limit"})
        if not self.server.jobs.ready():
            return self.reply(503, {"error": "runtime_unavailable"})
        try:
            ident = self.server.jobs.admit(self.rfile, length, mode)
        except OverflowError:
            return self.reply(429, {"error": "queue_or_storage_limit"})
        except (ValueError, TimeoutError, OSError):
            return self.reply(400, {"error": "invalid_or_incomplete_upload"})
        return self.reply(202, {"job": ident, "status_url": f"/v1/jobs/{ident}",
                                "result_url": f"/v1/jobs/{ident}/result"})


class Server(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    """Bounded local transport; the OS enforces the filesystem access boundary."""
    daemon_threads = True
    request_queue_size = 4

    def __init__(self, address, jobs):
        self.jobs = jobs
        self.slots = threading.BoundedSemaphore(4)
        super().__init__(address, Handler)

    def process_request(self, request, address):
        """Limit concurrent uploads before creating threads."""
        if not self.slots.acquire(blocking=False):
            request.close()
            return
        try:
            super().process_request(request, address)
        except Exception:
            self.slots.release()
            raise

    def process_request_thread(self, request, address):
        try:
            super().process_request_thread(request, address)
        finally:
            self.slots.release()


def main():
    """Start a sidecar or isolated worker with explicit server-owned directories."""
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["serve", "worker", "verify"])
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--job", type=Path)
    parser.add_argument("--state", type=Path, default=Path("/var/lib/corpus-ocr"))
    parser.add_argument("--socket", type=Path, default=Path("/run/corpus-ocr/ocr.sock"))
    args = parser.parse_args()
    os.umask(0o077)
    if args.command == "worker":
        try:
            worker(args.job, args.runtime)
        except Exception as exc:
            # Preserve full traceback only in the private supervisor log.
            import traceback
            traceback.print_exc()
            safe = str(exc) if type(exc) is ValueError and re.fullmatch(r"[a-z_]+", str(exc)) else type(exc).__name__
            atomic(args.job / "error.json", {"error": safe})
            raise SystemExit(1)
    elif args.command == "verify":
        print(json.dumps(verify_runtime(args.runtime)))
    else:
        jobs = Jobs(args.state, args.runtime)
        if args.socket.exists():
            if not args.socket.is_socket() or args.socket.stat().st_uid != os.getuid():
                raise RuntimeError("unsafe_existing_socket")
            # Refuse replacing a live instance; remove only a stale owned socket.
            probe = socket.socket(socket.AF_UNIX)
            try:
                probe.connect(str(args.socket))
            except ConnectionRefusedError:
                args.socket.unlink()
            else:
                raise RuntimeError("service_already_running")
            finally:
                probe.close()
        with Server(str(args.socket), jobs) as server:
            os.chmod(args.socket, 0o600)
            print(json.dumps({"event": "listening", "utc": now(),
                              "code_sha256": digest(__file__)}), flush=True)
            server.serve_forever()


if __name__ == "__main__":
    main()
