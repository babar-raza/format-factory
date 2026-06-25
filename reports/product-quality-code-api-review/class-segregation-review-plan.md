# Class Segregation Review Plan

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## Purpose

Class segregation measures whether code responsibilities are properly divided among distinct classes with single responsibilities. Poor segregation produces God Classes (one class does everything), blurs module boundaries, and makes the codebase hard to test and maintain.

---

## Required Component Boundaries Per Product

For every format product, these components should exist as distinct units:

| Component | Responsibility | .NET Pattern | Python Pattern |
|-----------|---------------|--------------|----------------|
| **Parser/Reader** | Convert file/bytes/stream to in-memory model | `FodsParser.cs` | `fods_parser.py` |
| **Model Objects** | Domain-specific typed data containers | `FodsSheet.cs`, `FodsCell.cs` | `FodsCell`, `FodsSheet` dataclass |
| **Edit Operations** | Mutations on the model | `FodsDocument.SetCellValue()` | `workbook_set_cell_value()` |
| **Writer/Serializer** | Convert in-memory model back to file format | `FodsWriter.cs` | `write_fods()` |
| **Exporter/Converter** | Convert to a DIFFERENT file format | `FodsCsvExporter.cs` | `csv_exporter.py` |
| **Validation** | Check format invariants | DTD check in parser | `parse_fods_strict()` |
| **Exceptions** | Custom error types | `FodsDocumentException.cs` | `FodsException` |
| **Public Facade** | Clean entry point hiding internal complexity | `FodsDocument.cs` (partial class) | `FodsDocument` class in `models.py` |
| **Package Entry** | Module/namespace entry point | `FormatFactory.Fods` namespace | `__init__.py` |

---

## Class Segregation Anti-Patterns to Flag

### God Class
A single class with 10+ unrelated responsibilities. In Format Factory context:
- `FodsDocument` doing parsing + editing + saving + exporting all in one class
- Even as a facade, if it directly contains all logic (not delegating), it's a God Class

### Partial Class Overuse
- .NET: `partial class` is legitimate for splitting large classes across files
- Anti-pattern: partial class splits that don't correspond to any logical boundary
  (e.g., FodsDocument.cs / FodsDocumentAccessor.cs / FodsDocumentExporter.cs — does the boundary match responsibilities?)

### Dead Base Class
- Base class defined but not used by any concrete class
- Format Factory risk: `_shared/_base_codec.py` and `_base_parser.py` in Python `_shared/`

### Architecture-Only Stubs Masquerading as Implementation
- `Spec/` and `Compat/` files with only `pass` or `# GENERATED — architecture_only`
- These exist for spec-parity tracking but are NOT behavioral implementations
- Risk: they inflate the apparent class count without providing functionality

### Leaking Internal Types
- Parser returns internal types that the user must also import
- Example: if `FodsParser.Parse()` returns `XDocument` instead of `FodsDocument`
- Python: if `parse_fods()` returns `lxml.etree._Element` instead of `FodsDocument`

### Neutral Model Ambiguity (Python)
- Dict-based neutral model (returned by parser) vs class-based model (wrapping the dict)
- Both exported at top level with no clear separation
- User doesn't know which to use

---

## Architecture Review Per Product

### FODS .NET

**File split:**
- `FodsDocument.cs` (partial 1/3): Core load/save/create + cell/sheet/row operations
- `FodsDocumentAccessor.cs` (partial 2/3): Query methods (GetRowCount, FilterRows, ExportSheetToHtml)
- `FodsDocumentExporter.cs` (partial 3/3): Export orchestration

**Assessment:**
- The partial class split is reasonable: document lifecycle in file 1, queries in file 2, exports in file 3
- BUT: having `ExportSheetToHtml()` in the accessor file and `FodsHtmlExporter.cs` as a separate class — which is the real home of export logic?
- The `Spec/` stubs (Document.cs, Table/TableCell.cs, Table/TableRow.cs) are architecture-only markers, not behavioral code

**Score estimate:** 3/5 (reasonable split, minor boundary blur)

### FODT .NET

Similar structure to FODS. 2-file partial class split instead of 3.
`Spec/Text/` and `Spec/Table/` stubs present but architecture-only.

**Score estimate:** 3/5

### NetPBM .NET

**File split:**
- `NetpbmDocument.cs`: Public facade
- `NetpbmImage.cs` (partial 1/4): Core image model
- `NetpbmImageAnalyzer.cs` (partial 2/4): Analytics methods
- `NetpbmImageFilters.cs` (partial 3/4): Filter operations
- `NetpbmImageTransforms.cs` (partial 4/4): Transform operations

**Assessment:**
- This is the BEST class segregation in the project
- Each partial split corresponds to a meaningful functional domain
- Parser, Writer, Exporter all separate classes
- Model (NetpbmImage) clearly separated from Document facade

**Score estimate:** 4/5

### NDJSON .NET

- `NdjsonDocument`: Model + facade (holds List<JsonElement>)
- `NdjsonReader`: Parse
- `NdjsonWriter`: Serialize
- `NdjsonCsvExporter`: Export

**Assessment:**
- Good separation of concerns at the class level
- The model itself is shallow (raw JsonElement list) — not a class segregation issue, but an object model depth issue
- Facade pattern is clear

**Score estimate:** 4/5 (good separation, shallow model is separate concern)

### Python FODS

**Architecture components:**
- `parser.py`: XML → neutral model dict (well-separated)
- `writer.py`: neutral model dict → FODS XML (well-separated)
- `neutral_model.py`: dict manipulation functions
- `models.py`: FodsDocument/FodsSheet/FodsCell thin wrappers over neutral model
- `spreadsheet_document.py`: Another spreadsheet facade
- `spreadsheet_model_document.py`: Yet another facade
- `Compat/FodsDocument.py`: Architecture-only stub (not behavioral)
- `Spec/`: Architecture-only stubs

**Assessment:**
- Parser and writer well-separated — good
- MULTIPLE competing facades (models.py, spreadsheet_document.py, spreadsheet_model_document.py) — this is a class segregation violation
- The dual-API problem (PQ-002) is a direct consequence of this multi-facade architecture
- `Compat/` stubs are intentional architecture markers, not a problem per se, but they add to apparent complexity

**Score estimate:** 2/5 (multiple competing facades, unclear primary model)

### Python _shared/

`src/python/_shared/_base_codec.py` and `_base_parser.py` exist.
Most format packages do NOT inherit from these base classes.
This is a dead abstraction — allocated space for a pattern that wasn't applied (PQ-016).

**Score estimate for base class usage:** 1/5

---

## Component Boundary Map Summary

| Product | Parser | Model | Edit | Writer | Exporter | Validation | Exception | Facade | Entry |
|---------|--------|-------|------|--------|----------|------------|-----------|--------|-------|
| FODS .NET | Separate | Separate | Facade | Separate | Separate | In-parser | Separate | Partial class | namespace |
| FODT .NET | Separate | Separate | Facade | Separate | Separate | In-parser | Separate | Partial class | namespace |
| NetPBM .NET | Separate | Partial×4 | Partial | Separate | Separate | In-parser | Separate | Separate | namespace |
| NDJSON .NET | Reader | Thin DTO | None | Writer | Separate | In-reader | Separate | Facade | namespace |
| CSV .NET | Reader | Thin | None | Writer | None | In-reader | None | Facade | namespace |
| TSV .NET | Reader | Thin | None | Writer | Separate | In-reader | Separate | None | namespace |
| ZST .NET | Parser | Pure DTO | None | MISSING | None | In-parser | Separate | None | namespace |
| FODS Python | Separate | Multi-facade | In-facade | Separate | Separate | In-parser | Separate | Multi | __init__ |
| FODT Python | Separate | Single | Separate file | Separate | Separate | In-parser | None | Single | __init__ |
| PBM Python | Separate | Dataclass | None | In-parser | Cross-format | In-parser | Hierarchy | None | __init__ |
| FODP Python | Codec-all | Dict | None | MISSING | None | In-codec | None | None | __init__ |

---

## Scoring Method

Each dimension rated 0–5:

- **Facade quality**: Does the primary public object clearly represent the document/format?
- **Parser separation**: Is parsing separate from the model? From the facade?
- **Model depth**: Are model objects typed with meaningful properties? Or raw dicts/lists?
- **Writer separation**: Is serialization separate from the model?
- **Exporter separation**: Are cross-format conversions clearly separate?
- **Validation separation**: Is validation logic clearly identifiable?
- **Exception model**: Custom hierarchy? Meaningful?
- **Class cohesion**: Does each class have a single clear responsibility?
- **Duplication risk**: Are there multiple classes doing the same thing?
- **God class risk**: Is any single class too large or responsible for too much?
- **Internal leakage**: Are internal implementation types exposed in the public API?
- **Maintainability**: Can a developer understand and modify the codebase without surprises?
