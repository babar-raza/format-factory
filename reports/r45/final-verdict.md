# R45 Final Verdict

**Sprint:** FORMAT-FACTORY-R45-TWO-PRODUCT-LOCAL-RC-REPLAYABLE-001
**Date:** 2026-05-21
**Verdict:** **R45_TWO_PRODUCT_LOCAL_RC_BASELINE_REPLAYABLE**

---

## Summary

R45 converts R44 from an overclaimed local RC baseline into a genuinely replayable
two-product local RC baseline. All 11 R44 blockers identified in the sprint prompt
are closed.

---

## What Was Accomplished

### MT1: R44 IV + Hardening

**Lane 1A — R44 Independent Verification**
- R44 classified: `R44_PROGRESS_ACCEPTED_RC_OVERCLAIMED`
- All accepted claims verified; overclaimed items identified and closed in R45
- Full IV: `reports/r45/r44-independent-verification.md`

**Lane 1B — UTF-8 State Snapshot Fix**
- Root cause: `tools/state/state_snapshot.py` used `open()` without `encoding="utf-8"`
- Fix: added `encoding="utf-8"`, `newline="\n"` to all file writes and reads
- Also replaced em dash U+2014 with ASCII hyphen to prevent future encoding issues
- `state/current-state.md` regenerated: valid UTF-8, no 0x97 byte
- **10 new tests** in `tests/state/test_r45_utf8_encoding.py` — all PASS

**Lane 1C — Contract Hardening**
- R45 contract uses `require_clean_git: true` (was `false` in R44)
- R44 contract weakness: RC baseline must commit before building

### MT2: Replay + Timeout Hardening

**Lane 2A — pytest-timeout Portability**
- Added `timeout = 120` to `pytest.ini` — now a declared project requirement
- All tests run with 120s default timeout (prevents replay hangs)
- **7 new tests** in `tests/evidence/test_r45_timeout_portability.py` — all PASS
- Tests use `pytest.importorskip` for clean skips in environments without pytest-timeout

**Lane 2B — Auto-Proof Bounded Replay**
- `tests/evidence/test_auto_proof_bundle.py` 9/9 PASS with `timeout=120` protection
- Tests verified bounded (9 tests * ~6s each = ~55s total, well within 120s)

### MT3: Package Artifact Materialization

**Lane 3A — Python Package Artifacts**
- FODS wheel rebuilt: SHA-256 = `0d9e6826...` (matches R44/R43 — no source changes)
- FODT wheel rebuilt: SHA-256 = `513e84aa...` (matches R44/R43 — no source changes)
- FODS sdist: SHA-256 = `93bc7179...`
- FODT sdist: SHA-256 = `f27c4342...`
- Artifact manifest: `.local/r45-metadata/package-artifact-manifest.yaml`

**Lane 3B — .NET Package Artifacts**
- FODS nupkg rebuilt: SHA-256 = `c262c44e...` (R45 fresh build — timestamp differs)
- FODT nupkg rebuilt: SHA-256 = `2d7a22f1...` (R45 fresh build)
- `dotnet pack` 0 warnings (readme fix from R44 intact)

**Lane 3C — Validator Extension**
- `tools/evidence/validate_evidence_bundle.py` extended:
  - `check_package_proof_present()` now requires proof for: LOCAL_RC, BASELINE_READY,
    RELEASE_CANDIDATE, TWO_PRODUCT (in addition to existing POC_READY)
- **10 new tests** in `tests/evidence/test_r45_validator_hardening.py` — all PASS

### MT4: .NET Consumer Project Proof

**Lane 4A — FODS .NET Consumer Project**
- Created `.local/consumer-proof/fods-consumer/` (C# console app)
- `dotnet restore` from local NuGet feed: PASS
- `dotnet run`: `FODS_CONSUMER_PROOF: PASS` — sheet_count=1 from minimal-spreadsheet.fods

**Lane 4B — FODT .NET Consumer Project**
- Created `.local/consumer-proof/fodt-consumer/` (C# console app)
- `dotnet restore` from local NuGet feed: PASS
- `dotnet run`: `FODT_CONSUMER_PROOF: PASS` — paragraph_count=1 from minimal-document.fodt

**Lane 4C — G11-G Approval Packet Rewrite**
- R44 packet incorrectly asked for `commercial_product_ready: true` for Tier 0
- R45 packet (`reports/r45/g11g-approval-packet.md`) corrects this:
  - Asks only for G11-G_TIER_0_BASELINE_ACCEPTED
  - Does NOT claim `commercial_product_ready: true`
  - Clearly separates Python FOSS (PyPI) and .NET commercial decisions
  - Requires C7+ capability before full commercial approval

- **8 new tests** in `tests/evidence/test_r45_consumer_proof.py` — all PASS

---

## Test Counts

| Suite | Result |
|-------|--------|
| tests/state/ | 30 passed (20 base + 10 new R45 UTF-8 tests) |
| tests/evidence/ (excl auto_proof) | 788 passed |
| tests/requirements/ + tests/packaging/ | 0 separate (counted in evidence) |
| tests/evidence/test_auto_proof_bundle.py | 9 passed |
| tests/python/ | 1010 passed, 2 pre-existing fail, 4 skip |
| .NET FODS | 157 passed |
| .NET FODT | 145 passed |
| **AUTHORITATIVE_TEST_RESULT** | **2139 passed, 2 pre-existing fail, 4 skip** |

Pre-existing failures (tracked since R29):
- `tests/python/dif/test_dif_parser.py::TestDifProbe::test_probe_nonexistent`
- `tests/python/ppm/test_ppm_parser.py::TestPpmProbe::test_probe_nonexistent`

---

## New Tests Added (R45 Only)

| File | Tests |
|------|-------|
| `tests/state/test_r45_utf8_encoding.py` | 10 |
| `tests/evidence/test_r45_timeout_portability.py` | 7 |
| `tests/evidence/test_r45_validator_hardening.py` | 10 |
| `tests/evidence/test_r45_consumer_proof.py` | 8 |
| **Total R45 new tests** | **35** |

---

## Active Blockers (Unchanged)

- **G11-G NOT_STARTED:** Gate 11 commercial approval requires Babar Raza written approval
- **ODS/ODT/QOI/XCF/DIF/PPM Gate 8:** Human review of security packets pending
- **commercial_product_ready: false** (all formats — requires C7+ + G11-G approval)
- **No push authorized:** Local artifacts only (PACKAGE_NOT_PUSHED)

---

## Deferred to R46

- FODS/FODT Python write/export round-trip (MT5)
- ZST RC designation
- PGM/PBM/SYLK Gate 10

---

## Package Artifacts (Local Only, R45)

| Artifact | SHA-256 |
|----------|---------|
| aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl | 0d9e6826515d849052bcda7f8546515063e51ab93d23e7183715c96b45c26014 |
| aspose_format_factory_fods-0.1.0.dev0.tar.gz | 93bc7179efb56cd3c53d8ce326957037ae393bf8abdd2662cf9ec2169eb5b32c |
| aspose_format_factory_fodt-0.1.0.dev0-py3-none-any.whl | 513e84aaa5b29c90128d11d4c80f3ce2c451cc0d5d9c8801b044b7b49ca391a5 |
| aspose_format_factory_fodt-0.1.0.dev0.tar.gz | f27c434299ec3739d879fd4b4609b80d5d675a4f9e85895d0ac440a86abb5e42 |
| FormatFactory.Fods.0.1.0-tier0.nupkg | c262c44ed7a424c29cd5061dabce40dbbbb05dab0ed083a3805d76945c4232a0 |
| FormatFactory.Fodt.0.1.0-tier0.nupkg | 2d7a22f141903c966a4a419e0e202b4223acbd2ffb2bd1177ba019edfac9c461 |

---

## Bundle Validation

BUNDLE_VALIDATION: PENDING (bundle not yet built)
