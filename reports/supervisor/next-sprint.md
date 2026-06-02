# Supervisor-Generated Next Sprint Prompt
# Source sprint: FORMAT-FACTORY-R90-MAINSTREAM-POC-PRODUCT-ACCELERATION-GOVERNED-SKILLS-SUPERVISOR-REPAIR-MEGA-TRAIN-001
# Generated: 2026-06-02T13:38:06.123478
# ADVISORY ONLY — not a Format Factory authority document
# This is INPUT to the next sprint, not a gate approval or commit authorization.

---

## Sprint Focus
REPAIR: Address CRITICAL contradictions before advancing

## Prior Sprint Summary
- Sprint ID: FORMAT-FACTORY-R90-MAINSTREAM-POC-PRODUCT-ACCELERATION-GOVERNED-SKILLS-SUPERVISOR-REPAIR-MEGA-TRAIN-001
- Evidence verdict: ACCEPTED
- Tests: 6835 passed, 12 failed, 26 skipped
- Autonomous continue: False

## Contradictions Requiring Repair
- [CRITICAL] Tests failed: 12 failures detected

## Synthesized Task List (Advisory)
- [pending] REPAIR-001: Repair: Tests failed: 12 failures detected
- [pending] TASK-002: Select governed product gaps and validate the product-code ledger
- [approval-blocked] TASK-003: Commit uncommitted product code and build sprint evidence bundle
- [approval-blocked] TASK-004: Advance FODS Gate 11 commercial readiness
- [approval-blocked] TASK-005: Advance FODT Gate 11 commercial readiness
- [blocked] TASK-006: Open ZST Gate 11
- [pending] TASK-007: Work on open taskcard: ABW-GATE4-001-parser-prototype
- [pending] TASK-008: Work on open taskcard: AI-USAGE-LEDGER-AND-METRICS
- [pending] TASK-009: Work on open taskcard: EVIDENCE-HYGIENE-ENFORCEMENT
- [pending] TASK-010: Product deepening: commercial-net-fods-dogfood-status-fods-to-csv-dotnet — dogfood_status.fods_to_csv_dotnet
- [pending] TASK-011: Product deepening: commercial-net-fods-dogfood-status-fods-to-html-dotnet — dogfood_status.fods_to_html_dotnet
- [pending] TASK-012: Product deepening: commercial-net-fodt-dogfood-status-fodt-to-markdown-dotnet — dogfood_status.fodt_to_markdown_dotnet
- [pending] TASK-013: Product deepening: commercial-net-fodt-dogfood-status-fodt-to-txt-dotnet — dogfood_status.fodt_to_txt_dotnet
- [pending] TASK-014: Product deepening: foss-reduced-sylk-python-status-write-sylk — python_status.write_sylk
- [pending] TASK-015: Advance one dogfood export path using a Format Factory library
- [pending] TASK-016: Build package artifacts and run installed-workflow proof
- [pending] TASK-017: Write evidence declaration and run supervisor autonomous-cycle

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

## Entry: FORMAT-FACTORY-R89-AUTHORITATIVE-TEST-BASELINE-DECLARATION-CLOSEOUT-POC-PRODUCT-DEEPENING-MEGA-TRAIN-001
- timestamp: 2026-06-02T08:43:07.409018
- verdict: REJECTED_BUNDLE_VALIDATION_FAIL
- test_count: 65
- fail_count: 0
- git_head: unknown
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r89-pass2.zip
- pending_marker_count: 0
- bundle_entry_count: 3627
- bundle_validation_pass: False
- validator_error_summary: ============================================================
EVIDENCE BUNDLE VALIDATION REPORT
============================================================
Contract: C:\Users\prora\OneDrive\Documents\
- test_delta: 0
- test_delta_from: 65

## Entry: FORMAT-FACTORY-R90-MAINSTREAM-POC-PRODUCT-ACCELERATION-GOVERNED-SKILLS-SUPERVISOR-REPAIR-MEGA-TRAIN-001
- timestamp: 2026-06-02
- status: IN_PROGRESS
- canonical_closeout: python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration .local/evidences/<run_id>/evidence-declaration.yaml
- legacy_run_on_latest: LEGACY_ONLY
- source_audit: R89 FODS, FODT, and Netpbm APIs remain present with tests
- acceleration_layer: IN_PROGRESS
- commercial_product_ready: false
- gate_11_approved: false
- publication_authorized: false
```

---
END OF SUPERVISOR-GENERATED NEXT SPRINT PROMPT
