# Format Factory — TSV

Parse and write TSV (tab-separated values) files with Format Factory.

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-07-02T16:00:10+00:00 source=package-metadata -->
```bash
pip install format-factory-tsv
```
<!-- END:README-INSTALLATION -->

## Quick Start

```python
from tsv import TsvDocument, parse_tsv_strict, write_tsv

# Class-based API (primary)
doc = TsvDocument.from_file("data.tsv")
print(doc.row_count, doc.column_count, doc.headers)

# Function API
model = parse_tsv_strict("data.tsv")
rows = model["rows"]  # list of list[str]
rows.append(["Alice", "Engineering", "95000"])
write_tsv(rows, "output.tsv", headers=model["headers"])
```

## Features

- Parse TSV files with tab delimiter
- Header-aware access (headers, rows, cell values)
- Write TSV output

## License

<!-- BEGIN:README-LICENSE generated=2026-07-02T16:00:10+00:00 source=package-metadata -->
Apache-2.0
<!-- END:README-LICENSE -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-07-02T16:00:10+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | Tab-Separated Values (TSV) |
| Track | python |
| Package | format-factory-tsv |
| Version | 0.1.0.dev0 |
| License | Apache-2.0 |
| Python | >=3.9 |
| .NET | unknown |
| Spec | IANA IANA registration (1993) |
| QName coverage | 3/3 implemented |
| Source files | 16 |
| Test files | 115 |
<!-- END:README-PACKAGE_INFO -->

## Public API

<!-- BEGIN:README-PUBLIC_API generated=2026-07-02T16:00:10+00:00 source=src-python-init -->
- `(dynamic)`
<!-- END:README-PUBLIC_API -->
