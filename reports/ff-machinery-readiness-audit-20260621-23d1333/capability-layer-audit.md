# Capability Layer Audit
# Sprint ID: ff-machinery-readiness-audit-20260621-23d1333

## Summary

The capability layer has 3,166 entries and 932 gap entries. It is the most complete layer
in terms of coverage data. However, capabilities are NOT derived from SAL spec facts —
they were derived from format-feature cross-product enumeration. The compiler from
capability to feature to code does NOT exist.

## Capability Map

| Metric | Value |
|--------|-------|
| Total capabilities | 3,166 |
| Total gaps | 932 |
| Gap severity field populated? | NO — all show `?` (not populated) |
| SAL-enriched? | CLAIMED (sal_enrichment field present) but NOT PROVEN (SAL is broken) |
| Compiler (capability → feature → code) | NOT FOUND |
| Downstream consumer | NOT FOUND |

## Capability IDs Structure

Format: `{FORMAT}-{PRODUCT_TYPE}-{FEATURE_NAME}-{SEQ}`
Example: `FODS-COMMERCIAL-LOAD-001`, `FODS-COMMERCIAL-EDIT_CELLS-001`

Capabilities cover: load, inspect, edit, add_sheet, rename_sheet, remove_sheet,
save_same_format, reload_and_verify, export_csv, export_html, export_json, etc.

This is a practical feature matrix, NOT a spec-derived hierarchy.

## Gap Ledger

| Metric | Value |
|--------|-------|
| Total gap entries | 932 |
| Formats covered | FODS, FODT, Netpbm, CSV, DIF, FODG, ABW, ZST, many others |
| Severity populated? | NO — all `?` |
| Gap format | `GAP-{FORMAT}-{TRACK}-{FEATURE}-{SEQ}` |
| Traceability to SAL facts | NOT PROVEN |
| Traceability to capability entries | CLAIMED but not validated |

## Capability-to-Feature Compiler

**Status: NOT FOUND**

The spec-to-feature-radical-correction-plan.md describes a "capability-to-feature compiler"
as a required component. No such tool was found in tools/supervisor/ or tools/.

The closest tool is `ai_implementation_designer.py` which uses an AI model to generate
feature plans — this is NOT a deterministic compiler from capability map to code.

## Proof Sufficiency

Capabilities claim SAL enrichment but this cannot be proven given the SAL is broken.
Gap ledger has 932 entries but severity is not populated, making prioritization impossible.
No link from specific capability to specific spec section or verified fact.

## Evidence Paths

- `reports/capability-layer/unified-capability-map.json` (3,166 entries)
- `reports/capability-layer/gap-ledger.json` (932 entries)
- `reports/capability-layer/commercial-capability-map.json`
- `reports/capability-layer/foss-reduced-capability-map.json`

## Required Fixes

1. Populate gap severity in gap-ledger.json (932 entries need severity)
2. Build deterministic capability-to-feature compiler (not AI-driven)
3. Wire SAL facts into capability derivation (currently disconnected)
4. Add spec_fact_refs to each capability entry (currently missing)
5. Create gap-to-taskcard promotion pipeline (tools exist but not wired)
