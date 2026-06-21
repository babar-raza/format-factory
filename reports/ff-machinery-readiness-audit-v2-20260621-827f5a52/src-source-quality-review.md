# Source Quality Review — Format Factory Machinery Audit v2
# Sprint ID: ff-machinery-readiness-audit-v2-20260621-827f5a52

## Review Criteria

For each product:
- Modularity and separation of concerns
- Real object model
- Class naming (spec-aligned vs. invented)
- Namespace/folder alignment
- Parsing / model / serialization / export separation
- Error handling
- Public API stability
- Test coverage
- Documentation
- Maintainability
- Professional library appearance

Rating Scale:
- Green: professional and qname-aligned
- Yellow: working but needs cleanup or naming alignment
- Orange: useful prototype but not presentable as a library
- Red: malformed, monolithic, or spec-misaligned
- Gray: not enough evidence

---

## FODS .NET (src/net/fods/) — YELLOW

Evidence: FodsDocument.cs (1293 LOC), FodsParser.cs, FodsWriter.cs, Model/ (FodsCell, FodsRow, FodsSheet)

### What the code proves:
- Load → edit → save → reload (C4-C7) vertical slice WORKS
- 30 public methods: Load, CreateNew, Save, AddSheet, RemoveSheet, SetCellValue, Export*
- DOM-backed with XDocument; DTD prohibited; file-size guard (50 MB default)
- Error handling: typed exceptions, security posture documented in comments
- ODF spec basis documented in XML comments (§3.1.2, §3.7, §9.4.2 etc.)
- Separate model classes FodsCell/FodsRow/FodsSheet with clear responsibilities
- Multiple exporters: CSV, HTML, JSON, ODS, PDF stub, PNG stub

### What's missing:
- Class naming: `FodsDocument` (format-prefixed) not `Office.Document` (spec-shaped)
- Namespace: `FormatFactory.Fods` not `FormatFactory.Fods.Office`
- NO spec_qname or canonical QName attribute in production class
- Spec/ stubs are `architecture_only` TODOs — production doesn't inherit from them
- FodsCell.cs has `string Value`, `int ColumnSpan` — working but not spec-literal property names
- Gate 11 status comment says "NOT release-ready" — honest self-assessment
- Export stubs (PDF, PNG) are referenced but not fully implemented

### Maintainability: HIGH for current scope
The code is well-structured C#, easy to follow, with clear comments referencing ODF sections.
A human .NET developer could maintain it. It does NOT look generated.

### Verdict: Yellow — Professional working library, not spec-shaped

---

## FODS Python (src/python/fods/) — YELLOW

Evidence: neutral_model.py (2186 LOC, modified), parser.py, writer.py, models.py

### What the code proves:
- Full parse → edit → save cycle working (44 passing tests)
- Rich public API: 25+ functions in __init__.py
- Security: parse_fods() never raises; parse_fods_strict() raises typed errors
- Spec/ stubs (15 classes) with spec_qname created

### What's missing:
- neutral_model.py: 2186 LOC monolithic model file — not modular
- Production API uses format-prefixed names (parse_fods, write_fods) — acceptable for facade
- 32 test collection errors (analytics functions not in __init__.py)
- Compat/ facades created but UNTRACKED (will be lost)
- models.py and neutral_model.py are parallel model representations — redundancy
- No clear separation: where does model end and serialization begin?

### Source quality issues:
- neutral_model.py is dirty (modified, uncommitted) — risky state
- The analytics functions referenced in 32 test files do not exist in the package
  (fods_cell_value_variance, etc.) — tests from suspended rotation left stranded

### Verdict: Yellow — Working but has organizational debt and test failures

---

## FODT Python (src/python/fodt/) — YELLOW

Evidence: neutral_model.py (1916 LOC), parser.py, writer.py, fodt_analytics.py, spec/ (8 classes)

### What the code proves:
- Parse → extract → save cycle
- Richer than most FOSS formats
- Analytics split into fodt_analytics.py (separate file)
- spec/ stubs (8 classes) COMPLIANT

### What's missing:
- No Compat/ layer
- neutral_model.py at 1916 LOC is large
- Same analytics function naming convention as FODS

### Verdict: Yellow — similar to FODS Python

---

## ZST Python (src/python/zst/) — Orange

Evidence: zst_codec.py (1549 LOC), zst_analytics.py (4604 LOC), __init__.py (810 LOC)

### Key issues:
- zst_analytics.py at 4604 LOC — exceeds any reasonable LOC cap
- No spec/ stubs (RFC 8878/9659 not processed)
- Analytics rotation suspended — large analytics file is dead weight
- No qname structure
- The main codec is reasonable but the analytics bloat is a problem

### Verdict: Orange — functional codec buried under analytics monolith

---

## XCF Python (src/python/xcf/) — Red

Evidence: xcf_parser.py (1269 LOC), xcf_analytics.py (4773 LOC)

### Key issues:
- xcf_analytics.py at 4773 LOC — monolith, rotation suspended
- GOV_BLOCK:monolith_detection_validator will fire
- No spec/ stubs
- XCF has no publicly available spec — spec backing is impossible
- Prior audit rated this Red; no change

### Verdict: Red — analytics monolith, no spec backing

---

## FODG/FODP Python (src/python/fodg/, src/python/fodp/) — Orange

Evidence: fodg_codec.py (3176 LOC), fodg_analytics.py (3214 LOC)

### Key issues:
- fodg_codec.py at 3176 LOC — at cap
- Analytics rotation suspended
- No spec/ stubs
- ODF Drawing/Presentation formats but no canonical class structure

### Verdict: Orange

---

## ABW/DIF/ODS/ODT/CSV Python — Gray

Evidence: src/python/{format}/__init__.py (199-220 LOC each)

### Key issues:
- Single-file codecs, minimal implementation
- No object model, no spec hierarchy
- Working for basic parse operations
- No tests or very minimal tests

### Verdict: Gray — basic FOSS stubs, not production libraries

---

## .NET FODT (src/net/fodt/) — Yellow

Evidence: FodtDocument.cs, FodtParser.cs, FodtWriter.cs, Model/ (FodtParagraph, FodtBody), Spec/ (architecture_only)

### Key issues:
- Similar to FODS .NET — working library with format-prefixed class names
- Spec/ stubs are architecture_only
- Several exporters (HTML, Markdown, TXT, PDF, PNG)

### Verdict: Yellow — same rating as FODS .NET

---

## Summary Table

| Product | Rating | Primary Issue |
|---------|--------|--------------|
| FODS .NET | Yellow | Not spec-shaped naming, Spec/ stubs are architecture_only |
| FODT .NET | Yellow | Same as FODS .NET |
| FODS Python | Yellow | 32 test errors, neutral_model.py dirty/untracked facades |
| FODT Python | Yellow | No Compat/ layer, large neutral_model.py |
| ZST Python | Orange | 4604 LOC analytics monolith |
| XCF Python | Red | 4773 LOC analytics monolith, no spec |
| FODG Python | Orange | At LOC cap, rotation suspended |
| ABW/DIF/ODS etc. | Gray | Minimal stubs only |
| CSV/TSV/NDJSON .NET | Gray | Simple readers/writers, no qname |

---

## Source Quality vs. Claim Assessment

The prior audit said "ZERO products have qname-structured namespaces, canonical classes, or Compat/ facades."

Current state (UPDATED):
- FODS Python spec/ stubs: CREATED (15 classes, COMPLIANT) — IMPROVEMENT
- FODS Python Compat/ facades: CREATED but UNTRACKED — PARTIAL IMPROVEMENT
- FODT Python spec/ stubs: CREATED (8 classes, COMPLIANT) — IMPROVEMENT
- .NET Spec/ stubs: architecture_only placeholders — NOT real QName implementation
- Production code still uses format-prefixed names everywhere
- No production code inherits from or connects to spec/ classes

The improvements are meaningful scaffolding but NOT production-ready QName compliance.
