# Phase Audit 1 — Correction

**Sprint:** FORMAT-FACTORY-R47-ARTIFACT-PROOF-REPAIR-AND-PHASE-AUDIT-PROGRESSION-001
**Date:** 2026-05-22
**Corrects:** reports/r46/phase-audit/phase-01-specification-ingestion.md

---

## What R46 Overclaimed

R46 Phase Audit 1 concluded with `PHASE_AUDIT_1: PASS`. This is overclaimed.

The audit found:
- 3 fully-cached core formats: FODS/ZST/ODS+ODT+FODT (via reuse) — PASS
- 7 formats with no local spec cache: QOI/XCF/DIF/PPM/PGM/PBM/SYLK — PARTIAL

Calling the whole Phase 1 PASS when 7 formats are PARTIAL is an overclaim.

---

## Corrected Classification

**PHASE_AUDIT_1: CORE_PASS_MINOR_FORMATS_PARTIAL**

| Format | Spec Cache | Gate 2 | Phase 1 Result |
|--------|-----------|---------|----------------|
| FODS | CACHED (ODF 1.3, SHA recorded) | PASS | **PASS** |
| FODT | REUSES FODS cache (documented) | PASS | **PASS** |
| ZST | CACHED (RFC 8878 + RFC 9659) | PASS | **PASS** |
| ODS | Reuses FODS cache | PASS | **PASS** |
| ODT | Reuses FODS cache | PASS | **PASS** |
| QOI | No local cache (URL known, public domain) | PASS | **PARTIAL** |
| XCF | No local cache (GIMP source doc) | PASS | **PARTIAL** |
| DIF | No local cache (Lotus/VisiCalc text spec) | PASS | **PARTIAL** |
| PPM | No local cache (Netpbm text spec) | PASS | **PARTIAL** |
| PGM | No local cache (Netpbm text spec) | PASS | **PARTIAL** |
| PBM | No local cache (Netpbm text spec) | PASS | **PARTIAL** |
| SYLK | No local cache (Microsoft SLYK text spec) | PASS | **PARTIAL** |

**Core formats (5): PASS**
**Minor formats (7): PARTIAL — no local spec cache**
**Overclaimed provenance: NONE** (no format falsely claims SUPPORTED_BY_CACHED_SOURCE)

---

## What Was Correct in R46 Phase Audit 1

- No format overclaims provenance — all PARTIAL formats correctly document the gap
- Source URLs are referenced for all 7 PARTIAL formats
- The audit correctly identified the gaps (just overclaimed the overall verdict)
- FODS/FODT/ZST/ODS/ODT spec chains are complete and honest

---

## Taskcards for Phase 1 Gaps

| Format | Gap | Priority | Sprint Target |
|--------|-----|----------|---------------|
| QOI | Cache QOI spec (2-page public domain spec) | LOW | R48 |
| PPM/PGM/PBM | Cache Netpbm spec (shared, plain text) | LOW | R48 |
| DIF | Document VisiCalc DIF spec URL in spec-evidence.md | LOW | R48 |
| XCF | Document XCF GIMP source reference explicitly | LOW | R49 |
| SYLK | Document SYLK/SLYK spec URL in spec-evidence.md | LOW | R48 |

---

## Corrected Phase 1 Result

**PHASE_AUDIT_1: CORE_PASS_MINOR_FORMATS_PARTIAL**

The core product formats (FODS, FODT, ZST, ODS, ODT) have complete and honest
specification ingestion. The 7 minor formats have documented source references
but no local cache files — low-risk gaps that do not affect product delivery.

This correction stands until all 7 format gaps are closed.
