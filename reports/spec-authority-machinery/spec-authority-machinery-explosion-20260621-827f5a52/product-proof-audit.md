# Spec Authority Machinery — Product Proof Audit

**Run ID:** `spec-authority-machinery-explosion-20260621-827f5a52`
**Date:** 2026-06-21

---

## Audit Objective

Assess whether product source files have credible, verifiable spec authority backing. Evaluate the proof level for each format and identify gaps in the spec → product → test chain.

---

## FODS (Proof Level: P5)

### Evidence Chain

| Link | Evidence | Status |
|------|---------|--------|
| Spec source | OASIS ODF 1.3 PDF → `.local/spec-cache/fods/1.3/normalized/text.txt` | VERIFIED |
| Workbench facts | `verified-facts-review.yaml`: 4,991 facts (9,974 deterministic + 16 agent verifier) | VERIFIED |
| SAL facts | `sal-facts-latest.json`: 4,987 workbench_verified + ~22 bootstrap-only | VERIFIED (workbench facts) |
| Requirement packs | 3 YAMLs; TC-0021 traceability review pending | PARTIAL |
| Spec stubs | 12 architecture-only classes: `spec_fact_ref = "FACT-FODS-006"` per class | VERIFIED |
| QName registry | 12 QNames: `table:table-cell → FACT-FODS-006 → Table.TableCell → table_cell.py` | VERIFIED |
| Product source | `neutral_model.py`: `FACT-FODS-001` cited in source comments | VERIFIED |
| Product source | `constants.py`: `FACT-FODS-001` cited in QN_DOCUMENT, ATTR_MIMETYPE | VERIFIED |
| Compat facades | `Compat/FodsCell`, `Compat/FodsDocument`, `Compat/FodsSheet` | VERIFIED |
| GAP-INT-002 | `FACT-FODS-001` cited in source exists in SAL output | PASS |
| Quarantine | `FODS-SPEC-001-requirements-QUARANTINE.md` — synthetic reqs quarantined (GAP-002) | QUARANTINE NOT USED |

**Chain completeness: STRONG.** Weak points: TC-0021 pending; SAL daily output has template facts; `architecture_only` stubs not yet in production parser.

---

## FODT (Proof Level: P4)

| Link | Evidence | Status |
|------|---------|--------|
| SAL facts | 4,933 workbench_verified (all workbench, no bootstrap) | STRONG |
| Spec stubs | Partial (GAP-ARCH-005) | PARTIAL |
| QName registry | NOT YET CREATED for FODT | MISSING |
| Product source | `neutral_model.py`: FACT-FODT-* cited | VERIFIED (per GAP-INT-002) |
| GAP-INT-002 | FODT cited facts exist in SAL | PASS |

**Chain completeness: GOOD.** Missing: QName registry; only partial spec stubs.

---

## ZST (Proof Level: P4)

| Link | Evidence | Status |
|------|---------|--------|
| SAL facts | 94 workbench_verified | MODERATE |
| Req graph | In spec-artifacts | EXISTS |
| Product source | `zst_codec.py`: FACT-ZST-* cited | VERIFIED (per GAP-INT-002) |
| GAP-INT-002 | ZST cited facts exist in SAL | PASS |

**Chain completeness: MODERATE.** Only 94 workbench facts for a complex format. No spec stubs.

---

## FODP/FODG/ODS/ODT (Proof Level: P3)

| Link | Evidence | Status |
|------|---------|--------|
| SAL facts | 1,066 each workbench_verified | STRONG COUNT |
| Acquisition chain | Undocumented — identical count suspicious | UNVERIFIED |
| Spec stubs | NOT CREATED | MISSING |
| QName registry | NOT CREATED | MISSING |

**Finding:** All four formats have exactly 1,066 workbench-verified SAL facts. This identical count is suspicious — it may indicate cross-format inheritance or shared workbench data rather than format-specific extraction. Requires investigation (RCA-FODFAM-CHAIN).

---

## Gnumeric / ABW / CSV (Proof Levels: P2, P1, P2)

| Format | Product Source | Tests | SAL Facts | Gap-ledger | Verdict |
|--------|---------------|-------|-----------|------------|---------|
| Gnumeric | EXISTS | EXISTS | 0 | 36 gaps, empty spec_facts | P2 — no spec authority |
| ABW | EXISTS | EXISTS | 0 | 50 gaps, empty spec_facts | P1 — spec unreachable |
| CSV | EXISTS | EXISTS | 0 | 58 gaps, STALE FACT-CSV-001/002 | P2 — stale refs create false confidence |

**Key finding for CSV:** The `spec_facts: ['FACT-CSV-001', 'FACT-CSV-002']` in 58 gap entries is a false positive. These IDs are not in SAL output. A PRODUCT_SOURCE citing a CSV gap satisfies TC-GUARD-001 but has no real spec authority.

---

## Product Source Quality — FACT Ref Density

| Source File | FACT refs | Verified in SAL |
|------------|-----------|-----------------|
| `fods/neutral_model.py` | FACT-FODS-001 (multiple) | YES — FACT-FODS-001 in SAL |
| `fods/constants.py` | FACT-FODS-001 (2 refs) | YES |
| `fods/spec/table/table_cell.py` | FACT-FODS-006 | YES — FACT-FODS-006 in SAL |
| `fodt/neutral_model.py` | FACT-FODT-* | YES (per test) |
| `zst/zst_codec.py` | FACT-ZST-* | YES (per test) |
| `gnumeric/*.py` | NONE | N/A |
| `abw/*.py` | NONE | N/A |
| `csv/*.py` | NONE | N/A |

**GAP-INT-002 `test_total_fact_refs_across_product_source` scans ALL Python source:** PASS — all cited FACT-* refs verified in SAL index (including template facts in index; see RCA-SAL-DEFAULT-MODE).

---

## Overall Assessment

**Formats with credible spec authority:** FODS (P5), FODT (P4), ZST (P4) — clear workbench provenance + product citations + test coverage.
**Formats with plausible spec authority:** FODP/FODG/ODS/ODT (P3) — large workbench counts; acquisition chain needs audit.
**Formats with no spec authority:** Gnumeric, ABW, CSV, TSV, SYLK, DIF, NDJSON, TOML, QOI, XCF, ORA, ZPAQ, XPM, PAM — zero workbench facts; product exists without spec backing.

**False confidence risk (most impactful):** CSV — gap entries with stale FACT-CSV-001/002 refs create the appearance of spec backing. TC-GUARD-001 accepts these gaps. Fix: clear stale refs or properly acquire CSV spec.
