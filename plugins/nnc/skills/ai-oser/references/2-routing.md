# R1 capability admission

An agent may request a concrete model/alias from the actual catalog or retain a
known runtime default. OSER checks eligibility, not whether the model is clever
enough. Evidence and evaluation inform future choices; provider positioning is
a dated prior, not a permanent role.

Identify host, provider and account separately. A capability snapshot needs a
source reference, observation time, validity period and evidence state. Only
PROBED/OBSERVED snapshots qualify for admission. A newly written config is not
proof of runtime activation. JSON import trusts its producer; prefer a real host
probe over a manually asserted evidence label.

Effort values and override scopes stay native. Approval is an explicit allowed
set for each host/provider/account binding. Default must resolve inside that set.
No silent fallback and no temporary parent-effort mutation around parallel child
launches. An unsupported scope is denied, not simulated.

`latest` is legal only when an actual catalog alias resolves it. Do not invent a
newer ID, sort marketing model names to infer quality, or silently change an open
execution. Store its resolved candidate and capability snapshot for provenance.

ADMITTED means the requested plan passed local policy checks. It does not start
inference and does not mean the host applied the plan. Native receipt records are
separate. The agent uses native delegation after admission; no second mandatory
routing model is inserted into every interaction.
