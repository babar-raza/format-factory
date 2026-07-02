---
artifact_id: fods-python-source-readme
artifact_type: source-python
path: src/python/fods/README.md
format_id: fods
product_family: cells
visibility: public
publish_allowed: true
open_source_allowed: true
generated_by: claude-sonnet-4-6
generated_at: "2026-05-09"
notes: "FODS Python FOSS package README. TC-0050 Phase 4."
---

# format-factory-fods

Python FOSS parser for the OpenDocument Flat Spreadsheet (FODS) format.

**Package:** `format-factory-fods`
**Version:** 0.1.0
**License:** Apache-2.0
**ODF Spec:** ODF 1.3 (Part 3)
**Gate history:** Gates 1-10 PASSED (format-factory project, 2026-05-08)

---

## Quick Start

```python
from fods import parse_fods

result = parse_fods("path/to/file.fods")
if "error" in result:
    print(f"Parse failed: {result['error']}")
else:
    for sheet in result["sheets"]:
        print(f"Sheet: {sheet['name']}  ({sheet['row_count']} rows)")
```

## Security Notes

- File size capped at 100 MB (IR-FODS-003).
- Uses `defusedxml` when available for XXE protection (IR-FODS-004).
- Row/column repeat expansion capped at 128 (IR-FODS-010/011).
- Macros detected, never executed (IR-FODS-016).

## Requirements Coverage

19/20 IR-FODS requirements implemented. IR-FODS-008 (formula evaluation) deferred Tier 3.
See `acquisition-packs/fods/phase4-traceability-matrix.md` for full mapping.

## Package Structure

```
src/python/fods/
    __init__.py          Public API exports
    parser.py            Core FODS parser (iterparse streaming)
    neutral_model.py     Neutral model builder and validator
    constants.py         ODF namespace URIs, element/attribute names
    exceptions.py        FodsError hierarchy
    README.md            This file
```

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-07-02T16:00:06+00:00 source=package-metadata -->
```bash
pip install format-factory-fods-python
```
<!-- END:README-INSTALLATION -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-07-02T16:00:06+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | Flat OpenDocument Spreadsheet |
| Track | python |
| Package | format-factory-fods-python |
| Version | 0.1.0 |
| License | Apache-2.0 |
| Python | >=3.9 |
| .NET | unknown |
| Spec | OASIS ODF 1.3 |
| QName coverage | 12/12 implemented |
| Source files | 49 |
| Test files | 107 |
<!-- END:README-PACKAGE_INFO -->

## Public API

<!-- BEGIN:README-PUBLIC_API generated=2026-07-02T16:00:06+00:00 source=src-python-init -->
- `(dynamic)`
<!-- END:README-PUBLIC_API -->

## License

<!-- BEGIN:README-LICENSE generated=2026-07-02T16:00:06+00:00 source=package-metadata -->
Apache-2.0
<!-- END:README-LICENSE -->
