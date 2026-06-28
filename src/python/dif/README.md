# Format Factory — DIF

Parse and write DIF (Data Interchange Format) files with Format Factory.

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-06-28T08:14:24+00:00 source=package-metadata -->
```bash
pip install format-factory-dif
```
<!-- END:README-INSTALLATION -->

## Quick Start

```python
from dif import DifDocument, load_dif, write_dif

# Class-based API (primary)
doc = DifDocument.from_file("spreadsheet.dif")
print(doc.spec_qname, doc.rows, doc.vectors, doc.tuples)

# Function API
model = load_dif("spreadsheet.dif")
write_dif(model, "output.dif")
```

## Features

- Parse DIF files (vectors/tuples format)
- Access rows as `DifCell` objects
- Write modified DIF output

## License

<!-- BEGIN:README-LICENSE generated=2026-06-28T08:14:24+00:00 source=package-metadata -->
Apache-2.0
<!-- END:README-LICENSE -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-06-28T08:14:24+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | Data Interchange Format |
| Track | python |
| Package | format-factory-dif |
| Version | 0.1.0 |
| License | Apache-2.0 |
| Python | >=3.9 |
| .NET | unknown |
| Spec | Software Arts (Bob Frankston, 1981) DIF Technical Specification (1981, public domain) |
| QName coverage | 6/6 implemented |
| Source files | 17 |
| Test files | 89 |
<!-- END:README-PACKAGE_INFO -->

## Public API

<!-- BEGIN:README-PUBLIC_API generated=2026-06-28T08:14:24+00:00 source=src-python-init -->
- `(dynamic)`
<!-- END:README-PUBLIC_API -->
