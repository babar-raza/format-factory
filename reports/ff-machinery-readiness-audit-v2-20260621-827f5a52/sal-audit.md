# SAL / Spec Authority Layer Audit — Format Factory Machinery Audit v2
# Sprint ID: ff-machinery-readiness-audit-v2-20260621-827f5a52

## SAL Pipeline Status

### Tool Inventory
19 tools in tools/specification-authority-layer/:
sal_master_runner.py, spec_parser.py, spec_indexer.py, spec_normalizer.py,
spec_digestor.py, spec_census.py, spec_source_registry.py, spec_vault_ingest.py,
requirement_extractor.py, requirement_graph.py, run_extraction_pipeline.py,
run_fact_verification.py, spec_governance_runtime.py, qname_src_compliance_reporter.py,
extractor_to_workbench_adapter.py, fact_coverage_report.py, migrate_sources_jsonl.py,
context_pack_builder.py, + 1 more

### SAL Fact Counts Per Format (live inspection)

| Format | Facts | Generator | Source | Real? |
|--------|-------|-----------|--------|-------|
| FODS | 4987 | sal_master_runner.py v1.0 | workbench_verified | PARTIAL (see below) |
| FODT | 4933 | sal_master_runner.py v1.0 | workbench_verified | PARTIAL |
| ZST | 94 | sal_master_runner.py v1.0 | workbench_verified | PARTIAL |
| ABW | 0 | sal_master_runner.py v1.0 | — | NO |
| CSV | 0 | sal_master_runner.py v1.0 | — | NO |

### FODS Workbench Facts Quality Assessment

Evidence from `.local/spec-cache/fods/1.3/workbench/verified-facts-review.yaml`:

```
fact_count: 4991 (actual list: 4991)
generated_by: TCA-010 downgrade pass (SPEC-AUTHORITY-LAYER-STOP-THE-BLEEDING-001)
authority_note: Contains 78 verified and pending facts covering FODS/ODF 1.3 spreadsheet elements
seeding_note: All facts downgraded from auto-seed (build_spec_workbench.py run030).
  Each fact must be verified by reading .local/spec-cache/fods/1.3/normalized/text.txt
  and setting validated_by: independent_agent_verification
verification_status distribution: {verified: 4348, verified_with_note: 639, pending: 3, unknown: 1}
```

CRITICAL FINDING: The `verification_status: verified` for 4348 facts was SET by the TCA-010
downgrade pass script, NOT by an agent or human independently reading the spec.

The original `authority_note` says "78 verified and pending facts" — these are the only
facts that were manually/independently verified. The remaining 4909 are auto-seeded.

The `build_spec_workbench.py run030` seeded from some source (likely from reading the ODF
spec PDF or normalized text), then TCA-010 set all seeds to `verified` status to prevent
the downgrade from setting them to `unverified`.

### Prior Audit Finding vs. Current

Prior audit: "SAL Pipeline BROKEN — template facts, not spec-derived. 78 FODS facts stranded."

Current state:
- `sal_master_runner.py` has been fixed to read from workbench (TC-SAL-IMPL-001 wired)
- The workbench now has 4991 FODS facts (was 78 in the prior audit)
- BUT: the new 4991 facts are auto-seeded, not independently verified
- The TCA-010 downgrade pass labeled all auto-seeds as "verified" status
- The seeding_note explicitly says "must be verified by reading spec text"

CONCLUSION: SAL now has VOLUME (4987 loadable facts) but NOT QUALITY (auto-seeded, not
independently verified against actual ODF 1.3 specification text). This is a significant
improvement in pipeline mechanics but the fact quality risk remains.

### What SAL Can Do Now (vs. Prior Audit)

| Capability | Prior Audit | Current |
|-----------|-------------|---------|
| Load FODS facts | BROKEN (stranded) | WORKS (4987 facts) |
| Fact IDs follow FACT-FORMAT-NNN | BROKEN (ODF-FACT-* / template IDs) | WORKS (FACT-FODS-001+) |
| Facts from spec text vs. templates | TEMPLATES ONLY | AUTO-SEED (partial improvement) |
| Independent verification | ZERO | 78 original + auto-seeded |
| SAL idempotency | BROKEN | FIXED (commit 827f5a52) |
| Multi-format support | FODS only (78 facts) | FODS+FODT+ZST |
| ZST fact IDs | MISSING | 94 facts |
| Template fact IDs (ODF-FACT-*) leak | YES | SUPPRESSED via from_cache_only |

### Downstream SAL Consumers

- `capability_compiler.py` reads `sal-facts-latest.json` (SAL output file)
- `validate_spec_fact_refs.py` validates that declared spec_fact_refs exist in SAL
- Context packs: SAL output feeds into .supervisor/ context
- Gap ledger: 625 of 958 gaps have spec_facts field

HOWEVER: The gap ledger spec_facts field was pre-populated when gaps were created (2026-06-08),
NOT dynamically derived from running the SAL pipeline. The SAL-to-capability connection
is still primarily static.

### SAL Readiness Summary

| Aspect | Status |
|--------|--------|
| Pipeline mechanics | PARTIAL — wired but auto-seeded |
| FODS fact volume | GREEN — 4987 loadable |
| FODS fact quality | YELLOW — auto-seeded; real spec reading not confirmed |
| FODT fact support | YELLOW — same as FODS |
| Other formats | RED — 0 facts (abw, csv, dif, etc.) |
| Fact ID format | GREEN — FACT-FODS-NNN consistent |
| Idempotency | GREEN — fixed 827f5a52 |
| SAL-to-capability connection | RED — still manual/static |
| Overclaim rejection | GRAY — no validator enforces SAL-derivation |

## SAL Test Results (Live Run — 2026-06-21)

8 failed, 183 passed in 616.54s

FAILED: test_fodt_qname_spec_chain.py::test_fodt_sal_facts_present
FAILED: test_gap_int_002_product_source_fact_refs.py::test_total_fact_refs_across_product_source
FAILED: test_plan_readiness_verdict.py::test_plan_version_is_v30
FAILED: test_sal_from_cache_only.py::TestConsumerReachability::test_sal_facts_has_results
FAILED: test_sal_from_cache_only.py::TestConsumerReachability::test_sal_facts_total_above_5000
FAILED: test_sal_from_cache_only.py::TestConsumerReachability::test_fods_facts_above_4900
FAILED: test_sal_from_cache_only.py::TestConsumerReachability::test_capability_compiler_reads_facts
FAILED: test_sal_from_cache_only.py::TestConsumerReachability::test_capability_map_generator_reads_facts

Interpretation:
- TestConsumerReachability (5 failures): capability_compiler.py and capability_map_generator.py
  CANNOT read SAL facts — confirms TC-CAPABILITY-COMPILER-001 (wrong SAL path bug)
- test_fodt_sal_facts_present: FODT facts not reaching downstream consumer
- test_total_fact_refs_across_product_source: product source lacks spec fact refs
- test_plan_version_is_v30: plan version mismatch (minor)

