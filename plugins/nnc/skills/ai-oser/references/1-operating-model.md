# R1 Mission, not a prescribed organization

The durable unit is a Mission bound to approved authority and acceptance.
Physical sessions and agent topology may change. The kernel has no model-role
map, mandatory wave/packet or requirement for a permanent parent session.

Read the Mission before doing work. `init` records a fixed acceptance denominator
and approved resource policy. Requirement changes create a new Mission/baseline;
the agent cannot silently rewrite those fields through the state API.

State updates use revision CAS plus idempotency keys. On a conflict, read again;
do not overwrite another actor's revision. Ownership has an epoch so a stale
owner cannot continue changing canonical Mission decisions after transfer.

A checkpoint records facts, next action, open native executions and dependencies.
Idle/WAITING is valid while registered work runs. Completion requires current
acceptance evidence and reconciliation, not a conversational `end_turn`.
Late native receipts may be ingested after owner transfer without granting them
permission to change policy or acceptance.

Crash recovery uses the latest durable checkpoint and artifacts. SessionEnd is
not a guaranteed veto. This candidate has no automatic wake runner: expose
MANUAL_RESUME_REQUIRED rather than claiming background recovery.

The state API is not a security sandbox. Filesystem permissions, sandbox policy,
approved provider credentials and protected deployment actions belong to the
host. Do not let a generated memory note replace approved authority.
