## ACTIVE PER-CHAT PLAN — SYSTEM LEDGER SUPPRESSED

A per-chat plan is active. Complete ALL plan taskcards before any ledger/product work.

- **Plan:** `C:/Users/prora/.claude/plans/floating-stargazing-globe.md`
- **Last completed taskcard:** `None`
- **Action:** Read the plan file. Find the next open taskcard after `None`. Execute it.
  After each: `python tools/supervisor/write_plan_lock.py --plan-path "C:/Users/prora/.claude/plans/floating-stargazing-globe.md" --last-taskcard <TC_ID>`
  When ALL done: `python tools/supervisor/write_plan_lock.py --plan-path "C:/Users/prora/.claude/plans/floating-stargazing-globe.md" --complete`

**Do NOT start system ledger / product hardening work until plan status = COMPLETE.**

---

# Supervisor-Generated Next Sprint Prompt
# Source sprint: snoopy-juggling-seal-section-32-execution
# Stream: mainstream
# Generated: 2026-06-22T19:26:13.357708
# ADVISORY ONLY — not a Format Factory authority document
# This is INPUT to the next sprint, not a gate approval or commit authorization.

---

## Sprint Focus
PRODUCT + REPAIR: Advance product POC AND address CRITICAL contradictions

## Prior Sprint Summary
- Sprint ID: snoopy-juggling-seal-section-32-execution
- Evidence verdict: ACCEPTED_WITH_REWORK
- Tests: 15 passed, 0 failed, 0 skipped
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
- [pending] TASK-003: Select governed product gaps and validate the product-code ledger
- [agent-owned] TASK-004: Prepare commit candidate summary and changed-file manifest
- [external-gate] TASK-005: Execute git commit (requires explicit user authorization — do NOT self-execute)
- [pending] TASK-006: Work on open taskcard: TC-0015-spec-retrieval-strategy-evaluation
- [pending] TASK-007: Work on open taskcard: TC-0016-fods-vector-index-pilot
- [pending] TASK-008: Work on open taskcard: TC-0020-spec-workbench-core
- [pending] TASK-009: Advance one dogfood export path using a Format Factory library
- [pending] TASK-010: Build package artifacts and run installed-workflow proof
- [pending] TASK-011: Write evidence declaration and run supervisor autonomous-cycle

## Section 2: Rework / Repair (Advisory — Fix Before Closeout)
- [pending] REPAIR-001: Repair: OVERCLAIMED: Fix DIF->CSV Dogfood Import Path for Installed-Package Context
- [pending] REPAIR-002: Repair: OVERCLAIMED: Fix DIF->CSV Reload Test (CSV Module Name Conflict)

## Contradictions Context
- [CRITICAL] OVERCLAIMED: Fix DIF->CSV Dogfood Import Path for Installed-Package Context
- [CRITICAL] OVERCLAIMED: Fix DIF->CSV Reload Test (CSV Module Name Conflict)

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
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\zst-frame-count-coverage-20260622\declaration-review-package.zip
- pending_marker_count: 0
- bundle_entry_count: 61
- bundle_validation_pass: True

## Entry: product-gap-closure-20260622
- timestamp: 2026-06-22T13:41:09.393555
- verdict: ACCEPTED
- test_count: 0
- fail_count: 0
- git_head: see-declaration
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\product-gap-closure-20260622\declaration-review-package.zip
- pending_marker_count: 0
- bundle_entry_count: 78
- bundle_validation_pass: True

## Entry: product-gap-closure-batch-20260622
- timestamp: 2026-06-22T13:45:10.827669
- verdict: ACCEPTED
- test_count: 0
- fail_count: 0
- git_head: see-declaration
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\product-gap-closure-batch-20260622\declaration-review-package.zip
- pending_marker_count: 0
- bundle_entry_count: 80
- bundle_validation_pass: True

## Entry: odf-parts-acquisition-20260622
- timestamp: 2026-06-22T13:51:09.833356
- verdict: ACCEPTED
- test_count: 16
- fail_count: 0
- git_head: see-declaration
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\odf-parts-acquisition-20260622\declaration-review-package.zip
- pending_marker_count: 0
- bundle_entry_count: 64
- bundle_validation_pass: True
- test_delta: +16
- test_delta_from: 0

## Entry: forensics-healing-sprint-20260622
- timestamp: 2026-06-22T14:23:06.944637
- verdict: ACCEPTED
- test_count: 0
- fail_count: 0
- git_head: see-declaration
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\forensics-healing-sprint-20260622\declaration-review-package.zip
- pending_marker_count: 0
- bundle_entry_count: 82
- bundle_validation_pass: True
```

---
END OF SUPERVISOR-GENERATED NEXT SPRINT PROMPT
