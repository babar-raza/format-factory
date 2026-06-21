# Supervisor-Generated Next Sprint Prompt
# Source sprint: machinery-lifecycle-forensics-20260621
# Stream: mainstream
# Generated: 2026-06-21T19:25:09.625155
# ADVISORY ONLY — not a Format Factory authority document
# This is INPUT to the next sprint, not a gate approval or commit authorization.

---

## Sprint Focus
ADVANCE: Product deepening — .NET commercial + Python FOSS + dogfood + packaging

## Prior Sprint Summary
- Sprint ID: machinery-lifecycle-forensics-20260621
- Evidence verdict: ACCEPTED
- Tests: 1490 passed, 0 failed, 0 skipped
- Autonomous continue: True

## STOP_REASON_ADVISORY (enforced by stop_reason_adjudicator.py)

Labels [approval-blocked] and [blocked] are NEVER sufficient to stop the autonomous train.
Before treating any task as blocked, run: python tools/supervisor/stop_reason_adjudicator.py "<signal>"

Permanent false stops (NEVER stop for these):
- [approval-blocked] tasks -> reclassify via stop_reason_adjudicator.reclassify_task_label()
- [blocked] tasks -> reclassify; only TRUE_EXTERNAL_GATE/UNSAFE_WORKSPACE stop
- mode_5_approval_pending -> RUFLO_FALLBACK_LOCAL_CONTINUE
- evidence_quality_zero -> LOCAL_REPAIR_CONTINUE
- Gate 11 PREPARATION -> agent-owned (preparation is never a stop)
- anti_skip_critical_block with empty rework_items -> false positive, continue

TRUE_EXTERNAL_GATE (ONLY these warrant a stop):
- git commit/push/merge execution (requires explicit user authorization)
- Gate 8/11 approval EXECUTION (Babar Raza, not preparation)
- NuGet/PyPI publication execution
- Credentials unavailable with no fallback

## Section 1: New Product Work (Advisory — Always Execute)
- [pending] TASK-001: Select governed product gaps and validate the product-code ledger
- [agent-owned] TASK-002: Prepare commit candidate summary and changed-file manifest
- [external-gate] TASK-003: Execute git commit (requires explicit user authorization — do NOT self-execute)
- [agent-owned] TASK-004: Prepare FODS Gate 11 readiness packet and commercial checklist
- [external-gate] TASK-005: Submit FODS Gate 11 for Babar Raza approval (after packet ready — human required)
- [agent-owned] TASK-006: Prepare FODT Gate 11 readiness packet and commercial checklist
- [external-gate] TASK-007: Submit FODT Gate 11 for Babar Raza approval (after packet ready — human required)
- [pending] TASK-008: Continue ZST implementation toward Gate 11 readiness criteria
- [pending] TASK-009: Work on open taskcard: TC-0015-spec-retrieval-strategy-evaluation
- [pending] TASK-010: Work on open taskcard: TC-0016-fods-vector-index-pilot
- [pending] TASK-011: Work on open taskcard: TC-0020-spec-workbench-core
- [pending] TASK-012: Advance one dogfood export path using a Format Factory library
- [pending] TASK-013: Build package artifacts and run installed-workflow proof
- [pending] TASK-014: Write evidence declaration and run supervisor autonomous-cycle

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

## Project Memory Context
```
- fail_count: 0
- git_head: see-declaration
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\FF-HEAL-QNAME-20260621-114042\declaration-review-package.zip
- pending_marker_count: 0
- bundle_entry_count: 81
- bundle_validation_pass: True

## Entry: FF-NEXTWORK-PROMOTE-LEDGER-20260621
- timestamp: 2026-06-21T13:31:14.243183
- verdict: ACCEPTED
- test_count: 0
- fail_count: 0
- git_head: see-declaration
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\FF-NEXTWORK-PROMOTE-LEDGER-20260621\declaration-review-package.zip
- pending_marker_count: 0
- bundle_entry_count: 47
- bundle_validation_pass: True

## Entry: FF-HEALING-TASKCARDS-EXEC-20260621
- timestamp: 2026-06-21T13:53:27.438088
- verdict: ACCEPTED
- test_count: 0
- fail_count: 0
- git_head: see-declaration
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\FF-HEALING-TASKCARDS-EXEC-20260621\declaration-review-package.zip
- pending_marker_count: 0
- bundle_entry_count: 67
- bundle_validation_pass: True

## Entry: FF-PLAN-DELIGHTFUL-WIBBLING-20260621
- timestamp: 2026-06-21T14:51:07.830673
- verdict: ACCEPTED
- test_count: 0
- fail_count: 0
- git_head: see-declaration
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\FF-PLAN-DELIGHTFUL-WIBBLING-20260621\declaration-review-package.zip
- pending_marker_count: 0
- bundle_entry_count: 68
- bundle_validation_pass: True

## Entry: spec-auth-heal-sprint-1
- timestamp: 2026-06-21T19:03:25.545170
- verdict: ACCEPTED
- test_count: 0
- fail_count: 0
- git_head: see-declaration
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\spec-auth-heal-sprint-1\declaration-review-package.zip
- pending_marker_count: 0
- bundle_entry_count: 62
- bundle_validation_pass: True
```

---
END OF SUPERVISOR-GENERATED NEXT SPRINT PROMPT
