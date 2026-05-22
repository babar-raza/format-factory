# R46 Independent Verification

**Sprint:** FORMAT-FACTORY-R47-ARTIFACT-PROOF-REPAIR-AND-PHASE-AUDIT-PROGRESSION-001
**Date:** 2026-05-22
**Verifier:** R47 preflight + direct ZIP inspection

---

## R46 Verdict (Before IV)

`R46_TWO_PRODUCT_ARTIFACT_CONTAINED_RC_BASELINE`

## R46 Verdict (After IV)

`R46_CODE_PROGRESS_ACCEPTED_ARTIFACT_CONTAINMENT_FALSE`

---

## Claim-by-Claim Classification

| Claim | Classification | Evidence |
|-------|----------------|----------|
| FODS/FODT Python writer capability (write_fods/write_fodt) | **VERIFIED** | Tests pass: 311 passed (fods+fodt), 4 skip |
| FODS/FODT source tests pass | **VERIFIED** | 1041 tests/python/, 2 pre-existing fail |
| Validator: check_repo_reports_pending() added | **VERIFIED** | Code present, 14 tests pass |
| pytest.ini filterwarnings fix | **VERIFIED** | Confirmed in pytest.ini |
| tools/testing/run_bounded_pytest.py created | **VERIFIED** | File present |
| Phase Audit 1 started | **VERIFIED** | reports/r46/phase-audit/phase-01-specification-ingestion.md present |
| R46 clean git status at close | **VERIFIED** | HEAD=9f0e30d, no uncommitted changes |
| AI remained non-authoritative | **VERIFIED** | No AI-generated code in sprint |
| Package artifact containment in bundle | **FALSE** | Direct ZIP inspection: 0 .whl, 0 .tar.gz, 0 .nupkg in .local/r46-bundle.zip |
| Artifacts in bundle-metadata/package-artifacts/ | **FALSE** | Builder iterdir() skips subdirectories — artifacts never entered ZIP |
| package-artifact-manifest.yaml claims match ZIP | **FALSE** | Manifest lists 6 artifacts; ZIP has 0 |
| Consumer proof replayable from extracted bundle | **FALSE** | Consumer projects use .local/consumer-proof-r46/ which is not in bundle |
| Validator detected artifact absence | **FALSE** | Validator passed because it only checks for manifest file, not actual artifacts |
| Phase Audit 1: PHASE_AUDIT_1: PASS | **PARTIAL** | Core formats PASS; QOI/XCF/DIF/PPM/PGM/PBM/SYLK have no local spec cache |
| Phase audit roadmap Phase 2 correct | **FALSE** | R46 roadmap Phase 2 was "Parser Quality"; required Phase 2 is "Sample Acquisition/Provenance" |
| AUTHORITATIVE_TEST_RESULT: 2208 passed | **VERIFIED** | Confirmed by two background task completions |

---

## Root Cause Analysis

### Root Cause 1: Builder subdirectory omission

File: `tools/evidence/build_evidence_bundle.py` lines 349-352:

```python
if metadata_path and metadata_path.exists():
    for mf in sorted(metadata_path.iterdir()):
        if mf.is_file():
            metadata_files.append(mf.name)
```

Only top-level files in `--metadata-dir` are included. `package-artifacts/` is
a subdirectory — it is never iterated and its contents are never added to the ZIP.

**Fix required:** Recursively include subdirectory files from metadata dir,
preserving relative path under `bundle-metadata/` in the ZIP.

### Root Cause 2: Validator accepts manifest without artifacts

`validate_evidence_bundle.py` accepts `bundle-metadata/package-artifact-manifest.yaml`
as sufficient proof. It does not verify that named artifact files actually exist in
the ZIP as entries.

**Fix required:** Add `check_artifact_inventory()` — compare manifest claims
against actual ZIP entries; fail if claimed files are absent; validate SHA-256.

### Root Cause 3: Phase Audit roadmap drift

R46 roadmap was authored from sprint priorities, not from the required phase sequence.
Phase 2 was set to "Parser Implementation Quality" instead of
"Sample Acquisition / Sample Provenance".

**Fix required:** Replace roadmap with the correct phase sequence.

---

## R46 Preserved Work

The following R46 deliverables are genuine and preserved:

1. **FODS/FODT Python write capability** — `src/python/fods/writer.py` + `src/python/fodt/writer.py`
2. **R46 tests (67 new)** — all pass
3. **Validator hardening** — `check_repo_reports_pending()` prevents future PENDING leaks
4. **Bounded pytest wrapper** — `tools/testing/run_bounded_pytest.py`
5. **Phase Audit 1 (partial)** — core format audit complete; minor format gaps documented

---

## R46 Supersession Declaration

R46 is superseded as:

**`R46_CODE_PROGRESS_ACCEPTED_ARTIFACT_CONTAINMENT_FALSE`**

Justification:
- Code progress (writer, tests, validator, timeout repair) is real and accepted
- Artifact containment claim is FALSE: ZIP had 0 actual artifacts
- Consumer proof claim is FALSE: depends on .local/ which is not in ZIP
- Validator false positive: R46 validator passed a bundle with no artifacts

R46 must not be treated as an artifact-contained RC baseline.
R47 is the first sprint to actually attempt genuine artifact containment.

---

## R47 Remediation Plan

1. Fix builder to recursively include metadata subdirectories (Lane 1B)
2. Fix validator to check actual artifact presence (Lane 1B)
3. Build real Python/. NET artifacts and include them in bundle (Lanes 2A/2C)
4. Consumer replay from extracted bundle (Lane 3A)
5. Correct Phase Audit 1 verdict (Lane 4A)
6. Correct Phase Audit roadmap (Lane 4B)
7. Start Phase Audit 2: sample acquisition/provenance (Lanes 4C/4D)

R46_IV_STATUS: COMPLETE
R46_SUPERSESSION: R46_CODE_PROGRESS_ACCEPTED_ARTIFACT_CONTAINMENT_FALSE
