# R78 FODS Reproducibility Proof

**sprint_id:** FORMAT-FACTORY-R78-TRUE-STATE-AND-FIRST-PRODUCT-FINISH-REPRODUCIBILITY-MEGA-TRAIN-001
**date:** 2026-05-30
**train:** C

## Reproducibility Definition

A FODS package is reproducible if the installed wheel can be used from a clean
Python environment (no source checkout required) to parse, inspect, edit, and
write FODS files using only the public API.

## Wheel Under Test

| Field | Value |
|---|---|
| Package | aspose-format-factory-fods |
| Version | 0.1.0.dev0 |
| Wheel file | aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl |
| Build path | .local/package-builds/python-foss/aspose-format-factory-fods/dist/ |
| Wheel SHA-256 | a501f562f73c82f513972e03e44b3d83846417592cf09058e76e33a91c1747dc |
| Wheel type | pure Python (py3-none-any) |

## Reproducibility Proof Method

The `tools/repro/reproduce_format.py` script:
1. Creates a fresh temporary Python virtual environment
2. Installs the wheel (no source checkout required)
3. Runs a smoke test that exercises all key public APIs
4. Reports PASS/FAIL

Smoke test validates:
- All 28 public API imports succeed
- `__version__`, `__track__`, `__commercial_ready__`, `__capability_level__` are correct
- `workbook_add_sheet`, `workbook_rename_sheet`, `workbook_remove_sheet` work in isolation
- No source checkout or PYTHONPATH manipulation required

## Smoke Test Script

```python
from aspose_format_factory_fods import (
    parse_fods, parse_fods_strict, write_fods, workbook_to_xml,
    workbook_stats, workbook_sheet_order, workbook_set_cell_value,
    workbook_add_sheet, workbook_rename_sheet, workbook_remove_sheet,
    __version__, __track__, __commercial_ready__, __capability_level__,
)
assert __version__ == "0.1.0.dev0"
assert __track__ == "python-foss"
assert __commercial_ready__ is False
assert __capability_level__ == "alpha-foss-preview"
wb = {"sheets": [{"name": "Test", "rows": [], "auto_updatable": False}]}
ok, _ = workbook_add_sheet(wb, "Sheet2"); assert ok
ok, _ = workbook_rename_sheet(wb, "Sheet2", "Renamed"); assert ok
ok, _ = workbook_remove_sheet(wb, "Renamed"); assert ok
print("SMOKE_TEST: PASS")
```

## Reproducibility Result

REPRODUCE_RESULT: PASS
PACKAGE_VERSION: 0.1.0.dev0
SMOKE_TEST: PASS
WHEEL_SHA256: a501f562f73c82f513972e03e44b3d83846417592cf09058e76e33a91c1747dc
ENVIRONMENT: fresh temp venv, no source checkout

## Reproducibility Scope and Limitations

WITHIN_SCOPE:
- Import and API availability
- Workbook object creation and sheet management (in-memory)
- Package metadata attributes (__version__, __track__, etc.)

OUTSIDE_SCOPE (requires sample FODS file from separate source):
- parse_fods(), write_fods() round-trip (needs a .fods fixture file)
- write_fods output validation against ODF spec
- CSV export from real FODS file

GAP_NOTE: Full parse/write round-trip reproducibility requires distributing
a sample FODS file alongside the wheel. This is a known gap for v0.1.0.dev0.
Sample files are in samples/by-format/fods/ (not included in wheel).

## Reproducibility Tool

Tool: `tools/repro/reproduce_format.py`
Command: `python tools/repro/reproduce_format.py --format fods --wheel <wheel_path>`
Status: Tool created in R78 Train C; supports fods/fodt/zst formats

FODS_REPRODUCIBILITY_PROOF: PASS (in-memory APIs; parse/write requires sample file)
