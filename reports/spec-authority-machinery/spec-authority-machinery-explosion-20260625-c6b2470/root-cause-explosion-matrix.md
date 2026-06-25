# Root Cause Explosion Matrix
## Run ID: spec-authority-machinery-explosion-20260625-c6b2470

---

## RCA-SUPERVISOR-GATES-001 [CRITICAL]
**TC-GUARD-001 OR Logic Bypass**

- **File**: `tools/supervisor/autonomous_cycle.py` Step 2d3, line 869
- **Mechanism**: Checks ONE OF {gap_ledger_ref, capability_ref, spec_fact_refs}. `gap_ledger_ref` alone satisfies the guard.
- **Evidence**: zst-frame-count-coverage-20260622 sprint: spec_fact_refs=None, gap_ledger_ref=GAP-ZST-FOSS-*, verdict=ACCEPTED
- **Impact**: 100% of product sprints can pass TC-GUARD-001 with zero spec authority citations
- **Scope**: Every format, every sprint
- **Repair**: Change OR logic to AND — require gap_ledger_ref AND (spec_fact_refs OR exception_classification)

---

## RCA-EVIDENCE-SCHEMA-001 [CRITICAL]
**Evidence Declaration Missing spec_fact_refs as Required Field**

- **File**: `docs/automation/supervisor-worker-contract.md`
- **Mechanism**: Required declaration fields do NOT include `spec_fact_refs`. Schema-valid without it.
- **Evidence**: supervisor-worker-contract.md field list: gap_ledger_ref, capability_ref, tests_run, worker_self_verdict — no spec_fact_refs
- **Impact**: sprint_executor_validate.py cannot enforce spec_fact_refs at validation time
- **Scope**: Every sprint, every format
- **Repair**: Add spec_fact_refs as required-or-explain field in contract; update validation schema

---

## RCA-PRODUCT-SELECTION-001 [CRITICAL]
**product_task_selector.py Checks poc-targets Only — Not P-Level**

- **File**: `tools/supervisor/product_task_selector.py`
- **Mechanism**: `_get_format_authority_status()` returns "ALLOWED" for any format in poc-targets.yaml regardless of P-level
- **Evidence**: Gnumeric (P1), ABW (P1) both in poc-targets → both return "ALLOWED"
- **Evidence**: `_BLOCKED_AUTHORITY_STATES` frozenset defined but never populated from P-level data
- **Evidence**: `_CANDIDATE_CATALOG` hard-codes tasks for Gnumeric/ABW bypassing all authority gates
- **Impact**: P1 formats receive product tasks without P4 requirement being checked
- **Scope**: All P1-P3 formats registered in poc-targets
- **Repair**: Call authority_gate_validation.py from `_get_format_authority_status()`; return actual P-level; block P<4 without exception

---

## RCA-V13-ENFORCEMENT-001 [CRITICAL]
**V13 Only Fires When spec_fact_refs Is Present and Invalid — Not When Absent**

- **File**: `tools/supervisor/governance_validators.py`, line 912
- **Mechanism**: V13 fires only if `spec_fact_refs` is provided AND fails validation. Absent field = no enforcement.
- **Evidence**: V13 conditional: `if declaration.get("spec_fact_refs")` — evaluates to False when absent
- **Impact**: Workers can submit evidence with no spec_fact_refs and V13 won't fire, even for PRODUCT_SOURCE items
- **Scope**: All formats where workers omit spec_fact_refs (currently all non-FODS formats)
- **Repair**: V13 should also fire when spec_fact_refs is absent AND no exception_classification is present

---

## RCA-INTEGRATION-001 [HIGH]
**authority_integration_fabric.py Is Not Called From Any Production Path**

- **File**: `tools/supervisor/authority_integration_fabric.py`
- **Mechanism**: File exists and imports from tools/requirements_authority/ (graph_store, coverage_evaluator, overclaim_detector, staleness_invalidator) but is NOT imported by autonomous_cycle.py or supervisor_loop.py
- **Evidence**: Grep for `authority_integration_fabric` in tools/supervisor/ — zero imports outside the file itself
- **Impact**: Entire requirements_authority/ layer is dormant. Proof graph never updated. Overclaims never detected.
- **Scope**: All formats, all sprints
- **Repair**: Add Step 0b-authority-state in autonomous_cycle.py calling authority_integration_fabric.py

---

## RCA-PROMPT-GENERATION-001 [HIGH]
**Worker Prompts Contain No Spec Authority Data**

- **File**: `tools/supervisor/generate_next_worker_prompt.py`
- **Mechanism**: `READ_BEFORE_EXECUTION` list includes poc-targets, gap-ledger, skill-registry, capability-map. Does NOT include: sal-facts-{format}.json, workbench/verified-facts.yaml, workbench/requirement-packs/
- **Evidence**: READ_BEFORE_EXECUTION list read during investigation — spec artifacts absent
- **Impact**: Workers executing product tasks have no spec-derived requirements to implement against. Code lacks citations, tests lack fact references.
- **Scope**: All formats
- **Repair**: Inject authority_level, top-N verified facts, requirement_pack_path for target format into prompts

---

## RCA-SKILLS-REPEATABILITY-001 [HIGH]
**Spec Acquisition Pipeline Not Registered as Governed Skills**

- **File**: `.supervisor/skill-registry.yaml`
- **Mechanism**: acquire_spec.py, spec_normalizer.py, run_extraction_pipeline.py, spec_verifier.py, requirement_extractor.py are NOT registered as governed skills with transcripts
- **Evidence**: skill-registry.yaml inspection — no acquire-spec, normalize-spec, extract-spec-facts entries
- **Impact**: Spec acquisition is a one-time manual operation with no governed repeatability. Cannot be triggered by queue actions or sprint automation.
- **Scope**: All formats needing spec acquisition (CSV, NDJSON, TOML, ZST full coverage, XCF, QOI)
- **Repair**: Register 5 minimum skills: acquire-spec-t3, normalize-spec, extract-spec-facts, authority-gate-validation, pilot-rerun-authority

---

## RCA-TEST-QUALITY-001 [HIGH]
**Tests for Non-ODF Formats Are Identifier-Only, Not Behavioral Spec-Derived**

- **Files**: `tests/python/gnumeric/`, `tests/python/abw/`, `tests/python/csv_format/`, etc.
- **Mechanism**: Tests validate `Class.spec_fact_ref == "FACT-FORMAT-001"` (identifier check) not behavioral assertions derived from spec requirements
- **Evidence**: `tests/python/gnumeric/test_spec_compat_layer.py` only checks `spec_fact_ref` string value
- **Evidence**: No test asserts "element X MUST contain attribute Y per §Z.Z" for Gnumeric/ABW
- **Impact**: Tests provide no evidence that implementation conforms to spec requirements. Passing tests do not prove spec compliance.
- **Scope**: 15+ formats at P1-P2
- **Repair**: Add behavioral spec-backed tests citing FACT-* IDs with assertions about element behavior per spec section

---

## RCA-PROOF-GRAPH-001 [HIGH]
**Proof Graph Exists for 1/4988 FODS Facts and 1/94 ZST Facts Only**

- **File**: `.local/spec-cache/fods/1.3/workbench/reports/authority-conveyor-20260608/fods-p6-proof-graph.yaml`
- **Mechanism**: Three iterations of proof graph builders (iter001-003) indicate ongoing evolution. Only FACT-FODS-001 and FACT-ZST-001 have formal YAML proof graph files.
- **Evidence**: fods-p6-proof-graph.yaml explicitly states: "P6 is claimed ONLY for FACT-FODS-001"
- **Evidence**: authority_gate_validation.py P6 classification based on any FACT-* in rglob("*.py") — includes build/ artifacts
- **Impact**: P-level classification is optimistic. Product ledger does NOT record actual fact coverage.
- **Scope**: All formats above P4
- **Repair**: Extend proof graph to FODS FACT-002..010; wire proof graph update to sprint closeout

---

## RCA-CODE-CITATIONS-001 [HIGH]
**rglob() in _check_code_citations Includes build/ Directory**

- **File**: `tools/supervisor/authority_gate_validation.py`, `_check_code_citations()` function
- **Mechanism**: Uses `src_dir.rglob("*.py")` which recurses into build/ subdirectories containing auto-generated code
- **Evidence**: Build artifacts may contain FACT-* strings copied from template files
- **Impact**: P6 classification may be based on build/ artifacts rather than production code
- **Scope**: Any format with build/ subdirectory containing Python files
- **Repair**: Exclude build/ from rglob: `for f in src_dir.rglob("*.py") if "build" not in f.parts`

---

## RCA-SPEC-CACHE-001 [MODERATE — by design]
**T3 Authorization Only Completed for ODF Formats**

- **Files**: T3 authorization records in .local/spec-cache/{format}/
- **Mechanism**: T3 authorization requires 6 conditions (legal category, redistribution, canonical URL, version, operator sign-off, qname-registry registration). Only completed for ODF/FODS.
- **Evidence**: CSV (RFC4180), NDJSON (ndjson.org), TOML (spec-toml.io), QOI (qoi.phoboslab.org) all have accessible specs but no T3 completion
- **Impact**: 15+ formats cannot advance beyond P2 until T3 is completed for each. Creates two-tier system.
- **Scope**: All non-ODF formats with accessible specs
- **Repair**: Run T3 authorization workflow for RFC4180 (CSV), spec-toml.io (TOML), ndjson.org (NDJSON), qoi.phoboslab.org (QOI)

---

## RCA-NORMALIZATION-001 [MODERATE]
**Normalization Not Run for Formats With Accessible Specs**

- **Files**: `tools/spec-cache/spec_normalizer.py`
- **Mechanism**: spec_normalizer.py was run for ODF/FODS, producing normalized/text.txt + sections.jsonl + chunks.jsonl. Not run for CSV, NDJSON, TOML, ZST (partially), XCF, QOI despite accessible specs.
- **Evidence**: sal-facts counts: CSV=2, NDJSON=2, TOML=2 — only structural metadata facts, no extracted spec text facts
- **Impact**: Formats with accessible specs sit at P2 when they could advance to P3-P4 with normalization
- **Scope**: CSV, NDJSON, TOML, ZST (remaining 92 facts), XCF, QOI
- **Repair**: Run normalization pipeline for RFC4180, spec-toml.io, ndjson.org after T3 authorization

---

## RCA-PRODUCT-LEDGER-001 [MODERATE]
**poc-targets.yaml Does Not Record Authority Level or Proof Level Per Format**

- **File**: `product-capability-matrix/poc-targets.yaml`
- **Mechanism**: poc-targets.yaml records gates_passed (1-11), commercial_product_ready, and readiness grades but NO authority_level or proof_level column
- **Evidence**: FODS entry: gates_passed: 1-11, commercial_product_ready: false, no authority_level
- **Impact**: Product readiness dashboard cannot display spec authority standing. No automated overclaim detection from ledger.
- **Scope**: All 20 formats
- **Repair**: Add authority_level column to poc-targets.yaml; populate from authority_gate_validation.py output per sprint

---

## RCA-AI-POLICY-001 [LOW]
**AI/LLM Policy Is Sound But Not Runtime-Enforced**

- **Files**: `docs/governance/ai-authority-boundary.md`, `docs/llm-and-embedding-strategy.md`
- **Mechanism**: Policy forbids AI authority. ai_draft labels exist. ai_evidence_critic.py and ai_implementation_designer.py are labeled ai_draft. No active embeddings in production. No runtime enforcement of ai_draft labels.
- **Evidence**: No embeddings deployed. No RAG pipeline active. AI tools labeled but not guarded.
- **Impact**: Low current risk — AI tools not in production path. Future risk if ai_draft tools get promoted without runtime enforcement.
- **Scope**: Future state risk
- **Repair**: Add V49 governance validator to detect ai_draft items being cited as authoritative evidence

---

## RCA-SUPERVISOR-GATES-002 [MODERATE — by design]
**exception_classification Allows 15 Formats to Bypass V13 Legitimately**

- **File**: `tools/supervisor/governance_validators.py V13`
- **Mechanism**: `no_public_spec_available` (ABW, SYLK, DIF, TSV), `schema_authority_available` (Gnumeric), `legacy_backfill` (CSV, NDJSON, TOML, XCF, QOI) are valid exceptions that allow PRODUCT_SOURCE items to pass V13 without spec_fact_refs
- **Evidence**: These exceptions are architecturally correct per design for formats without accessible formal specs
- **Impact**: By design — but reveals systemic gap: 15/20 formats permanently in exception territory with no path to P4 until T3 authorization is completed for each format's spec
- **Scope**: 15 formats (designed exception)
- **Repair**: `legacy_backfill` exception is NOT permanent — it should have a sunset date. Track T3 authorization for CSV/NDJSON/TOML/QOI as mandatory work items. Formats with accessible specs should advance beyond P2 within 2 sprints.
