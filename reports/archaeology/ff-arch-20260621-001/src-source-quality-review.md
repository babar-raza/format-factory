# Source Quality Review — ff-arch-20260621-001

## .NET Source Quality

### FodsDocument.cs (src/net/fods/FodsDocument.cs)
- LOC: ~970 (too large for a single file — mix of parser, model, exporters)
- Documentation: Excellent XML docs on all public members
- Security: DTD prohibition, file size guard, XmlResolver=null — GREEN
- Error handling: FodsDocumentException hierarchy, never-throw fallback — GREEN
- Spec compliance: ODF spec section refs in comments — YELLOW (section numbers, not SAL IDs)
- Naming: FodsDocument (format-prefixed) — RED per QName standard
- Separation: Parser, model, exporters mixed in one file — ORANGE
- Overall: YELLOW (functional, secure, well-documented; naming/structure not canonical)

### FodsCell.cs (src/net/fods/Model/FodsCell.cs)
- LOC: 74 — appropriate size
- Clear spec references (ODF 1.3 §9.4.5)
- Live DOM mutation through XElement
- Naming: FodsCell (should be Table.TableCell) — RED per QName standard
- Location: src/net/fods/Model/ (should be Spec/Table/) — RED
- Overall: YELLOW (small, focused, correct behavior; wrong name and location)

### FodtDocument.cs (src/net/fodt/FodtDocument.cs)
- LOC: ~978 — too large
- Excellent documentation; secure; well-tested
- Contains: Load, Edit, Save, Export, Search, Statistics, Metadata
- Many duplicate methods (GetWordCount() + WordCount property)
- Naming: FodtDocument (format-prefixed) — RED
- Separation: Everything in one file — ORANGE
- Overall: YELLOW-ORANGE (functional monolith)

### FODT Spec/ stubs (src/net/fodt/Spec/)
- All 10-line architecture_only stubs with QName constants only
- Correct naming (Text.Paragraph, Table.TableCell)
- Correct location (Spec/Text/, Spec/Table/)
- No implementation yet
- Overall: ORANGE (right structure, empty)

---

## Python Source Quality

### fods/parser.py (src/python/fods/fods/fods/parser.py)
- LOC: ~468 — appropriate
- Excellent: iterparse streaming, defusedxml XXE protection, IR reference annotations
- Spec fact annotations on every decision (IR-FODS-001 through IR-FODS-020)
- Clear error hierarchy with parse_errors list
- Neutral model output: clean dict structure
- Names: parse_fods(), parse_fods_strict() — function-only, no class naming issues
- Overall: GREEN (best-quality Python source in the repo)

### fodt/models.py (src/python/fodt/models.py)
- LOC: ~60+
- Clean class hierarchy: FodtDocument, FodtParagraph, FodtSpan
- Property-based API (.text, .kind, .spans, .style_name)
- Naming: FodtDocument (format-prefixed) — ORANGE (should be Office.Document)
- But: compat.py transition plan in place — this is a transitional class
- Overall: YELLOW (clean code; naming is acknowledged transitional issue)

### fodt/compat.py (src/python/fodt/compat.py)
- LOC: 23 — minimal switch file
- Excellent: documents exactly when to switch; clear bootstrap rules
- Architecture-aware: knows about spec/ stubs and when to activate them
- Overall: GREEN (excellent design for a transition file)

### fodt/spec/text/paragraph.py
- LOC: 6 — skeleton only
- Has: spec_qname = "text:p", spec_fact_ref = "FACT-FODT-003"
- Has: TODO comment about implementation
- Correct canonical class name (Paragraph, not FodtParagraph)
- Overall: ORANGE (right structure; empty)

### xcf/xcf_parser.py + xcf_analytics.py
- Source healed: xcf_parser.py 1301/3997 LOC cap
- Analytics extraction demonstrated correct pattern
- No spec-alignment (binary format)
- Overall: YELLOW

### zst/zst_codec.py + zst_analytics.py
- Source healed: zst_codec.py 1558/4210 LOC cap
- Same pattern as XCF
- Overall: YELLOW

---

## Cross-Cutting Quality Issues

| Issue | Severity | Formats Affected |
|-------|----------|-----------------|
| Monolithic files (all in one) | MEDIUM | FodsDocument.cs, FodtDocument.cs |
| Format-prefixed class names | HIGH | All .NET + Python FODT models |
| Duplicate API surface | LOW | FodtDocument WordCount/GetWordCount |
| Missing object model (dict only) | HIGH | Python FODS |
| Triple nesting structural defect | BLOCKER | Python FODS |
| Committed build artifacts | MEDIUM | All Python packages |
