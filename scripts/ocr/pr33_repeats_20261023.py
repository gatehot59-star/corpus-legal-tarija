#!/usr/bin/env python3
"""Run three fresh, serial PR33 jobs; compare full UTF-8 only after inference.

No prior transcript is passed to the candidate. Each API job creates a fresh
worker and model. The original is opened only after all three workers exit.
This is an experimental instrument, not a deployment or product regression.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import fcntl
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import signal
import statistics
import subprocess
import sys
import time
import traceback
import unicodedata


def utc():
    """Return a timezone-qualified timestamp."""
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    """Hash a file without allocating it all in RAM."""
    value = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def save(path, data):
    """Atomically save one owned record, including intermediate failures."""
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".new")
    with temporary.open("w", encoding="utf-8") as output:
        json.dump(data, output, ensure_ascii=False, allow_nan=False, indent=2)
        output.write("\n")
        output.flush()
        os.fsync(output.fileno())
    temporary.replace(path)


def require(condition, message):
    """Fail regardless of Python optimization flags."""
    if not condition:
        raise ValueError(message)


def compare_bytes(left, right):
    """Compare literal bytes without strip, Unicode conversion or normalization."""
    require(isinstance(left, bytes) and isinstance(right, bytes), "bytes_required")
    same = left == right
    first = None
    if not same:
        first = next((i for i, (a, b) in enumerate(zip(left, right)) if a != b),
                     min(len(left), len(right)))
    return {
        "equal": same, "left_bytes": len(left), "right_bytes": len(right),
        "left_sha256": hashlib.sha256(left).hexdigest(),
        "right_sha256": hashlib.sha256(right).hexdigest(),
        "first_different_byte": first,
    }


def compare_samples(samples):
    """Compare all unordered pairs, rejecting missing or repeated sample IDs."""
    require(len(samples) >= 2, "too_few_samples")
    require(len({name for name, _ in samples}) == len(samples), "duplicate_sample_id")
    return [{"left": a[0], "right": b[0], **compare_bytes(a[1], b[1])}
            for a, b in itertools.combinations(samples, 2)]


def validate_result(result, seal):
    """Independently validate page coverage, complete text and measured metadata."""
    require(result["schema"] == "corpus-ocr/1", "schema")
    require(result["status"] == "requires_review", "status")
    require(result["fidelity_certified"] is False, "false_certification")
    require(result["expected_pages"] == result["completed_pages"] == 2, "page_count")
    pages = result["pages"]
    require([page["page"] for page in pages] == [1, 2], "page_order")
    for page in pages:
        require(page["method"] == "PaddleOCR-VL-1.6", "wrong_engine")
        require(page["status"] == "requires_review", "page_status")
        require(page["blank_by_pixels"] is False, "unexpected_blank")
        blocks = page["blocks"]
        require([block["index"] for block in blocks] == list(range(len(blocks))),
                "block_indices")
        require(page["text"] == "\n".join(block["text"] for block in blocks),
                "block_text_mismatch")
        require(hashlib.sha256(page["text"].encode("utf-8")).hexdigest()
                == page["text_sha256"], "text_hash")
        require(page["image_sha256"] == seal["page_images"][str(page["page"])]["sha256"],
                "image_changed")
        seconds = page["extraction_seconds"]
        require(type(seconds) in (int, float) and math.isfinite(seconds) and seconds > 0,
                "invalid_page_time")
    require(result["text"] == "\n\f\n".join(page["text"] for page in pages),
            "document_text_mismatch")
    require(result["markdown"] == "\n\n".join(
        f"<!-- page:{page['page']} -->\n" + page["text"] for page in pages),
        "document_markdown_mismatch")
    provenance = result["provenance"]
    for field, expected in seal["provenance"].items():
        require(provenance[field] == expected, "provenance_changed:" + field)
    timings = provenance["timings"]
    for field in ("preparation_seconds", "load_seconds", "warmup_seconds",
                  "extraction_sum_seconds", "worker_wall_seconds"):
        seconds = timings[field]
        require(type(seconds) in (int, float) and math.isfinite(seconds) and seconds > 0,
                "invalid_time:" + field)
    require(math.isclose(sum(page["extraction_seconds"] for page in pages),
                         timings["extraction_sum_seconds"], rel_tol=1e-12),
            "extraction_sum_mismatch")


def self_test():
    """Exercise literal equality and result validators with positive and mutants."""
    text = "NO PAGAR Bs20.000.000\nCláusula á.\n"
    original = text.encode("utf-8")
    controls = {"identical": compare_bytes(original, original)}
    require(controls["identical"]["equal"], "positive_rejected")
    mutants = {
        "character": text.replace("20.000.000", "30.000.000"),
        "trailing_space": text + " ",
        "LF_to_CRLF": text.replace("\n", "\r\n"),
        "unicode_NFD": unicodedata.normalize("NFD", text),
        "negation_removed": text.replace("NO PAGAR", "PAGAR"),
    }
    for name, altered in mutants.items():
        outcome = compare_bytes(original, altered.encode("utf-8"))
        require(not outcome["equal"], "comparator_missed:" + name)
        controls[name] = outcome
    for name, samples in (
        ("duplicate_id", [("a", original), ("a", original)]),
        ("missing_sample", [("a", original)]),
    ):
        try:
            compare_samples(samples)
        except ValueError as error:
            controls[name] = {"rejected": True, "error": str(error)}
        else:
            raise ValueError("coverage_guard_missed:" + name)
    pairs = compare_samples([(str(i), original) for i in range(4)])
    require(len(pairs) == 6 and all(p["equal"] for p in pairs), "pair_count")
    seal = {"page_images": {"1": {"sha256": "1" * 64}, "2": {"sha256": "2" * 64}},
            "provenance": {"code_sha256": "a" * 64, "device": "cpu"}}
    pages = []
    for number in (1, 2):
        value = "synthetic control " + str(number)
        pages.append({"page": number, "method": "PaddleOCR-VL-1.6",
                      "status": "requires_review", "blank_by_pixels": False,
                      "blocks": [{"index": 0, "text": value}], "text": value,
                      "text_sha256": hashlib.sha256(value.encode()).hexdigest(),
                      "image_sha256": str(number) * 64, "extraction_seconds": 1.0})
    positive = {"schema": "corpus-ocr/1", "status": "requires_review",
                "fidelity_certified": False, "expected_pages": 2, "completed_pages": 2,
                "pages": pages, "text": "\n\f\n".join(p["text"] for p in pages),
                "markdown": "\n\n".join(
                    f"<!-- page:{p['page']} -->\n" + p["text"] for p in pages),
                "provenance": {"code_sha256": "a" * 64, "device": "cpu",
                               "timings": {"preparation_seconds": 1.0, "load_seconds": 1.0,
                                           "warmup_seconds": 1.0,
                                           "extraction_sum_seconds": 2.0,
                                           "worker_wall_seconds": 5.0}}}
    validate_result(positive, seal)
    controls["envelope_positive"] = {"accepted": True}
    for name in ("missing_page", "zero_time", "wrong_input_image",
                 "contradictory_text", "wrong_source", "false_fidelity"):
        value = copy.deepcopy(positive)
        if name == "missing_page":
            value["pages"].pop()
        elif name == "zero_time":
            value["pages"][0]["extraction_seconds"] = 0
        elif name == "wrong_input_image":
            value["pages"][0]["image_sha256"] = "0" * 64
        elif name == "contradictory_text":
            value["text"] += " "
        elif name == "wrong_source":
            value["provenance"]["code_sha256"] = "0" * 64
        else:
            value["fidelity_certified"] = True
        try:
            validate_result(value, seal)
        except (ValueError, KeyError) as error:
            controls[name] = {"rejected": True, "error": str(error)}
        else:
            raise ValueError("envelope_guard_missed:" + name)
    return {"status": "PASS", "controls": controls, "four_samples_pairs_per_page": len(pairs),
            "synthetic_controls_not_ocr": True}


def worker_processes(subject, job_root):
    """Find only this candidate's workers, never production or unrelated processes."""
    found = []
    for process in Path("/proc").iterdir():
        if not process.name.isdigit():
            continue
        try:
            argv = [v.decode() for v in (process / "cmdline").read_bytes().split(b"\0") if v]
            if len(argv) < 4 or argv[1:3] != [str(subject / "ocr_service.py"), "worker"]:
                continue
            require("--job" in argv, "worker_job_argument_missing")
            job = Path(argv[argv.index("--job") + 1])
            if job.parent != job_root:
                continue
            stat = (process / "stat").read_text().rsplit(") ", 1)[1].split()
            found.append({"pid": int(process.name), "start_ticks": int(stat[19]),
                          "job": job.name, "argv": argv,
                          "cgroup": (process / "cgroup").read_text()})
        except FileNotFoundError:
            continue
    return found


def cgroup_snapshot():
    """Read the experiment cgroup while it still exists, preserving missing fields."""
    lines = Path("/proc/self/cgroup").read_text().splitlines()
    relative = next((line[3:] for line in lines if line.startswith("0::")), None)
    if relative is None:
        return {"unavailable": "no_cgroup_v2"}
    directory = Path("/sys/fs/cgroup") / relative.lstrip("/")
    result = {"path": str(directory)}
    for name in ("memory.current", "memory.peak", "memory.swap.current",
                 "memory.swap.peak", "memory.events", "cpu.stat"):
        path = directory / name
        try:
            result[name] = path.read_text()
        except OSError as error:
            result[name] = {"unavailable": type(error).__name__}
    return result


def production_busy():
    """Yield to actual production OCR demand without changing production state."""
    directory = Path("/var/lib/corpus-ocr")
    require(directory.is_dir(), "production_state_unavailable")
    active = []
    for item in directory.iterdir():
        state = item / "state.json"
        if not item.is_dir() or not state.is_file():
            continue
        value = json.loads(state.read_bytes())
        if value.get("status") in ("queued", "running"):
            active.append({"job": item.name, "status": value["status"]})
    return active


def stop_owned(server, subject, jobs):
    """Terminate only processes belonging to this experiment on exit or deadline."""
    actions = []
    for sig in (signal.SIGTERM, signal.SIGKILL):
        workers = worker_processes(subject, jobs)
        for worker in workers:
            try:
                os.killpg(worker["pid"], sig)
                actions.append({"worker": worker, "signal": sig.name})
            except ProcessLookupError:
                pass
        if workers:
            time.sleep(2)
        else:
            break
    if server is not None and server.poll() is None:
        os.killpg(server.pid, signal.SIGTERM)
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(server.pid, signal.SIGKILL)
            server.wait(timeout=10)
    remaining = worker_processes(subject, jobs)
    return {"actions": actions, "server_exit": server.returncode if server else None,
            "remaining_workers": remaining}


def image_manifest(job, seal):
    """Observe the actual rendered images before the unmodified worker deletes them."""
    from PIL import Image
    rows = []
    for number in (1, 2):
        path = job / "work" / f"page-{number:04d}.png"
        if not path.is_file():
            return None
        with Image.open(path) as image:
            row = {"page": number, "sha256": digest(path), "width": image.width,
                   "height": image.height, "mode": image.mode}
        expected = seal["page_images"][str(number)]
        require(all(row[k] == expected[k] for k in ("sha256", "width", "height", "mode")),
                "actual_render_changed")
        rows.append(row)
    return rows


def statistics_for(values):
    """Return descriptive times, never an invented latency pass/fail threshold."""
    require(len(values) == 3 and all(v > 0 for v in values), "time_coverage")
    return {"individual_seconds": values, "mean_seconds": statistics.mean(values),
            "median_seconds": statistics.median(values), "minimum_seconds": min(values),
            "maximum_seconds": max(values), "range_seconds": max(values) - min(values),
            "sample_stdev_seconds": statistics.stdev(values)}


def final_comparison(root, seal, runs):
    """Read the reference only after all new workers finished, then compare every pair."""
    require(len(runs) == 3 and len({r["job"] for r in runs}) == 3, "run_coverage")
    require(all(a["finished_monotonic"] <= b["submitted_monotonic"]
                for a, b in zip(runs, runs[1:])), "overlapping_jobs")
    identities = [(worker["pid"], worker["start_ticks"])
                  for run in runs for worker in run["workers"]]
    require(len(identities) == 3 and len(set(identities)) == 3, "fresh_worker_identity")
    reference = Path(seal["reference_result"])
    require(digest(reference) == seal["reference_result_sha256"], "original_changed")
    original = json.loads(reference.read_bytes())
    validate_result(original, seal)
    results = [json.loads((root / f"r{number}-result.json").read_bytes())
               for number in (1, 2, 3)]
    for result in results:
        validate_result(result, seal)
    original_texts = root / "original-texts"
    original_texts.mkdir()
    pairs, raw_pairs, times = {}, {}, {}
    for page in (1, 2):
        text = original["pages"][page - 1]["text"].encode("utf-8")
        (original_texts / f"page-{page}.utf8.txt").write_bytes(text)
        samples = [("original", text)] + [
            (f"r{i}", (root / f"r{i}-page-{page}.utf8.txt").read_bytes()) for i in (1, 2, 3)]
        pairs[str(page)] = compare_samples(samples)
        raw_path = Path(seal["reference_job"]) / f"raw-{page:04d}.json"
        require(digest(raw_path) == seal["reference_raw_sha256"][str(page)],
                "original_raw_changed")
        raw_samples = [("original", raw_path.read_bytes())] + [
            (f"r{i}", (root / "jobs" / runs[i - 1]["job"] /
                       f"raw-{page:04d}.json").read_bytes()) for i in (1, 2, 3)]
        raw_pairs[str(page)] = compare_samples(raw_samples)
        values = [result["pages"][page - 1]["extraction_seconds"] for result in results]
        previous = original["pages"][page - 1]["extraction_seconds"]
        times[str(page)] = {**statistics_for(values), "original_seconds": previous,
                            "differences_from_original_seconds": [v - previous for v in values]}
    text_equal = all(pair["equal"] for rows in pairs.values() for pair in rows)
    raw_equal = all(pair["equal"] for rows in raw_pairs.values() for pair in rows)
    return {"text_repeatability": "PASS" if text_equal else "FAIL",
            "raw_json_byte_equality": "PASS" if raw_equal else "FAIL",
            "text_pairs": pairs, "raw_json_pairs": raw_pairs, "timings_by_page": times,
            "reference_read_utc": utc(), "reference_read_after_fresh_workers": True,
            "new_inferences": 6, "fresh_workers": 3, "new_vm_sessions": 0,
            "latency_verdict": "NO MEDIDO: no predeclared tolerance",
            "general_legal_fidelity": "NO MEDIDO"}


def run(base):
    """Run one sealed batch with serial API admissions and bounded resource ownership."""
    base = base.resolve()
    seal = json.loads((base / "seal.json").read_bytes())
    subject = base / "subject"
    root = base / "state" / "run"
    root.mkdir(mode=0o700, exist_ok=False)
    jobs = root / "jobs"
    sock = root / "candidate.sock"
    fixture = base / "input.pdf"
    server = None
    records = []
    start = time.monotonic()
    verdict = {"status": "running", "text_repeatability": "EN CURSO",
               "started_utc": utc(), "runs": records, "seal_sha256": digest(base / "seal.json"),
               "instrument_sha256": digest(__file__), "new_inferences_completed": 0}
    save(root / "verdict.json", verdict)
    lock = (base / "state" / "batch.lock").open("a")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for relative, expected in seal["source_sha256"].items():
            require(digest(base / relative) == expected, "source_changed:" + relative)
        require(digest(fixture) == seal["input_sha256"], "fixture_changed")
        require(seal["order"] == [[1, 2], [1, 2], [1, 2]], "wrong_schedule")
        save(root / "self-test.json", self_test())
        freeze = subprocess.run([sys.executable, "-m", "pip", "freeze", "--all"],
                                capture_output=True, text=True, timeout=30)
        save(root / "environment.json", {
            "utc": utc(), "python": sys.version, "uname": list(os.uname()),
            "boot_id": Path("/proc/sys/kernel/random/boot_id").read_text(),
            "pip_freeze": {"exit": freeze.returncode, "stdout": freeze.stdout,
                           "stderr": freeze.stderr},
            "seed_policy": seal["seed_policy"],
        })
        require(freeze.returncode == 0 and hashlib.sha256(freeze.stdout.encode()).hexdigest()
                == seal["pip_freeze_sha256"], "environment_changed")
        sys.path.insert(0, str(subject))
        from ocr_client import request
        command = [sys.executable, str(subject / "ocr_service.py"), "serve",
                   "--runtime", seal["runtime"], "--state", str(jobs), "--socket", str(sock)]
        save(root / "server-command.json", {"argv": command, "utc": utc()})
        log = (root / "server.log").open("wb")
        server = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                                  start_new_session=True)
        log.close()
        deadline = time.monotonic() + seal["readiness_timeout_seconds"]
        while time.monotonic() < deadline:
            require(server.poll() is None, "candidate_server_exited")
            if sock.exists():
                status, ready = request(str(sock), "GET", "/ready")
                if status == 200:
                    save(root / "ready.json", ready)
                    break
            time.sleep(2)
        else:
            raise TimeoutError("readiness_deadline")
        for number in (1, 2, 3):
            busy = production_busy()
            require(not busy, "production_ocr_demand:" + json.dumps(busy))
            require(not worker_processes(subject, jobs), "previous_worker_still_alive")
            require(digest(fixture) == seal["input_sha256"], "fixture_changed")
            submitted = time.monotonic()
            submitted_utc = utc()
            status, admission = request(str(sock), "POST", "/v1/jobs?mode=auto",
                                        fixture.read_bytes())
            require(status == 202, "admission_failed")
            ident = admission["job"]
            require(ident not in {r["job"] for r in records}, "reused_job_id")
            record = {"repeat": number, "job": ident, "admission_status": status,
                      "admission": admission, "submitted_utc": submitted_utc,
                      "submitted_monotonic": submitted, "workers": [],
                      "page_inference_ids": [f"{ident}:page-1", f"{ident}:page-2"]}
            records.append(record)
            save(root / "runs.json", records)
            deadline = submitted + seal["per_job_timeout_seconds"]
            state = None
            rendered = None
            with (root / f"r{number}-polls.jsonl").open("w", encoding="utf-8") as polls:
                while time.monotonic() < deadline:
                    busy = production_busy()
                    require(not busy, "production_ocr_demand:" + json.dumps(busy))
                    require(server.poll() is None, "candidate_server_exited")
                    status, state = request(str(sock), "GET", "/v1/jobs/" + ident)
                    require(status == 200, "job_poll_failed")
                    workers = worker_processes(subject, jobs)
                    for worker in workers:
                        require(worker["job"] == ident, "wrong_worker_job")
                        if worker not in record["workers"]:
                            record["workers"].append(worker)
                            save(root / "runs.json", records)
                    if rendered is None and state.get("progress", {}).get("phase") in (
                            "loading", "extraction"):
                        rendered = image_manifest(jobs / ident, seal)
                        if rendered:
                            save(root / f"r{number}-rendered-images.json", rendered)
                    sample = {"utc": utc(), "monotonic": time.monotonic(), "state": state,
                              "workers": workers, "resources": cgroup_snapshot()}
                    polls.write(json.dumps(sample, ensure_ascii=False) + "\n")
                    polls.flush()
                    save(root / "checkpoint.json", {"utc": sample["utc"], "repeat": number,
                         "job": ident, "state": state, "completed_repeats": number - 1,
                         "new_pages_completed": 2 * (number - 1)
                             + state.get("progress", {}).get("completed_pages", 0)})
                    if state["status"] in ("requires_review", "failed", "interrupted"):
                        break
                    time.sleep(5)
                else:
                    raise TimeoutError("sealed_job_deadline")
            record.update({"state": state, "finished_utc": utc(),
                           "finished_monotonic": time.monotonic()})
            save(root / "runs.json", records)
            require(state["status"] == "requires_review" and state["worker_exit"] == 0
                    and state["timed_out"] is False and state["signal"] is None,
                    "worker_failed")
            require(state["progress"]["completed_pages"] == 2
                    and state["progress"]["phase"] == "completed", "terminal_progress")
            require(len(record["workers"]) == 1 and rendered is not None,
                    "missing_worker_or_image_observation")
            require(not worker_processes(subject, jobs), "worker_not_reaped")
            status, result = request(str(sock), "GET", "/v1/jobs/" + ident + "/result")
            save(root / f"r{number}-result.json", result)
            require(status == 200, "result_unavailable")
            validate_result(result, seal)
            require(json.loads((jobs / ident / "result.json").read_bytes()) == result,
                    "api_worker_result_mismatch")
            for page in result["pages"]:
                number_page = page["page"]
                raw_path = jobs / ident / f"raw-{number_page:04d}.json"
                raw = json.loads(raw_path.read_bytes())
                inner = raw.get("res", raw)
                require([v["block_content"] for v in inner["parsing_res_list"]]
                        == [v["text"] for v in page["blocks"]], "raw_blocks_mismatch")
                (root / f"r{number}-page-{number_page}.utf8.txt").write_bytes(
                    page["text"].encode("utf-8"))
            verdict["new_inferences_completed"] = 2 * number
            save(root / "verdict.json", verdict)
        require(not worker_processes(subject, jobs), "comparison_before_worker_exit")
        comparison = final_comparison(root, seal, records)
        save(root / "comparison.json", comparison)
        verdict.update(status="complete", text_repeatability=comparison["text_repeatability"],
                       raw_json_byte_equality=comparison["raw_json_byte_equality"],
                       comparison_path=str(root / "comparison.json"))
    except BaseException as error:
        verdict.update(status="failed", text_repeatability="NO MEDIDO",
                       error_type=type(error).__name__, error=str(error))
        traceback.print_exc()
    finally:
        verdict["resources_before_teardown"] = cgroup_snapshot()
        verdict["teardown"] = stop_owned(server, subject, jobs)
        verdict["finished_utc"] = utc()
        verdict["continuous_wall_seconds"] = time.monotonic() - start
        save(root / "verdict.json", verdict)
        lock.close()
        print(json.dumps(verdict, ensure_ascii=False), flush=True)
    if verdict["status"] != "complete":
        return 1
    return 0 if verdict["text_repeatability"] == "PASS" else 2


def main():
    """Expose a cheap self-test and exactly one explicitly requested experiment."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--base", type=Path)
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), ensure_ascii=False, indent=2))
        return 0
    if args.base is None:
        parser.error("--base is required for actual inference")
    return run(args.base)


if __name__ == "__main__":
    raise SystemExit(main())
