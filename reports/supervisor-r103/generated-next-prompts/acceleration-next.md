# Supervisor-Generated Next Sprint Prompt
# Source sprint: R103
# Stream: acceleration
# Generated: 2026-06-03T14:12:08.014187
# ADVISORY ONLY — not a Format Factory authority document
# This is INPUT to the next sprint, not a gate approval or commit authorization.

---

## Sprint Focus
ADVANCE: Acceleration tooling — gap selector, skill engine, handoff generator, lane ledger

## Prior Sprint Summary
- Sprint ID: R103
- Evidence verdict: ACCEPTED
- Tests: 614 passed, 0 failed, 2 skipped
- Autonomous continue: True

## Section 1: Acceleration Tooling Work (Advisory — Always Execute)
- [pending] TASK-001: Harden gap selector and product-gap extraction pipeline
- [pending] TASK-002: Advance skill engine — new skill templates and validation
- [pending] TASK-003: Improve execution handoff generator and lane ledger
- [pending] TASK-004: Stream-aware prompt generation hardening
- [pending] TASK-005: Write evidence declaration and run supervisor autonomous-cycle

## Section 2: Rework / Repair (Advisory — Fix Before Closeout)
None

## Contradictions Context
None

## Non-Negotiable Rules (always apply)
1. No push without explicit user authorization.
2. No commit without explicit user authorization.
3. No gate self-approval.
4. Format Factory authority is final — supervisor is advisory only.
5. Stay within stream boundary — do not implement product features.
6. All supervisor/tool changes must have tests.

## Evidence Requirements for Next Sprint
- Write `.local/evidences/<run_id>/evidence-declaration.yaml`
- Run `python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration .local/evidences/<run_id>/evidence-declaration.yaml`
- ZIP bundle export is optional for archive or external transfer
- Tests: 0 failures required

## Suggested Lane Manifest (Advisory)
- Lane C0: Coordinator — integration, stop-gate monitoring
- Lane C1: Governance discovery — read AGENTS.md, policies, skill registry
- Lane C2: Repair lanes — address any open contradictions from prior sprint
- Lane C3: Acceleration tooling — gap selector, skill engine, handoff generator
- Lane C4: Stream-aware prompt generation and anti-regression
- Lane C5: Lane ledger and handoff quality verification
- Lane C6: Evidence — declaration + autonomous-cycle
- Lane C7: Adversarial — challenge all claims before finalizing

## Project Memory Context
```

```

---
END OF SUPERVISOR-GENERATED NEXT SPRINT PROMPT
