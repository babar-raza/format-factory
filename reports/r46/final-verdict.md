# R46 Final Verdict

**Sprint:** FORMAT-FACTORY-R46-ARTIFACT-CONTAINED-TWO-PRODUCT-RC-001
**Date:** 2026-05-21
**Verdict:** **R46_TWO_PRODUCT_ARTIFACT_CONTAINED_RC_BASELINE**

---

## Summary

R46 converts R45 from an overclaimed "REPLAYABLE" baseline into a genuinely
artifact-contained two-product RC baseline. All 8 R45 blockers are closed.

---

## What Was Accomplished

### MT1: R45 IV + Closeout Hardening

**Lane 1A — R45 Independent Verification**
- R45 classified: `R45_RC_PROGRESS_ACCEPTED_ARTIFACT_AND_CONSUMER_REPLAY_PARTIAL`
- R45 verdict of "REPLAYABLE" was overclaimed — bundle had no actual artifacts, consumer proof not bundled
- Full IV: `reports/r46/r45-independent-verification.md`

**Lane 1B — Validator: repo/reports pending check**
- Root cause: `check_no_pending_reports()` only scanned `bundle-metadata/` files
- Fix: new `check_repo_reports_pending()` function scans `repo/reports/<RUN>/final-verdict.md`
- False-positive guard: markdown list items (`- BUNDLE_VALIDATION: PENDING ref`) are NOT flagged
- **14 new tests** in `tests/evidence/test_r46_validator_hardening.py` — all PASS
- R45 defect reproduced and caught in test

**Lane 1C — R46 Contract**
- `tools/evidence/contracts/r46-artifact-contained-two-product-rc.yaml` created
- `require_clean_git: true`, `min_metadata_count: 30`
- 10 named `required_metadata_files` (meets REQUIRED_METADATA_DEPTH_MINIMUM_NAMED)

### MT2: Artifact-Contained Package Proof

**Lane 2A/2B/2C — Artifacts in bundle-metadata/package-artifacts/**
- All 6 artifacts rebuilt and included in `bundle-metadata/package-artifacts/`:
  - `aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl` (SHA: 0d9e6826...)
  - `aspose_format_factory_fods-0.1.0.dev0.tar.gz` (SHA: 58c842df...)
  - `aspose_format_factory_fodt-0.1.0.dev0-py3-none-any.whl` (SHA: 513e84aa...)
  - `aspose_format_factory_fodt-0.1.0.dev0.tar.gz` (SHA: 0ccca2da...)
  - `FormatFactory.Fods.0.1.0-tier0.nupkg` (SHA: 8868b910...)
  - `FormatFactory.Fodt.0.1.0-tier0.nupkg` (SHA: 30028823...)
- Installed-wheel smoke: PASS (both FODS and FODT install cleanly in fresh venv)

### MT3: Consumer Proof Replayability

**Lane 3A/3B — Consumer projects from bundled artifacts**
- Created `.local/consumer-proof-r46/` with `nuget.config` pointing to `r46-metadata/package-artifacts/`
- FODS: `dotnet restore` + `dotnet run` → `FODS_CONSUMER_PROOF: PASS` (sheet_count=1)
- FODT: `dotnet restore` + `dotnet run` → `FODT_CONSUMER_PROOF: PASS` (paragraph_count=1)
- **11 new tests** in `tests/evidence/test_r46_consumer_proof.py` — all PASS

### MT4: Timeout and Bounded Replay Repair

**Lane 4A — pytest.ini filterwarnings fix**
- Added `filterwarnings = ignore:Unknown config option.*timeout:pytest.PytestConfigWarning`
- Suppresses warning in clean envs without pytest-timeout; no effect when pytest-timeout is installed

**Lane 4B — tools/testing/run_bounded_pytest.py**
- Created subprocess wrapper with wall-clock timeout (no pytest-timeout required)
- `--suite <path> --max-seconds <N>` CLI; exit code 2 for timeout
- **11 new tests** in `tests/evidence/test_r46_timeout_portability.py` — all PASS

### MT5: Phase Audit 1 — Specification Ingestion

**Lane 5A — Phase Audit Roadmap**
- `reports/r46/phase-audit-roadmap.md`: 7 phases defined, one per sprint (R46-R52)

**Lane 5B/5C/5D — Phase 1 Audit**
- `reports/r46/phase-audit/phase-01-specification-ingestion.md`
- FODS: ODF 1.3 cached, SHA recorded — PASS
- FODT: Reuses FODS spec cache (documented) — PASS
- ZST: Two RFCs cached — PASS
- ODS/ODT: Documented reuse — PASS
- QOI/XCF/DIF/PPM/PGM/PBM/SYLK: Source URLs documented but no local cache — PARTIAL
- **PHASE_AUDIT_1: PASS** (no overclaimed provenance; gaps are documentation-level)

### MT6: Two-Product Capability Deepening

**Lane 6A — FODS Python write/export**
- `src/python/fods/writer.py`: `write_fods()` + `workbook_to_xml()`
- **16 new tests** in `tests/python/fods/test_r46_write_capability.py` — all PASS
- Round-trip verified: write → parse → same sheet count/name

**Lane 6B — FODT Python write/export**
- `src/python/fodt/writer.py`: `write_fodt()` + `document_to_xml()`
- **15 new tests** in `tests/python/fodt/test_r46_write_capability.py` — all PASS
- Round-trip verified: write → parse → same block count/content

---

## Test Counts

| Suite | Result |
|-------|--------|
| tests/state/ + tests/evidence/ + tests/requirements/ + tests/packaging/ (excl auto_proof) | 856 passed |
| tests/evidence/test_auto_proof_bundle.py | 9 passed |
| tests/python/ | 1041 passed, 2 pre-existing fail, 4 skip |
| .NET FODS | 157 passed |
| .NET FODT | 145 passed |
| **AUTHORITATIVE_TEST_RESULT** | **2208 passed, 2 pre-existing fail, 4 skip** |

Pre-existing failures (tracked since R29):
- `tests/python/dif/test_dif_parser.py::TestDifProbe::test_probe_nonexistent`
- `tests/python/ppm/test_ppm_parser.py::TestPpmProbe::test_probe_nonexistent`

---

## New Tests Added (R46 Only)

| File | Tests |
|------|-------|
| `tests/evidence/test_r46_validator_hardening.py` | 14 |
| `tests/evidence/test_r46_timeout_portability.py` | 11 |
| `tests/evidence/test_r46_consumer_proof.py` | 11 |
| `tests/python/fods/test_r46_write_capability.py` | 16 |
| `tests/python/fodt/test_r46_write_capability.py` | 15 |
| **Total R46 new tests** | **67** |

---

## Active Blockers (Unchanged)

- **G11-G NOT_STARTED:** Gate 11 commercial approval requires Babar Raza written approval
- **ODS/ODT/QOI/XCF/DIF/PPM Gate 8:** Human review of security packets pending
- **commercial_product_ready: false** (all formats — requires C7+ + G11-G approval)
- **No push authorized:** Local artifacts only (PACKAGE_NOT_PUSHED)

---

## Deferred to R47

- ZST RC designation
- PGM/PBM/SYLK Gate 10
- AI acceleration (MT8)
- QOI/XCF/DIF spec caching (Phase Audit 2 targets)

---

## Package Artifacts (Included in Bundle, Local Only, R46)

| Artifact | SHA-256 |
|----------|---------|
| aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl | 0d9e6826515d849052bcda7f8546515063e51ab93d23e7183715c96b45c26014 |
| aspose_format_factory_fods-0.1.0.dev0.tar.gz | 58c842dff73727c29ebda4f9d1607707b55300cea431717000c26b59b33182bd |
| aspose_format_factory_fodt-0.1.0.dev0-py3-none-any.whl | 513e84aaa5b29c90128d11d4c80f3ce2c451cc0d5d9c8801b044b7b49ca391a5 |
| aspose_format_factory_fodt-0.1.0.dev0.tar.gz | 0ccca2da1ecae8388a48ebf35340af90df522a2f2f755227866009cd1d9a4962 |
| FormatFactory.Fods.0.1.0-tier0.nupkg | 8868b910b8917a20ca6638356c88f5e06af390f59787fcde12fac0d0b5822dcf |
| FormatFactory.Fodt.0.1.0-tier0.nupkg | 3002882389249bbbb6736ac1d6a123499dadff94658d48bbc2d524fcade03b24 |

---

BUNDLE_VALIDATION: PENDING
