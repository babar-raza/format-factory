# Supervisor-Generated Next Sprint Prompt
# Source sprint: FORMAT-FACTORY-SUPERVISOR-R102-STREAM-AWARE-REVIEW-CAMPAIGN-001
# Stream: skills
# Generated: 2026-06-03T13:42:32.741420
# ADVISORY ONLY — not a Format Factory authority document
# This is INPUT to the next sprint, not a gate approval or commit authorization.

---

## Sprint Focus
ADVANCE: Governed execution — skill commands, validation fixtures, transcript ledger

## Prior Sprint Summary
- Sprint ID: FORMAT-FACTORY-SUPERVISOR-R102-STREAM-AWARE-REVIEW-CAMPAIGN-001
- Evidence verdict: ACCEPTED
- Tests: 548 passed, 0 failed, 0 skipped
- Autonomous continue: True

## Section 1: Governed Skill Work (Advisory — Always Execute)
- [pending] TASK-001: Validate and expand governed skill commands
- [pending] TASK-002: Add skill transcript ledger tests
- [pending] TASK-003: Harden skill registry schema and add new skill templates
- [pending] TASK-004: Skill execution isolation and rollback testing
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
- Lane C3: Skill command validation and expansion
- Lane C4: Transcript ledger testing and query capabilities
- Lane C5: Skill execution isolation and rollback testing
- Lane C6: Evidence — declaration + autonomous-cycle
- Lane C7: Adversarial — challenge all claims before finalizing

## Project Memory Context
```

```

---
END OF SUPERVISOR-GENERATED NEXT SPRINT PROMPT
