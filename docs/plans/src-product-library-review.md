# Source Product Library Review

**Date:** 2026-06-18
**Authority:** `C:/Users/prora/.claude/plans/smooth-juggling-moler.md`
**Source data:** `registry/source-structure-baseline.json`
**Status:** Documentation only — no source changes

## Executive Summary

Every Python codec/parser file in the format-factory library is at or over its frozen
`baseline_loc_cap`. Three formats (FODG, XCF, ZST) are significantly over cap and are
actively or latently blocked by `GOV_BLOCK:monolith_detection_validator`. All remaining
17 format files are exactly at their caps.

**Key finding:** The deepening-to-codec-files pattern is structurally exhausted across
the entire codebase AND violates master plan §24.7 (BINDING). New analytics functions
MUST go to `<format>_analytics.py` (create if not exists) — these files do NOT exist
yet and are at 0 LOC (not capped). The codec files are the WRONG target.

## Python Codec/Parser Files — LOC vs Cap

| File | Current LOC | Frozen Cap | Delta | Status | Risk |
|------|------------|-----------|-------|--------|------|
| `src/python/fodg/fodg_codec.py` | 5933 | 4334 | **+1599 (+37%)** | **BLOCKED NOW** | CRITICAL |
| `src/python/fodg/__init__.py` | 1386 | 1000 | **+386 (+39%)** | **BLOCKED NOW** | CRITICAL |
| `src/python/xcf/xcf_parser.py` | 5588 | 3997 | **+1591 (+40%)** | **LATENT BLOCK** | HIGH |
| `src/python/xcf/__init__.py` | 1279 | 894 | **+385 (+43%)** | **LATENT BLOCK** | HIGH |
| `src/python/zst/zst_codec.py` | 5750 | 4210 | **+1540 (+37%)** | **LATENT BLOCK** | HIGH |
| `src/python/zst/__init__.py` | 1267 | 867 | **+400 (+46%)** | **LATENT BLOCK** | HIGH |
| `src/python/fods/neutral_model.py` | 4129 | 4127 | **+2 OVER** | AT CAP | CRITICAL |
| `src/python/fodt/neutral_model.py` | 4097 | 4097 | 0 | AT CAP | HIGH |
| `src/python/abw/abw_codec.py` | 3215 | 3215 | 0 | AT CAP | HIGH |
| `src/python/gnumeric/gnumeric_codec.py` | 3706 | 3706 | 0 | AT CAP | HIGH |
| `src/python/ndjson/ndjson_codec.py` | 3396 | 3396 | 0 | AT CAP | MEDIUM |
| `src/python/ods/ods_parser.py` | 3584 | 3584 | 0 | AT CAP | MEDIUM |
| `src/python/dif/dif_parser.py` | 3382 | 3382 | 0 | AT CAP | MEDIUM |
| `src/python/tsv/tsv_parser.py` | 3351 | 3351 | 0 | AT CAP | MEDIUM |
| `src/python/sylk/sylk_parser.py` | 3276 | 3276 | 0 | AT CAP | MEDIUM |
| `src/python/csv/csv_parser.py` | 3026 | 3026 | 0 | AT CAP | MEDIUM |
| `src/python/pbm/pbm_parser.py` | 2902 | 2902 | 0 | AT CAP | MEDIUM |
| `src/python/pgm/pgm_parser.py` | 2831 | 2831 | 0 | AT CAP | MEDIUM |
| `src/python/ppm/ppm_parser.py` | 2802 | 2802 | 0 | AT CAP | MEDIUM |
| `src/python/toml/toml_codec.py` | 2641 | 2641 | 0 | AT CAP | MEDIUM |
| `src/python/qoi/qoi_parser.py` | 2610 | 2610 | 0 | AT CAP | MEDIUM |
| `src/python/fodp/fodp_codec.py` | 2365 | 2365 | 0 | AT CAP | LOW |
| `src/python/odt/odt_parser.py` | 2179 | 2179 | 0 | AT CAP | LOW |

## §24.7 Analytics Architecture Status

All analytics functions added in prior deepening sprints were placed in codec/parser
files (grandfathered violations in `source-structure-baseline.json` with category
`mixed_model_analytics`). This was §24.7 non-compliant but the violations were frozen
at their caps as of 2026-06-17.

**Current state of §24.7-compliant `analytics.py` files:**

| Format | `analytics.py` File | LOC | Status |
|--------|---------------------|-----|--------|
| All 23 formats | `src/python/<format>/analytics.py` | 0 (not created) | **AVAILABLE** |

No `analytics.py` files exist yet — every format has 0 LOC in this file.
These files are NOT in `source-structure-baseline.json` (no cap exists).
All 23 formats have a completely open §24.7-compliant analytics path.

## Conclusion

1. **Codec files are exhausted as targets** for new analytics function additions
2. **§24.7 mandates `analytics.py`** as the ONLY valid target for new analytics work
3. **`analytics.py` files do NOT exist** → 0 LOC → NOT capped → fully available
4. **Three formats (FODG, XCF, ZST) need decomposition** to resolve monolith blocks
5. **The `add-analytics-function` skill** targets `analytics.py` and enforces §24.7

## Recommendations

1. Execute FODG decomposition sprint (active block) per `taskcards/skill-gaps/fodg-monolith-rework-path.md`
2. Execute XCF decomposition sprint (latent block) per `taskcards/skill-gaps/xcf-monolith-rework-path.md`
3. Execute ZST decomposition sprint (latent block) per `taskcards/skill-gaps/zst-monolith-rework-path.md`
4. Use `add-analytics-function` skill for all new analytics work — targets `analytics.py`
5. Do NOT add analytics functions to any codec/parser file — RULE-AM-001 will block it
