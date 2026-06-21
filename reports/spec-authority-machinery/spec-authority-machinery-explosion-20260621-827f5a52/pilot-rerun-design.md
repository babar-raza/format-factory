# Spec Authority Machinery — Pilot Rerun Design

**Run ID:** `spec-authority-machinery-explosion-20260621-827f5a52`
**Date:** 2026-06-21

---

## Pilot 1: Positive Pilot — FODS P5 Chain Verification

**Objective:** Prove the full FODS spec authority chain end-to-end: spec → fact → stub → registry → product → test.

**Why viable NOW (improvements since original plan):**
- 4,987 workbench-verified facts in SAL output
- 3 req-packs available
- 12 spec stubs with `spec_fact_ref` on each class
- 12 QName registry entries with full chain
- Compat facades exist (FodsCell, FodsDocument, FodsSheet)
- GAP-INT-002 already verifies FODS fact citations

### Environment
```
Repository: c:\Users\prora\OneDrive\Documents\GitHub\format-factory
Branch: main
HEAD: ed51041f
SAL output: .local/sal-output/sal-facts-latest.json (2026-06-21T21:28:38)
Workbench: .local/spec-cache/fods/1.3/workbench/verified-facts-review.yaml
```

### Official Entry Points
1. `sal_master_runner.run_sal_pipeline(["fods"], from_cache_only=True)`
2. `test_gap_int_002_product_source_fact_refs.py::TestProductSourceFactRefs`
3. `test_sal_runner_idempotency.py::test_fods_idempotent_fact_count`

### Primary Chain Test

```python
# test_fods_p5_chain.py (proposed — to be created in next sprint)
import json
from pathlib import Path

REPO = Path(__file__).parent.parent.parent
SAL = json.load(open(REPO / '.local/sal-output/sal-facts-latest.json'))

def test_fact_fods_006_exists_in_sal_with_workbench_source():
    for r in SAL['results']:
        if r['format_id'] == 'fods':
            match = [f for f in r['spec_facts'] if f.get('qname') == 'FACT-FODS-006']
            assert match, "FACT-FODS-006 not in SAL output"
            assert match[0].get('source') == 'workbench_verified'
            return
    assert False, "FODS not in SAL results"

def test_table_cell_spec_fact_ref():
    stub = REPO / 'src/python/fods/spec/table/table_cell.py'
    content = stub.read_text()
    assert 'spec_fact_ref = "FACT-FODS-006"' in content

def test_qname_registry_maps_table_cell():
    import yaml
    reg = yaml.safe_load(open(REPO / 'shared/qname-registry/fods.yaml').read())
    tc_entry = next((e for e in reg if e.get('qname') == 'table:table-cell'), None)
    assert tc_entry is not None
    assert tc_entry.get('spec_fact_ref') == 'FACT-FODS-006'

def test_neutral_model_cites_fact_ref():
    model = (REPO / 'src/python/fods/neutral_model.py').read_text()
    assert 'FACT-FODS-001' in model
```

### Negative Controls
1. Verify Gnumeric has 0 SAL workbench facts (`test_gnumeric_zero_sal_facts`)
2. Verify FACT-CSV-001 is NOT in SAL output
3. Verify bootstrap_only facts do NOT have `source: workbench_verified`

### Expected Outcome: PASS

---

## Pilot 2: Bypass Detection Pilot — Zero-Fact Format Analysis

**Objective:** Prove that the system can detect and report when a product item is declared for a format with no spec authority, and that a human reviewer would have clear visibility of the bypass path.

**Focus:** CSV (most impactful — has stale spec_facts creating false confidence)

### Stale Ref Detection
```python
# Run from repo root
python -c "
import json
gaps = json.load(open('reports/capability-layer/gap-ledger.json'))['gaps']
sal = json.load(open('.local/sal-output/sal-facts-latest.json'))
sal_ids = {f.get('qname','') for r in sal['results'] for f in r.get('spec_facts',[])}
csv_stale = [(g['gap_id'], g['spec_facts']) for g in gaps
             if g.get('format')=='CSV' and any(sf not in sal_ids for sf in g.get('spec_facts',[]))]
print(f'CSV gaps with stale fact refs: {len(csv_stale)}')
print('Sample:', csv_stale[:3])
"
```
**Expected:** 58 gaps with stale refs.

### TC-GUARD-001 Bypass Path
```python
# Demonstrate that a CSV gap satisfies TC-GUARD-001
declaration_item = {
    "item_id": "TEST-CSV-001",
    "item_type": "PRODUCT_SOURCE",
    "gap_ledger_ref": "GAP-CSV-FOSS-PROBE_CSV-001",  # has stale FACT-CSV-001/002
    "evidence_paths": ["src/python/csv/csv_parser.py"]
}
# TC-GUARD-001 accepts this because gap_ledger_ref is present
# Even though GAP-CSV-FOSS-PROBE_CSV-001 has no real spec backing
```
**Expected finding:** TC-GUARD-001 PASSES despite no real spec authority.

### Idempotency Check (zero-fact formats)
```python
from sal_master_runner import run_sal_pipeline
r = run_sal_pipeline(["csv", "gnumeric", "abw"], from_cache_only=True)
for entry in r["results"]:
    assert entry["workbench_verified_fact_count"] == 0, f"Unexpected wb facts for {entry['format_id']}"
```
**Expected:** All zero; any nonzero would indicate inadvertent template fact introduction.

---

## Pilot 3: SAL Idempotency Pilot (Existing Tests)

**Run:** `pytest tests/specification-authority-layer/test_sal_runner_idempotency.py -v`

Tests:
- `test_fods_idempotent_fact_count`: TWO FODS runs → same fact count
- `test_fods_idempotent_fact_ids`: TWO FODS runs → same fact ID set
- `test_zst_idempotent_fact_count`: Same for ZST
- `test_zst_idempotent_fact_ids`: Same for ZST
- `test_all_formats_idempotent_total`: All formats → same total; >= 14,000

**Gap:** No test for `test_gnumeric_zero_idempotent()` or `test_csv_zero_idempotent()`.

---

## Pilot 4: Authority Regression Pilot (To Be Created)

**Objective:** Detect regressions where template facts are re-added to zero-fact formats.

```python
def test_no_template_fact_regression_for_zero_formats():
    """Ensure formats with 0 workbench facts have 0 SAL facts in from_cache_only mode."""
    from sal_master_runner import run_sal_pipeline
    ZERO_FACT_FORMATS = ["gnumeric", "abw", "csv", "tsv", "sylk", "dif"]
    r = run_sal_pipeline(ZERO_FACT_FORMATS, from_cache_only=True)
    for entry in r["results"]:
        fid = entry["format_id"]
        count = len(entry["spec_facts"])
        assert count == 0, f"{fid} has {count} facts in from_cache_only mode — regression!"
```
