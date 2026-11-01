# Formation — from vague idea to Mission

Formation is not a software waterfall. It reduces uncertainty until there is a
direction worth operating as a durable Mission.

## Reality audit

Capture only material facts:
- who currently does the work;
- current steps/tools/data;
- what hurts, how often, and baseline if known;
- what cannot change;
- what access/approval is available;
- what is still unknown.

## Research lane

Compare relevant classes, not a predetermined stack:
1. native capability/configuration;
2. existing product/SaaS;
3. reusable Skill/workflow/automation;
4. integration/composition;
5. custom build.

For each viable candidate, capture fit, source, unknowns and what must be tested.
The list can be shorter if the problem clearly excludes a class.

## Mission boundary

A Mission describes the outcome, not a host's internal plan. Internal tasks,
subagents, teams and workflows may change without rewriting acceptance.

At `MISSION_READY`, retain `direction_approval` with `approved_by`, an ISO-8601
`approved_at` with timezone, and `decision_ref` pointing to the human's actual
approval. Reuse approval already present in the session or authoritative record;
do not ask again or manufacture an approval. This is a recorded attestation, not
authentication, Mission initialization, or permission to deploy.
