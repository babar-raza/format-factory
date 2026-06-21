# Capability Layer Audit — Format Factory Machinery Audit v2
# Sprint ID: ff-machinery-readiness-audit-v2-20260621-827f5a52

## Capability Layer Data

### Gap Ledger
File: reports/capability-layer/gap-ledger.json
- schema_version: 1.0
- generated_at: 2026-06-21T16:06:07 (today, latest)
- sprint_id: FORMAT-FACTORY-CAPABILITY-FEATURE-UNDERSTANDING-LAYER-INVESTIGATIVE-HEALING-001
- total_gaps: 958
- Status distribution: {closed: 932, open: 26}
- Gaps WITH spec_facts: 625
- Gaps WITHOUT spec_facts: 333

### GAP Status Analysis

932 of 958 gaps are marked "closed". CRITICAL FINDING:
The prior audit documented that 932 gaps were "closed" from the previous run.
TODAY the gap ledger still shows 932 closed with 26 open.

This is suspicious — it means 932 capability gaps are considered done, but:
1. Many format products have minimal implementations
2. The gap ledger was generated in a single sprint from template data
3. The "closed" status tracks whether a function EXISTS in source code, not whether
   it is spec-backed, tests-proven, or Gate-ready

Evidence of false closure: XCF has 74 gaps, FODS has 67, FODT has 100, yet FODT
source is functional only at FOSS level, not approaching Gate 11 by spec criteria.

### Capability-to-Feature Compiler

`tools/supervisor/capability_compiler.py` EXISTS (newly discovered since prior audit):
- Usage: `python capability_compiler.py --gap-record '...' --output-dir ...`
- Reads SAL facts from `sal-facts-latest.json` (SAL output file)
- Generates feature IR and taskcards from gap records

BUT: It reads from `.local/sal-output/sal-facts-latest.json`, not from the workbench
cache at `.local/spec-cache/sal-facts-*.json`. These are DIFFERENT paths.

CRITICAL: `sal-facts-latest.json` is written by `sal_master_runner.py` in the old template mode.
The workbench-verified facts live in `sal-facts-fods.json` (workbench cache).
The compiler likely reads template facts (not workbench verified facts).

### `product_feature_factory.py`

`tools/supervisor/product_feature_factory.py` EXISTS but its connection to the
capability compiler is unknown without runtime inspection.

### Capability Map

`reports/capability-layer/foss-reduced-capability-map.json`:
- schema_version, generated_at, product_type, sprint_id, run_id — but no capability list in top keys
- Full capability map: reports/capability-layer/commercial-capability-map.json

Prior audit: "3,166 capabilities exist but are NOT derived from SAL facts. No capability-to-feature compiler."

Current state:
- Compiler EXISTS (capability_compiler.py)
- But reads from wrong SAL path
- Gap ledger is mostly "closed" without quality evidence
- The action-queue.json in reports/capability-layer/ shows items

### SAL → Capability Connection

| Step | Expected | Actual |
|------|----------|--------|
| SAL produces facts | FACT-FODS-NNN | WORKS (4987 facts) |
| Capability map derived from facts | capability_id links to FACT-* | NOT CONFIRMED |
| Gap ledger derived from capability | gap links to capability | PARTIALLY (625 with spec_facts) |
| Compiler reads SAL facts | reads workbench cache | READS WRONG PATH (latest.json) |
| Compiler generates taskcards | governed taskcards per gap | NOT WIRED INTO SPRINT LOOP |
| Gap consumer in task generation | reads gap-ledger.json | NOT CONFIRMED (was advisory_only: true) |

### Summary

The capability layer has DATA (958 gaps, capability maps) but the PIPELINE from
SAL → capability → feature → product is still not mechanically connected end-to-end.
The compiler exists but reads from the wrong SAL output file. The gap ledger shows
932 "closed" gaps which inflate closure rates without quality evidence.
