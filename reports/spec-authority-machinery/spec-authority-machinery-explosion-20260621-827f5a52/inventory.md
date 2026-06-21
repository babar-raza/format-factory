# Spec Authority Machinery — Inventory

**Run ID:** `spec-authority-machinery-explosion-20260621-827f5a52`
**Date:** 2026-06-21

---

## 1. SAL Pipeline Tools (19-20 modules)

| File | Role | Status |
|------|------|--------|
| `tools/specification-authority-layer/sal_master_runner.py` | Master pipeline runner; orchestrates fact loading, from_cache_only mode, output | ACTIVE — idempotency fix applied; default mode still mixes template+workbench |
| `tools/specification-authority-layer/run_extraction_pipeline.py` | Extraction pipeline runner | ACTIVE |
| `tools/specification-authority-layer/validate_spec_fact_refs.py` | Validates spec_fact_refs field in declarations | ACTIVE — used by autonomous_cycle.py Step 2d |
| `tools/specification-authority-layer/*.py` (remaining 17+) | Various extraction, normalization, indexing tools | ACTIVE (existence verified via healing gate: 19-20 modules) |

---

## 2. SAL Output Artifacts

| File | Content | Status |
|------|---------|--------|
| `.local/sal-output/sal-facts-latest.json` | 14,284+ total facts; FODS 4,987 wb + ~22 bootstrap; FODT 4,933 wb; ZST 94 wb; FODP/FODG/ODS/ODT 1,066 each wb | ACTIVE — generated 2026-06-21T21:28:38; DEFAULT mode (not from_cache_only) |
| `.local/spec-cache/fods/1.3/workbench/verified-facts-review.yaml` | 4,991 fact entries; verification_status: verified/verified_with_note | ACTIVE — primary workbench source for FODS |
| `.local/spec-cache/fods/1.3/workbench/requirement-packs/parser-requirements.yaml` | 10 FODS parser requirements | ACTIVE — TC-0021 review pending |
| `.local/spec-cache/fods/1.3/workbench/requirement-packs/model-requirements-draft.yaml` | Model requirements draft | ACTIVE — draft status |
| `.local/spec-cache/fods/1.3/workbench/requirement-packs/sample-requirements.yaml` | Sample requirements | ACTIVE |
| `.local/spec-cache/fods/1.3/normalized/text.txt` | Normalized ODF 1.3 spec text | ACTIVE |
| `.local/spec-cache/gnumeric/v10/spec-index.yaml` | Gnumeric spec index | METADATA-ONLY — `normalized_text_cached: false` |
| `.local/spec-cache/abw/awml-1.0/spec-index.yaml` | ABW spec index | METADATA-ONLY — DTD unreachable (ECONNREFUSED) |
| `.local/spec-artifacts/FODS-SPEC-001-requirements-QUARANTINE.md` | Quarantined synthetic FODS requirements | QUARANTINE (GAP-002, 2026-06-07) — do not use |

---

## 3. Gap Ledger

| File | Content | Status |
|------|---------|--------|
| `reports/capability-layer/gap-ledger.json` | 958 gaps across all formats | ACTIVE |
| — ABW entries | 50 gaps; spec_facts: [] (empty — stale magic IDs previously cleaned) | CLEAN — no stale refs |
| — Gnumeric entries | 36 gaps; spec_facts: [] (empty) | CLEAN — no stale refs |
| — CSV entries | 58 gaps; spec_facts: ['FACT-CSV-001', 'FACT-CSV-002'] | STALE — 116 refs to non-existent SAL IDs |
| — authority_level | 0/958 entries have this field | ABSENT |

---

## 4. Governance and Enforcement

| File | Role | Status |
|------|------|--------|
| `tools/supervisor/autonomous_cycle.py` | Autonomous sprint runner; TC-GUARD-001 BLOCK (Step 2d3); Step 1b healing gate (ADVISORY) | ACTIVE |
| `tools/supervisor/governance_validators.py` | 38+ validators; V45 (class names), V46 (skill_transcript WARN), V47 (spec_fact_refs) | ACTIVE — 3,077 lines |
| `tools/supervisor/check_system_healing_gate.py` | Healing gate; Lane 1: fods_facts_gte_10 (ADVISORY) | ACTIVE — checks existence, not workbench_count |
| `tests/specification-authority-layer/test_gap_int_002_product_source_fact_refs.py` | GAP-INT-002 integration test; checks FODS/FODT/ZST existence + ALL source FACT-* refs | ACTIVE — no source==workbench_verified check |
| `tests/specification-authority-layer/test_sal_runner_idempotency.py` | SAL idempotency tests for FODS, ZST, all-formats total >= 14000 | ACTIVE — does NOT test Gnumeric/ABW == 0 |
| `tests/supervisor/test_tc_guard_001_enforce.py` | TC-GUARD-001 regression tests (8 tests) | ACTIVE |

---

## 5. Spec Stubs and Architecture Layer (NEW since previous investigation)

| File | Role | Status |
|------|------|--------|
| `src/python/fods/spec/` (12 modules) | Architecture-only spec stubs; `spec_fact_ref = "FACT-FODS-006"` per class | ACTIVE — architecture_only; not production parser |
| `src/python/fods/spec/office/document.py` | Canonical class: Office.Document; spec_fact_ref: FACT-FODS-001 | architecture_only |
| `src/python/fods/spec/table/table_cell.py` | Canonical class: Table.TableCell; spec_fact_ref: FACT-FODS-006; facade: FodsCell | architecture_only |
| `src/python/fodt/spec/` | FODT architecture-only spec stubs | ACTIVE |
| `shared/qname-registry/fods.yaml` | 12 QNames mapped: QName → FACT-FODS-NNN → canonical class → Python/C# file | ACTIVE — all status: architecture_only |

---

## 6. Evidence and Authorization

| File | Role | Status |
|------|------|--------|
| `reports/authorizations/AUTH-SPEC-HEAL-20260621-002.yaml` | Delegation authorization: TC-V45-WIRING, TC-SAL-IDEMPOTENCY, TC-COMMIT-001 | ACTIVE |
| `reports/ff-arch-20260621-001/` | Forensics sprint outputs (machinery lifecycle) | NOT FOUND at this path — located at `reports/forensics-archaeology-20260621/` or `reports/machinery-lifecycle-forensics-20260621/` |
| `reports/spec-authority/spec-auth-inv-20260621-002/` | Prior partial spec-authority investigation | PARTIAL — 14 files exist (reference material) |
| `.local/spec-authority-machinery/spec-authority-machinery-explosion-20260621-827f5a52/` | This investigation's evidence bundle directory | CREATED — this run |

---

## 7. Product Source (spec authority wiring)

| File | FACT refs | Status |
|------|-----------|--------|
| `src/python/fods/neutral_model.py` | FACT-FODS-001 (multiple references) | WIRED |
| `src/python/fods/constants.py` | FACT-FODS-001 (QN_DOCUMENT, ATTR_MIMETYPE) | WIRED |
| `src/python/fods/Compat/` | FodsCell, FodsDocument, FodsSheet etc. | ACTIVE — facades added in commit 3024f68c |
| `src/python/fodt/neutral_model.py` | FACT-FODT-* references | WIRED (per GAP-INT-002 test) |
| `src/python/zst/zst_codec.py` | FACT-ZST-* references | WIRED (per GAP-INT-002 test) |
| `src/python/gnumeric/` | No FACT refs | NOT WIRED |
| `src/python/abw/` | No FACT refs | NOT WIRED |
| `src/python/csv/` | No FACT refs | NOT WIRED |

---

## 8. Item Count Summary

| Category | Count |
|----------|-------|
| SAL modules | 19-20 |
| Formats with workbench-verified facts | 10 (FODS, FODT, ZST, FODP, FODG, ODS, ODT, PPM, PGM, PBM) |
| Formats with 0 SAL facts | 12 (Gnumeric, ABW, ORA, QOI, XCF, ZPAQ, DIF, SYLK, CSV, TSV, XPM, PAM) |
| Gap ledger entries | 958 |
| Gap entries with stale spec_facts | 58 (all CSV) |
| Gap entries with authority_level | 0 |
| FODS QNames in registry | 12 |
| FODS spec stub classes | 12 (architecture_only) |
| FODS workbench-verified facts | 4,987 |
| FODS requirement packs | 3 |
| Total SAL facts in daily output | 14,284+ |
