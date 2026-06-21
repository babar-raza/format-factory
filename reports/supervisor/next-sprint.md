# Supervisor-Generated Next Sprint Prompt
# Source sprint: post-recon-repair-gate11-20260621
# Stream: mainstream
# Generated: 2026-06-21T22:11:21.274265
# ADVISORY ONLY — not a Format Factory authority document
# This is INPUT to the next sprint, not a gate approval or commit authorization.

---

## Sprint Focus
PRODUCT + REPAIR: Advance product POC AND address CRITICAL contradictions

## Prior Sprint Summary
- Sprint ID: post-recon-repair-gate11-20260621
- Evidence verdict: ACCEPTED_WITH_WARNINGS
- Tests: 65 passed, 5 failed, 0 skipped
- Autonomous continue: False

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
- [pending] TASK-002: Select governed product gaps and validate the product-code ledger
- [agent-owned] TASK-003: Prepare commit candidate summary and changed-file manifest
- [external-gate] TASK-004: Execute git commit (requires explicit user authorization — do NOT self-execute)
- [pending] TASK-005: Work on open taskcard: TC-0015-spec-retrieval-strategy-evaluation
- [pending] TASK-006: Work on open taskcard: TC-0016-fods-vector-index-pilot
- [pending] TASK-007: Work on open taskcard: TC-0020-spec-workbench-core
- [pending] TASK-008: Advance one dogfood export path using a Format Factory library
- [pending] TASK-009: Build package artifacts and run installed-workflow proof
- [pending] TASK-010: Write evidence declaration and run supervisor autonomous-cycle

## Section 2: Rework / Repair (Advisory — Fix Before Closeout)
- [pending] REPAIR-001: Repair: Tests failed: 5 failures detected in evidence bundle

## Contradictions Context
- [CRITICAL] Tests failed: 5 failures detected in evidence bundle

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

## Entry: ff-gate11-fodt-readiness-20260621
- timestamp: 2026-06-21T21:53:20.833985
- verdict: ACCEPTED
- test_count: 567
- fail_count: 0
- git_head: see-declaration
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\ff-gate11-fodt-readiness-20260621\declaration-review-package.zip
- pending_marker_count: 0
- bundle_entry_count: 66
- bundle_validation_pass: True
- test_delta: -50
- test_delta_from: 617

## Entry: ff-dtd-guard-tests-20260621
- timestamp: 2026-06-21T21:59:23.603593
- verdict: ACCEPTED
- test_count: 1186
- fail_count: 0
- git_head: see-declaration
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\ff-dtd-guard-tests-20260621\declaration-review-package.zip
- pending_marker_count: 0
- bundle_entry_count: 60
- bundle_validation_pass: True
- test_delta: +619
- test_delta_from: 567

## Entry: ff-registry-sync-20260621
- timestamp: 2026-06-21T22:01:21.582379
- verdict: ACCEPTED
- test_count: 1186
- fail_count: 0
- git_head: see-declaration
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\ff-registry-sync-20260621\declaration-review-package.zip
- pending_marker_count: 0
- bundle_entry_count: 60
- bundle_validation_pass: True
- test_delta: 0
- test_delta_from: 1186

## Entry: skill-gov-sync-final-20260621
- timestamp: 2026-06-21T22:05:27.705424
- verdict: ACCEPTED
- test_count: 0
- fail_count: 0
- git_head: see-declaration
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\skill-gov-sync-final-20260621\declaration-review-package.zip
- pending_marker_count: 0
- bundle_entry_count: 80
- bundle_validation_pass: True
```

---
END OF SUPERVISOR-GENERATED NEXT SPRINT PROMPT
