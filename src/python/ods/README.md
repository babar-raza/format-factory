# Format Factory — ODS

Parse and write ODS (OpenDocument Spreadsheet) files with Format Factory.

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-07-02T16:00:08+00:00 source=package-metadata -->
```bash
pip install format-factory-ods
```
<!-- END:README-INSTALLATION -->

## Quick Start

```python
from ods import OdsDocument, parse_ods, write_ods

# Class-based API (primary)
doc = OdsDocument.from_file("spreadsheet.ods")
print(doc.sheet_count, doc.sheets[0].name)

# Edit and save
write_ods(doc.to_dict(), "output.ods")
```

## Features

- Parse ODS files (ODF 1.3 spreadsheet format)
- Access sheets, rows, and cells
- Write ODS output

## License

<!-- BEGIN:README-LICENSE generated=2026-07-02T16:00:08+00:00 source=package-metadata -->
Apache-2.0
<!-- END:README-LICENSE -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-07-02T16:00:08+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | OpenDocument Spreadsheet |
| Track | python |
| Package | format-factory-ods |
| Version | 0.1.0 |
| License | Apache-2.0 |
| Python | >=3.9 |
| .NET | unknown |
| Spec | OASIS Open Document Format TC ODF 1.3 (ISO/IEC 26300-3:2021) |
| QName coverage | 4/4 implemented |
| Source files | 22 |
| Test files | 113 |
<!-- END:README-PACKAGE_INFO -->

## Public API

<!-- BEGIN:README-PUBLIC_API generated=2026-07-02T16:00:08+00:00 source=src-python-init -->
- `(dynamic)`
<!-- END:README-PUBLIC_API -->
