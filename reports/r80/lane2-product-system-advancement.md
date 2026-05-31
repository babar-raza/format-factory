# Lane 2 — Product and System Advancement

**sprint_id:** FORMAT-FACTORY-R80-REPAIR-PLUS-ADVANCEMENT-SUPERVISOR-EVIDENCE-PRODUCT-SYSTEM-HARDENING-20260530

## R79 Work Verified and Documented

R79 was substantially completed in the dirty tree prior to this sprint.
All R79 code changes and tests are present in the working tree (untracked/modified tracked files).
R80 Lane 2 verifies and documents this work.

### R79 Achievement Summary

| Achievement | Status | Evidence |
|---|---|---|
| All 17 R78 defects resolved | VERIFIED | r78-defect-ledger.md in reports/r79/ |
| FODS/FODT wheels rebuilt from current source | VERIFIED | test_r79_installed_fods_workflow.py (8 tests pass) |
| PACKAGE_VERSION synchronized (0.1.0.dev0) | VERIFIED | test_r79_package_source_sync.py::TestPackageVersionSync (4 tests pass) |
| FODT structural gap repaired (GAP-FODT-STRUCT-001) | VERIFIED | test_r79_package_source_sync.py::TestFodtStructuralGapRepaired (6 tests pass) |
| R77 sheet APIs in FODS installed wheel | VERIFIED | test_r79_package_source_sync.py::TestFodsR77ApiPresence (5 tests pass) |
| R77 paragraph APIs in FODT installed wheel | VERIFIED | test_r79_package_source_sync.py::TestFodtR77ApiPresence (4 tests pass) |
| FODS API count >= 28 | VERIFIED | test_installed_api_count_at_least_28 PASS |
| FODT API count >= 28 | VERIFIED | test_fodt_api_count_at_least_28 PASS |
| Paragraph roundtrip preserved by write_fodt | VERIFIED | test_append_then_roundtrip_preserves_paragraph PASS |
| FODT paragraph management tests (R77) | VERIFIED | test_r77_fodt_paragraph_management.py (20/20 PASS) |
| FODT end-to-end workflow tests (R78) | VERIFIED | test_r78_fodt_end_to_end_workflow.py (18/18 PASS) |

### Key Fix: GAP-FODT-STRUCT-001 Resolved

**Previous state (R78):** `document_append_paragraph`, `document_remove_paragraph`, `document_paragraph_count` wrote to `doc["body"]["blocks"]` but `write_fodt` reads `doc["blocks"]` (root level). Paragraphs appended did NOT survive round-trip.

**R79 fix:** `src/python/fodt/neutral_model.py` updated so all three APIs operate on `doc["blocks"]` (root level). Round-trip preservation verified by `test_append_then_roundtrip_preserves_paragraph`.

**Verified by:** 6 tests in `TestFodtStructuralGapRepaired` — all PASS.

### Total R79 Product Tests

| Test Suite | Tests | Result |
|---|---|---|
| test_r79_installed_fods_workflow.py | 8 | 8/8 PASS |
| test_r79_package_source_sync.py | 19 | 19/19 PASS |
| test_r77_fodt_paragraph_management.py | 20 | 20/20 PASS |
| test_r78_fodt_end_to_end_workflow.py | 18 | 18/18 PASS |
| **TOTAL** | **65** | **65/65 PASS** |

## System Advancement: Supervisor Sprint Width Policy

Added policy to default supervisor sprint structure:
- No narrow metadata-only sprints
- Every sprint: repair + advancement + validator hardening + sync + IV lanes
- Documented in `reports/r80/lane4-state-doc-sync.md`

## What Remains for R79 Closure

R79 has `require_clean_git: true`. A clean commit is needed before building the R79 bundle.
Current blocking factors:
- Supervisor sprint files (untracked) would need to be committed alongside R79 code
- Or: commit ONLY the R79 code changes and supervisor-sprint append-only changes

**Taskcard:** TC-R79-CLOSURE-001 — Commit R79 code changes + build R79 evidence bundle with clean git.

## Supervisor System Advancement: Sprint Width Policy

The supervisor's `generate_supervisor_packet.py` now produces a `next-sprint.md` that includes repair + advancement + validator + sync + IV lanes by default. This was already operational from the previous supervisor sprint. Verified by the supervisor replay (supervisor loop exit 0, all 5 packet files generated).
