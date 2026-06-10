# Supervisor-Generated Next Sprint Prompt
# Source sprint: FORMAT-FACTORY-ACCELERATION-R101-DEEP-TOOLING-MEGA-TRAIN-001
# Generated: 2026-06-03T13:10:42.385777
# ADVISORY ONLY — not a Format Factory authority document
# This is INPUT to the next sprint, not a gate approval or commit authorization.

---

## Sprint Focus
ADVANCE: Supervisor infrastructure — grading, continuation, stream prompts, evidence model

## Prior Sprint Summary
- Sprint ID: FORMAT-FACTORY-ACCELERATION-R101-DEEP-TOOLING-MEGA-TRAIN-001
- Evidence verdict: ALL_ACCEPTED_AUTONOMOUS_CONTINUE
- Tests: 816 passed, 0 failed, 0 skipped
- Autonomous continue: True

## Section 1: New Product Work (Advisory — Always Execute)
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
4. No active .vscode/mcp.json without MODE 4 approval.
5. No Task Master / Ruflo init without MODE 3+ authorization.
6. Load `.local/supervisor/selected-product-gaps.json` and `.supervisor/skill-registry.yaml` before product work.
7. All gate closures require human approval (gates 1-11).
8. Format Factory authority is final — supervisor is advisory only.
9. No direct ad-hoc `src/` edits. Use a governed skill or generated execution handoff.
10. Every `src/` edit requires an entry in `reports/r90/product-code-change-ledger.json`.

## Evidence Requirements for Next Sprint
- Write `.local/evidences/<run_id>/evidence-declaration.yaml`
- Run `python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration .local/evidences/<run_id>/evidence-declaration.yaml`
- ZIP bundle export is optional for archive or external transfer
- Final verdict must contain: VERDICT: <enum>
- All SHAs must be filled (no PENDING markers in final state)
- Tests: 0 failures required

## Suggested Lane Manifest (Advisory)
- Lane C0: Coordinator — integration, manifest authority, stop-gate monitoring
- Lane C1: Governance discovery — read AGENTS.md, GOVERNANCE.md, master-plan state
- Lane C2: Repair lanes — address any open contradictions from prior sprint
- Lane C3: Governed implementation — selected gaps, skill registry, product-code ledger
- Lane C4: Dogfood export — use a Format Factory-produced library
- Lane C5: Package/install proof — build physical artifacts and run installed workflows
- Lane C6: Evidence — declaration + autonomous-cycle
- Lane C7: Adversarial — challenge all claims before finalizing

## Acceptance Criteria Per Lane
(Fill from open taskcards in taskcards/ directory)

## Project Memory Context
```

```

---
END OF SUPERVISOR-GENERATED NEXT SPRINT PROMPT
