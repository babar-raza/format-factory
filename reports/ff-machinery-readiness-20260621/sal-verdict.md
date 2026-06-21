# SAL (Specification Authority Layer) Verdict
# Run: ff-machinery-readiness-20260621-3024f68c
# Generated: 2026-06-21

## Verdict: ACTIVE_BUT_INCOMPLETE — PILOT_ONLY

SAL is active for ODF formats (FODS/FODT have thousands of facts) but is NOT production-ready:
- 3 of 20 tools are actively used; 17 are ghost infrastructure
- Facts are never regenerated automatically
- Non-ODF formats have 0 extracted facts
- SAL output (verified-facts-review.yaml) is NOT consumed by capability layer or source generator

## Evidence

### Facts by Format
| Format | Verified Facts | Source |
|--------|----------------|--------|
| FODS | 4991 | `.local/spec-cache/fods/1.3/normalized/` |
| FODT | 4936 | `.local/spec-cache/fodt/odf-1.3/workbench/` |
| FODG | 1083 | `.local/spec-cache/fodg/extracted/workbench/` |
| ODS | 1083 | `.local/spec-cache/ods/extracted/workbench/` |
| ODT | 1083 | `.local/spec-cache/odt/extracted/workbench/` |
| FODP | 1083 | `.local/spec-cache/fodp/extracted/workbench/` |
| ZST | 96 | `.local/spec-cache/zst/` |
| CSV | 2 | `.local/spec-cache/csv/rfc4180/` |
| PBM/PGM/PPM | 2 each | `.local/spec-cache/{format}/netpbm-spec/` |
| ABW | 0 | spec-index.yaml only |
| DIF | 0 | spec-index.yaml only |
| Gnumeric | 0 | spec-index.yaml only |
| NDJSON | 0 | none |
| TSV | 0 | none |

### Active Tools (3 of 20)
1. `normalize_pdf.py` — PDF → text extraction (FODS only)
2. `build_citation_map.py` — citation maps (FODS only)
3. `sal_master_runner.py` — partial coordination (992 LOC, complex but partial)

### Ghost Infrastructure (17 of 20)
`requirement_extractor.py`, `requirement_graph.py`, `spec_digestor.py`, `spec_indexer.py`,
`spec_parser.py`, `spec_source_registry.py`, `spec_vault_ingest.py`, `context_pack_builder.py`,
`extractor_to_workbench_adapter.py`, `fact_coverage_report.py`, `run_extraction_pipeline.py`,
`run_fact_verification.py`, `qname_src_compliance_reporter.py`, `spec_census.py`,
`spec_governance_runtime.py`, `migrate_sources_jsonl.py`, and others.

### SAL → Downstream Connection: MISSING
Facts in `verified-facts-review.yaml` are NOT read by:
- QName derivation pipeline → qname-to-code-map.yaml built manually
- Capability map generator → uses hardcoded goal lists
- Source generator → no connection

### Rework Items in Signal (SAL)
The continuation signal has these SAL-related rework items:
- TC-SAL-IDEMPOTENCY — SAL extraction is not idempotent
- TC-SAL-HEAL-001 — SAL pipeline wiring incomplete
- TC-SAL-HEAL-005 — specific SAL healing needed

## Root Causes
1. **RC-SAL-MANUAL-FACT-SEEDING**: Facts were manually extracted in run030; no automated re-extraction
2. **RC-SAL-GHOST-TOOLS**: 17 tools have no invocation path; they're dead code in tools/specification-authority-layer/
3. **RC-SAL-NO-DOWNSTREAM**: SAL output format (verified-facts-review.yaml) has no machine-readable consumer in capability pipeline

## Required Actions
1. **TC-SAL-WIRING-001**: Wire sal_master_runner.py to run all 20 tools in sequence for one format
2. **TC-SAL-NONODF-001**: Implement fact extraction for ABW, DIF, Gnumeric (these have spec-index.yaml but 0 facts)
3. **TC-SAL-DOWNSTREAM-001**: Create machine-readable consumer that reads verified-facts-review.yaml → updates capability claims
4. **TC-SAL-IDEMPOTENCY**: Fix sal_master_runner.py to be idempotent (multiple runs don't duplicate facts)
5. **TC-SAL-FRESHNESS-001**: Add spec version tracking and invalidation when spec changes
