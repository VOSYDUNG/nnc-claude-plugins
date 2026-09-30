"""Bounded, opt-in host discovery. No model turn, credential-file read or login.

Codex probe performs initialize -> model/list (paginated) -> rateLimits/read.
It never starts/resumes a thread, consumes credits, requests approvals or wakes
an existing session. Run explicitly; installing the plugin does not run a probe.
"""
from __future__ import annotations

import json
import queue
import shutil
import subprocess
import threading
import time

from .adapters import codex_catalog, codex_health
from .common import OserError, require, utcnow

MAX_LINE = 2 * 1024 * 1024


def available_hosts():
    return {"codex": bool(shutil.which("codex")), "claude-code": bool(shutil.which("claude")),
            "active_host": "UNKNOWN", "note": "installed binaries do not identify the current host"}


def codex_probe(project, provider, account, timeout=15, executable=None):
    command = executable or shutil.which("codex")
    require(command is not None, "HOST_UNAVAILABLE", "codex binary was not found")
    require(0 < timeout <= 60, "INVALID_TIMEOUT", "probe timeout must be in (0,60]")
    process = subprocess.Popen([command, "app-server"], cwd=str(project), stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, encoding="utf-8", bufsize=1)
    messages = queue.Queue(maxsize=256)
    deadline = time.monotonic() + timeout

    def reader():
        try:
            while True:
                line = process.stdout.readline(MAX_LINE + 1)
                if not line:
                    messages.put_nowait({"_eof": True})
                    return
                if len(line) > MAX_LINE:
                    messages.put_nowait({"_error": "PROBE_RESPONSE_TOO_LARGE"})
                    return
                try:
                    messages.put_nowait(json.loads(line))
                except json.JSONDecodeError:
                    continue
        except (OSError, ValueError, queue.Full):
            return

    thread = threading.Thread(target=reader, daemon=True)
    thread.start()

    def send(value):
        process.stdin.write(json.dumps(value) + "\n")
        process.stdin.flush()

    def call(method, params, req_id):
        send({"method": method, "id": req_id, "params": params})
        while True:
            remaining = deadline - time.monotonic()
            require(remaining > 0, "PROBE_TIMEOUT", "host did not complete bounded discovery")
            try:
                message = messages.get(timeout=remaining)
            except queue.Empty as exc:
                raise OserError("PROBE_TIMEOUT", "host did not complete bounded discovery") from exc
            require(isinstance(message, dict), "PROBE_SCHEMA", "host returned non-object JSON")
            require(not message.get("_eof"), "HOST_EXITED", "host exited during probe")
            require(not message.get("_error"), "PROBE_SCHEMA", "host response exceeds bounds")
            if "method" in message and "id" in message:
                # Never satisfy credential refresh/approval requests in a probe.
                send({"id": message["id"], "error": {"code": -32601, "message": "Read-only probe does not handle host requests"}})
            if message.get("id") == req_id and ("result" in message or "error" in message):
                require("error" not in message, "HOST_RPC_ERROR", "host rejected read-only method " + method)
                return message["result"]

    try:
        call("initialize", {"clientInfo": {"name": "nnc_oser_probe", "version": "5.0.0-rc.1"}}, 1)
        send({"method": "initialized", "params": {}})
        models, cursor, seen = [], None, set()
        for page in range(20):
            params = {"limit": 100, "includeHidden": False}
            if cursor:
                params["cursor"] = cursor
            result = call("model/list", params, 10 + page)
            require(isinstance(result, dict) and isinstance(result.get("data"), list), "PROBE_SCHEMA", "invalid model/list reply")
            models.extend(result["data"])
            cursor = result.get("nextCursor")
            if not cursor:
                break
            require(cursor not in seen, "PROBE_PAGINATION", "model/list cursor loop")
            seen.add(cursor)
        require(not cursor, "PROBE_PAGINATION", "catalog exceeds bounded page limit")
        observed_at = utcnow()
        catalog = codex_catalog({"data": models, "nextCursor": None}, provider, account, observed_at,
                                "codex-app-server:model/list", "PROBED")
        health, health_error = [], None
        try:
            limits = call("account/rateLimits/read", {}, 100)
            health = codex_health(limits, provider, account, utcnow(), "codex-app-server:account/rateLimits/read")
        except OserError as exc:
            health_error = exc.code
        return {"catalog": catalog, "health": health, "health_error": health_error,
                "model_calls": 0, "can_wake": "UNKNOWN", "active_host": "codex-app-server"}
    finally:
        try:
            process.stdin.close()
        except (OSError, BrokenPipeError):
            pass
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2)
        process.stdout.close()
        thread.join(timeout=1)
