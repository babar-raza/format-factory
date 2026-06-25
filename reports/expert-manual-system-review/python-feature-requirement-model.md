# Python FOSS Feature Requirement Model
# Format Factory — Expert Manual System Review
# Phase 4 output — Generated: 2026-06-25

## Purpose

Define what a "complete" Python FOSS library means for Format Factory,
by format category. This model is the target against which each package is assessed.

---

## Category 1: Spreadsheet Formats

Applies to: FODS, FODS/FODT, GNUMERIC, ODS, SYLK, DIF, TSV, CSV

### Minimum Viable FOSS Library (PY-3)

| Requirement | Description |
|------------|-------------|
| FOSS-SS-001 | Parse from file → return document model |
| FOSS-SS-002 | Document model exposes sheets, rows, cells |
| FOSS-SS-003 | Cell values accessible (string, numeric, date) |
| FOSS-SS-004 | Write/save function produces valid output file |
| FOSS-SS-005 | Roundtrip test: load → save → reload → values match |

### Release Candidate (PY-4)

| Requirement | Description |
|------------|-------------|
| FOSS-SS-006 | Export to CSV or JSON |
| FOSS-SS-007 | Installed wheel workflow proven |
| FOSS-SS-008 | spec_qname on document class |
| FOSS-SS-009 | Consumer roundtrip example in examples/ |

### Strong FOSS Product (PY-5)

| Requirement | Description |
|------------|-------------|
| FOSS-SS-010 | README with quickstart |
| FOSS-SS-011 | Cell edit API (add_row, set_cell, etc.) |
| FOSS-SS-012 | Error handling for malformed input |
| FOSS-SS-013 | Multi-sheet support where format allows |

---

## Category 2: Document/Text Formats

Applies to: FODT, ABW, ODT

### Minimum Viable (PY-3)

| Requirement | Description |
|------------|-------------|
| FOSS-DOC-001 | Parse from file → return paragraph list |
| FOSS-DOC-002 | Paragraphs accessible as strings |
| FOSS-DOC-003 | Write/save produces valid document |
| FOSS-DOC-004 | Export to plain text |

### Release Candidate (PY-4)

| Requirement | Description |
|------------|-------------|
| FOSS-DOC-005 | Export to Markdown or HTML |
| FOSS-DOC-006 | Installed wheel workflow proven |
| FOSS-DOC-007 | Append paragraph API |

---

## Category 3: Presentation Formats

Applies to: FODP

### Minimum Viable (PY-3)

| Requirement | Description |
|------------|-------------|
| FOSS-PRES-001 | Parse from file → return slide list |
| FOSS-PRES-002 | Slide content accessible |
| FOSS-PRES-003 | **Write/save produces valid presentation** |

**Note:** FODP currently at PY-2 — missing FOSS-PRES-003.
Export-only (txt/csv/json) is not adequate for a presentation library.

---

## Category 4: Drawing/Diagram Formats

Applies to: FODG

### Minimum Viable (PY-3)

| Requirement | Description |
|------------|-------------|
| FOSS-DRAW-001 | Parse from file → return shape/page model |
| FOSS-DRAW-002 | Shape content accessible |
| FOSS-DRAW-003 | Write/save produces valid drawing |

---

## Category 5: Image Formats — Raster

Applies to: PBM, PGM, PPM, QOI, XCF

### Minimum Viable (PY-3)

| Requirement | Description |
|------------|-------------|
| FOSS-IMG-001 | Parse → image model with dimensions, pixel access |
| FOSS-IMG-002 | Write produces valid image file (for formats that support it) |
| FOSS-IMG-003 | Format conversion where applicable (PBM→PGM, PGM→PPM) |

**Note:** XCF is a complex GIMP format — no-write is acceptable.
PBM/PGM/PPM all now have writers (corrected from initial assessment).

---

## Category 6: Config/Serialization Formats

Applies to: TOML, NDJSON

### Minimum Viable (PY-3)

| Requirement | Description |
|------------|-------------|
| FOSS-CFG-001 | Parse → typed config model |
| FOSS-CFG-002 | Write/serialize back to format |
| FOSS-CFG-003 | Key/value access API |

---

## Category 7: Compression

Applies to: ZST

### Minimum Viable (PY-3)

| Requirement | Description |
|------------|-------------|
| FOSS-COMP-001 | Compress data → bytes |
| FOSS-COMP-002 | Decompress bytes → original data |
| FOSS-COMP-003 | Document model with frame metadata |

**Note:** ZST Python satisfies all three via the zstandard library.

---

## Current Package Assessment Against Model

| Package | Category | Min Viable Met | RC Met | Strong Met | Gap |
|---------|----------|----------------|--------|------------|-----|
| FODS | SS | YES | YES | PARTIAL | No README per format |
| FODT | DOC | YES | YES | PARTIAL | No README per format |
| FODG | DRAW | YES | PARTIAL | NO | No installed wheel proven |
| ABW | DOC | YES | PARTIAL | NO | No export to Markdown |
| CSV | SS | YES | PARTIAL | NO | No multi-sheet (N/A) |
| DIF | SS | YES | PARTIAL | NO | Limited edit API |
| GNUMERIC | SS | YES | YES | NO | Dict model may confuse |
| NDJSON | CFG | YES | YES | NO | No export |
| ODS | SS | YES | PARTIAL | NO | No edit API |
| ODT | DOC | YES | PARTIAL | NO | No export to Markdown |
| PBM | IMG | YES | PARTIAL | NO | No installed wheel |
| PGM | IMG | YES | PARTIAL | NO | No installed wheel |
| PPM | IMG | YES | PARTIAL | NO | No installed wheel |
| QOI | IMG | YES | PARTIAL | NO | No export |
| SYLK | SS | YES | PARTIAL | NO | File-based API unusual |
| TOML | CFG | YES | PARTIAL | NO | No export |
| TSV | SS | YES | PARTIAL | NO | No multi-sheet (N/A) |
| XCF | IMG | PARTIAL | NO | NO | No write (acceptable), no export |
| ZST | COMP | YES | PARTIAL | NO | Analytics-heavy |
| FODP | PRES | NO | NO | NO | **Missing write_fodp** |
