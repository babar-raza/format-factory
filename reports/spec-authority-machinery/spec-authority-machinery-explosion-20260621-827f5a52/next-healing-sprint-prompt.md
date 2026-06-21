# Next Healing Sprint Prompt

**Run ID:** `spec-authority-machinery-explosion-20260621-827f5a52`
**Date:** 2026-06-21
**Mission:** Fix the 4 highest-priority spec authority gaps identified in this investigation

---

## Context: What Is Already Done (DO NOT REDO)

The following work is COMPLETE and must not be repeated or reversed:
- SAL idempotency fix (`from_cache_only=True` code path is clean) — commit `827f5a52`
- TC-GUARD-001 BLOCK mode — commit `83f062cf`
- FODS spec stubs (12 architecture-only classes with spec_fact_ref) — commit `8ca43a12`
- QName registry fods.yaml (12 QNames) — commit `8ca43a12`
- V45 validator (BLOCK: format-prefixed names) — commit `827f5a52`
- V47 validator (BLOCK: spec_fact_refs field) — commit `3024f68c`
- FODS/FODT Compat facades — commit `3024f68c`
- ABW/Gnumeric gap-ledger spec_facts cleaned (empty) — done

---

## Sprint Target: 4 Repairs

### Repair 1 (CRITICAL): Fix CSV gap-ledger stale spec_facts

**Root cause:** RCA-GAP-LEDGER-CSV-STALE
**What to do:**
1. Load `reports/capability-layer/gap-ledger.json`
2. For all gaps where `format == "CSV"` and `spec_facts` is non-empty:
   - Set `spec_facts: []` (CSV has 0 workbench SAL facts; FACT-CSV-001/002 are dead refs)
3. Write the updated gap-ledger.json
4. Do NOT modify any other gap entries

**Verification:**
```bash
python -c "
import json
g = json.load(open('reports/capability-layer/gap-ledger.json'))
stale = [x for x in g['gaps'] if x.get('format')=='CSV' and x.get('spec_facts')]
print(f'CSV stale gaps remaining: {len(stale)}')
"
```
Expected: `CSV stale gaps remaining: 0`

**Forbidden paths:**
- Do NOT add FACT-CSV-001/002 to SAL output (CSV has no workbench YAML)
- Do NOT create fake workbench facts for CSV
- Do NOT modify non-CSV gap entries

---

### Repair 2 (HIGH): Add source filter to GAP-INT-002

**Root cause:** RCA-GAP-INT-002-NO-SOURCE-CHECK
**File:** `tests/specification-authority-layer/test_gap_int_002_product_source_fact_refs.py`

**What to do:**
1. In `_load_sal_facts()`: add filter `if fact.get('source') == 'workbench_verified'`
2. Add two new tests:
   ```python
   def test_gnumeric_has_zero_sal_workbench_facts(self, sal_index):
       assert "gnumeric" not in sal_index or len(sal_index.get("gnumeric", set())) == 0

   def test_abw_has_zero_sal_workbench_facts(self, sal_index):
       assert "abw" not in sal_index or len(sal_index.get("abw", set())) == 0
   ```
3. Ensure existing FODS/FODT/ZST tests still pass after the filter is applied (they should — all cited facts are workbench_verified)

**Verification:**
```bash
.venv/Scripts/pytest tests/specification-authority-layer/test_gap_int_002_product_source_fact_refs.py -v
```
Expected: ALL PASS (including 2 new tests)

**Forbidden paths:**
- Do NOT reduce the minimum fact count thresholds
- Do NOT remove the `test_total_fact_refs_across_product_source` test
- Do NOT modify SAL output files

---

### Repair 3 (HIGH): Switch SAL daily output to from_cache_only mode

**Root cause:** RCA-SAL-DEFAULT-MODE
**What to do:**
1. Find the invocation that generates `sal-facts-latest.json` (search for `run_sal_pipeline` calls that use default mode in scripts/cron/CI)
2. Add `from_cache_only=True` parameter to that invocation
3. Regenerate `sal-facts-latest.json` in clean mode
4. Verify: `python -c "import json; s=json.load(open('.local/sal-output/sal-facts-latest.json')); bt=sum(1 for r in s['results'] for f in r['spec_facts'] if f.get('fact_status')=='bootstrap_only'); print(f'bootstrap_only: {bt}')"`  → should print `bootstrap_only: 0`

**Caution:** After switching to clean mode, the total fact count will decrease (template facts removed). Update `test_all_formats_idempotent_total` assertion if needed (check `assert total1 >= 14000` — if clean-mode total drops below 14000, lower the assertion to the clean-mode count).

**Verification:**
```bash
.venv/Scripts/pytest tests/specification-authority-layer/ -v
```
Expected: all tests pass.

**Forbidden paths:**
- Do NOT add template facts to any format's workbench YAML
- Do NOT reduce the workbench fact count (clean mode should still have 4,987+ FODS facts)

---

### Repair 4 (MEDIUM): Add workbench_count check to healing gate Lane 1

**Root cause:** RCA-HEALING-GATE-DEPTH-001
**File:** `tools/supervisor/check_system_healing_gate.py`

**What to do:**
1. In Lane 1 handler: load `sal-facts-latest.json`
2. Extract `workbench_verified_fact_count` for FODS and FODT
3. Add criteria:
   ```python
   "fods_workbench_verified_count_positive": fods_wb_count > 0,
   "fodt_workbench_verified_count_positive": fodt_wb_count > 0,
   ```
4. Lane 1 still passes (both should be positive with current workbench)
5. Gate output JSON includes the new criteria

**Verification:**
```bash
python tools/supervisor/check_system_healing_gate.py --json | python -c "import json,sys; d=json.load(sys.stdin); lane1=[l for l in d['lane_results'] if l['lane']==1][0]; print(lane1['checks'])"
```
Expected: both new criteria appear and are `true`.

**Forbidden paths:**
- Do NOT change the gate mode from ADVISORY to BLOCKING (this is a future step)
- Do NOT fail the gate for formats without workbench facts (only check FODS and FODT)

---

## Required Evidence

For sprint acceptance, provide:
1. Gap-ledger: CSV entries have `spec_facts: []` (script output showing 0 stale)
2. GAP-INT-002 tests: all pass, including `test_gnumeric_has_zero_sal_workbench_facts` and `test_abw_has_zero_sal_workbench_facts`
3. SAL daily output: `bootstrap_only: 0` from the verification command
4. Healing gate output: `fods_workbench_verified_count_positive: true` in Lane 1 checks
5. Full test run: `pytest tests/specification-authority-layer/ -v` — all pass

## Next Sprint Scope NOT Including

- Upgrading V46 to BLOCK mode (requires adoption audit first)
- Creating FODT QName registry (Phase D — lower priority)
- Full SAL → autonomous_cycle integration (Phase C — separate sprint)
- TC-0021 req-pack traceability review (B1 — separate sprint)
- Gnumeric/ABW spec acquisition (requires external resource — BLOCKED_EXTERNAL_CANDIDATE)
