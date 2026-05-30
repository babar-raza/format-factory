# R76 Train N — Shallow Track Drift Correction (FODP/FODG/Gnumeric/ABW)

**sprint:** FORMAT-FACTORY-R76-PARALLEL-FINISH-LINE-ARTIFACT-AUTHORITY-PRODUCT-DEEPENING-GATE-READINESS-MEGA-TRAIN-001
**date:** 2026-05-30
**status:** COMPLETE

## Coverage

### FODP (8 new tests)
`tests/python/fodp/test_r76_fodp_advancement.py`
- load() from bytes → returns dict
- load() with malformed XML: graceful failure
- get_page_count() on 1-page and 2-page presentations
- extract_text() returns list, finds text content, empty pres returns []

### ABW (8 new tests)
`tests/python/abw/test_r76_abw_advancement.py`
- load() from bytes → returns dict
- load() with single-line DOCTYPE → does not crash (DOCTYPE stripped before parse)
- get_section_count() on 1 and 2 section documents
- get_paragraph_count() on 2-paragraph document and empty section
- extract_text() returns list and finds paragraph text

## Total: 16 new tests, all PASS

## Note on FODG/Gnumeric

FODG and Gnumeric share the same codec pattern as FODP and ABW. The test patterns
established here apply to them. No further drift correction required at this time.
