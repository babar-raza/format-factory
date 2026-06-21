# Spec Authority Machinery — Healing Roadmap

**Run ID:** `spec-authority-machinery-explosion-20260621-827f5a52`
**Date:** 2026-06-21

---

## Phase A: Quick Wins (Current Sprint or Next Sprint)

### A1 — Fix CSV gap-ledger stale spec_facts (RCA-GAP-LEDGER-CSV-STALE)
**Priority:** HIGH
**Work:**
1. Clear `spec_facts: ['FACT-CSV-001', 'FACT-CSV-002']` from all 58 CSV gap entries
2. Set `spec_facts: []` for all CSV gaps (CSV has 0 workbench facts)
3. Document as resolved in authority-debt-ledger.json
**Verification:** `python -c "import json; g=json.load(open('reports/capability-layer/gap-ledger.json')); csv=[x for x in g['gaps'] if x.get('format')=='CSV' and x.get('spec_facts')]; print(len(csv), 'stale')"` → should print `0 stale`
**Status:** NOT YET DONE

### A2 — Switch SAL daily output to from_cache_only mode (RCA-SAL-DEFAULT-MODE)
**Priority:** HIGH
**Work:**
1. Find the script/command that generates `sal-facts-latest.json` daily
2. Add `from_cache_only=True` parameter to the invocation
3. Regenerate `sal-facts-latest.json` in clean mode
4. Verify template facts gone from FODS output (should be 4,987, no bootstrap_only)
**Verification:** `python -c "import json; s=json.load(open('.local/sal-output/sal-facts-latest.json')); bt=sum(1 for r in s['results'] for f in r['spec_facts'] if f.get('fact_status')=='bootstrap_only'); print('bootstrap_only:', bt)"` → should print `bootstrap_only: 0`
**Status:** NOT YET DONE

### A3 — Add authority_level to gap-ledger entries (RCA-GAP-LEDGER-NO-AUTH-LEVEL)
**Priority:** MEDIUM
**Work:**
1. Load SAL facts; build `workbench_verified_count` per format
2. Derive `authority_level` per gap: `"P5"` if wb_count >= 1000, `"P3"` if >= 10, `"P1"` if >= 1, `"P0"` if 0
3. Update gap-ledger JSON with `authority_level` field on each entry
**Verification:** `python -c "import json; g=json.load(open('reports/capability-layer/gap-ledger.json')); print(sum(1 for x in g['gaps'] if x.get('authority_level')))"` → should print `958`
**Status:** NOT YET DONE

### A4 — Add explicit source check to GAP-INT-002 (RCA-GAP-INT-002-NO-SOURCE-CHECK)
**Priority:** HIGH
**Work:**
1. In `_load_sal_facts()` in `test_gap_int_002_product_source_fact_refs.py`: filter to `source == 'workbench_verified'`
2. Add test `test_all_sal_fact_sources_are_workbench_verified()` that asserts all facts in index have source field
3. Verify test still passes for FODS/FODT/ZST
**Verification:** Tests pass; bootstrap-only fact IDs no longer in the SAL index used by GAP-INT-002
**Status:** NOT YET DONE

### A5 — Add workbench_count criterion to healing gate Lane 1 (RCA-HEALING-GATE-DEPTH-001)
**Priority:** MEDIUM
**Work:**
1. In `check_system_healing_gate.py` Lane 1: add check that reads `sal-facts-latest.json` and checks `workbench_verified_fact_count > 0` for FODS, FODT, ZST
2. New criterion: `fods_workbench_verified_count_positive: true`
3. Update lane_results JSON accordingly
**Verification:** Gate JSON shows new criterion; passes for FODS/FODT/ZST; would fail if those counts were 0
**Status:** NOT YET DONE

---

## Phase B: FODS Positive Pilot Verification

### B1 — TC-0021 FODS Req Pack Traceability Review
**Priority:** MEDIUM
**Work:**
1. Read `parser-requirements.yaml` (10 requirements)
2. For each requirement, verify the cited FACT-FODS-NNN exists in `sal-facts-latest.json`
3. Document any requirements that cannot be traced
**Status:** PENDING — no blocking dependency

### B2 — FODS Proof Chain E2E Test
**Priority:** MEDIUM
**Work:**
1. Create `test_fods_proof_chain_p5.py`:
   - FACT-FODS-006 exists in SAL output with `source: workbench_verified`
   - `table_cell.py` spec stub has `spec_fact_ref = "FACT-FODS-006"`
   - `fods.yaml` QName registry maps `table:table-cell` to `FACT-FODS-006`
   - `neutral_model.py` cites `FACT-FODS-001`
   - All three verifications form a chain test
**Status:** NOT YET CREATED

---

## Phase C: Medium-Term Enforcement

### C1 — SAL → autonomous_cycle minimal integration (RCA-SUPERVISOR-GATES-001)
**Priority:** CRITICAL (highest ROI from authority chain perspective)
**Work:**
1. In `autonomous_cycle.py` Step 1c (new): read `sal-facts-latest.json`; extract `workbench_verified_fact_count` per format
2. In Step 2d3 (TC-GUARD-001): if gap's format has 0 workbench facts, emit advisory warning to sprint context
3. Gate remains non-blocking initially; documents the gap in sprint output
**Status:** NOT YET DONE — no blocker

### C2 — Upgrade V46 to BLOCK mode
**Priority:** LOW (after bootstrap phase completes)
**Pre-condition:** New skills adopted across all PRODUCT_SOURCE items
**Work:** Change `blocks_sprint: False` to `blocks_sprint: True` in V46 validator after 90% adoption rate achieved
**Status:** NOT YET DONE — requires adoption first

### C3 — Zero-fact format documentation in authority-debt-ledger.json
**Priority:** MEDIUM
**Work:**
1. Create `authority-debt-ledger.json` (see Phase D)
2. Add entry for each format with 0 workbench facts documenting the reason and recommended path
3. Update healing gate Lane 1 to verify the ledger exists
**Status:** CREATED IN PHASE D of this investigation

---

## Phase D: Future Gates

### D1 — Add FODT QName registry
**Priority:** MEDIUM
**Work:** Create `shared/qname-registry/fodt.yaml` with FODT QNames mapped to workbench facts
**Status:** NOT YET DONE

### D2 — Add workbench extraction for ZST expansion
**Priority:** LOW
**Work:** ZST has only 94 workbench facts; expand workbench YAML to cover more format elements
**Status:** NOT YET DONE

### D3 — Investigate FODP/FODG/ODS/ODT 1,066-fact pattern (RCA-FODFAM-CHAIN)
**Priority:** MEDIUM
**Work:** Audit workbench YAMLs for FODP/FODG/ODS/ODT; verify each fact is format-specific
**Status:** NOT YET DONE

---

## Phase Summary

| Phase | Items | Priority | Status |
|-------|-------|---------|--------|
| A — Quick Wins | A1-A5 | HIGH/MEDIUM | NOT STARTED |
| B — FODS Pilot | B1-B2 | MEDIUM | NOT STARTED |
| C — Enforcement | C1-C3 | CRITICAL/LOW | NOT STARTED |
| D — Future | D1-D3 | MEDIUM/LOW | NOT STARTED |

**Recommended next sprint:** Execute A1, A2, A4 (stale refs, clean SAL mode, GAP-INT-002 source check) — highest ROI in reducing false confidence.
