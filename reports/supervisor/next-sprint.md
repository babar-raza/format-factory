# Supervisor-Generated Next Sprint Prompt
# Source sprint: FORMAT-FACTORY-R85-POC-DIRECTION-LOCAL-SUPERVISOR-AUTONOMOUS-PRODUCT-FACTORY-MEGA-TRAIN-001
# Generated: 2026-05-31T23:27:54.398493
# ADVISORY ONLY — not a Format Factory authority document
# This is INPUT to the next sprint, not a gate approval or commit authorization.

---

## Sprint Focus
ADVANCE: Continue normal mega-train lanes

## Prior Sprint Summary
- Sprint ID: FORMAT-FACTORY-R85-POC-DIRECTION-LOCAL-SUPERVISOR-AUTONOMOUS-PRODUCT-FACTORY-MEGA-TRAIN-001
- Evidence verdict: ACCEPTED
- Tests: 349 passed, 0 failed, 0 skipped
- Autonomous continue: True

## Contradictions Requiring Repair
None

## Synthesized Task List (Advisory)
- [approval-blocked] TASK-001: Advance FODS Gate 11 commercial readiness
- [approval-blocked] TASK-002: Advance FODT Gate 11 commercial readiness
- [blocked] TASK-003: Open ZST Gate 11
- [pending] TASK-004: Work on open taskcard: ABW-GATE4-001-parser-prototype
- [pending] TASK-005: Work on open taskcard: AI-USAGE-LEDGER-AND-METRICS
- [pending] TASK-006: Work on open taskcard: EVIDENCE-HYGIENE-ENFORCEMENT
- [pending] TASK-007: Build and validate next sprint evidence bundle

## Non-Negotiable Rules (always apply)
1. No push without explicit user authorization.
2. No commit without explicit user authorization.
3. No gate self-approval.
4. No active .vscode/mcp.json without MODE 4 approval.
5. No Task Master / Ruflo init without MODE 3+ authorization.
6. Evidence bundle (ZIP) must be produced and validated with BUNDLE_VALIDATION: PASS.
7. All gate closures require human approval (gates 1-11).
8. Format Factory authority is final — supervisor is advisory only.

## Evidence Requirements for Next Sprint
- Evidence bundle built via tools/evidence/build_evidence_bundle.py
- Validated via tools/evidence/validate_evidence_bundle.py → BUNDLE_VALIDATION: PASS
- Final verdict must contain: VERDICT: <enum>
- All SHAs must be filled (no PENDING markers in final state)
- Tests: 0 failures required

## Suggested Lane Manifest (Advisory)
- Lane C0: Coordinator — integration, manifest authority, stop-gate monitoring
- Lane C1: Governance discovery — read AGENTS.md, GOVERNANCE.md, master-plan state
- Lane C2: Repair lanes — address any open contradictions from prior sprint
- Lane C3: Implementation — per open taskcards
- Lane C4: Validation — pytest, py_compile, schema validation
- Lane C5: Negative/fuzz — negative test coverage
- Lane C6: Evidence — bundle build + validation
- Lane C7: Adversarial — challenge all claims before finalizing

## Acceptance Criteria Per Lane
(Fill from open taskcards in taskcards/ directory)

## Project Memory Context
```
- pending_marker_count: 2
- bundle_entry_count: 81

## Entry: FORMAT-FACTORY-R83-BROAD-PRODUCT-FINISH-REVIEW-PACKAGE-ARTIFACTS-FODS-FODT-NEXTFORMATS-AUTHORITY-MEGA-TRAIN-001
- timestamp: 2026-05-31T14:37:07.182547
- verdict: ACCEPTED
- test_count: 161
- fail_count: 0
- git_head: unknown
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r83-pass1.zip
- pending_marker_count: 0
- bundle_entry_count: 3380

## Entry: ** FORMAT-FACTORY-R83-BROAD-PRODUCT-FINISH-REVIEW-PACKAGE-ARTIFACTS-FODS-FODT-NEXTFORMATS-AUTHORITY-MEGA-TRAIN-001
- timestamp: 2026-05-31T14:47:05.888050
- verdict: ACCEPTED
- test_count: 0
- fail_count: 0
- git_head: unknown
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r83-supervisor-review-package.zip
- pending_marker_count: 1
- bundle_entry_count: 9

## Entry: FORMAT-FACTORY-R84-BROAD-CLOSURE-RAW-LOGS-FINAL-AUTHORITY-FODS-FODT-ZST-NEXTFORMAT-ADVANCEMENT-MEGA-TRAIN-001
- timestamp: 2026-05-31T20:09:07.506275
- verdict: ACCEPTED
- test_count: 65
- fail_count: 0
- git_head: unknown
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r84-pass2.zip
- pending_marker_count: 0
- bundle_entry_count: 3430

## Entry: FORMAT-FACTORY-R85-POC-DIRECTION-LOCAL-SUPERVISOR-AUTONOMOUS-PRODUCT-FACTORY-MEGA-TRAIN-001
- timestamp: 2026-05-31
- sprint_type: DIRECTION_CORRECTION + PRODUCT_FACTORY_POC
- direction_corrected: true
- product_factory_primary_goal: true
- evidence_role: SUPPORT_INFRASTRUCTURE_NOT_FINISH_LINE
- commercial_net_poc_targets: FODS, FODT, Netpbm
- foss_reduced_poc_targets: ZST, PBM+PGM+PPM, SYLK
- supervisor_loop_used: true
- mcp_activation: NOT_PERFORMED
- ruflo_daemon: NOT_STARTED
- commercial_product_ready: false
- gate_11_approved: false
- gate_8_approved: false
- poc_matrix_path: product-capability-matrix/poc-targets.yaml
- dogfood_export_strategy: docs/export/dogfood-export-strategy.md
- next_action: Run supervisor_loop.py run-on-latest after evidence bundle built
```

---
END OF SUPERVISOR-GENERATED NEXT SPRINT PROMPT
