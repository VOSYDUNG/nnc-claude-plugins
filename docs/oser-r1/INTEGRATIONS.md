# Host integrations and observability limits

The **kernel** has no inference provider dependency. Adapters decode host wire
formats. Adding an adapter does not create a permission to use another provider
or copy project data to it. Each approved host/provider/account binding stays
separate. The default route is the host's native agent orchestration.

## Common stdio MCP entry

Launch from the intended project or pass its absolute path explicitly:

```text
python /absolute/path/to/plugins/nnc/oser/oser.py serve --project /absolute/project
```

Example MCP client configuration shape (adapt to the actual host's config file):

```json
{
  "mcpServers": {
    "nnc-oser": {
      "command": "python",
      "args": ["/absolute/path/to/plugins/nnc/oser/oser.py", "serve", "--project", "/absolute/project"]
    }
  }
}
```

Codex and Claude configuration file formats need not be the same. Configure the
above command through each host's documented MCP integration; do not copy
`mcpServers` JSON blindly into a TOML config. The server takes its trusted root
from launch arguments; tool calls cannot change it to another filesystem root.
It exposes tools only, no sampling capability, executable shell or open port.

## Claude plugin

`plugins/nnc/.mcp.json` uses `${CLAUDE_PLUGIN_ROOT}/oser/oser.py` and the launch
working directory. Verify the project root in the first Mission response.
The skill is `/nnc:ai-oser`. If `python` isn't the desired interpreter on this
machine, configure the explicit interpreter command in the host's MCP setup.
No global settings are overwritten and no model-profile files are generated.

Optional command hooks/statusLine must be reviewed and installed by the user or
a trusted host setup action. This candidate does not auto-edit settings:

```text
python /absolute/plugin/oser/oser.py statusline --project /absolute/project --provider APPROVED_PROVIDER --account LOCAL_ACCOUNT_REF
python /absolute/plugin/oser/oser.py hook --project /absolute/project --provider APPROVED_PROVIDER --account LOCAL_ACCOUNT_REF
```

Both read native JSON from stdin, write local observations, and never call a
model. The hook returns no blocking instruction. SessionEnd cannot veto an exit.
A Stop/SubagentStop event is not proof that the Mission passed acceptance.

StatusLine quota/context are accepted only if the actual callback exposes those
fields. A callback has no universal source-update timestamp; therefore this
collector retains the observed values with freshness UNKNOWN. Do not invent
`observed_at=now` merely because a cached callback ran again. A trusted native
collector with a genuine source observation time can use `oser health --input
FILE --adapter claude-code --observed-at ISO --provider ... --account ...`.

`claude_current_catalog()` sees the **current model only** and retained effort.
It does not discover a complete model lineup or prove per-child effort control.
Use a supported host probe/registration path for those controls before recording
a wider catalog. Full live Claude catalog/effort actuation is still pending.

## Codex App Server discovery

```text
oser probe --host codex --project PROJECT --provider APPROVED_PROVIDER --account LOCAL_ACCOUNT_REF
```

This opt-in probe starts a short-lived local `codex app-server`, performs:
`initialize`, `initialized`, paginated `model/list`, `account/rateLimits/read`,
then terminates its own child process. No thread/start, turn/start, model
inference, login, approval, credential-file scan or existing-session wake occurs.
RPC errors and timeouts are reported explicitly. Default time budget is 15s.
Catalog response is PROBED; this proves read-only discovery, not effort actuation
or model suitability. `isDefault` is not a latest-version guarantee.

Provider/account arguments are the caller's approved binding to the configured
App Server, **not** an identity inferred from a model string. Confirm that binding
against the host/account setup. The probe must not be used as a way to silently
switch providers. Rate limits may be unavailable in a particular auth mode.

Record returned catalog via `catalog.record`, returned samples via `health`, and
retain the native output as provenance. No auto-admission occurs when a probe is
run. The actual native model execution remains the agent/host's responsibility.

## Read versus report versus enforcement

- DOCUMENTED: schema/instructions are known; no local proof yet.
- PROBED: bounded host operation returned capability evidence.
- OBSERVED: actual execution/callback provided a fact.
- UNKNOWN/UNAVAILABLE: no usable source or unsupported feature.
- ADMISSION_ONLY: local request passes policy; no native mutation is claimed.
- RECORDED_ATTESTATION: caller supplied evidence claim plus integrity hashes.

An agent or arbitrary local user can lie in JSON. These states are provenance
labels, not cryptographic authentication. Keep trusted acquisition outside
untrusted prompts and retain native evidence. This is not a multi-tenant server.

## Recovery, Health and data boundaries

There is no daemon/wake channel in this candidate. It reports
MANUAL_RESUME_REQUIRED/UNAVAILABLE rather than simulating an always-on worker.
Use checkpoints, native execution references and replay-safe receipts. A later
adapter may implement native wake after explicit conformance tests.

Runtime view separates checkpoint `reported_runtime_state` from fresh native
receipt observations. A lack of progress does not auto-kill an agent. Quota is
per-account/per-provider/per-window; stale samples keep their last value labeled
STALE, not reset to zero. Full raw transcripts remain outside the parent context.

## Official interfaces used

- Claude plugin layout: https://code.claude.com/docs/en/plugins-reference
- Claude statusLine: https://code.claude.com/docs/en/statusline
- Claude lifecycle hooks: https://code.claude.com/docs/en/hooks
- Codex App Server: https://developers.openai.com/codex/app-server
- MCP lifecycle: https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle

These references describe potential host support. Test the installed version;
a web schema is not a local conformance result.
