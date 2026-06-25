# Class Segregation Rubric

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## Purpose

Scores the architectural quality of class boundaries within each product. Good class segregation
means each component has a single clear responsibility, components are independently testable,
and no component leaks its implementation details into public API.

---

## Segregation Dimensions (scored 0–5)

### CS-1: Parser/Reader Isolation

Is parsing separate from the public document model? Can you parse without constructing the full model?

| Score | Criteria |
|-------|---------|
| 0 | No parser — document class parses itself in constructor |
| 1 | Parser exists but is tightly coupled to model construction |
| 2 | Parser returns raw data; model wraps it with minimal separation |
| 3 | Parser is separate class; returns intermediate representation |
| 4 | Parser is independently testable; model is built from parser output |
| 5 | Parser implements interface; can be mocked; streaming parser available |

### CS-2: Model/Domain Object Quality

Is the data model a proper domain object or a raw data container?

| Score | Criteria |
|-------|---------|
| 0 | No model — raw dict/List/JsonElement returned directly |
| 1 | Thin named tuple or dataclass with no behavior |
| 2 | Typed properties but no validation or domain methods |
| 3 | Domain methods (GetCell, FilterRows); typed properties; basic validation |
| 4 | Rich domain model; immutable where appropriate; builders provided |
| 5 | Full domain model with spec_qname; validated invariants; factory methods; typed collections |

### CS-3: Writer/Serializer Isolation

Is serialization separate from the model? Can you serialize without the parser?

| Score | Criteria |
|-------|---------|
| 0 | No writer — save is inside model class or not available |
| 1 | Writer is a private method inside the model class |
| 2 | Writer is a static method or standalone function |
| 3 | Writer is a separate class/module |
| 4 | Writer accepts an interface/protocol; can write to stream OR file |
| 5 | Writer implements serialization interface; multiple output formats possible |

### CS-4: Exporter Isolation

Are exporters (format-to-format converters) separate from the core writer?

| Score | Criteria |
|-------|---------|
| 0 | No exporters |
| 1 | Export methods inside model class |
| 2 | Static export functions in same namespace |
| 3 | Separate exporter class per format |
| 4 | Exporter accepts model interface; independently testable |
| 5 | Exporter registry; discoverable; new exporters addable without core change |

### CS-5: Exception Hierarchy

Is there a proper exception hierarchy with a product-specific base exception?

| Score | Criteria |
|-------|---------|
| 0 | Raw framework exceptions propagate (NullReferenceException, KeyError) |
| 1 | Single exception type catches all errors |
| 2 | 2–3 exception types but not hierarchically organized |
| 3 | Base exception + 2–3 specialized subtypes |
| 4 | Base + specialized subtypes + meaningful messages and InnerException |
| 5 | Full hierarchy; exceptions catchable at any level; all include diagnostic context |

### CS-6: Public Facade Clarity

Is there a single clear entry point that a developer finds immediately?

| Score | Criteria |
|-------|---------|
| 0 | No clear entry point; 50+ names at top level |
| 1 | Entry point exists but buried among implementation details |
| 2 | Entry point visible but competing with other classes of similar name |
| 3 | Single clear entry class (e.g. FodsDocument); obvious from module name |
| 4 | Entry class has clear static factory methods (Load, CreateNew) |
| 5 | Entry class + curated __all__ + type stubs + XML doc on all methods |

---

## Class Segregation Scores

| Product | CS-1 | CS-2 | CS-3 | CS-4 | CS-5 | CS-6 | Avg |
|---------|------|------|------|------|------|------|-----|
| FODS .NET | 4 | 5 | 4 | 5 | 4 | 3 | 4.2 |
| FODT .NET | 4 | 4 | 4 | 5 | 4 | 4 | 4.2 |
| NetPBM .NET | 5 | 5 | 5 | 3 | 4 | 4 | 4.3 |
| NDJSON .NET | 4 | 2 | 4 | 3 | 4 | 3 | 3.3 |
| CSV .NET | 3 | 2 | 3 | 1 | 1 | 3 | 2.2 |
| TSV .NET | 3 | 2 | 3 | 3 | 3 | 2 | 2.7 |
| ZST .NET | 3 | 2 | 0 | 0 | 3 | 2 | 1.7 |
| FODS Python | 3 | 3 | 3 | 3 | 3 | 2 | 2.8 |
| FODT Python | 3 | 3 | 3 | 4 | 2 | 2 | 2.8 |
| PBM Python | 4 | 4 | 2 | 3 | 5 | 4 | 3.7 |
| ZST Python | 3 | 3 | 4 | 0 | 2 | 2 | 2.3 |
| FODP Python | 2 | 1 | 0 | 0 | 1 | 1 | 0.8 |

---

## Known Segregation Anti-Patterns in Format Factory

### Anti-Pattern 1: Partial Class Over-Splitting (.NET)
`FodsDocument` is split across `FodsDocument.cs`, `FodsDocumentAccessor.cs`, `FodsDocumentExporter.cs`.
Partial classes hide which methods belong to which responsibility domain.
**Recommended fix:** Keep partial split but add region markers or extract to interfaces.

### Anti-Pattern 2: Raw Model Leakage (NDJSON .NET)
`NdjsonDocument.Records` returns `IReadOnlyList<JsonElement>` — leaks System.Text.Json internal type.
**Recommended fix:** Introduce `NdjsonRecord` wrapper class.

### Anti-Pattern 3: No Writer Segregation (ZST .NET)
No `ZstWriter` class exists — entire write path is absent.
**Recommended fix:** Create `ZstWriter` static class with `Compress`/`Decompress` methods.

### Anti-Pattern 4: Dead Base Class (Python _shared/)
`_shared/_base_codec.py` and `_base_parser.py` exist but no format package inherits from them.
**Recommended fix:** Either delete or adopt consistently across all 20 packages.

### Anti-Pattern 5: Dual API Exposure (FODS Python)
Dict-function API AND class-based API both exported with equal prominence.
**Recommended fix:** Mark dict API as `@deprecated` or move to `fods._compat` internal module.

---

## Segregation Quality Bands

| Avg Score | Band |
|-----------|------|
| 0.0 – 1.5 | Structurally broken |
| 1.5 – 2.5 | Prototype architecture |
| 2.5 – 3.5 | Acceptable POC architecture |
| 3.5 – 4.2 | Professional architecture |
| 4.3 – 5.0 | Exemplary architecture |
