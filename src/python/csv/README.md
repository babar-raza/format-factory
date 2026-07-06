# Format Factory — CSV

Parse, query, and write CSV (comma-separated values) files with Format Factory.

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-07-04T11:41:36+00:00 source=package-metadata -->
```bash
pip install format-factory-csv
```
<!-- END:README-INSTALLATION -->

## Quick Start

```python
from csv_format import CsvDocument, parse_csv_strict, write_csv_to_file

# Class-based API (primary)
doc = CsvDocument.from_file("data.csv")
print(doc.row_count, doc.column_count, doc.headers)

# Function API
model = parse_csv_strict("data.csv")
write_csv_to_file(model["rows"], "output.csv", headers=model["headers"])
```

## Features

- Parse CSV files with delimiter detection
- Query rows, columns, and cell values
- Header-aware access (`get_column_names()`, `get_cell_value()`)
- Write CSV output

## Known Issue: Package Name Shadows Python stdlib `csv`

The package directory is named `csv`, which shadows Python's built-in `csv` module
in certain import configurations. This was established early in the project and
renaming it would break hundreds of existing imports, tests, and oracle cases.

The installed package name is `format-factory-csv` and the importable module is
`csv_format` (not `csv`), which avoids the stdlib conflict at runtime. Do not
attempt to import using `from csv import ...` — Python will resolve to the stdlib.

**Correct usage:**
```python
from csv_format import CsvDocument, parse_csv_strict, write_csv_to_file
```

**Do not rename** the `src/python/csv/` directory without a major version bump and
a coordinated import migration across all tests, oracle cases, and downstream consumers.

## License

<!-- BEGIN:README-LICENSE generated=2026-07-04T11:41:36+00:00 source=package-metadata -->
Apache-2.0
<!-- END:README-LICENSE -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-07-04T11:41:36+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | Comma-Separated Values (CSV) |
| Track | python |
| Package | format-factory-csv |
| Version | 0.1.0.dev0 |
| License | Apache-2.0 |
| Python | >=3.9 |
| .NET | unknown |
| Spec | IETF (RFC 4180) RFC 4180 (2005) |
| QName coverage | 3/3 implemented |
| Source files | 19 |
| Test files | 62 |
<!-- END:README-PACKAGE_INFO -->

## Public API

<!-- BEGIN:README-PUBLIC_API generated=2026-07-04T11:41:36+00:00 source=src-python-init -->
- `(dynamic)`
<!-- END:README-PUBLIC_API -->
