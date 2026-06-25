# Feature Comprehensiveness Rubric

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## What is Feature Comprehensiveness?

Feature comprehensiveness measures whether the product covers the full expected feature set for its format domain. A product can be deeply implemented on the features it has but still be incomplete if entire feature categories are missing.

Comprehensiveness is evaluated WITHIN the context of the format's purpose:
- A spreadsheet format should cover: cells, sheets, types, formulas, styles, rows, columns
- A document format should cover: paragraphs, headings, lists, tables, metadata, styles
- An image format should cover: dimensions, pixels, channels, transforms, conversion
- A compression format should cover: compress, decompress, frame inspection, roundtrip

---

## Scoring Rubric (0–5)

| Score | Criteria |
|-------|----------|
| 0 | No features for the format domain |
| 1 | Only the most minimal feature (e.g., load + get one property) |
| 2 | Core load/save, basic access, no advanced features |
| 3 | Core features covered; advanced features (style, formula, transforms) missing or weak |
| 4 | Core + most advanced features covered; a few domain-specific niche features missing |
| 5 | Full domain coverage; edge cases handled; format-specific advanced features present |

---

## Feature Domain Matrices

### Spreadsheet Comprehensiveness

Expected spreadsheet feature categories:
1. Load/parse (file, stream, bytes)
2. Cell access (get/set, typed values, formulas)
3. Sheet management (add/remove/rename/copy)
4. Row/column operations (add/remove/clear/sort/filter)
5. Cell formatting (style, merge, borders)
6. Export (CSV, HTML, JSON, PDF)
7. Roundtrip verification
8. Error handling (malformed, size guards)
9. Column headers / named ranges

| Product | Load | Cell | Sheets | Row/Col | Format | Export | Roundtrip | Errors | Headers | Score |
|---------|------|------|--------|---------|--------|--------|-----------|--------|---------|-------|
| FODS .NET | 4 | 5 | 5 | 4 | 3 | 5 | 4 | 4 | 5 | **4.3** |
| FODS Python | 4 | 4 | 4 | 3 | 2 | 4 | 4 | 3 | 4 | **3.6** |
| ODS Python | 4 | 3 | 3 | 3 | 1 | 3 | 3 | 2 | 3 | **2.8** |
| GNUMERIC Python | 4 | 3 | 3 | 2 | 1 | 3 | 3 | 2 | 2 | **2.6** |
| SYLK Python | 3 | 3 | 1 | 3 | 0 | 4 | 2 | 1 | 2 | **2.1** |
| DIF Python | 3 | 2 | 1 | 1 | 0 | 1 | 2 | 1 | 1 | **1.3** |
| CSV .NET | 3 | 2 | 1 | 1 | 0 | 1 | 2 | 2 | 3 | **1.7** |
| CSV Python | 3 | 2 | 1 | 1 | 0 | 1 | 2 | 2 | 3 | **1.7** |
| TSV .NET | 3 | 2 | 1 | 1 | 0 | 2 | 2 | 2 | 2 | **1.7** |
| TSV Python | 3 | 2 | 1 | 1 | 0 | 1 | 2 | 2 | 2 | **1.6** |

### Document Comprehensiveness

Expected document feature categories:
1. Load/parse
2. Paragraph CRUD
3. Headings (H1–H6)
4. Lists (ordered/unordered/nested)
5. Tables
6. Text search/replace
7. Metadata (author, title, date, description)
8. Export (text, HTML, Markdown, PDF)
9. Create from scratch
10. Styles/formatting

| Product | Load | Paras | Heads | Lists | Tables | Search | Meta | Export | Create | Styles | Score |
|---------|------|-------|-------|-------|--------|--------|------|--------|--------|--------|-------|
| FODT .NET | 4 | 4 | 4 | 3 | 2 | 3 | 3 | 5 | 4 | 2 | **3.4** |
| FODT Python | 4 | 4 | 3 | 2 | 2 | 3 | 2 | 4 | 4 | 1 | **2.9** |
| ODT Python | 4 | 3 | 2 | 1 | 1 | 1 | 1 | 1 | 3 | 1 | **1.8** |
| ABW Python | 4 | 4 | 0 | 0 | 0 | 1 | 0 | 1 | 3 | 0 | **1.3** |

### Image Comprehensiveness

Expected image feature categories:
1. Load (file, stream, bytes)
2. Dimension access (width, height)
3. Pixel access (get/set individual pixels)
4. Color channels (R/G/B access)
5. Transforms (flip, rotate, resize, crop)
6. Filters (blur, sharpen, grayscale, sepia)
7. Format conversion
8. Save/export
9. Binary format support (P4/P5/P6 for NetPBM)
10. Error/malformed input handling

| Product | Load | Dims | Pixels | Channels | Transforms | Filters | Convert | Save | Binary | Errors | Score |
|---------|------|------|--------|----------|------------|---------|---------|------|--------|--------|-------|
| NetPBM .NET | 5 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 3 | 4 | **4.0** |
| PBM Python | 4 | 4 | 3 | 2 | 0 | 0 | 4 | 3 | 4 | 5 | **2.9** |
| PGM Python | 4 | 4 | 3 | 2 | 0 | 0 | 4 | 3 | 4 | 4 | **2.8** |
| PPM Python | 4 | 4 | 3 | 4 | 0 | 0 | 3 | 3 | 4 | 4 | **2.9** |
| QOI Python | 3 | 3 | 2 | 2 | 0 | 0 | 0 | 3 | 3 | 2 | **1.8** |
| XCF Python | 4 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 2 | **1.2** |

### Compression Comprehensiveness

Expected compression feature categories:
1. Compress string/bytes
2. Decompress bytes
3. Compress file
4. Decompress file
5. Frame inspection (count, header descriptor)
6. Roundtrip verification
7. Level control
8. Stream-based compress/decompress
9. Error handling (bad magic, truncated)

| Product | CmpStr | DcmpStr | CmpFile | DcmpFile | Frame | Roundtrip | Level | Stream | Errors | Score |
|---------|--------|---------|---------|----------|-------|-----------|-------|--------|--------|-------|
| ZST .NET | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 2 | **0.6** |
| ZST Python | 4 | 4 | 3 | 3 | 3 | 4 | 4 | 0 | 2 | **3.0** |

---

## Key Comprehensiveness Gaps

| Gap | Product | Missing Category | Impact |
|----|---------|-----------------|--------|
| No compress/decompress | ZST .NET | compress (1-7) | CRITICAL — product unusable for compression |
| No write | FODP Python | save (all) | HIGH — read-only without documentation |
| No write | XCF Python | save, convert | HIGH — GIMP format unusable for output |
| No transforms | Python image formats | transforms (category 5) | MEDIUM — .NET has full transforms |
| No table ops | ABW Python | tables | LOW |
| No formula eval | All spreadsheets | formula eval | LOW (deferred — requires formula engine) |
| No async APIs | All .NET products | async/await | LOW (enterprise feature) |
