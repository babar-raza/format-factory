# Supervisor-Generated Next Sprint Prompt
# Source sprint: convergence-product-verify-20260624-3f98f85d
# Stream: mainstream
# Generated: 2026-06-24T12:51:09.262045
# ADVISORY ONLY — not a Format Factory authority document
# This is INPUT to the next sprint, not a gate approval or commit authorization.

---

## Sprint Focus
ADVANCE: Product deepening — .NET commercial + Python FOSS + dogfood + packaging

## Prior Sprint Summary
- Sprint ID: convergence-product-verify-20260624-3f98f85d
- Evidence verdict: ACCEPTED
- Tests: 1609 passed, 0 failed, 0 skipped
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
- [pending] TASK-004: Work on open taskcard: TC-0015-spec-retrieval-strategy-evaluation
- [pending] TASK-005: Work on open taskcard: TC-0016-fods-vector-index-pilot
- [pending] TASK-006: Work on open taskcard: TC-0020-spec-workbench-core
- [pending] TASK-007: Product deepening: GAP-FODS-COMM-SAVE_SAME_FO-001 — GAP-FODS-COMM-SAVE_SAME_FO-001
- [pending] TASK-008: Product deepening: GAP-FODT-COMM-SAVE_SAME_FO-001 — GAP-FODT-COMM-SAVE_SAME_FO-001
- [pending] TASK-009: Product deepening: GAP-FODS-COMM-RELOAD_AND_V-001 — GAP-FODS-COMM-RELOAD_AND_V-001
- [pending] TASK-010: Product deepening: GAP-FODT-COMM-RELOAD_AND_V-001 — GAP-FODT-COMM-RELOAD_AND_V-001
- [pending] TASK-011: Product deepening: GAP-ABW-FOSS-ABW_SECTION_-001 — GAP-ABW-FOSS-ABW_SECTION_-001
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

## Entry: capability-convergence-iteration-1-20260624
- timestamp: 2026-06-24T11:43:07.337296
- verdict: ACCEPTED
- test_count: 25
- fail_count: 0
- git_head: see-declaration
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\cap-convergence-iter1-20260624-3f98f85d\declaration-review-package.zip
- pending_marker_count: 0
- bundle_entry_count: 69
- bundle_validation_pass: True
- test_delta: +25
- test_delta_from: 0

## Entry: agentic-maturity-wave1-20260624-3f98f85d
- timestamp: 2026-06-24T11:51:07.229944
- verdict: ACCEPTED
- test_count: 3
- fail_count: 0
- git_head: see-declaration
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\agentic-maturity-wave1-20260624-3f98f85d\declaration-review-package.zip
- pending_marker_count: 0
- bundle_entry_count: 69
- bundle_validation_pass: True
- test_delta: -22
- test_delta_from: 25

## Entry: convergence-product-verify-20260624-3f98f85d
- timestamp: 2026-06-24T11:55:06.709637
- verdict: ACCEPTED
- test_count: 0
- fail_count: 0
- git_head: see-declaration
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\convergence-product-verify-20260624-3f98f85d\declaration-review-package.zip
- pending_marker_count: 0
- bundle_entry_count: 63
- bundle_validation_pass: True

## Entry: convergence-audit1-20260624-3f98f8
- timestamp: 2026-06-24T12:01:06.758778
- verdict: ACCEPTED
- test_count: 6155
- fail_count: 0
- git_head: see-declaration
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\convergence-audit1-20260624-3f98f8\declaration-review-package.zip
- pending_marker_count: 0
- bundle_entry_count: 62
- bundle_validation_pass: True
- test_delta: +6155
- test_delta_from: 0
```

---
END OF SUPERVISOR-GENERATED NEXT SPRINT PROMPT
