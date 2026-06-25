# Verification Plan — Spec Authority Layer Healing
## Run ID: spec-authority-machinery-explosion-20260625-c6b2470

---

## Pre-Healing Verification (Already Confirmed)

These gates were verified during the investigation and establish the baseline:

| Gate | Status | Result |
|------|--------|--------|
| VG-001: Gnumeric → P1 | VERIFIED | authority_level_int=1, product_expansion_allowed=false |
| VG-002: FODS → P6 | VERIFIED | authority_level_int=6, product_expansion_allowed=true |
| VG-009: Detector 19 fires for ODF without spec_fact_refs | VERIFIED | Fires, downgrades verdict |
| VG-010: authority_conveyor.py returns action plan | VERIFIED | Structured JSON output |
| VG-011: refresh_check.py reports stale entries | VERIFIED | 4 stale entries identified |
| VG-012: authority_integration_fabric NOT imported | VERIFIED | Zero matches in autonomous_cycle.py |
| VG-015: sal-facts-fods.json contains 4988 entries | VERIFIED | 4988 confirmed |

---

## Phase A Verification Tests

Run these tests to confirm Phase A repairs are complete:

### VG-003: TC-GUARD-001 BLOCKS gap_ledger_ref-only sprint

```bash
# Create minimal FODS PRODUCT_SOURCE declaration with only gap_ledger_ref
# Submit to autonomous_cycle.py and verify it adds to rework_items
python -c "
from tools.supervisor.autonomous_cycle import check_tc_guard_001
item = {
    'item_id': 'TEST-VG-003',
    'item_type': 'PRODUCT_SOURCE',
    'format': 'fods',
    'gap_ledger_ref': 'GAP-FODS-TEST-001'
    # spec_fact_refs: ABSENT
    # exception_classification: ABSENT
}
result = check_tc_guard_001(item)
print('PASS' if result == 'BLOCKED' else 'FAIL - still allowed without spec_fact_refs')
"
```

**Expected after Phase A**: BLOCKED

### VG-005: V13 FAILS absent spec_fact_refs for FODS

```bash
python -c "
from tools.supervisor.governance_validators import validate_spec_fact_refs_wired
declaration = {
    'format': 'fods',
    'items': [{'item_type': 'PRODUCT_SOURCE', 'item_id': 'TEST-VG-005'}],
    # spec_fact_refs: ABSENT
    # exception_classification: ABSENT
}
result = validate_spec_fact_refs_wired(declaration)
print('PASS' if not result.passed else 'FAIL - V13 did not fire for absent spec_fact_refs')
"
```

**Expected after Phase A**: V13 fires → blocks_sprint=True

### VG-006: V13 PASSES exception_classification for Gnumeric

```bash
python -c "
from tools.supervisor.governance_validators import validate_spec_fact_refs_wired
declaration = {
    'format': 'gnumeric',
    'exception_classification': 'schema_authority_available',
    'items': [{'item_type': 'PRODUCT_SOURCE', 'item_id': 'TEST-VG-006'}]
}
result = validate_spec_fact_refs_wired(declaration)
print('PASS' if result.passed else 'FAIL - V13 incorrectly blocked valid exception')
"
```

**Expected**: PASS (both before and after Phase A)

### VG-007: product_task_selector BLOCKS NDJSON without exception

```bash
python -c "
from tools.supervisor.product_task_selector import get_format_authority_status
status = get_format_authority_status('ndjson')
print('PASS' if 'BLOCKED' in status else f'FAIL - NDJSON returned {status} (should be BLOCKED at P2)')
"
```

**Expected after Phase A**: BLOCKED (currently returns ALLOWED from poc-targets)

---

## Phase B Verification Tests

### VG-018: FODS proof graph has 10+ facts

```python
import yaml
from pathlib import Path

graph_files = list(Path('.local/spec-cache/fods/1.3/workbench/reports').rglob('*proof-graph.yaml'))
assert graph_files, "No proof graph found"
g = yaml.safe_load(graph_files[0].read_text())
fact_count = len([k for k in g if k.startswith('FACT-FODS-')])
print(f'PASS - {fact_count} facts in proof graph' if fact_count >= 10 else f'FAIL - only {fact_count} facts')
```

---

## Phase C Verification Tests

### VG-013: authority_integration_fabric imported

```bash
grep -n "authority_integration_fabric" tools/supervisor/autonomous_cycle.py
# Expected: at least one match showing import and Step 0b call
```

### VG-014: FODS worker prompt contains spec facts

```bash
python tools/supervisor/generate_next_worker_prompt.py --format-id fods --output /tmp/test-prompt.txt
grep -c "FACT-FODS-" /tmp/test-prompt.txt
# Expected: 3+ matches
```

### VG-016: poc-targets.yaml has authority_level per format

```bash
python -c "
import yaml
poc = yaml.safe_load(open('product-capability-matrix/poc-targets.yaml').read())
formats_without_level = [fmt for fmt, data in poc.get('formats', {}).items() if 'authority_level' not in data]
print(f'PASS - all formats have authority_level' if not formats_without_level else f'FAIL - missing: {formats_without_level}')
"
```

### VG-017: 5 skills registered

```bash
grep -E "acquire-spec-t3|normalize-spec|extract-spec-facts|authority-gate-validation|pilot-rerun-authority" .supervisor/skill-registry.yaml
# Expected: 5 distinct matches
```

---

## Regression Tests

After each phase, run the full governance validator suite to confirm no regressions:

```bash
.venv/Scripts/pytest tests/supervisor/test_governance_validators.py -x -v
# Expected: 92 pass (all existing tests) + new Phase A tests
```

---

## Final Acceptance Criteria

Phase A is COMPLETE when:
- [ ] VG-003: TC-GUARD-001 blocks gap_ledger_ref-only sprint
- [ ] VG-005: V13 fires for absent spec_fact_refs (FODS PRODUCT_SOURCE)
- [ ] VG-006: V13 passes exception_classification (Gnumeric)
- [ ] VG-007: product_task_selector blocks NDJSON at P2
- [ ] VG-008: product_task_selector allows Gnumeric with exception
- [ ] 92+ governance validator tests pass
- [ ] No new regressions in autonomous_cycle.py tests
