# Source Quality Review

**Sprint:** forensics-archaeology-20260621

---

## Scoring System

- **Green:** Professional, qname-aligned, production-presentable
- **Yellow:** Working, functional, needs cleanup to be presentable
- **Orange:** Useful prototype but not presentable to external audience
- **Red:** Malformed, non-aligned, or structurally problematic

---

## Python Packages

### fods — Yellow (3,914 LOC, 35 files)

**Strengths:**
- Neutral model with formal schema (Gate 5 passed)
- Spec stubs in spec/ with spec_qname and spec_fact_ref
- Compat/ facade layer started
- models.py classes have spec_qname
- Strong exception hierarchy
- 4987 SAL facts available

**Weaknesses:**
- parser.py returns dicts, not spec stub instances (not wired to Compat/)
- writer.py status uncertain (may be incomplete)
- fods/fods/ duplicate spec directory needs removal
- Two parallel object hierarchies (models.py + Compat/) can diverge

**Production readiness:** Python FOSS track — read-only, exportable to CSV

### fodt — Yellow (4,525 LOC, 21 files)

**Strengths:**
- Neutral model formal (Gate 5 passed)
- Spec stubs in spec/ with 8 classes
- models.py functional
- list_traversal.py shows depth in list handling
- 4933 SAL facts

**Weaknesses:**
- models.py classes (FodtSpan, FodtParagraph, FodtDocument) MISSING spec_qname
- No Compat/ layer yet
- No write capability

**Production readiness:** Similar to FODS Python — read-only

### ods — Orange (2,487 LOC, 5 files)

**Strengths:** Has writer (ods_writer.py), CSV exporter, stats module
**Weaknesses:** OdsDocument/OdsSheet/OdsRow/OdsCell have no spec_qname; 1066 SAL facts unused
**Production readiness:** Functional but not spec-aligned

### odt — Orange (981 LOC, 2 files)

**Strengths:** Parser handles Odt containers
**Weaknesses:** Only parser.py + pyproject.toml; no spec_qname; no writer
**Production readiness:** Parse-only prototype

### csv — Orange (1,843 LOC, 5 files)

**Strengths:** Parser + writer + stats + analytics; complete CRUD
**Weaknesses:** No domain class, no spec_qname, 0 SAL facts
**Production readiness:** Functional utility library; not spec-shaped

### xcf — Orange (7,022 LOC, 3 files)

**Strengths:** Parser works; analytics module
**Weaknesses:** 7022 LOC total (monolith risk at cap); no spec_qname; 0 SAL facts; XcfImage class uninspected
**Production readiness:** Prototype — monolith structure blocks deepening

### zst — Orange (7,130 LOC, 3 files)

**Strengths:** Codec works (compress/decompress); analytics module
**Weaknesses:** 7130 LOC at cap; no spec_qname; only 94 SAL facts
**Production readiness:** Functional but not spec-shaped

### fodg — Red/Orange (6,421 LOC, 3 files)

**Strengths:** Parser/encoder works
**Weaknesses:** 6421 LOC (near cap); no spec_qname; 0 SAL facts; analytics rotation suspended
**Production readiness:** Prototype; deepening blocked

### Others (dif, sylk, abw, gnumeric, fodp, pbm, pgm, ppm, qoi, ndjson, tsv, toml) — Orange

Functional parsers but all lack spec_qname, have no spec stubs, and most have no SAL facts.
All are Generation 1 code — format-prefixed names, monolithic parsers.

---

## .NET Packages

### FormatFactory.Fods — Yellow/Green (1,579+ LOC)

**Strengths:**
- FodsDocument: DOM-backed, load/edit/save/reload verified (611 tests)
- Security guards (DTD prohibited, 50MB limit, XmlResolver disabled)
- Multiple exporters (CSV, HTML, JSON, PDF, ODS, PNG)
- Spec/ directory with namespace-organized stubs
- Model/ directory with FodsSheet, FodsRow, FodsCell
- ODF spec citations in XML documentation
- FodsParser.cs streaming parser (alternative to DOM for large files)

**Weaknesses:**
- Spec/ stubs don't have spec_qname XML attribute equivalent
- Class names are format-prefixed (FodsDocument, FodsSheet) rather than canonical
- Some exporters are placeholder implementations (PDF, PNG likely minimal)

**Professional presentation:** GOOD — could be shown to external audiences with minor cleanup

### FormatFactory.Fodt — Yellow/Green

Similar to FODS .NET. Strong read/write/export suite.

### FormatFactory.Csv, FormatFactory.Ndjson, FormatFactory.Tsv — Yellow

Clean CRUD pattern (Document + Reader + Writer). No spec_qname but well-structured.
These are correctly simple (simple tabular formats → simple implementations).

### FormatFactory.Zst — Orange

Parse-only with basic document class. Limited depth.

### Html, Markdown, Txt writers — Orange

Writer-only stubs. Export target implementations, not full format libraries.

---

## Overall Source Quality Summary

| Rating | Python Packages | .NET Packages |
|--------|----------------|--------------|
| Green | 0 | 0 |
| Yellow | 2 (fods, fodt) | 2 (fods, fodt) |
| Orange | 17 | 7 |
| Red | 1 (fodg — near GOV_BLOCK) | 0 |

**The system produces Orange-quality output for most formats.** Only FODS and FODT have
begun the journey toward professional, spec-aligned, production-quality libraries. The gap
between "functional prototype" (Orange) and "professional library" (Green) is substantial
and requires the machinery repairs documented in this sprint.
