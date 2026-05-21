# Phase Audit Roadmap

**Sprint:** FORMAT-FACTORY-R46-ARTIFACT-CONTAINED-TWO-PRODUCT-RC-001
**Date:** 2026-05-21
**Status:** R46 executes Phase Audit 1 (Specification Ingestion)

---

## Overview

Starting in R46, each sprint includes one Phase Audit Train. Phase audits are
systematic, phased reviews of the project's technical and governance systems.
Each phase audit produces an audit report that becomes part of the sprint bundle.

Phase audits are **non-blocking**: a partial audit result does not block the sprint
verdict. They are accumulative — each sprint advances the audit by one phase.

---

## Phase Audit Schedule

| Phase | Name | R-Sprint | Status |
|-------|------|----------|--------|
| Phase 1 | Specification Ingestion | R46 | IN_PROGRESS (this sprint) |
| Phase 2 | Parser Implementation Quality | R47 | SCHEDULED |
| Phase 3 | Test Coverage and Oracle Verification | R48 | SCHEDULED |
| Phase 4 | Gate Evidence Completeness | R49 | SCHEDULED |
| Phase 5 | Generated Requirements Traceability | R50 | SCHEDULED |
| Phase 6 | .NET Commercial Product Depth | R51 | SCHEDULED |
| Phase 7 | AI Platform Integration Quality | R52 | SCHEDULED |

---

## Phase 1 — Specification Ingestion (R46)

**Scope:** For each format at Gate 2+, verify:
1. Spec is cached in `.local/spec-cache/<format>/` (or documented source URL)
2. `spec-index.yaml` exists and is valid
3. Spec SHA-256 is recorded in acquisition-pack `spec-evidence.md`
4. Spec version matches the implemented parser
5. No over-claimed provenance (SUPPORTED_BY_CACHED_SOURCE vs PLAUSIBLE)

**Formats audited in R46:** FODS, FODT, ZST, ODS (partial), ODT (partial)

**Output:** `reports/r46/phase-audit/phase-01-specification-ingestion.md`

---

## Phase 2 — Parser Implementation Quality (R47)

**Scope:** For each format with a Python parser:
1. Parser handles all documented valid inputs
2. Parser rejects all documented invalid inputs
3. Error messages are informative
4. No hardcoded paths or debug code

---

## Phase 3 — Test Coverage and Oracle Verification (R48)

**Scope:**
1. Gate 4-7 test counts vs required coverage
2. Fuzz test scope vs expected inputs
3. Oracle comparison methodology

---

## Phase 4 — Gate Evidence Completeness (R49)

**Scope:** For each format, verify all gate evidence files are complete and non-stub.

---

## Phase 5 — Generated Requirements Traceability (R50)

**Scope:** FODS/FODT generated-requirements: spec citations → implementation → tests.

---

## Phase 6 — .NET Commercial Product Depth (R51)

**Scope:** FODS/FODT .NET: C4-C6 capability completeness, G11 sub-gates.

---

## Phase 7 — AI Platform Integration Quality (R52)

**Scope:** AI platform governance, fixture mode accuracy, live endpoint proof.
