# Python Gap Matrix — TC-REVIEW-001
Generated: 2026-07-04 | Authority: plans/.claude/drifting-wobbling-honey.md

| Format | spec/ | Compat/ | models→spec | Compat behavioral | analytics sep | LOC≤800 | Status |
|--------|-------|---------|-------------|-------------------|---------------|---------|--------|
| fods | PASS | PASS | FAIL | FAIL | FAIL | FAIL(1103 LOC fods_analytics.py) | CRITICAL |
| fodt | PASS | PASS | FAIL | FAIL | WARN | FAIL(1009 LOC text_document.py) | CRITICAL |
| csv | PASS | PASS | FAIL | PARTIAL | PASS | FAIL(1050 LOC tabular_document.py) | NEEDS_WORK |
| tsv | PASS | PASS | FAIL | PARTIAL | WARN | FAIL(851 LOC tabular_document.py) | NEEDS_WORK |
| abw | PASS | PASS | FAIL | PASS | FAIL | FAIL(1051 LOC word_document.py) | CRITICAL |
| dif | PASS | PASS | FAIL | PARTIAL | WARN | FAIL(995 LOC interchange_document.py) | NEEDS_WORK |
| fodg | PASS | PASS | FAIL | PARTIAL | FAIL | FAIL(826 LOC fodg_codec.py) | CRITICAL |
| fodp | PASS | PASS | FAIL | PARTIAL | FAIL | PASS | NEEDS_WORK |
| gnumeric | PASS | PASS | FAIL | PARTIAL | FAIL | FAIL(913 LOC gnumeric_analytics.py) | CRITICAL |
| ndjson | PASS | PASS | FAIL | PARTIAL | FAIL | FAIL(926 LOC json_stream.py) | CRITICAL |
| ods | PASS | PASS | FAIL | PARTIAL | FAIL | FAIL(1000 LOC ods_analytics.py) | CRITICAL |
| odt | PASS | PASS | FAIL | PASS | WARN | PASS | NEEDS_WORK |
| pbm | PASS | PASS | FAIL | PARTIAL | WARN | PASS | NEEDS_WORK |
| pgm | PASS | PASS | FAIL | PARTIAL | WARN | PASS | NEEDS_WORK |
| ppm | PASS | PASS | FAIL | PARTIAL | WARN | PASS | NEEDS_WORK |
| qoi | PASS | PASS | FAIL | PARTIAL | WARN | PASS | NEEDS_WORK |
| sylk | PASS | PASS | FAIL | PARTIAL | PASS | FAIL(894 LOC sylk_analytics.py) | NEEDS_WORK |
| toml | PASS | PASS | FAIL | PARTIAL | FAIL | PASS | NEEDS_WORK |
| xcf | PASS | PASS | FAIL | PARTIAL | WARN | FAIL(898 LOC xcf_image_metrics.py) | NEEDS_WORK |
| zst | PASS | PASS | FAIL | PARTIAL | FAIL | FAIL(1073 LOC zst_codec.py) | CRITICAL |

## Summary
- Total formats: 20
- CLEAN (no failures): 0 — 
- NEEDS_WORK: 12
- CRITICAL: 8

## Key Findings
1. `models→spec` FAIL: Most formats wrap neutral dicts — MINOR_REALIGNMENT target for Wave 1
2. `Compat behavioral` PARTIAL/FAIL: Compat/ facades are architecture markers only
3. `LOC≤800` violations: see healing targets in TC-HEAL-PY-001/002

## Acceptance: PASS — 20 formats × 6 checks complete