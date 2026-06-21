# Final Verdict

**Sprint:** forensics-archaeology-20260621
**Date:** 2026-06-21
**Investigator:** Claude Sonnet 4.6 (forensic archaeology mode)

---

## VERDICT: READY_AFTER_TARGETED_MACHINERY_REPAIRS

The system is NOT ready for broad product deepening. It IS ready for a targeted FODS+FODT
proof-of-concept after 4 targeted machinery repairs (R1-R4, estimated 6-8 hours of work).

---

## Evidence Summary

### What works well

1. **FODS .NET** is a professional prototype: DOM-backed, load/edit/save/export, 611 tests,
   security guards, ODF spec citations. This is the closest thing to a "professional library"
   in the repo today.

2. **FODT .NET** is nearly as strong: same pattern, 567 tests, 5 export formats.

3. **SAL for ODF formats** is substantial: 4,987 FODS facts and 4,933 FODT facts, all
   marked workbench_verified, referencing ODF 1.3 spec sections.

4. **Spec stubs (FODS, FODT)** exist and follow the correct pattern: spec_qname attributes,
   spec_fact_ref links, namespace-organized directories. This is the right architecture.

5. **Autonomous supervisor** is operational: continuation, plan locks, governance validators
   (46 total), evidence declaration, evidence bundling all work.

6. **Capability compiler** exists and is executable — it can consume gap records and SAL facts.

7. **40+ skills** are registered, including spec-parity, qname-mapping, and gate-check skills.

### What is broken or missing

1. **78% of Python classes lack spec_qname** (106 of 135). 18/20 Python packages are
   Generation 1 code with no spec/ directory and no spec_qname on domain classes.

2. **FODT models.py classes are missing spec_qname** despite spec stubs existing. This is
   an oversight from the spec stub creation sprint (commit 8ca43a12).

3. **fods/fods/ duplicate** creates two parallel spec stub trees with conflicting class names.

4. **Capability compiler has a path mismatch**: reads from `.local/sal-output/` but SAL files
   are in `.local/spec-cache/`. The compiler cannot currently load SAL facts.

5. **Skills don't enforce spec_qname**: `add-python-object-model-feature` generates new
   product classes without requiring spec_qname — the most critical enforcement gap.

6. **No backfill facility**: No systematic tool exists to bring existing Gen 1 classes
   into spec compliance. FODS backfill was done ad-hoc.

7. **SAL coverage is incomplete**: CSV, XCF, TOML have 0 SAL facts. Non-ODF formats
   cannot participate in the spec-to-feature pipeline.

8. **Spec → code tracing is manual**: No end-to-end proof that "FACT-FODS-006 → TableCell
   spec stub → FodsCell facade → parser output" is mechanically enforced.

9. **Lane separation is prompt-only**: No code prevents a product deepening sprint from
   running before system healing lanes complete.

10. **FODS Python write is incomplete**: The Python track is read-only; .NET is ahead.
    Cross-language parity (P criterion) requires Python write capability.

---

## Why "Ready After Targeted Repairs" (Not "Not Ready")

The system has made genuine, evidence-backed progress:
- Spec stubs exist for FODS and FODT (2 formats with the most depth)
- The design pattern (spec stubs → Compat/ facades → production parser) is correct
- SAL facts are real and substantial for ODF family
- The supervisor correctly identifies Gate 11 as a TRUE_EXTERNAL_GATE
- All governance validators pass (1490 tests as of last sprint)

The 4 immediate blockers (R1-R4) are small, targeted fixes that unblock the FODS+FODT
spec-to-library proof. After those fixes, a proof-of-concept sprint can demonstrate:
`FACT-FODS-001 → office:document spec stub → FodsDocument facade → load → write → export`

That proof is the critical milestone needed before broader product deepening.

---

## Go / No-Go Decision

| Format | Deepening Allowed? | Condition |
|--------|-------------------|-----------|
| FODS .NET | YES — after R1-R4 | Formalize spec references in Spec/ dir |
| FODT .NET | YES — after R1-R4 | Same as FODS .NET |
| FODS Python | YES — after R1-R4 | Add write capability |
| FODT Python | YES — after R1-R4 + TC-FODT-COMPAT-001 | Create Compat/ layer first |
| ODS, ODT | BLOCKED | Spec stubs required first |
| All others | BLOCKED | SAL facts + spec stubs required |

---

## Self-Check Answers

- Did I inspect actual repo evidence? **YES** — read files, ran validators, counted classes
- Did I avoid relying on summaries? **YES** — inspected source files directly
- Did I inspect src/ directly? **YES** — every package listed and classified
- Did I audit .NET and Python products? **YES** — both tracks covered
- Did I identify generation waves? **YES** — 4 waves identified with evidence
- Did I audit qname compliance per product? **YES** — 135 classes audited
- Did I inspect skills? **YES** — 40+ skills catalogued
- Did I inspect SAL? **YES** — fact counts per format, pipeline gaps identified
- Did I inspect capability layer? **YES** — 958 gaps, compiler assessed
- Did I inspect downstream generation? **YES** — entry points identified
- Did I inspect autonomous supervisor? **YES** — mode, state, gaps
- Did I check machinery/product lane separation? **YES** — collision risks identified
- Did I check contamination/collision risk? **YES** — 4 risks documented
- Did I identify whether backfill exists? **YES** — no systematic facility
- Did I design backfill if missing? **YES** — backfill-facility-design.md
- Did I separate working/repeatable/governed/production-ready? **YES**
- Did I avoid claiming Gate 11 readiness from tests alone? **YES** — criteria-based assessment
- Did I produce taskcards? **YES** — taskcards.yaml with 15+ taskcards
- Did I produce a gap matrix? **YES** — system-gap-matrix.yaml with 16 gaps
- Did I give a clear go/no-go verdict? **YES** — READY_AFTER_TARGETED_MACHINERY_REPAIRS
- Did I provide the next execution prompt? **YES** — next-agent-execution-prompt.md
