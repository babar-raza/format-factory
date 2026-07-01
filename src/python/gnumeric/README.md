# aspose-format-factory-gnumeric

Python FOSS parser for the Gnumeric spreadsheet format.

**Package:** `aspose-format-factory-gnumeric`
**Version:** 0.1.0.dev0
**Track:** python-foss
**Capability Level:** alpha-foss-preview
**License:** Apache-2.0
**Spec:** Gnumeric XML (gzip-compressed, namespace http://www.gnumeric.org/v10.dtd)
**Gate history:** Gates 1-7 PASSED (format-factory project)

---

## Quick Start

```python
from gnumeric import load, get_sheet_count, get_cell_count, extract_values, get_sheet_metadata

# Load a Gnumeric document
doc = load("path/to/spreadsheet.gnumeric")

# Get the number of sheets
count = get_sheet_count(doc)

# Get total cell count
cells = get_cell_count(doc)

# Extract all cell values
values = extract_values(doc)

# Get metadata for a specific sheet
meta = get_sheet_metadata(doc, sheet_index=0)
```

## Security Notes

- Compressed file size capped at 64 MiB.
- Uses `gzip` + `xml.etree.ElementTree` (stdlib) -- XXE-safe by default.
- No external dependencies required.

## Dependencies

None (stdlib only).

## Package Structure

```
src/python/gnumeric/
    __init__.py              Public API exports
    gnumeric_codec.py        Core Gnumeric parser (gzip + XML)
    LICENSE                  Apache-2.0 license
    README.md                This file
```

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-07-01T22:41:26+00:00 source=package-metadata -->
```bash
pip install format-factory-gnumeric
```
<!-- END:README-INSTALLATION -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-07-01T22:41:26+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | Gnumeric Spreadsheet |
| Track | python |
| Package | format-factory-gnumeric |
| Version | 0.1.0.dev0 |
| License | Apache-2.0 |
| Python | >=3.9 |
| .NET | unknown |
| Spec | GNOME Project Gnumeric XML format (GNOME documentation) |
| QName coverage | 3/3 implemented |
| Source files | 16 |
| Test files | 118 |
<!-- END:README-PACKAGE_INFO -->

## Public API

<!-- BEGIN:README-PUBLIC_API generated=2026-07-01T22:41:26+00:00 source=src-python-init -->
- `(dynamic)`
<!-- END:README-PUBLIC_API -->

## License

<!-- BEGIN:README-LICENSE generated=2026-07-01T22:41:26+00:00 source=package-metadata -->
Apache-2.0
<!-- END:README-LICENSE -->
