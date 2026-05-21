# R41 Lane K: POC Pipeline Matrix

**Sprint:** R41
**Date:** 2026-05-21

## Product Track Status

| Track | Format | Tests | Gate Status | Package | Smoke |
|-------|--------|-------|-------------|---------|-------|
| Python FOSS | FODS | 181 pass, 4 skip | Gates 1-10 PASS | 10,696B whl | PASS |
| Python FOSS | FODT | 181 pass, 4 skip | Gates 1-10 PASS | 12,290B whl | PASS |
| .NET Commercial | FODS | 157/157 | Gates 1-10 PASS (G11-G NOT_STARTED) | 25,600B DLL | PASS |
| .NET Commercial | FODT | 145/145 | Gates 1-10 PASS (G11-G NOT_STARTED) | 23,552B DLL | PASS |

All 4 product-track cells: GREEN.

## R41 Defect Closure Summary

| Defect | Lane | Fix | Status |
|--------|------|-----|--------|
| R40 final-verdict BUNDLE_VALIDATION: PENDING despite built bundle | A | Updated to PASS with SHA-256 | CLOSED |
| State snapshot captures R40_COMPLETE** (bold leak) | B | Changed regex to [A-Z0-9_]+ | CLOSED |
| test_auto_proof_bundle fails in no-Git extracted replay | E | Validator unexpected-folders → warning; test contract sets required_top_level_folders | CLOSED |
| test_gateway_lazy_import_produces_clear_error fails w/o litellm | F | Test now handles both litellm-present and absent paths | CLOSED |
| Package proof prose-only (no hashes) | D | SHA-256 hashes added for all 6 artifacts | CLOSED |
| Evidence ZIPs committed (bloat risk) | C | evidence-bundles/*.zip added to .gitignore; guard test added | CLOSED |

## Next Acceleration Opportunities

| Format | Track | Next Gate | Blocker |
|--------|-------|-----------|---------|
| ODS | Python FOSS | Gate 8 security review | Awaiting human approval |
| ODT | Python FOSS | Gate 8 security review | Awaiting human approval |
| QOI | Python FOSS | Gate 8 security review | Awaiting human approval |
| XCF | Python FOSS | Gate 8 security review | Awaiting human approval |
| DIF | Python FOSS | Gate 8 security review | Awaiting human approval |
| PPM | Python FOSS | Gate 8 security review | Awaiting human approval |
| FODS | .NET Commercial | Gate 11 G11-G | Awaiting Babar Raza approval |
| FODT | .NET Commercial | Gate 11 G11-G | Awaiting Babar Raza approval |

## Gate 11 Gap (FODS/FODT)

G11-G requires: Babar Raza written approval + C7+ capability demo.
Current state: g11f_hardening_in_progress. commercial_product_ready: false.
No NuGet or PyPI publication authorized.
