# R63 R62 Defect Ledger

**Sprint:** FORMAT-FACTORY-R63-AI-ASSISTED-RC-CLOSURE-AND-WORKAHEAD-MULTI-SPRINT-MEGA-TRAIN-001
**Date:** 2026-05-24
**Defects from:** R62 Independent Verification (Train A)

---

## Defect Ledger

### IV-R62-001: R62 Sidecar Not Committed/Delivered
- **Severity:** CRITICAL
- **Evidence:** reports/**/*.sha256-proof.json gitignored; no committed sidecar alongside R62 ZIP
- **Impact:** Cannot self-verify without sidecar; chain broken
- **R63 Repair:** Train C — create R63 sidecar at committed-safe path; write sidecar tests referencing R63

### IV-R62-002: fods/__init__.py Missing 4 Public API Exports
- **Severity:** CRITICAL
- **Missing APIs:** workbook_formula_list, workbook_cell_range, workbook_merged_cell_summary, workbook_sheet_order
- **Evidence:** `import fods; hasattr(fods, 'workbook_formula_list')` → False
- **Impact:** Installed-wheel API proof overclaimed 14/14; actual 10/18 for claimed APIs
- **R63 Repair:** Train D — add 4 imports to fods/__init__.py + __all__; rebuild wheel

### IV-R62-003: fodt/__init__.py Missing 4 Public API Exports
- **Severity:** CRITICAL
- **Missing APIs:** document_list_stats, document_reading_level, document_hyperlink_count, document_footnote_count
- **Evidence:** `import fodt; hasattr(fodt, 'document_list_stats')` → False
- **Impact:** Same as IV-R62-002 for FODT
- **R63 Repair:** Train D — add 4 imports to fodt/__init__.py + __all__; rebuild wheel

### IV-R62-004: R62 Sidecar Tests Fail From Extracted Bundle
- **Severity:** HIGH
- **Evidence:** test_r62_final_response_sidecar_path_exists.py references reports/r61/r61-pass2-final.zip.sha256-proof.json (gitignored)
- **Impact:** 9 of 33 sidecar tests fail from clean extraction
- **R63 Repair:** Train C — write R63 sidecar tests referencing committed paths only

### IV-R62-005: No R62 Packaging Test
- **Severity:** HIGH
- **Evidence:** ls tests/packaging/ — no test_r62_*.py
- **Impact:** No packaging replay coverage for R62 artifacts
- **R63 Repair:** Train E — create test_r63_package_rc.py

### IV-R62-006: INV-007 Active — "to be updated" in final-verdict.md
- **Severity:** HIGH
- **Evidence:** check_repo_invariants.py → INV-007: FAIL
- **Impact:** State snapshot production blocker persists across sessions
- **R63 Repair:** Immediate — rephrase AUTHORITATIVE_TEST_RESULT in reports/r62/final-verdict.md

### IV-R62-007: SHA Mismatch Between Final-Verdict and Actual ZIP
- **Severity:** MEDIUM (documented, not blocking)
- **Evidence:** final-verdict.md: BUNDLE_VALIDATION_PASS_2_SHA = 3d4f1ac0... (intermediate); actual ZIP SHA = d364678f... (final rebuild)
- **Impact:** Requires sidecar for authoritative SHA; sidecar is correct
- **R63 Repair:** Documented — sidecar is authoritative; reclassify as acceptable divergence

### IV-R62-008: Packaging Replay Test Has Skips
- **Severity:** MEDIUM
- **Evidence:** test_r61_extracted_bundle_package_replay.py: skips under non-.local conditions
- **Impact:** Partial replay coverage
- **R63 Repair:** Train E — normalize packaging replay

### IV-R62-009: AI Reviewers Fixture-Only — Missed Closure Blockers
- **Severity:** LOW (process deficiency, not implementation defect)
- **Evidence:** All R62 AI reviewer files: token_usage=0, api_calls_count=0, mode=fixture
- **Impact:** AI did not catch IV-R62-001 through IV-R62-006 during sprint
- **R63 Repair:** Train B — document AI_NOT_LIVE; continue fixture mode with explicit labeling

### IV-R62-010: AUTHORITATIVE_TEST_RESULT Contains INV-007 Trigger
- **Severity:** HIGH (same root cause as IV-R62-006)
- **Evidence:** Line: "tests that require final-verdict/state to be updated"
- **Impact:** INV-007 active in every session using this repo
- **R63 Repair:** Immediate fix in final-verdict.md

### IV-R62-011: Installed-Wheel Proof Overclaimed "14/14"
- **Severity:** HIGH
- **Evidence:** R62 claimed 14/14 PASS; actual APIs tested were only 7+7 (not the 9+9 required)
- **Impact:** Installer claim is overclaim; repair requires 9+9 proof
- **R63 Repair:** Train D + F — fix APIs, rebuild wheels, prove 9+9

### IV-R62-012: R62 Scoreboard Had IN_PROGRESS at Initial Bundle Build
- **Severity:** LOW (resolved in same session)
- **Evidence:** Scoreboard was updated to COMPLETE before final bundle rebuild
- **Impact:** None — scoreboard was corrected before final bundle
- **R63 Repair:** Accepted; documented

---

## Defect Counts

| Severity | Count |
|---|---|
| CRITICAL | 3 (IV-R62-001, 002, 003) |
| HIGH | 5 (IV-R62-004, 005, 006, 010, 011) |
| MEDIUM | 2 (IV-R62-007, 008) |
| LOW | 2 (IV-R62-009, 012) |
| **Total** | **12** |

DEFECT_LEDGER_STATUS: COMPLETE (12 defects)
