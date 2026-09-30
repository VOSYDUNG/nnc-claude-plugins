# NNC OSER — Mission R1

**5.0.0-rc.1 · test candidate, not a production certification.**

NNC OSER keeps a project's Mission, approved authority, acceptance evidence,
continuation state and Health durable while the current agent chooses how to
work. It does **not** prescribe a Governor, model family, task roster, effort
ladder or number of agents.

The repository retains its Claude-plugin packaging name. The R1 Python kernel
and stdio MCP server also work outside Claude Code: Codex and other hosts connect
through their own supported interface. No inference provider SDK is required.
Python **3.9+**, standard library, Git for linked-worktree resolution.

## Test this branch

```bash
git clone --branch refactor/oser-vnext-r1 https://github.com/VOSYDUNG/nnc-claude-plugins.git
cd nnc-claude-plugins
python -m unittest discover -s tests -v
python plugins/nnc/oser/oser.py version
python examples/r1_demo.py
```

The demo creates a disposable project, runs a real deterministic check and shows
Mission progress plus UNKNOWN quota. It does not call a model, consume a paid
quota, touch another project or deploy anything.

## Use with a project

Start from [the example contract](examples/r1-contract.example.json), replacing
its project-specific paths, acceptance and approved account bindings. An empty
`bindings` list denies all model-resource admission; it never invents credentials.

```bash
python /path/to/plugins/nnc/oser/oser.py init --project /path/to/project --contract /path/to/approved-contract.json
python /path/to/plugins/nnc/oser/oser.py status --project /path/to/project --json
python /path/to/plugins/nnc/oser/oser.py doctor --project /path/to/project
python /path/to/plugins/nnc/oser/oser.py serve --project /path/to/project
```

`init` creates `.nnc-oser/state.sqlite3` and a small `BOOTSTRAP.md`; it does not
overwrite `AGENTS.md`, `CLAUDE.md`, host settings or model profiles. After review,
reference the bootstrap file from the project's host instructions. Prefer MCP
structured arguments over manually constructing JSON through a shell.

### What runs today

| R1 component | Implemented behavior |
|---|---|
| Mission state | SQLite transaction + revision CAS, idempotent events, owner epochs, checkpoints |
| Acceptance | Fixed per-Mission criteria, evidence kinds, content hashes, source/authority drift invalidation |
| Admission | Current catalog + explicit host/provider/account/action/effort envelope; requested/resolved distinct from observed |
| Continuity | Registered open executions, legal waiting, late receipt reconciliation, ownership transfer |
| Measurement | Snapshot dedup by native response identity; conflicting/missing records INVALID/UNKNOWN |
| Health | Scoped quota/context snapshots, source freshness, quiet text view; no model heartbeat |
| Claude adapter | statusLine and lifecycle decoding, current-model-only snapshot, transcript usage decoder |
| Codex adapter | model/list and rate-limit decoding; opt-in bounded App Server discovery with no model turn |
| MCP | Six local structured tools; no sampling, shell-execution, deployment or login tool |

### What this candidate does **not** claim

- Admission is **not** a host sandbox, an inference call or proof that a model
  honored its requested settings. Observe a native receipt separately.
- A catalog imported from JSON is only as trustworthy as its producer. Use
  actual host probes, not a model's self-description; local file access is not
  a cryptographic approval boundary.
- Evidence is a recorded evaluator/host attestation with integrity checks. A log
  hash does not prove a behavioral claim. Use the correct evaluator or human UAT.
- No automatic model spawning, quota-based scheduler, parent effort mutation,
  auto-recovery daemon, wake injection or production deployment is installed.
- `SessionEnd` cannot prevent a crash. Recovery is explicitly
  `MANUAL_RESUME_REQUIRED` until a host-supported runner is implemented/tested.
- Quota source age missing means UNKNOWN. Repeating an old callback is not fresh
  subscription data. Model-specific limits are not inferred from token totals.
- No claim of lower total compute or of complete live Claude/Codex conformance.

## Claude plugin and Codex integration

On an installed release, the Claude entry is `/nnc:ai-oser`; bundled `.mcp.json`
exposes the local server. This branch is **not** published to `main` by testing it.
Use your host's supported local-plugin loading or configure stdio directly.
Codex does not need a Claude plugin installer: point its MCP client at the same
Python `serve --project ...` command.

See [integrations and trust boundaries](docs/oser-r1/INTEGRATIONS.md),
[operation contracts](docs/oser-r1/OPERATIONS.md),
[test matrix](docs/oser-r1/CONFORMANCE.md) and
[migration guide](docs/oser-r1/MIGRATION.md).

## v4 compatibility

Old commands remain available with a prominent warning. A v4 project still uses
its original doctor/status unless R1 was explicitly initialized. R1 `init`
refuses an active v4 manifest instead of silently mixing both instruction sets.

```bash
oser migration-plan --project /path/to/v4-project  # inventory only, zero writes
oser legacy doctor --project /path/to/v4-project
```

The old `oser_core/`, catalogs and templates are legacy compatibility data, not
R1 routing policy. Historical quantitative metrics are **INVALIDATED** as a
baseline because response-block and execution-reuse accounting was unreliable.
Raw/private project transcripts are deliberately not included in this repository.

MIT · NNC Lao Group
