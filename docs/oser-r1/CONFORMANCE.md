# R1 conformance boundary

Run `python -m unittest discover -s tests -v`. The suite creates disposable
projects and synthetic host payloads. The Codex probe test uses a real subprocess
running a deterministic fake App Server; it does not query a paid model.

The old 27-test v4 suite is retained unchanged to protect the compatibility lane.
Passing those tests does not rehabilitate historical v4 quantitative metrics.

| R1 gate | Implemented offline coverage | Still requires live validation |
|---|---|---|
| A01 BOOT-CROSS-HOST | Shared kernel, Claude/Codex decoders, neutral provider binding, MCP handshake | Actual Claude Code/Codex client loading and completing the same Mission |
| A02 CAPABILITY-TRUTH | Documented/stale/unknown denied; requested/resolved/receipt distinct; current-only Claude catalog | Trusted installed-host catalog collection and native receipt binding |
| A03 EFFORT-BOUNDARY | Default cannot bypass envelope; unsupported values/scopes denied; observed mismatch blocks closure | Actual per-child/turn effort actuation and host permission enforcement |
| A04 LATEST-RESOLUTION | Explicit native aliases; no guessed latest; open plan immutable on catalog refresh | Model catalog refresh policy and runtime upgrade behavior |
| A05 USAGE-BLOCK-REPLAY | Repeated blocks/import dedup; conflicting snapshot INVALID; missing identity UNKNOWN | Provider-specific cumulative/delta formats outside supported snapshots |
| A06 RESUME-REHOME | Open native relation labels; no double charge on cross-Mission rehome | Native resume lifecycle/event capture per host |
| A07 CRASH-LATE-RESULT | Reopen SQLite; late receipt after owner transfer; epoch/CAS; reconciliation and duplicates | Host crash, runner lifecycle, side-effect idempotency at each external system |
| A08 WAIT-NOT-STALL | Legal registered wait; no elapsed-time auto-kill; reported versus observed runtime | Host-specific liveness expectations and long-running jobs |
| A09 ACCEPTANCE-REGRESSION | Test ≠ behavioral kind; source/artifact/authority drift; fixed denominator | Trusted test/HIFI/UAT evaluator for the actual project |
| A10 QUOTA-STALE | Source-age truth; reset doesn't invent zero; account buckets separate | Genuine fresh subscription readings in each auth mode |
| A11 SAFETY-PERMISSION | Explicit account/action/effort admission; path confinement; no login/deploy tool | Native sandbox/approval guards; this library is not an OS security boundary |
| A12 QUIET-OBSERVER | Collector/view no model calls; identical sample no rewrite; no false wake | Opt-in supported wake/runner if later implemented |

## Adversarial cases included

Revision races, repeated event keys, source disappearance, same-time conflicting
receipts, future timestamps, duplicate terminal notifications, old-owner reuse,
Windows drive-relative paths, symlink escapes, cross-Mission unknown usage,
request metadata appearing on a later response block, reported RUNNING without
native observation, and stale execution observations.

## Do not confuse these results

- Python tests passing means the included contracts/fixtures pass.
- MCP handshake passing means this server's supported transport tests pass.
- Codex read-only probe passing on a machine means discovery works there.
- None of those prove autonomous end-to-end recovery, lower compute, a perfect
  model selector, or product/HIFI correctness on a real Mission.

Start the next evaluation in a disposable project: native host vs native+OSER
with the same Mission and acceptance. Add a custom selector only if it has a
specific falsifiable hypothesis. Reproduce 429 using a fixture, not deliberate
subscription exhaustion. Never copy one experiment's solution into the other.
