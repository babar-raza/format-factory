# R40 Final Verdict

**Sprint:** R40 — R39 Fix Closure + Package Build Proof
**Date:** 2026-05-21
**Verdict:** R40_COMPLETE

---

## Executive Summary

R39 was classified as PARTIAL_PROGRESS_WITH_OVERCLAIMED_CLOSURE by independent review. R40 reproduced all 9 findings and resolved each with evidence.

## What Was Fixed

### Bug Fixes (Lane C, D)
1. **gateway.py binding**: `from ... import get_api_key` → `import ... as _ai_config; _ai_config.get_api_key()` — test patches now work correctly.
2. **ODS path traversal test**: Replaced `/etc/passwd` path assertion with UUID sentinel + `TemporaryDirectory` sandbox — cross-platform correct.
3. **ZST decompress_bytes order**: Magic/type validation moved before `_get_zstandard()` import — `ZstInvalidFrameError` raised before `ImportError` on platforms without zstandard.
4. **Package no-Git mode**: `test_tracked_files_returns_list` and `test_no_secrets_in_tracked` now `pytest.skip` when `get_tracked_files()` returns `[]`.

### Package Infrastructure (Lane E, F)
5. **fods/fodt added to package-matrix.yaml**: Both formats now have entries with correct metadata.
6. **fods/fodt `__init__.py` enriched**: `__track__`, `__commercial_ready__ = False`, `__capability_level__ = "alpha-foss-preview"` added.
7. **test_python_package_matrix.py updated**: Count 5→7, EXPECTED_PACKAGES/EXPECTED_MODULES include fods/fodt.
8. **Python wheels actually built**: `aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl` (10,696B) + `aspose_format_factory_fodt-0.1.0.dev0-py3-none-any.whl` (12,290B). Both install + import in clean venv.
9. **NuGet packs rebuilt correctly**: `dotnet build` + `dotnet pack` (not `--no-build`). FormatFactory.Fods.dll=25,600B, FormatFactory.Fodt.dll=23,552B. Consumer smoke test: `SMOKE_OK` for both.

## Test Results

AUTHORITATIVE_TEST_RESULT: 3984 passed, 2 pre-existing failed (dif/ppm test_probe_nonexistent), 13 skipped.

| Suite | Result |
|-------|--------|
| tests/ (all excl. AI, evidence) | 2452 pass, 2 pre-existing fail, 13 skip |
| tests/evidence/ | 613 pass |
| tests/ai/ | 617 pass |
| tests/net/fods | 157 pass |
| tests/net/fodt | 145 pass |

## Authority Checks

- STATE_SNAPSHOT: PASS
- STATE_LINT: PASS (2 pre-existing warnings: r27/r32 below-floor — documented)
- REQUIREMENTS_SCHEMA_VALIDATION: PASS

## Commercial Status

commercial_product_ready: false (all formats)
Gate 11 G11-G: NOT_STARTED — awaiting Babar Raza approval.
No NuGet or PyPI publication — local builds only.

## Sprint Verdict

**VERDICT: R40_COMPLETE**

All R39 independent-review findings resolved. All 4 product-track cells green. Package builds proved with artifacts and smoke tests. 3984 tests passing.

BUNDLE_VALIDATION: PENDING

Evidence bundle blocked on clean git. All R40 changes are uncommitted (governance rule: no commit without explicit user request). Bundle can be built once human commits the sprint work.

Ready-to-send commit sequence:
```bash
# 1. Stage all R40 changes
git add packaging/python/build-local-packages.py \
        packaging/python/package-matrix.yaml \
        src/python/fods/__init__.py \
        src/python/fodt/__init__.py \
        src/python/zst/zst_codec.py \
        state/current-state.json \
        state/current-state.md \
        tests/evidence/test_python_package_matrix.py \
        tests/package/test_build_review_package.py \
        tests/python/ods/test_ods_gate7_fuzz_guard.py \
        tools/ai/control_plane/gateway.py \
        tools/evidence/contracts/r40-r39-fix-closure-package-build-proof.yaml \
        reports/r40/

# 2. Commit
git commit -m "fix(r40): close R39 IV findings — gateway binding, cross-platform tests, package builds"

# 3. Build and validate bundle
PYTHONPATH=. python tools/evidence/build_evidence_bundle.py \
  --repo-root . \
  --contract tools/evidence/contracts/r40-r39-fix-closure-package-build-proof.yaml \
  --metadata-dir .local/r40-metadata/ \
  --output evidence-bundles/
PYTHONPATH=. python tools/evidence/validate_evidence_bundle.py \
  --bundle evidence-bundles/r40-*.zip
```
