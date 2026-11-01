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

## QA/QC sơ bộ — early verification

QA/QC sơ bộ is the early phase of verification inside Formation. It runs after
the direction is approved (DECISION) and before `MISSION_READY`, and its output is
the Mission's common rules. QA designs how quality and outcome will be assured;
QC names the concrete checks that will run during delivery (Workflow B).

Produce four things:
1. Outcome acceptance criteria, each listing the evidence kinds it `requires`.
   This maps directly onto the `oser init` contract:
   `acceptance: [{id, description, requires: [...]}]`.
2. Invariants that must not be violated: source-of-truth data, authority, safety
   and privacy.
3. The QC checks/evaluators that will produce each evidence kind in delivery, and
   who or what evaluates: deterministic test, reviewer, or human UAT.
4. Remaining unknowns and how each will be reduced (investigate, test-first, pilot).

Rules:
- No QA/QC sơ bộ → not `MISSION_READY`.
- These rules are carried into the Mission draft and locked by the R1 kernel as the
  fixed acceptance denominator. Changing them after lock is a Delta Mission.
- Delivery runs the QC checks defined here; a passing test is still separate from
  real-world use and acceptance.

## Mission boundary

A Mission describes the outcome, not a host's internal plan. Internal tasks,
subagents, teams and workflows may change without rewriting acceptance.

At `MISSION_READY`, retain `direction_approval` with `approved_by`, an ISO-8601
`approved_at` with timezone, and `decision_ref` pointing to the human's actual
approval. Reuse approval already present in the session or authoritative record;
do not ask again or manufacture an approval. This is a recorded attestation, not
authentication, Mission initialization, or permission to deploy.
