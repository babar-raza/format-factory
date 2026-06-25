# .NET Commercial Product Quality Review Plan

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## Scope

Review all 10 .NET products for commercial readiness:
```
src/net/fods/     src/net/fodt/    src/net/netpbm/
src/net/ndjson/   src/net/csv/     src/net/tsv/
src/net/zst/      src/net/html/    src/net/markdown/  src/net/txt/
```

---

## Product Tiers

### Tier 1 — Primary Commercial Products (highest investment, most tests)
- **FODS** — OpenDocument flat spreadsheet; 16+ source files; 73+ tests; 5 exporters
- **FODT** — OpenDocument flat text; 13+ source files; 65+ tests; 5 exporters
- **NetPBM** — Netpbm image formats (PBM/PGM/PPM); 10+ source files; 65+ tests; transforms/filters

### Tier 2 — Secondary Products (functional but thinner)
- **NDJSON** — NDJSON stream format; 6 source files; 6+ tests; stream API present
- **CSV** — CSV format; 4 source files; 4+ tests; target writer role
- **TSV** — TSV format; 5 source files; 6+ tests; has exporter

### Tier 3 — Incomplete Products
- **ZST** — Zstandard; 3 source files; 2+ tests; NO WRITER (critical gap)

### Tier 4 — Internal Helpers (not standalone products)
- **HTML** — Writer helper for FODS/FODT exporters
- **Markdown** — Writer helper for FODT exporters
- **TXT** — Writer helper for FODT exporters

---

## Review Methodology Per Product

### Step 1: Source Inventory
- Count public classes, methods, properties
- Classify each class by role (Parser/Model/Edit/Writer/Exporter/Exception/Facade)
- Check file count vs logical responsibility split

### Step 2: API Review
- Check all load overloads (file path? stream? bytes? content string?)
- Check edit methods — are they on the Document facade? On model objects? On helper classes?
- Check save methods — stream? file path? atomic?
- Check export methods — what targets? Are they self-contained?
- Score against api-quality-rubric.md

### Step 3: Architecture Review
- Is parser separate from document facade?
- Does the model have typed properties or raw strings/collections?
- Is the writer separate from the model?
- Are exporters separate classes?
- Check partial class boundaries: do they match logical responsibilities?

### Step 4: Feature Review
- Score each feature area (load/edit/save/export) against FA levels
- Score complexity (C levels)
- Check feature comprehensiveness against domain expectations

### Step 5: Exception and Security Review
- Does the product have a custom exception type?
- Do exceptions wrap the original cause?
- Are DTD attacks prevented (FODS/FODT: DTD prohibited + XmlResolver null)?
- Are size guards present?
- Is InvariantCulture used for number parsing?

### Step 6: Test Review
- Count test files
- Check test naming (feature-organized vs sprint-named)
- Check test quality: happy path only? or edge cases + error cases?
- Check roundtrip tests

### Step 7: Packaging Review
- Does README.md exist at `src/net/{format}/`?
- Is PackageId in csproj clean?
- Is PackageDescription accurate (Gate 11 contradiction)?
- Is Version consistent?
- Are PackageAuthor, PackageUrl, Keywords set?

### Step 8: Score and Verdict
- Score all 18 dimensions on 0–5 scale
- Compute weighted commercial readiness score
- Classify: NOT_PRODUCT / DEMO / POC / COMMERCIAL_CANDIDATE / COMMERCIAL_READY

---

## Critical Questions Per .NET Product

### FODS .NET
1. Does `FodsDocument.Load(string filePath)` throw `FodsDocumentException` on malformed XML? (Expected: YES — DTD prohibited)
2. Does `GetColumnHeaders()` return consistent results across 3 overloads?
3. Does `MergeCells()` handle adjacent/overlapping merges?
4. Does `SortRows()` use InvariantCulture for all numeric comparison?
5. Does `Save()` preserve all extended XML namespaces from original file?
6. Is the Gate 11 csproj contradiction addressed?
7. Does `FodsDocumentExporter.cs` (partial 3/3) have distinct responsibilities from `FodsDocumentAccessor.cs`?

### FODT .NET
1. Are Spec/Table/* operations wired to `FodtDocument` public API? (PQ-012)
2. Does `FodtPdfExporter.cs` produce real PDF output or is it a stub?
3. Does `FodtPngExporter.cs` produce real PNG output or is it a stub?
4. Does `AddList()` support nested lists?

### NetPBM .NET
1. Does `NetpbmDocument.LoadStream(Stream)` correctly handle all P1-P6 formats?
2. Does `NetpbmExporter` documentation clearly state it is within-family only?
3. Does `FlipHorizontal()` handle the P4 binary bit-packed format correctly?
4. Are there tests for malformed PBM/PGM/PPM input?

### NDJSON .NET
1. Is `NdjsonDocument.Load(string content)` clearly different from `LoadFile(string path)` in documentation?
2. What happens when `GetAllKeys()` is called on an empty document?
3. Does `Filter()` return a new document or mutate in place?

### ZST .NET
1. Is there ANY compress/decompress capability? (Expected: NO — critical gap)
2. What is the intended use of `ZstDocument.ContentTypeHint`?
3. Is `ZstParser.Parse(byte[])` well-tested?

---

## .NET Review Execution Sequence

1. FODS (Tier 1 — highest priority, most complex)
2. FODT (Tier 1 — similar depth)
3. NetPBM (Tier 1 — unique domain)
4. NDJSON (Tier 2)
5. CSV (Tier 2)
6. TSV (Tier 2)
7. ZST (Tier 3 — critical gap review)
8. HTML/Markdown/TXT (Tier 4 — quick scan)

---

## Files Produced

- `dotnet-product-quality-review-plan.md` (this file)
- `dotnet-product-quality-matrix.json` — scored quality matrix
- `dotnet-commercial-readiness-rubric.md` — scoring rubric
