# Supervisor-Generated Next Sprint Prompt
# Source sprint: FORMAT-FACTORY-R83-BROAD-PRODUCT-FINISH-REVIEW-PACKAGE-ARTIFACTS-FODS-FODT-NEXTFORMATS-AUTHORITY-MEGA-TRAIN-001
# Generated: 2026-05-31T14:43:06.434438
# ADVISORY ONLY — not a Format Factory authority document
# This is INPUT to the next sprint, not a gate approval or commit authorization.

---

## Sprint Focus
ADVANCE: Continue normal mega-train lanes

## Prior Sprint Summary
- Sprint ID: FORMAT-FACTORY-R83-BROAD-PRODUCT-FINISH-REVIEW-PACKAGE-ARTIFACTS-FODS-FODT-NEXTFORMATS-AUTHORITY-MEGA-TRAIN-001
- Evidence verdict: ACCEPTED
- Tests: 161 passed, 0 failed, 0 skipped
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

## Entry: FORMAT-FACTORY-R79-PACKAGE-SOURCE-SYNC-FIRST-REAL-FODS-PRODUCT-RC-ZST-DEPENDENCY-REPLAY-MEGA-TRAIN-001 [STALE]
- timestamp: 2026-05-31T10:53:52.946007
- verdict: ACCEPTED
- test_count: 65
- fail_count: 0
- git_head: unknown
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r79-pass2.zip
- pending_marker_count: 0
- bundle_entry_count: 3300

## Entry: FORMAT-FACTORY-R82-TRUE-AUTHORITY-RECOVERY-FODS-INSTALLED-PRODUCT-RC-PACKAGE-ARTIFACTS-REPRODUCIBILITY-MEGA-TRAIN-001
- timestamp: 2026-05-31T13:13:31.382196
- verdict: ACCEPTED
- test_count: 73
- fail_count: 0
- git_head: unknown
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r82-supervisor-review-package.zip
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
```

---
END OF SUPERVISOR-GENERATED NEXT SPRINT PROMPT
