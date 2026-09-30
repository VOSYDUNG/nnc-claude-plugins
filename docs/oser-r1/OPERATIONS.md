# R1 operation contract

The default entry is `python plugins/nnc/oser/oser.py`. The `oser`/`oser.cmd`
wrappers call the same entry. Python APIs are in `oser_mission/`; `oser_core/`
is the explicit legacy implementation. R1 uses only the standard library.

## Storage and trust

One canonical `.nnc-oser/state.sqlite3` lives at the main Git worktree's root.
Linked worktrees discover it through `git rev-parse --git-common-dir`. Ordinary
non-Git projects use the supplied directory. Use local storage, not an assumed
multi-machine network filesystem or independently synced JSON copies.

SQLite `BEGIN IMMEDIATE` serializes writers; each Mission mutation checks a
revision and ownership epoch. Retry after re-reading on REVISION_CONFLICT.
Idempotency keys are project-wide: reuse the same key only for the same logical
operation. A replay returns its original result, not a new revision.

This is a local integrity contract, **not** a hostile-agent security boundary.
The trusted launcher chooses the project. A caller able to run arbitrary shell
or edit the database shares the local user's authority. Keep host sandboxes,
provider permissions, execution approvals and production restrictions intact.
Never put credentials, account tokens or private transcripts into examples.

## Initial contract

`oser init --project PROJECT --contract approved.json` accepts:

- `id`, `goal`, `owner`: nonblank project-specific values.
- `baseline.id`, `baseline.authority`: local `{path, sha256?}` or external
  `{ref, revision}`. Local hashes are checked. External references remain
  REFERENCE_ONLY; the kernel does not fetch or validate external authority.
- `sources`: explicit relative files/directories defining the evidence scope.
  Keep logs, OSER state and build outputs outside these source paths. Source
  scans are bounded; symlink escapes and filesystem-root paths are rejected.
- `acceptance`: fixed `{id, description, requires: [evidence_kind, ...]}` list.
  Different evidence kinds are not interchangeable.
- `policy.bindings`: explicit `{host, provider, account, allowed_actions,
  allowed_efforts, allow_uncontrolled_effort?}`. These values come from approved
  host configuration, not model self-identification. Empty bindings deny all.
- `policy.max_active_executions`: approved concurrency envelope. It is not a
  prescribed team size. Direct non-LLM work needs no model execution record.

No API edits the current acceptance or policy in place. A product change creates
another Mission/baseline with explicit approval. Existing records remain intact.

## Mutation envelope

MCP `oser_mission_apply` takes:

```json
{
  "mission": "M1",
  "operation": "checkpoint.record",
  "payload": {"summary": "Current durable facts", "next_action": "Next acceptance check"},
  "expected_revision": 0,
  "event_key": "M1-checkpoint-001",
  "actor": "owner-a",
  "owner_epoch": 0
}
```

CLI equivalent: `oser apply --mission M1 --operation checkpoint.record
--payload FILE --revision 0 --event-key M1-checkpoint-001 --actor owner-a
--epoch 0 --project PROJECT`. Prefer structured MCP arguments for an agent.

| Operation | Required payload | Meaning |
|---|---|---|
| `catalog.record` | Capability snapshot below | Record externally sourced runtime evidence; does not probe or load profiles |
| `execution.open` | `ref`, `native_ref`, `request` | Admit a plan and register a segment; does **not** start an agent |
| `execution.receipt` | `ref`, `native_ref`, `status`, `observed_at`, `source_ref`, optional `observed`/`ttl_seconds` | Ingest actual native facts; may arrive after owner transfer |
| `execution.reconcile` | `ref`, `evidence_ref` | Hash a local reconciliation artifact for a terminal segment |
| `checkpoint.record` | `summary`, `next_action`, optional `runtime_state`, `waiting_for`, `external_wait_ref` | Save continuation facts; WAITING needs a durable dependency |
| `ownership.transfer` | `to`, `reason` | Requires current owner's checkpoint; increments epoch atomically |
| `evidence.record` | `criterion`, `kind`, `outcome`, `path`, `producer_ref` | Store pass/fail attestation plus artifact/source hashes |
| `blocker.set` | `id`, `summary`, optional `kind`, `resolved`, `evidence_ref` | Track blockers/approvals; resolving one does not grant new provider/deploy rights |
| `mission.complete` | `{}` | All acceptance evidence current/pass, no blockers, all registered executions reconciled without policy mismatch |

Execution status is normalized for closure: RUNNING, WAITING, INTERRUPTED,
UNKNOWN, COMPLETED, FAILED, CANCELLED. Preserve the original in `native_status`.
`relation: {from: EXISTING_SEGMENT, native_relation: NATIVE_VALUE}` is optional on
execution.open. Native relation vocabulary is open; it is not a fixed attempt
mode. Resume after a terminal segment gets a new segment, not a rewrite.

A receipt's `observed` may contain host/provider/account/model/effort. Fields not
observed are not filled from the requested plan. Mismatches are recorded and
block closure. Timestamps must be sourced, not reconstructed from fetch time.
Callbacks should use stable event IDs. Duplicate identical observations must
not reset a reconciled result.

## Capability snapshot

```json
{
  "schema": "nnc-oser/capabilities@1",
  "host": "actual-host",
  "provider": "approved-provider",
  "account": "local-account-reference",
  "observed_at": "SOURCE_TIMESTAMP_WITH_TIMEZONE",
  "ttl_seconds": 300,
  "source_ref": "host-method-or-evidence-reference",
  "evidence_state": "PROBED",
  "default_model": "runtime-returned-model-id",
  "aliases": {},
  "models": [{
    "id": "runtime-returned-model-id",
    "available": true,
    "efforts": ["native-level"],
    "default_effort": "native-level",
    "effort_scopes": ["turn"],
    "context_window": 32768
  }]
}
```

This is a **shape example, not a real probe result**. Importing it does not prove
its claims. `PROBED` is reserved for a real probe's output; don't let the agent
manufacture that label. Kernel validation can check structure, not attest the
truth of an arbitrary JSON file. Sandbox/launcher controls define trust.

`oser admit --request FILE` is pure. Request fields: `model` (default
`runtime_default`), `effort` (default `runtime_default`), `effort_scope` (default
`execution`), `action` (default `inference`), optional
`required_context_tokens` and explicit identity fields. Specify `turn` for a
Codex turn override, `current` only for a retained current Claude setting.
Missing/unsupported scope is denied instead of modifying the parent globally.

`ADMITTED` is ADMISSION_ONLY / NOT_STARTED. The host must execute via its native
interface and provide an observed receipt. Do not present admission as enforced
host settings or a completed model call. No marketing role-to-model map exists.

## Evidence and progress

`requires: ["test", "behavioral"]` needs both. A test result alone cannot close it.
All criteria are required, not weighted to hide missing critical gates. Progress
is accepted/total, **not** elapsed time or estimated remaining work.

Evidence is a RECORDED_ATTESTATION: kernel hashes the file and current declared
sources, but does not interpret arbitrary log text as truth or independently
re-run every test. An appropriate deterministic evaluator, reviewer or human UAT
must supply the claim. On source/artifact/authority drift, old evidence becomes
STALE and a completed Mission displays REOPENED. Current source fingerprinting
is conservative at Mission scope: all evidence may need revalidation after a
source change. Per-criterion impact graphs are deferred, not guessed.

Canonical artifact access is relative to the main project. Copy/export a child
worktree's evidence into a reviewed canonical artifact location before recording
it. The kernel does not silently follow external worktree paths.

## Usage import

`oser usage --mission M1 --input FILE.jsonl --adapter claude-code
--provider APPROVED_PROVIDER --account ACCOUNT --since ISO --until ISO`
accepts an explicit bounded time scope. `until` is exclusive. **Do not assign an
entire multi-Mission Root transcript to one Mission.** There is no implicit
whole-agent-per-attempt summation.

Neutral records use host/provider/account/session_ref/request_id/response_id,
`mode: snapshot` and input_tokens/output_tokens/cache_read_tokens/cache_write_tokens.
One native response is counted once; conflicting snapshots become INVALID.
Unknown identity remains UNKNOWN and cannot contaminate another Mission. Delta
or cumulative-stream conversion must be implemented by an adapter first.
Known subtotal is separate from total; imported coverage is not whole-account
coverage. No subscription percent, price or FLOP is manufactured from tokens.
