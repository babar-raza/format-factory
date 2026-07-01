# Format Factory — SYLK

Parse and write SYLK (Symbolic Link Format) spreadsheet files with Format Factory.

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-07-01T23:47:31+00:00 source=package-metadata -->
```bash
pip install format-factory-sylk
```
<!-- END:README-INSTALLATION -->

## Quick Start

```python
from sylk import SylkDocument, load_sylk, set_cell_value

# Class-based API (primary)
doc = SylkDocument.from_file("spreadsheet.slk")
print(doc.rows, doc.cells)

# File-based edit API
set_cell_value("input.slk", "output.slk", row=1, col=1, value="Updated")
```

## Features

- Parse SYLK (.slk) files
- Access cell data by row/column coordinates
- File-based cell editing and write
- Export to CSV

## License

<!-- BEGIN:README-LICENSE generated=2026-07-01T23:47:31+00:00 source=package-metadata -->
Apache-2.0
<!-- END:README-LICENSE -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-07-01T23:47:31+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | Symbolic Link (SYLK) |
| Track | python |
| Package | format-factory-sylk |
| Version | 0.1.0 |
| License | Apache-2.0 |
| Python | >=3.9 |
| .NET | unknown |
| Spec | Microsoft (1986) SYLK Format (1986) |
| QName coverage | 4/4 implemented |
| Source files | 17 |
| Test files | 98 |
<!-- END:README-PACKAGE_INFO -->

## Public API

<!-- BEGIN:README-PUBLIC_API generated=2026-07-01T23:47:31+00:00 source=src-python-init -->
- `(dynamic)`
<!-- END:README-PUBLIC_API -->
