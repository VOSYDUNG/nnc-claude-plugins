# From v4 to R1 without corrupting an active project

R1 is a test candidate. Do not update every production project automatically.
Keep v4 source history, ledger, raw transcripts and project-owned authority.
No private project artifacts should be committed to this public plugin repo.

## First: inspect, do not mutate

```text
oser migration-plan --project PROJECT
oser legacy doctor --project PROJECT
```

The plan reports the legacy manifest and hashes of relevant instruction files.
It makes zero writes. R1 init refuses `.claude/oser/project.json` while active.
Older install/update/migrate/ledger/metrics/root/quota commands are routed to a
warned legacy lane; v4 project doctor/status remain compatible.

## Review before transitioning a project

1. Checkpoint the running Mission and outstanding native executions; don't kill
   background work or remove its worktree just to switch the plugin.
2. Preserve current v4 artifacts in Git/backup. Reconcile the project's generated
   CLAUDE block, CONTROL-PLANE and relevant memory references so they do not still
   impose a mandatory Governor/model family. Preserve business/safety invariants.
3. Review old managed host settings and temporary effort definitions. Remove only
   entries actually owned by the old installation, with the owner's approval.
4. Once explicitly archived, move the old manifest out of its active path. R1
   does not guess which project-owned files are safe to delete.
5. Create a new approved Mission contract, initialize R1 and reference its small
   bootstrap from host project instructions. Import actual capability evidence.
6. Run conformance plus a small Mission before relying on unattended delivery.

There is intentionally no destructive `v4 -> R1 --force` migration. Historical
wave/packet acceptance cannot be translated into verified R1 acceptance without
reviewing its evidence. In particular, old token totals and first-pass ratios
are not imported as valid benchmarks.

## Rollback

Keep the previous plugin version/commit and the archived v4 configuration. Stop
new R1 writes before restoring the older project setup. R1 `.nnc-oser/` is a
separate store and need not overwrite v4. Do not reset project product code,
force-push branches, remove worktrees or revert real deployments automatically.

`5.0.0-rc.1` changes on this branch are not a production release or go-live approval.
