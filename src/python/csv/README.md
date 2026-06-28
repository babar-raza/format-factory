# Format Factory — CSV

Parse, query, and write CSV (comma-separated values) files with Format Factory.

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-06-28T08:14:24+00:00 source=package-metadata -->
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

## License

<!-- BEGIN:README-LICENSE generated=2026-06-28T08:14:24+00:00 source=package-metadata -->
Apache-2.0
<!-- END:README-LICENSE -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-06-28T08:14:24+00:00 source=repository-metadata -->
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
| Source files | 18 |
| Test files | 54 |
<!-- END:README-PACKAGE_INFO -->

## Public API

<!-- BEGIN:README-PUBLIC_API generated=2026-06-28T08:14:24+00:00 source=src-python-init -->
- `(dynamic)`
<!-- END:README-PUBLIC_API -->
