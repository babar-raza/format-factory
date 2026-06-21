# Product Deepening Readiness Plan — ff-arch-20260621-001

## Current Assessment

**NOT READY for unrestricted product deepening.** Targeted, governed product deepening
may continue for .NET FODS and FODT after three machinery repairs complete.

---

## What Is Safe To Continue (Now)

The following product deepening is SAFE even before machinery repairs:

1. **.NET FODS exports** (additional export formats): These don't introduce new class names.
   They create exporter classes (FodsPdfExporter, etc.) which are utility classes, not spec model.

2. **.NET FODT text operations**: AppendParagraph, InsertHeading, GetDocumentStats, etc.
   These operate through existing FodtDocument (Gen 2) API. Don't introduce naming violations.

3. **Python FODS analytics**: Existing neutral-model analytics functions (not new analytics classes).
   TC-GUARD-001 ensures gap_ledger_ref required.

4. **Python FODT**: Additional parser capabilities through neutral model.

---

## What Is NOT Safe Until Machinery Repairs

1. **New object model classes**: Cannot add new FodsXxx classes without a canonical target
2. **New Python package structures**: FODS triple nesting must be fixed first
3. **Analytics function bulk generation**: V42 blocks _mod_N_times_M; TC-GUARD-001 requires spec_fact_refs
4. **New formats entering spec-to-library pipeline**: SAL must produce sal-facts-latest.json first

---

## Gated Deepening Plan

### Gate A: Source Hygiene (Required first)
- TC-HYGIENE-FODS-001 complete
- V43 validator active
- Skills updated with QName enforcement

**After Gate A:** Product deepening may add new APIs to .NET FODS/FODT using canonical names only

### Gate B: Canonical Spec Classes Exist (Required second)
- TC-QNAME-CANONICAL-001 complete (FODS Spec/ stubs created)
- TC-QNAME-FODT-SPEC-IMPL-001 complete (FODT spec/ implemented)

**After Gate B:** Object model deepening may proceed; new classes go to Spec/ not Model/

### Gate C: Backfill Complete
- TC-QNAME-BACKFILL-FODS-001 complete (FodsCell is facade)

**After Gate C:** Gate 11 QName compliance criteria (C12-C14) can be claimed

### Gate D: SAL Pipeline Connected
- TC-SAL-OUTPUT-001 complete
- TC-FEATURE-COMPILER-CODEGEN-001 complete

**After Gate D:** New format additions can follow spec-to-library path automatically

---

## Products Recommended for Next Product Deepening Pilot

After Gate A complete:

**Pilot 1: FODT Python — complete spec/ migration**
- Implement Text.Paragraph, Text.Heading, Text.Span, Text.List in spec/
- Switch compat.py
- Run pilot: parse FODT → Text.Paragraph objects → export HTML
- Evidence: test_compat_bootstrap.py + integration test

**Pilot 2: FODS .NET — add canonical TableCell**
- Create Spec/Table/TableCell.cs (implemented, not stub)
- Create Compat/Fods/FodsCell.cs facade
- Run pilot: load FODS → Table.TableCell objects → edit → save → verify roundtrip
- Evidence: canonical object model used end-to-end
