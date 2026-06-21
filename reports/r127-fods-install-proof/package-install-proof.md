# Package Install Proof — format-factory-fods-python

**Sprint:** sal-impl-001b-20260618 continuation  
**Date:** 2026-06-18  
**Skill:** package-install-proof (v1.2)

## Summary

| Package | Version | Wheel | Import | API Smoke |
|---------|---------|-------|--------|-----------|
| fods | 0.1.0.dev0 | format_factory_fods_python-0.1.0.dev0-py3-none-any.whl | import fods: OK | 9/9 tests PASS |

## Build

```
python -m build src/python/fods/ --outdir /tmp/fods-wheel/
# Successfully built format_factory_fods_python-0.1.0.dev0-py3-none-any.whl
```

## Install

```
pip install /tmp/fods-wheel/format_factory_fods_python-0.1.0.dev0-py3-none-any.whl --force-reinstall
# Successfully installed format-factory-fods-python-0.1.0.dev0
```

## Import Test

```
import fods
fods.PACKAGE_VERSION  # → '0.1.0.dev0'
fods.FORMAT_ID        # → 'fods'
```

**Result:** PASS

## API Smoke Test Results

| # | API Call | Result |
|---|----------|--------|
| 1 | `parse_fods_strict(path)` | OK — 1 sheet ['Sheet1'] |
| 2 | `workbook_stats(wb)` | OK — 1 cell |
| 3 | `workbook_to_csv(wb, 'Sheet1')` | OK — `'Hello\r\n'` |
| 4 | `workbook_set_cell_value(wb, 'Sheet1', 0, 0, 'World')` | OK — mutates in-place |
| 5 | `write_fods(wb, path)` | OK — 619 bytes |
| 6 | `workbook_add_sheet(wb, 'Summary')` | OK — sheets: ['Sheet1', 'Summary'] |
| 7 | `workbook_rename_sheet(wb, 'Summary', 'Report')` | OK — sheets: ['Sheet1', 'Report'] |
| 8 | `workbook_get_cell_value(wb, 'Sheet1', 0, 0)` | OK — `'World'` |
| 9 | `workbook_numeric_summary(wb)` | OK — 0 numeric cells |

**Overall verdict: PASS — 9/9 API smoke tests green**

## Notes

- `workbook_set_cell_value`, `workbook_add_sheet`, `workbook_rename_sheet` all mutate in-place and return `(bool, msg)` tuples.
- The installed example `edit_save_export_fods_installed.py` uses stale API (`workbook_sheet_names`, `workbook_row_values`, `workbook_col_values`, `workbook_edit_cell`) that no longer exists. This is a documentation gap (not a production blocker). Smoke test used the actual installed API.
- `workbook_to_xml` is exposed but `write_fods` is the primary serialization path.
