# Healing Architecture — Spec Authority Layer
## Run ID: spec-authority-machinery-explosion-20260625-c6b2470

---

## 1. Design Principles

### Principle 1: Two-Tier Authority Model
The system MUST accept two permanent tiers:

**Tier 1 — Formal Spec Formats** (FODS, FODT, ODS, ODT, FODG, FODP, ZST, CSV, TOML, NDJSON, QOI, PBM, PGM, PPM)
- P4+ is achievable and required for product expansion
- T3 authorization must be completed before P3 advancement
- proof graph required for P6 claim
- spec_fact_refs mandatory in PRODUCT_SOURCE evidence (no legacy_backfill exception after 2 sprints)

**Tier 2 — Exception Formats** (Gnumeric, ABW, SYLK, DIF, TSV)
- P1 is the correct ceiling — no formal published spec exists
- exception_classification (schema_authority_available or no_public_spec_available) is permanent
- Product expansion allowed under exception, not by bypassing spec authority
- Product code can exist at P1 but must be documented as schema-grounded, not spec-grounded

Do NOT force P4 on Tier 2 formats. The exception classifications are correct.

### Principle 2: FODS Vertical Slice as Template
The FODS chain (PDF → 4988 facts → Compat/ citations → behavioral tests → proof graph) is the production template. All repairs must preserve this chain and extend it.

### Principle 3: Fail-Closed Authority Gates
Every spec authority gate must fail-closed (block when data absent) not fail-open (allow when data absent). The V13 absent=no-op and TC-GUARD-001 OR logic are the primary failure modes.

### Principle 4: No New Product Expansion Without P4
After Phase A repairs close, no new Tier 1 format should receive product expansion tasks unless authority_gate_validation.py returns P4+. The product_task_selector must enforce this.

### Principle 5: AI Assists, Never Authorizes
LLM tools may assist with spec section candidate retrieval and contradiction detection. LLM output is always labeled ai_draft and requires human verification before advancing to P4+. This principle must be enforced by a governance validator (V49), not just policy.

---

## 2. Target Architecture (Post-Healing)

```
[External Spec Source]
         │
         ▼ (after T3 authorization)
acquire_spec.py  ← governed skill: acquire-spec-t3
         │
         ▼
spec_normalizer.py  ← governed skill: normalize-spec
         │
         ▼
run_extraction_pipeline.py  ← governed skill: extract-spec-facts
         │
         ▼
spec_verifier.py  ← governed skill: verify-spec-facts
         │
         ▼
.local/spec-cache/{format}/workbench/verified-facts.yaml
         │
         ▼
requirement_extractor.py  ← governed skill: generate-requirement-pack
         │
         ▼
sal-facts-{format}.json  ← canonical FACT-{FMT}-NNN registry
         │
    ┌────┴────┐
    │         │
    ▼         ▼
authority_gate_validation.py    authority_integration_fabric.py
→ P-level per format             ← called from autonomous_cycle.py Step 0b
→ product_expansion_allowed       → generates authority-integration-contract.json
→ enforced in product_task_selector → updates requirements_authority/graph_store
    │                                 → runs coverage_evaluator
    ▼                                 → runs overclaim_detector
product_task_selector.py
→ checks actual P-level from authority_gate_validation.py
→ blocks P<4 formats (no exception) from product tasks
→ allows P1 formats with exception_classification
         │
         ▼
generate_next_worker_prompt.py
→ injects: authority_level, top-N verified facts, requirement_pack_path
→ READ_BEFORE_EXECUTION: + sal-facts-{format}.json, workbench/requirement-packs/
         │
         ▼
[Worker executes with spec-grounded requirements]
→ Code cites: # Spec authority: {element} (FACT-{FMT}-NNN, §X.Y)
→ Tests cite: FACT-{FMT}-NNN with behavioral assertions
         │
         ▼
[Evidence declaration]
→ spec_fact_refs: ["FACT-{FMT}-NNN"] (mandatory for Tier 1)
→ exception_classification: (valid for Tier 2)
→ gap_ledger_ref: GAP-{FORMAT}-*
         │
         ▼
[V13 enforcement — FIXED]
→ FIRES when: spec_fact_refs absent AND no exception_classification AND PRODUCT_SOURCE
→ FIRES when: spec_fact_refs present AND invalid
→ PASSES when: exception_classification present (Tier 2 formats)
         │
         ▼
[TC-GUARD-001 enforcement — FIXED]
→ REQUIRES: gap_ledger_ref AND (spec_fact_refs OR exception_classification)
→ OR logic removed
         │
         ▼
[authority_integration_fabric.py — WIRED]
→ Updates proof graph per sprint close
→ Records authority_level in product ledger
→ Runs overclaim detector
         │
         ▼
[poc-targets.yaml — UPDATED]
→ authority_level column added per format
→ Records highest proven FACT-* per format
→ Displays in product readiness dashboard
```

---

## 3. File Changes Required

### autonomous_cycle.py (tools/supervisor/)
1. **Step 0b-authority-state**: Add call to `authority_integration_fabric.py` before Step 1
2. **Step 2d3 TC-GUARD-001**: Change OR to AND — gap_ledger_ref AND (spec_fact_refs OR exception_classification)
3. **Step 5**: Inject authority_level into next sprint prompt generation

### product_task_selector.py (tools/supervisor/)
1. **`_get_format_authority_status()`**: Call `authority_gate_validation.py --format-id {fmt} --json` and return actual P-level
2. **`_BLOCKED_AUTHORITY_STATES`**: Populate from P-level lookup (block P0, P1 without exception)
3. **Remove `_CANDIDATE_CATALOG`**: Replace with dynamic selection from gap-ledger + authority gate

### governance_validators.py (tools/supervisor/)
1. **V13 `validate_spec_fact_refs_wired()`**: Add ABSENT check — fire when spec_fact_refs absent AND no exception_classification AND PRODUCT_SOURCE

### supervisor-worker-contract.md (docs/automation/)
1. Add `spec_fact_refs` as required-or-explain field with guidance:
   - For Tier 1 formats: provide FACT-{FMT}-* IDs from sal-facts-{format}.json
   - For Tier 2 formats: provide exception_classification instead
   - For both: gap_ledger_ref required

### generate_next_worker_prompt.py (tools/supervisor/)
1. **READ_BEFORE_EXECUTION**: Add `sal-facts-{format}.json` and `workbench/requirement-packs/` for target format
2. **Prompt template**: Inject authority_level and top-3 verified facts for target format

### poc-targets.yaml (product-capability-matrix/)
1. Add `authority_level` field per format entry (populated from authority_gate_validation.py)
2. Add `highest_proven_fact` field (e.g., "FACT-FODS-001")
3. Add `proof_graph_exists` boolean field

### .supervisor/skill-registry.yaml
1. Register: acquire-spec-t3, normalize-spec, extract-spec-facts, authority-gate-validation, pilot-rerun-authority

---

## 4. Non-Changes (Intentional)

- **Tier 2 exception_classifications**: Do NOT remove. Gnumeric=schema_authority_available, ABW/SYLK/DIF/TSV=no_public_spec_available are architecturally correct.
- **FODS Compat/ code**: Do NOT remove existing FACT-FODS-* citations. These are the reference implementation.
- **fods-p6-proof-graph.yaml**: Do NOT modify. Extend it by adding FACT-FODS-002..010.
- **refresh_check.py non-blocking**: Keep non-blocking. Advisory status is correct for staleness checks.
- **V13 exception_classification bypass**: Keep for Tier 2 formats. Only close the absent-spec-fact bypass for Tier 1.
