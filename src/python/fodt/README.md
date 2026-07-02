---
artifact_id: fodt-python-source-readme
artifact_type: source-python
path: src/python/fodt/README.md
format_id: fodt
product_family: words
visibility: public
publish_allowed: true
open_source_allowed: true
generated_by: claude-opus-4-6
generated_at: "2026-05-11"
notes: "FODT Python FOSS package README. TC-0052 Phase 4. IV repair."
---

# format-factory-fodt

Python FOSS parser for the OpenDocument Flat Text (FODT) format.

**Package:** `format-factory-fodt`
**Version:** 0.1.0
**License:** Apache-2.0
**ODF Spec:** ODF 1.3 (Part 3)
**Gate history:** Gates 1-9 PASSED (format-factory project, 2026-05-08); Phase 4 code-complete (2026-05-09)

---

## Quick Start

```python
from fodt import parse_fodt

result = parse_fodt("path/to/file.fodt")
if "error" in result:
    print(f"Parse failed: {result['error']}")
else:
    for block in result["blocks"]:
        print(f"{block['type']}: {block['text'][:60]}")
```

## Public API

<!-- BEGIN:README-PUBLIC_API generated=2026-07-02T13:18:25+00:00 source=src-python-init -->
- `(dynamic)`
<!-- END:README-PUBLIC_API -->

## Supported Scope (Tiers 0-2)

- Paragraphs and headings (with outline level 1-6)
- Lists with nested items (iterative traversal, safe for deep nesting)
- Tables with rows and cells
- MIME type and ODF version detection
- Unsupported feature detection (embedded frames, text fields, macros)

## Not Supported

- Embedded images / draw frames (detected, not extracted)
- Text fields (detected, not evaluated)
- Macros (detected, never executed)
- Styles, formatting, page layout
- Full ODF compliance is not claimed

## Security Notes

- File size capped at 100 MB (IR-FODT-002).
- Uses `defusedxml` when available for XXE protection (IR-FODT-004).
- List traversal uses explicit stack, not recursion (IR-FODT-003).
- Macros detected, never executed.

## Requirements Coverage

15/15 IR-FODT requirements implemented.
See `acquisition-packs/fodt/` for the full FUL package and traceability.

## Package Structure

```
src/python/fodt/
    __init__.py          Public API exports
    parser.py            Core FODT parser (iterparse streaming)
    neutral_model.py     Neutral model builder and validator (7-entity)
    list_traversal.py    Iterative DFS list item collection (IR-FODT-003)
    constants.py         ODF namespace URIs, element/attribute names
    exceptions.py        FodtError hierarchy
    README.md            This file
```

## Running Tests

```bash
python -m pytest tests/python/fodt/ -q
```

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-07-02T13:18:25+00:00 source=package-metadata -->
```bash
pip install format-factory-fodt-python
```
<!-- END:README-INSTALLATION -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-07-02T13:18:25+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | Flat OpenDocument Text |
| Track | python |
| Package | format-factory-fodt-python |
| Version | 0.1.0.dev0 |
| License | Apache-2.0 |
| Python | >=3.9 |
| .NET | unknown |
| Spec | OASIS ODF 1.3 |
| QName coverage | 8/9 implemented |
| Source files | 41 |
| Test files | 140 |
<!-- END:README-PACKAGE_INFO -->

## License

<!-- BEGIN:README-LICENSE generated=2026-07-02T13:18:25+00:00 source=package-metadata -->
Apache-2.0
<!-- END:README-LICENSE -->
