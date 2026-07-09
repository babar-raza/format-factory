# Supervisor-Generated Next Sprint Prompt
# Source sprint: hazy-questing-peach
# Stream: mainstream
# Generated: 2026-07-09T18:37:10.238247
# ADVISORY ONLY — not a Format Factory authority document
# This is INPUT to the next sprint, not a gate approval or commit authorization.

---

## Sprint Focus
ADVANCE: Product deepening — .NET commercial + Python FOSS + dogfood + packaging

## Prior Sprint Summary
- Sprint ID: hazy-questing-peach
- Evidence verdict: ACCEPTED
- Tests: 1634 passed, 0 failed, 0 skipped
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
- git commit/push/merge: SCM Agent task (AGENTS.md §AG4). Classify EXTERNAL_BLOCKER if credentials or policy unavailable.
- Gate 11 G11-G approval EXECUTION (Babar Raza only — sole TRUE_EXTERNAL_GATE)
- NuGet/PyPI publication execution
- Credentials unavailable with no fallback

## Section 1: New Product Work (Advisory — Always Execute)
- [pending] TASK-001: Select governed product gaps and validate the product-code ledger
- [agent-owned] TASK-002: Prepare commit candidate summary and changed-file manifest
- [external-gate] TASK-003: Execute git commit (SCM Agent task — AGENTS.md §AG4.1)
- [pending] TASK-004: Work on open taskcard: TC-0015-spec-retrieval-strategy-evaluation
- [pending] TASK-005: Work on open taskcard: TC-0016-fods-vector-index-pilot
- [pending] TASK-006: Work on open taskcard: TC-0020-spec-workbench-core
- [pending] TASK-007: Advance one dogfood export path using a Format Factory library
- [pending] TASK-008: Build package artifacts and run installed-workflow proof
- [pending] TASK-009: Write evidence declaration and run supervisor autonomous-cycle

## Section 2: Rework / Repair (Advisory — Fix Before Closeout)
None

## Contradictions Context
None

## Non-Negotiable Rules (always apply)
1. No push: SCM Agent task (AGENTS.md §AG4.2). Execute when credentials and branch policy allow; else classify EXTERNAL_BLOCKER: git_push_credentials_unavailable.
2. No commit: SCM Agent task (AGENTS.md §AG4.1). Execute when sprint policy authorizes and tests pass; else classify specific blocker.
3. No gate self-approval without evidence.
4. No active .vscode/mcp.json without MODE 4 approval.
5. No Task Master / Ruflo init without MODE 3+ authorization.
6. Load `.local/supervisor/selected-product-gaps.json` and `.supervisor/skill-registry.yaml` before product work.
7. Gates 1-10: agent-owned policy gates (evidence + validators + acceptance criteria per AGENTS.md §AG5). Gate 11 G11-G: sole TRUE_EXTERNAL_GATE (Babar Raza).
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
- test_delta: -5955
- test_delta_from: 6357

## Entry: R1264-R1269-BATCH
- timestamp: 2026-07-02T20:57:14.552431
- verdict: ACCEPTED
- test_count: 109
- fail_count: 0
- git_head: see-declaration
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\r1264-r1269-batch\declaration-review-package.zip
- pending_marker_count: 0
- bundle_entry_count: 81
- bundle_validation_pass: True
- test_delta: -293
- test_delta_from: 402

## Entry: BULK-PROPERTIES-R1233-R1291
- timestamp: 2026-07-02T22:05:10.502981
- verdict: ACCEPTED
- test_count: 1775
- fail_count: 0
- git_head: see-declaration
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\MA-2026-07-02-BULK-R1233-R1291\declaration-review-package.zip
- pending_marker_count: 0
- bundle_entry_count: 96
- bundle_validation_pass: True
- test_delta: +1666
- test_delta_from: 109

## Entry: PQLM-GOV-001
- timestamp: 2026-07-04T16:37:13.503440
- verdict: ACCEPTED
- test_count: 0
- fail_count: 0
- git_head: see-declaration
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\pqlm-gov-001-20260704-001\declaration-review-package.zip
- pending_marker_count: 0
- bundle_entry_count: 67
- bundle_validation_pass: True

## Entry: bright-greeting-goose-20260706T104442Z
- timestamp: 2026-07-06T15:49:10.375834
- verdict: ACCEPTED
- test_count: 0
- fail_count: 0
- git_head: see-declaration
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\bright-greeting-goose-20260706T104442Z\declaration-review-package.zip
- pending_marker_count: 0
- bundle_entry_count: 70
- bundle_validation_pass: True
```

---
END OF SUPERVISOR-GENERATED NEXT SPRINT PROMPT
