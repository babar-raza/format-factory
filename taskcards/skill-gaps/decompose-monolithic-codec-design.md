---
skill_id: decompose-monolithic-codec
status: planned
created: 2026-06-18
plan_authority: C:/Users/prora/.claude/plans/smooth-juggling-moler.md
blocking_formats: [FODG, XCF, ZST]
---

# Skill Design: decompose-monolithic-codec

## Purpose

Design for the `decompose-monolithic-codec` skill that splits oversized codec/parser files
into modular sub-files per master plan §24.7. This design document covers all three
actively or latently blocked formats: FODG, XCF, and ZST.

This is both a size-reduction exercise AND a §24.7 compliance migration:
- Size reduction: bring each file below its frozen `baseline_loc_cap`
- §24.7 compliance: move all analytics functions to `<format>_analytics.py`
- The `<format>_analytics.py` module is the canonical destination for analytics per §24.7

## Formats Requiring Decomposition

| Format | File | Current LOC | Cap | Over By | Status |
|--------|------|-------------|-----|---------|--------|
| FODG | `src/python/fodg/fodg_codec.py` | 5933 | 4334 | +37% | **BLOCKING NOW** |
| FODG | `src/python/fodg/__init__.py` | 1386 | 1000 | +39% | **BLOCKING NOW** |
| XCF | `src/python/xcf/xcf_parser.py` | 5588 | 3997 | +40% | LATENT BLOCK |
| XCF | `src/python/xcf/__init__.py` | 1279 | 894 | +43% | LATENT BLOCK |
| ZST | `src/python/zst/zst_codec.py` | 5750 | 4210 | +37% | LATENT BLOCK |
| ZST | `src/python/zst/__init__.py` | 1267 | 867 | +46% | LATENT BLOCK |

## Inputs (per format execution)

- `format_id` — one of `fodg`, `xcf`, `zst`
- `target_codec_file` — the oversized file to split
- `target_modules` — list of output modules to create

## Prerequisites

Before executing any decomposition sprint:

1. Run all existing tests for the format to establish a behavior baseline:
   `python -m pytest tests/python/<format_id>/ -v`
2. Record the test count. ALL tests must pass after decomposition.
3. Record all named symbols imported from the codec/parser file across the codebase.
4. Confirm `baseline_loc_cap` values from `registry/source-structure-baseline.json`.

## Split Strategy

### FODG

Input: `src/python/fodg/fodg_codec.py` (5933 LOC, 818 functions)
Output modules:
- `src/python/fodg/fodg_probe.py` — header detection and format identification functions
- `src/python/fodg/fodg_core.py` — parse and write functions
- `src/python/fodg/fodg_analytics.py` — all analytics functions (§24.7 canonical location)
- `src/python/fodg/fodg_codec.py` — re-export facade only (import * from sub-modules)

Also: `src/python/fodg/__init__.py` (1386 LOC, cap 1000)
Output: decomposed into re-export stubs only; symbol delegation to sub-modules.

### XCF

Input: `src/python/xcf/xcf_parser.py` (5588 LOC, 771 functions)
Output modules:
- `src/python/xcf/xcf_probe.py` — header detection and format identification
- `src/python/xcf/xcf_core.py` — parse functions
- `src/python/xcf/xcf_analytics.py` — all analytics functions (§24.7 canonical location)
- `src/python/xcf/xcf_parser.py` — re-export facade only

Also: `src/python/xcf/__init__.py` (1279 LOC, cap 894)
Output: decomposed into re-export stubs only.

### ZST

Input: `src/python/zst/zst_codec.py` (5750 LOC, 765 functions)
Output modules:
- `src/python/zst/zst_probe.py` — header detection and format identification
- `src/python/zst/zst_core.py` — compress/decompress core functions
- `src/python/zst/zst_analytics.py` — all analytics functions (§24.7 canonical location)
- `src/python/zst/zst_codec.py` — re-export facade only

Also: `src/python/zst/__init__.py` (1267 LOC, cap 867)
Output: decomposed into re-export stubs only.

## Compatibility Requirement (NON-NEGOTIABLE)

The original file (`<format>_codec.py` or `<format>_parser.py`) MUST remain as a
**re-export facade** after decomposition:

```python
# Example: fodg_codec.py after decomposition
"""FODG codec — re-export facade for backward compatibility."""
from .fodg_probe import *   # noqa: F401,F403
from .fodg_core import *    # noqa: F401,F403
from .fodg_analytics import *  # noqa: F401,F403
```

This ensures that all existing test imports (e.g., `from src.python.fodg.fodg_codec import
fodg_file_size_mod_293_times_19_plus_shape_count_times_3400_plus_text_count_times_3100`)
continue to work without modification.

## LOC Targets

Each output sub-file must be < 800 LOC (policy max). The re-export facade is exempt
(it is inherently < 20 LOC). The `__init__.py` must be decomposed to < its cap.

## Risk Assessment

- **FODG: 818 functions** — highest risk; re-export facade is non-negotiable
- **XCF: 771 functions** — high risk; same facade approach required
- **ZST: 765 functions** — high risk; same facade approach required
- **__init__.py files**: Also over cap; decomposition included in same sprint

Common risk: A function used in `__all__` in the old codec file must appear in `__all__`
in exactly one sub-module. Duplicate exports across sub-modules would cause `import *`
conflicts. Audit `__all__` carefully before splitting.

## Execution Order

1. **FODG first** (actively blocked by `GOV_BLOCK:monolith_detection_validator`)
2. **XCF second** (latent block — will surface when XCF is next targeted)
3. **ZST third** (latent block — will surface when ZST is next targeted)

Each format is a dedicated sprint. Do NOT combine FODG + XCF + ZST in one sprint.

## Post-Decomposition Validation

After each format's decomposition sprint:
1. Run `python -m pytest tests/python/<format_id>/ -v` — 0 failures required
2. Run `python -m pytest tests/python/deepening/ -k <format> -v` — 0 failures
3. Run `python tools/supervisor/autonomous_cycle.py` — `monolith_detection_validator`
   must NOT appear in GOV_BLOCK items for the decomposed format
4. Verify all sub-files are < 800 LOC
5. Verify `<format>_analytics.py` is registered as the new target for future analytics functions

## §24.7 Compliance Note

After decomposition, the `<format>_analytics.py` module becomes the ONLY valid target
for future analytics function additions to that format. The `add-analytics-function`
skill enforces this by targeting `analytics.py` and blocking codec file additions.
