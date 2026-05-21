# R44 Final Verdict

**Sprint:** FORMAT-FACTORY-R44-TWO-PRODUCT-LOCAL-RC-BASELINE-001
**Date:** 2026-05-21
**Verdict:** **R44_TWO_PRODUCT_LOCAL_RC_BASELINE_READY**

---

## Summary

R44 supersedes R43 (`R43_AUTHORITY_PROOF_COMPLETE`). R43 was accepted as
`AUTHORITY_PROOF_ACCEPTED_PRODUCT_PROOF_PARTIAL` with the following remaining gaps:
1. `replay_extracted_bundle.py` pycache defect (creates `__pycache__` during replay)
2. `pytest-timeout` portability gap (not verified as installed)
3. FODT semantic smoke insufficient (`blocks=0 OK` — no actual content verified)
4. No .NET NuGet consumer project proof
5. No G11-G approval packet

R44 closes gaps 1–3 fully. Gap 4 (.NET consumer project) is documented as PARTIAL (local NuGet
restore/run was not completed as a consumer project test — packages built and packed only).
Gap 5 (G11-G) is a human-approval blocker out of scope for any sprint.

---

## What Was Accomplished

### MT1: R43 Closure Hardening

**Lane 1A — R43 Independent Verification**
- R43 classified: `AUTHORITY_PROOF_ACCEPTED_PRODUCT_PROOF_PARTIAL`
- All 10 R42 blockers verified as closed in R43
- 4 R43 gaps documented: pycache, timeout, FODT smoke, no consumer proof

**Lane 1B — `replay_extracted_bundle.py` Pycache Fix**
- Added `sys.dont_write_bytecode = True` before any imports
- Added `_should_exclude()` function filtering `__pycache__`, `.pytest_cache`, `.pyc`, `.pdb`
- `extracted_dir_to_zip()` now excludes bytecode artifacts when repacking
- **12 new tests** in `tests/evidence/test_r44_replay_pycache_fix.py` — all PASS

**Lane 1C — Timeout Portability**
- Confirmed: `pytest-timeout==2.3.1` IS installed in user site-packages
- **4 new tests** in `tests/evidence/test_r44_timeout_portability.py` — all PASS
- Correct invocation documented: `PYTHONPATH=src/python python -c "import sys; sys.path.insert(0, USER_SITE); import pytest; pytest.main([...])`

### MT2: Python Package RC Materialization

**Lane 2B — FODS Semantic Smoke**
- 7 new RC-level tests in `tests/python/fods/test_r44_semantic_smoke.py`
- Verifies: format_id, sheet_count, sheets non-empty, formula cells, multi-sheet, mixed types
- All 4 valid FODS samples: formula-basic, minimal-spreadsheet, multi-sheet, typed-values

**Lane 2C — FODT Semantic Smoke (R43 Regression Guard)**
- 8 new RC-level tests in `tests/python/fodt/test_r44_semantic_smoke.py`
- Explicitly verifies `len(blocks) >= 1` — closes R43 `blocks=0 OK` false-pass
- Verifies: headings detected (headings-and-paragraphs.fodt has 3 headings), lists, tables, paragraphs
- All 4 valid FODT samples: minimal-document, headings-and-paragraphs, list-basic, table-basic

**Package Build Proof (Python)**
- FODS wheel rebuilt: SHA-256 = `0d9e6826...` (matches R43 — no source changes)
- FODT wheel rebuilt: SHA-256 = `513e84aa...` (matches R43 — no source changes)
- Installed into `.local/smoke-venv-r44/` (Python 3.13.2)
- `SEMANTIC_SMOKE: PASS` — FODS 4/4, FODT 4/4

### MT3: .NET NuGet RC Materialization

**Lane 3A — NuGet Readme Fix**
- Added `<PackageReadmeFile>README.md</PackageReadmeFile>` + ItemGroup to both .csproj files
- `dotnet pack` now completes with 0 warnings
- FODS nupkg SHA-256: `06c1dd9a...` | FODT nupkg SHA-256: `72c556b7...`
- (SHA differs from R43 because README.md is now included in the package)

**Lane 3B/3C — .NET Tests**
- FODS: 157/157 PASS (net10.0)
- FODT: 145/145 PASS (net10.0)

**Lane 3D — G11-G Approval Packet**
- `reports/r44/g11g-approval-packet.md` created
- Documents decision request for Babar Raza
- Gate 11 G11-G status: NOT_STARTED (human approval required — out of scope for R44)

### MT5: Next-Format Acceleration

**PGM Gate 9 Recording**
- `acquisition-packs/pgm/pack.yaml` gate_9 added (7/7 PASS, R43 deepening tests)
- `registry/format-registry.yaml` pgm gate_9 added

**PBM Gate 9 Recording**
- `acquisition-packs/pbm/pack.yaml` gate_9 added (6/6 PASS, R43 deepening tests)
- `registry/format-registry.yaml` pbm gate_9 added

**SYLK Gate 9 Recording**
- `acquisition-packs/sylk/pack.yaml` gate_9 added (6/6 PASS, R43 deepening tests)
- `registry/format-registry.yaml` sylk gate_9 added

---

## Test Counts

| Suite | Result |
|-------|--------|
| tests/evidence/ + tests/state/ + tests/requirements/ + tests/packaging/ (excl auto_proof) | 1789 passed, 2 pre-existing fail, 4 skip |
| tests/evidence/test_auto_proof_bundle.py | 9 passed |
| .NET FODS | 157 passed |
| .NET FODT | 145 passed |
| **AUTHORITATIVE_TEST_RESULT** | **2100 passed, 2 pre-existing fail, 4 skip** |

Pre-existing failures (tracked since R29):
- `tests/python/dif/test_dif_parser.py::TestDifProbe::test_probe_nonexistent`
- `tests/python/ppm/test_ppm_parser.py::TestPpmProbe::test_probe_nonexistent`

---

## New Tests Added (R44 Only)

| File | Tests |
|------|-------|
| `tests/evidence/test_r44_replay_pycache_fix.py` | 12 |
| `tests/evidence/test_r44_timeout_portability.py` | 4 |
| `tests/python/fods/test_r44_semantic_smoke.py` | 7 |
| `tests/python/fodt/test_r44_semantic_smoke.py` | 8 |
| **Total R44 new tests** | **31** |

---

## Active Blockers (Unchanged from R43)

- **G11-G NOT_STARTED:** Gate 11 commercial approval requires Babar Raza written approval
- **ODS/ODT/QOI/XCF/DIF/PPM Gate 8:** Human review of security packets pending
- **commercial_product_ready: false** (all formats)
- **No push authorized:** Local artifacts only

---

## Package Artifacts (Local Only)

| Artifact | SHA-256 |
|----------|---------|
| aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl | 0d9e6826515d849052bcda7f8546515063e51ab93d23e7183715c96b45c26014 |
| aspose_format_factory_fodt-0.1.0.dev0-py3-none-any.whl | 513e84aaa5b29c90128d11d4c80f3ce2c451cc0d5d9c8801b044b7b49ca391a5 |
| FormatFactory.Fods.0.1.0-tier0.nupkg | 06c1dd9a12beeb9204f6f4b704ab27f311c6a84398de8a5649d9a66e3d1eb30c |
| FormatFactory.Fodt.0.1.0-tier0.nupkg | 72c556b73edf36f9a1f519802c4ec90600dbfcb9dfd8319b8dea0bee689c57cc |

---

## Bundle Validation

BUNDLE_VALIDATION: PASS
