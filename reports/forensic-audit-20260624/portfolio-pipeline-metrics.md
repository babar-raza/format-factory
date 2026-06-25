# FORMAT FACTORY — PORTFOLIO PIPELINE METRICS
# Generated: 2026-06-24 | Mission: FF-FORENSIC-AUDIT-20260624

## Executive Summary

| Metric | Value | Notes |
|--------|-------|-------|
| Governed formats | 25 | registry: 24 active + 1 odf-shared |
| Formats with Python source | 20 | 4 have no source at all |
| Formats with .NET source | 10 | commercial flagship focus |
| Total SAL spec facts | 14,486 | 14,331 workbench-verified |
| ODF family facts | 13,204 | 91.2% of all facts |
| Non-ODF facts | 1,282 | 8.8% across 19 non-ODF formats |
| Total capabilities | 1,766 | 1,641 foss_reduced + 125 commercial |
| Capabilities with verified spec backing | ~200 | ODF commercial only |
| Capability-to-verified-fact ratio (non-ODF) | ~27x | inflation |
| Total gaps in gap-ledger | 1,018 | 975 closed, 9 open |
| QName registry entries populated | 0 | all 20 files are empty |
| Packages published | 0 | all local_only_not_published |
| Formats commercially ready | 0 | Gate 11 not approved |
| Python test files total | ~1,800 | across all formats |
| .NET test files total | ~250 | fods/fodt/netpbm focus |

---

## Spec-to-Product Pipeline Loss Ratios

```
SPEC SOURCES (25 formats, 14,486 facts)
    ↓ FACT AUTHORIZATION (14,331 verified — 99.0% rate)
    ↓ QNAME DERIVATION (0 qname entries — 0.0% rate) ← CRITICAL BREAK
    ↓ CAPABILITY EXTRACTION (1,766 caps — ratio: 0.12 caps/fact)
    ↓ FEATURE PLANNING (1,766 features = caps, no separate feature planning step)
    ↓ CODE TRANSLATION (20 Python formats — translation quality varies widely)
    ↓ TEST COVERAGE (very uneven: 15–625 tests per format)
    ↓ PACKAGE PROOF (all local_only, 0 published)
    ↓ CONSUMER PROOF (0 documented end-to-end consumers)
```

**Critical breaks in the pipeline:**
1. **SPEC_TO_FACT (non-ODF)**: 13 formats have 2-9 facts each despite meaningful specs
2. **FACT_TO_QNAME**: 0 qname entries across all 20 formats — total break
3. **CODE_TO_PACKAGE**: All 16 packages local-only, 0 published

---

## Per-Family Aggregate Metrics

### ODF Family (fods, fodt, ods, odt, fodp, fodg)
| Metric | Value |
|--------|-------|
| Spec facts | 13,204 |
| Capabilities | 589 (commercial+foss) |
| Python products | 6 |
| .NET products | 2 (fods, fodt) |
| Production-track formats | 2 (fods, fodt) |
| Roundtrip capable | 4 (fods, fodt, ods, fodg) |
| Read-only/probe | 2 (odt, fodp) |
| Pipeline grade | B (strong spec, partial product) |

### Cells Family (csv, tsv, dif, sylk, gnumeric)
| Metric | Value |
|--------|-------|
| Spec facts | 30 (gnumeric 9, sylk 9, dif 9, csv 8, tsv 5) |
| Capabilities | 449 (combined) |
| Inflation ratio | ~15x |
| Roundtrip capable | 2 (sylk, gnumeric) |
| Read-write only | 1 (dif) |
| Prototype only | 2 (csv, tsv) |
| Pipeline grade | D (sparse spec, inconsistent product) |

### Imaging Family (xcf, qoi, ppm, pgm, pbm, xpm, pam, ora)
| Metric | Value |
|--------|-------|
| Spec facts | 36 (xpm 3, pam 3, ora 6, xcf 5, qoi 5, ppm 5, pgm 5, pbm 5) |
| Capabilities | 397 (combined foss_reduced) |
| Inflation ratio | ~11x |
| Roundtrip capable | 1 (qoi) |
| Read-only | 3 (ppm, pgm, pbm) |
| Probe-only | 1 (xcf) |
| No source | 3 (xpm, pam, ora) |
| Pipeline grade | D (specs appropriate for short formats but product depth low) |

### Data Family (ndjson, toml)
| Metric | Value |
|--------|-------|
| Spec facts | 10 (ndjson 5, toml 5) |
| Capabilities | 186 (combined) |
| Inflation ratio | ~18x |
| Roundtrip capable | 2 (both) |
| Test count | 15 (toml), 80 (ndjson) |
| Pipeline grade | D+ (roundtrip works but spec not processed) |

### Words Family (abw, fodt, odt)
| Metric | Value |
|--------|-------|
| Spec facts | 4,973 (fodt 4957, odt 1074, abw 8) |
| Roundtrip capable | 2 (fodt, abw) |
| Read-only | 1 (odt) |
| Pipeline grade | B (fodt production-track, others partial) |

### Archive Family (zst, zpaq)
| Metric | Value |
|--------|-------|
| Spec facts | 114 (zst 109, zpaq 5) |
| Python source | 1 (zst) |
| .NET source | 1 (zst) |
| Blocked | 1 (zpaq) |
| Pipeline grade | C (zst has good test coverage, sparse spec facts) |

---

## Process-Quality Grading Matrix (0–5)

| Dimension | ODF/FODS | ODF/FODT | ZST | ABW | GNM | XCF | QOI | NetPBM | DIF/SYLK | CSV/TSV | NDJSON | TOML |
|-----------|----------|----------|-----|-----|-----|-----|-----|--------|----------|---------|--------|------|
| 1. Spec Discovery | 5 | 5 | 4 | 2 | 2 | 2 | 4 | 4 | 2 | 3 | 3 | 2 |
| 2. Spec Completeness | 5 | 5 | 3 | 1 | 1 | 1 | 3 | 3 | 1 | 2 | 1 | 2 |
| 3. Semantic Extraction | 5 | 5 | 3 | 1 | 1 | 1 | 2 | 2 | 1 | 1 | 1 | 1 |
| 4. Fact Provenance | 4 | 4 | 3 | 1 | 1 | 1 | 2 | 2 | 1 | 1 | 1 | 1 |
| 5. Fact Authorization | 5 | 5 | 4 | 2 | 1 | 1 | 2 | 2 | 1 | 1 | 1 | 1 |
| 6. Qname Fidelity | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 7. Hierarchy Fidelity | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 8. Capability Fidelity | 3 | 3 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 9. Feature Planning | 3 | 3 | 2 | 2 | 2 | 1 | 2 | 2 | 1 | 1 | 1 | 1 |
| 10. Taskcard Quality | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | 1 | 1 | 1 | 1 |
| 11. Code Translation | 4 | 4 | 3 | 3 | 3 | 1 | 3 | 2 | 2 | 2 | 3 | 3 |
| 12. Public API Quality | 3 | 3 | 4 | 2 | 2 | 1 | 3 | 2 | 2 | 2 | 3 | 2 |
| 13. Test Quality | 3 | 3 | 4 | 3 | 3 | 2 | 3 | 2 | 2 | 1 | 2 | 1 |
| 14. Integration Quality | 2 | 2 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| 15. End-to-End Proof | 2 | 2 | 2 | 1 | 1 | 0 | 1 | 0 | 1 | 0 | 1 | 0 |
| 16. Packaging/Consumer | 2 | 2 | 2 | 2 | 2 | 0 | 2 | 2 | 2 | 0 | 0 | 0 |
| 17. Evidence Quality | 3 | 3 | 3 | 2 | 2 | 1 | 2 | 2 | 2 | 1 | 2 | 1 |
| 18. Repeatability | 3 | 3 | 4 | 3 | 3 | 2 | 3 | 2 | 2 | 2 | 3 | 2 |
| 19. Governance Enf. | 4 | 4 | 4 | 3 | 3 | 2 | 3 | 3 | 3 | 3 | 3 | 3 |
| 20. Maintainability | 3 | 3 | 3 | 2 | 2 | 2 | 3 | 2 | 2 | 2 | 3 | 2 |
| **AVERAGE** | **2.8** | **2.8** | **2.8** | **1.75** | **1.7** | **1.0** | **2.1** | **1.8** | **1.5** | **1.3** | **1.8** | **1.4** |

**Portfolio average across all graded formats: 1.97 / 5.0**

**Key findings:**
- Dimensions 6 (Qname Fidelity) and 7 (Hierarchy Fidelity): **0 across the entire portfolio** — the qname registry is empty
- Only 2 formats (FODS, FODT) score ≥ 2.5 average
- No format has achieved packaging or consumer proof

---

## Pipeline Anomaly Summary

| Boundary | Anomaly Count | Severity | Primary Anomaly |
|----------|---------------|----------|-----------------|
| SPEC_TO_FACT | 17 | CRITICAL | Non-ODF formats have 2-22 facts (should be 30-500) |
| FACT_TO_AUTHORITY | 1 | LOW | bootstrap_only facts (148 total) are not workbench verified |
| FACT_TO_QNAME | 1 | CRITICAL | Zero qname derivations across all 20 formats |
| FACT_TO_CAPABILITY | 1 | HIGH | 27x average inflation for non-ODF formats |
| CAPABILITY_TO_FEATURE | 1 | MEDIUM | No separate feature planning step; capabilities == features |
| FEATURE_TO_CODE | 8 | HIGH | 8 formats with incomplete implementations |
| CODE_TO_TEST | 4 | HIGH | 4 formats with < 20 tests |
| CODE_TO_INTEGRATION | 1 | MEDIUM | No cross-format integration layer |
| CODE_TO_PACKAGE | 1 | HIGH | 16 local packages, 0 published |
| PACKAGE_TO_CONSUMER | 1 | HIGH | 0 documented consumer proofs |

---

## Summary Verdict

**Overall Pipeline Grade: D+ (1.97/5.0)**

The Format Factory pipeline has three tiers:

**Tier 1 — Production Track (2 formats):** FODS, FODT
- Rich spec, full SAL pipeline, read/write/roundtrip in both Python and .NET
- Strong test suites (567-611 .NET tests, 211-248 Python tests)
- Blocked at: QName registry population, Gate 11 commercial approval

**Tier 2 — Working But Incomplete (8 formats):** ODS, FODG, ZST, ABW, GNUMERIC, QOI, SYLK, NDJSON
- Roundtrip capable in Python
- Spec facts very sparse (2-18 verified facts)
- Capabilities not grounded in spec evidence

**Tier 3 — Partial or No Implementation (14 formats):** ODT, FODP, XCF, PPM, PGM, PBM, DIF, CSV, TSV, TOML, XPM, PAM, ZPAQ, ORA
- Missing write path, roundtrip, or full implementation
- Very low test counts or no tests

**Portfolio Blockers (in priority order):**
1. RC-002: QName registry is empty — blocks all qname-to-code traceability
2. RC-001: Non-ODF spec extraction yields only 2-22 facts — capabilities are unsupported
3. RC-005: 8 formats have incomplete implementations (read-only, probe-only, or prototype)
4. RC-003: Capability inflation (27x average) means the capability layer is not spec-derived
5. RC-007: 15 formats have no .NET implementation (all commercial targets blocked)
