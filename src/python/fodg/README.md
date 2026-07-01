# aspose-format-factory-fodg

Python FOSS parser for the Flat OpenDocument Graphics (FODG) format.

**Package:** `aspose-format-factory-fodg`
**Version:** 0.1.0.dev0
**Track:** python-foss
**Capability Level:** alpha-foss-preview
**License:** Apache-2.0
**Spec:** ODF 1.3 (Part 3) -- OASIS Royalty-Free Category 1
**Gate history:** Gates 1-7 PASSED (format-factory project)

---

## Quick Start

```python
from fodg import load, get_page_count, get_shape_count, extract_text, get_page_metadata

# Load a FODG document
doc = load("path/to/drawing.fodg")

# Get the number of pages
count = get_page_count(doc)

# Get the total shape count
shapes = get_shape_count(doc)

# Extract all text content
text = extract_text(doc)

# Get metadata for a specific page
meta = get_page_metadata(doc, page_index=0)
```

## Security Notes

- File size capped at 64 MiB.
- Uses `xml.etree.ElementTree` (stdlib) -- XXE-safe by default.
- No external dependencies required.

## Dependencies

None (stdlib only).

## Package Structure

```
src/python/fodg/
    __init__.py          Public API exports
    fodg_codec.py        Core FODG parser (ODF 1.3 XML)
    LICENSE              Apache-2.0 license
    README.md            This file
```

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-07-01T12:16:26+00:00 source=package-metadata -->
```bash
pip install format-factory-fodg
```
<!-- END:README-INSTALLATION -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-07-01T12:16:26+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | Flat OpenDocument Drawing |
| Track | python |
| Package | format-factory-fodg |
| Version | 0.1.0.dev0 |
| License | Apache-2.0 |
| Python | >=3.9 |
| .NET | unknown |
| Spec | OASIS ODF 1.3 |
| QName coverage | 3/3 implemented |
| Source files | 18 |
| Test files | 101 |
<!-- END:README-PACKAGE_INFO -->

## Public API

<!-- BEGIN:README-PUBLIC_API generated=2026-07-01T12:16:26+00:00 source=src-python-init -->
- `(dynamic)`
<!-- END:README-PUBLIC_API -->

## License

<!-- BEGIN:README-LICENSE generated=2026-07-01T12:16:26+00:00 source=package-metadata -->
Apache-2.0
<!-- END:README-LICENSE -->
