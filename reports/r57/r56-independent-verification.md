# R56 Independent Verification — R57 Train A

**Sprint:** FORMAT-FACTORY-R57-SELF_VERIFYING-RC-REPLAY-PRODUCT-EXPANSION-PHASE8-MEGA-TRAIN-001
**Subject:** R56 — FORMAT-FACTORY-R56-R55-CLOSURE-REPAIR-PACKAGE-RC-PHASE7-PRODUCT-EXPANSION-MEGA-TRAIN-001
**Date:** 2026-05-23
**IV Verdict:** R56_MULTI_MEGA_TRAIN_PRODUCT_PROGRESS_ACCEPTED_PACKAGE_RC_PARTIAL_CLOSURE_REJECTED

---

## IV Methodology

This IV was performed by fresh preflight reads of all R56 report files, source files,
and the contract/validator before beginning any R57 work. Evidence for each defect
is cited with exact file paths and line numbers.

---

## R56 Positive Findings (Accepted)

| Item | Status | Evidence |
|------|--------|----------|
| TC-0057 criterion 3 (hyperlinks) | CLOSED_VERIFIED | src/python/fodt/writer.py `_write_span()` emits text:a; 6 tests in TestHyperlinkPreservation |
| TC-0059 criterion 2 (nested lists) | CLOSED_VERIFIED | src/python/fodt/writer.py `_write_list()` level-stack; 5 tests in TestNestedListHierarchy |
| CSV Gate 5 neutral model | PASS | 17/17 tests in test_r56_csv_gate5_neutral_model.py |
| TSV Gate 5 neutral model | PASS | 17/17 tests in test_r56_tsv_gate5_neutral_model.py |
| FODT 259 tests pass | PASS | R56 total confirmed in scoreboard |
| .NET 302 tests pass | PASS | dotnet-commercial-readiness-dryrun.md |
| fods.yaml + fodt.yaml created | PASS | release-manifests/python-foss/ (IV-R55-006 repair) |
| Validator 4 new functions | PASS | check_embedded_sidecar_bundle_match/check_nested_zips_allowed/check_scoreboard_finality/check_package_claim_policy_consistency |
| 7/7 wheels rebuilt (self_contained) | PASS | package-rc-self-contained.md; manifest in .local/ |
| R55 IV 10 defects documented | PASS | r55-defect-ledger.md |

---

## IV-R56-001: No Top-Level Sidecar for r56-pass2-final.zip

**Severity:** BLOCKING
**Category:** Evidence protocol gap

**Finding:** The R56 final bundle `.local/r56-pass2-final.zip` (SHA:
`5043fe754c23a5ce2ee3ce97dd4ebfc2facfd2d224bc43ec82b955828a152ca7`)
required an external sidecar proof file. Per the two-pass protocol (adopted in R53),
the sidecar `.sha256-proof.json` must be stored in a persistent location outside the
ZIP.

**Evidence:**
- Sidecar created at `.local/r56-pass2-final.zip.sha256-proof.json` (gitignored `.local/`)
- No sidecar committed to repo or stored in `reports/r56/`
- After R56 session ends, the sidecar is effectively inaccessible without re-running the build
- Contract (`tools/evidence/contracts/r56-r55-closure-repair-package-rc-phase7.yaml`) does
  not declare `sidecar_required: true` — no enforcement was in place

**R57 Fix:** Contract must declare `sidecar_required: true` + `final_proof_policy: external_sidecar`.
R57 final bundle sidecar must be stored in `reports/r57/` (committed to repo).

---

## IV-R56-002: Contract Missing Sidecar Policy Fields

**Severity:** MAJOR
**Category:** Contract incompleteness

**Finding:** `tools/evidence/contracts/r56-r55-closure-repair-package-rc-phase7.yaml` lacks:
- `sidecar_required: true`
- `final_proof_policy: external_sidecar`

**Evidence (line inspection):**
- File confirmed at line 16: `require_clean_git: true`
- File confirmed at line 17: `min_metadata_count: 30`
- No `sidecar_required` line present
- No `final_proof_policy` line present

**R57 Fix:** R57 contract will include both fields. Tests in `test_r57_sidecar_required_top_level.py`
will verify that validation fails without a sidecar when the contract declares sidecar_required.

---

## IV-R56-003 / IV-R56-004: BUNDLE_VALIDATION_PASS_2_SHA: PENDING Not Caught

**Severity:** MAJOR
**Category:** Validator gap

**Finding:** During R56 Train K, `reports/r56/final-verdict.md` temporarily contained
`BUNDLE_VALIDATION_PASS_2_SHA: PENDING` before the Pass 2 SHA was known. This was later
updated, but the validator never flagged it.

**Evidence — PENDING_MARKER_PATTERNS (validate_evidence_bundle.py lines 175-197):**
```python
PENDING_MARKER_PATTERNS = [
    "PENDING (bundle not yet built)",
    "validation_status: PENDING",
    "BUNDLE_VALIDATION: PENDING",
    "BUNDLE_VALIDATION: [PENDING]",
    ...
]
```
Pattern `BUNDLE_VALIDATION_PASS_2_SHA: PENDING` is NOT present.

**Evidence — check_repo_reports_pending STATUS_LINE_PATTERNS (lines 327-333):**
```python
STATUS_LINE_PATTERNS = [
    "BUNDLE_VALIDATION: PENDING",
    "BUNDLE_VALIDATION: [PENDING]",
    "TO BE UPDATED AFTER BUNDLE",
    "PENDING — building evidence bundle",
    "validation_status: PENDING",
]
```
Pattern `BUNDLE_VALIDATION_PASS_2_SHA: PENDING` is NOT present in this list either.

**R57 Fix:** Add `BUNDLE_VALIDATION_PASS_2_SHA: PENDING` and `BUNDLE_VALIDATION_PASS_1_SHA: PENDING`
to both `PENDING_MARKER_PATTERNS` and `STATUS_LINE_PATTERNS`. Add `test_r57_pending_marker_strictness.py`.

---

## IV-R56-005: test_r56_package_rc.py Hardcoded .local/ Path

**Severity:** MAJOR
**Category:** Test portability

**Finding:** `tests/packaging/test_r56_package_rc.py` line 24:
```python
ARTIFACTS_DIR = PROJECT_ROOT / ".local" / "r56-metadata" / "package-artifacts"
```
This path does not exist in a clean-extracted bundle (`.local/` is gitignored). Anyone
running this test from a fresh `git clone` or extracted bundle ZIP will get 16 failures
immediately (TestPackageArtifactsExist).

**Evidence:** File confirmed. Path is absolute and cannot be overridden without modifying the test.

**R57 Fix:**
- Create `tools/packaging/find_bundle_artifacts.py` — discovery function that checks
  `.local/r57-metadata/package-artifacts/` then `bundle-metadata/package-artifacts/`
- `test_r57_package_rc.py` uses discovery function; skips gracefully when dir absent

---

## IV-R56-006 / IV-R56-007: Truncated SHA-256 in Manifest / Validator Silent Skip

**Severity:** MAJOR
**Category:** Evidence integrity

**Finding:** `.local/r56-metadata/package-artifact-manifest.yaml` line 12:
```yaml
wheel_sha256: 9c10377a748a5f0df9b6e0817a5249ff
```
All 7 entries have 32-char hexadecimal values (MD5 length), not 64-char SHA-256 values.

**Validator behavior:** `check_artifact_inventory()` (lines 424):
```python
sha_match = re.search(r'(?:SHA-256|sha256):\s*([0-9a-fA-F]{64})', stripped)
```
The regex requires exactly 64 hex chars, so the 32-char values silently fail to match.
No SHA validation occurs, no error is reported.

**R57 Fix:**
- Recompute all 7 wheel SHA-256 values from actual `.whl` bytes
- Add explicit SHA length check in validator: warn/error when `wheel_sha256` length != 64
- Update manifest with correct 64-char SHA values

---

## IV-R56-008: final-bundle-validation-proof.txt Missing Required Fields

**Severity:** MAJOR
**Category:** Evidence completeness

**Finding:** `.local/r56-metadata/final-bundle-validation-proof.txt` contains only:
```
R56 Final Bundle Validation Proof
Sprint: FORMAT-FACTORY-R56-...
Python tests (non-AI): 3892 passed, 13 skipped, 2 pre-existing fail
Python tests (AI): 617 passed
.NET tests: 302 passed
Invariants: PASS (14/14)
State snapshot: R56 current
Contract: FORMAT-FACTORY-R56-...
BUNDLE_BUILD: PASS (see below after validation)
```

Missing required self-verifying fields:
- Bundle filename (r56-pass2-final.zip)
- SHA-256 of the bundle (Pass 1 and Pass 2)
- Size in bytes
- Entry count
- Sidecar proof path
- Exit code from validator run
- `BUNDLE_VALIDATION: PASS` confirmation line

**R57 Fix:** R57 final proof must include all fields. `test_r57_final_proof_completeness.py`
will verify proof contains all required keys.

---

## IV-R56-009: R56 Overstated Format Advancement

**Severity:** MINOR
**Category:** Overclaim

**Finding:** `reports/r56/next-format-advancement.md` Section 4 table includes PPM, DIF, SYLK, PGM, PBM
under "Next-Format Advancement" even though no code or tests were changed for these formats.

Exact quotes from report:
- "PPM Gates 1-10 confirmed at local_release_candidate_ready (no new work)"
- "DIF Gates 1-10 confirmed at local_release_candidate_ready (no new work)"
- "SYLK Gates 1-9 confirmed pass (no new work)"
- "PGM Gates 1-9 status confirmed (Gate 10 deferred — next sprint)"
- "PBM Gates 1-9 status confirmed (Gate 10 deferred — next sprint)"

Status confirmation without code/test work is not advancement. Only CSV and TSV
received actual advancement (Gate 4 → Gate 5) in R56.

**R57 Fix:** R57 Train F must advance ≥4 tracks with actual code and tests. Status confirmation
does not count as advancement in R57.

---

## IV-R56-010: fods.yaml unsupported_capabilities Conflicts with TC-0055

**Severity:** MINOR
**Category:** Release manifest accuracy

**Finding:** `release-manifests/python-foss/fods.yaml` line 48:
```yaml
unsupported_capabilities:
  - Cell style/formatting preservation
```

**TC-0055 closure evidence** (taskcards/TC-0055-style-metadata-fods.md):
- Closed R55
- `office:automatic-styles` captured in `_auto_styles_elem` in `parser.py`
- `office:styles` captured in `_styles_elem` in `parser.py`
- Writer `workbook_to_xml()` re-emits both before `office:body`
- 5 tests in `TestStyleMetadataCapture` — all pass

**Conclusion:** Raw style metadata XML (`office:automatic-styles`, `office:styles`) IS preserved.
"Cell style/formatting preservation" is ambiguous and conflicts with TC-0055.

**R57 Fix:** Split into:
- Unsupported: "Full visual style fidelity (colors, fonts, column widths round-trip)"
- Supported (already in key_capabilities): "Style metadata XML passthrough (office:automatic-styles preserved verbatim)"

---

## IV Summary

| ID | Severity | Category | R57 Train |
|----|----------|----------|-----------|
| IV-R56-001 | BLOCKING | Evidence protocol gap | B/L |
| IV-R56-002 | MAJOR | Contract incompleteness | B |
| IV-R56-003/004 | MAJOR | Validator gap | B |
| IV-R56-005 | MAJOR | Test portability | C |
| IV-R56-006/007 | MAJOR | Evidence integrity | D |
| IV-R56-008 | MAJOR | Evidence completeness | B/L |
| IV-R56-009 | MINOR | Overclaim | F |
| IV-R56-010 | MINOR | Release manifest accuracy | E |

**IV VERDICT:** R56_MULTI_MEGA_TRAIN_PRODUCT_PROGRESS_ACCEPTED_PACKAGE_RC_PARTIAL_CLOSURE_REJECTED

All positive deliverables (TC-0057/TC-0059 closed, 96 new tests, 302 .NET pass,
CSV/TSV Gate 5, 7 wheels) are accepted. Eight specific closure gaps require R57 repair.
