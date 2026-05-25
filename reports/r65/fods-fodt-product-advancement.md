# R65 FODS/FODT Product Advancement

## FODS (2 new capabilities)
1. workbook_named_range_list(workbook) — returns list of defined named ranges
2. workbook_column_style_summary(workbook) — returns dict mapping sheet names to column style attributes

## FODT (2 new capabilities)
1. document_footnote_endnote_summary(document) — returns dict with footnote_count, endnote_count, inline_note_count
2. document_image_frame_list(document) — returns list of dicts with frame info

## Tests
- tests/python/fods/test_r65_fods_advancement.py
- tests/python/fodt/test_r65_fodt_advancement.py

FODS_FODT_ADVANCEMENT_STATUS: COMPLETE
