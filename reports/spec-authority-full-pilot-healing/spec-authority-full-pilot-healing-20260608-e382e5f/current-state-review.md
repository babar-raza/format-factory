# Current State Review — Spec Authority Full Pilot Healing Sprint

**Run ID:** spec-authority-full-pilot-healing-20260608-e382e5f
**Branch:** main
**HEAD:** e382e5fd8e65bc146c0821602cb8fb1ecfab982c
**Date:** 2026-06-08

---

## 1. Prior Package Findings Import (TCA-FULL-001)

### Package 122 (SPEC-AUTHORITY-LAYER-STOP-THE-BLEEDING-001)

**What was proven:**
- TCA-003: `.local/spec-source-registry/sources.jsonl` initialized (10 entries)
- TCA-009: Synthetic fixture `FODS-SPEC-001-requirements.json` quarantined (renamed to -synthetic-DO-NOT-USE)
- TCA-010: Verified facts review YAML created; FACT-FODS-001 verified from spec text
- TCA-012: Bypass ledger YAMLs written for Gnumeric and ABW

**What remained unproven (defects DEF-001 through DEF-010):**
- tests_run=0 (zero enforcement tests)
- anti-skip FAIL (missing_raw_logs, missing_sample_outputs)
- Adoption compliance FAIL_MISSING_TRANSCRIPTS
- No actual supervisor/product selector enforcement proven
- Gnumeric incorrectly classified as `no_public_spec_available` (has XSD)
- No negative tests proving spec_fact_refs blocks product work

### Package 123 (SPEC-AUTHORITY-LAYER-STOP-THE-BLEEDING-REPAIR-AND-ENFORCEMENT-001)

**What was proven:**
- `tools/supervisor/validate_spec_fact_refs.py` created — BLOCKING enforcement module
- `tools/supervisor/evidence_declaration.py` wired — `_validate_spec_fact_refs()` in `validate_schema()`
- `tools/supervisor/grade_declared_work.py` wired — `_check_spec_fact_refs_grade_impact()` + REJECTED grade
- `tools/supervisor/inspect_declared_evidence.py` wired — `_raw_item` passthrough
- `tools/supervisor/product_task_selector.py` wired — authority gate against BLOCKED_* states
- 25 enforcement tests pass (20 spec_fact_refs + 5 selector)
- Gnumeric bypass ledger corrected to `schema_authority_available`
- Supervisor cycle exit 0, 7/7 ACCEPTED, Adoption compliance PASS

**What remained unproven (live pilot verification missing):**
- No live pilot declarations run through the actual production pipeline
- Anti-skip still had `missing_sample_outputs` (LOW caveat)
- No sample outputs demonstrating rejection/acceptance behavior

---

## 2. Current Infrastructure State

### Enforcement Tooling

| File | Status |
|------|--------|
| `tools/supervisor/validate_spec_fact_refs.py` | ACTIVE — 6 valid exceptions, BLOCKING gate |
| `tools/supervisor/evidence_declaration.py` | WIRED — calls `_validate_spec_fact_refs()` |
| `tools/supervisor/grade_declared_work.py` | WIRED — REJECTED grade on spec_fact_refs violation |
| `tools/supervisor/inspect_declared_evidence.py` | WIRED — `_raw_item` passthrough |
| `tools/supervisor/product_task_selector.py` | PARTIALLY WIRED — see critical defect below |

### Critical Defect Found (TCA-FULL-008)

`product_task_selector.py` reads `data.get("poc_targets", [])` but `poc-targets.yaml` has NO `poc_targets` key.
Top-level keys are: `commercial_net_products`, `foss_reduced_products`, `on_hold`, `summary`.
→ `_get_format_authority_status()` ALWAYS returns "ALLOWED" for every format.
→ The authority gate in the selector NEVER fires in production.
→ This requires healing (TCA-FULL-008 REPAIR).

### Schema Discrepancy Found

`schemas/evidence/spec-fact-refs.schema.json` has 5 valid exceptions in its enum.
`tools/supervisor/validate_spec_fact_refs.py` has 6 (adds `schema_authority_available`).
→ Schema must be updated to match code (minor, non-blocking).

### FODS Authority Chain

- Spec cached: `.local/spec-cache/fods/1.3/OpenDocument-v1.3-os-part3-schema.pdf`
- Source SHA256: `sha256:92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066`
- Normalized text: `.local/spec-cache/fods/1.3/normalized/text.txt`
- Facts file: `.local/spec-cache/fods/1.3/workbench/verified-facts-review.yaml`
- FACT-FODS-001: `verification_status: verified`, `validated_by: independent_agent_verifier` ✓
- FACT-FODS-002 through FACT-FODS-010: `needs_review`
- Proof level: **P4** (source-backed requirements exist; tests exist; but supervisor enforcement only partial until selector gate is fixed)

### Gnumeric Schema Authority

- Schema: `gnumeric.xsd` — retrieved via WebFetch, namespace `http://www.gnumeric.org/v10.dtd`
- Retrieval status: `RETRIEVED_VIA_WEBFETCH`
- Full XSD not stored locally
- No verified facts file exists
- `exception_classification: schema_authority_available` — correct
- Proof level: **P1** (schema exists; no verified facts; no tests citing schema facts)

### ABW No-Public-Spec

- `abisource.com` is BLOCKED_SERVER_DOWN
- No schema/DTD retrievable
- `exception_classification: no_public_spec_available` — correct
- Proof level: **P0** (no authority document accessible; all code is pre-existing backfill)

### Synthetic Fixture Quarantine

- `FODS-SPEC-001-requirements-synthetic-DO-NOT-USE.json` — quarantined ✓
- `FODS-SPEC-001-requirements-QUARANTINE.md` — quarantine marker exists ✓

---

## 3. Tests Status (Baseline)

| Suite | Tests | Status |
|-------|-------|--------|
| test_spec_fact_refs_enforcement.py | 20 | ALL PASS |
| test_product_task_selector_authority_gate.py | 5 | ALL PASS (mocked YAML) |
| **Total** | **25** | **25/25 PASS** |

Note: selector tests pass because they mock the YAML data. In production, the gate never fires.

---

## 4. Planned Pilots

| Pilot | Expected | Current Status |
|-------|----------|----------------|
| TCA-FULL-002: Negative missing refs | REJECT | Not run |
| TCA-FULL-003: Positive spec-backed | ACCEPT | Not run |
| TCA-FULL-004: Legacy backfill readiness | REJECT readiness | Not run |
| TCA-FULL-005: Investigation abuse | REJECT product readiness | Not run |
| TCA-FULL-006: Invalid fact ID | REJECT | Not run |
| TCA-FULL-007: AI-only authority | REJECT | Not run |
| TCA-FULL-008: Selector blocked-format | BLOCK | NEEDS REPAIR FIRST |
| TCA-FULL-009: Continuation safety | SAFE | Not run |
| TCA-FULL-010: FODS authority chain | P4 chain | Not run |
| TCA-FULL-011: Gnumeric schema-authority | SCHEMA only, not product-ready | Not run |
| TCA-FULL-012: ABW no-public-spec | DEBT, no readiness | Not run |
| TCA-FULL-013: Synthetic fixture quarantine | REJECT as authority | Not run |
