# Spec Authority Machinery — Format Authority Matrix

**Run ID:** `spec-authority-machinery-explosion-20260621-827f5a52`
**Date:** 2026-06-21

---

| Format | SAL Facts (Total) | Workbench-Verified | Source Type | Spec Stubs | QName Registry | Req Packs | Proof Level | Notes |
|--------|-------------------|--------------------|-----------|-----------|--------------------|-----------|-------------|-------|
| FODS | ~5,009 | 4,987 | workbench_verified | YES (12 classes) | YES (12 QNames) | YES (3 packs) | **P5** | Full chain: spec→workbench→fact→stub→qname→product. TC-0021 review pending. Daily SAL has ~22 bootstrap-only also. |
| FODT | 4,933 | 4,933 | workbench_verified | YES (partial) | NO | NO | **P4** | Spec stubs added (GAP-ARCH-005). No QName registry. All SAL facts are workbench-verified. |
| ZST | 94 | 94 | workbench_verified | NO | NO | NO | **P4** | Workbench facts; req-graph exists; code+tests. |
| FODP | 1,066 | 1,066 | workbench_verified | NO | NO | NO | **P3** | Large workbench count; no stubs or registry. Acquisition chain undocumented. |
| FODG | 1,066 | 1,066 | workbench_verified | NO | NO | NO | **P3** | Same as FODP. |
| ODS | 1,066 | 1,066 | workbench_verified | NO | NO | NO | **P3** | Same as FODP. |
| ODT | 1,066 | 1,066 | workbench_verified | NO | NO | NO | **P3** | Same as FODP. |
| PPM | 2 | 2 | workbench_verified | NO | NO | NO | **P3** | Minimal workbench facts. |
| PGM | 2 | 2 | workbench_verified | NO | NO | NO | **P3** | Minimal workbench facts. |
| PBM | 2 | 2 | workbench_verified | NO | NO | NO | **P3** | Minimal workbench facts. |
| DIF | 0 | 0 | NONE | NO | NO | NO | **P2** | Code+tests exist; spec artifacts normalized; candidate reqs. |
| NETPBM | 0 | 0 | NONE | NO | NO | NO | **P2** | Code+tests exist; spec artifacts normalized. |
| Gnumeric | 0 | 0 | NONE | NO | NO | NO | **P2** | Code+tests; XML schema known but no normalized text; gap-ledger spec_facts: [] (CLEAN) |
| CSV | 0 | 0 | NONE | NO | NO | NO | **P2** | Code+tests; gap-ledger has STALE FACT-CSV-001/002 refs in 58 gaps (116 total) |
| ABW | 0 | 0 | NONE | NO | NO | NO | **P1** | Code+tests; DTD unreachable; gap-ledger spec_facts: [] (CLEAN); lowest confidence |
| SYLK | 0 | 0 | NONE | NO | NO | NO | **P2** | Code+tests; 893 tests pass |
| TSV | 0 | 0 | NONE | NO | NO | NO | **P2** | Code+tests; no spec acquisition |
| NDJSON | 0 | 0 | NONE | NO | NO | NO | **P2** | Code+tests; informal spec |
| TOML | 0 | 0 | NONE | NO | NO | NO | **P2** | Code+tests; formal spec exists but not acquired |
| QOI | 0 | 0 | NONE | NO | NO | NO | **P2** | Code+tests |
| XCF | 0 | 0 | NONE | NO | NO | NO | **P2** | Code+tests |
| ORA | 0 | 0 | NONE | NO | NO | NO | **P2** | Code+tests |
| ZPAQ | 0 | 0 | NONE | NO | NO | NO | **P2** | Code+tests |
| XPM | 0 | 0 | NONE | NO | NO | NO | **P2** | Code+tests |
| PAM | 0 | 0 | NONE | NO | NO | NO | **P2** | Code+tests |

---

## Proof Level Definitions

| Level | Criteria |
|-------|---------|
| P6 | Full chain enforced in production: spec→fact→gate→product→test→automated release blocking |
| P5 | Spec stubs + QName registry + workbench facts + req packs + tests; not yet production-gated |
| P4 | Workbench facts + code + tests + spec stubs (partial); no QName registry |
| P3 | Workbench facts + code + tests; no stubs, registry, or req packs |
| P2 | Code + tests + spec artifacts; no workbench-verified facts |
| P1 | Code + tests only; spec unreachable or not acquired |
| P0 | No code or spec evidence |

---

## Format Groups by Proof Level

**P5 (1 format):** FODS — full chain with stubs, registry, req-packs, 4,987 workbench facts

**P4 (2 formats):** FODT (4,933 wb), ZST (94 wb) — workbench facts + partial stubs (FODT) or req-graph (ZST)

**P3 (7 formats):** FODP, FODG, ODS, ODT (1,066 wb each), PPM, PGM, PBM (2 wb each)

**P2 (13 formats):** Gnumeric, DIF, NETPBM, SYLK, TSV, NDJSON, TOML, QOI, XCF, ORA, ZPAQ, XPM, PAM, CSV (stale gap refs)

**P1 (1 format):** ABW — DTD unreachable, spec not acquired, lowest confidence

---

## Gap Summary by Format

| Format | Gap Count | Stale Spec Facts | SAL Facts | TC-GUARD Status |
|--------|-----------|-----------------|-----------|-----------------|
| ABW | 50 | 0 (cleaned) | 0 | Gaps cite no fact IDs — gap_ledger_ref satisfies guard with no substance |
| Gnumeric | 36 | 0 (cleaned) | 0 | Same as ABW |
| CSV | 58 | 116 stale refs (FACT-CSV-001/002) | 0 | Stale IDs appear spec-backed; guard accepts |
| FODS | many | 0 | 4,987 wb | Real spec authority; guard enforces correctly |
