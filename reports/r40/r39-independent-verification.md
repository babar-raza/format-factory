# R40 Lane A: R39 Independent Verification Report

**Sprint:** R40
**Date:** 2026-05-21
**Reviewer:** R40 agent (independent session)
**Subject:** R39 partial-closure findings

## R39 Independent Review Classification

| # | Finding | R39 Status | R40 Action | R40 Result |
|---|---------|-----------|------------|------------|
| F01 | Gateway.py binds `get_api_key` directly — test patches to `config.get_api_key` don't affect bound symbol | CONFIRMED_BUG | Fixed: `import tools.ai.control_plane.config as _ai_config`, call `_ai_config.get_api_key()` at call site | FIXED |
| F02 | ODS path traversal test uses `/etc/passwd` — false negative on Linux (file pre-exists) | CONFIRMED_BUG | Fixed: use `uuid.uuid4().hex` sentinel + `tempfile.TemporaryDirectory()` sandbox | FIXED |
| F03 | ZST `decompress_bytes()` calls `_get_zstandard()` before magic check | CONFIRMED_BUG | Fixed in R40: magic/type check moved before `_get_zstandard()` call | FIXED (committed in R40) |
| F04 | Package `test_tracked_files_returns_list` hard-asserts non-empty — fails without `.git` | CONFIRMED_BUG | Fixed: `pytest.skip` when `get_tracked_files()` returns `[]` (no-Git mode) | FIXED |
| F05 | Python FODS/FODT packages not in package-matrix.yaml, no wheel/sdist built | CONFIRMED_GAP | Added to matrix, built wheels: fods 10,696B whl + 9,525B sdist; fodt 12,290B whl + 10,589B sdist | FIXED |
| F06 | fods/fodt `__init__.py` missing `__commercial_ready__`/`__capability_level__` | CONFIRMED_GAP | Added `__track__`, `__commercial_ready__ = False`, `__capability_level__ = "alpha-foss-preview"` to both | FIXED |
| F07 | `test_python_package_matrix.py` hardcoded count==5, missing fods/fodt in EXPECTED_PACKAGES | CONFIRMED_GAP | Updated count to 7, EXPECTED_PACKAGES and EXPECTED_MODULES to include fods/fodt | FIXED |
| F08 | .NET NuGet packs used `--no-build` with stale 11,776B DLL (FodsDocument not in binary) | CONFIRMED_BUG | Rebuilt with `dotnet build` + `dotnet pack`, DLL now 25,600B (FODS) / 23,552B (FODT) | FIXED |
| F09 | No NuGet consumer smoke test executed | CONFIRMED_GAP | Consumer project created + smoke test run: `FodsDocumentException` caught, `SMOKE_OK` confirmed | FIXED |

## Summary

All 9 R39 findings reproduced and resolved. No findings carried forward.

**R39 Classification:** PARTIAL_PROGRESS_WITH_OVERCLAIMED_CLOSURE (confirmed)
**R40 Classification:** FIXES_COMPLETE — all 9 findings addressed with evidence.
