# Autonomous Supervisor Audit — Format Factory Machinery Audit v2
# Sprint ID: ff-machinery-readiness-audit-v2-20260621-827f5a52

## Supervisor State Summary

| Component | Status | Evidence |
|-----------|--------|---------|
| approval-gates.md | AUTONOMOUS_CONTINUE: YES | reports/supervisor/approval-gates.md |
| continuation-signal.json | state=YES, iter=10 | .local/supervisor/continuation-signal.json |
| active-plan-lock.json | TERMINAL_CLOSED (keen-dancing-hopper) | .local/supervisor/active-plan-lock.json |
| session-resume.md | Last sprint: ACCEPTED, 1490 tests | reports/supervisor/session-resume.md |
| mode | MODE 4 (ACTIVE_MCP_ACTIVATION) | approval-gates.md |

## Plan Lock Analysis (UPDATED)

Prior audit: "Plan lock IN_PROGRESS — BLOCKS autonomy"
Current: `status: TERMINAL_CLOSED`, `track_type: product`

By GAP-WF-004 fix (commit f03234b0), TERMINAL_CLOSED on a product-track plan does NOT
block the product-track continuation. The machinery track can still start.

Remaining concern: Is there a machinery track? No. There is only a product track.
Lane separation is still absent.

## Governance Validators

Tools: tools/supervisor/governance_validators.py (~2953 LOC), governance_validator_runner.py

Validators added since prior audit:
- V45: test path correction (commit 827f5a52)
- V46: validate_skill_transcript — requires skill transcripts for skill-attributed work

Current count: ~40 validators (38 active at prior audit + V45 + V46)

Dirty files: governance_validators.py MODIFIED (uncommitted additions)

Known pre-existing test failures: 5 tests in TestRunAllValidators fail with
`ModuleNotFoundError: No module named 'tools'` (import issue, not validator logic).

## Key Validator Coverage

| Risk | Validator | Active |
|------|-----------|--------|
| Monolith detection | V35 (monolith_detection_validator) | YES |
| Analytics rotation suspension | V42 | YES |
| Spec fact refs validation | validate_spec_fact_refs | YES |
| Deepening suspension | V42 | YES |
| GOV_BLOCK:monolith_detection | enforced in autonomous_cycle.py Step 2d3 | YES |
| TC-GUARD-001 (no gap_ledger_ref) | BLOCK mode | YES |
| TC-GUARD-002 (purposeful check) | grade_declared_work.py | YES |
| QName compliance validation | NOT IN VALIDATORS | NO |
| Backfill required before migration | NOT IN VALIDATORS | NO |
| Lane boundary enforcement | NOT IN VALIDATORS | NO |
| SAL facts freshness | NOT IN VALIDATORS | NO |

## Critical Missing Validators

1. **No QName compliance gate** — product source commits are never blocked for missing spec_qname
2. **No SAL derivation gate** — no validator requires facts to trace to verified spec text
3. **No lane boundary enforcement** — product and machinery share one track
4. **No capability-compiler execution gate** — sprint can claim capability coverage without running compiler

## Continuation Analysis

check_continuation.py: returns CONTINUE (YES state, iter=10, no SESSION_MISMATCH)

But: iteration=10 is approaching max_iterations (typically 20 by policy). At iter>=20,
governed rollover resets to 0. This is not a stop — just a note.

The `stream_field_match` false stop from memory notes is repaired (stale plan locks fixed).

## Autonomous Loop Readiness

| Capability | Status |
|-----------|--------|
| Sprint closeout (declaration → cycle → review) | WORKS |
| check_continuation.py | WORKS — returns CONTINUE |
| SAL-backed work selection | NOT DONE (gap-ledger reads, not SAL-driven) |
| Lane separation | ABSENT |
| Gate 11 STOP enforcement | PARTIAL (requires user approval, not hard-coded stop) |
| Unattended FODS/FODT deepening | CONDITIONALLY READY |
| Recovery from context exhaustion | WORKS (session-resume.md) |

## Lane Separation — STILL ABSENT

The system has:
- ONE product track (session-product.id)
- ONE machinery track (session-machinery.id)

But these two session files just track session IDs for continuation isolation.
They do NOT represent separate work queues, file ownership lists, or collision guards.

Prior audit: "Lane separation ABSENT — single product track"
Current: machinery and product session files exist but they are identity markers,
not true lane isolation with separate state, ledgers, and ownership rules.
