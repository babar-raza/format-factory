# Supervisor-Generated Next Sprint Prompt
# Source sprint: IDEMPOTENT-SWARM-SPRINT-117
# Stream: mainstream
# Generated: 2026-06-16T15:19:42.914344
# ADVISORY ONLY — not a Format Factory authority document
# This is INPUT to the next sprint, not a gate approval or commit authorization.

---

## Sprint Focus
ADVANCE: Product deepening — .NET commercial + Python FOSS + dogfood + packaging

## Prior Sprint Summary
- Sprint ID: IDEMPOTENT-SWARM-SPRINT-117
- Evidence verdict: ACCEPTED_WITH_REWORK
- Tests: 12 passed, 0 failed, 0 skipped
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
- [agent-owned] TASK-002: Prepare FODS Gate 11 readiness packet and commercial checklist
- [external-gate] TASK-003: Submit FODS Gate 11 for Babar Raza approval (after packet ready — human required)
- [agent-owned] TASK-004: Prepare FODT Gate 11 readiness packet and commercial checklist
- [external-gate] TASK-005: Submit FODT Gate 11 for Babar Raza approval (after packet ready — human required)
- [pending] TASK-006: Continue ZST implementation toward Gate 11 readiness criteria
- [pending] TASK-007: Work on open taskcard: FODS-COMMERCIAL-EXPORT-HTML-PDF-PNG
- [pending] TASK-008: Work on open taskcard: FODT-COMMERCIAL-EXPORT-HTML-PDF-PNG
- [pending] TASK-009: Work on open taskcard: NEXT-COMMERCIAL-IMPLEMENTATION-SWARM
- [pending] TASK-010: Product deepening: GAP-ABW-FOSS-LOAD-001 — GAP-ABW-FOSS-LOAD-001
- [pending] TASK-011: Product deepening: GAP-FODG-FOSS-LOAD-001 — GAP-FODG-FOSS-LOAD-001
- [pending] TASK-012: Product deepening: GAP-Gnumeric-FOSS-LOAD-001 — GAP-Gnumeric-FOSS-LOAD-001
- [pending] TASK-013: Product deepening: GAP-TOML-FOSS-ROUNDTRIP-001 — GAP-TOML-FOSS-ROUNDTRIP-001
- [pending] TASK-014: Product deepening: GAP-DIF-FOSS-PROBE_DIF-001 — GAP-DIF-FOSS-PROBE_DIF-001
- [pending] TASK-015: Advance one dogfood export path using a Format Factory library
- [pending] TASK-016: Build package artifacts and run installed-workflow proof
- [pending] TASK-017: Write evidence declaration and run supervisor autonomous-cycle

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
- timestamp: 2026-06-16T15:11:10.543853
- verdict: ACCEPTED
- test_count: 21
- fail_count: 0
- git_head: see-declaration
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\product-deepening-sprint70-20260616-fc60c35\declaration-review-package.zip
- pending_marker_count: 0
- bundle_entry_count: 40
- bundle_validation_pass: True
- test_delta: +9
- test_delta_from: 12

## Entry: IDEMPOTENT-SWARM-SPRINT-115
- timestamp: 2026-06-16T15:13:09.725761
- verdict: ACCEPTED
- test_count: 12
- fail_count: 0
- git_head: see-declaration
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\idempotent-swarm-sprint115-20260616-baf84d6\declaration-review-package.zip
- pending_marker_count: 0
- bundle_entry_count: 60
- bundle_validation_pass: True
- test_delta: -9
- test_delta_from: 21

## Entry: IDEMPOTENT-SWARM-SPRINT-116
- timestamp: 2026-06-16T15:17:09.977942
- verdict: ACCEPTED
- test_count: 12
- fail_count: 0
- git_head: see-declaration
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\idempotent-swarm-sprint116-20260616-baf84d6\declaration-review-package.zip
- pending_marker_count: 0
- bundle_entry_count: 60
- bundle_validation_pass: True
- test_delta: 0
- test_delta_from: 12

## Entry: TOML-DEEPENING-R275-R279-20260616
- timestamp: 2026-06-16T15:19:10.293711
- verdict: ACCEPTED
- test_count: 50
- fail_count: 0
- git_head: see-declaration
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\toml-deepening-r275-r279-20260616-e5ba655\declaration-review-package.zip
- pending_marker_count: 0
- bundle_entry_count: 66
- bundle_validation_pass: True
- test_delta: +38
- test_delta_from: 12
```

---
END OF SUPERVISOR-GENERATED NEXT SPRINT PROMPT
