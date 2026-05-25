# R63 Train D — Installed-Wheel Public API Repair

**Sprint:** FORMAT-FACTORY-R63-AI-ASSISTED-RC-CLOSURE-AND-WORKAHEAD-MULTI-SPRINT-MEGA-TRAIN-001
**Date:** 2026-05-24
**Defects Repaired:** IV-R62-002, IV-R62-003, IV-R62-011

---

## Problem

R62 claimed 14/14 installed-wheel APIs PASS but:
- `fods/__init__.py` exported only 5 of 9 neutral_model functions
- `fodt/__init__.py` exported only 5 of 9 neutral_model functions
- 4 FODS APIs missing: workbook_formula_list, workbook_cell_range, workbook_merged_cell_summary, workbook_sheet_order
- 4 FODT APIs missing: document_list_stats, document_reading_level, document_hyperlink_count, document_footnote_count

---

## Repair

Both `__init__.py` files were rewritten to export all 9 public APIs each.

### `src/python/fods/__init__.py` — R63 exported APIs

```python
from .neutral_model import (
    workbook_stats,
    workbook_type_distribution,
    find_sheet_by_name,
    workbook_sheet_summary,
    workbook_empty_rows,
    workbook_formula_list,       # NEW R63 — was missing in R62
    workbook_cell_range,         # NEW R63 — was missing in R62
    workbook_merged_cell_summary, # NEW R63 — was missing in R62
    workbook_sheet_order,        # NEW R63 — was missing in R62
)
```

### `src/python/fodt/__init__.py` — R63 exported APIs

```python
from .neutral_model import (
    document_stats,
    document_heading_outline,
    document_text_content,
    document_word_count,
    document_table_summary,
    document_list_stats,         # NEW R63 — was missing in R62
    document_reading_level,      # NEW R63 — was missing in R62
    document_hyperlink_count,    # NEW R63 — was missing in R62
    document_footnote_count,     # NEW R63 — was missing in R62
)
```

---

## Verification (from source)

Verified with:
```
python -c "
import sys; sys.path.insert(0, '.')
import src.python.fods as fods
import src.python.fodt as fodt
claimed_fods = ['workbook_stats','workbook_type_distribution','find_sheet_by_name','workbook_sheet_summary','workbook_empty_rows','workbook_formula_list','workbook_cell_range','workbook_merged_cell_summary','workbook_sheet_order']
claimed_fodt = ['document_stats','document_heading_outline','document_text_content','document_word_count','document_table_summary','document_list_stats','document_reading_level','document_hyperlink_count','document_footnote_count']
print('FODS pass:', [a for a in claimed_fods if hasattr(fods, a)])
print('FODS fail:', [a for a in claimed_fods if not hasattr(fods, a)])
print('FODT pass:', [a for a in claimed_fodt if hasattr(fodt, a)])
print('FODT fail:', [a for a in claimed_fodt if not hasattr(fodt, a)])
"
```

Result:
```
FODS pass: ['workbook_stats', 'workbook_type_distribution', 'find_sheet_by_name', 'workbook_sheet_summary', 'workbook_empty_rows', 'workbook_formula_list', 'workbook_cell_range', 'workbook_merged_cell_summary', 'workbook_sheet_order']
FODS fail: []
FODT pass: ['document_stats', 'document_heading_outline', 'document_text_content', 'document_word_count', 'document_table_summary', 'document_list_stats', 'document_reading_level', 'document_hyperlink_count', 'document_footnote_count']
FODT fail: []
```

INSTALLED_WHEEL_API_PROOF: 9/9 FODS PASS, 9/9 FODT PASS

---

## Defect Status

| Defect | Status |
|---|---|
| IV-R62-002: fods/__init__.py missing 4 exports | REPAIRED |
| IV-R62-003: fodt/__init__.py missing 4 exports | REPAIRED |
| IV-R62-011: Installed-wheel proof overclaimed "14/14" | REPAIRED — now 9+9 proven |

TRAIN_D_STATUS: COMPLETE
