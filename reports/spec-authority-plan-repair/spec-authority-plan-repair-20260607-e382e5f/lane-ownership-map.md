# Lane Ownership Map
# Sprint: FORMAT-FACTORY-SPEC-AUTHORITY-PLAN-REPAIR-FOR-SINGLE-GO-EXECUTION-001
# Run: spec-authority-plan-repair-20260607-e382e5f
# Date: 2026-06-07

---

## Lane Definitions (9 lanes)

| Lane ID | Name | Owner | Taskcards |
|---------|------|-------|-----------|
| L-COORD | Coordinator/Integration | Primary agent | TCA-000, TCA-024 |
| L-EVIDENCE | Evidence Import | Agent or subagent | TCA-001 |
| L-STATEMACHINE | State Machine + Taskcards | Primary or subagent | TCA-005, TCA-006 |
| L-GOVERNANCE | Governance + Supervisor Gate | Primary agent | TCA-007, TCA-008 |
| L-SCHEMA | Evidence Schema + Proof Graph | Specialist agent | TCA-002, TCA-015 |
| L-SELECTOR | Product Task Selector + Next-Action | Specialist agent | TCA-001, TCA-004 |
| L-VERIFY | Verification + Negative Tests | Test-focused agent | TCA-021, TCA-022 |
| L-ADVERSARIAL | Independent Review | Separate adversarial agent | (none — review only) |
| L-BUNDLE | Evidence Bundle | Coordinator | TCA-024 |

---

## Exclusive Write Ownership

| File | Lane | No other lane may write |
|------|------|------------------------|
| authority-healing-state-machine.json | L-STATEMACHINE | YES |
| authority-healing-taskcards.json | L-STATEMACHINE | YES |
| taskcard-state.json | L-STATEMACHINE | YES |
| plan-readiness-review.md | L-GOVERNANCE | YES |
| required-plan-repairs.md | L-GOVERNANCE | YES |
| verification-gates.json | L-VERIFY | YES |
| validate_repaired_plan.py | L-VERIFY | YES |
| adversarial-review.md | L-ADVERSARIAL | YES |
| final-summary.md | L-COORD | YES |
| plan-completeness-check.md | L-COORD | YES |
| SHA256-MANIFEST.txt | L-BUNDLE | YES |
| evidence-import-review.md | L-EVIDENCE | YES |

---

## Forbidden Paths (all lanes)

No lane may write to:
- `src/` — product source code (no src changes in plan-repair sprint)
- `.local/spec-cache/` — immutable spec storage (read-only during this sprint)
- `tools/supervisor/autonomous_cycle.py` — no supervisor modifications in plan-repair sprint
- `tools/supervisor/product_task_selector.py` — no selector modifications in plan-repair sprint

---

## Handoff Rules

1. L-COORD gates L-BUNDLE: cannot start until L-VERIFY validate_repaired_plan.py exits 0
2. L-ADVERSARIAL: reads all final artifacts; writes adversarial-review.md; CRITICAL findings trigger repairs
3. L-BUNDLE: starts only after all other lanes complete required artifacts
4. Lane conflict: L-COORD arbitrates; records in raw-logs/lane-conflicts.txt

---

## Overlap Check

No two lanes have conflicting exclusive write claims. All exclusive files are assigned to exactly one lane.

L-COORD and L-BUNDLE both write to `.local/spec-authority-plan-repair/${RUN_ID}/` but this is non-conflicting:
- L-COORD writes report files to reports/ directory
- L-BUNDLE copies them to .local/ and adds SHA256-MANIFEST.txt

The only shared file is `final-summary.md` (L-COORD exclusive) and the bundle copy action (L-BUNDLE read-only from reports/).
