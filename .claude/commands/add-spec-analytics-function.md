# /add-spec-analytics-function

## Purpose
Add one spec-backed domain analytics function to a format's canonical domain module.
This skill is ONLY for functions directly grounded in a SAL spec fact (FACT-FORMAT-N).
Arithmetic rotation functions (`_mod_N_times_N`) are permanently forbidden.

## Prerequisites
- [ ] Gap exists in gap-ledger.json with status: open
- [ ] At least one spec_fact in gap.spec_facts verified in SAL output
- [ ] Target module is a domain module (not *_analytics.py, not *_analytics_extra.py)
- [ ] Target module is within baseline_loc_cap (check registry/source-structure-baseline.json)
- [ ] Function name does not contain `_mod_` or `_times_`

## Required Inputs
- format_id: (e.g., abw)
- function_name: (e.g., abw_total_sentence_count)
- target_module: (e.g., src/python/abw/analysis/text_metrics.py)
- spec_fact_ref: (e.g., FACT-ABW-015)
- gap_ledger_ref: (e.g., GAP-ABW-FOSS-ABW_TOTAL_SE-001)
- formula: (exact formula as string or prose description)
- expected_values: (list of test vectors with inputs and expected outputs)
- focused_test_command: (.venv/Scripts/pytest tests/python/<format>/test_*.py -v --tb=short)

## Allowed Paths

- `src/python/<format>/` — domain module files only (not *_analytics.py or *_analytics_extra.py)
- `tests/python/<format>/` — test files for the added function
- `reports/capability-layer/gap-ledger.json` — close the gap entry
- `reports/all-format-deepening/product-code-ledger.json` — add ledger entry
- `.local/transcripts/` — skill invocation transcript

## Forbidden Paths

- `src/python/<format>/<format>_analytics.py` (HARD BLOCK)
- `src/python/<format>/<format>_analytics_extra.py` (HARD BLOCK)
- Any file matching `*_extra.py`, `*_misc.py`
- Any function name containing `_mod_` or `_times_`

## Stop Conditions

Stop and report `BLOCKED` if:
- The gap entry does not exist or has `status != open`
- The spec_fact_ref is not in the SAL cache (run `/ingest-spec-sal` first)
- The target module is at or above its `baseline_loc_cap`
- The function name contains `_mod_` or `_times_`

## Steps

### Step 1: Verify gap is open
```python
import json
from pathlib import Path
gap_ledger = json.loads(Path('reports/capability-layer/gap-ledger.json').read_text(encoding='utf-8'))
gaps = gap_ledger.get('gaps', gap_ledger) if isinstance(gap_ledger, dict) else gap_ledger
gap = next((g for g in gaps if isinstance(g, dict) and g.get('gap_id') == '<gap_ledger_ref>'), None)
assert gap is not None, "Gap not found in ledger"
assert gap.get('status') == 'open', f"Gap status is not open: {gap.get('status')}"
```

### Step 2: Verify spec_fact_ref exists in SAL
```
python tools/spec/query_sal.py <spec_fact_ref>
```
Expected: fact returned with description. If not found: STOP — run `/ingest-spec-sal` first.

### Step 3: Identify target module and check LOC cap
```python
import json
from pathlib import Path
baseline = json.loads(Path('registry/source-structure-baseline.json').read_text(encoding='utf-8'))
# Target module must NOT be *_analytics.py or *_analytics_extra.py
# Check LOC cap:
known = baseline.get('known_violations', {})
entry = known.get('<target_module_rel_path>', {})
cap = entry.get('baseline_loc_cap', 800)
current_loc = sum(1 for _ in open('<target_module>', encoding='utf-8'))
assert current_loc < cap, f"LOC {current_loc} at or above cap {cap}"
```

### Step 4: Write function with spec attribution
Add to the identified target module:
```python
def <function_name>(<params>) -> <return_type>:
    """<docstring describing the metric>.

    Source: <spec_fact_ref>
    Gap: <gap_ledger_ref>
    """
    # Implementation
    ...
```

### Step 5: Write test with at least 2 vectors
```python
# In tests/python/<format>/test_<function_name>.py
class Test<FunctionName>:
    def test_basic_case(self, ...):
        ...
    def test_edge_case(self, ...):
        ...
```

### Step 6: Run focused test
```
.venv/Scripts/pytest <test_path> -v --tb=short
```
All tests must pass before proceeding.

### Step 7: New architecture violation check
Run the inline detector from CLAUDE.md §Closeout-0 if src/python/ was modified.

### Step 8: Close gap in ledger
Set `status: "closed"` in gap-ledger.json for the gap entry.

### Step 9: Add product-code ledger entry
```json
{
  "entry_id": "<gap_id>-<date>",
  "skill_id": "add-spec-analytics-function",
  "gap_ledger_ref": "<gap_id>",
  "spec_fact_refs": ["<spec_fact_ref>"],
  "changed_files": ["src/python/<format>/<module>.py"],
  "test_files": ["tests/python/<format>/test_<function>.py"],
  "committed_at": null
}
```

### Step 10: Write skill invocation transcript
Path: `.local/transcripts/add-spec-analytics-function-<gap_id>-<ts>.yaml`

## Evidence
- [ ] spec_fact_ref verified in SAL: PASS/FAIL
- [ ] function targets domain module (not analytics.py): PASS/FAIL
- [ ] LOC within baseline_loc_cap: PASS/FAIL
- [ ] Focused tests pass: PASS/FAIL
- [ ] No `_mod_` or `_times_` in function name: PASS/FAIL
- [ ] Gap closed in ledger: PASS/FAIL
- [ ] Product-code ledger entry added: PASS/FAIL
