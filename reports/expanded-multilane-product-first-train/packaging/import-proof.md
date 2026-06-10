# Import Proof — Sprint EXPANDED-MULTI-LANE-001

## ABW Package

Package installed (egg-info present). Import path: `from abw.abw_codec import ...`

Verified by: `test_r123_abw_csv_export.py::TestExportToCsv::test_package_import` — PASS

```python
import abw
assert hasattr(abw, "export_to_csv")   # PASS
assert "export_to_csv" in abw.__all__  # PASS
```

## Gnumeric Package

Package installed (egg-info present). Import path: `from gnumeric.gnumeric_codec import ...`

Verified by: `test_r123_gnumeric_cell_accessor.py::TestGetCellValue::test_package_import` — PASS

```python
import gnumeric
assert hasattr(gnumeric, "get_cell_value")    # PASS
assert "get_cell_value" in gnumeric.__all__   # PASS
```

## NDJSON Module

NOT pip-installed. Import via repo path:
```python
sys.path.insert(0, str(_REPO))
from src.python.ndjson.ndjson_codec import append_record, filter_records
```

Verified by: `test_r123_ndjson_append_filter.py::TestFilterRecords::test_package_import` — PASS

## Verdict
All 3 touched formats importable. New functions accessible from package API.
