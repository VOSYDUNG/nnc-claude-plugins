---
name: ai-oser
description: NNC OSER Human Mission Space. Use for durable Mission state, authority, evidence, checkpoints, Health, interrupted work and capability admission. If the user has only a vague idea or does not know what to build, use mission-formation first; if the Mission is clear, use adaptive-delivery. No fixed agent/model topology.
---

# NNC OSER — Human Mission R2

This skill is the kernel/admin discovery entry, not a workflow scheduler or permission grant.
Use `mission-formation` before Mission lock and `adaptive-delivery` after the Mission is clear.
The CLI/MCP implements state contracts. Host permissions remain authoritative.

1. Read the current Mission with `oser status --json` or `oser_mission_read`.
   No state yet: ask for or derive a proposed Mission contract, then have its
   authority, acceptance and resource envelope approved before `init`.
2. Work toward that Mission. Proactively choose direct work, tools, delegation,
   parallel work and appropriate review. No mandatory team, wave or packet.
3. Select only real runtime candidates within the approved envelope. Native
   selectors are preferred where appropriate. Do not guess latest model IDs,
   infer permissions from your identity, or assume effort names match providers.
4. Record useful checkpoints and evidence through structured OSER tools. Waiting
   while registered children run is legal; `end_turn` is not Mission completion.
5. Reconcile terminal results before completion, including late notifications.
   Missing observability is UNKNOWN, never "everything is healthy".

## Interfaces

`oser init --contract FILE` · `oser status --json` · `oser doctor` ·
`oser serve` · `oser admit --request FILE` · `oser health` · `oser usage`.
All project commands accept `--project DIR`. CLI JSON inputs accept `-` for stdin.
For an agent, prefer `oser_mission_init`, `oser_mission_read`,
`oser_mission_apply`, `oser_admit`, `oser_health`, `oser_usage` MCP tools.

Read only the relevant reference:
- [Mission and continuity](references/1-operating-model.md)
- [Capability and admission](references/2-routing.md)
- [Evidence, usage and Health](references/3-measurement.md)

The fuller repository operation contracts are in `docs/oser-r1/OPERATIONS.md`.
No code here can grant provider access, read credentials, prevent all exits,
spawn arbitrary models, or wake a session unless the host actually supports it.

## Existing v4 project

`oser migration-plan` is read-only. Preserve the v4 ledger and project rules;
review active legacy instructions before R1 initialization. Do not delete them
by guesswork. `oser legacy ...` keeps compatibility with an explicit warning.
