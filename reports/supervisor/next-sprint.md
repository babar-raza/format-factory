# Supervisor-Generated Next Sprint Prompt
# Source sprint: FORMAT-FACTORY-R82-TRUE-AUTHORITY-RECOVERY-FODS-INSTALLED-PRODUCT-RC-PACKAGE-ARTIFACTS-REPRODUCIBILITY-MEGA-TRAIN-001
# Generated: 2026-05-31T13:13:31.179931
# ADVISORY ONLY — not a Format Factory authority document
# This is INPUT to the next sprint, not a gate approval or commit authorization.

---

## Sprint Focus
REPAIR: Address CRITICAL contradictions before advancing

## Prior Sprint Summary
- Sprint ID: FORMAT-FACTORY-R82-TRUE-AUTHORITY-RECOVERY-FODS-INSTALLED-PRODUCT-RC-PACKAGE-ARTIFACTS-REPRODUCIBILITY-MEGA-TRAIN-001
- Evidence verdict: ACCEPTED
- Tests: 73 passed, 0 failed, 0 skipped
- Autonomous continue: False

## Contradictions Requiring Repair
- [CRITICAL] PENDING markers found in final-verdict.md: 2 occurrences

## Synthesized Task List (Advisory)
- [pending] REPAIR-001: Repair: PENDING markers found in final-verdict.md: 2 occurrences

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
- supervisor_status: IMPLEMENTED
- current_product_phase: Phase 3 — FODS/FODT Gates 1-10 PASSED; G11-G NOT_STARTED
- r78_status: R78_FODS_PRODUCT_SLICE_COMPLETE_ZST_LOCAL_RC_READY_PUBLICATION_BLOCKED
- r78_head: 9b4e9e38a254b24ccb558e2b9dcb21d5f59c3506
- no_real_evidence_bundle: true (no .zip found in .local/evidence/)
- supervisor_scripts: 6 implemented
- schemas: 4 validated
- prompts: 5 written
- tm_bridge_validators: 2 implemented
- tm_bridge_tests: 2 files
- docs_created: 19 documents
- mcp_activation: NOT_PERFORMED (MODE 4 requires explicit human approval)
- ruflo_daemon: NOT_STARTED
- taskmaster_init: NOT_RUN
- vscode_mcp_json: ABSENT
- r78_conflict: NONE
- next_action: MODE 4 MCP activation requires explicit human approval

## Stale Threshold
Entries older than 3 sprints are marked [STALE]. None stale at initialization.

## Entry: ** FORMAT-FACTORY-AI-LLM-EMBEDDING-PLAN-MEMORY-SYNC-001
- timestamp: 2026-05-30T17:21:58.683779
- verdict: ACCEPTED
- test_count: 0
- fail_count: 0
- git_head: unknown
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\evidence-bundles\r40-r39-fix-closure-package-build-proof.zip
- pending_marker_count: 0
- bundle_entry_count: 2201

## Entry: FORMAT-FACTORY-R80-REPAIR-PLUS-ADVANCEMENT-SUPERVISOR-EVIDENCE-PRODUCT-SYSTEM-HARDENING-20260530
- timestamp: 2026-05-30T19:52:10.954828
- verdict: ACCEPTED
- test_count: 65
- fail_count: 0
- git_head: unknown
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\evidence\r80-repair-plus-advancement-supervisor-evidence-product-system-hardening-20260530.zip
- pending_marker_count: 0
- bundle_entry_count: 3159

## Entry: FORMAT-FACTORY-R79-PACKAGE-SOURCE-SYNC-FIRST-REAL-FODS-PRODUCT-RC-ZST-DEPENDENCY-REPLAY-MEGA-TRAIN-001
- timestamp: 2026-05-31T10:53:52.946007
- verdict: ACCEPTED
- test_count: 65
- fail_count: 0
- git_head: unknown
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r79-pass2.zip
- pending_marker_count: 0
- bundle_entry_count: 3300
```

---
END OF SUPERVISOR-GENERATED NEXT SPRINT PROMPT
