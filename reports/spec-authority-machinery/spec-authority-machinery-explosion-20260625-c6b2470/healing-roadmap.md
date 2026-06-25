# Healing Roadmap — Spec Authority Layer
## Run ID: spec-authority-machinery-explosion-20260625-c6b2470

---

## Phase A — Stop the Bleeding (Immediate, 2 sprints)

Goal: Close the 3 critical bypass paths that allow product sprints to proceed with zero spec authority.

### A-001: TC-GUARD-001 AND Logic
**File**: `tools/supervisor/autonomous_cycle.py` Step 2d3
**Change**: Replace OR with AND — require gap_ledger_ref AND (spec_fact_refs OR exception_classification)
**Risk**: MODERATE — migration required for existing declarations without spec_fact_refs

### A-002: V13 — Fire When spec_fact_refs Absent
**File**: `tools/supervisor/governance_validators.py` V13
**Change**: Add ABSENT check — fire when spec_fact_refs absent AND no exception_classification AND PRODUCT_SOURCE AND Tier 1 format
**Risk**: MODERATE — controlled migration for FODS/FODT/ODS/ODT sprints

### A-003: Evidence Schema — spec_fact_refs Required-or-Explain
**File**: `docs/automation/supervisor-worker-contract.md`
**Change**: Add spec_fact_refs as required-or-explain field; Tier 1 → provide FACT-*; Tier 2 → exception_classification
**Risk**: LOW

### A-004: product_task_selector — Wire P-Level Check
**File**: `tools/supervisor/product_task_selector.py`
**Change**: Call authority_gate_validation.py for actual P-level; block P<4 without exception; remove hard-coded _CANDIDATE_CATALOG
**Risk**: HIGH — blocks CSV/NDJSON/TOML/XCF/QOI (P2, legacy_backfill); needs explicit exception to proceed

---

## Phase B — Make One Vertical Slice Real (1 sprint)

Goal: Complete the FODS vertical slice as a production template.

### B-001: Extend proof graph to FACT-FODS-002..010
**File**: `.local/spec-cache/fods/1.3/workbench/reports/authority-conveyor-*/`
**Change**: Run `build_proof_graph_iter003.py` for 10 facts; verify P6 is evidence-based not coverage-assumed

### B-002: Fix _check_code_citations rglob
**File**: `tools/supervisor/authority_gate_validation.py`
**Change**: Exclude build/ and __pycache__/ from P6 code citation check

### B-003: Add citations to fods_parser.py (not just Compat/)
**File**: `src/python/fods/` main source
**Change**: Spec authority comments in parse_fods(), document_from_fods(), sheet_from_xml()

### B-004: Run authority_conveyor.py pilot
**Change**: Document FODS advancement from P6(1 fact) → P6(10 facts)

---

## Phase C — Integrate Machinery (3 sprints)

Goal: Wire the dormant integration fabric and inject spec authority into the autonomous loop.

### C-001: Wire authority_integration_fabric.py
**File**: `tools/supervisor/autonomous_cycle.py`
**Change**: Add Step 0b-authority-state calling authority_integration_fabric.py

### C-002: Inject spec facts into worker prompts
**File**: `tools/supervisor/generate_next_worker_prompt.py`
**Change**: Add sal-facts + top-3 verified facts to READ_BEFORE_EXECUTION and prompt template

### C-003: Register 5 minimum spec authority skills
**File**: `.supervisor/skill-registry.yaml`
**Skills**: acquire-spec-t3, normalize-spec, extract-spec-facts, authority-gate-validation, pilot-rerun-authority

### C-004: Add authority_level to poc-targets.yaml
**File**: `product-capability-matrix/poc-targets.yaml`
**Change**: authority_level, highest_proven_fact, proof_graph_exists fields per format

---

## Phase D — Expand Coverage (6 sprints)

Goal: Advance CSV, TOML, NDJSON from P2 to P3+; expand ZST to full RFC8878 coverage.

- D-001: T3 + normalization for CSV (RFC4180) → P3+
- D-002: T3 + normalization for TOML (spec-toml.io) → P3+
- D-003: T3 + normalization for NDJSON (ndjson.org) → P3+
- D-004: Expand ZST from 2 to 94+ fact citations → P5+
- D-005: Behavioral spec-backed tests for FODT, ODS, ODT
- D-006: Sunset legacy_backfill exception after D-001..D-003 complete

---

## Phase E — Safe AI Assist (future, post A-D)

- E-001: Deploy embedding pipeline for FODS chunks.jsonl
- E-002: Add V49 governance validator (ai_draft cannot be cited as authoritative)
- E-003: Run contradiction detection for FODS code vs spec facts

---

## Phase F — Production Readiness (final)

- F-001: All ODF formats at P5+ (code + test citations)
- F-002: Product readiness dashboard shows authority level
- F-003: Pilot reruns documented for FODS, ZST, CSV

---

## Stop Conditions (No-Go Gates)

The autonomous pipeline MUST NOT drive new product expansion at scale until Phase A is complete:
- TC-GUARD-001 AND logic enforced
- V13 fires for absent spec_fact_refs (Tier 1 formats)
- product_task_selector calls authority_gate_validation.py

**Go/No-Go Verdict for current state**: NO-GO

**Go/No-Go Verdict after Phase A**: CONDITIONAL-GO (for Tier 1 formats at P4+; Tier 2 formats continue under exception)
