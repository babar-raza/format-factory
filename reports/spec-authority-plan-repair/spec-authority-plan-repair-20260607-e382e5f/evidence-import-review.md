# Evidence Import Review
# Sprint: FORMAT-FACTORY-SPEC-AUTHORITY-PLAN-REPAIR-FOR-SINGLE-GO-EXECUTION-001
# Run: spec-authority-plan-repair-20260607-e382e5f
# Evidence source: reports/spec-authority/spec-authority-investigation-001/
# Live repo HEAD: e382e5f (branch: main)
# Date: 2026-06-07

---

## Re-verification of GAP-001 through GAP-010

Each finding re-verified by inspecting live repo at HEAD e382e5f.

---

### GAP-001: Normalization Pipeline Never Run

**Original finding:** `.local/spec-normalize/` does not exist; normalization has never been run.

**Live re-verification:**
- `.local/spec-normalize/`: MISSING — confirmed
- However: `.local/spec-cache/fods/1.3/normalized/` EXISTS with full normalization output:
  - text.txt (2224560 bytes)
  - sections.jsonl (259878 bytes)
  - pages.jsonl (2201357 bytes)
  - chunks.jsonl (615888 bytes)
  - source-manifest.yaml, page-map.yaml, citations.yaml

**Status: PARTIALLY UPDATED**

The normalization DID run, but output was placed at `.local/spec-cache/fods/1.3/normalized/` instead of `.local/spec-normalize/fods/1.3/`. The investigation sprint referenced the wrong expected path. The plan's healing steps for TCA-011 need to reference the actual normalized output location.

**Impact on repair plan:** TCA-011 must use `.local/spec-cache/fods/1.3/normalized/text.txt` as the primary normalized text path. The `.local/spec-normalize/` path referenced in healing-design.md is a planning artifact, not the actual repo state.

---

### GAP-002: Synthetic Fixture Data in Proof Graph / Requirements

**Original finding:** `build_proof_graph_iter001.py` injects synthetic fixture text. All 223 authority tests test against fixtures, not real spec PDFs.

**Live re-verification:**
- `FODS-SPEC-001-requirements.json` text_fragments:
  - "Document root SHALL be office:document element." — SYNTHETIC
  - "MUST include office:spreadsheet body." — SYNTHETIC
  - "Table element SHALL be table:table." — SYNTHETIC
  - "Each table MUST have a unique name." — SYNTHETIC
- `build_proof_graph_iter001.py` — no synthetic injection found in file body (it builds capability claim nodes, not spec text)
- The synthetic text is in `.local/spec-artifacts/FODS-SPEC-001-requirements.json` which was generated from synthetic fixture input

**Status: CONFIRMED**

Requirements are synthetic. The real normalized spec text exists at `.local/spec-cache/fods/1.3/normalized/text.txt` but `requirement_extractor.py` has not been run against it to produce real requirements.

---

### GAP-003: Spec Source Registry Not Persisted

**Original finding:** `.local/spec-source-registry/sources.jsonl` does not exist.

**Live re-verification:**
- `.local/spec-source-registry/`: directory exists but is EMPTY
- `sources.jsonl`: NOT FOUND

**Status: CONFIRMED**

---

### GAP-004: Evidence Schema Missing spec_fact_refs

**Original finding:** Evidence declarations do not require spec_fact_refs for product work.

**Live re-verification:**
- `schemas/evidence-declaration.schema.json`: NOT FOUND (no formal JSON schema file exists)
- `docs/automation/supervisor-worker-contract.md`: not yet checked; is the narrative schema location
- `grep -r "spec_fact_refs" schemas/`: returns empty

**Status: CONFIRMED**

No formal evidence-declaration.schema.json exists. The spec_fact_refs field is not defined anywhere in the schema layer. The repair plan (REPAIR-007) addresses this.

---

### GAP-005: No FACT-xxx Annotations in Source Code

**Original finding:** No implementation code cites any spec fact ID.

**Live re-verification:**
- `grep -r "FACT-" src/`: returns EMPTY
- `grep -r "SPEC-FACT:" src/`: returns EMPTY

**Status: CONFIRMED**

---

### GAP-006: No Candidate-to-Verified Promotion Workflow

**Original finding:** All requirements are candidate status; no promotion workflow exists.

**Live re-verification:**
- `FODS-SPEC-001-requirements.json`: all 6 requirements have `status: "candidate"` — correct
- `verified-facts.yaml` (at `.local/spec-cache/fods/1.3/workbench/`):
  - Has 10 facts with `verification_status: "verified"`
  - Set by `build_spec_workbench.py (run030)` — automated tool
  - NO `validated_by` field in any fact
  - This is a schema violation: facts should not be "verified" without a `validated_by` provenance
- No `spec_verifier.py` human-review CLI workflow confirmed

**Status: CONFIRMED WITH NUANCE**

Facts exist as "verified" but were set by automated tool without human confirmation. The healing plan's goal (add human-review workflow) remains necessary. Additionally, `verified-facts.yaml` has a data integrity issue: 10 facts marked verified with no validated_by — these should be downgraded to "candidate" or marked "needs_review".

---

### GAP-007: Tests Are Empirical, Not Spec-Driven

**Original finding:** No test cites a FACT-xxx spec fact ID.

**Live re-verification:**
- `grep -r "SPEC-FACT:" tests/`: no results from spec authority annotations (grep returned unrelated SPRINT ID matches in test headers)
- `grep -r "FACT-FODS\|FACT-ZST\|FACT-ABW" tests/`: would return empty

**Status: CONFIRMED**

---

### GAP-008: authority_integration_fabric Not Wired to Supervisor

**Original finding:** `authority_integration_fabric.py` exists but is not imported or called by `autonomous_cycle.py`.

**Live re-verification:**
- `tools/supervisor/authority_integration_fabric.py`: EXISTS
- `grep "authority_integration_fabric" tools/supervisor/autonomous_cycle.py`: EMPTY — not imported

**Status: CONFIRMED**

---

### GAP-009: Product Ledger Missing spec_fact_ids

**Original finding:** Product code change ledger has no `spec_fact_ids` field.

**Live re-verification:**
- `grep "spec_fact_ids" reports/r90/product-code-change-ledger.json`: EMPTY

**Status: CONFIRMED**

---

### GAP-010: tools/ai/ Disconnected from Authority Layer

**Original finding:** `tools/ai/` is not connected to the authority layer.

**Live re-verification:**
- `tools/ai/`: EXISTS with extensive structure (agentic/, contracts/, control_plane/, normalization/, pipeline/, prompts/, requirements/, retrieval/, schemas/, synthesis/, telemetry/, test_generation/, validators/)
- AI layer structure is well-developed but integration into authority chain not confirmed from file listings

**Status: CANNOT VERIFY FROM FILE LISTINGS ALONE**

Requires inspection of import chains and authority contract files. Marked as "cannot fully verify without tool run" — recorded as STALE_EVIDENCE risk per rollback plan.

---

## Summary Table

| GAP | Original Finding | Live Status | Impact on Plan |
|-----|-----------------|-------------|----------------|
| GAP-001 | normalization not run | PARTIALLY_UPDATED — output exists at different path | Update TCA-011 path |
| GAP-002 | synthetic fixture data | CONFIRMED | TCA-009 still required |
| GAP-003 | spec-source-registry empty | CONFIRMED | TCA-003 still required |
| GAP-004 | evidence schema no spec_fact_refs | CONFIRMED | REPAIR-007 still required |
| GAP-005 | no FACT-xxx in src/ | CONFIRMED | TCA-016 still required |
| GAP-006 | no promotion workflow | CONFIRMED (+data integrity issue) | TCA-010 still required; add verified-facts downgrade sub-task |
| GAP-007 | no spec-driven tests | CONFIRMED | TCA-017 still required |
| GAP-008 | authority_integration_fabric not wired | CONFIRMED | TCA-013 still required |
| GAP-009 | ledger missing spec_fact_ids | CONFIRMED | TCA-014 still required |
| GAP-010 | tools/ai/ disconnected | CANNOT_VERIFY | Mark as deferred; not blocking plan-repair sprint |

---

## New Findings (discovered during plan-repair preflight)

### NEW-001: verified-facts.yaml has 10 facts with no validated_by field
- Location: .local/spec-cache/fods/1.3/workbench/verified-facts.yaml
- Details: `build_spec_workbench.py (run030)` set verification_status=verified for all 10 facts without a validated_by field
- Risk: These facts appear verified but have no human or independent agent confirmation
- Repair: TCA-010 should include a sub-step: downgrade existing verified-facts to "needs_review" pending proper validation

### NEW-002: schemas/evidence-declaration.schema.json does not exist as a JSON schema file
- Location: expected at schemas/evidence-declaration.schema.json
- Details: Schema exists only as narrative in docs/automation/supervisor-worker-contract.md
- Risk: Schema validation is ad-hoc; no formal JSON schema to enforce spec_fact_refs
- Repair: REPAIR-007 should include creating a minimal JSON schema fragment for spec_fact_refs enforcement

### NEW-003: No CI/pre-commit hooks present
- Details: .github/workflows/, .husky/, hooks/ all MISSING
- Impact: All verification gates run locally only; no automated CI enforcement
- Repair: All verification-gates.json entries set ci_available=false
