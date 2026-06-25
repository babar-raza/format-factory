# Pipeline Integration Matrix — Spec Authority
## Run ID: spec-authority-machinery-explosion-20260625-c6b2470

---

## Rating Legend

- **READS_SPEC_DATA**: Stage reads spec facts, requirement packs, or verified facts
- **REQUIRES_SPEC_AUTH**: Stage enforces spec authority as a gate condition
- **BYPASS_POSSIBLE**: Stage can complete without spec authority being present
- **SEVERITY**: CRITICAL / HIGH / MODERATE / LOW

---

## Pipeline Stage Matrix

| Stage | Reads Spec Data | Requires Spec Auth | Bypass Possible | Severity | Root Cause | Repair |
|-------|----------------|-------------------|----------------|----------|------------|--------|
| **S01 T3 Authorization** | N/A | YES (6 conditions) | NO | CRITICAL | Only ODF completed T3 | Register `acquire-spec-t3` skill; require T3 completion before P2 classification |
| **S02 Spec Acquisition (acquire_spec.py)** | YES (downloads) | YES (T3 required) | NO | HIGH | Not a governed skill; manual execution | Register as governed skill with transcript |
| **S03 Spec Normalization (spec_normalizer.py)** | YES (normalizes) | YES (requires S02) | BLOCKED_UPSTREAM | HIGH | Not run for CSV/NDJSON/TOML/ZST/PBM/PGM/PPM | Register `normalize-spec` skill; run for all formats with accessible specs |
| **S04 Fact Extraction (run_extraction_pipeline.py)** | YES (extracts) | YES (requires S03) | BLOCKED_UPSTREAM | HIGH | Not a governed skill | Register `extract-spec-facts` skill |
| **S05 Fact Verification (spec_verifier.py)** | YES (verifies) | YES (requires S04) | BLOCKED_UPSTREAM | HIGH | Not run for non-ODF | Register `verify-spec-facts` skill |
| **S06 Requirement Pack Generation** | YES (generates) | YES (requires S05) | BLOCKED_UPSTREAM | HIGH | Requirement packs exist for FODS only | Register `generate-requirement-pack` skill |
| **S07 SAL Facts Registry (sal-facts-{format}.json)** | OUTPUT | YES (upstream) | BLOCKED_UPSTREAM | HIGH | Only meaningful entries for ODF/ZST | Normalize + extract for CSV/TOML/QOI/XCF |
| **S08 Authority Gate Validation (authority_gate_validation.py)** | YES | YES | **YES — NOT CALLED** | **CRITICAL** | product_task_selector doesn't call it | Wire authority_gate_validation into product_task_selector |
| **S09 Task Selection (product_task_selector.py)** | NO | **NO — poc-targets only** | **YES — always** | **CRITICAL** | _get_format_authority_status() checks poc-targets membership only | Replace with authority_gate_validation P-level lookup |
| **S10 Prompt Generation (generate_next_worker_prompt.py)** | **NO** | **NO** | **YES — always** | HIGH | sal-facts NOT in READ_BEFORE_EXECUTION | Inject top-N verified facts + authority level into prompts |
| **S11 Worker Execution** | **NO** | **NO** | **YES — always** | HIGH | Workers receive no spec-derived requirements | Inject via prompt; workers must cite FACT-* in code |
| **S12 Evidence Declaration** | NO | **NO — spec_fact_refs optional** | **YES — always** | **CRITICAL** | supervisor-worker-contract.md missing spec_fact_refs requirement | Add spec_fact_refs as required-or-explain field |
| **S13 Declaration Validation (sprint_executor_validate.py)** | NO | **NO — validates schema only** | **YES — always** | HIGH | Schema doesn't include spec_fact_refs as required | Update schema; validate spec_fact_refs presence |
| **S14 Governance Validators — V13** | PARTIAL | PARTIAL | **YES — absent=no-op** | **CRITICAL** | V13 only fires if spec_fact_refs PROVIDED AND INVALID | Fix V13 to also fire when spec_fact_refs ABSENT (without exception_classification) |
| **S15 TC-GUARD-001 (autonomous_cycle.py Step 2d3)** | NO | PARTIAL | **YES — gap_ledger_ref bypass** | **CRITICAL** | OR logic allows gap_ledger_ref alone | Change to AND: require gap_ledger_ref AND (spec_fact_refs OR exception_classification) |
| **S16 Anti-Skip Detector 19 (ODF spec linkage)** | PARTIAL | PARTIAL | YES — advisory only | MODERATE | Downgrades verdict but does NOT block | Consider making Detector 19 blocking for ODF PRODUCT_SOURCE items |
| **S17 Proof Graph Update (build_proof_graph_iter003.py)** | NO | NO | YES | HIGH | Not called from autonomous_cycle.py | Wire proof graph update at sprint close for ODF formats |
| **S18 Authority Integration (authority_integration_fabric.py)** | YES (design) | YES (design) | **YES — NEVER CALLED** | **CRITICAL** | Not imported by any production path | Add Step 0b-authority-state in autonomous_cycle.py |
| **S19 Product Ledger Update** | NO | NO | YES | HIGH | No authority_level column in poc-targets | Add authority_level to poc-targets.yaml; record per sprint |
| **S20 Supervisor Review** | NO | PARTIAL (V13, TC-GUARD) | YES | MODERATE | Supervisor grades evidence quality but spec authority is advisory | Require authority_level in supervisor verdict packet |
| **S21 Autonomous Continuation Check** | NO | NO | YES | MODERATE | check_continuation doesn't verify spec authority state | Add spec authority state to continuation signal |
| **S22 Release Gate (RELEASE_GATE items)** | NO | PARTIAL (V48 gates stubs) | YES | MODERATE | No minimum P-level requirement at release gate | Add P4+ requirement for commercial release gate |

---

## Critical Bypass Summary

### Bypass 1: TC-GUARD-001 OR Logic (CRITICAL)
- **Location**: `tools/supervisor/autonomous_cycle.py` Step 2d3
- **Bypass**: `gap_ledger_ref` alone satisfies the guard — spec_fact_refs not required
- **Impact**: 100% of product sprints can pass TC-GUARD-001 with zero spec authority
- **Repair**: Change OR to AND — require gap_ledger_ref AND (spec_fact_refs OR exception_classification)

### Bypass 2: Evidence Schema Missing spec_fact_refs (CRITICAL)
- **Location**: `docs/automation/supervisor-worker-contract.md`
- **Bypass**: spec_fact_refs not in required fields — any declaration without it is schema-valid
- **Impact**: No spec authority citation can be enforced at the schema level
- **Repair**: Add spec_fact_refs as required-or-explain field; update sprint_executor_validate.py

### Bypass 3: product_task_selector poc-targets-only Check (CRITICAL)
- **Location**: `tools/supervisor/product_task_selector.py`
- **Bypass**: _get_format_authority_status() checks poc-targets.yaml membership, not P-level
- **Impact**: P1 formats (Gnumeric, ABW) receive ALLOWED status for product tasks
- **Repair**: Call authority_gate_validation.py and return actual P-level; block P<4 without exception

### Bypass 4: V13 Absent-vs-Invalid Distinction (CRITICAL)
- **Location**: `tools/supervisor/governance_validators.py V13`
- **Bypass**: V13 only fires when spec_fact_refs is PROVIDED AND INVALID — absent = no enforcement
- **Impact**: Workers can submit evidence with no spec_fact_refs and V13 won't fire
- **Repair**: V13 should also fire when spec_fact_refs is absent and exception_classification is absent

### Bypass 5: authority_integration_fabric.py Unwired (CRITICAL)
- **Location**: `tools/supervisor/authority_integration_fabric.py`
- **Bypass**: File exists but NOT imported by autonomous_cycle.py or supervisor_loop.py
- **Impact**: requirements_authority/ layer (graph_store, coverage_evaluator, overclaim_detector) is dormant
- **Repair**: Add Step 0b-authority-state in autonomous_cycle.py calling authority_integration_fabric.py
