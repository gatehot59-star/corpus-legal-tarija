#!/usr/bin/env python3
"""Submit a local file to the private sidecar, poll it and print the full result."""
import argparse
import http.client
import json
from pathlib import Path
import socket
import sys
import time


class UnixConnection(http.client.HTTPConnection):
    """HTTP over an owner-only Unix socket, never over an unauthenticated TCP port."""
    def __init__(self, path):
        super().__init__("localhost", timeout=30)
        self.path = path

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX)
        self.sock.settimeout(self.timeout)
        self.sock.connect(self.path)


def request(path, method, route, body=None):
    """Return HTTP status and decoded JSON, closing the transport on every request."""
    connection = UnixConnection(path)
    try:
        connection.request(method, route, body=body,
                           headers={"Content-Type": "application/octet-stream"})
        response = connection.getresponse()
        return response.status, json.loads(response.read())
    finally:
        connection.close()


def main():
    """Submit or query jobs without granting arbitrary server-side path access."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--socket", default="/run/corpus-ocr/ocr.sock")
    parser.add_argument("--mode", choices=["auto", "ocr", "txt"], default="auto")
    parser.add_argument("--wait", type=int, default=0,
                        help="Maximum seconds to wait; zero returns the job ID immediately.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input", type=Path)
    group.add_argument("--job")
    group.add_argument("--ready", action="store_true")
    args = parser.parse_args()
    if args.ready:
        status, value = request(args.socket, "GET", "/ready")
    else:
        if args.input:
            if not 0 < args.input.stat().st_size <= 20 * 1024 * 1024:
                parser.error("input exceeds the 20 MiB limit or is empty")
            status, value = request(args.socket, "POST", "/v1/jobs?mode=" + args.mode,
                                    args.input.read_bytes())
            if status != 202 or not args.wait:
                print(json.dumps(value, ensure_ascii=False, indent=2))
                return 0 if status == 202 else 1
            job = value["job"]
            print(json.dumps({"job": job}), file=sys.stderr, flush=True)
        else:
            job = args.job
        import re
        if not re.fullmatch(r"[0-9a-f]{32}", job):
            parser.error("invalid job ID")
        end = time.monotonic() + args.wait
        while True:
            status, value = request(args.socket, "GET", "/v1/jobs/" + job)
            if value.get("status") == "requires_review":
                status, value = request(args.socket, "GET", "/v1/jobs/" + job + "/result")
                break
            if status != 200 or value.get("status") in ("failed", "interrupted"):
                status = 409
                break
            if time.monotonic() >= end:
                status = 202
                break
            time.sleep(5)
    print(json.dumps(value, ensure_ascii=False, indent=2))
    return 0 if status in (200, 202) else 1


if __name__ == "__main__":
    raise SystemExit(main())
