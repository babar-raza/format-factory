# Object Model Rubric

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## Purpose

Scores the depth and quality of the domain object model exposed to users. A good object model
makes the format's structure discoverable and navigable through typed properties, not through
raw dictionaries or string-keyed lookups.

---

## Object Model Levels (OM-0 through OM-5)

| Level | Label | Description |
|-------|-------|-------------|
| **OM-0** | Absent | No domain object; returns raw format bytes or nothing |
| **OM-1** | Raw container | Returns untyped dict, List, or byte array |
| **OM-2** | Named tuple / dataclass | Typed fields but no behavior or navigation |
| **OM-3** | Domain object | Typed properties; basic methods; domain vocabulary |
| **OM-4** | Rich domain model | Hierarchical (Document → Sheet → Row → Cell); typed collections; navigation methods |
| **OM-5** | Full domain model | Spec-conformant; typed at every level; mutable; buildable from scratch; factory methods; schema-validated |

---

## Object Model Scoring Dimensions

### OM-D1: Type Coverage

What percentage of the format's structure is represented as typed properties?

| Score | Criteria |
|-------|---------|
| 0 | 0% — raw dict or bytes only |
| 1 | < 20% — top-level only |
| 2 | 20–50% — partial coverage |
| 3 | 50–75% — common fields typed |
| 4 | 75–90% — most structure typed |
| 5 | > 90% — full spec coverage |

### OM-D2: Hierarchy Depth

Does the model represent the format's natural hierarchy (workbook → sheet → row → cell)?

| Score | Criteria |
|-------|---------|
| 0 | Flat dict or single object |
| 1 | One-level hierarchy only |
| 2 | Two-level hierarchy |
| 3 | Three-level hierarchy matching format structure |
| 4 | Four+ levels with typed navigation at each level |
| 5 | Complete hierarchy matching spec; no level collapsed |

### OM-D3: Mutability Model

Can the user build/modify a document from scratch using the API?

| Score | Criteria |
|-------|---------|
| 0 | Immutable DTO — parse only |
| 1 | Some fields settable but no factory method |
| 2 | CreateNew() exists; basic fields settable |
| 3 | CreateNew() + most edit operations available |
| 4 | Full CRUD on all model objects |
| 5 | Builder pattern; fluent API; all format features constructable |

### OM-D4: Collection Semantics

Are collections typed, bounded, and navigable?

| Score | Criteria |
|-------|---------|
| 0 | No collections |
| 1 | Raw List or array — no semantic access |
| 2 | Collections exist; indexable by position |
| 3 | Collections indexable by name AND position |
| 4 | Collections with typed enumerators; LINQ-compatible (.NET) / list comprehension-friendly (Python) |
| 5 | Observable collections with change notifications; immutable snapshots available |

---

## Object Model Scores

### .NET Products

| Product | Model Classes | OM-D1 | OM-D2 | OM-D3 | OM-D4 | Level |
|---------|--------------|-------|-------|-------|-------|-------|
| FODS .NET | FodsDocument, FodsSheet, FodsRow, FodsCell | 4 | 5 | 5 | 4 | OM-4 |
| FODT .NET | FodtDocument, FodtBody, FodtParagraph | 4 | 4 | 5 | 4 | OM-4 |
| NetPBM .NET | NetpbmDocument, NetpbmImage | 5 | 3 | 5 | 4 | OM-4 |
| NDJSON .NET | NdjsonDocument (List<JsonElement>) | 2 | 1 | 2 | 2 | OM-2 |
| CSV .NET | CsvDocument, CsvRecord | 3 | 2 | 2 | 3 | OM-2 |
| TSV .NET | TsvDocument | 2 | 1 | 1 | 2 | OM-1 |
| ZST .NET | ZstDocument (pure DTO) | 2 | 1 | 0 | 1 | OM-1 |

### Python Products

| Product | Model Classes | OM-D1 | OM-D2 | OM-D3 | OM-D4 | Level |
|---------|--------------|-------|-------|-------|-------|-------|
| FODS Python | FodsDocument, FodsSheet, FodsCell | 3 | 4 | 4 | 3 | OM-3 |
| FODT Python | FodtDocument | 3 | 3 | 4 | 3 | OM-3 |
| ODS Python | (dict-based) | 2 | 2 | 3 | 2 | OM-2 |
| ODT Python | (dict-based) | 2 | 2 | 3 | 2 | OM-2 |
| PBM Python | PbmImage dataclass | 4 | 2 | 3 | 3 | OM-3 |
| ZST Python | ZstDocument | 3 | 1 | 2 | 2 | OM-2 |
| NDJSON Python | NdjsonDocument | 3 | 2 | 3 | 3 | OM-3 |
| TOML Python | TomlDocument | 3 | 2 | 3 | 3 | OM-3 |
| SYLK Python | SylkDocument | 2 | 1 | 2 | 2 | OM-2 |
| FODP Python | (raw dict) | 1 | 1 | 0 | 1 | OM-1 |

---

## Object Model Gaps

| Gap | Product | Impact |
|-----|---------|--------|
| NdjsonDocument uses raw JsonElement | NDJSON .NET | Developer must know System.Text.Json API to navigate NDJSON records |
| ZstDocument is pure DTO (no Load/Save) | ZST .NET | User cannot interact with model programmatically |
| FODP returns raw dict | FODP Python | No typed access to presentation structure |
| GNUMERIC returns raw dict | GNUMERIC Python | Cell access requires key string magic |
| No ODS domain class | ODS Python | All operations are dict-mutation; no discoverable API |

---

## Object Model Quality Bands

| Level | Band |
|-------|------|
| OM-0 to OM-1 | Not a domain model |
| OM-2 | Minimal — typed container |
| OM-3 | Practical domain model |
| OM-4 | Professional domain model |
| OM-5 | Exemplary / spec-conformant |
