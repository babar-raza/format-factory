# R84 Train I: FODT Feature Advancement

**Sprint:** FORMAT-FACTORY-R84
**Train:** I
**Date:** 2026-05-31
**Status:** COMPLETE

## New APIs

### document_to_text(document) -> str

Plain-text export of a FODT document.

- Headings rendered as `# heading text` (using `#` count matching heading level)
- Tables rendered with tab-separated cells, rows separated by newlines
- Lists rendered with `- item` prefix
- Paragraphs rendered as plain text with newline separation
- Returns empty string for empty document

Source: `src/python/fodt/neutral_model.py`
Exported from: `src/python/fodt/__init__.py`

### document_get_paragraph_text(document, paragraph_index) -> str | None

Returns text of paragraph block at 0-based index among paragraph-type blocks.

- Counts only blocks with kind="paragraph" (not headings, tables, lists)
- Returns None if index out of range
- Read-side complement of document_set_block_text

Source: `src/python/fodt/neutral_model.py`
Exported from: `src/python/fodt/__init__.py`

## Tests

File: `tests/python/fodt/test_r84_fodt_text_export.py`
- 8 test cases: empty document, paragraphs only, headings, tables, lists,
  mixed content, get_paragraph_text by index, out-of-range returns None

## Documentation

Added to `docs/python-foss/fodt-api.md` under "R84 Additions".

## Result

PASS — both new APIs implemented, tested, documented, and exported.
