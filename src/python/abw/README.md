# aspose-format-factory-abw

Python FOSS parser for the AbiWord (ABW) document format.

**Package:** `aspose-format-factory-abw`
**Version:** 0.1.0.dev0
**Track:** python-foss
**Capability Level:** alpha-foss-preview
**License:** Apache-2.0
**Spec:** AWML 1.0 (AbiWord Markup Language, plain XML)
**Gate history:** Gates 1-7 PASSED (format-factory project)

---

## Quick Start

```python
from abw import load, get_section_count, get_paragraph_count, extract_text

# Load an AbiWord document
doc = load("path/to/document.abw")

# Get the number of sections
sections = get_section_count(doc)

# Get the number of paragraphs
paragraphs = get_paragraph_count(doc)

# Extract all text content
text = extract_text(doc)
```

## Security Notes

- File size capped at 64 MiB.
- DOCTYPE declarations stripped before parsing (XXE protection).
- Uses `xml.etree.ElementTree` (stdlib) -- XXE-safe by default.
- No external dependencies required.

## Dependencies

None (stdlib only).

## Package Structure

```
src/python/abw/
    __init__.py          Public API exports
    abw_codec.py         Core ABW parser (AWML 1.0 XML)
    LICENSE              Apache-2.0 license
    README.md            This file
```

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-07-01T21:21:02+00:00 source=package-metadata -->
```bash
pip install format-factory-abw
```
<!-- END:README-INSTALLATION -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-07-01T21:21:02+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | AbiWord Word Processing Document |
| Track | python |
| Package | format-factory-abw |
| Version | 0.1.0.dev0 |
| License | Apache-2.0 |
| Python | >=3.9 |
| .NET | unknown |
| Spec | AbiSource Project AWML 1.0 (outdated DTD) |
| QName coverage | 0/3 implemented |
| Source files | 19 |
| Test files | 156 |
<!-- END:README-PACKAGE_INFO -->

## Public API

<!-- BEGIN:README-PUBLIC_API generated=2026-07-01T21:21:02+00:00 source=src-python-init -->
- `(dynamic)`
<!-- END:README-PUBLIC_API -->

## License

<!-- BEGIN:README-LICENSE generated=2026-07-01T21:21:02+00:00 source=package-metadata -->
Apache-2.0
<!-- END:README-LICENSE -->
