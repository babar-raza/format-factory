# Phase Audit Roadmap (Corrected)

**Sprint:** FORMAT-FACTORY-R47-ARTIFACT-PROOF-REPAIR-AND-PHASE-AUDIT-PROGRESSION-001
**Date:** 2026-05-22
**Replaces:** reports/r46/phase-audit-roadmap.md (drifted sequence)

---

## Why the Roadmap Was Corrected

R46's phase-audit roadmap drifted from the required phase sequence. Specifically:
- R46 roadmap Phase 2 was "Parser Implementation Quality"
- Required Phase 2 is **"Sample Acquisition / Sample Provenance"**

The correct sequence was specified by Babar Raza: each sprint audits one phase,
proceeding from source acquisition through product readiness. Parser quality comes
AFTER sample provenance because parser quality cannot be fully assessed without
knowing whether the samples used to test it have verified provenance.

---

## Required Phase Sequence (Authoritative)

| Phase | Name | Sprint | Status |
|-------|------|--------|--------|
| Phase 1 | Specification Ingestion / Spec Cache / Canonical Source | R46 | COMPLETE (CORE_PASS_MINOR_FORMATS_PARTIAL) |
| Phase 2 | Sample Acquisition / Sample Provenance | R47 | IN_PROGRESS (this sprint) |
| Phase 3 | Parser Requirements / Prototype Creation | R48 | SCHEDULED |
| Phase 4 | Neutral Model / Oracle / Fuzz / Security | R49 | SCHEDULED |
| Phase 5 | Product Mapping / Implementation Authorization | R50 | SCHEDULED |
| Phase 6 | Package / Release Candidate Materialization | R51 | SCHEDULED |
| Phase 7 | Commercial Readiness / Publication Governance | R52 | SCHEDULED |

---

## Why Phase 2 = Sample Acquisition / Sample Provenance

The project requires rigorous provenance for all test data. Sample provenance audit:
1. Establishes ground truth for downstream parser/oracle audits
2. Ensures no unlicensed test data is committed
3. Enables deterministic corpus rebuild (samples generator recipes)
4. Is prerequisite for Phase 3 (parser requirements depend on known-good samples)

Auditing parser quality (originally proposed Phase 2) before sample provenance
would risk basing quality assessments on samples with unknown license/provenance.

---

## Phase 1 Detail (Closed, R46, Corrected in R47)

**PHASE_AUDIT_1: CORE_PASS_MINOR_FORMATS_PARTIAL**
- Core formats (FODS/FODT/ZST/ODS/ODT): PASS
- Minor formats (QOI/XCF/DIF/PPM/PGM/PBM/SYLK): PARTIAL (no local cache, documented source URLs)
- Full correction: `reports/r47/phase-audit/phase-01-correction.md`

---

## Phase 2 Detail (R47, In Progress)

**Scope:** Audit sample provenance for all formats with committed test fixtures.
- FODS, FODT, ZST: full audit (see phase-02-sample-acquisition-provenance.md)
- ODS, ODT, QOI, XCF, DIF, PPM, PGM, PBM, SYLK: matrix audit

**Output:** `reports/r47/phase-audit/phase-02-sample-acquisition-provenance.md`

---

## Phase 3 Preview (R48)

**Scope:** Parser Requirements and Prototype Creation
- For each format with a Python parser: verify requirements completeness
- Check parser handles documented valid/invalid inputs
- Verify prototype creation matches requirements
- No hardcoded paths or debug code

---

## Standing Policy

This roadmap is the authoritative phase sequence. Changes to the phase sequence
require a recorded decision (DEC-NNN in GOVERNANCE.md or plans/master-plan.md).
Phase order cannot be changed within a sprint without a new decision record.
