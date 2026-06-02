# Supervisor-Generated Next Sprint Prompt
# Source sprint: FORMAT-FACTORY-R90-AUTONOMOUS-CONTINUATION-PPM-TESTS-EXAMPLES-POC-MATRIX-UPDATE-001
# Generated: 2026-06-01T22:20:31.907062
# ADVISORY ONLY — not a Format Factory authority document
# This is INPUT to the next sprint, not a gate approval or commit authorization.

---

## Sprint Focus
ADVANCE: Continue normal mega-train lanes

## Prior Sprint Summary
- Sprint ID: FORMAT-FACTORY-R90-AUTONOMOUS-CONTINUATION-PPM-TESTS-EXAMPLES-POC-MATRIX-UPDATE-001
- Evidence verdict: ACCEPTED
- Tests: 3000 passed, 0 failed, 11 skipped
- Autonomous continue: True

## Contradictions Requiring Repair
None

## Synthesized Task List (Advisory)
- [approval-blocked] TASK-001: Commit uncommitted product code and build sprint evidence bundle
- [approval-blocked] TASK-002: Advance FODS Gate 11 commercial readiness
- [approval-blocked] TASK-003: Advance FODT Gate 11 commercial readiness
- [blocked] TASK-004: Open ZST Gate 11
- [pending] TASK-005: Work on open taskcard: ABW-GATE4-001-parser-prototype
- [pending] TASK-006: Work on open taskcard: AI-USAGE-LEDGER-AND-METRICS
- [pending] TASK-007: Work on open taskcard: EVIDENCE-HYGIENE-ENFORCEMENT
- [pending] TASK-008: Product deepening: GAP-CAP-001 — PPM load/parse (P3/P6)
- [pending] TASK-009: Product deepening: GAP-CAP-003 — FODS→CSV export
- [pending] TASK-010: Product deepening: GAP-DOGFOOD-DIF-CSV-001 — GAP-DOGFOOD-DIF-CSV-001
- [pending] TASK-011: Product deepening: GAP-DOC-001 — No standalone .NET Netpbm example (examples/net/netpbm/ dire
- [pending] TASK-012: Product deepening: GAP-DOC-002 — No FODS→CSV example (capability not yet implemented)
- [pending] TASK-013: Build and validate next sprint evidence bundle

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
- poc_matrix_path: product-capability-matrix/poc-targets.yaml
- dogfood_export_strategy: docs/export/dogfood-export-strategy.md
- next_action: Run supervisor_loop.py run-on-latest after evidence bundle built

## Entry: FORMAT-FACTORY-R86-SUPERVISOR-TRUTH-POC-PRODUCT-FACTORY-DEEPENING-NETPBM-FODS-FODT-FOSS-DOGFOOD-MEGA-TRAIN-001
- timestamp: 2026-06-01T15:11:05.235301
- verdict: REJECTED_BUNDLE_VALIDATION_FAIL
- test_count: 169
- fail_count: 0
- git_head: unknown
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r86-pass2.zip
- pending_marker_count: 0
- bundle_entry_count: 3526
- bundle_validation_pass: False
- validator_error_summary: ============================================================
EVIDENCE BUNDLE VALIDATION REPORT
============================================================
Contract: C:\Users\prora\OneDrive\Documents\
- test_delta: +104
- test_delta_from: 65

## Entry: FORMAT-FACTORY-R87-CLEAN-SUPERVISOR-CLOSEOUT-REVIEW-PACKAGE-POC-PRODUCT-FACTORY-DEEPENING-MEGA-TRAIN-001
- timestamp: 2026-06-01T17:11:06.955469
- verdict: REJECTED_BUNDLE_VALIDATION_FAIL
- test_count: 65
- fail_count: 0
- git_head: unknown
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r87-pass1.zip
- pending_marker_count: 0
- bundle_entry_count: 3549
- bundle_validation_pass: False
- validator_error_summary: ============================================================
EVIDENCE BUNDLE VALIDATION REPORT
============================================================
Contract: C:\Users\prora\OneDrive\Documents\
- test_delta: -104
- test_delta_from: 169

## Entry: FORMAT-FACTORY-R88-DECLARATION-DRIVEN-AUTONOMOUS-CLOSEOUT-POC-PRODUCT-DEEPENING-MEGA-TRAIN-001
- timestamp: 2026-06-01T20:47:07.615679
- verdict: ACCEPTED
- test_count: 65
- fail_count: 0
- git_head: unknown
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r88-pass2.zip
- pending_marker_count: 0
- bundle_entry_count: 3574
- bundle_validation_pass: True
- test_delta: 0
- test_delta_from: 65
```

---
END OF SUPERVISOR-GENERATED NEXT SPRINT PROMPT
