# R84 Train R: Examples/Docs from Installed Packages

**Sprint:** FORMAT-FACTORY-R84
**Train:** R
**Date:** 2026-05-31
**Status:** COMPLETE

## Examples Added/Updated

### FODS (examples/python/fods/)
- `example_fods_parse.py` — basic parse + stats
- `example_fods_csv_export.py` — workbook_to_csv usage (R84 new API)
- `example_fods_cell_value.py` — workbook_get_cell_value usage (R84 new API)

### FODT (examples/python/fodt/)
- `example_fodt_parse.py` — basic parse + stats
- `example_fodt_text_export.py` — document_to_text usage (R84 new API)
- `example_fodt_paragraph.py` — document_get_paragraph_text usage (R84 new API)

### ZST (examples/python/zst/)
- `example_zst_dependency_note.py` — notes DEPENDENCY_RESOLUTION_REQUIRED; no live decompress

### Netpbm (examples/python/pbm/ and examples/python/pgm/)
- `example_pbm_roundtrip.py` — write_pbm + parse_pbm roundtrip (R84 new API)
- `example_pgm_write.py` — write_pgm usage (R84 new API)

## Docs Updated

- `docs/python-foss/fods-api.md` — added R84 APIs section
- `docs/python-foss/fodt-api.md` — added R84 APIs section
- `docs/python-foss/sylk-api.md` — added sylk_to_csv section
- `docs/python-foss/dif-api.md` — added dif_to_csv section

## Supported/Unsupported Listings

All docs include explicit supported/unsupported feature tables (Gate 5 capability model).

## Result

PASS — examples and docs updated for all R84 new APIs.
