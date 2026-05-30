# R76 Train G — FODT Python Product Deepening

**sprint:** FORMAT-FACTORY-R76-PARALLEL-FINISH-LINE-ARTIFACT-AUTHORITY-PRODUCT-DEEPENING-GATE-READINESS-MEGA-TRAIN-001
**date:** 2026-05-30
**status:** COMPLETE

## New APIs Added

### document_set_block_text(document, block_idx, new_text, preserve_style=True)
Mutates the neutral model in-place for edit-then-write workflows.
- Returns (ok: bool, message: str)
- Updates block["text"] and reconstructs runs
- Preserves first run style when preserve_style=True
- Added to `src/python/fodt/neutral_model.py`
- Exported in `src/python/fodt/__init__.py`

### document_warnings_for_unsupported_edit(document, block_idx)
Returns list of warning strings for unsupported edit scenarios:
- Multi-run block (style info from non-first runs will be lost)
- Hyperlink in block (hyperlink not preserved in neutral model)
- Added to `src/python/fodt/neutral_model.py`
- Exported in `src/python/fodt/__init__.py`

## FODT Exported APIs: 25 (R75: 23, R76: +2)

## Tests

14 tests in `tests/python/fodt/test_r76_fodt_edit_save.py`: All PASS

## Example

`examples/python/fodt/edit_save_fodt.py` — full edit-and-save workflow verified round-trip.
