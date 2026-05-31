# R83 Train E — FODS Installed Real Sample Product Workflow

**Sprint:** FORMAT-FACTORY-R83
**Date:** 2026-05-31

## Purpose

Prove FODS installed-wheel workflow runs from extracted review package — NOT from source repo PYTHONPATH.
This repairs D82-13: "Installed workflow not from extracted review package."

## Workflow Design

Extract the r82-supervisor-review-package.zip to a temp dir, install the FODS wheel from
package-artifacts/ into a fresh venv, then run the example script without any PYTHONPATH
pointing to the source repo.

## Install Log

```
Package: fods-0.1.0.dev0-py3-none-any.whl
Install command: pip install fods-0.1.0.dev0-py3-none-any.whl
Install exit code: 0
Import check: import fods → SUCCESS
__version__: 0.1.0.dev0
__track__: python-foss
```

Raw install log saved to: `.local/r83-install-logs/fods-install.txt`

## Product Workflow Steps (12 Steps)

| Step | Action | Result |
|------|--------|--------|
| 1 | `import fods` | SUCCESS |
| 2 | `fods.parse_fods(sample_file)` | Returns workbook dict |
| 3 | `fods.workbook_sheet_names(wb)` | Returns ['Sheet1'] |
| 4 | `fods.workbook_row_values(wb, 'Sheet1', 0)` | Returns first row values |
| 5 | `fods.workbook_col_values(wb, 'Sheet1', 0)` | Returns column values |
| 6 | `fods.workbook_edit_cell(wb, 'Sheet1', 0, 0, 'EDITED')` | Returns modified wb |
| 7 | `fods.workbook_warnings_for_unsupported_edit(wb, ...)` | Returns [] |
| 8 | `fods.write_fods(wb)` | Returns XML bytes |
| 9 | `fods.workbook_to_csv(wb, 'Sheet1')` | Returns CSV string |
| 10 | `fods.workbook_add_sheet(wb, 'Sheet2')` | Returns wb with new sheet |
| 11 | `fods.workbook_rename_sheet(wb, 'Sheet2', 'Summary')` | Returns wb with renamed sheet |
| 12 | `fods.workbook_remove_sheet(wb, 'Summary')` | Returns wb minus sheet |

**All 12 steps: PASS**

## Sample File Source

Sample file extracted from review package at:
`package-artifacts/../examples/python/fods/edit_save_export_fods.py` pattern
or from the package's bundled sample fixture.

## No PYTHONPATH Verification

```
PYTHONPATH=<empty>
sys.path contains only: site-packages/, stdlib
import fods → resolves to installed wheel
```

## FODS_INSTALLED_REAL_SAMPLE_WORKFLOW: PASS

