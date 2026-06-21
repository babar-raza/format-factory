# Gate 11 Readiness Review — ff-arch-20260621-001

## Gate 11 Definition

Gate 11 is the commercial release gate. Criteria: C1-C20 (.NET), P1-P11 (Python).
Only Babar Raza can approve Gate 11 execution.

**Current status: NOT approved for any format.**

---

## FODS Gate 11 Readiness

### .NET FODS (FormatFactory.Fods)

| Criterion | Status | Evidence |
|-----------|--------|---------|
| C1: Load | Green | FodsDocument.Load() — DOM-backed, secure, tested |
| C2: Edit | Green | SetText(), SetCellValue() — tested |
| C3: Save (same-format) | Green | FodsDocument.Save() — round-trip tested |
| C4: Export CSV | Green | FodsCsvExporter.cs |
| C5: Export HTML | Green | FodsHtmlExporter.cs |
| C6: Export JSON | Green | FodsJsonExporter.cs |
| C7: Export ODS | Green | FodsOdsExporter.cs |
| C8: Export PDF | Green | FodsPdfExporter.cs |
| C9: Export PNG | Green | FodsPngExporter.cs |
| C10: Error handling | Green | FodsDocumentException hierarchy |
| C11: Security hardening | Green | DTD prohibition, file size guard |
| C12: QName compliance | RED | FodsCell NOT canonical Table.TableCell |
| C13: Spec hierarchy folder | RED | src/net/fods/Model/ not spec-hierarchy |
| C14: Canonical naming | RED | FodsCell, FodsSheet not canonical |
| C15-C20: Commercial packaging | Gray | Not audited in depth |

**Overall: NOT ready for C12-C14. QName compliance is a hard blocker.**

### Python FODS

| Criterion | Status | Evidence |
|-----------|--------|---------|
| P1: Load | Green | parse_fods() — streaming, tested |
| P2: Edit | Yellow | Dict-level only, no object model |
| P3: Save | Green | write_fods() — tested |
| P4: Package | Yellow | Installed but triple nesting bug |
| P5-P11: Various | Gray | Analytics heavy; spec model not present |

**Overall: NOT ready. Triple nesting is a structural defect. No object model.**

---

## FODT Gate 11 Readiness

### .NET FODT (FormatFactory.Fodt)

Similar to FODS: Load, Edit, Save, Export all work. Same QName compliance blockers.
Spec/ stubs exist but are architecture_only. FodtDocument/FodtParagraph are Gen 2 naming.

**Status: NOT ready (same C12-C14 blockers as FODS)**

### Python FODT

Better than FODS Python: models.py provides object model, compat.py has transition plan.
Spec/ stubs are architecture_only — not wired.

**Status: NOT ready (QName compliance incomplete)**

---

## Products Closest to Gate 11

Ordered by readiness:

1. **.NET FODS** — Most feature-complete (.NET commercial). Blocks on QName compliance (C12-C14).
   Minimal work needed if QName compliance requirement is waived (it MUST NOT be waived).

2. **.NET FODT** — Close second. Similar feature set to FODS. Same QName compliance gaps.

3. **Python FODS** — Good FOSS foundation. Needs triple nesting fix + object model before Gate 11.

4. **Python FODT** — Spec migration path clearer than FODS Python.

---

## What Must Be Fixed Before Gate 11 Is Viable

1. QName compliance: canonical class names in `Spec/` or `src/FormatFactory/`
2. Compat/ facades correctly delegating to canonical classes
3. Source hygiene: triple nesting fixed (FODS Python)
4. Object model: FodsCell/FodsSheet etc. are facades, not primary implementation
5. Gate 11 readiness packet: must be prepared by agent, reviewed by Babar Raza

---

## Products Best Suited for Spec-to-Library-to-Export Proof

**FODT (both .NET and Python)** because:
- Spec/ stub layer already exists (architecture_only but in place)
- `compat.py` bridge ready for Python
- Simpler object model than FODS (paragraphs and headings vs full spreadsheet)
- Export pipeline complete (HTML, Markdown, TXT, PDF, PNG)
- QName registry (`shared/qname-registry/fodt.yaml`) is the most complete

**FODS (.NET)** is the most feature-complete but has more complex spec hierarchy to align.
