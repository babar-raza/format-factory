# Public API Review Plan

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## Purpose

This plan defines the systematic method for reviewing the public API surface of every Format Factory product. API quality directly determines developer usability, discoverability, and the chance that a user can successfully use the product without reading the internals.

---

## What "Public API" Means Per Product

### .NET
- All `public` classes, methods, properties, and events in the product namespace
- Only items that would appear in IntelliSense to a consumer
- Extension methods visible through standard `using` directives
- Excludes: `internal`, `private`, `protected internal`, and any `[EditorBrowsable(Never)]` items

### Python
- All names in `__all__` (or all non-underscore names if `__all__` not curated)
- All top-level imports visible after `from {package} import *`
- All items visible in IDE autocomplete after `import {package}` or `from {package} import *`
- Excludes: names starting with `_`; module-type objects after the `_FF_API_EXCLUDE` filter

---

## API Surface Inventory Method

For each product:

1. **Entry point identification**: What is the first thing a developer does? (`FodsDocument.Load()`, `parse_fods()`, `ZstParser.Parse()`)
2. **Namespace/module scan**: List all public classes and top-level functions
3. **Method grouping**: Classify each method into one of: load | edit | save | export | validate | error | utility
4. **Property audit**: Are property names descriptive? Consistent across products?
5. **Overload audit**: Are there stream overloads? File path overloads? Content overloads?
6. **Exception audit**: Do methods throw custom exceptions with meaningful messages? Or raw framework exceptions?
7. **Return type audit**: Consistency — are collections `IReadOnlyList` vs `List`? Null vs empty vs exception?
8. **Discoverability audit**: Can a developer figure out what to do from IntelliSense/autocomplete alone?

---

## API Quality Dimensions (scored 0–5)

| Dimension | What it measures |
|-----------|-----------------|
| **Namespace/Module Quality** | Is the module name clear? Does `import fods` vs `from src.python.fods import *` matter? |
| **Naming Quality** | Are method/property names clear, consistent, and idiomatic? |
| **Discoverability** | Can a developer figure out the API from autocomplete alone without docs? |
| **Workflow Quality** | Does the API support a natural load → edit → save workflow without surprises? |
| **Load API** | Is loading intuitive? Overloads? File vs stream vs bytes? |
| **Edit API** | Are edit operations on the model (not file-based)? Are they chainable? |
| **Save API** | Is saving back to file/stream clear? Roundtrip guaranteed? |
| **Export API** | Can you get to other formats? Are exporter targets clear? |
| **Validation API** | Does the API make invalid states unrepresentable? What error do you get? |
| **Error API** | Are exceptions custom-typed, meaningful, catchable? Do they have good messages? |
| **Consistency** | Do .NET products feel like one family? Python products? Cross-product patterns? |
| **Usability** | Can a developer be productive in 15 minutes without reading source? |

---

## Known API Problems (pre-identified)

### FODS .NET

**PQ-008: No Load(Stream) overload**
- `FodsDocument.Load(string filePath)` — file path only
- `NdjsonDocument.Load(Stream stream)` — has stream support
- Inconsistency across products. FODT also has no stream overload.
- Impact: Cannot use in-memory workflows without temp file

**PQ-018: GetColumnHeaders() static inconsistency**
- Has 3 overloads including a `static` variant
- No other FodsDocument methods are static
- The static overload forces callers to pass the document as a parameter — anti-pattern
- Resolution: evaluate whether static variant should be deprecated

**PQ-006: Gate 11 csproj description contradiction**
- `FormatFactory.Fods.csproj` PackageDescription says "Gate 11 approved 2026-06-05"
- `FodsDocument.cs` header says "Gate 11 status: commercial_readiness_in_progress (NOT approved)"
- A NuGet consumer reading the package description is misled

### NDJSON .NET

**PQ-011: Load() naming ambiguity**
- `NdjsonDocument.Load(string content)` — `content` parameter name suggests it takes content STRING
- `NdjsonDocument.LoadFile(string path)` — `path` parameter name suggests file path
- Confusion: does `Load()` expect the NDJSON text content, or a file path?
- Source confirms: `Load()` takes NDJSON content as string; `LoadFile()` takes file path
- Better names: `LoadFromString()` and `LoadFromFile()` (FODT/FODS pattern: just `Load(filePath)`)

### Python FODS

**PQ-001: Wildcard star-imports**
- `from .parser import *`, `from .neutral_model import *`, etc. in `__init__.py`
- Result: ~50+ names leaked into `fods` namespace
- Developer doing `import fods; fods.<TAB>` sees 50+ items with no grouping
- Many are implementation details (dict manipulation functions) not intended for direct use

**PQ-002: Dual API**
- Dict-function API: `parse_fods(path)` → dict, `workbook_set_cell_value(model, ...)` → mutated dict
- Class API: `FodsDocument(path)`, `.sheets`, `.get_sheet(name)`, `.set_cell(...)`
- Both exported from same `__init__.py` with no guidance on which to use
- The `FodsDocument` class-based wrapper imports both — it's confusing which one IS the API

---

## API Consistency Check Between .NET Products

| Method Group | FODS .NET | FODT .NET | NetPBM .NET | NDJSON .NET | CSV .NET | TSV .NET | ZST .NET |
|-------------|-----------|-----------|-------------|-------------|----------|----------|----------|
| Load(path)  | Yes | Yes | Yes | via LoadFile | via LoadFile | via TsvReader | via ZstParser.Parse |
| Load(Stream)| No | No | Yes (LoadStream) | Yes | No | No | No |
| Load(content/bytes)| No | No | No | Yes (Load) | Yes (Load) | No | Yes (Parse(byte[])) |
| CreateNew() | Yes | Yes | Yes (FromImage) | No | No | No | No |
| Save(path)  | Yes | Yes | Yes | via SaveToFile | via SaveToFile | No | No |
| Custom exception | Yes | Yes | Yes | Yes | No | Yes | Yes |

**Consistency issues:**
- Some products: `Load(filePath)` for file path
- Other products: `LoadFile(filePath)` for file path, `Load(content)` for content string
- No consistent convention across the product family
- ZST.NET is the only product where the document class has no Load or Save at all

---

## API Consistency Check Between Python Products

| Aspect | FODS | FODT | ODS | ODT | PBM | ZST | FODP |
|--------|------|------|-----|-----|-----|-----|------|
| Primary load fn | parse_fods | parse_fodt | load_ods | load_odt | parse_pbm | compress_string | load |
| Primary save fn | write_fods | write_fodt | write_ods | write_odt | (none) | (bytes) | (none) |
| Document class | FodsDocument | FodtDocument | (none) | (none) | PbmImage | ZstDocument | (dict) |
| Edit API style | class method | neutral dict fn | dict mutation | (none) | (none) | (none) | read-only |
| Error type | FodsException | (none) | (none) | (none) | PbmError | (none) | (none) |

**Consistency issues:**
- No common naming convention: `load_fods`, `parse_fods`, `load`, `parse_pbm_strict` — all variations
- Some formats have typed Document classes, some return raw dicts, some return lists
- Exception types only exist for some formats (PBM best practice)
- FODP uses `load()` (same as FODG, ABW) but has no write counterpart — surprising

---

## API Review Execution Method

For each product in this sequence:
1. Read `__init__.py` (Python) or list public members in csproj namespace (C#)
2. Count: how many public names are there? Can a user navigate them?
3. Test the workflow mentally: "I want to load FODS, edit a cell, save" — which methods?
4. Check: is there a stream overload? A bytes overload?
5. Check: what happens if the file doesn't exist? What exception do you get?
6. Check: are return types clear? `string?` vs `string` vs `throw`?
7. Score each dimension 0–5

---

## Files Produced

- `public-api-review-plan.md` (this file)
- `public-api-matrix.json` — scored matrix for all 30 products
- `api-quality-rubric.md` — scoring rubric for API quality dimensions
