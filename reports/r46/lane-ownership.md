# R46 Lane Ownership

**Sprint:** FORMAT-FACTORY-R46-ARTIFACT-CONTAINED-TWO-PRODUCT-RC-001
**Date:** 2026-05-21

---

## MT1: R45 Correction + Closeout Hardening

| Lane | Task | Status |
|------|------|--------|
| 1A | R45 IV report (r45-independent-verification.md) | COMPLETE |
| 1B | Validator: catch PENDING in repo/reports/*/final-verdict.md + tests | IN_PROGRESS |
| 1C | R46 contract with artifact proof requirements | PENDING |

## MT2: Artifact-Contained Package Proof

| Lane | Task | Status |
|------|------|--------|
| 2A | Policy: define artifact-contained proof requirement | PENDING |
| 2B | Python artifacts (.whl + .tar.gz) rebuilt + in metadata | PENDING |
| 2C | .NET artifacts (.nupkg) rebuilt + in metadata | PENDING |

## MT3: Consumer Proof Replayability

| Lane | Task | Status |
|------|------|--------|
| 3A | FODS .NET consumer proof replayable from bundled nupkg | PENDING |
| 3B | FODT .NET consumer proof replayable from bundled nupkg | PENDING |
| 3C | Consumer proof validator (logs-only fails) | PENDING |

## MT4: Timeout and Bounded Replay Repair

| Lane | Task | Status |
|------|------|--------|
| 4A | pytest.ini filterwarnings fix for Unknown config option: timeout | PENDING |
| 4B | tools/testing/run_bounded_pytest.py subprocess wrapper | PENDING |

## MT5: Phase Audit 1 — Specification Ingestion

| Lane | Task | Status |
|------|------|--------|
| 5A | reports/r46/phase-audit-roadmap.md (7 phase definitions) | PENDING |
| 5B | reports/r46/phase-audit/phase-01-specification-ingestion.md | PENDING |
| 5C | spec-cache audit: FODS, FODT, ZST, ODS/ODT/QOI ingestion review | PENDING |
| 5D | Spec ingestion validator/skill | PENDING |

## MT6: Two-Product Capability Deepening

| Lane | Task | Status |
|------|------|--------|
| 6A | FODS Python write/export capability + tests | PENDING |
| 6B | FODT Python write/export capability + tests | PENDING |

## MT7: Next-Format Acceleration

| Lane | Task | Status |
|------|------|--------|
| 7A | ZST RC designation review | DEFERRED_R47 |
| 7B | Gate 8 packet compression (ODS/ODT/QOI/XCF/DIF/PPM) | DEFERRED_R47 |
| 7C | PGM/PBM/SYLK Gate 10 | DEFERRED_R47 |

## MT9: Docs/Taskcards/Memory

| Lane | Task | Status |
|------|------|--------|
| 9A | Master plan sync | PENDING |
| 9B | Memory sync | PENDING |

## MT10: Final Adversarial IV + Bundle

| Lane | Task | Status |
|------|------|--------|
| 10A | Full test run (all suites) | PENDING |
| 10B | Artifact-contained bundle build | PENDING |
| 10C | Final verdict | PENDING |
