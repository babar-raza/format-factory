# Product Source Quality Review
# Sprint ID: ff-machinery-readiness-audit-20260621-23d1333

## Rating Scale
- GREEN: Professional, qname-aligned, modular, presentable
- YELLOW: Working but needs cleanup/restructuring
- ORANGE: Useful prototype, not presentable as a library
- RED: Malformed, monolithic, or not aligned to spec
- GRAY: Insufficient evidence

---

## .NET Commercial Products

### FODS (.NET) — src/net/fods/

| Attribute | Assessment |
|-----------|-----------|
| LOC | FodsDocument.cs: 1293, FodsParser.cs: 286, FodsWriter.cs: 56, 8 exporters |
| Modular? | YES — separate files for parser, document, writer, exporters |
| Real object model? | YES — FodsDocument with DOM backing; FodsSheet, FodsRow, FodsCell |
| Classes named after spec? | PARTIAL — uses spec references in XML namespace constants; class NAMES are format-prefixed, not spec-literal (FodsDocument vs Office.Document) |
| Namespace follows spec? | NO — `namespace FormatFactory.Fods`, not `FormatFactory.Office` or `FormatFactory.Table` |
| Parsing separate from model? | YES — FodsParser.cs (read-only parse) + FodsDocument.cs (DOM edit) |
| Error handling professional? | YES — DTD prohibited, XmlResolver disabled, size guard, exception types |
| Public APIs stable? | YES — Load(), Save(), AddSheet(), EditCell() etc. all documented |
| Tests meaningful? | YES — 547 .NET test functions per poc-targets.yaml |
| Documentation present? | YES — XML doc comments, spec references in comments |
| Maintainable? | YES — clear structure, reasonable LOC per file |
| Presentable? | PARTIALLY — works, documented, but naming is not spec-literal |
| Gate status | G11-G approved (commercial_readiness_in_progress, not final) |

**Rating: YELLOW** — Professional working code, not yet spec-literal in naming.

---

### FODT (.NET) — src/net/fodt/

| Attribute | Assessment |
|-----------|-----------|
| LOC | FodtDocument.cs: 977, FodtParser.cs: 320, FodtWriter.cs: 55, 6 exporters |
| Modular? | YES |
| Classes named after spec? | PARTIAL — same pattern as FODS |
| Presentable? | PARTIALLY — clean code, not spec-literal naming |

**Rating: YELLOW**

---

### ZST (.NET) — src/net/zst/

| Attribute | Assessment |
|-----------|-----------|
| Files | ZstDocument.cs, ZstParser.cs |
| Gate status | PREPARATION only, not Gate 11 ready |

**Rating: GRAY** — insufficient direct inspection in this audit pass.

---

## Python FOSS Products

### FODS Python — src/python/fods/fods/

| Attribute | Assessment |
|-----------|-----------|
| LOC | parser.py: 467, writer.py: 182, neutral_model.py: 2194, models.py: 130, constants.py: 56, exceptions.py: 40 |
| Modular? | YES — distinct module files per concern |
| Real object model? | PARTIAL — neutral model uses dicts, not dataclasses/typed models |
| Named after spec? | PARTIAL — functions use `parse_fods`, `workbook_*` prefixes (not spec QNames) |
| Folder structure follows spec? | NO — flat fods/fods/ with no namespace subfolders |
| Neutral model? | YES — 6-entity workbook model (Workbook/Sheet/Row/Cell/Formula/Warning) |
| Tests broken? | YES — 31+ ImportError failures for unimplemented functions |
| Presentable? | YELLOW — solid architecture, broken test suite undermines confidence |
| ANOMALY | Nested `fods/fods/` package structure is non-standard |

**Rating: YELLOW** — Architecture is sound for a functional library but neutral model
uses bare dicts (not typed classes), naming is functional not spec-literal, and the
test suite has 31+ ImportErrors for missing functions.

---

### FODT Python — src/python/fodt/

| Attribute | Assessment |
|-----------|-----------|
| Files | parser.py, writer.py, neutral_model.py (2405 LOC), models.py, constants.py, exceptions.py, compat.py, list_traversal.py |
| Structure | Similar to FODS Python — modular and clean |
| Tests | Small set (compat_bootstrap, compat_e2e, fodt_domain_models, spec_qname_stubs) |

**Rating: YELLOW**

---

### XCF Python — src/python/xcf/

| Attribute | Assessment |
|-----------|-----------|
| xcf_parser.py LOC | 1269 |
| xcf_analytics.py LOC | 5725 — MONOLITH |
| Modular? | NO — analytics file is >5700 lines of arithmetic functions |
| Real object model? | PARTIAL — parser returns object, analytics takes file paths |
| Source quality | Analytics functions are formula variations (no spec backing per MEMORY.md) |
| GOV_BLOCK | Previously triggered GOV_BLOCK:monolith_detection_validator |
| Presentable? | NO — 5725-line analytics file is not presentable |

**Rating: RED** — xcf_analytics.py is a spec-unsupported monolith. Rotation suspended.

---

### ZST Python — src/python/zst/

| Attribute | Assessment |
|-----------|-----------|
| zst_codec.py LOC | 1549 |
| Modular? | PARTIAL — healed from prior monolith (cap was 4210, now 1558 per MEMORY.md) |
| zst_analytics.py | Not directly inspected but referenced in MEMORY.md as 4604 LOC |
| Presentable? | ORANGE — working but not modular enough |

**Rating: ORANGE**

---

### ABW Python — src/python/abw/

| Attribute | Assessment |
|-----------|-----------|
| abw_codec.py LOC | 1503 |
| Modular? | NO — single file |
| Presentable? | ORANGE |

**Rating: ORANGE**

---

### FODG Python — src/python/fodg/

| Attribute | Assessment |
|-----------|-----------|
| fodg_codec.py LOC | 1476 |
| Modular? | NO — single file |
| fodg_analytics.py | Exists (3214 LOC per MEMORY.md) |

**Rating: ORANGE**

---

### CSV Python — src/python/csv/

| Attribute | Assessment |
|-----------|-----------|
| Files | csv_parser.py, csv_writer.py, csv_stats.py |
| Modular? | YES |
| Tests | Large test suite |

**Rating: YELLOW**

---

## Summary Table

| Product | Language | Rating | Key Issue |
|---------|----------|--------|-----------|
| FODS | .NET | YELLOW | Not spec-literal naming, not qname-structured |
| FODT | .NET | YELLOW | Same as FODS .NET |
| ZST | .NET | GRAY | Insufficient inspection |
| FODS | Python | YELLOW | 31+ broken tests, nested package anomaly, dict-based model |
| FODT | Python | YELLOW | Small test suite, newly added |
| XCF | Python | RED | 5725-line analytics monolith |
| ZST | Python | ORANGE | Single large codec file |
| ABW | Python | ORANGE | Single large codec file |
| FODG | Python | ORANGE | Single large codec file |
| CSV | Python | YELLOW | Modular, decent |

## Global Issues Across All Products

1. **No spec QName in class/function names** — all products use format-prefixed flat names
2. **No canonical namespace library** — src/net/FormatFactory/ and src/python/{format}/office/ do not exist
3. **Neutral models use dicts, not typed dataclasses** — makes APIs harder to use and type-check
4. **Analytics functions without spec backing** — suspension of rotation due to GOV_BLOCK
5. **Broken test suite in FODS** — 31 ImportErrors (functions planned but never implemented)
6. **No Compat/ layer** — the intended facade pattern was never created

## What "Working" Means Here

The FODS and FODT products in both .NET and Python are "working" in the sense that:
- They parse real files
- They can create/edit/save documents
- They export to CSV, HTML, PDF, PNG, Markdown etc.
- They have hundreds of tests passing

They are NOT "spec-literal" or "qname-aligned" in the sense that:
- Class names are format-prefixed, not spec-concept-named
- No namespace/folder hierarchy following spec structure
- No `spec_qname` attribute on any class
- No Compat/ layer separating facade from canonical
