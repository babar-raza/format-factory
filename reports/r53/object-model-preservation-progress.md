# Object Model Preservation Progress

**Sprint:** FORMAT-FACTORY-R53-SELF-VERIFYING-BASELINE-001
**Date:** 2026-05-22

## FODS Preservation Status

| Feature | Parse | Write | Round-trip | Test |
|---------|-------|-------|-----------|------|
| String cells | PASS | PASS | PASS | tests/python/fods/ |
| Float/numeric cells | PASS | PASS | PASS | tests/python/fods/ |
| Boolean cells | PASS | PASS | PASS | tests/python/fods/ |
| Date cells | PASS | warning | Partial | tests/python/fods/ |
| Formula attribute (TC-0054) | PASS | **PASS (R53)** | **PASS (R53)** | test_r53_formula_preservation.py |
| Sheet name | PASS | PASS | PASS | tests/python/fods/ |
| Multi-sheet | PASS | PASS | PASS | tests/python/fods/ |
| Macros/scripts | Detect+warn | n/a | n/a | tests/python/fods/ |
| Merged/covered cells | Detect+warn | n/a | n/a | tests/python/fods/ |
| Embedded charts | Detect+warn | n/a | n/a | tests/python/fods/ |

## FODT Preservation Status

| Feature | Parse | Write | Round-trip | Test |
|---------|-------|-------|-----------|------|
| Paragraphs | PASS | PASS | PASS | tests/python/fodt/ |
| Headings (text:outline-level) | PASS | MISSING (TC-0057) | PARTIAL | tests/python/fodt/ |
| Lists (text:list) | PASS | MISSING (TC-0058) | PARTIAL | tests/python/fodt/ |
| Tables (table:table) | PASS | MISSING (TC-0059) | PARTIAL | tests/python/fodt/ |
| TXT export | PASS | n/a | PASS | tests/python/fodt/ |
| Inline spans/formatting | Detect+collect | n/a | PARTIAL | tests/python/fodt/ |
| Embedded images | Detect+warn | n/a | n/a | tests/python/fodt/ |
| Macros/scripts | Detect+warn | n/a | n/a | tests/python/fodt/ |

## Key R53 Advance

**TC-0054 closed:** FODS formula attribute now preserved verbatim on write.

Before R53: `parse_fods("formula.fods")["sheets"][0]["rows"][3]["cells"][0]["formula"]` → `"oooc:=SUM([.A1:.A3])"` but after `write_fods(wb, path)` + re-parse, `formula` was `None`.

After R53: formula round-trip verified in `test_r53_formula_preservation.py::test_formula_roundtrip_via_fixture`.

## Known Limitations (FODT)

Writer uses a simplified block-by-block serialization. Heading, list, and table blocks
are written as plain paragraphs without their structural attributes. This is intentional
for the current alpha scope — the parser correctly captures structure, and the writer
will be extended in R54+ to emit heading/list/table XML.

## Deferred Features

- FODT heading/list/table write-back: R54
- FODT Markdown export: R54+
- FODS formula evaluation: explicitly deferred per IR-FODS-008 (security boundary)
