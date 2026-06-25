# Feature Availability Review Plan

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## Feature Availability Levels (FA-0 through FA-5)

| Level | Meaning |
|-------|---------|
| **FA-0** | Feature not available (not implemented) |
| **FA-1** | Internal only or unproven (code exists but no public API or no tests) |
| **FA-2** | Public API exists but weak (no tests, no examples, limited cases) |
| **FA-3** | Implemented and tested (basic case covered) |
| **FA-4** | Implemented with edge/error/roundtrip tests |
| **FA-5** | Professional with docs, examples, output proof, and edge cases |

---

## Feature Sets by Format Domain

### Spreadsheet Formats: FODS, ODS, SYLK, DIF, GNUMERIC, CSV, TSV

**Core spreadsheet features to check:**

| Feature | FODS .NET | FODS Py | ODS Py | SYLK Py | DIF Py | GNUMERIC Py | CSV .NET | CSV Py | TSV .NET | TSV Py |
|---------|-----------|---------|--------|---------|--------|-------------|----------|--------|----------|--------|
| Load from file | FA-4 | FA-4 | FA-4 | FA-3 | FA-3 | FA-4 | FA-3 | FA-3 | FA-3 | FA-3 |
| Typed cell values (str/num/bool/date) | FA-4 | FA-3 | FA-3 | FA-2 | FA-2 | FA-3 | FA-2 | FA-2 | FA-2 | FA-2 |
| Multi-sheet access | FA-4 | FA-4 | FA-3 | FA-0 | FA-0 | FA-3 | FA-0 | FA-0 | FA-0 | FA-0 |
| Get/set single cell value | FA-5 | FA-4 | FA-3 | FA-3 | FA-2 | FA-3 | FA-3 | FA-3 | FA-3 | FA-3 |
| Add/remove row | FA-4 | FA-3 | FA-3 | FA-3* | FA-2 | FA-3 | FA-1 | FA-1 | FA-1 | FA-1 |
| Add/remove/rename sheet | FA-4 | FA-3 | FA-3 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 |
| Cell merge | FA-3 | FA-2 | FA-1 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 |
| Cell style/formatting | FA-3 | FA-2 | FA-1 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 |
| Formula (write) | FA-3 | FA-2 | FA-1 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 |
| Formula (evaluate) | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 |
| Sort rows | FA-4 | FA-3 | FA-2 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 |
| Filter rows | FA-4 | FA-3 | FA-2 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 |
| Export to CSV | FA-5 | FA-4 | FA-4 | FA-4 | FA-1 | FA-4 | FA-3 | FA-3 | FA-3 | FA-2 |
| Export to HTML | FA-4 | FA-3 | FA-2 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 |
| Export to JSON | FA-4 | FA-3 | FA-2 | FA-0 | FA-0 | FA-3 | FA-0 | FA-0 | FA-0 | FA-0 |
| Roundtrip (load → edit → save → reload) | FA-4 | FA-4 | FA-3 | FA-2 | FA-2 | FA-3 | FA-2 | FA-2 | FA-2 | FA-2 |
| Malformed input guard | FA-4 | FA-3 | FA-2 | FA-1 | FA-1 | FA-2 | FA-2 | FA-2 | FA-2 | FA-2 |
| Column header access | FA-5 | FA-4 | FA-3 | FA-2 | FA-1 | FA-3 | FA-3 | FA-3 | FA-2 | FA-3 |

*SYLK add_row is file-based

### Document Formats: FODT, ODT, ABW

**Core document features to check:**

| Feature | FODT .NET | FODT Py | ODT Py | ABW Py |
|---------|-----------|---------|--------|--------|
| Load from file | FA-4 | FA-4 | FA-4 | FA-4 |
| Paragraph CRUD | FA-4 | FA-4 | FA-3 | FA-4 |
| Heading management | FA-4 | FA-3 | FA-2 | FA-0 |
| Lists (ordered/unordered) | FA-3 | FA-2 | FA-1 | FA-0 |
| Tables in document | FA-2* | FA-2 | FA-1 | FA-0 |
| Text search/replace | FA-3 | FA-3 | FA-1 | FA-1 |
| Metadata (author/title/date) | FA-3 | FA-2 | FA-1 | FA-0 |
| Plain text export | FA-4 | FA-4 | FA-2 | FA-3 |
| HTML export | FA-4 | FA-4 | FA-1 | FA-1 |
| Markdown export | FA-4 | FA-4 | FA-1 | FA-0 |
| PDF export | FA-2** | FA-0 | FA-0 | FA-0 |
| Roundtrip | FA-4 | FA-4 | FA-3 | FA-3 |
| Create from scratch | FA-4 | FA-4 | FA-3 | FA-3 |

*Table in FODT .NET — Spec/Table exists but wiring unconfirmed
**PDF likely stub

### Image Formats: PBM/PGM/PPM .NET (NetPBM), PBM/PGM/PPM Python, QOI Python, XCF Python

| Feature | NetPBM .NET | PBM Py | PGM Py | PPM Py | QOI Py | XCF Py |
|---------|-------------|--------|--------|--------|--------|--------|
| Load from file | FA-4 | FA-4 | FA-4 | FA-4 | FA-3 | FA-4 |
| Load from stream | FA-4 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 |
| Get dimensions | FA-4 | FA-4 | FA-4 | FA-4 | FA-3 | FA-4 |
| Pixel access (get/set) | FA-4 | FA-3 | FA-3 | FA-3 | FA-2 | FA-0 |
| Color channel separation | FA-4 | FA-2 | FA-2 | FA-4 | FA-2 | FA-0 |
| Flip horizontal/vertical | FA-4 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 |
| Rotate | FA-4 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 |
| Resize | FA-4 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 |
| Crop | FA-4 | FA-0 | FA-0 | FA-0 | FA-0 | FA-0 |
| Format conversion | FA-4 | FA-4 | FA-4 | FA-3 | FA-0 | FA-0 |
| Save/write | FA-4 | FA-3 | FA-3 | FA-3 | FA-3 | FA-0 |
| Binary format (P4/P5/P6) | FA-3 | FA-4 | FA-4 | FA-4 | N/A | N/A |
| ASCII format (P1/P2/P3) | FA-3 | FA-4 | FA-4 | FA-4 | N/A | N/A |
| Malformed input guard | FA-4 | FA-5 | FA-4 | FA-4 | FA-2 | FA-2 |
| Layer access (XCF) | N/A | N/A | N/A | N/A | N/A | FA-4 |
| Layer names (real) | N/A | N/A | N/A | N/A | N/A | FA-4 |

### Compression: ZST .NET, ZST Python

| Feature | ZST .NET | ZST Python |
|---------|----------|------------|
| Load/Parse metadata | FA-3 | FA-3 |
| Frame count detection | FA-3 | FA-3 |
| Magic bytes validation | FA-3 | FA-3 |
| Compress string/bytes | FA-0 | FA-4 |
| Decompress bytes | FA-0 | FA-4 |
| Compress file | FA-0 | FA-3 |
| Decompress file | FA-0 | FA-3 |
| Roundtrip (compress → decompress) | FA-0 | FA-4 |
| Frame inspection | FA-3 | FA-3 |
| Multiple frame support | FA-2 | FA-2 |
| Stream-based compress/decompress | FA-0 | FA-0 |
| Level control (compression level) | FA-0 | FA-4 |

---

## Critical Feature Gaps Summary

| Product | Missing Feature | FA Gap | Severity |
|---------|----------------|--------|----------|
| ZST .NET | Compress/decompress capability | FA-0 | CRITICAL |
| ZST .NET | ZstWriter class | FA-0 | CRITICAL |
| FODP Python | Write/save capability | FA-0 | HIGH |
| XCF Python | Write/export capability | FA-0 | HIGH |
| QOI Python | Full edit API | FA-0 | MEDIUM |
| SYLK Python | Model-based edit (currently file-based) | FA-1 | MEDIUM |
| FODT .NET | Table operations (Spec/Table/* wiring?) | FA-1→FA-2 | MEDIUM |
| All .NET except NetPBM | Stream Load | FA-0 | MEDIUM |
| CSV/TSV .NET | Edit API (add row, set cell) | FA-1 | LOW |
| All formats | Formula evaluation | FA-0 | LOW (deferred) |
| All formats | Async load/save APIs | FA-0 | LOW (deferred) |

---

## Feature Availability Scoring Method

For each feature in the matrix:
1. Does a public API method exist for this feature?
2. Can it be invoked from `__init__.py` or namespace without reading source?
3. Are there tests covering it?
4. Do the tests include edge cases (empty, malformed, large, special characters)?
5. Are there examples showing real usage?
6. Is there documentation (docstring, XML comment, README)?

Score FA-0 if step 1 fails. FA-1 if step 1 passes but step 2 fails. FA-2 if steps 1-2 pass. FA-3 for steps 1-3. FA-4 for steps 1-4. FA-5 for all steps.
