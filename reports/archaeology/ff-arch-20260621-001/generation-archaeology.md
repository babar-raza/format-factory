# Generation Archaeology — ff-arch-20260621-001

## Generation Wave Taxonomy

### Generation 1 — Document/Function-First (No spec model)

**Characteristics:**
- Flat codec/parser/writer modules
- No object model class per spec element
- Returns plain dicts (neutral model) or flat data structures
- Functions named after format (e.g., `parse_fods`, `load_zst`)
- No namespace awareness in class names
- No QName constants in source

**Products using Generation 1:**
- Python: csv, dif, gnumeric, ndjson, odt, pbm, pgm, ppm, qoi, sylk, toml, tsv
- .NET: csv, ndjson, tsv (document-based but no object model)

**Status:** Active. Valuable for FOSS analytics tier. NOT presentable as a professional library
because there is no spec-derived object model.

---

### Generation 2 — DOM-Backed / Format-Prefixed Names

**Characteristics:**
- Format-prefixed class names: `FodsDocument`, `FodsCell`, `FodtDocument`, `FodtParagraph`
- XElement-backed (live DOM mutation) for .NET
- Spec references in XML comments (e.g., "ODF 1.3 §9.4.5")
- Some security hardening (DTD prohibition, file size guard)
- Editable: can Load → Edit → Save
- Names do NOT follow QName hierarchy

**Products using Generation 2:**
- .NET FODS: `FodsDocument`, `FodsCell`, `FodsRow`, `FodsSheet` — fully implemented, ~970 LOC
- .NET FODT: `FodtDocument`, `FodtParagraph`, `FodtBody` — fully implemented, ~978 LOC + model classes
- Python FODT: `FodtDocument`, `FodtParagraph`, `FodtSpan` in `models.py`

**Status:** Active. Functional and demonstrably working (Gate evidence exists). NOT production-ready
because names violate QName canonical standard. Would need Compat/ facades to be presentable.

**Facade requirement:** Per `registry/odf-ontology/qname-to-code-map.yaml`:
- `FodsCell` → should be facade in `Compat/Fods/` delegating to `Table.TableCell`
- `FodtDocument` → should be facade in `Compat/Fodt/` delegating to `Office.Document`
- Currently these ARE the implementation (no canonical target exists)

---

### Generation 3 — Partial QName / Spec-Aware Wrappers

**Characteristics:**
- QName constants embedded (e.g., `QName = "text:p"`, `SpecFactRef = "FACT-FODT-003"`)
- `architecture_only` status — skeleton files, no implementation
- Files generated but not yet wired into production path
- QName registry exists (`shared/qname-registry/fodt.yaml`)
- `compat.py` pattern: routes imports through a switch file

**Products using Generation 3:**
- .NET FODT Spec layer: `Spec/Text/Paragraph.cs`, `Spec/Table/TableCell.cs`, etc. — 10-line stubs
- Python FODT spec layer: `spec/text/paragraph.py`, `spec/table/table_cell.py`, etc. — 7-line stubs
- `shared/qname-registry/fodt.yaml` maps QNames to files with `status: architecture_only`

**Status:** Architecture seeded, NOT implemented. `compat.py` explicitly says:
"DO NOT import from .spec.* until stubs are implemented."

---

### Generation 4 — Live DOM + Spec Identity + Canonical Hierarchy

**Characteristics:**
- Canonical class hierarchy matching spec namespace tree
- Classes like `Table.TableCell` (not `FodsCell`)
- Spec identity metadata embedded
- Canonical classes live in `src/FormatFactory/{Namespace}/{Element}.cs`
- Format-specific facades live in `Compat/{Format}/`
- Python: `{format}/table/table_cell.py`, not `{format}_cell.py`
- No arbitrary LLM-invented names

**Products using Generation 4:** NONE EXIST.

The canonical target paths defined in `registry/odf-ontology/qname-to-code-map.yaml` such as:
- `src/FormatFactory/Table/TableCell.cs`
- `src/FormatFactory/Text/Paragraph.cs`
- `src/FormatFactory/Office/Document.cs`
- `src/python/{format}/table/table_cell.py`

**NONE of these files exist in src/.**

---

## Evidence per Product

### .NET FODS: Generation 2 (confirmed)
- Evidence: `src/net/fods/FodsDocument.cs` line 34: `public sealed class FodsDocument`
- Format-prefixed name. Spec references in comments. Live DOM via XDocument.
- No canonical `Table.TableCell` class exists. `FodsCell` IS the implementation.

### .NET FODT: Generation 2 + Generation 3 skeleton (mixed)
- Evidence: `FodtDocument.cs` is 978-line Generation 2 implementation
- `Spec/Text/Paragraph.cs` is 10-line Generation 3 architecture_only stub:
  ```cs
  // GENERATED — architecture_only
  public static class Paragraph
  {
      public const string QName = "text:p";
      public const string SpecFactRef = "FACT-FODT-003";
  }
  ```
- The Spec/ layer and the Model/ layer coexist without integration.

### Python FODS: Generation 1 (streaming parser with neutral model)
- Evidence: `src/python/fods/fods/fods/parser.py` — iterparse-based, returns dict
- No object model classes. Returns neutral model dict.
- QName constants exist in `constants.py` (e.g., `QN_CELL = "{urn:...}table-cell"`)
- Not truly Generation 3 because QName constants are only used as string matchers, not as class identity

### Python FODT: Generation 1 + Generation 2 + Generation 3 skeleton (mixed)
- Evidence: `parser.py` = Gen 1 (returns neutral model dict)
- `models.py` + `compat.py` = Gen 2 (FodtDocument, FodtParagraph classes)
- `spec/{text,table}/*.py` = Gen 3 skeleton (architecture_only stubs)
- Three generations coexist in the same package. Not yet integrated.

---

## What Produced Each Generation

| Wave | Producer | Evidence |
|------|----------|---------|
| Gen 1 | Autonomous sprint product deepening | `parse_fods`, `load_zst` style functions across all formats |
| Gen 2 | Targeted sprint (DEC-033 Option B) | FodsDocument.cs header says "DEC-033 Option B" |
| Gen 3 (stubs) | Recent FODT pilot sprint (2026-06-20) | Commit `fd0395a7 feat(fodt): add FODT QName registry, Python spec stubs, .NET Spec stubs` |
| Gen 4 | NOT PRODUCED | Does not exist in src/ |

---

## Conclusions

1. Generation waves 1 and 2 dominate all actual source.
2. Generation 3 exists only as architecture stubs for FODT.
3. Generation 4 (canonical spec hierarchy) does not exist anywhere.
4. The QName ontology map DEFINES Gen 4 targets but none are implemented.
5. The `compat.py` pattern is the bridge strategy — FODT has the bridge wired but not activated.
6. No other format has a compat.py or spec/ layer.
