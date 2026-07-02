# aspose-format-factory-fodp

Python FOSS parser for the Flat OpenDocument Presentation (FODP) format.

**Package:** `aspose-format-factory-fodp`
**Version:** 0.1.0.dev0
**Track:** python-foss
**Capability Level:** alpha-foss-preview
**License:** Apache-2.0
**Spec:** ODF 1.3 (Part 3) -- OASIS Royalty-Free Category 1
**Gate history:** Gates 1-7 PASSED (format-factory project)

---

## Quick Start

```python
from fodp import load, get_page_count, extract_text, get_page_metadata

# Load a FODP document
doc = load("path/to/presentation.fodp")

# Get the number of pages (slides)
count = get_page_count(doc)

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
src/python/fodp/
    __init__.py          Public API exports
    fodp_codec.py        Core FODP parser (ODF 1.3 XML)
    LICENSE              Apache-2.0 license
    README.md            This file
```

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-07-02T07:51:54+00:00 source=package-metadata -->
```bash
pip install format-factory-fodp
```
<!-- END:README-INSTALLATION -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-07-02T07:51:54+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | Flat OpenDocument Presentation |
| Track | python |
| Package | format-factory-fodp |
| Version | 0.1.0 |
| License | Apache-2.0 |
| Python | >=3.9 |
| .NET | unknown |
| Spec | OASIS ODF 1.3 |
| QName coverage | 3/3 implemented |
| Source files | 15 |
| Test files | 36 |
<!-- END:README-PACKAGE_INFO -->

## Public API

<!-- BEGIN:README-PUBLIC_API generated=2026-07-02T07:51:54+00:00 source=src-python-init -->
- `(dynamic)`
<!-- END:README-PUBLIC_API -->

## License

<!-- BEGIN:README-LICENSE generated=2026-07-02T07:51:54+00:00 source=package-metadata -->
Apache-2.0
<!-- END:README-LICENSE -->
