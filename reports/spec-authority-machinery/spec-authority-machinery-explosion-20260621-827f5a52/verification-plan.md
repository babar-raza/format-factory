# Spec Authority Machinery — Verification Plan

**Run ID:** `spec-authority-machinery-explosion-20260621-827f5a52`
**Date:** 2026-06-21

---

## Verification Categories

### Category 1: SAL Pipeline Correctness (6 checks)

| Check ID | Description | Expected | Current Status |
|----------|-------------|----------|----------------|
| VC-SAL-001 | `sal-facts-latest.json` exists and generated within 24h | EXISTS, fresh | PASS |
| VC-SAL-002 | FODS workbench_verified_fact_count >= 4000 | >= 4000 | PASS (4,987) |
| VC-SAL-003 | FODT workbench_verified_fact_count >= 1000 | >= 1000 | PASS (4,933) |
| VC-SAL-004 | Gnumeric workbench_verified_fact_count == 0 | == 0 | PASS (0) |
| VC-SAL-005 | ABW workbench_verified_fact_count == 0 | == 0 | PASS (0) |
| VC-SAL-006 | SAL daily output uses from_cache_only=True (no bootstrap_only facts) | 0 bootstrap_only | FAIL — ~22 bootstrap_only in FODS (RCA-SAL-DEFAULT-MODE) |

### Category 2: Gap-Ledger Integrity (4 checks)

| Check ID | Description | Expected | Current Status |
|----------|-------------|----------|----------------|
| VC-GAP-001 | ABW gap entries: spec_facts == [] | All empty | PASS (cleaned) |
| VC-GAP-002 | Gnumeric gap entries: spec_facts == [] | All empty | PASS (cleaned) |
| VC-GAP-003 | CSV gap entries: spec_facts == [] OR all IDs exist in SAL | All valid | FAIL — 116 stale refs (FACT-CSV-001/002) |
| VC-GAP-004 | authority_level field present on all gap entries | 958/958 | FAIL — 0/958 have field |

### Category 3: Enforcement Gates (5 checks)

| Check ID | Description | Expected | Current Status |
|----------|-------------|----------|----------------|
| VC-GATE-001 | TC-GUARD-001 in BLOCK mode | BLOCK | PASS |
| VC-GATE-002 | V45 validator in BLOCK mode | BLOCK | PASS |
| VC-GATE-003 | V47 validator in BLOCK mode | BLOCK | PASS |
| VC-GATE-004 | V46 validator in BLOCK mode | BLOCK (target) | FAIL — WARN only |
| VC-GATE-005 | autonomous_cycle.py reads SAL facts | READS SAL | FAIL — NOT CONNECTED |

### Category 4: GAP-INT-002 Test Quality (4 checks)

| Check ID | Description | Expected | Current Status |
|----------|-------------|----------|----------------|
| VC-INT-001 | GAP-INT-002 filters SAL index to workbench_verified only | source filter present | FAIL — no filter |
| VC-INT-002 | GAP-INT-002 asserts Gnumeric SAL count == 0 | assertion present | FAIL — not present |
| VC-INT-003 | GAP-INT-002 asserts ABW SAL count == 0 | assertion present | FAIL — not present |
| VC-INT-004 | GAP-INT-002 FODS/FODT/ZST fact count checks pass | PASS | PASS |

### Category 5: FODS Proof Chain (5 checks)

| Check ID | Description | Expected | Current Status |
|----------|-------------|----------|----------------|
| VC-FODS-001 | FACT-FODS-006 in SAL with source==workbench_verified | YES | PASS |
| VC-FODS-002 | table_cell.py spec_fact_ref == "FACT-FODS-006" | MATCH | PASS |
| VC-FODS-003 | fods.yaml maps table:table-cell to FACT-FODS-006 | MAPPED | PASS |
| VC-FODS-004 | neutral_model.py cites FACT-FODS-001 | CITED | PASS |
| VC-FODS-005 | TC-0021 req-pack traceability verified | ALL REQS TRACED | PENDING |

### Category 6: Healing Gate Depth (3 checks)

| Check ID | Description | Expected | Current Status |
|----------|-------------|----------|----------------|
| VC-HEAL-001 | Healing gate Lane 1 checks workbench_verified_count > 0 | criterion present | FAIL — checks fods_facts_gte_10 only |
| VC-HEAL-002 | Healing gate passes in current state | PASS | PASS (for current state) |
| VC-HEAL-003 | Healing gate mode is ENFORCING (not ADVISORY) | ENFORCING | FAIL — ADVISORY |

---

## Verification Execution Commands

```bash
# VC-SAL-006: Check bootstrap_only count in daily SAL output
python -c "
import json
s = json.load(open('.local/sal-output/sal-facts-latest.json'))
bt = sum(1 for r in s['results'] for f in r['spec_facts'] if f.get('fact_status')=='bootstrap_only')
print(f'bootstrap_only facts: {bt}')
"

# VC-GAP-003: Check CSV stale refs
python -c "
import json
g = json.load(open('reports/capability-layer/gap-ledger.json'))
stale = [(x['gap_id'], x['spec_facts']) for x in g['gaps'] if x.get('format')=='CSV' and x.get('spec_facts')]
print(f'CSV gaps with stale refs: {len(stale)}')
"

# VC-FODS-001: Verify FACT-FODS-006 in SAL
python -c "
import json
s = json.load(open('.local/sal-output/sal-facts-latest.json'))
for r in s['results']:
    if r['format_id']=='fods':
        match = [f for f in r['spec_facts'] if f.get('qname')=='FACT-FODS-006']
        print(f'FACT-FODS-006: {match}')
        break
"

# Run GAP-INT-002 tests
.venv/Scripts/pytest tests/specification-authority-layer/test_gap_int_002_product_source_fact_refs.py -v

# Run SAL idempotency tests
.venv/Scripts/pytest tests/specification-authority-layer/test_sal_runner_idempotency.py -v
```

---

## Pass/Fail Summary

| Category | Total | PASS | FAIL | PENDING |
|----------|-------|------|------|---------|
| SAL Pipeline | 6 | 5 | 1 | 0 |
| Gap-Ledger | 4 | 2 | 2 | 0 |
| Enforcement Gates | 5 | 3 | 2 | 0 |
| GAP-INT-002 | 4 | 1 | 3 | 0 |
| FODS Proof Chain | 5 | 4 | 0 | 1 |
| Healing Gate Depth | 3 | 1 | 2 | 0 |
| **Total** | **27** | **16** | **10** | **1** |

**59% PASS rate.** Primary failures: SAL default mode, GAP-INT-002 source filter, enforcement depth gaps.
