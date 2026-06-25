# Feature Quality Rubric

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## Purpose

Scores the quality of individual features — not whether a feature exists (that is FA level),
but how well it works when it does exist.

---

## Feature Quality Dimensions

### FQ-1: Correctness

Does the feature produce correct output for valid input?

| Score | Criteria |
|-------|---------|
| 0 | Feature absent or non-functional |
| 1 | Works for trivial cases; fails on basic real data |
| 2 | Works for common cases; fails on edge inputs |
| 3 | Works for most real-world inputs |
| 4 | Works for all tested inputs including edge cases |
| 5 | Mathematically verified or exhaustively tested; handles all format variants |

### FQ-2: Robustness

Does the feature handle invalid, malformed, or unexpected inputs gracefully?

| Score | Criteria |
|-------|---------|
| 0 | Crashes or produces silent wrong results on malformed input |
| 1 | Some inputs cause unhandled exceptions |
| 2 | Most invalid inputs produce some kind of error |
| 3 | Invalid inputs produce meaningful errors with message |
| 4 | Invalid inputs produce typed, catchable exceptions with diagnostic info |
| 5 | All attack vectors handled; DTD injection, oversized input, encoding issues covered |

### FQ-3: Performance

Is the feature performance acceptable for production use?

| Score | Criteria |
|-------|---------|
| 0 | Times out or hangs on real data |
| 1 | Extremely slow (minutes for KB-size data) |
| 2 | Slow but functional for small files only |
| 3 | Acceptable for development use |
| 4 | Suitable for production; handles MB-size files in < 1 second |
| 5 | Streaming support; handles GB-size inputs; memory-efficient |

### FQ-4: Output Fidelity

Does save/export output accurately represent the in-memory model?

| Score | Criteria |
|-------|---------|
| 0 | Output not produced or binary garbage |
| 1 | Output produced but missing major content |
| 2 | Core content present but formatting/structure lost |
| 3 | Most content and structure preserved |
| 4 | Full roundtrip fidelity for common features |
| 5 | Schema-validated output; all format features preserved in roundtrip |

### FQ-5: Compatibility

Does the feature handle format variants and versions?

| Score | Criteria |
|-------|---------|
| 0 | Only handles single hand-crafted test file |
| 1 | Handles one format variant |
| 2 | Handles common format variants |
| 3 | Handles most real-world format variations |
| 4 | Handles format version differences and optional features |
| 5 | Handles all standardized variants; tested against reference test suites |

---

## Feature Quality Scores by Format Domain

### Spreadsheet Domain (FODS, ODS, GNUMERIC, SYLK, CSV, TSV)

| Feature | FODS .NET | FODS Python | ODS Python | SYLK Python | CSV |
|---------|-----------|-------------|------------|-------------|-----|
| Cell read | 5 | 4 | 4 | 3 | 3 |
| Cell write | 5 | 4 | 4 | 2 | 2 |
| Formula | 4 | 3 | 2 | 1 | 0 |
| Multiple sheets | 5 | 4 | 3 | 0 | 0 |
| Cell styles | 4 | 3 | 2 | 0 | 0 |
| Malformed guard | 4 | 3 | 2 | 2 | 2 |

### Document Domain (FODT, ODT, ABW)

| Feature | FODT .NET | FODT Python | ODT Python | ABW Python |
|---------|-----------|-------------|------------|------------|
| Paragraph CRUD | 5 | 4 | 3 | 3 |
| Heading support | 4 | 3 | 2 | 1 |
| Export to HTML | 4 | 4 | 2 | 1 |
| Export to Markdown | 4 | 4 | 1 | 0 |
| Export to plain text | 4 | 4 | 3 | 2 |
| Table support | 1 | 2 | 1 | 0 |
| Malformed guard | 4 | 3 | 2 | 2 |

### Image Domain (NetPBM, PBM/PGM/PPM, QOI, XCF)

| Feature | NetPBM .NET | PBM Python | PPM Python | QOI Python |
|---------|-------------|------------|------------|------------|
| Pixel read | 5 | 4 | 4 | 4 |
| Pixel write | 5 | 3 | 3 | 4 |
| Transform | 4 | 3 | 3 | 2 |
| Format convert | 4 | 4 | 4 | 2 |
| Binary support | 4 | 4 | 4 | N/A |
| Malformed guard | 4 | 5 | 4 | 3 |

### Compression Domain (ZST)

| Feature | ZST .NET | ZST Python |
|---------|----------|------------|
| Decompress | 3 | 4 |
| Compress | 0 | 4 |
| Stream ops | 0 | 3 |
| Roundtrip | 0 | 4 |
| Malformed guard | 3 | 3 |

---

## Feature Quality Summary

**Strongest features:** FODS .NET cell operations (FQ=5), NetPBM .NET transforms (FQ=4-5), PBM Python malformed guard (FQ=5)

**Weakest features:** ZST .NET compress (FQ=0), FODT table support (FQ=1), ABW Markdown export (FQ=0)

**Critical gap:** ZST .NET has FQ=0 for compress/stream/roundtrip — the three most important features of a compression library.
