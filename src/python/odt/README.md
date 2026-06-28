# Format Factory — ODT

Parse and write ODT (OpenDocument Text) files with Format Factory.

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-06-28T08:14:26+00:00 source=package-metadata -->
```bash
pip install format-factory-odt
```
<!-- END:README-INSTALLATION -->

## Quick Start

```python
from odt import OdtDocument, parse_odt, write_odt, odt_from_text

# Class-based API (primary)
doc = OdtDocument.from_file("document.odt")
print(doc.paragraph_count, doc.paragraphs[0])

# Create a new document from text
odt_from_text("Hello, Format Factory!", "output.odt")

# Roundtrip
model = parse_odt("document.odt")
write_odt(model["paragraphs"], "copy.odt")
```

## Features

- Parse ODT files (ODF 1.3 text document format)
- Access paragraphs and document structure
- Write ODT output

## License

<!-- BEGIN:README-LICENSE generated=2026-06-28T08:14:26+00:00 source=package-metadata -->
Apache-2.0
<!-- END:README-LICENSE -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-06-28T08:14:26+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | OpenDocument Text |
| Track | python |
| Package | format-factory-odt |
| Version | 0.1.0 |
| License | Apache-2.0 |
| Python | >=3.9 |
| .NET | unknown |
| Spec | OASIS Open Document Format TC ODF 1.3 (ISO/IEC 26300-3:2021) |
| QName coverage | 3/3 implemented |
| Source files | 19 |
| Test files | 30 |
<!-- END:README-PACKAGE_INFO -->

## Public API

<!-- BEGIN:README-PUBLIC_API generated=2026-06-28T08:14:26+00:00 source=src-python-init -->
- `(dynamic)`
<!-- END:README-PUBLIC_API -->
