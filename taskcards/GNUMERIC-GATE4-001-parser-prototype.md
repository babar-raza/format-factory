# GNUMERIC-GATE4-001 — Gnumeric Gate 4 Parser Prototype

**Created:** 2026-05-16 (R19)
**Status:** not_started
**Priority:** MEDIUM
**Blocker:** Requires R20+ implementation sprint prompt

## Scope

Create `prototypes/by-format/gnumeric/gnumeric_parser.py`:
- Decompress gzip + parse Gnumeric XML (gnm: namespace v10)
- Extract: sheet count, sheet names, cell data (row/col/value/type)
- Corpus validation: 3 synthetic samples from samples/by-format/gnumeric/

## Key Technical Notes

- File format: gzip-compressed XML
- Namespace: xmlns:gnm="http://www.gnumeric.org/v10.dtd"
- Root element: Workbook
- Parse flow: gzip.decompress() → xml.etree.ElementTree.parse()
- Cell ValueTypes: 60=string, 40=integer, 30=float (from XSD schema)

## Prerequisites

- [x] Gnumeric Gate 1: passed
- [x] Gnumeric Gate 2: passed (XSD retrieved)
- [x] Gnumeric Gate 3: passed (3 synthetic samples)
- [ ] Prototype: not created yet
- [ ] Gate 4 tests: not created yet
- [ ] DEC-034 IV: not done yet

## Test Plan

- PT-001: minimal-spreadsheet.gnumeric — sheet_count == 1, name == "Sheet1"
- PT-002: multi-cell-basic.gnumeric — cell(0,0) == "Name"
- PT-003: empty-sheet.gnumeric — cells == []
- PT-004: All 3 samples — no crash, valid decompression
