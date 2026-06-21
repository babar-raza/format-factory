# Capability Layer Audit — ff-arch-20260621-001

## Summary

**Status: POPULATED but PARTIALLY CONNECTED**

The capability layer has 932 tracked gaps, format-specific capability maps, and a
gap ledger with spec fact references. A capability-to-feature compiler exists.
However, the compiler's SAL input (`sal-facts-latest.json`) does not exist,
and there is no automated pipeline from capabilities to product source.

---

## Capability Layer Files

| File | Contents | Status |
|------|----------|--------|
| reports/capability-layer/gap-ledger.json | 932 capability gaps with spec refs | EXISTS |
| reports/capability-layer/unified-capability-map.json | Unified map across formats | EXISTS |
| reports/capability-layer/commercial-capability-map.json | Commercial-tier capabilities | EXISTS |
| reports/capability-layer/foss-reduced-capability-map.json | FOSS-tier capabilities | EXISTS |
| reports/capability-layer/action-queue.json | Prioritized action queue | EXISTS |
| tools/supervisor/capability_compiler.py | Capability-to-feature compiler | EXISTS (but SAL input missing) |
| tools/supervisor/capability_queue_consumer.py | Consumes action queue | EXISTS |
| schemas/capability/capability_gap.schema.json | Gap schema | EXISTS |
| schemas/capability/capability_map.schema.json | Map schema | EXISTS |

---

## Gap Ledger Evidence

Total gaps: **932**

Sample gap structure (from gap-ledger.json):
```json
{
  "gap_id": "GAP-FODS-COMM-LOAD-001",
  "format": "FODS",
  "product_type": "commercial",
  "capability_name": "Load",
  "current_state": "implementation_verified",
  "status": "closed",
  "priority": "P0",
  "spec_facts": ["FACT-FODS-001", ..., "FACT-FODS-032"]
}
```

Spec facts ARE referenced in gap entries. The link from capability gaps to spec facts EXISTS.

---

## Capability-to-Feature Compiler Assessment

`tools/supervisor/capability_compiler.py`:
- EXISTS and has executable implementation
- Reads SAL facts from `.local/sal-output/sal-facts-latest.json`
- That file DOES NOT EXIST (not found in repo)
- When SAL file is missing, compiler returns empty facts (`{}`)
- Compiler generates feature IRs and taskcards from gap records
- Has no source code generation capability (generates taskcard YAML, not .cs/.py files)

**Gap: Compiler produces taskcards not source code. Source code generation is absent.**

---

## Does Capability Layer Consume SAL Facts?

**PARTIALLY.** Capability gaps reference `spec_facts` IDs. But:
1. The gap ledger was NOT auto-generated from SAL — it was manually curated
2. The capability compiler CAN read SAL facts (when available) to enrich taskcards
3. No automated pipeline: SAL → extract facts → populate gap ledger → compiler → generate source

---

## Capability-to-Feature Compiler Existence

YES — `tools/supervisor/capability_compiler.py` exists with:
- `load_sal_facts()` — reads SAL output
- `compile_gap_to_feature_ir()` — converts gap to feature IR
- `generate_taskcard()` — generates taskcard from feature IR
- CLI: `--gap-record '...' --output-dir ...`

**BUT: No code generator. Taskcards are produced, not source code.**

---

## Pipeline Gaps

| Missing Step | Impact |
|---|---|
| SAL pipeline not producing sal-facts-latest.json | Compiler has no spec inputs |
| Compiler produces taskcards, not source code | Source still handwritten |
| No automated QName → source path resolution | Classes placed at wrong locations |
| No post-generation validator | Cannot verify generated source meets spec |
| No regression test of compiler output | Output quality unknown |
