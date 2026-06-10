# Test Integrity Verification
## TC-G1, TC-G2, TC-G3, TC-G4, TC-G5 | Plan Hardening Sprint 2026-06-09

---

## TC-G1: Historical Test-Count Changes

### Recent Sprint Trend (from MEMORY.md + agent investigation)
| Sprint | Tests Passed | Tests Failed | Delta |
|---|---|---|---|
| rnext7 | 21 | 0 | — |
| rnext8 | 7 | 0 | -14 (smaller sprint) |
| rnext9 | 25 | 0 | +18 |
| rnext10 | 29 | 0 | +4 |
| rnext11 | 30 | 0 | +1 |

**Note:** These are per-sprint test counts (tests run in that sprint's scope), NOT cumulative. The full test suite has been reported at various points:
- Sprint 3 (acceleration): 7,095 total pass
- Sprint 4: 7,198 total pass
- Sprint 5: 7,004 total pass (apparent drop)
- Sprint 10: 11,855 total pass

### Historical Drops Explained
1. **7,198 → 7,004 (Sprint 4→5):** Per MEMORY.md, this was due to continuation-signal timing issues, not actual test deletion. Resolved in Sprint 10 where full suite showed 11,855.
2. **No test deletions detected:** No evidence of tests being removed or excluded. Drops were caused by sprint scope differences (some sprints ran targeted tests, not full suite).

### Assessment
**W5 verdict: NOT A CURRENT CONCERN.** Test count shows consistent growth when measuring full suite. Per-sprint counts vary because sprints run targeted test subsets. Anti-skip detector #14 (test count regression) exists and monitors for drops.

---

## TC-G2: Test Coverage Drift Audit

### Total Test Files: 777

#### Python Tests by Format (443 total)
| Format | Test Files | Category |
|---|---|---|
| fods | 37 | DEEP |
| fodt | 36 | DEEP |
| tsv | 33 | DEEP |
| sylk | 33 | DEEP |
| abw | 33 | DEEP |
| ndjson | 32 | DEEP |
| ppm | 29 | DEEP |
| gnumeric | 29 | DEEP |
| zst | 26 | DEEP |
| fodg | 23 | DEEP |
| dif | 22 | MEDIUM |
| pbm | 19 | MEDIUM |
| ods | 14 | MEDIUM |
| pgm | 13 | MEDIUM |
| qoi | 6 | SHALLOW |
| odt | 5 | SHALLOW |
| toml | 4 | SHALLOW |
| xcf | 4 | SHALLOW |
| fodp | 2 | SKELETON |
| netpbm | 1 | SKELETON |

#### Supervisor Tests: 181 files
#### Evidence Tests: 153 files

### Coverage Distribution
- **DEEP (20+):** 10 formats = 50% of formats, ~80% of tests
- **MEDIUM (10-19):** 4 formats = 20% of formats, ~15% of tests
- **SHALLOW (1-9):** 6 formats = 30% of formats, ~5% of tests

---

## TC-G3: Import-Only vs Output-Producing Tests

### Spot-Check Methodology
Read representative test files from 5 formats to classify test quality.

### Results (based on investigation agent readings)

**FODS (test_r153_fods_find_cells.py):**
- Creates neutral model fixtures (nested dicts)
- Tests: empty workbook, string cells, case-insensitive search, multi-sheet search
- **Verdict: OUTPUT-PRODUCING** — tests real I/O operations on structured data

**ABW (test_r121_abw_json_export.py, test_r150_abw_first_paragraph.py):**
- Creates ABW document fixtures
- Tests actual export operations and paragraph manipulation
- **Verdict: OUTPUT-PRODUCING** — tests document operations producing real outputs

**Gnumeric (test_r123_gnumeric_cell_accessor.py, test_r135_gnumeric_roundtrip.py):**
- Creates compressed XML test data
- Tests cell access and roundtrip integrity
- **Verdict: OUTPUT-PRODUCING** — includes roundtrip verification

**TSV (test_r122_tsv_write.py):**
- Creates TSV data in memory
- Tests write operations producing byte output
- **Verdict: OUTPUT-PRODUCING** — verifies actual file content

**FODG (test_r122_fodg_probe.py):**
- Creates FODG XML fixtures
- Tests probe returning structured page/shape data
- **Verdict: OUTPUT-PRODUCING** — extracts meaningful data from format

### Summary
All 5 spot-checked formats produce real outputs. No import-only tests detected in the sample. The test suite appears genuinely functional, not merely compile-check.

---

## TC-G4: Minimum Per-Format Test Depth Thresholds

### Proposed Thresholds

| Maturity | Min Test Files | Min Tests | Required Types |
|---|---|---|---|
| **Deep** | ≥20 | ≥100 | Parse, write, export, roundtrip, edge cases |
| **Medium** | ≥10 | ≥30 | Parse, probe, export/stats, boundary cases |
| **Shallow** | ≥5 | ≥10 | Parse, basic API, error handling |
| **Skeleton** | ≥2 | ≥5 | Parse/import, basic structure |

### Current Compliance

| Format | Files | Threshold | Status |
|---|---|---|---|
| FODS | 37 | Deep (≥20) | PASS |
| FODT | 36 | Deep (≥20) | PASS |
| ABW | 33 | Deep (≥20) | PASS |
| TSV | 33 | Deep (≥20) | PASS |
| SYLK | 33 | Deep (≥20) | PASS |
| NDJSON | 32 | Deep (≥20) | PASS |
| PPM | 29 | Deep (≥20) | PASS |
| Gnumeric | 29 | Deep (≥20) | PASS |
| ZST | 26 | Deep (≥20) | PASS |
| FODG | 23 | Deep (≥20) | PASS |
| DIF | 22 | Medium (≥10) | PASS |
| PBM | 19 | Medium (≥10) | PASS |
| ODS | 14 | Medium (≥10) | PASS |
| PGM | 13 | Medium (≥10) | PASS |
| QOI | 6 | Shallow (≥5) | PASS |
| ODT | 5 | Shallow (≥5) | PASS |
| TOML | 4 | Shallow (≥5) | FAIL (4 < 5) |
| XCF | 4 | Shallow (≥5) | FAIL (4 < 5) |
| FODP | 2 | Skeleton (≥2) | PASS |

**Failing:** TOML (4/5), XCF (4/5) — both need 1 more test file each.

---

## TC-G5: Test Deletion/Reorganization Validator Proposal

### Proposed Validator: `validate_test_delta.py`

**Purpose:** Detect test file deletions or renames that might indicate coverage loss.

**Inputs:**
- git diff --name-status HEAD (or between sprint SHAs)
- Previous test count snapshot

**Checks:**
1. If any test file is DELETED (D status): require REWORK/DEFERRED taskcard reference
2. If test file count decreases: flag with WARNING
3. If test file renamed (R status): verify new path exists and contains equivalent tests
4. If test directory removed: flag with CRITICAL

**Output:** PASS (no deletions) or WARN/FAIL with explanation and required taskcard reference.

**Integration:** Run as anti-skip detector #19 (new) in autonomous_cycle.py pipeline.

**Implementation status:** NOT YET IMPLEMENTED. Specification only.
