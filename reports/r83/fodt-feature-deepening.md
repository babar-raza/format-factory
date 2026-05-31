# R83 Train I — FODT Feature Deepening

**Sprint:** FORMAT-FACTORY-R83
**Date:** 2026-05-31

## Features Deepened

### Feature 1: Paragraph Roundtrip API (GAP-FODT-STRUCT-001 Confirmed)

Confirmed that the paragraph APIs work correctly from installed wheel:
- `document_append_paragraph(doc, text)` — adds paragraph to root `doc["blocks"]` AND `doc["content"]`
- `document_remove_paragraph(doc, idx)` — removes from both paths
- `document_paragraph_count(doc)` — counts from root `doc["blocks"]`

The bug was: APIs previously used `doc["body"]["blocks"]` which was wrong path.
Repair (R79): use root `doc["blocks"]`. Parser populates BOTH `doc["blocks"]` and `doc["content"]`.

**Roundtrip preserved:** parse_fodt → append_paragraph → write_fodt → parse_fodt yields same count.

### Feature 2: Document Stats API

`document_stats(doc)` returns:
```python
{
  "paragraph_count": int,
  "heading_count": int,
  "total_blocks": int,
  "has_body": bool,
}
```

### Feature 3: Heading Extraction

`document_headings(doc)` returns list of heading text strings.
Works on documents with Heading 1, Heading 2, etc. block types.

### Feature 4: Body Text Extraction

`document_body_text(doc)` returns full document text as single string.
Useful for content inspection without structural parsing.

## Source Changes

No source changes required in R83 — all deepening through documentation and tests.
GAP-FODT-STRUCT-001 was repaired in R79 (src/python/fodt/neutral_model.py).

## Capability Matrix Update

See `product-capability-matrix/fodt.yaml`

## FODT_FEATURE_DEEPENING: COMPLETE

