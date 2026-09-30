# R1 measurement and Health

Mission progress measures current acceptance coverage, not task counts, elapsed
time or remaining engineering effort. Every criterion may require distinct kinds
of evidence. Passing a unit test is not a substitute for behavioral/UAT evidence.
Evidence carries baseline, source fingerprint and artifact hash. Relevant source
or artifact changes make it stale. Recorded attestations still require a trusted
evaluator; the kernel does not semantically validate arbitrary log text.

Usage counts one native response snapshot once, even if repeated in multiple
content blocks or re-imported. Conflicting snapshots, unsupported delta modes or
missing identity remain INVALID/UNKNOWN. A response cannot be charged again by
re-homing it into a second Mission. Totals cover imported records only.
Cache read/write, input and output remain separate; thinking is not added again
to output. No token-to-subscription-percent or physical compute conversion.

Quota samples are scoped by host/provider/account/bucket. Keep source observation
time separate from fetch time. Callback age may be unknown. Do not pool quota
percentages or infer that a reset guarantees zero use. A missing source is UNKNOWN.

Runtime self-reports are distinct from recorded native observations. Lack of new
acceptance for a while does not by itself prove a stall. The local collector/view
has no model heartbeat and no automatic wake. Full logs stay outside context;
read details only to resolve an actual decision.

Legacy v4 quantitative metrics are historical and INVALIDATED as a new test baseline.
