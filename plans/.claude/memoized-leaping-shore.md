# Plan: Fix Import Failures — REVISED against current system state
# Status: v3 — re-assessed 2026-07-03, verified against HEAD

---

## A. Current-State Reassessment

**What changed since the previous plan was written:**
All 18 analytics functions were implemented in source (likely in a prior sprint). The plan's implementation taskcards TC-001 through TC-009 are **already complete**. The code now lives in dedicated submodules (not in the parser files the plan originally targeted).

**Evidence of prior completion:**

| Old TC | Plan target | Actual location | Status |
|--------|-------------|-----------------|--------|
| TC-001 PBM | `pbm_parser.py` | `src/python/pbm/bitmap_image.py:555,568` | DONE ✅ |
| TC-002 PGM | `pgm_parser.py` | `src/python/pgm/grayscale_image.py:629,641` | DONE ✅ |
| TC-003 PPM | `ppm_parser.py` | `src/python/ppm/color_image.py:614,620` | DONE ✅ |
| TC-004 NDJSON | `ndjson_codec.py` | `src/python/ndjson/ndjson_record_stats.py:591,611` | DONE in source — **NOT wired** ❌ |
| TC-005 SYLK | `sylk_parser.py` | `src/python/sylk/spreadsheet_document.py:893,899` | DONE ✅ |
| TC-006 DIF | `dif_parser.py` | `src/python/dif/dif_stats.py:250,262` | DONE ✅ |
| TC-007 FODT | `fodt_document_query.py` | `src/python/fodt/text_document.py:995,1007` | DONE ✅ |
| TC-008 FODP | `fodp_codec.py` | `src/python/fodp/presentation_document.py:633,646` | DONE ✅ |
| TC-009 ZST | `zst_codec.py` | `src/python/zst/zst_codec.py:1023` + in `__all__` line 80 | DONE ✅ |

---

## B. Item-by-Item Status

### TC-001 PBM — `pbm_column_transition_count`, `pbm_center_black_count`
**Status: PARTIALLY DONE**
- Source: ✅ both functions in `bitmap_image.py:555,568`
- `src/python/pbm/__init__.py` has `from .bitmap_image import *` (line 9) → importable via `src.python.pbm` ✅
- Site-packages: ❌ `bitmap_image.py` in `.venv/Lib/site-packages/pbm/` does NOT contain these functions (stale copy from before they were added)
- **Deepening tests use `from src.python.pbm import ...` → imports source directly → tests SHOULD PASS now**
- Site-packages gap still matters for any code importing from the installed `pbm` package

### TC-002 PGM — `pgm_pixel_median`, `pgm_edge_pixel_mean`
**Status: PARTIALLY DONE**
- Source: ✅ both in `grayscale_image.py:629,641`
- `src/python/pgm/__init__.py` has `from .grayscale_image import *` (line 9) ✅
- Site-packages: ❌ `grayscale_image.py` in site-packages is stale (Grep: No matches found)
- Deepening tests use source import path → SHOULD PASS

### TC-003 PPM — `ppm_pixel_value_sum`, `ppm_channel_contrast_sum`
**Status: PARTIALLY DONE**
- Source: ✅ both in `color_image.py:614,620`
- `src/python/ppm/__init__.py` has `from .color_image import *` (line 10) ✅
- Site-packages: ❌ `color_image.py` in site-packages is stale
- Deepening tests use source import path → SHOULD PASS

### TC-004 NDJSON — `ndjson_max_key_depth`, `ndjson_field_value_mean`
**Status: INCOMPLETE — critical wiring gap**
- Source: ✅ both in `ndjson_record_stats.py:591,611`
- `src/python/ndjson/__init__.py`: imports only from `ndjson_codec` — does **NOT** import from `ndjson_record_stats` ❌
- Result: `from src.python.ndjson import ndjson_max_key_depth` → **ImportError** (test_r364 still fails)
- NDJSON is editable (via `__editable__.format_factory_ndjson-0.1.0.dev0.pth`) → one-line fix needed in `__init__.py`

### TC-005 SYLK — `sylk_cell_text_length_sum`, `sylk_numeric_value_sum`
**Status: PARTIALLY DONE**
- Source: ✅ both in `spreadsheet_document.py:893,899`
- `src/python/sylk/__init__.py` has `from .spreadsheet_document import *` (line 10) ✅
- Site-packages: ❌ `spreadsheet_document.py` in site-packages is stale
- Deepening tests use source import path → SHOULD PASS

### TC-006 DIF — `dif_string_cell_total_length`, `dif_numeric_value_total`
**Status: PARTIALLY DONE**
- Source: ✅ both in `dif_stats.py:250,262`
- `src/python/dif/__init__.py` has `from .dif_stats import *` (line 10) ✅
- Site-packages: ❌ `dif_stats.py` in site-packages is stale
- Deepening tests use source import path → SHOULD PASS

### TC-007 FODT — `fodt_word_count_total`, `fodt_paragraph_count_total`
**Status: DONE**
- Source: ✅ both in `text_document.py:995,1007`
- `src/python/fodt/__init__.py` has `from .text_document import *` (line 15) ✅
- FODT is editable (`__editable__.format_factory_fodt_python-0.1.0.dev0.pth`) → source IS the installed package ✅

### TC-008 FODP — `fodp_text_to_shape_ratio`, `fodp_slide_count_squared`
**Status: DONE**
- Source: ✅ both in `presentation_document.py:633,646`
- `src/python/fodp/__init__.py` has `from .presentation_document import *` (line 21) ✅
- FODP is editable (`__editable__.format_factory_fodp-0.1.0.pth`) ✅

### TC-009 ZST — `get_compression_summary`
**Status: DONE**
- Source: ✅ in `zst_codec.py:1023`
- `src/python/zst/__init__.py`: in explicit `__all__` at line 80 + explicit import at line 86 ✅
- ZST is editable (`__editable__.format_factory_zst-0.1.0.dev0.pth`) ✅

### TC-010 Site-packages sync — new analytics modules
**Status: PARTIALLY DONE**
- PBM `models.py`: ✅ site-packages has `is_ascii`, `long_edge`, `short_edge` (verified at lines 111, 116, 121)
- CSV `models.py`: ✅ site-packages has `is_large`, `is_tiny`, `has_uniform_rows` (verified at lines 138, 143, 148)
- PBM `bitmap_image.py`: ❌ new functions not in site-packages
- PGM `grayscale_image.py`: ❌ stale in site-packages
- PPM `color_image.py`: ❌ stale in site-packages
- SYLK `spreadsheet_document.py`: ❌ stale in site-packages
- DIF `dif_stats.py`: ❌ stale in site-packages
- PGM/PPM/TSV/XCF/ODS/ODT/FODG/QOI `models.py`: status unverified

### TC-011 Run tests
**Status: NOT RUN**

### New property tests (r1233–r1246) import pattern
**Evidence from reading test files:**
- `test_r1237_pbm_encoding_dimension_properties.py`: imports `from pbm.models import PbmDocument` (installed package) → site-packages/pbm/models.py is already synced ✅
- `test_r1233_csv_scale_properties.py`: uses `importlib` to load `src/python/csv/models.py` directly → bypasses site-packages entirely ✅

---

## C. Remaining Problems

### Problem 1 — NDJSON `__init__.py` wiring gap (CRITICAL)
**Root cause:** `ndjson_record_stats.py` was added to source but never wired into `ndjson/__init__.py`. The module imports only from `ndjson_codec`.
**Impact:** `from src.python.ndjson import ndjson_max_key_depth` and `ndjson_field_value_mean` → `ImportError` → `test_r364` still fails at these two imports.
**Fix:** One line added to `src/python/ndjson/__init__.py`.

### Problem 2 — Site-packages stale for 5 non-editable formats (analytics modules)
**Root cause:** Non-editable packages are wheel snapshots. New functions added to `bitmap_image.py`, `grayscale_image.py`, `color_image.py`, `spreadsheet_document.py`, `dif_stats.py` since last install date are not reflected.
**Impact:** Any code importing from installed `pbm`, `pgm`, `ppm`, `sylk`, `dif` packages will NOT see the new functions. Deepening tests avoid this by using `src.python.*` imports, but installed-package imports would fail.
**Fix:** Copy 5 updated submodule files to site-packages.

### Problem 3 — models.py sync unknown for PGM, PPM, TSV, XCF, ODS, ODT, FODG, QOI
**Root cause:** Not verified. PBM and CSV confirmed synced. Others may or may not be.
**Impact:** New property tests for those formats may fail if they import from installed packages and models.py is stale.
**Fix:** Verify and sync if needed.

---

## D. Revised Plan (current reality only)

### TC-NEW-001 — Wire NDJSON `__init__.py`
**Status:** ready
**Priority:** CRITICAL — blocks test_r364
**File:** `src/python/ndjson/__init__.py`
**Change:** Add one import line after the existing `from .ndjson_codec import *` line:
```python
from .ndjson_record_stats import *  # noqa: F401, F403
```
**Why this works:** NDJSON is editable (`.pth` file points to source) → change is immediately live. Dynamic `__all__` in `__init__.py` (line 31-36) will include all public names from `ndjson_record_stats`.

**Validation:**
```bash
.venv/Scripts/python -c "from src.python.ndjson import ndjson_max_key_depth, ndjson_field_value_mean; print('OK')"
```

---

### TC-NEW-002 — Sync analytics modules to non-editable site-packages
**Status:** ready
**Priority:** HIGH — needed for any installed-package consumer; good hygiene even if deepening tests avoid it
**Prerequisites:** TC-NEW-001 (independent but should be done together)

```bash
SITE=".venv/Lib/site-packages"

# Backup first
cp "$SITE/pbm/bitmap_image.py"           "$SITE/pbm/bitmap_image.py.bak"    2>/dev/null || true
cp "$SITE/pgm/grayscale_image.py"        "$SITE/pgm/grayscale_image.py.bak" 2>/dev/null || true
cp "$SITE/ppm/color_image.py"            "$SITE/ppm/color_image.py.bak"     2>/dev/null || true
cp "$SITE/sylk/spreadsheet_document.py" "$SITE/sylk/spreadsheet_document.py.bak" 2>/dev/null || true
cp "$SITE/dif/dif_stats.py"             "$SITE/dif/dif_stats.py.bak"       2>/dev/null || true

# Sync analytics submodules
cp src/python/pbm/bitmap_image.py          "$SITE/pbm/bitmap_image.py"
cp src/python/pgm/grayscale_image.py       "$SITE/pgm/grayscale_image.py"
cp src/python/ppm/color_image.py           "$SITE/ppm/color_image.py"
cp src/python/sylk/spreadsheet_document.py "$SITE/sylk/spreadsheet_document.py"
cp src/python/dif/dif_stats.py             "$SITE/dif/dif_stats.py"

# Invalidate bytecode caches for synced packages
for fmt in pbm pgm ppm sylk dif; do
  find "$SITE/$fmt/__pycache__" -name "*.pyc" -delete 2>/dev/null || true
done
```

**Validation:**
```bash
.venv/Scripts/python -c "
from pbm.bitmap_image import pbm_column_transition_count
from pgm.grayscale_image import pgm_pixel_median
from ppm.color_image import ppm_pixel_value_sum
from sylk.spreadsheet_document import sylk_cell_text_length_sum
from dif.dif_stats import dif_string_cell_total_length
print('site-packages sync OK')
"
```

**Rollback:** `for f in $(find .venv/Lib/site-packages -name "*.bak"); do cp "$f" "${f%.bak}"; done`

---

### TC-NEW-003 — Verify and sync models.py for remaining non-editable formats
**Status:** ready
**Priority:** MEDIUM — blocks new property tests r1234–r1246 if any import from installed packages

First check if properties already synced:
```bash
SITE=".venv/Lib/site-packages"
python -c "
from pgm.models import PgmDocument
from ppm.models import PpmDocument
# Check for recently added properties
checks = [
    ('pgm long_edge', hasattr(PgmDocument, 'long_edge')),
    ('pgm short_edge', hasattr(PgmDocument, 'short_edge')),
    ('ppm long_edge', hasattr(PpmDocument, 'long_edge')),
]
for name, ok in checks:
    print(f'  {name}: {\"OK\" if ok else \"MISSING\"}')
" 2>&1
```

If any show MISSING, sync the models.py for affected formats:
```bash
# Only sync formats where properties are missing
for fmt in pgm ppm tsv xcf ods odt fodg qoi; do
  cp "src/python/$fmt/models.py" "$SITE/$fmt/models.py"
  find "$SITE/$fmt/__pycache__" -name "*.pyc" -delete 2>/dev/null || true
done
```

---

### TC-NEW-004 — Run all previously-failing tests and verify
**Status:** backlog
**Prerequisites:** TC-NEW-001, TC-NEW-002, TC-NEW-003

```bash
PYTEST=".venv/Scripts/pytest"

# Primary failing tests
$PYTEST tests/python/deepening/test_r363_pbm_pgm_fodp_fodt_deepening.py -v
$PYTEST tests/python/deepening/test_r364_ppm_ndjson_sylk_dif_deepening.py -v
$PYTEST tests/python/zst/test_r267_zst_compression_summary.py -v

# New property tests
$PYTEST \
  tests/python/csv/test_r1233_csv_scale_properties.py \
  tests/python/tsv/test_r1234_tsv_scale_properties.py \
  tests/python/xcf/test_r1235_xcf_pixel_size_properties.py \
  tests/python/ods/test_r1236_ods_sheet_scale_properties.py \
  tests/python/pbm/test_r1237_pbm_encoding_dimension_properties.py \
  tests/python/pgm/test_r1238_pgm_encoding_size_properties.py \
  tests/python/ppm/test_r1239_ppm_encoding_size_properties.py \
  tests/python/fodt/test_r1240_fodt_structure_classification_properties.py \
  tests/python/ndjson/test_r1241_ndjson_object_shape_properties.py \
  tests/python/toml/test_r1242_toml_size_value_type_properties.py \
  tests/python/qoi/test_r1243_qoi_edge_channel_properties.py \
  tests/python/odt/test_r1244_odt_scale_content_balance_properties.py \
  tests/python/fods/test_r1245_fods_workbook_scale_properties.py \
  tests/python/fodg/test_r1246_fodg_density_complexity_properties.py \
  -v

# Regression check
$PYTEST tests/python/ -x -q 2>&1 | tail -20
```

**Acceptance criteria:**
- test_r363: all 8 functions import and pass
- test_r364: all 8 functions import and pass (previously `ndjson_max_key_depth` was ImportError)
- test_r267: `get_compression_summary` imports and passes
- r1233–r1246: all pass (models properties found)
- Regression: no new failures

---

## Files to Modify

| Action | File | Change |
|--------|------|--------|
| MODIFY | `src/python/ndjson/__init__.py` | Add `from .ndjson_record_stats import *` after line 13 |
| SYNC | `.venv/Lib/site-packages/pbm/bitmap_image.py` | Copy from source |
| SYNC | `.venv/Lib/site-packages/pgm/grayscale_image.py` | Copy from source |
| SYNC | `.venv/Lib/site-packages/ppm/color_image.py` | Copy from source |
| SYNC | `.venv/Lib/site-packages/sylk/spreadsheet_document.py` | Copy from source |
| SYNC | `.venv/Lib/site-packages/dif/dif_stats.py` | Copy from source |
| SYNC (conditional) | `.venv/Lib/site-packages/{pgm,ppm,tsv,xcf,ods,odt,fodg,qoi}/models.py` | Only if TC-NEW-003 check shows MISSING |

**No new source files created. No `_analytics.py` files. No `__init__.py` changes except NDJSON.**

---

## Discarded Work (from old plan)

| Old TC | Reason discarded |
|--------|-----------------|
| TC-001 through TC-009 (implement functions) | All functions already exist in source |
| TC-010 full sync (all formats) | Scoped down to only the 5 formats with stale analytics submodules |
| All `__init__.py` updates except NDJSON | Already correctly wired via star imports |
| FODP explicit `__all__` update | `presentation_document.py` is already star-imported; functions are exported |
| ZST `__init__.py` update | Already in `__all__` at line 80 and explicitly imported at line 86 |
| Pre-implementation checks for `Path` / `Any` imports | Implementation already done |

---

## Execution Order

TC-NEW-001 → TC-NEW-002 → TC-NEW-003 → TC-NEW-004

TC-NEW-001 is the only code change. All others are file copies or test runs.

---

## Taskcard Status Summary

| Taskcard | Status |
|----------|--------|
| TC-NEW-001 | CLOSED |
| TC-NEW-002 | CLOSED |
| TC-NEW-003 | CLOSED |
| TC-NEW-004 | CLOSED |


<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-07-02T20:55:40.429356+00:00"
  locked_by: "0ce45942c388"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
