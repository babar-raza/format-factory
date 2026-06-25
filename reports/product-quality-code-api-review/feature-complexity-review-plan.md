# Feature Complexity Review Plan

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## Feature Complexity Levels (C0–C5)

| Level | Meaning |
|-------|---------|
| **C0** | No implementation |
| **C1** | Trivial wrapper or hardcoded behavior (passes constant, always returns same value) |
| **C2** | Simple happy-path (works for one clean example; no edge cases, no errors) |
| **C3** | Structured with real parsing/model behavior (handles multiple cases, basic errors) |
| **C4** | Handles variants, errors, roundtrip, practical cases (production-grade happy path) |
| **C5** | Advanced, extensible, robust commercial-grade (handles all edge cases, well-tested, documented) |

---

## Complexity Assessment Method

For each feature:
1. Read the implementing source
2. How many conditional branches handle different cases?
3. Does it handle malformed input meaningfully?
4. Does it preserve semantics on roundtrip?
5. Does it handle the format's full variant range?
6. Is there a test verifying correct behavior for multiple inputs?

C0: No code. C1: 1-2 lines, trivial. C2: Simple logic, 1 path. C3: Multiple branches, real parsing. C4: Full case coverage + error handling. C5: All edge cases + documentation + tests.

---

## Feature Complexity Estimates by Product

### FODS .NET — Spreadsheet Operations

| Feature | Estimated C-Level | Rationale |
|---------|------------------|-----------|
| Load FODS from file | C4 | DTD guard, size guard, LINQ to XML, namespace resolution |
| SetCellValue(sheet, row, col, value) | C4 | DOM navigation, cell creation/update, type handling |
| GetCellValue(sheet, row, col) | C4 | DOM query, repeated-cell handling, type parsing |
| GetColumnHeaders() | C4 | Multiple overloads; header detection logic |
| MergeCells() | C3 | Merge-span attribute writing; no edge cases visible |
| SetCellFormula() | C3 | Formula string injection; no formula validation |
| SetCellStyle() | C3 | Style attribute setting; no style resolution |
| SortRows() | C4 | Stable sort, culture-invariant number parsing |
| FilterRows() | C4 | Predicate-based filtering, returns matching rows |
| AddSheet() / RemoveSheet() | C4 | DOM manipulation with validation |
| CopySheet() | C3 | Deep XML clone; may not handle all edge cases |
| Save() | C4 | Atomic DOM serialization; namespace preservation |
| Export to CSV | C4 | Escape handling, header row, empty cell handling |
| Export to HTML | C4 | Table generation, header, cell types |
| Roundtrip (load → edit → save → reload) | C4 | Verified in tests |

**FODS .NET Overall Complexity:** C4

### FODT .NET — Document Operations

| Feature | Estimated C-Level | Rationale |
|---------|------------------|-----------|
| Load FODT from file | C4 | Same as FODS (DTD guard, size guard, LINQ to XML) |
| AddParagraph() | C4 | DOM manipulation, namespace handling |
| RemoveParagraph() | C4 | DOM remove with index validation |
| AddHeading() | C4 | text:h element creation with level attribute |
| AddList() | C3 | list element; likely simple implementation |
| Export to HTML | C4 | Paragraph → div/p conversion |
| Export to Markdown | C4 | Heading → #, paragraph → newline |
| Export to TXT | C4 | Strip all tags |
| Export to PDF | C1-C2 | Likely stub or thin wrapper |
| Export to PNG | C1-C2 | Likely stub or thin wrapper |

**FODT .NET Overall Complexity:** C3-C4

### NetPBM .NET — Image Operations

| Feature | Estimated C-Level | Rationale |
|---------|------------------|-----------|
| Load PBM (P1 ASCII) | C4 | Parse rows, handle whitespace/comments, validate size |
| Load PBM (P4 binary) | C4 | Bit-packed binary decode, alignment handling |
| Load PGM (P5 binary) | C4 | Byte-per-pixel binary decode |
| Load PPM (P6 binary) | C4 | RGB triplet binary decode |
| GetPixel() | C3 | Array index calculation |
| SetPixel() | C3 | Array index write |
| FlipHorizontal() | C4 | Handles both PPM (3-channel) and PBM/PGM (single-channel) separately — confirmed in source |
| FlipVertical() | C3-C4 | Similar handling |
| Rotate() | C3 | Matrix transpose |
| Resize() | C3 | Nearest-neighbor interpolation (likely) |
| Crop() | C3 | Subarray extraction |
| ApplyBlur() | C3 | Convolution kernel |
| ApplySepia() | C3 | Fixed transformation matrix |
| PBM→PGM conversion | C4 | Confirmed in NetpbmExporter.cs |
| PBM→PPM conversion | C4 | Confirmed in NetpbmExporter.cs |
| Save (binary format) | C4 | Bit-pack for P4, byte for P5, RGB for P6 |

**NetPBM .NET Overall Complexity:** C4

### NDJSON .NET — JSON Operations

| Feature | Estimated C-Level | Rationale |
|---------|------------------|-----------|
| Load from content string | C3 | Split lines, parse each as JsonDocument |
| Load from stream | C3 | StreamReader line-by-line |
| LoadFile from path | C3 | File.ReadAllLines then parse |
| GetAllKeys() | C3 | Enumerate JsonElement properties, union set |
| Filter() | C3 | LINQ predicate on List<JsonElement> |
| GetFieldValues(key) | C3 | Enumerate records, get property by key |
| IsUniformSchema() | C3 | Check all records have same keys |
| SaveToFile() | C2 | Serialize each JsonElement back to JSON line |
| Export to CSV | C3 | Key-based CSV construction |

**NDJSON .NET Overall Complexity:** C3

### ZST .NET — Read-Only

| Feature | Estimated C-Level | Rationale |
|---------|------------------|-----------|
| Parse magic bytes | C3 | Read first 4 bytes, compare |
| Count frames | C3 | Scan frame boundaries |
| Read frame header descriptor | C3 | Read FHD byte from first frame |
| Computed properties | C2 | Simple arithmetic on parsed values |
| Compress | C0 | NOT IMPLEMENTED |
| Decompress | C0 | NOT IMPLEMENTED |

**ZST .NET Overall Complexity:** C2-C3 (for inspection only)

### Python FODS

| Feature | Estimated C-Level | Rationale |
|---------|------------------|-----------|
| parse_fods (neutral model) | C4 | Full XML → dict with sheet/row/cell hierarchy |
| FodsDocument class | C3 | Thin wrapper over neutral model |
| write_fods | C4 | Dict → XML with namespace handling |
| workbook_set_cell_value | C3 | Dict mutation |
| CSV export | C3 | Flatten to CSV |
| TSV export | C3 | Flatten to TSV |
| Roundtrip | C4 | Tested via examples |

**FODS Python Overall Complexity:** C3-C4

### Python PBM

| Feature | Estimated C-Level | Rationale |
|---------|------------------|-----------|
| parse_pbm (P1 ASCII) | C4 | Token-based parser with comment handling |
| parse_pbm (P4 binary) | C4 | Bit-packed binary decode |
| parse_pbm_strict | C4 | Additional validation layer |
| probe_pbm | C3 | Header-only check |
| Error hierarchy | C5 | 4 specific exception types with meaningful messages |
| PBM→PGM conversion | C4 | Format conversion with proper grayscale encoding |
| Security guards | C4 | MAX_FILE_SIZE, MAX_DIMENSION with meaningful errors |

**PBM Python Overall Complexity:** C4

### Python ZST

| Feature | Estimated C-Level | Rationale |
|---------|------------------|-----------|
| compress_string | C3 | zstandard library call with level |
| decompress_to_string | C3 | zstandard library decompress call |
| ZstDocument.from_file | C3 | Parse file stats and frame info |
| Roundtrip | C4 | Verified in consumer_roundtrip.py |

**ZST Python Overall Complexity:** C3

### Python FODP

| Feature | Estimated C-Level | Rationale |
|---------|------------------|-----------|
| load() | C3 | XML parse → dict |
| get_page_count(path) | C2 | Count page elements |
| fodp_slide_count(path) | C2 | Alias of above |
| Write | C0 | NOT IMPLEMENTED |

**FODP Python Overall Complexity:** C2

---

## Complexity Summary Table

| Product | Load | Edit | Save | Export | Overall |
|---------|------|------|------|--------|---------|
| FODS .NET | C4 | C4 | C4 | C4 | **C4** |
| FODT .NET | C4 | C4 | C4 | C3 | **C3-C4** |
| NetPBM .NET | C4 | C4 | C4 | C4 | **C4** |
| NDJSON .NET | C3 | C2 | C2 | C3 | **C3** |
| CSV .NET | C3 | C2 | C2 | C1 | **C2** |
| TSV .NET | C3 | C1 | C2 | C3 | **C2** |
| ZST .NET | C3 | C0 | C0 | C0 | **C1-C2** |
| FODS Python | C4 | C3 | C4 | C3 | **C3-C4** |
| FODT Python | C4 | C4 | C4 | C4 | **C4** |
| ODS Python | C3 | C3 | C3 | C3 | **C3** |
| PBM Python | C4 | C0 | C3 | C4 | **C3-C4** |
| ZST Python | C3 | C0 | C3 | C0 | **C3** |
| SYLK Python | C3 | C2 | C2 | C3 | **C2-C3** |
| DIF Python | C3 | C2 | C3 | C1 | **C2** |
| GNUMERIC Python | C3 | C3 | C3 | C3 | **C3** |
| FODP Python | C3 | C0 | C0 | C0 | **C2** |
| QOI Python | C3 | C1 | C3 | C0 | **C2-C3** |
| XCF Python | C3 | C0 | C0 | C0 | **C2** |
