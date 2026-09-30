"""Minimal MCP stdio tools server: no sampling, network listener or shell tool.

Root is fixed by the trusted launcher. Unknown lifecycle notifications do not
become model calls. Tools have structured arguments; no heredoc is necessary.
"""
from __future__ import annotations

import json
import sqlite3

from . import VERSION
from .capabilities import admit
from .common import OserError, require
from .health import Health
from .state import Store
from .usage import Usage

PROTOCOLS = ("2024-11-05", "2025-03-26", "2025-06-18", "2025-11-25")
MAX_LINE = 2 * 1024 * 1024
STRING = {"type": "string", "minLength": 1}
OPERATIONS = ["catalog.record", "execution.open", "execution.receipt", "execution.reconcile",
              "checkpoint.record", "ownership.transfer", "evidence.record", "blocker.set", "mission.complete"]


def tool(name, description, props, required, readonly=False):
    return {"name": name, "description": description,
            "inputSchema": {"type": "object", "properties": props, "required": required, "additionalProperties": False},
            "annotations": {"readOnlyHint": readonly, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}}


TOOLS = [
    tool("oser_mission_init", "Create approved Mission baseline; never modifies host settings, deploys or spawns models. Existing Mission IDs cannot be overwritten.",
         {"contract": {"type": "object"}, "event_key": STRING}, ["contract", "event_key"]),
    tool("oser_mission_read", "Read Mission, acceptance frontier, owner epoch/revision, latest checkpoint, policy and runtime catalog. No raw transcript.",
         {"mission": STRING}, ["mission"], True),
    tool("oser_mission_apply", "Atomic idempotent Mission operation. Supply current revision/owner epoch. catalog.record stores proven capabilities; execution.open checks admission, NOT spawn; receipt records native facts; evidence.record hashes artifact and current sources; checkpoint permits waiting; transfer changes owner epoch. No authority/policy edit operation.",
         {"mission": STRING, "operation": {"type": "string", "enum": OPERATIONS}, "payload": {"type": "object"},
          "expected_revision": {"type": "integer", "minimum": 0}, "event_key": STRING, "actor": STRING,
          "owner_epoch": {"type": "integer", "minimum": 0}},
         ["mission", "operation", "payload", "expected_revision", "event_key", "actor", "owner_epoch"]),
    tool("oser_admit", "Check a proposed native model/effort against current capability evidence and approved account envelope. ADMITTED does not mean execution started or native sandbox enforced.",
         {"mission": STRING, "request": {"type": "object"}}, ["mission", "request"], True),
    tool("oser_health", "Read per-account quota/context and freshness. Never combines percentages or wakes the model.", {}, [], True),
    tool("oser_usage", "Read deduplicated imported response usage. Incomplete/conflicting measurements remain UNKNOWN/INVALID.",
         {"mission": STRING}, ["mission"], True),
]


def invoke(project, name, arguments):
    definition = next((t for t in TOOLS if t["name"] == name), None)
    require(definition is not None, "UNKNOWN_TOOL", "unknown OSER tool")
    schema = definition["inputSchema"]
    require(isinstance(arguments, dict), "INVALID_ARGUMENTS", "arguments must be an object")
    require(set(schema["required"]).issubset(arguments) and not (set(arguments) - set(schema["properties"])),
            "INVALID_ARGUMENTS", "missing or unexpected tool arguments")
    if name == "oser_mission_init":
        from .cli import initialize
        return initialize(project, arguments["contract"], arguments["event_key"])
    store = Store(project)
    if name == "oser_health":
        return {"samples": Health(store).read(), "model_calls": 0}
    mission = arguments["mission"]
    if name == "oser_mission_read":
        state = store.read(mission)
        return dict(store.evaluate(state), baseline=state["baseline"], sources=state["sources"], policy=state["policy"],
                    catalog=state["catalog"], executions=[{"ref": e["ref"], "status": e["status"], "reconciled": e["reconciled"]}
                                                          for e in state["executions"].values()])
    if name == "oser_usage":
        return Usage(store).report(mission)
    if name == "oser_admit":
        state = store.read(mission)
        return admit(state["catalog"], state["policy"], arguments["request"])
    from .cli import summary
    return summary(store.apply(**arguments))


def serve(project, source, sink):
    initialized = False

    def output(value):
        sink.write(json.dumps(value, ensure_ascii=False, allow_nan=False) + "\n")
        sink.flush()

    while True:
        line = source.readline(MAX_LINE + 1)
        if not line:
            return
        if len(line) > MAX_LINE:
            while line and not line.endswith("\n"):
                line = source.readline(MAX_LINE + 1)
            output({"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Request too large"}})
            continue
        request = None
        try:
            request = json.loads(line)
            require(isinstance(request, dict) and request.get("jsonrpc") == "2.0", "INVALID_REQUEST", "JSON-RPC 2.0 object required")
            method, params = request.get("method"), request.get("params", {})
            require(isinstance(params, dict), "INVALID_REQUEST", "params must be an object")
            if "id" not in request:
                continue
            if method == "initialize":
                require(not initialized, "ALREADY_INITIALIZED", "connection already initialized")
                requested = params.get("protocolVersion")
                version = requested if requested in PROTOCOLS else PROTOCOLS[-1]
                initialized = True
                result = {"protocolVersion": version, "capabilities": {"tools": {}},
                          "serverInfo": {"name": "nnc-oser", "version": VERSION}}
            elif method == "ping":
                result = {}
            else:
                require(initialized, "NOT_INITIALIZED", "initialize first")
                if method == "tools/list":
                    result = {"tools": TOOLS}
                elif method == "tools/call":
                    try:
                        value = invoke(project, params.get("name"), params.get("arguments", {}))
                        result = {"content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False)}], "isError": False}
                    except (OserError, OSError, ValueError, TypeError, KeyError, sqlite3.Error) as exc:
                        result = {"content": [{"type": "text", "text": json.dumps({"code": getattr(exc, "code", "INPUT_OR_STORAGE_ERROR"), "message": str(exc)})}], "isError": True}
                else:
                    output({"jsonrpc": "2.0", "id": request["id"], "error": {"code": -32601, "message": "Method not found"}})
                    continue
            output({"jsonrpc": "2.0", "id": request["id"], "result": result})
        except (OserError, ValueError, TypeError, KeyError) as exc:
            output({"jsonrpc": "2.0", "id": request.get("id") if isinstance(request, dict) else None,
                    "error": {"code": -32700 if isinstance(exc, json.JSONDecodeError) else -32600,
                              "message": str(exc)}})
