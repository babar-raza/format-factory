# Supervisor-Generated Next Sprint Prompt
# Source sprint: FORMAT-FACTORY-SUPERVISOR-R102-STREAM-AWARE-REVIEW-CAMPAIGN-001
# Stream: supervisor
# Generated: 2026-06-03T13:42:32.746675
# ADVISORY ONLY — not a Format Factory authority document
# This is INPUT to the next sprint, not a gate approval or commit authorization.

---

## Sprint Focus
ADVANCE: Supervisor infrastructure — grading, continuation, stream prompts, evidence model

## Prior Sprint Summary
- Sprint ID: FORMAT-FACTORY-SUPERVISOR-R102-STREAM-AWARE-REVIEW-CAMPAIGN-001
- Evidence verdict: ACCEPTED
- Tests: 548 passed, 0 failed, 0 skipped
- Autonomous continue: True

## Section 1: Supervisor Infrastructure Work (Advisory — Always Execute)
- [pending] TASK-001: Harden grading engine — anti-skip and deep grading
- [pending] TASK-002: Improve continuation state machine and checkpoint logic
- [pending] TASK-003: Stream-aware prompt generation and anti-regression
- [pending] TASK-004: Evidence model hardening — manifest, materialization, review package
- [pending] TASK-005: Replay test infrastructure
- [pending] TASK-006: Write evidence declaration and run supervisor autonomous-cycle

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
- Lane C1: Governance discovery — read AGENTS.md, policies, context-pack
- Lane C2: Repair lanes — address any open contradictions from prior sprint
- Lane C3: Grading engine hardening and anti-skip checks
- Lane C4: Continuation state machine and checkpoint logic
- Lane C5: Stream-aware prompt generation and replay infrastructure
- Lane C6: Evidence — declaration + autonomous-cycle
- Lane C7: Adversarial — challenge all claims before finalizing

## Project Memory Context
```

```

---
END OF SUPERVISOR-GENERATED NEXT SPRINT PROMPT
