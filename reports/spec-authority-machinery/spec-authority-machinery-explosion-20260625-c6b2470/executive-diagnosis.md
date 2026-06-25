# Executive Diagnosis — Spec Authority Machinery Explosion
## Run ID: spec-authority-machinery-explosion-20260625-c6b2470
## Date: 2026-06-25 | Branch: main | HEAD: c6b24706

---

## One-Page Answer: Where Do We Stand?

**The Specification Authority Layer physically exists and is partially real** — but three structural bypasses allow product work to proceed without spec authority for the majority of formats. The layer is production-enforced for a small number of ODF formats (FODS, FODT) and structurally correct for formats with no public spec (Gnumeric, ABW, SYLK, DIF). For the remaining formats, the enforcement is bypassable and the pipeline does not require spec authority before scheduling, executing, or accepting product work.

---

## Rating Summary

| Dimension | Rating | Evidence |
|-----------|--------|----------|
| Layer Existence | STRONG | tools/spec-cache/ (15+ scripts), .local/spec-cache/ (per-format workbenches), validate_spec_fact_refs.py, authority_gate_validation.py |
| Layer Correctness | MODERATE | FODS=4988 verified facts with full chain; Gnumeric=3 structural facts correctly classified P1; most others 2-94 structural facts |
| Pipeline Integration | MOSTLY_ADVISORY | V13 blocking but bypassable; TC-GUARD-001 gap_ledger_ref bypass; authority_integration_fabric.py UNWIRED |
| Enforcement | WEAK | 3 critical bypass paths exist; evidence schema missing mandatory spec_fact_refs; product_task_selector checks poc-targets only |
| Repeatability | WEAK | Skills exist but spec acquisition/normalization/fact-extraction not registered as governed skills |
| AI/Embedding Support | MOSTLY_ADVISORY | Policy docs sound; ai_draft tools exist; no embeddings deployed; not in production path |
| Product Proof (FODS/FODT) | STRONG | P6 for FACT-FODS-001 with full proof graph; genuine behavioral spec-backed tests |
| Product Proof (ODF family) | MODERATE | P5 (cited in code and tests), full facts exist, no proof graphs yet |
| Product Proof (non-ODF) | WEAK-P2 | Gnumeric/ABW=P1 (designed); ZST=P6; PBM/PGM/PPM=P5; CSV/NDJSON/XCF/TOML/QOI=P2-legacy |
| Go/No-Go for Factory | NO-GO | Three critical bypasses must close before the pipeline can drive governed acquisition at scale |

---

## Top 10 Root Causes

1. **RCA-SUPERVISOR-GATES-001 [CRITICAL]**: TC-GUARD-001 in autonomous_cycle.py accepts `gap_ledger_ref` alone as sufficient — no spec_fact_refs required. Any product sprint can pass with zero spec authority if it has a gap ledger reference.

2. **RCA-EVIDENCE-SCHEMA-001 [CRITICAL]**: Evidence declaration required fields (supervisor-worker-contract.md) do NOT include `spec_fact_refs`. A sprint achieves ACCEPTED verdict with only gap_ledger_ref. The supervisor accepts product work with zero spec authority citations.

3. **RCA-PRODUCT-SELECTION-001 [HIGH]**: `product_task_selector.py` checks poc-targets.yaml membership only (binary ALLOWED/BLOCKED), NOT actual P-level. The `_BLOCKED_AUTHORITY_STATES` frozenset exists but `_get_format_authority_status()` never populates it from actual P-level data. Hard-coded task catalog bypasses authority check.

4. **RCA-PROMPT-GENERATION-001 [HIGH]**: `generate_next_worker_prompt.py` does NOT inject spec authority data (fact IDs, requirement packs, spec sections) into worker prompts. Workers receive no spec-derived requirements to implement against.

5. **RCA-INTEGRATION-001 [HIGH]**: `authority_integration_fabric.py` (connecting to tools/requirements_authority/ with graph_store, coverage_evaluator, overclaim_detector) is NOT called from autonomous_cycle.py or any production path. The integration fabric is an unused production component.

6. **RCA-SKILLS-REPEATABILITY-001 [HIGH]**: Spec acquisition (acquire_spec.py), normalization (spec_normalizer.py), fact extraction (run_extraction_pipeline.py), and requirement pack generation are NOT registered as governed skills with transcripts. These are one-time manual operations with no repeatable pipeline mechanism.

7. **RCA-TEST-GENERATION-001 [HIGH]**: For Gnumeric/ABW/CSV/TSV/NDJSON/XCF/TOML/QOI, test files check only that `spec_fact_ref` CLASS ATTRIBUTES match expected strings — NOT behavioral spec-derived assertions. Happy-path tests predominate. No negative tests proving spec-forbidden behavior fails.

8. **RCA-PROOF-GRAPH-001 [HIGH]**: Three iterations of proof graph builders (iter001-iter003) indicate ongoing evolution. Only FODS and ZST have formal proof graph YAML files. ODS/ODT/FODG/FODP are P5 (facts cited in code+tests) but no proof graph. Product ledger does NOT record authority level.

9. **RCA-SPEC-CACHE-001 [MODERATE-BY-DESIGN]**: Non-ODF formats have metadata-only spec cache entries (2-5 structural facts). T3 authorization has only been completed for ODF/FODS. This is by design — but creates a two-tier system where 15+ formats have no path to P4 until T3 is completed.

10. **RCA-NORMALIZATION-001 [MODERATE]**: Normalization tools (spec_normalizer.py) exist and were used for ODF/FODS, but have NOT been run for CSV, NDJSON, TOML, XCF, QOI, or other formats with accessible public specs. These formats sit at P2 (spec cached but no facts) when they could advance to P3-P4.

---

## Top 10 Repairs (Priority Order)

1. **TC-GUARD-001 bypass closure**: Change OR logic to AND — require BOTH gap_ledger_ref AND (spec_fact_refs OR exception_classification). File: `tools/supervisor/autonomous_cycle.py` Step 2d3. One sprint.

2. **Evidence schema mandatory field**: Add `spec_fact_refs` as required-or-explain field in `docs/automation/supervisor-worker-contract.md` and `sprint_executor_validate.py` repair logic. One sprint.

3. **product_task_selector P-level check**: Replace poc-targets.yaml membership check with `authority_gate_validation.py` P-level lookup. Block task emission for P<4 formats without exception. File: `tools/supervisor/product_task_selector.py`. One sprint.

4. **Wire authority_integration_fabric.py**: Add Step 0b-authority-state in autonomous_cycle.py to call authority_integration_fabric.py and generate authority-integration-contract.json. File: `tools/supervisor/autonomous_cycle.py`. One sprint.

5. **Prompt injection of spec authority**: Modify `generate_next_worker_prompt.py` to inject authority level, top-N verified facts, and requirement pack references for the target format. One sprint.

6. **Proof graph for ODF family**: Extend proof graph from FODS FACT-FODS-001 to FODS FACT-FODS-001→010 and create proof graphs for ODS/ODT/FODG/FODP. One sprint.

7. **Register 5 minimum skills**: `acquire-spec-t3`, `normalize-spec`, `extract-spec-facts`, `authority-gate-validation`, `pilot-rerun-authority`. Register in .supervisor/skill-registry.yaml. One sprint.

8. **ZST/CSV/TOML normalization**: Run spec normalization pipeline for ZST (RFC8878), CSV (RFC4180), TOML (spec-toml.io). Advance from P2 to P3+. Two sprints.

9. **Test quality upgrade for ODF formats**: Add behavioral spec-backed tests for FODT, ODS, ODT that assert specific element behavior per spec fact IDs. Two sprints.

10. **Product ledger authority level**: Add authority_level column to poc-targets.yaml and product readiness dashboard. One sprint.

---

## Go/No-Go Verdict

**NO-GO for using current layer to drive future autonomous acquisition at scale.**

Rationale: The three critical bypasses (TC-GUARD-001, evidence schema, product_task_selector) mean that 100% of product sprints can proceed without any spec authority citation. The autonomous pipeline does not enforce spec authority as a production gate. Repairs 1-3 above must close before the pipeline can be trusted to drive governed acquisition.

**Exception**: The FODS and ZST vertical slices ARE production-quality with genuine P6 proof graphs, behavioral spec-backed tests, and full chain from spec PDF to code to evidence. These can serve as pilot templates for other formats after the bypass closures.

---

## Final Verdict

**`SPEC_AUTHORITY_LAYER_EXISTS_BUT_PIPELINE_BYPASSES_IT`**
