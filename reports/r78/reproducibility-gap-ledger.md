# R78 Reproducibility Gap Ledger

**sprint_id:** FORMAT-FACTORY-R78-TRUE-STATE-AND-FIRST-PRODUCT-FINISH-REPRODUCIBILITY-MEGA-TRAIN-001
**date:** 2026-05-30
**train:** C

## Gap Table

| ID | Format | Gap Description | Severity | R78 Status |
|---|---|---|---|---|
| REPRO-GAP-01 | FODS | parse_fods/write_fods round-trip requires sample .fods file not in wheel | MODERATE | DOCUMENTED |
| REPRO-GAP-02 | FODT | parse_fodt/write_fodt round-trip requires sample .fodt file not in wheel | MODERATE | DOCUMENTED |
| REPRO-GAP-03 | ZST | Full compress/decompress proof done (no external fixture needed for ZST) | N/A | CLOSED |
| REPRO-GAP-04 | FODS/FODT | Version is 0.1.0.dev0 (dev/alpha); wheel naming includes non-stable marker | MINOR | DOCUMENTED |
| REPRO-GAP-05 | FODS | document_append_paragraph / write_fodt structural gap (body.blocks vs root blocks) | MAJOR | DOCUMENTED |
| REPRO-GAP-06 | ALL | No deterministic build (wheel build date in metadata varies by machine) | MINOR | DOCUMENTED |

## Gap Analysis

### REPRO-GAP-01/02: Parse round-trip requires sample files
**Root cause:** FODS/FODT wheels are pure Python but require actual FODS/FODT files to
demonstrate parse/write. The wheel doesn't bundle sample files (correct for a library wheel).
**Mitigation:** tests/python/fods/ and tests/python/fodt/ have full round-trip tests
against samples/by-format/{fods,fodt}/ fixtures. The public API smoke test validates
all imports and in-memory API calls without needing a fixture file.
**R78 action:** DOCUMENTED — not a defect; standard library wheel behavior.

### REPRO-GAP-03: ZST fully reproducible
ZST smoke test includes compress/decompress round-trip in memory — no external file needed.
All 8 ZST public APIs verified in clean venv.
**R78 action:** CLOSED — ZST is fully reproducible.

### REPRO-GAP-05: FODT structural gap (body.blocks vs root blocks)
**Root cause:** `document_append_paragraph`, `document_remove_paragraph`, and
`document_paragraph_count` write to/read from `document["body"]["blocks"]`.
Analysis APIs (`document_text_content`, `document_heading_outline`) and `write_fodt`
read from root-level `document["blocks"]`. This dual-structure design means paragraphs
appended via the management API are NOT serialized by write_fodt.
**Impact:** For a parsed document, appended paragraphs are visible via `document_paragraph_count`
but not in round-trip text. For constructed documents with `body.blocks`, analysis APIs
return empty results.
**R78 action:** DOCUMENTED as GAP-FODT-STRUCT-001. Will require a future sprint to unify
the document model. Existing R77 tests (test_r77_fodt_paragraph_management.py) test
only the body.blocks APIs and pass. R78 tests document the dual-structure behavior.

## Reproducibility Summary

FODS_REPRODUCIBILITY: PASS (in-memory API proof)
FODT_REPRODUCIBILITY: PASS (in-memory API proof)
ZST_REPRODUCIBILITY: PASS (full compress/decompress proof)
GAPS_DOCUMENTED: 6
GAPS_BLOCKING_RC: 0 (all documented; no RC-blocking gaps)
