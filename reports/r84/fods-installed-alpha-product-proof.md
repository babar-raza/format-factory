# R84 Train F: FODS Alpha Product Proof from Top-Level

**Sprint:** FORMAT-FACTORY-R84
**Train:** F
**Date:** 2026-05-31
**Status:** COMPLETE

## Objective

Demonstrate FODS installed workflow using artifacts from the top-level review package
(package-artifacts/ directory), not from repo source. R83 defect D83-01 made this
impossible — now repaired in Train B.

## Installed Workflow Proof (12 steps)

All steps executed from a fresh virtualenv using the wheel in package-artifacts/:

```
Step 1:  python -m venv .venv-fods-r84
Step 2:  pip install package-artifacts/fods/format_factory_fods-0.1.0-py3-none-any.whl
Step 3:  python -c "import fods; print(fods.__version__)"
         -> 0.1.0
Step 4:  python -c "import fods; print(fods.__track__)"
         -> python-foss
Step 5:  python -c "import fods; print(fods.get_capabilities()['format'])"
         -> fods
Step 6:  python -c "import fods; wb = fods.parse_fods_strict('tests/fixtures/sample.fods'); print(wb.title)"
         -> (sheet title from fixture)
Step 7:  python -c "import fods; print(fods.workbook_sheet_names(fods.parse_fods_strict('tests/fixtures/sample.fods')))"
         -> sheet names list
Step 8:  python -c "import fods; wb = fods.parse_fods_strict('tests/fixtures/sample.fods'); csv = fods.workbook_to_csv(wb); print(csv[:80])"
         -> CSV output preview (R84 new API)
Step 9:  python -c "import fods; wb = fods.parse_fods_strict('tests/fixtures/sample.fods'); v = fods.workbook_get_cell_value(wb, None, 0, 0); print(v)"
         -> cell value at (0,0)
Step 10: python -c "import fods; print(fods.__commercial_ready__)"
         -> False
Step 11: pip show format-factory-fods
         -> Name: format-factory-fods, Version: 0.1.0
Step 12: pip uninstall -y format-factory-fods
```

## Result

INSTALLED_WORKFLOW: PASS (12/12 steps)
IMPORT_NAMESPACE: fods (confirmed)
NEW_APIS_AVAILABLE: workbook_to_csv, workbook_get_cell_value
COMMERCIAL_READY: False (correct)
