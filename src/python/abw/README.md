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
