# Product Governance Healing Sprint — Authoritative Execution Plan
**Plan ID:** iterative-mixing-shannon
**Type:** governance_healing
**Mission:** FF-PGH-001
**Authority source:** This file. All other documents are analysis artifacts only.
**authoritative_plan:** C:/Users/prora/.claude/plans/iterative-mixing-shannon.md
**Plan version:** v2.0 (micro-taskcardized, machine-state hardened)

---

## PART I — PREFLIGHT ANALYSIS

### P1.1 — Repository + Plan State

```
repository:          C:/Users/prora/OneDrive/Documents/GitHub/format-factory
branch:              main
head:                af879e55 (verified 2026-07-10)
active plan path:    C:/Users/prora/.claude/plans/iterative-mixing-shannon.md
plan title:          Product Governance Healing Sprint
plan format:         markdown with embedded YAML structures
authority source:    this file (plan mode, current conversation)
plan size (v1):      ~900 lines, 19 parent taskcards, no children, no micro-steps
major sections:      6 phases (A–F), 1 context, 1 verification, 1 execution notes
existing children:   NONE
existing micro-steps: NONE
existing state vocab: OPEN (single flat status — insufficient)
existing validation: acceptance criteria only — no commands
existing evidence:   not specified per taskcard
existing DAG:        implicit phase ordering only
duplicate-plan risk: LOW — one plan file found, no competing v2/final/revised variants
```

### P1.2 — Critical Pre-execution Corrections

The following defects were found in plan v1 and are CORRECTED in this v2. Do not use v1 instructions where v2 contradicts them.

| # | Defect | v1 (WRONG) | v2 (CORRECT) |
|---|--------|-----------|-------------|
| C1 | Validator module path | `tools/governance/governance_validators_product_gov.py` | `tools/supervisor/governance_validators_product_gov.py` |
| C2 | Current expected_count | "165" | **167** (verified at HEAD, `governance_validator_runner.py` line 813) |
| C3 | New expected_count | "179" | **181** (167 + 14 new validators V150–V163) |
| C4 | TC-PGH-013 redundancy | Separate parent TC | Folded into TC-PGH-007 as child TC-PGH-007-04 |
| C5 | tools/governance/ status | "may already exist — check" | **EXISTS** — 8 CI governance tools present. Extend only. |
| C6 | registry/governance/ status | Assumed exists | **DOES NOT EXIST** — must be created with `mkdir` |
| C7 | reports/product-governance/ status | Assumed exists | **DOES NOT EXIST** — must be created with `mkdir` |
| C8 | governance_validators_product_gov.py | Assumed exists | **DOES NOT EXIST** — must be created fresh |
| C9 | lane-scope-registry.yaml | "add governance lane manually" | File is **machine-generated** — must be re-generated, not hand-edited |
| C10 | Pilot 9 target | "pick from audit" (undefined) | Pre-scoped: add missing INTENTIONAL_UNMAPPED to one FODS model class found in TC-PGH-003 audit |
| C11 | Primary FODS class name | `FodsDocument` (plan v1) | **`FodsDocument`** — verified in `src/python/fods/models.py`; `FodsDocument` does NOT exist |
| C12 | FODS parser filename | `parser.py` | **`parser.py`** — verified at `src/python/fods/parser.py`; exports `parse_fods()` |
| C13 | FODS writer filename | `writer.py` | **`writer.py`** — verified at `src/python/fods/writer.py`; exports `write_fods()` |
| C14 | Pilot 1 method implementation | `[ws.name for ws in self.worksheets]` | `[s.name for s in self.sheets()]` — `sheets()` is already a method on `FodsDocument` returning `list[FodsSheet]`; `FodsSheet.name` is a property |
| C15 | Pilot 9 default class | `fods.models.FodsFormula` | **DOES NOT EXIST** in models.py — all 3 FODS model classes (`FodsDocument`, `FodsSheet`, `FodsCell`) already have `spec_qname`; Pilot 9 target must come from TC-PGH-003-02 audit of OTHER formats or spec/ subclasses |

### P1.3 — Existing Infrastructure Verified

```
tools/governance/ (EXISTS — extend only):
  check_docs_placement.py, check_git_safety.py, check_methodology_links.py,
  ci_skill_attribution_check.py, install_hooks.py, pre_mutation_guard.py,
  run_ci_governance_check.py, validate_taskcard_execution_contract.py

.supervisor/schemas/ (EXISTS — 25 schemas):
  autonomous-execution-contract, evidence-bundle-contract, evidence-declaration,
  evidence-manifest, evidence-review, gate-definition, governance-contract,
  human-gate-classification, item-grade, loop-decision-state-machine,
  next-ruflo-lanes, next-sprint-taskmaster, next-work-items, project-adapter-contract,
  proof-backed-poc-gate, skill-registry, stage1-issue-model, stage2-taskcard-contract,
  stage3-quality-scoring-rubric, stop-reason-decision, summary-parser-contract,
  supervisor-cycle-manifest, supervisor-review, supervisor-verdict, taskcard-state-machine

tests/governance/ (EXISTS):
  test_capability_parity.py, test_check_git_safety.py, test_methodology_links.py, fixtures/

tests/supervisor/test_governance_validators_integration.py (EXISTS):
  asserts len(summary["validators"]) >= 29 (soft lower-bound, not hard equal — safe to add)

registry/lane-scope-registry.yaml (EXISTS — machine-generated 2026-07-03)
```

---

## PART II — PRESERVED CONTEXT

Format Factory has sophisticated execution governance (165+ validators, evidence declarations, plan locks, gate system) but lacks **product lifecycle governance**: no formal change proposals before material changes, no governed artifact lifecycle (DRAFT→RELEASED), no traceability chain enforcement (PUBLIC_API→QNAME→SPEC_FACT→TEST→RELEASE), no change-impact analysis records, no promotion records with baselines, no reopening conditions enforced, and no product governance ledger. The pipeline that creates products is also ungoverned relative to its effect on generated outputs.

This plan implements the 20-section governance healing specification. It **extends** existing infrastructure (validators, schemas, lanes, gap ledger, format-registry) rather than replacing it. All governance artifacts integrate with the existing supervisor pipeline via the evidence declaration system.

**Key existing infrastructure to reuse:**
- `tools/supervisor/governance_validator_runner.py` — extend `expected_count` (167 → 181)
- `tools/supervisor/governance_validators_ext4.py` — style reference for new validator module
- `.supervisor/schemas/` — add 9 new schemas alongside existing 25
- `registry/format-registry.yaml` — add `governance_status:` fields per format
- `.supervisor/skill-registry.yaml` — add `change_proposal_required` field
- `tools/supervisor/lifecycle_audit.py` — existing plan audit machinery

**Non-goals:**
- Do NOT replace existing validators or schemas
- Do NOT create a parallel supervisor pipeline
- Do NOT add product format features beyond Pilot 1's minimal `get_worksheet_names()`
- Do NOT hand-edit `registry/lane-scope-registry.yaml` — it is machine-generated

---

## PART III — NORMALIZED REQUIREMENTS INVENTORY

Each requirement maps to one or more taskcards. IDs are stable across reruns.

| Req ID | Source § | Requirement | Parent TC(s) |
|--------|----------|-------------|-------------|
| REQ-GOV-001 | §1 | Single governance-binding.yaml enumerating all authorities with precedence | TC-PGH-001 |
| REQ-GOV-002 | §2 | governance-control-inventory.yaml covering all 16 lifecycle stages | TC-PGH-002 |
| REQ-GOV-003 | §16 | product-governance-ledger.yaml with all ungoverned-change findings | TC-PGH-003 |
| REQ-GOV-004 | §3 | governed-artifact schema + pilot artifact-registry.yaml | TC-PGH-004 |
| REQ-GOV-005 | §4 | change-proposal schema + manager CLI + 2 pilot proposals | TC-PGH-005 |
| REQ-GOV-006 | §5 | change-impact schema + impact_analyzer.py | TC-PGH-006 |
| REQ-GOV-007 | §10 | change-decision schema + pilot decision records | TC-PGH-006 |
| REQ-GOV-008 | §11 | promotion-record schema + promotion_manager.py + PROM-FODS-001 | TC-PGH-007 |
| REQ-GOV-009 | §13 | release-candidate schema + release_eligibility_checker.py + RC-FODS-PYREL-001 | TC-PGH-007 |
| REQ-GOV-010 | §6 | Traceability chain builder + V150–V152 architecture validators | TC-PGH-008 |
| REQ-GOV-011 | §7 | Pipeline change governor + V153–V155 pipeline validators | TC-PGH-009 |
| REQ-GOV-012 | §8 | pre_write_checklist.py + file-ownership.yaml + V156 | TC-PGH-010 |
| REQ-GOV-013 | §9 | doc_compliance_checker.py + traceability-graph.yaml + V157–V158 | TC-PGH-011 |
| REQ-GOV-014 | §12 | reopening_detector.py + V159 | TC-PGH-012 |
| REQ-GOV-015 | §14 | maintenance_classifier.py + V160 | TC-PGH-012 |
| REQ-GOV-016 | §17 | governance_validators_product_gov.py + runner update + schema tests | TC-PGH-014 |
| REQ-GOV-017 | §17 | artifact-registry.yaml backfill (20 Python + 5 .NET + 15 pipeline) | TC-PGH-015 |
| REQ-GOV-018 | §18.1 | Pilot 1: product API change full lifecycle | TC-PGH-016 child 01 |
| REQ-GOV-019 | §18.2 | Pilot 2: rejected change proof | TC-PGH-016 child 02 |
| REQ-GOV-020 | §18.3 | Pilot 3: pipeline change with product pilot | TC-PGH-016 child 03 |
| REQ-GOV-021 | §18.4 | Pilot 4: documentation-only change | TC-PGH-016 child 04 |
| REQ-GOV-022 | §18.5 | Pilot 5: compatibility-breaking change gating | TC-PGH-016 child 05 |
| REQ-GOV-023 | §18.6 | Pilot 6: promoted artifact modification reopening | TC-PGH-017 child 01 |
| REQ-GOV-024 | §18.7 | Pilot 7: release candidate eligibility check | TC-PGH-017 child 02 |
| REQ-GOV-025 | §18.8 | Pilot 8: generated-output drift detection | TC-PGH-017 child 03 |
| REQ-GOV-026 | §18.9 | Pilot 9: maintenance fix full lifecycle | TC-PGH-017 child 04 |
| REQ-GOV-027 | §18.10 | Pilot 10: idempotency proof | TC-PGH-017 child 05 |
| REQ-GOV-028 | §19 | completion_gate_checker.py measuring 22 counters = 0 | TC-PGH-018 |
| REQ-GOV-029 | §20 | governance-report.md with final verdict | TC-PGH-019 |

---

## PART IV — SOLUTION OPTIONS (Key Decisions)

### D1: Where to place new validators

**Option A (SELECTED):** `tools/supervisor/governance_validators_product_gov.py`
- Follows existing pattern; runner imports from `tools/supervisor/`
- Idiomatic; no sys.path changes needed; survives runner refactors
- Score: 5/5 root-cause, 5/5 integration, 5/5 maintainability

**Option B (REJECTED):** `tools/governance/governance_validators_product_gov.py`
- Would require adding `tools/governance/` to sys.path in runner
- Breaks naming convention; runner imports only from tools/supervisor/
- Score: 2/5 integration

### D2: TC-PGH-013 redundancy

**Option A (SELECTED):** Fold TC-PGH-013 into TC-PGH-007 as child TC-PGH-007-04
- Eliminates confusion; release eligibility tools are built in TC-PGH-007
- TC-PGH-013 only adds report generation — this is a child of TC-PGH-007

**Option B (REJECTED):** Keep as separate parent
- Creates artificial split between tool building (TC-PGH-007) and running it (TC-PGH-013)

### D3: Pilot 9 target scoping

**Option A (SELECTED):** After TC-PGH-003 audit, apply maintenance fix to the FIRST `missing_qname` gap found in FODS source. If no FODS gap found, add `INTENTIONAL_UNMAPPED` annotation to `fods.models.FodsFormula` (a known model class without spec_qname).
- Pre-scoped; unambiguous; safe; demonstrates defect_fix maintenance lifecycle

**Option B (REJECTED):** "Pick from audit" — too vague for weak agent execution

### D4: Pilot 3 pipeline change target

**Option A (SELECTED):** Add a `# governance: change_proposal_ref: CP-PILOT-003` header comment to `.claude/commands/add-python-api.md` (documentation-level change to skill file). Verify product pilot: run `python tools/governance/pipeline_change_governor.py pilot --skill add-python-api --format fods`.
- Low risk; proves governance tracking of pipeline files; no logic changes

**Option B (REJECTED):** Modify actual skill logic — too risky during governance sprint

### D5: lane-scope-registry.yaml governance lane

**Option A (SELECTED):** Generate updated `registry/lane-scope-registry.yaml` by calling the existing generator script (if available) or by appending a new lane entry using `python tools/supervisor/scope_guard.py add-lane governance-healing` (check if such CLI exists first). If no generator exists, add lane entry directly to YAML with a NOTE that it needs machine-regeneration on next sync.
- Pragmatic; avoids hand-editing machine-generated file without understanding the generator

**Option B (REJECTED):** Hand-edit without checking generator — violates "do not hand-edit machine-generated files" rule

---

## PART V — TASKCARD MASTER TABLE (v2)

| TC-ID | Phase | Req | Title | Children | Status |
|-------|-------|-----|-------|----------|--------|
| TC-PGH-001 | A | REQ-GOV-001 | Governance Binding Record | 3 | PROPOSED |
| TC-PGH-002 | A | REQ-GOV-002 | Governance Control Inventory | 4 | PROPOSED |
| TC-PGH-003 | A | REQ-GOV-003 | Current State Audit + Ledger | 4 | PROPOSED |
| TC-PGH-004 | B | REQ-GOV-004 | Governed Artifact Schema + Model | 3 | PROPOSED |
| TC-PGH-005 | B | REQ-GOV-005 | Change Proposal Schema + Manager | 4 | PROPOSED |
| TC-PGH-006 | B | REQ-GOV-006,007 | Impact Analysis + Decision Schemas | 4 | PROPOSED |
| TC-PGH-007 | B | REQ-GOV-008,009 | Promotion + Release Candidate Schemas | 4 | PROPOSED |
| TC-PGH-008 | C | REQ-GOV-010 | Product Architecture Traceability Chain | 4 | PROPOSED |
| TC-PGH-009 | C | REQ-GOV-011 | Pipeline Governance Enforcement | 3 | PROPOSED |
| TC-PGH-010 | C | REQ-GOV-012 | Code Writing Governance Checklist | 3 | PROPOSED |
| TC-PGH-011 | C | REQ-GOV-013 | Documentation + Traceability Graph | 3 | PROPOSED |
| TC-PGH-012 | C | REQ-GOV-014,015 | Reopening Detector + Maintenance Classifier | 3 | PROPOSED |
| TC-PGH-014 | D | REQ-GOV-016 | Governance Machinery Integration | 4 | PROPOSED |
| TC-PGH-015 | D | REQ-GOV-017 | Artifact Backfill (Products + Pipeline) | 3 | PROPOSED |
| TC-PGH-016 | E | REQ-GOV-018–022 | Required Pilots 1–5 | 5 | PROPOSED |
| TC-PGH-017 | E | REQ-GOV-023–027 | Required Pilots 6–10 | 5 | PROPOSED |
| TC-PGH-018 | F | REQ-GOV-028 | Completion Gate — 22 Counters | 3 | PROPOSED |
| TC-PGH-019 | F | REQ-GOV-029 | Final Governance Report | 2 | PROPOSED |

*Note: TC-PGH-013 REMOVED — folded into TC-PGH-007-04.*

---

## PART VI — DEPENDENCY DAG

Execute in this order. Tasks within the same group may run in parallel only if they touch different files.

```
GROUP 1 (no dependencies):
  TC-PGH-001 → creates registry/governance/ + governance-binding.yaml + schema
  TC-PGH-003 → creates reports/product-governance/ + audit ledger + schema
    (TC-PGH-003 runs investigation; TC-PGH-001 creates binding — independent)

GROUP 2 (requires GROUP 1 complete):
  TC-PGH-002 → requires reports/product-governance/ from TC-PGH-003
                requires registry/governance/governance-binding.yaml from TC-PGH-001

GROUP 3 (requires TC-PGH-001 complete):
  TC-PGH-004 → requires registry/governance/ directory from TC-PGH-001
  TC-PGH-005 → requires registry/governance/ directory from TC-PGH-001
  TC-PGH-006 → requires TC-PGH-005 schema + registry/governance/change-proposals/
  TC-PGH-007 → independent of TC-PGH-005/006 (different schema)
    NOTE: TC-PGH-006 must precede TC-PGH-007 if promotion records reference decision IDs

GROUP 4 (requires GROUP 3 complete — Phase C tools):
  TC-PGH-008 → requires TC-PGH-004 artifact-registry.yaml (for traceability_chain_builder)
  TC-PGH-009 → requires TC-PGH-005 (change-proposal schema for pipeline governor)
  TC-PGH-010 → requires TC-PGH-005 (file-ownership.yaml references change_proposal_ids)
  TC-PGH-011 → requires TC-PGH-008 (traceability_chain_builder.py outputs traceability-graph.yaml)
  TC-PGH-012 → requires TC-PGH-007 (reopening_detector reads promotion records)

GROUP 5 (requires all Phase C tools complete):
  TC-PGH-014 → integrates all new validators into runner — requires TC-PGH-008/009/010/011/012
  TC-PGH-015 → requires TC-PGH-004 (artifact schema) + TC-PGH-007 (promotion schema)

GROUP 6 (requires GROUP 5):
  TC-PGH-016 → requires all schemas + tools + validators from Groups 3-5
  TC-PGH-017 → requires TC-PGH-016 (Pilot 7 references Pilot 1 artifacts)
                TC-PGH-012 reopening_detector.py required for Pilot 6

GROUP 7 (requires GROUP 6):
  TC-PGH-018 → requires all 10 pilots complete
  TC-PGH-019 → requires TC-PGH-018 (references 22 counter results)
```

**File ownership locks (no two tasks may modify simultaneously):**

| File | Owned by |
|------|----------|
| `tools/supervisor/governance_validators_product_gov.py` | TC-PGH-008-04 (creates), TC-PGH-009-03 (extends), TC-PGH-010-03, TC-PGH-011-03, TC-PGH-012-03 — must be SEQUENTIAL |
| `tools/supervisor/governance_validator_runner.py` | TC-PGH-014-03 only |
| `tests/supervisor/test_governance_validators_integration.py` | TC-PGH-014-04 only |
| `registry/format-registry.yaml` | TC-PGH-014-05 only |
| `.supervisor/skill-registry.yaml` | TC-PGH-014-02 only |

---

## PART VII — MACHINE STATE RULES

### Valid parent taskcard transitions:
```
PROPOSED → READY                  (prerequisites confirmed)
READY → IN_PROGRESS               (first child started)
IN_PROGRESS → CHILDREN_IN_PROGRESS (all children started)
CHILDREN_IN_PROGRESS → INTEGRATION_PENDING (all children CLOSED)
INTEGRATION_PENDING → VERIFIED    (integration checks pass)
VERIFIED → SCORED                 (quality scoring complete)
SCORED → CLOSED                   (all quality dims ≥ 4/5)
SCORED → REROUTED                 (any quality dim < 4/5)
any → BLOCKED                     (unresolvable blocker)
any → BLOCKED_EXTERNAL            (TRUE_EXTERNAL_GATE)
any → DEFERRED_WITH_REASON        (explicit deferral)
```

### Valid child taskcard transitions:
```
TODO → READY → IN_PROGRESS → IMPLEMENTED → VERIFIED → SCORED → CLOSED
SCORED → REROUTED → IN_PROGRESS (rework)
any → BLOCKED → READY (when unblocked)
any → BLOCKED_EXTERNAL (TRUE_EXTERNAL_GATE)
any → DEFERRED_WITH_REASON
```

### Invalid transitions (blocked):
```
TODO → CLOSED (skip verification)
READY → CLOSED (skip implementation)
IMPLEMENTED → CLOSED (skip verification)
REROUTED → CLOSED (without rework)
parent CLOSED while any mandatory child is not CLOSED
parent CLOSED without integration evidence
```

### Micro-step transitions:
```
PENDING → READY → ACTIVE → COMPLETE
ACTIVE → FAILED → READY (retry)
ACTIVE → BLOCKED → READY (when unblocked)
PENDING → SKIPPED_NOT_APPLICABLE (must record reason)
```

---

## PART VIII — ENHANCED TASKCARDS

---

### TC-PGH-001 — Governance Binding Record

```
Parent Taskcard ID: TC-PGH-001
Title: Create governance-binding.yaml enumerating all authorities with precedence
Type: PARENT
Status: PROPOSED
Owner: governance_lane
Supervisor: plan_supervisor

Source:
  Plan requirement ID: REQ-GOV-001
  Plan section: §1
  Deep-analysis finding: No single authority binding record exists in the repo.
    Authorities are scattered across CLAUDE.md, registry/, docs/. Need one canonical
    file that a future governance validator (V161+) can read to confirm authority.
  Root cause: System healing focus omitted the meta-layer of governance.
  Selected solution: Create registry/governance/governance-binding.yaml + schema.

Objective:
  - Produce one YAML file that enumerates all authorities in required precedence order,
    with verified file paths and decision scopes.

Outcome:
  - registry/governance/governance-binding.yaml exists and validates against its schema.
  - All 8 authority precedence slots are filled.
  - All referenced paths resolve to real files in the repository.

Scope:
  Allowed files:
    - registry/governance/governance-binding.yaml (CREATE NEW)
    - .supervisor/schemas/governance-binding.schema.json (CREATE NEW)
    - plans/.claude/iterative-mixing-shannon.md (this plan — update status only)
  Allowed folders: registry/governance/ (CREATE), .supervisor/schemas/
  Forbidden files: ALL other files
  Forbidden folders: src/, tests/, tools/supervisor/, oracle/

Preserved behavior:
  - Existing registry/ files unchanged
  - Existing schemas unchanged

Inputs:
  - registry/gate-contract-registry.yaml (authority reference)
  - registry/gate11-criteria.yaml (authority reference)
  - docs/code-quality/production-library-standard-v2.md (authority reference)
  - docs/gates/python-release-gate-definitions.md (authority reference)
  - .governance/capabilities/registry.yaml (authority reference)
  - shared/qname-registry/ (authority reference)

Outputs:
  - registry/governance/governance-binding.yaml
  - .supervisor/schemas/governance-binding.schema.json

Dependencies: NONE (first task, creates registry/governance/ directory)

Child taskcards:
  - TC-PGH-001-01: Verify authority file paths + create registry/governance/ directory
  - TC-PGH-001-02: Write governance-binding.schema.json
  - TC-PGH-001-03: Write governance-binding.yaml and validate against schema

Parent acceptance criteria:
  - registry/governance/ directory exists
  - governance-binding.yaml validates against governance-binding.schema.json
  - All 8 required_authority_order slots (1–8) filled with non-null values
  - All path values in specification_authorities, qname_authorities, etc. resolve to real files
  - python -c "import yaml; yaml.safe_load(open('registry/governance/governance-binding.yaml'))" exits 0

Evidence required:
  - Path-verification log: list of all referenced paths + EXISTS/MISSING status
  - Schema validation log: jsonschema output

Quality dimensions (all must score ≥ 4/5):
  - requirement correctness (does it match §1 spec?)
  - root-cause coverage (does it bind ALL authority types listed in §1?)
  - integration completeness (does it reference real paths?)
  - evidence completeness (schema validation log present?)
  - regression safety (no existing files modified?)

Closeout criteria:
  - TC-PGH-001-01 CLOSED, TC-PGH-001-02 CLOSED, TC-PGH-001-03 CLOSED
  - parent integration check passes (yaml.safe_load + path resolution)

Rollback:
  - Delete registry/governance/governance-binding.yaml and .supervisor/schemas/governance-binding.schema.json
  - Delete registry/governance/ if empty

Reroute rule:
  If any path in governance-binding.yaml resolves to MISSING, mark TC-PGH-001-01 REROUTED
  and repair the path before closing TC-PGH-001-03.
```

#### TC-PGH-001-01 — Verify authority paths + create directory

```
Child Taskcard ID: TC-PGH-001-01
Parent Taskcard ID: TC-PGH-001
Title: Verify all planned authority file paths exist; create registry/governance/ directory
Type: CHILD
Status: TODO

Source:
  Req: REQ-GOV-001
  Section: §1 authority-binding inputs
  Analysis: Cannot create a valid governance-binding.yaml without first confirming
    every referenced path exists. One broken path makes the binding misleading.

Purpose:
  Confirm all authority paths before writing the binding YAML.

Scope:
  Allowed files: READ-ONLY on all files being verified
  Allowed operation: inspect + record + create directory (mkdir)
  Forbidden: modify any existing file

Inputs:
  - Planned path list from §1 (see TC-PGH-001 inputs above)

Expected output:
  - A written record (in evidence) of all paths and their EXISTS/MISSING status
  - registry/governance/ directory created

Preconditions: NONE

Micro-steps:
  MS-PGH-001-01-01: Check existence of oracle/schemas/odf-1.3-relaxng/ directory
  MS-PGH-001-01-02: Check existence of registry/odf-ontology/ directory
  MS-PGH-001-01-03: Check existence of shared/qname-registry/ directory (or equivalent)
  MS-PGH-001-01-04: Check existence of registry/odf-ontology/namespace-tree.yaml
  MS-PGH-001-01-05: Check existence of docs/governance/dotnet-library-standard.md
  MS-PGH-001-01-06: Check existence of docs/code-quality/production-library-standard-v2.md
  MS-PGH-001-01-07: Check existence of docs/code-quality/architecture-contract.md
  MS-PGH-001-01-08: Check existence of registry/source-structure-baseline.json
  MS-PGH-001-01-09: Check existence of registry/gate-contract-registry.yaml
  MS-PGH-001-01-10: Check existence of registry/gate11-criteria.yaml
  MS-PGH-001-01-11: Check existence of docs/gates/python-release-gate-definitions.md
  MS-PGH-001-01-12: Check existence of registry/format-registry.yaml
  MS-PGH-001-01-13: Check existence of .governance/capabilities/registry.yaml
  MS-PGH-001-01-14: Record all EXISTS/MISSING results in evidence file
  MS-PGH-001-01-15: For any MISSING paths, find the correct path using Glob/Grep
  MS-PGH-001-01-16: Create registry/governance/ directory (mkdir -p registry/governance)

Acceptance checks:
  - All planned paths verified (EXISTS or corrected to correct path)
  - registry/governance/ directory exists
  - Evidence file written with path results

Evidence required:
  - Written list of all paths + EXISTS/MISSING + corrected paths for any MISSING

Next valid task: TC-PGH-001-02
```

**Micro-step detail for TC-PGH-001-01:**

```
MS-PGH-001-01-01
  Action: Check if oracle/schemas/odf-1.3-relaxng/ exists using Glob
  Target: File: oracle/schemas/odf-1.3-relaxng/
  Allowed: Glob tool only
  Expected output: directory found or not found
  Completion check: result recorded

MS-PGH-001-01-03
  Action: Check shared/qname-registry/ — NOTE: may be at registry/odf-ontology/ or
    a different path. Grep for "qname-registry" in repository first.
  Target: shared/ directory or equivalent
  Allowed: Glob + Grep
  Expected output: actual qname registry path recorded

MS-PGH-001-01-14
  Action: Write evidence file at .local/evidences/pgh-001/path-verification.txt
    Format: one line per path: "EXISTS: registry/format-registry.yaml" or "MISSING: path"
  Allowed: Write tool

MS-PGH-001-01-15
  Action: For each MISSING path, use Glob("**/<filename>") to find actual location.
    Replace planned path with actual path in running notes.
  Completion check: zero MISSING paths remain unresolved

MS-PGH-001-01-16
  Action: Run bash mkdir -p registry/governance
  Completion check: Glob("registry/governance/") returns directory
```

#### TC-PGH-001-02 — Write governance-binding.schema.json

```
Child Taskcard ID: TC-PGH-001-02
Parent Taskcard ID: TC-PGH-001
Title: Write .supervisor/schemas/governance-binding.schema.json
Type: CHILD
Status: TODO

Source:
  Req: REQ-GOV-001
  Analysis: Schema must precede YAML so YAML can be validated against it.

Purpose:
  Provide a JSON Schema that validates governance-binding.yaml structure.

Scope:
  Allowed files: .supervisor/schemas/governance-binding.schema.json (CREATE)
  Forbidden: all other files

Inputs:
  - Read one existing schema (e.g., .supervisor/schemas/gate-definition.schema.json)
    to understand style conventions ($schema, required, properties pattern)

Expected output:
  - .supervisor/schemas/governance-binding.schema.json

Preconditions: TC-PGH-001-01 CLOSED

Micro-steps:
  MS-PGH-001-02-01: Read .supervisor/schemas/gate-definition.schema.json (style reference)
  MS-PGH-001-02-02: Write governance-binding.schema.json with required fields:
    binding_id (string, required), schema_version (string, required),
    repository (string, required), branch (string, required), head (string, required),
    required_authority_order (object with integer keys 1-8, required),
    product_roots (array of strings, required),
    pipeline_roots (array of strings, required),
    specification_authorities (array, required),
    qname_authorities (array, required),
    aspose_api_authorities (array, required),
    architecture_authorities (array, required),
    code_quality_authorities (array, required),
    release_authorities (array, required),
    promotion_authorities (array, required),
    evidence_roots (array, required)
  MS-PGH-001-02-03: Validate schema JSON is parseable:
    python -c "import json; json.load(open('.supervisor/schemas/governance-binding.schema.json'))"
  MS-PGH-001-02-04: Record validation result in evidence

Acceptance checks:
  - File exists
  - json.load() exits 0
  - All required fields present in schema

Evidence required: Schema file path + validation exit code
Next valid task: TC-PGH-001-03
```

#### TC-PGH-001-03 — Write governance-binding.yaml

```
Child Taskcard ID: TC-PGH-001-03
Parent Taskcard ID: TC-PGH-001
Title: Write registry/governance/governance-binding.yaml using verified paths
Type: CHILD
Status: TODO

Source:
  Req: REQ-GOV-001
  Analysis: Use path results from TC-PGH-001-01 and schema from TC-PGH-001-02.

Scope:
  Allowed files: registry/governance/governance-binding.yaml (CREATE)
  Forbidden: all other files

Inputs:
  - TC-PGH-001-01 evidence (verified paths)
  - TC-PGH-001-02 output (schema)
  - Current git HEAD: run `git rev-parse HEAD` to get SHA

Preconditions: TC-PGH-001-01 CLOSED, TC-PGH-001-02 CLOSED

Micro-steps:
  MS-PGH-001-03-01: Run Bash git rev-parse HEAD → record SHA as <HEAD>
  MS-PGH-001-03-02: Write registry/governance/governance-binding.yaml using the
    YAML structure defined in §1 of this plan, substituting verified paths from
    TC-PGH-001-01 evidence for any paths that were corrected.
  MS-PGH-001-03-03: Validate YAML parses:
    python -c "import yaml; yaml.safe_load(open('registry/governance/governance-binding.yaml'))"
  MS-PGH-001-03-04: Validate YAML against schema using jsonschema:
    python -c "
    import json, yaml, jsonschema
    schema = json.load(open('.supervisor/schemas/governance-binding.schema.json'))
    data = yaml.safe_load(open('registry/governance/governance-binding.yaml'))
    jsonschema.validate(data, schema)
    print('VALID')
    "
  MS-PGH-001-03-05: Verify all path values in YAML resolve to existing files:
    Run Glob/Read check for each path value in the YAML
  MS-PGH-001-03-06: Record validation result and path-resolution results in evidence

Acceptance checks:
  - YAML parses cleanly
  - jsonschema.validate passes
  - All path values resolve to existing files
  - required_authority_order has exactly 8 entries (keys 1–8)

Evidence required:
  - YAML validation output
  - Schema validation output (VALID)
  - Path resolution log (all EXISTS)

Rollback: Delete registry/governance/governance-binding.yaml
Next valid task: TC-PGH-002-01 (parent complete, move to next parent)
```

---

### TC-PGH-002 — Governance Control Inventory

```
Parent Taskcard ID: TC-PGH-002
Title: Create governance-control-inventory.yaml covering all 16 lifecycle stages
Type: PARENT
Status: PROPOSED
Owner: governance_lane

Source:
  Req: REQ-GOV-002
  Section: §2
  Analysis: No formal per-stage governance inventory exists. Controls exist in
    scattered form (validators, gate contracts) but no unified document maps
    lifecycle stage → authority → enforcement_point → evidence.
  Root cause: Governance grew incrementally; no architectural inventory was made.
  Selected solution: Create reports/product-governance/governance-control-inventory.yaml
    with one record per lifecycle stage. Create schema first.

Objective:
  Produce governance-control-inventory.yaml covering all 16 lifecycle stages.

Required counters after this TC closes:
  GOVERNANCE_CONTROLS_NOT_INVENTORIED = 0
  LIFECYCLE_STAGES_WITHOUT_GOVERNANCE = 0
  GOVERNANCE_CONTROLS_WITHOUT_AUTHORITY = 0

Scope:
  Allowed files:
    - reports/product-governance/governance-control-inventory.yaml (CREATE)
    - .supervisor/schemas/governance-control.schema.json (CREATE)
  Allowed folders: reports/product-governance/ (CREATE), .supervisor/schemas/

Dependencies: TC-PGH-001 (needs reports/product-governance/ — actually independent,
  both can create their directories; TC-PGH-001 creates registry/governance/,
  this TC creates reports/product-governance/)
  CORRECTION: TC-PGH-002 is INDEPENDENT of TC-PGH-001. Can run in parallel.

Child taskcards:
  - TC-PGH-002-01: Create reports/product-governance/ directory
  - TC-PGH-002-02: Write governance-control.schema.json
  - TC-PGH-002-03: Write governance-control-inventory.yaml (16 entries)
  - TC-PGH-002-04: Verify no stage has authority=null; embed counters in header

Parent acceptance criteria:
  - 16 lifecycle stage entries present
  - Each entry has non-null authority, enforcement_points, and evidence fields
  - All enforcement_point values reference real validators (V-numbers) or registry paths
  - Counters in YAML header all = 0
```

#### TC-PGH-002-01 — Create reports/product-governance/ directory

```
Child Taskcard ID: TC-PGH-002-01
Status: TODO
Micro-steps:
  MS-PGH-002-01-01: Run Bash: mkdir -p reports/product-governance
  MS-PGH-002-01-02: Verify directory exists: Glob("reports/product-governance/")
  MS-PGH-002-01-03: Create placeholder .gitkeep if needed
Acceptance: directory exists
```

#### TC-PGH-002-02 — Write governance-control.schema.json

```
Child Taskcard ID: TC-PGH-002-02
Status: TODO
Preconditions: TC-PGH-002-01 CLOSED
Micro-steps:
  MS-PGH-002-02-01: Read .supervisor/schemas/gate-definition.schema.json (style reference)
  MS-PGH-002-02-02: Write .supervisor/schemas/governance-control.schema.json
    Required fields per record: control_id (string), lifecycle_stage (string enum of 16),
    authority (string, non-null), inputs (array), outputs (array),
    decision_owner (string), enforcement_points (array), evidence (array),
    bypasses (array), known_failures (array), status (enum: ACTIVE|INACTIVE|DRAFT)
  MS-PGH-002-02-03: python -c "import json; json.load(open('.supervisor/schemas/governance-control.schema.json'))" → exit 0
```

#### TC-PGH-002-03 — Write governance-control-inventory.yaml

```
Child Taskcard ID: TC-PGH-002-03
Status: TODO
Preconditions: TC-PGH-002-02 CLOSED
Micro-steps:
  MS-PGH-002-03-01: Read registry/gate-contract-registry.yaml to map existing controls
  MS-PGH-002-03-02: Read tools/supervisor/governance_validator_runner.py imports list
    to map validators to lifecycle stages
  MS-PGH-002-03-03: Write governance-control-inventory.yaml header with counters:
    GOVERNANCE_CONTROLS_NOT_INVENTORIED: 0
    LIFECYCLE_STAGES_WITHOUT_GOVERNANCE: 0
    GOVERNANCE_CONTROLS_WITHOUT_AUTHORITY: 0
  MS-PGH-002-03-04: Write entries for all 16 lifecycle stages:
    new_format_creation, new_capability_addition, public_api_change,
    parser_model_writer_change, file_class_organization, documentation_change,
    bug_fix, refactoring, compatibility_change, dependency_change,
    pipeline_change, code_generator_change, prompt_skill_change,
    package_creation, release_approval, post_release_maintenance
  MS-PGH-002-03-05: Each entry MUST have enforcement_points referencing real validators
    (e.g., [V13, V43, V150] not placeholders)
  MS-PGH-002-03-06: Validate YAML parses cleanly

Acceptance checks:
  - Exactly 16 lifecycle stage entries
  - No authority field is null or empty
  - All enforcement_point values correspond to real validators (cross-check with runner imports)
```

#### TC-PGH-002-04 — Verify counters + final validation

```
Child Taskcard ID: TC-PGH-002-04
Status: TODO
Preconditions: TC-PGH-002-03 CLOSED
Micro-steps:
  MS-PGH-002-04-01: Count entries with authority=null → must be 0
  MS-PGH-002-04-02: Count entries with enforcement_points=[] → must be 0
  MS-PGH-002-04-03: Validate inventory YAML against schema
  MS-PGH-002-04-04: Record counter values in evidence file
```

---

### TC-PGH-003 — Current State Audit + Ledger

```
Parent Taskcard ID: TC-PGH-003
Title: Audit repository for ungoverned changes; produce product-governance-ledger.yaml
Type: PARENT
Status: PROPOSED
Owner: governance_lane

Source:
  Req: REQ-GOV-003
  Section: §16
  Analysis: The §16 audit produces the foundational gap list that drives TC-PGH-015
    backfill and Pilot 9. Must run BEFORE TC-PGH-015 and must find Pilot 9 target.

Objective:
  Audit for 7 categories of governance gaps; produce product-governance-ledger.yaml
  with all findings. Every CRITICAL gap must have task_id assigned.

Special: This TC ALSO determines Pilot 9 target (D3 solution above). After TC-PGH-003
  closes, record the Pilot 9 target in this plan's TC-PGH-017-04 scope section.

Scope:
  Allowed files:
    - reports/product-governance/product-governance-ledger.yaml (CREATE)
    - .supervisor/schemas/governance-gap.schema.json (CREATE)
    All other files READ-ONLY (audit only)

Dependencies: TC-PGH-002-01 (needs reports/product-governance/ directory to exist)

Child taskcards:
  - TC-PGH-003-01: Write governance-gap.schema.json
  - TC-PGH-003-02: Run Python source audit (spec_qname, models.py, __all__)
  - TC-PGH-003-03: Run pipeline + registry audit (skills, format-registry, oracle)
  - TC-PGH-003-04: Write product-governance-ledger.yaml; identify Pilot 9 target
```

#### TC-PGH-003-01 — Write governance-gap.schema.json

```
Child Taskcard ID: TC-PGH-003-01
Status: TODO
Micro-steps:
  MS-PGH-003-01-01: Read .supervisor/schemas/gate-definition.schema.json (style reference)
  MS-PGH-003-01-02: Write .supervisor/schemas/governance-gap.schema.json
    Fields: gap_id (string, required), category (enum of 7 categories, required),
    severity (enum: CRITICAL|HIGH|MEDIUM|LOW, required),
    product_or_pipeline (enum: product|pipeline, required),
    affected_artifacts (array), symptom (string, required),
    evidence (array), first_failed_boundary (string),
    root_cause (string), governance_repair (string),
    proof_required (string), task_ids (array), lane (string),
    status (enum: OPEN|CLOSED|DEFERRED, required), next_action (string)
  MS-PGH-003-01-03: json.load validation → exit 0
```

#### TC-PGH-003-02 — Python source audit

```
Child Taskcard ID: TC-PGH-003-02
Status: TODO
Preconditions: NONE (read-only audit)
Micro-steps:
  MS-PGH-003-02-01: For each of 20 Python formats in src/python/, read models.py
    Check: does every class have spec_qname ClassVar? Record MISSING items.
  MS-PGH-003-02-02: For each format, read __init__.py.
    Check: does every item in __all__ trace to a class with spec_qname?
    Record any public symbols without spec_qname trace.
  MS-PGH-003-02-03: For FODS specifically, read fods/models.py in full.
    NOTE (C15): All 3 primary FODS model classes (FodsDocument, FodsSheet, FodsCell) already
    have spec_qname. ALSO read src/python/fods/spec/ subdirectory for any class without
    spec_qname and not annotated INTENTIONAL_UNMAPPED.
    RECORD the first such class name found anywhere in fods/ — this is the CANDIDATE for
    Pilot 9 target. If no FODS candidate, check fodt/models.py and ods/models.py next.
  MS-PGH-003-02-04: Check 5 .NET format packages in src/net/ — read each
    *Document.cs or main model file. Verify SpecQName constant present.
  MS-PGH-003-02-05: Write evidence file: .local/evidences/pgh-003/python-audit.txt
    Format: one line per finding: "MISSING spec_qname: fods.models.FodsFormula"

Acceptance checks:
  - All 20 Python formats inspected
  - All 5 .NET formats inspected
  - Pilot 9 candidate identified (or "NO_CANDIDATE_FOUND" recorded)
```

#### TC-PGH-003-03 — Pipeline + registry audit

```
Child Taskcard ID: TC-PGH-003-03
Status: TODO
Micro-steps:
  MS-PGH-003-03-01: Read .supervisor/skill-registry.yaml — check that
    change_proposal_required field exists for each skill. Count missing.
  MS-PGH-003-03-02: Read registry/format-registry.yaml — check each format entry
    for presence of release_gates section (pyrel_g1 through pyrel_g5).
    Count formats missing release_gates.
  MS-PGH-003-03-03: Read oracle/ — verify all 20 Python FOSS formats have
    oracle/formats/{format}/oracle-run-summary.json. Count missing.
  MS-PGH-003-03-04: Run git log --oneline -50 — scan for commits that modified
    src/python/ or src/net/ files without a corresponding change proposal record
    (heuristic: no CP- reference in commit message). Record approximate count.
  MS-PGH-003-03-05: Write evidence: .local/evidences/pgh-003/pipeline-audit.txt
```

#### TC-PGH-003-04 — Write product-governance-ledger.yaml

```
Child Taskcard ID: TC-PGH-003-04
Status: TODO
Preconditions: TC-PGH-003-01, TC-PGH-003-02, TC-PGH-003-03 CLOSED
Micro-steps:
  MS-PGH-003-04-01: Compile all findings from TC-PGH-003-02 and TC-PGH-003-03
    evidence files into gap records. Assign gap_ids: GOV-GAP-001, GOV-GAP-002, etc.
  MS-PGH-003-04-02: Classify each gap by category and severity.
    CRITICAL severity rules:
      - missing_qname on released format model class → CRITICAL
      - released_without_traceability → CRITICAL
      - promoted_without_baseline → CRITICAL
    HIGH severity rules:
      - ungoverned_pipeline_component (missing change_proposal_required field) → HIGH
  MS-PGH-003-04-03: For every CRITICAL gap, assign task_ids referencing TC-PGH-015
    or TC-PGH-014 as appropriate.
  MS-PGH-003-04-04: Write reports/product-governance/product-governance-ledger.yaml
    with schema_version header and gap records.
  MS-PGH-003-04-05: RECORD PILOT 9 TARGET: From MS-PGH-003-02-03 result,
    record in this plan under TC-PGH-017-04 scope: "Pilot 9 target: <class name>"
    If NO_CANDIDATE_FOUND: scope = "Add INTENTIONAL_UNMAPPED to fods.models.FodsFormula"
  MS-PGH-003-04-06: Validate YAML parses cleanly
  MS-PGH-003-04-07: Verify all CRITICAL gaps have non-empty task_ids

Acceptance checks:
  - product-governance-ledger.yaml exists with ≥ 1 gap record
  - All CRITICAL gaps have task_ids
  - Pilot 9 target recorded
```

---

### TC-PGH-004 — Governed Artifact Schema + Model

```
Parent Taskcard ID: TC-PGH-004
Title: Create governed-artifact schema and pilot artifact-registry.yaml
Type: PARENT
Status: PROPOSED
Owner: governance_lane

Source:
  Req: REQ-GOV-004
  Section: §3

Objective:
  .supervisor/schemas/governed-artifact.schema.json validates.
  registry/governance/artifact-registry.yaml has 6+ pilot artifact entries
  covering all required artifact_types and lifecycle states.

Scope:
  Allowed files:
    - .supervisor/schemas/governed-artifact.schema.json (CREATE)
    - registry/governance/artifact-registry.yaml (CREATE)

Dependencies: TC-PGH-001 (registry/governance/ directory must exist)

Child taskcards:
  - TC-PGH-004-01: Write governed-artifact.schema.json
  - TC-PGH-004-02: Read FODS source to identify 6 pilot artifact paths/symbols
  - TC-PGH-004-03: Write artifact-registry.yaml with 6 pilot entries
```

#### TC-PGH-004-01 — Write governed-artifact.schema.json

```
Child Taskcard ID: TC-PGH-004-01
Status: TODO
Micro-steps:
  MS-PGH-004-01-01: Read .supervisor/schemas/item-grade.schema.json (style reference)
  MS-PGH-004-01-02: Write .supervisor/schemas/governed-artifact.schema.json
    Required fields: artifact_id, artifact_type (enum of 21 types), product_or_pipeline,
    path_or_symbol, authority_ids (array), version, status (enum of 11 states),
    owner, dependencies (array), consumers (array), proof (array),
    promotion_record, release_records (array), change_history (array)
    Artifact types enum must include ALL 21 from §3:
      specification_fact, qname_mapping, capability, architecture_decision, public_api,
      model_type, parser_component, writer_component, source_file, test,
      documentation_page, example, generated_package, product_release,
      skill, prompt, template, generator, validator, reviewer, certification_rule
    Status enum must include ALL 11 from §3:
      DRAFT, PROPOSED, UNDER_REVIEW, ACCEPTED, REJECTED, PROMOTED,
      RELEASE_ELIGIBLE, RELEASED, REOPENED, DEPRECATED, RETIRED
  MS-PGH-004-01-03: json.load validation → exit 0
```

#### TC-PGH-004-02 — Identify pilot artifact paths

```
Child Taskcard ID: TC-PGH-004-02
Status: TODO
Micro-steps:
  MS-PGH-004-02-01: Read src/python/fods/__init__.py — record __all__ list
  MS-PGH-004-02-02: Read src/python/fods/models.py — record class names
  MS-PGH-004-02-03: Read src/python/fods/parser.py first 30 lines — record main function
  MS-PGH-004-02-04: Verify oracle/formats/fods/oracle-run-summary.json exists
  MS-PGH-004-02-05: Record 6 pilot artifact definitions:
    1. ART-FODS-API-001: public_api, src/python/fods/__init__.py, RELEASED
    2. ART-FODS-MODEL-001: model_type, fods.models.FodsDocument (spec_qname=office:document), RELEASED
    3. ART-FODS-PARSER-001: parser_component, src/python/fods/parser.py, RELEASED (exports parse_fods)
    4. ART-FODS-WRITER-001: writer_component, src/python/fods/writer.py, RELEASED (exports write_fods)
    5. ART-FODS-TEST-001: test, tests/python/fods/ (directory), RELEASED
    6. ART-FODS-SKILL-001: skill, .claude/commands/add-python-api.md, PROMOTED
```

#### TC-PGH-004-03 — Write artifact-registry.yaml

```
Child Taskcard ID: TC-PGH-004-03
Status: TODO
Preconditions: TC-PGH-004-01 CLOSED, TC-PGH-004-02 CLOSED
Micro-steps:
  MS-PGH-004-03-01: Write registry/governance/artifact-registry.yaml
    with schema_version header and 6 pilot entries from TC-PGH-004-02
  MS-PGH-004-03-02: Each entry must have valid status, artifact_type from schema enum
  MS-PGH-004-03-03: Validate YAML parses: python -c "import yaml; ..."
  MS-PGH-004-03-04: Validate 6 entries present; all path_or_symbol values non-empty
```

---

### TC-PGH-005 — Change Proposal Schema + Manager

```
Parent Taskcard ID: TC-PGH-005
Title: Change proposal schema + manager CLI + 2 pilot proposals
Type: PARENT
Status: PROPOSED
Owner: governance_lane

Source:
  Req: REQ-GOV-005
  Section: §4

Objective:
  - .supervisor/schemas/change-proposal.schema.json validates
  - tools/governance/change_proposal_manager.py CLI runs: init, validate, list, check-required
  - registry/governance/change-proposals/CP-PGH-PILOT-001.yaml (accepted — Pilot 1)
  - registry/governance/change-proposals/CP-PGH-PILOT-002.yaml (rejected — Pilot 2)

Scope:
  Allowed files:
    - .supervisor/schemas/change-proposal.schema.json (CREATE)
    - tools/governance/change_proposal_manager.py (CREATE — new file in existing tools/governance/)
    - registry/governance/change-proposals/ (CREATE directory)
    - registry/governance/change-proposals/CP-PGH-PILOT-001.yaml (CREATE)
    - registry/governance/change-proposals/CP-PGH-PILOT-002.yaml (CREATE)

Dependencies: TC-PGH-001 (registry/governance/ directory)

Child taskcards:
  - TC-PGH-005-01: Write change-proposal.schema.json
  - TC-PGH-005-02: Write change_proposal_manager.py with 4 CLI commands
  - TC-PGH-005-03: Write CP-PGH-PILOT-001.yaml (API add — status: SUBMITTED)
  - TC-PGH-005-04: Write CP-PGH-PILOT-002.yaml (root-level cell method — status: SUBMITTED)
```

#### TC-PGH-005-01 — Write change-proposal.schema.json

```
Child Taskcard ID: TC-PGH-005-01
Status: TODO
Micro-steps:
  MS-PGH-005-01-01: Read .supervisor/schemas/governance-contract.schema.json (style ref)
  MS-PGH-005-01-02: Write .supervisor/schemas/change-proposal.schema.json
    Required fields: change_id, title, artifact_ids (array), product_or_pipeline,
    reason, authority, specification_facts (array), qnames (array),
    capabilities (array), architecture_decisions (array), current_behavior,
    proposed_behavior, affected_files (array), affected_types (array),
    affected_public_apis (array), affected_products (array),
    compatibility_impact (enum: NONE|PATCH|MINOR|MAJOR),
    documentation_impact, release_impact, risks (array),
    required_tests (array), required_evidence (array),
    lane, owner, status (enum: DRAFT|SUBMITTED|ACCEPTED|REJECTED|WITHDRAWN)
  MS-PGH-005-01-03: json.load validation → exit 0
```

#### TC-PGH-005-02 — Write change_proposal_manager.py

```
Child Taskcard ID: TC-PGH-005-02
Status: TODO
Preconditions: TC-PGH-005-01 CLOSED
Micro-steps:
  MS-PGH-005-02-01: Read tools/governance/check_docs_placement.py (style reference
    for existing tools/governance/ tools — understand CLI pattern used)
  MS-PGH-005-02-02: Write tools/governance/change_proposal_manager.py with argparse CLI:
    Subcommands:
      init --type <type> --format <format>  → scaffold proposal YAML
      validate <proposal-yaml>              → schema validation
      list [--status <status>]              → list proposals in registry/governance/change-proposals/
      check-required <source-file>          → check if file has governing proposal_id in
                                             registry/governance/file-ownership.yaml
    Import: yaml, json, argparse, pathlib, jsonschema (optional)
    REPO_ROOT detection: Path(__file__).resolve().parent.parent.parent
  MS-PGH-005-02-03: Run python tools/governance/change_proposal_manager.py --help → exit 0
  MS-PGH-005-02-04: Run python tools/governance/change_proposal_manager.py list → exit 0
    (empty list is acceptable before proposals exist)
  MS-PGH-005-02-05: Record --help output in evidence

Acceptance checks:
  - Tool runs without ImportError
  - --help exits 0
  - list exits 0
```

#### TC-PGH-005-03 — Write CP-PGH-PILOT-001.yaml (Pilot 1 proposal)

```
Child Taskcard ID: TC-PGH-005-03
Status: TODO
Preconditions: TC-PGH-005-01 CLOSED (schema available for validation)
Micro-steps:
  MS-PGH-005-03-01: Create directory registry/governance/change-proposals/
  MS-PGH-005-03-02: Write CP-PGH-PILOT-001.yaml:
    change_id: CP-PGH-PILOT-001
    title: "Add get_worksheet_names() to FODS public API"
    artifact_ids: [ART-FODS-API-001]
    product_or_pipeline: product
    reason: "Demonstrate product API change governance lifecycle (Pilot 1)"
    authority: "qname-registry"
    specification_facts: [FACT-FODS-001]  # ODF table:table element
    qnames: ["table:table"]
    current_behavior: "No get_worksheet_names() method on FodsDocument"
    proposed_behavior: "FodsDocument.get_worksheet_names() returns list[str]"
    affected_files: ["src/python/fods/__init__.py", "src/python/fods/models.py"]
    affected_public_apis: ["FodsDocument.get_worksheet_names"]
    affected_products: [fods]
    compatibility_impact: PATCH
    status: SUBMITTED
  MS-PGH-005-03-03: Run python tools/governance/change_proposal_manager.py validate
    registry/governance/change-proposals/CP-PGH-PILOT-001.yaml → exit 0 or record result
```

#### TC-PGH-005-04 — Write CP-PGH-PILOT-002.yaml (Pilot 2 rejected proposal)

```
Child Taskcard ID: TC-PGH-005-04
Status: TODO
Micro-steps:
  MS-PGH-005-04-01: Write CP-PGH-PILOT-002.yaml:
    change_id: CP-PGH-PILOT-002
    title: "Add root-level get_cell_value() to FodsDocument (REJECTED)"
    current_behavior: "Cell access via spreadsheet.sheets[0].cells[row][col]"
    proposed_behavior: "FodsDocument.get_cell_value(sheet, row, col) root-level shortcut"
    compatibility_impact: MINOR
    status: SUBMITTED
    NOTE: This proposal will receive decision REJECT in TC-PGH-006-04
  MS-PGH-005-04-02: Validate with manager tool
```

---

### TC-PGH-006 — Impact Analysis + Decision Schemas

```
Parent Taskcard ID: TC-PGH-006
Title: Impact analysis + decision schemas + pilot impact and decision records
Type: PARENT
Status: PROPOSED
Owner: governance_lane

Source:
  Req: REQ-GOV-006, REQ-GOV-007
  Sections: §5, §10

Objective:
  - .supervisor/schemas/change-impact.schema.json validates
  - .supervisor/schemas/change-decision.schema.json validates
  - tools/governance/impact_analyzer.py runs
  - CI-PGH-PILOT-001.yaml (impact for Pilot 1 proposal)
  - CD-PGH-PILOT-001.yaml (ACCEPT decision for Pilot 1)
  - CD-PGH-PILOT-002.yaml (REJECT decision for Pilot 2)

Dependencies: TC-PGH-005 (proposals must exist before decisions)

Child taskcards:
  - TC-PGH-006-01: Write change-impact.schema.json
  - TC-PGH-006-02: Write change-decision.schema.json
  - TC-PGH-006-03: Write impact_analyzer.py CLI
  - TC-PGH-006-04: Write pilot impact + decision YAML records
```

#### TC-PGH-006-01 — Write change-impact.schema.json

```
Child Taskcard ID: TC-PGH-006-01
Status: TODO
Micro-steps:
  MS-PGH-006-01-01: Write .supervisor/schemas/change-impact.schema.json
    Fields: change_id (string, required), direct_artifacts (array),
    transitive_artifacts (array), affected_qnames (array),
    affected_capabilities (array), affected_public_contracts (array),
    affected_products (array), affected_pipeline_components (array),
    compatibility_class (enum: NONE|PATCH|MINOR|MAJOR, required),
    versioning_class (string), promotion_reopenings (array),
    required_migrations (array), proof_scope (array), release_blockers (array)
  MS-PGH-006-01-02: json.load validation → exit 0
```

#### TC-PGH-006-02 — Write change-decision.schema.json

```
Child Taskcard ID: TC-PGH-006-02
Status: TODO
Micro-steps:
  MS-PGH-006-02-01: Write .supervisor/schemas/change-decision.schema.json
    Fields: change_id (string, required), reviewers (array),
    architecture_verdict, qname_verdict, api_verdict, code_quality_verdict,
    compatibility_verdict, documentation_verdict, proof_verdict,
    pipeline_impact_verdict, release_verdict (each: enum PASS|FAIL|DEFERRED|NA),
    final_decision (enum: ACCEPT|ACCEPT_WITH_REWORK_BEFORE_RELEASE|REJECT|
                         DEFER_WITH_AUTHORITY|BLOCKED_TRUE_EXTERNAL, required),
    rejection_reasons (array), required_rework (array), evidence (array)
  MS-PGH-006-02-02: json.load validation → exit 0
```

#### TC-PGH-006-03 — Write impact_analyzer.py

```
Child Taskcard ID: TC-PGH-006-03
Status: TODO
Preconditions: TC-PGH-006-01 CLOSED
Micro-steps:
  MS-PGH-006-03-01: Write tools/governance/impact_analyzer.py with CLI:
    Subcommands:
      analyze --proposal <yaml-path>       → read proposal, scaffold impact analysis YAML
      check-completeness <impact-yaml>     → verify all required fields populated
    Logic for analyze:
      - Read proposal YAML
      - Extract affected_files, affected_types, affected_public_apis
      - Populate direct_artifacts from artifact_ids in proposal
      - Set compatibility_class from compatibility_impact in proposal
      - Write output to registry/governance/change-impacts/CI-{change_id}.yaml
  MS-PGH-006-03-02: python tools/governance/impact_analyzer.py --help → exit 0
```

#### TC-PGH-006-04 — Write pilot impact + decision records

```
Child Taskcard ID: TC-PGH-006-04
Status: TODO
Preconditions: TC-PGH-006-03 CLOSED, TC-PGH-005-03 CLOSED
Micro-steps:
  MS-PGH-006-04-01: Create directory registry/governance/change-impacts/
  MS-PGH-006-04-02: Run impact_analyzer.py analyze --proposal
    registry/governance/change-proposals/CP-PGH-PILOT-001.yaml
    → creates CI-PGH-PILOT-001.yaml
  MS-PGH-006-04-03: Create directory registry/governance/change-decisions/
  MS-PGH-006-04-04: Write CD-PGH-PILOT-001.yaml:
    change_id: CP-PGH-PILOT-001
    architecture_verdict: PASS  # method follows spec hierarchy
    qname_verdict: PASS         # maps to table:table
    api_verdict: PASS           # consistent with existing FodsDocument API
    compatibility_verdict: PASS # PATCH change
    final_decision: ACCEPT
    evidence: [registry/governance/change-impacts/CI-PGH-PILOT-001.yaml]
  MS-PGH-006-04-05: Write CD-PGH-PILOT-002.yaml:
    change_id: CP-PGH-PILOT-002
    architecture_verdict: FAIL  # violates §6: root-level method for nested concept
    qname_verdict: FAIL         # no spec QName for a shortcut accessor
    api_verdict: FAIL           # inconsistent with navigable object model
    final_decision: REJECT
    rejection_reasons:
      - "Violates §6: root-level methods for nested concepts are prohibited"
      - "No specification QName authorizes get_cell_value at spreadsheet level"
      - "Cell access belongs to the cell hierarchy, not the root document"
    evidence: [registry/governance/change-proposals/CP-PGH-PILOT-002.yaml]
  MS-PGH-006-04-06: Validate both decision YAMLs parse cleanly
```

---

### TC-PGH-007 — Promotion + Release Candidate Schemas + Tools

```
Parent Taskcard ID: TC-PGH-007
Title: Promotion + RC schemas + tools + pilot records + release eligibility report
Type: PARENT
Status: PROPOSED
Owner: governance_lane

Source:
  Req: REQ-GOV-008, REQ-GOV-009
  Sections: §11, §13
  NOTE: TC-PGH-013 is FOLDED INTO this taskcard as child TC-PGH-007-04.

Objective:
  - promotion-record.schema.json + release-candidate.schema.json validate
  - promotion_manager.py + release_eligibility_checker.py run
  - PROM-FODS-001.yaml + RC-FODS-PYREL-001.yaml exist
  - reports/product-governance/release-eligibility-report.yaml generated

Dependencies: TC-PGH-006 (decision records needed for promotion references)

Child taskcards:
  - TC-PGH-007-01: Write promotion-record.schema.json
  - TC-PGH-007-02: Write release-candidate.schema.json
  - TC-PGH-007-03: Write promotion_manager.py + release_eligibility_checker.py
  - TC-PGH-007-04: Write pilot PROM-FODS-001.yaml + RC-FODS-PYREL-001.yaml
                   + run eligibility checker to produce report
```

#### TC-PGH-007-01 — Write promotion-record.schema.json

```
Child Taskcard ID: TC-PGH-007-01
Status: TODO
Micro-steps:
  MS-PGH-007-01-01: Write .supervisor/schemas/promotion-record.schema.json
    Fields: promotion_id (required), change_ids (array, required), product_or_pipeline,
    source_revision (string, required), architecture_revision, qname_revision,
    capability_revision, public_api_baseline (object),
    promoted_files (array, required), promoted_types (array),
    proof_bundle (string), documentation_bundle (string),
    compatibility_class (enum: PATCH|MINOR|MAJOR|PREVIEW, required),
    release_eligibility (enum: ELIGIBLE|NOT_ELIGIBLE|BLOCKED, required),
    promotion_level (enum of 6 levels, required),
    promotion_hash (string, required),
    reopening_conditions (array)
  MS-PGH-007-01-02: json.load → exit 0
```

#### TC-PGH-007-02 — Write release-candidate.schema.json

```
Child Taskcard ID: TC-PGH-007-02
Status: TODO
Micro-steps:
  MS-PGH-007-02-01: Write .supervisor/schemas/release-candidate.schema.json
    Fields: release_id (required), product (required), version (required),
    included_change_ids (array), excluded_change_ids (array),
    source_revision, package_revision, public_api_diff (object),
    compatibility_class (enum: PATCH|MINOR|MAJOR|PREVIEW|NOT_RELEASEABLE),
    migration_required (boolean), tests (array), consumer_proof (array),
    documentation (array), release_notes, known_limitations (array),
    open_risks (array), certification, reproducibility_proof,
    final_decision (enum: ACCEPT|REJECT|PENDING, required)
  MS-PGH-007-02-02: json.load → exit 0
```

#### TC-PGH-007-03 — Write promotion_manager.py + release_eligibility_checker.py

```
Child Taskcard ID: TC-PGH-007-03
Status: TODO
Preconditions: TC-PGH-007-01, TC-PGH-007-02 CLOSED
Micro-steps:
  MS-PGH-007-03-01: Write tools/governance/promotion_manager.py with CLI:
    Subcommands:
      promote --format <fmt> --change-ids <id1,id2>  → scaffold PROM-{FMT}-NNN.yaml
      baseline --promotion-id <id>                    → compute promotion_hash from promoted_files
      status --promotion-id <id>                      → print current status
      check-reopening --promotion-id <id>             → check if promoted files changed at HEAD
  MS-PGH-007-03-02: python tools/governance/promotion_manager.py --help → exit 0
  MS-PGH-007-03-03: Write tools/governance/release_eligibility_checker.py with CLI:
    Subcommands:
      check <format>   → check one RC YAML in registry/governance/release-candidates/
      report           → check all RC YAMLs, output release-eligibility-report.yaml
    Checks performed (§13 rejection conditions):
      1. All included_change_ids have ACCEPT decision in change-decisions/
      2. proof_bundle path exists in .local/supervisor/reviews/ or .local/evidences/
      3. documentation references exist
      4. compatibility_class is not null
      5. If migration_required=true, release_notes contains migration guidance
  MS-PGH-007-03-04: python tools/governance/release_eligibility_checker.py --help → exit 0
```

#### TC-PGH-007-04 — Write pilot records + run eligibility report

```
Child Taskcard ID: TC-PGH-007-04
Status: TODO
Preconditions: TC-PGH-007-03 CLOSED, TC-PGH-006-04 CLOSED (CD-PILOT-001 must be ACCEPT)
Micro-steps:
  MS-PGH-007-04-01: Run git rev-parse HEAD → record <SHA>
  MS-PGH-007-04-02: Read src/python/fods/__init__.py → record __all__ contents as baseline
  MS-PGH-007-04-03: Create registry/governance/promotions/ directory
  MS-PGH-007-04-04: Write registry/governance/promotions/PROM-FODS-001.yaml:
    promotion_id: PROM-FODS-001
    change_ids: [CP-PGH-PILOT-001]
    product_or_pipeline: product
    source_revision: <SHA from MS-PGH-007-04-01>
    public_api_baseline: {__all__: <from MS-PGH-007-04-02>}
    promoted_files: [src/python/fods/__init__.py, src/python/fods/models.py,
                    src/python/fods/parser.py, src/python/fods/writer.py]
    promoted_types: [FodsDocument]
    compatibility_class: PATCH
    release_eligibility: ELIGIBLE
    promotion_level: PROMOTED_STABLE
    promotion_hash: <compute sha256 of promoted_files content list>
  MS-PGH-007-04-05: Create registry/governance/release-candidates/ directory
  MS-PGH-007-04-06: Write registry/governance/release-candidates/RC-FODS-PYREL-001.yaml:
    release_id: RC-FODS-PYREL-001
    product: fods
    version: "0.1.0"
    included_change_ids: [CP-PGH-PILOT-001]
    source_revision: <SHA>
    compatibility_class: PATCH
    migration_required: false
    final_decision: PENDING
  MS-PGH-007-04-07: Run release_eligibility_checker.py report
    → verify report written to reports/product-governance/release-eligibility-report.yaml
  MS-PGH-007-04-08: Read release-eligibility-report.yaml → verify RC-FODS-PYREL-001 has verdict
```

---

### TC-PGH-008 — Product Architecture Traceability Chain

```
Parent Taskcard ID: TC-PGH-008
Title: Traceability chain builder + validators V150–V152 in new module
Type: PARENT
Status: PROPOSED
Owner: governance_lane

CRITICAL CORRECTION (C1): New validator module path is
  tools/supervisor/governance_validators_product_gov.py
  NOT tools/governance/governance_validators_product_gov.py
  Reason: governance_validator_runner.py imports from tools/supervisor/ via lazy
  imports inside run_all_governance_validators(). The runner cannot find modules
  in tools/governance/ without sys.path changes.

Source:
  Req: REQ-GOV-010
  Section: §6

Objective:
  - tools/governance/traceability_chain_builder.py runs for FODS
  - tools/supervisor/governance_validators_product_gov.py created with V150–V152
  - reports/product-governance/traceability-graph.yaml generated for FODS

Scope:
  Allowed files:
    - tools/governance/traceability_chain_builder.py (CREATE NEW)
    - tools/supervisor/governance_validators_product_gov.py (CREATE NEW — V150–V152 only)
    - reports/product-governance/traceability-graph.yaml (CREATE — generated output)
  Forbidden: tools/supervisor/governance_validator_runner.py (updated in TC-PGH-014)

Dependencies: TC-PGH-004 (artifact-registry.yaml for cross-reference)

Child taskcards:
  - TC-PGH-008-01: Read FODS source tree to understand traceability chain data
  - TC-PGH-008-02: Write traceability_chain_builder.py
  - TC-PGH-008-03: Run builder for FODS → produce traceability-graph.yaml
  - TC-PGH-008-04: Write governance_validators_product_gov.py with V150–V152
```

#### TC-PGH-008-01 — Read FODS source for traceability data

```
Child Taskcard ID: TC-PGH-008-01
Status: TODO
Micro-steps:
  MS-PGH-008-01-01: Read src/python/fods/__init__.py — record every item in __all__
  MS-PGH-008-01-02: Read src/python/fods/models.py — record each class + spec_qname value
  MS-PGH-008-01-03: Read src/python/fods/parser.py first 50 lines — record main function name
  MS-PGH-008-01-04: Glob tests/python/fods/test_*.py — record test file names
  MS-PGH-008-01-05: Verify oracle/formats/fods/fods-valid-001.yaml exists (or find actual name)
  MS-PGH-008-01-06: Read shared/qname-registry/fods.yaml (or equivalent) to map symbol→qname
  MS-PGH-008-01-07: Record one complete chain:
    symbol → canonical_type → qname → spec_fact → parser_fn → writer_fn → test → evidence
    for the primary FODS class (FodsDocument or equivalent)
```

#### TC-PGH-008-02 — Write traceability_chain_builder.py

```
Child Taskcard ID: TC-PGH-008-02
Status: TODO
Preconditions: TC-PGH-008-01 CLOSED
Micro-steps:
  MS-PGH-008-02-01: Write tools/governance/traceability_chain_builder.py with CLI:
    Subcommands:
      build --format <fmt>   → produce reports/product-governance/traceability-graph.yaml
      check-chain <symbol>   → check traceability status for one symbol
    Logic for build:
      1. Read src/python/{fmt}/__init__.py → extract __all__
      2. For each symbol in __all__, trace to class in models.py
      3. For each class, get spec_qname ClassVar value
      4. Match spec_qname to shared/qname-registry/{fmt}.yaml (if exists)
      5. Record parser function (grep for "def parse_" in parser.py — for FODS this is parse_fods)
      6. Record writer function (grep for "def write_" in writer.py — for FODS this is write_fods)
         NOTE: Some formats may use {fmt}_parser.py naming; FODS uses parser.py. Check per format.
      7. Record test file (Glob tests/python/{fmt}/test_*.py)
      8. Record oracle evidence (oracle/formats/{fmt}/oracle-run-summary.json)
      9. Determine chain_status: COMPLETE if all 8 slots filled; PARTIAL if ≥5; BROKEN if <5
    Output YAML structure per chain entry as defined in §6 of this plan
  MS-PGH-008-02-02: python tools/governance/traceability_chain_builder.py --help → exit 0
```

#### TC-PGH-008-03 — Run builder for FODS

```
Child Taskcard ID: TC-PGH-008-03
Status: TODO
Preconditions: TC-PGH-008-02 CLOSED, TC-PGH-002-01 CLOSED (reports/product-governance/ exists)
Micro-steps:
  MS-PGH-008-03-01: python tools/governance/traceability_chain_builder.py build --format fods
  MS-PGH-008-03-02: Verify reports/product-governance/traceability-graph.yaml was created
  MS-PGH-008-03-03: Read traceability-graph.yaml → verify ≥1 chain entry with chain_status
  MS-PGH-008-03-04: Count entries with chain_status=BROKEN → record as
    RELEASED_SYMBOLS_WITHOUT_TRACEABILITY counter value
  MS-PGH-008-03-05: Run builder for FODT and CSV as well (3 pilot formats per §9)
```

#### TC-PGH-008-04 — Write governance_validators_product_gov.py (V150–V152)

```
Child Taskcard ID: TC-PGH-008-04
Status: TODO
Preconditions: TC-PGH-008-03 CLOSED (traceability-graph.yaml exists for validation)
Scope: tools/supervisor/governance_validators_product_gov.py (CREATE NEW)

Micro-steps:
  MS-PGH-008-04-01: Read tools/supervisor/governance_validators_ext4.py lines 1-80
    (style reference — understand function signature, return dict, validator_id field)
  MS-PGH-008-04-02: Write tools/supervisor/governance_validators_product_gov.py skeleton:
    - Module docstring: "Product governance validators V150-V163"
    - Import: from pathlib import Path; import yaml, json
    - REPO_ROOT = Path(__file__).resolve().parent.parent.parent
    - All 14 validator stubs (V150-V163) returning {validator_id, result: "WARN", ...}
  MS-PGH-008-04-03: Implement V150 validate_public_api_has_qname_authority:
    - Read {format}/__init__.py __all__ for each format declared RELEASED in artifact-registry.yaml
    - For each symbol, check if it appears in traceability-graph.yaml with non-empty qname
    - Return FAIL if any RELEASED format has __all__ symbol with no qname trace
    - blocks_sprint: False (WARN for now — not enough pilot data to block)
  MS-PGH-008-04-04: Implement V151 validate_no_speculative_public_api:
    - Grep src/python/*/__init__.py for "# SPECULATIVE" or "# TODO: implement"
    - Return FAIL if found in __all__ export section
    - blocks_sprint: False
  MS-PGH-008-04-05: Implement V152 validate_canonical_type_has_parser_path:
    - For each format in artifact-registry.yaml at RELEASED status,
      read models.py, check each class has either spec_qname or INTENTIONAL_UNMAPPED
    - Return WARN for missing; FAIL if ≥3 classes in one format are missing both
    - blocks_sprint: False
  MS-PGH-008-04-06: python -c "import sys; sys.path.insert(0, 'tools/supervisor');
    from governance_validators_product_gov import validate_public_api_has_qname_authority"
    → exit 0 (import test)
  MS-PGH-008-04-07: Record import test result in evidence
```

---

### TC-PGH-009 — Pipeline Governance Enforcement

```
Parent Taskcard ID: TC-PGH-009
Title: Pipeline change governor + V153–V155 added to governance_validators_product_gov.py
Type: PARENT
Status: PROPOSED

Source:
  Req: REQ-GOV-011
  Section: §7

NOTE: Validators V153-V155 are APPENDED to tools/supervisor/governance_validators_product_gov.py
  (created in TC-PGH-008-04). TC-PGH-009 extends that file; cannot run until TC-PGH-008-04 CLOSED.

Objective:
  - tools/governance/pipeline_change_governor.py runs
  - registry/governance/pipeline-components.yaml covers key generator skills
  - V153, V154, V155 appended to governance_validators_product_gov.py

Dependencies: TC-PGH-008-04 CLOSED (governance_validators_product_gov.py must exist)

Child taskcards:
  - TC-PGH-009-01: Write pipeline_change_governor.py + pipeline-components.yaml
  - TC-PGH-009-02: Write registry/governance/file-ownership.yaml skeleton
  - TC-PGH-009-03: Append V153–V155 to governance_validators_product_gov.py
```

#### TC-PGH-009-01 — Pipeline change governor + components registry

```
Child Taskcard ID: TC-PGH-009-01
Status: TODO
Micro-steps:
  MS-PGH-009-01-01: Glob .claude/commands/*.md → list all skill command files
    Record count and names of generator/deepening skills
  MS-PGH-009-01-02: Write registry/governance/pipeline-components.yaml:
    List 15 key pipeline components:
    - .claude/commands/add-python-api.md (skill)
    - .claude/commands/add-dotnet-api.md (skill)
    - tools/supervisor/autonomous_cycle.py (generator)
    - tools/supervisor/governance_validator_runner.py (validator)
    - tools/supervisor/sprint_executor.py (generator)
    - tools/governance/traceability_chain_builder.py (generator)
    - tools/governance/change_proposal_manager.py (governance tool)
    - tools/governance/impact_analyzer.py (governance tool)
    - tools/governance/promotion_manager.py (governance tool)
    - tools/governance/release_eligibility_checker.py (governance tool)
    - tools/governance/reopening_detector.py (governance tool)
    - tools/governance/pre_write_checklist.py (governance tool)
    - tools/governance/doc_compliance_checker.py (governance tool)
    - tools/governance/maintenance_classifier.py (governance tool)
    - tools/governance/completion_gate_checker.py (governance tool)
    Each entry: component_id, path, component_type, governs_products (array or []),
    change_proposal_required (bool), product_pilot_required (bool),
    current_version (HEAD SHA), last_product_pilot (null initially)
  MS-PGH-009-01-03: Write tools/governance/pipeline_change_governor.py with CLI:
    Subcommands:
      pilot --skill <skill-name> --format <fmt> → record that skill was run for format,
        creating pilot evidence entry in registry/governance/pipeline-components.yaml
      check-changed → compare current HEAD vs last recorded versions,
        list pipeline components changed without a change_proposal
      status → print pipeline-components.yaml summary
  MS-PGH-009-01-04: python tools/governance/pipeline_change_governor.py --help → exit 0
```

#### TC-PGH-009-02 — Write file-ownership.yaml skeleton

```
Child Taskcard ID: TC-PGH-009-02
Status: TODO
Micro-steps:
  MS-PGH-009-02-01: Write registry/governance/file-ownership.yaml:
    Schema: file_path → {lane, owner, change_proposal_id, registered_at}
    Initial entries covering FODS source files:
      src/python/fods/__init__.py: {lane: governance, owner: governance_sprint, change_proposal_id: null}
      src/python/fods/models.py: {lane: governance, owner: governance_sprint, change_proposal_id: null}
      src/python/fods/parser.py: {lane: governance, owner: governance_sprint, change_proposal_id: null}
    NOTE: Most files start with change_proposal_id: null (pre-governance)
    This represents the "backfill gap" that the governance system will fix going forward.
  MS-PGH-009-02-02: Validate YAML parses
```

#### TC-PGH-009-03 — Append V153–V155 to governance_validators_product_gov.py

```
Child Taskcard ID: TC-PGH-009-03
Status: TODO
Preconditions: TC-PGH-008-04 CLOSED (file exists), TC-PGH-009-01 CLOSED (pipeline-components.yaml exists)
Micro-steps:
  MS-PGH-009-03-01: Read tools/supervisor/governance_validators_product_gov.py (current state)
  MS-PGH-009-03-02: Append V153 validate_pipeline_change_proposal_required:
    - Read pipeline-components.yaml → get list of change_proposal_required=true components
    - For each such component, check if file appears in declaration changed_files
    - If yes: check if declaration has a change_proposal reference for that file
    - Return WARN if pipeline file changed without proposal reference (not FAIL — pre-governance state)
  MS-PGH-009-03-03: Append V154 validate_pipeline_change_has_product_pilot:
    - For each pipeline component changed in declaration,
      check if last_product_pilot in pipeline-components.yaml was updated in this run
    - Return WARN if no pilot recorded (FAIL would block all current sprints)
  MS-PGH-009-03-04: Append V155 validate_generated_output_matches_promoted:
    - Check if any promotion record has promotion_hash recorded
    - If yes: for promoted_files, compute sha256 of current content, compare to stored hash
    - Return WARN if hash differs (not FAIL yet — baselines not complete)
  MS-PGH-009-03-05: Import test: python -c "from governance_validators_product_gov import
    validate_pipeline_change_proposal_required, validate_pipeline_change_has_product_pilot,
    validate_generated_output_matches_promoted" → exit 0
```

---

### TC-PGH-010 — Code Writing Governance Checklist

```
Parent Taskcard ID: TC-PGH-010
Title: pre_write_checklist.py + V156 appended to governance_validators_product_gov.py
Type: PARENT
Status: PROPOSED

Source:
  Req: REQ-GOV-012
  Section: §8

Dependencies: TC-PGH-008-04 CLOSED, TC-PGH-009-02 CLOSED (file-ownership.yaml)

Child taskcards:
  - TC-PGH-010-01: Write pre_write_checklist.py
  - TC-PGH-010-02: Populate file-ownership.yaml with broader file set
  - TC-PGH-010-03: Append V156 to governance_validators_product_gov.py
```

#### TC-PGH-010-01 — Write pre_write_checklist.py

```
Child Taskcard ID: TC-PGH-010-01
Status: TODO
Micro-steps:
  MS-PGH-010-01-01: Write tools/governance/pre_write_checklist.py with CLI:
    Subcommands:
      check --file <path>   → check: has governing change_proposal_id in file-ownership.yaml?
                              Returns: OK | MISSING_PROPOSAL | NOT_REGISTERED
      register --file <path> --proposal-id <id>  → add/update file in file-ownership.yaml
      list-unregistered → list src/python/ + src/net/ files not in file-ownership.yaml
  MS-PGH-010-01-02: python tools/governance/pre_write_checklist.py --help → exit 0
  MS-PGH-010-01-03: python tools/governance/pre_write_checklist.py check
    --file src/python/fods/parser.py → output NOT_REGISTERED or MISSING_PROPOSAL
    (expected result since file not yet registered with proposal — that's the gap)
  MS-PGH-010-01-04: Record output in evidence
```

#### TC-PGH-010-02 — Populate file-ownership.yaml

```
Child Taskcard ID: TC-PGH-010-02
Status: TODO
Preconditions: TC-PGH-010-01 CLOSED
Micro-steps:
  MS-PGH-010-02-01: Run pre_write_checklist.py list-unregistered → get full list
  MS-PGH-010-02-02: Add entries for all 20 Python format __init__.py files to file-ownership.yaml
    (These are the most-changed files; all start with change_proposal_id: null)
  MS-PGH-010-02-03: Add entries for all .NET format source files (src/net/*)
  MS-PGH-010-02-04: Validate YAML parses
```

#### TC-PGH-010-03 — Append V156 to governance_validators_product_gov.py

```
Child Taskcard ID: TC-PGH-010-03
Status: TODO
Preconditions: TC-PGH-008-04, TC-PGH-009-03 CLOSED (sequential file edits)
Micro-steps:
  MS-PGH-010-03-01: Read governance_validators_product_gov.py (current state after V155)
  MS-PGH-010-03-02: Append V156 validate_material_change_has_proposal:
    - For each PRODUCT_SOURCE work item in declaration with status=completed,
      get changed_files list
    - For each changed file, check file-ownership.yaml for change_proposal_id
    - Return WARN if any changed PRODUCT_SOURCE file has change_proposal_id=null
      (WARN not FAIL — pre-governance state means many files lack proposals)
  MS-PGH-010-03-03: Import test for V156 → exit 0
```

---

### TC-PGH-011 — Documentation + Traceability Graph

```
Parent Taskcard ID: TC-PGH-011
Title: doc_compliance_checker.py + traceability graph for FODS/FODT/CSV + V157–V158
Type: PARENT
Status: PROPOSED

Source:
  Req: REQ-GOV-013
  Section: §9

Dependencies: TC-PGH-008-03 CLOSED (traceability-graph.yaml generated for 3 formats)
              TC-PGH-008-04, TC-PGH-009-03, TC-PGH-010-03 CLOSED (sequential append)

Child taskcards:
  - TC-PGH-011-01: Write doc_compliance_checker.py
  - TC-PGH-011-02: Run doc compliance check for FODS; produce doc-compliance-report.yaml
  - TC-PGH-011-03: Append V157–V158 to governance_validators_product_gov.py
```

#### TC-PGH-011-01 — Write doc_compliance_checker.py

```
Child Taskcard ID: TC-PGH-011-01
Status: TODO
Micro-steps:
  MS-PGH-011-01-01: Write tools/governance/doc_compliance_checker.py with CLI:
    Subcommands:
      check --format <fmt>  → scan {fmt}/ package for docstring issues
      report                → write reports/product-governance/doc-compliance-report.yaml
    Check logic:
      1. Read __init__.py → get __all__ list
      2. For each exported symbol, read its docstring (ast.parse)
      3. Check: does docstring claim "returns X" where X is not in traceability-graph.yaml test?
      4. Check: does docstring say "raises Y" where Y is not in exceptions.py?
      5. Record mismatches as WARN (not error — many are expected before governance)
  MS-PGH-011-01-02: python tools/governance/doc_compliance_checker.py --help → exit 0
```

#### TC-PGH-011-02 — Run doc compliance for FODS

```
Child Taskcard ID: TC-PGH-011-02
Status: TODO
Micro-steps:
  MS-PGH-011-02-01: python tools/governance/doc_compliance_checker.py check --format fods
  MS-PGH-011-02-02: python tools/governance/doc_compliance_checker.py report
    → creates reports/product-governance/doc-compliance-report.yaml
  MS-PGH-011-02-03: Read report → count DOCUMENTATION_CONTRADICTING_RELEASED_BEHAVIOR
  MS-PGH-011-02-04: Record counter value in evidence
```

#### TC-PGH-011-03 — Append V157–V158

```
Child Taskcard ID: TC-PGH-011-03
Status: TODO
Preconditions: TC-PGH-010-03 CLOSED (sequential file edit)
Micro-steps:
  MS-PGH-011-03-01: Read governance_validators_product_gov.py current state
  MS-PGH-011-03-02: Append V157 validate_released_symbols_traceable:
    - Read traceability-graph.yaml
    - For each format at RELEASED status in artifact-registry.yaml,
      check every __all__ symbol appears in graph with chain_status != BROKEN
    - Return WARN with count of BROKEN chains (counter value for completion gate)
  MS-PGH-011-03-03: Append V158 validate_documentation_not_contradictory:
    - Read doc-compliance-report.yaml (if exists; skip if missing — best-effort)
    - Return WARN with count of contradictions found
  MS-PGH-011-03-04: Import test → exit 0
```

---

### TC-PGH-012 — Reopening Detector + Maintenance Classifier

```
Parent Taskcard ID: TC-PGH-012
Title: reopening_detector.py + maintenance_classifier.py + V159–V160
Type: PARENT
Status: PROPOSED

Source:
  Req: REQ-GOV-014, REQ-GOV-015
  Sections: §12, §14

Dependencies: TC-PGH-007-04 CLOSED (PROM-FODS-001.yaml must exist for detector to scan)
              TC-PGH-011-03 CLOSED (sequential append to validator file)

Child taskcards:
  - TC-PGH-012-01: Write reopening_detector.py
  - TC-PGH-012-02: Write maintenance_classifier.py
  - TC-PGH-012-03: Append V159–V160 to governance_validators_product_gov.py
```

#### TC-PGH-012-01 — Write reopening_detector.py

```
Child Taskcard ID: TC-PGH-012-01
Status: TODO
Micro-steps:
  MS-PGH-012-01-01: Write tools/governance/reopening_detector.py with CLI:
    Subcommands:
      scan --base-promotion <prom-id>  → compare HEAD vs promotion baseline
      check --declaration <yaml>       → check which promotions need reopening
    Logic for scan:
      1. Read registry/governance/promotions/{prom-id}.yaml
      2. Get promoted_files list + promotion_hash
      3. For each promoted file, compute sha256 of current content
      4. If sha256 != stored hash → record reopening_condition triggered
      5. Classify which reopening condition applies:
         - src/python/{fmt}/models.py changed → public_api_change
         - __init__.py changed → public_api_change
         - {fmt}_parser.py changed → parser_writer_behavior_change
         - compatibility_class changed → compatibility_change
      6. Output list of triggered conditions
  MS-PGH-012-01-02: python tools/governance/reopening_detector.py --help → exit 0
  MS-PGH-012-01-03: python tools/governance/reopening_detector.py scan
    --base-promotion PROM-FODS-001 → verify it reads the promotion file without error
  MS-PGH-012-01-04: Record output in evidence (may show no conditions if files unchanged)
```

#### TC-PGH-012-02 — Write maintenance_classifier.py

```
Child Taskcard ID: TC-PGH-012-02
Status: TODO
Micro-steps:
  MS-PGH-012-02-01: Write tools/governance/maintenance_classifier.py with CLI:
    Subcommands:
      classify --proposal <yaml>  → determine maintenance_class from proposal fields
      list-classes               → print all 10 valid maintenance classes
    Classification rules:
      - status=bug → defect_fix
      - reason contains "spec" → specification_alignment
      - compatibility_impact=MAJOR → compatibility_fix
      - reason contains "refactor" → refactoring
      - reason contains "performance" → performance_improvement
      - artifact_type=documentation_page → documentation_correction
      - reason contains "dependency" or "upgrade" → dependency_update
      - reason contains "security" or "cve" → security_fix
      - status=deprecated → deprecation
      - status=retire → retirement
  MS-PGH-012-02-02: python tools/governance/maintenance_classifier.py list-classes → exit 0
```

#### TC-PGH-012-03 — Append V159–V160

```
Child Taskcard ID: TC-PGH-012-03
Status: TODO
Preconditions: TC-PGH-011-03 CLOSED (sequential append)
Micro-steps:
  MS-PGH-012-03-01: Read governance_validators_product_gov.py current state
  MS-PGH-012-03-02: Append V159 validate_no_silent_promoted_change:
    - Read all promotion records in registry/governance/promotions/
    - For each, get promoted_files
    - Cross-reference with declaration changed_files
    - If overlap: check if any changed promoted_file has a governing change_proposal in
      file-ownership.yaml with non-null change_proposal_id
    - Return WARN if promoted file changed without proposal (not FAIL — pre-governance)
  MS-PGH-012-03-03: Append V160 validate_maintenance_change_classified:
    - For each declaration work item with item_type=bug_fix or description containing "refactor",
      check if maintenance_class field is present
    - Return WARN if missing (not FAIL — field doesn't yet exist in schema)
  MS-PGH-012-03-04: Import test → exit 0
```

---

### TC-PGH-014 — Governance Machinery Integration

```
Parent Taskcard ID: TC-PGH-014
Title: Wire all 14 new validators into runner; update expected_count 167→181
Type: PARENT
Status: PROPOSED

CRITICAL CORRECTIONS (C2, C3):
  Current expected_count = 167 (verified at HEAD, not 165 as stated in MEMORY.md).
  After adding 14 validators (V150–V163): new expected_count = 181.

Source:
  Req: REQ-GOV-016
  Section: §17

Dependencies: TC-PGH-008-04, TC-PGH-009-03, TC-PGH-010-03, TC-PGH-011-03, TC-PGH-012-03
  CLOSED (all 14 validators must exist in governance_validators_product_gov.py before
  runner integration — otherwise runner fails on import)

Child taskcards:
  - TC-PGH-014-01: Verify governance_validators_product_gov.py has all 14 validators
  - TC-PGH-014-02: Update .supervisor/skill-registry.yaml (change_proposal_required field)
  - TC-PGH-014-03: Wire new module into governance_validator_runner.py
  - TC-PGH-014-04: Add focused test for new validators
  - TC-PGH-014-05: Update registry/format-registry.yaml (governance_status section)
```

#### TC-PGH-014-01 — Verify all 14 validators present

```
Child Taskcard ID: TC-PGH-014-01
Status: TODO
Micro-steps:
  MS-PGH-014-01-01: Read tools/supervisor/governance_validators_product_gov.py
  MS-PGH-014-01-02: Count function definitions matching "def validate_" → must be exactly 14
  MS-PGH-014-01-03: Verify each V150–V163 function is present:
    validate_public_api_has_qname_authority (V150)
    validate_no_speculative_public_api (V151)
    validate_canonical_type_has_parser_path (V152)
    validate_pipeline_change_proposal_required (V153)
    validate_pipeline_change_has_product_pilot (V154)
    validate_generated_output_matches_promoted (V155)
    validate_material_change_has_proposal (V156)
    validate_released_symbols_traceable (V157)
    validate_documentation_not_contradictory (V158)
    validate_no_silent_promoted_change (V159)
    validate_maintenance_change_classified (V160)
    validate_release_candidate_changes_accepted (V161)
    validate_release_candidate_compatibility_known (V162)
    validate_reopening_conditions_documented (V163)
  MS-PGH-014-01-04: python -c "import sys; sys.path.insert(0, 'tools/supervisor');
    import governance_validators_product_gov as m;
    fns = [f for f in dir(m) if f.startswith('validate_')]
    print(len(fns)); assert len(fns) == 14, f'Expected 14, got {len(fns)}'" → exit 0
  MS-PGH-014-01-05: If count != 14, identify missing validators and return BLOCKED
    with list of missing items (reroute to applicable parent TC)
```

#### TC-PGH-014-02 — Update skill-registry.yaml

```
Child Taskcard ID: TC-PGH-014-02
Status: TODO
Micro-steps:
  MS-PGH-014-02-01: Read .supervisor/skill-registry.yaml first 100 lines
    to understand skill entry structure
  MS-PGH-014-02-02: For each skill entry in skill-registry.yaml that is a
    "material change" skill (add-python-api, add-dotnet-api, add-same-format-writer-feature,
    format-feature-expansion, new-format-kickstart, product-source-task,
    add-dogfood-export, add-roundtrip-test):
    Add field: change_proposal_required: true
  MS-PGH-014-02-03: For governance/planning/acquisition skills:
    Add field: change_proposal_required: false
  MS-PGH-014-02-04: Validate YAML parses: python -c "import yaml; yaml.safe_load(open('.supervisor/skill-registry.yaml'))"
```

#### TC-PGH-014-03 — Wire module into governance_validator_runner.py

```
Child Taskcard ID: TC-PGH-014-03
Status: TODO
Preconditions: TC-PGH-014-01 CLOSED (14 validators confirmed present)

CRITICAL: The runner uses LAZY IMPORTS inside run_all_governance_validators() function.
Do NOT add imports at module level. Follow the existing pattern exactly.

Micro-steps:
  MS-PGH-014-03-01: Read tools/supervisor/governance_validator_runner.py lines 800-850
    to find: (a) the exact current expected_count line, (b) the import pattern
    for the most recently added module (should be near latest V number)
  MS-PGH-014-03-02: Inside run_all_governance_validators() function body,
    after the last validator module import block, add:
      from governance_validators_product_gov import (
          validate_public_api_has_qname_authority,
          validate_no_speculative_public_api,
          validate_canonical_type_has_parser_path,
          validate_pipeline_change_proposal_required,
          validate_pipeline_change_has_product_pilot,
          validate_generated_output_matches_promoted,
          validate_material_change_has_proposal,
          validate_released_symbols_traceable,
          validate_documentation_not_contradictory,
          validate_no_silent_promoted_change,
          validate_maintenance_change_classified,
          validate_release_candidate_changes_accepted,
          validate_release_candidate_compatibility_known,
          validate_reopening_conditions_documented,
      )
  MS-PGH-014-03-03: Add 14 validator calls to the validators list in the function
    (follow the pattern of existing validators — each returns a dict result)
  MS-PGH-014-03-04: Update expected_count from 167 to 181 on the exact line where
    it currently reads: expected_count = 167
  MS-PGH-014-03-05: Run runner with a minimal test declaration to verify it loads:
    python -c "
    import sys; sys.path.insert(0, 'tools/supervisor')
    from governance_validator_runner import run_all_governance_validators
    print('Import OK')
    " → exit 0
```

#### TC-PGH-014-04 — Add focused test for new validators

```
Child Taskcard ID: TC-PGH-014-04
Status: TODO
Preconditions: TC-PGH-014-03 CLOSED
Micro-steps:
  MS-PGH-014-04-01: Read tests/governance/test_capability_parity.py first 30 lines
    to understand test file structure in tests/governance/
  MS-PGH-014-04-02: Write tests/governance/test_product_gov_validators.py:
    - Test that governance_validators_product_gov module imports without error
    - Test that each of the 14 functions returns a dict with keys:
      validator_id, result, summary (minimum required fields)
    - Test V150 with a mock declaration that has no changed_files → returns PASS
    - Test V151 with a mock source string containing "# SPECULATIVE" → returns FAIL/WARN
    - Test that ALL 14 validators return result in {PASS, FAIL, WARN}
  MS-PGH-014-04-03: Run .venv/Scripts/pytest tests/governance/test_product_gov_validators.py -v
    → all tests PASS
  MS-PGH-014-04-04: Record test output in evidence
```

#### TC-PGH-014-05 — Update format-registry.yaml governance_status

```
Child Taskcard ID: TC-PGH-014-05
Status: TODO
Micro-steps:
  MS-PGH-014-05-01: Read registry/format-registry.yaml first 100 lines to understand structure
  MS-PGH-014-05-02: For the fods format entry, add governance_status section:
    governance_status:
      artifact_registry_entry: ART-FODS-API-001
      promotion_record: PROM-FODS-001
      release_candidate: RC-FODS-PYREL-001
      governance_healed: true
      governance_heal_date: "2026-07-10"
  MS-PGH-014-05-03: Add minimal governance_status to the other 3 pilot formats
    (FODT, CSV, TSV): artifact_registry_entry: null, governance_healed: false
  MS-PGH-014-05-04: Validate YAML parses
```

---

### TC-PGH-015 — Artifact Backfill (Products + Pipeline)

```
Parent Taskcard ID: TC-PGH-015
Title: Backfill artifact-registry.yaml with all 20 Python + 5 .NET + 15 pipeline artifacts
Type: PARENT
Status: PROPOSED

Source:
  Req: REQ-GOV-017
  Section: §17
  Analysis: The pilot artifact-registry.yaml from TC-PGH-004 has only 6 entries.
    Full backfill requires ~110 entries covering all governed artifacts.
    To avoid one massive edit, decompose by category.

Dependencies: TC-PGH-004 CLOSED (artifact schema + initial registry exist)
              TC-PGH-003 CLOSED (audit identifies status of each format)

Child taskcards:
  - TC-PGH-015-01: Backfill Python format artifacts (20 formats × 4 key artifacts each)
  - TC-PGH-015-02: Backfill .NET format artifacts (5 formats × 3 artifacts each)
  - TC-PGH-015-03: Backfill pipeline component artifacts (15 components from TC-PGH-009-01)
```

#### TC-PGH-015-01 — Backfill Python format artifacts

```
Child Taskcard ID: TC-PGH-015-01
Status: TODO
Preconditions: TC-PGH-004-03 CLOSED (artifact-registry.yaml exists with 6 pilot entries)

Micro-steps:
  MS-PGH-015-01-01: Read registry/format-registry.yaml → extract all 20 format_ids
    for Python FOSS formats
  MS-PGH-015-01-02: For each of 20 formats, determine status:
    - If oracle/formats/{fmt}/oracle-run-summary.json exists → status: RELEASED
    - Otherwise → status: ACCEPTED
  MS-PGH-015-01-03: Append to registry/governance/artifact-registry.yaml:
    For each format, 4 artifact entries:
    1. ART-{FMT}-API-001: public_api, src/python/{fmt}/__init__.py, <status>
    2. ART-{FMT}-MODEL-001: model_type, src/python/{fmt}/models.py, <status>
    3. ART-{FMT}-PARSER-001: parser_component, src/python/{fmt}/{fmt}_parser.py, <status>
    4. ART-{FMT}-TEST-001: test, tests/python/{fmt}/, <status>
    NOTE: For formats without explicit models.py (check with Glob), use source_file type
  MS-PGH-015-01-04: Validate YAML parses after appending
  MS-PGH-015-01-05: Count entries → must be ≥ 86 (6 pilot + 80 new)

COUNTER computed: UNGOVERNED_PRODUCT_ARTIFACTS (Python portion) = 0 after this step
```

#### TC-PGH-015-02 — Backfill .NET format artifacts

```
Child Taskcard ID: TC-PGH-015-02
Status: TODO
Micro-steps:
  MS-PGH-015-02-01: Glob src/net/*/ → identify .NET format directories
  MS-PGH-015-02-02: For each .NET format (fods, fodt, csv, tsv, netpbm variants):
    Append 3 entries:
    1. ART-{FMT}-NET-MODEL-001: model_type, src/net/{fmt}/Model/, RELEASED
    2. ART-{FMT}-NET-PARSER-001: parser_component, src/net/{fmt}/Parsing/, RELEASED
    3. ART-{FMT}-NET-TEST-001: test, tests/dotnet/{fmt}/, RELEASED
  MS-PGH-015-02-03: Validate YAML parses
```

#### TC-PGH-015-03 — Backfill pipeline artifacts

```
Child Taskcard ID: TC-PGH-015-03
Status: TODO
Micro-steps:
  MS-PGH-015-03-01: For each of 15 pipeline components in pipeline-components.yaml:
    Append artifact entry:
    ART-PIPE-{COMPONENT_ID}: artifact_type = validator|skill|generator|governance tool,
    path_or_symbol = component path, status = PROMOTED (if tested) or ACCEPTED (if not)
  MS-PGH-015-03-02: Validate YAML parses
  MS-PGH-015-03-03: Verify total artifact count ≥ 100
  MS-PGH-015-03-04: Compute UNGOVERNED_PRODUCT_ARTIFACTS:
    = total formats in format-registry - formats in artifact-registry → must = 0
  MS-PGH-015-03-05: Compute UNGOVERNED_PIPELINE_COMPONENTS:
    = total pipeline tools in pipeline-components.yaml - tools in artifact-registry → must = 0
```

---

### TC-PGH-016 — Required Pilots 1–5

```
Parent Taskcard ID: TC-PGH-016
Title: Execute and evidence Pilots 1–5 (API change, rejected change, pipeline change, docs-only, compat-breaking)
Type: PARENT
Status: PROPOSED

Dependencies: ALL Phase B + C taskcards CLOSED (schemas, tools, validators all ready)
              TC-PGH-015 CLOSED (backfill complete)

Child taskcards:
  - TC-PGH-016-01: Pilot 1 — Product API Change
  - TC-PGH-016-02: Pilot 2 — Rejected Change
  - TC-PGH-016-03: Pilot 3 — Pipeline Change with Product Pilot
  - TC-PGH-016-04: Pilot 4 — Documentation-Only Change
  - TC-PGH-016-05: Pilot 5 — Compatibility-Breaking Change Gating
```

#### TC-PGH-016-01 — Pilot 1: Product API Change

```
Child Taskcard ID: TC-PGH-016-01
Status: TODO
Source:
  Req: REQ-GOV-018
  Section: §18.1
  Scope: Add get_worksheet_names() to src/python/fods/__init__.py + fods/models.py

Micro-steps:
  MS-PGH-016-01-01: Verify CP-PGH-PILOT-001.yaml status=SUBMITTED exists
  MS-PGH-016-01-02: Verify CI-PGH-PILOT-001.yaml exists (impact record)
  MS-PGH-016-01-03: Verify CD-PGH-PILOT-001.yaml final_decision=ACCEPT exists
  MS-PGH-016-01-04: Read src/python/fods/models.py to find primary spreadsheet class
  MS-PGH-016-01-05: Add method to FodsDocument class in src/python/fods/models.py:
    def get_worksheet_names(self) -> list[str]:
      """Return names of all worksheets in this spreadsheet document.
      spec_qname: table:table (ODF 1.3 §9.1.2)
      Uses existing self.sheets() method which returns list[FodsSheet].
      FodsSheet.name is a property returning the sheet name string.
      """
      return [s.name for s in self.sheets()]
    NOTE: self.sheets() already exists on FodsDocument (returns list[FodsSheet]).
    FodsSheet.name is already a property. This is a trivial delegation.
  MS-PGH-016-01-06: Verify FodsDocument is exported via src/python/fods/__init__.py
    (uses `from .models import *` — FodsDocument will be in __all__ automatically;
     no explicit __all__ entry needed since __init__.py generates __all__ dynamically)
  MS-PGH-016-01-07: Update CP-PGH-PILOT-001.yaml status: ACCEPTED
  MS-PGH-016-01-08: Run .venv/Scripts/pytest tests/python/fods/ -v -k "worksheet"
    Expected: if test not yet written, 0 collected (acceptable for pre-test pilot).
    If test_fods_domain_models.py or test_fods_primary_api.py covers FodsDocument,
    run those too: .venv/Scripts/pytest tests/python/fods/test_fods_domain_models.py -v → PASS
  MS-PGH-016-01-09: Update PROM-FODS-001.yaml: add CP-PGH-PILOT-001 to change_ids
  MS-PGH-016-01-10: Run traceability_chain_builder.py build --format fods
    → verify get_worksheet_names appears in traceability-graph.yaml

Acceptance:
  - Method exists in models.py
  - __all__ updated
  - CP-PGH-PILOT-001.yaml status=ACCEPTED
  - Traceability chain includes get_worksheet_names symbol
```

#### TC-PGH-016-02 — Pilot 2: Rejected Change

```
Child Taskcard ID: TC-PGH-016-02
Status: TODO
Source:
  Req: REQ-GOV-019
  Section: §18.2
  NOTE: This pilot requires NO code implementation. It proves rejection by governance records only.

Micro-steps:
  MS-PGH-016-02-01: Verify CP-PGH-PILOT-002.yaml exists (status=SUBMITTED)
  MS-PGH-016-02-02: Verify CD-PGH-PILOT-002.yaml final_decision=REJECT with 3+ rejection_reasons
  MS-PGH-016-02-03: Update CP-PGH-PILOT-002.yaml status: REJECTED
  MS-PGH-016-02-04: Verify V150 (or impact_analyzer check) would also detect the violation:
    python tools/governance/impact_analyzer.py analyze
    --proposal registry/governance/change-proposals/CP-PGH-PILOT-002.yaml
    → verify output notes qname=[] (no spec authority) which contributes to REJECT
  MS-PGH-016-02-05: Record evidence: CP-PGH-PILOT-002.yaml (REJECTED) +
    CD-PGH-PILOT-002.yaml + impact_analyzer output

Acceptance:
  - CP-PGH-PILOT-002.yaml status=REJECTED
  - CD-PGH-PILOT-002.yaml final_decision=REJECT
  - rejection_reasons list non-empty with specific §6 violation references
```

#### TC-PGH-016-03 — Pilot 3: Pipeline Change with Product Pilot

```
Child Taskcard ID: TC-PGH-016-03
Status: TODO
Source:
  Req: REQ-GOV-020
  Section: §18.3
  TARGET (D4 solution): Add a governance header comment to .claude/commands/add-python-api.md

Micro-steps:
  MS-PGH-016-03-01: Read .claude/commands/add-python-api.md first 10 lines
  MS-PGH-016-03-02: Write CP-PGH-PILOT-003.yaml:
    change_id: CP-PGH-PILOT-003
    title: "Add governance header to add-python-api skill command"
    product_or_pipeline: pipeline
    affected_files: [.claude/commands/add-python-api.md]
    compatibility_impact: NONE
    status: SUBMITTED
  MS-PGH-016-03-03: Write CI-PGH-PILOT-003.yaml (pipeline impact):
    change_id: CP-PGH-PILOT-003
    affected_pipeline_components: [PIPE-FODS-SKILL-001]
    compatibility_class: NONE
  MS-PGH-016-03-04: Write CD-PGH-PILOT-003.yaml with final_decision: ACCEPT
  MS-PGH-016-03-05: Add one line to .claude/commands/add-python-api.md:
    (at top, after # title): <!-- governance: change_proposal_ref: CP-PGH-PILOT-003 -->
  MS-PGH-016-03-06: Update CP-PGH-PILOT-003.yaml status: ACCEPTED
  MS-PGH-016-03-07: Run pipeline_change_governor.py pilot --skill add-python-api --format fods
    → record pilot evidence; updates pipeline-components.yaml last_product_pilot field
  MS-PGH-016-03-08: Verify pipeline-components.yaml last_product_pilot updated to CP-PGH-PILOT-003
  MS-PGH-016-03-09: Verify PIPELINE_CHANGES_WITHOUT_PRODUCT_IMPACT_PROOF = 0 for this change

Acceptance:
  - All 3 governance YAML files exist (proposal, impact, decision)
  - .claude/commands/add-python-api.md has governance comment
  - pipeline-components.yaml last_product_pilot field updated
```

#### TC-PGH-016-04 — Pilot 4: Documentation-Only Change

```
Child Taskcard ID: TC-PGH-016-04
Status: TODO
Source:
  Req: REQ-GOV-021
  Section: §18.4

Micro-steps:
  MS-PGH-016-04-01: Read src/python/fods/parser.py — confirmed public API is parse_fods()
    (NOT load_fods — that name does not exist; the main function is parse_fods())
  MS-PGH-016-04-02: Write CP-PGH-PILOT-004.yaml:
    title: "Add Returns: FodsDocument annotation to parse_fods() docstring"
    product_or_pipeline: product
    compatibility_impact: NONE
    documentation_impact: "Adds Returns: FodsDocument to docstring"
    release_impact: PATCH
    status: SUBMITTED
  MS-PGH-016-04-03: Write CI-PGH-PILOT-004.yaml: compatibility_class: NONE
  MS-PGH-016-04-04: Write CD-PGH-PILOT-004.yaml: final_decision: ACCEPT, documentation_verdict: PASS
  MS-PGH-016-04-05: Update docstring for parse_fods() in src/python/fods/parser.py:
    Add to existing docstring: "Returns: dict — neutral model workbook dict"
    (NOTE: parse_fods() currently returns a dict, not FodsDocument; the high-level FodsDocument
     class is in models.py. Docstring must document the ACTUAL return type accurately.
     Add: "Returns: dict containing workbook structure, or error dict on failure. Use
     FodsDocument.from_file() for the typed object model.")
  MS-PGH-016-04-06: Update CP-PGH-PILOT-004.yaml status: ACCEPTED
  MS-PGH-016-04-07: Run doc_compliance_checker.py check --format fods
    → verify no contradiction flagged for load function
  MS-PGH-016-04-08: Verify DOCUMENTATION_CONTRADICTING_RELEASED_BEHAVIOR = 0

Acceptance:
  - Docstring updated
  - doc_compliance_checker passes for load function
  - 3 governance YAML files complete
```

#### TC-PGH-016-05 — Pilot 5: Compatibility-Breaking Change Gating

```
Child Taskcard ID: TC-PGH-016-05
Status: TODO
Source:
  Req: REQ-GOV-022
  Section: §18.5
  NOTE: DO NOT IMPLEMENT the rename. Prove gating only via governance records.

Micro-steps:
  MS-PGH-016-05-01: Write CP-PGH-PILOT-005.yaml:
    title: "PROPOSAL ONLY: Rename FodsDocument.sheets() to .worksheets()"
    compatibility_impact: MAJOR
    affected_public_apis: [FodsDocument.sheets]
    NOTE: FodsDocument.sheets() is an existing method in models.py returning list[FodsSheet].
    This proposal is proof-of-gating ONLY — do NOT rename the method.
    status: SUBMITTED
  MS-PGH-016-05-02: Write CI-PGH-PILOT-005.yaml: compatibility_class: MAJOR,
    required_migrations: ["Callers of .sheets must be updated to .worksheets"]
  MS-PGH-016-05-03: Write CD-PGH-PILOT-005.yaml:
    final_decision: ACCEPT_WITH_REWORK_BEFORE_RELEASE
    required_rework: ["Migration guide must be added to release_notes before RC creation"]
    release_verdict: FAIL
  MS-PGH-016-05-04: Update RC-FODS-PYREL-001.yaml to add CP-PGH-PILOT-005 to excluded_change_ids
    (cannot be included until migration guide written)
  MS-PGH-016-05-05: Run release_eligibility_checker.py check fods
    → verify CP-PGH-PILOT-005 is correctly excluded (not blocking RC for other reasons)
  MS-PGH-016-05-06: Verify CP-PGH-PILOT-005.yaml remains status: SUBMITTED (not implemented)
    and that src/python/fods/ files are UNCHANGED (no rename happened)

Acceptance:
  - CP-PGH-PILOT-005.yaml status=SUBMITTED (not ACCEPTED — rework required before release)
  - CD-PGH-PILOT-005.yaml final_decision=ACCEPT_WITH_REWORK_BEFORE_RELEASE
  - RC-FODS-PYREL-001.yaml excluded_change_ids includes CP-PGH-PILOT-005
  - No code was renamed (Glob confirms FodsDocument.sheets still exists)
```

---

### TC-PGH-017 — Required Pilots 6–10

```
Parent Taskcard ID: TC-PGH-017
Title: Execute and evidence Pilots 6–10 (reopening, RC eligibility, drift, maintenance, idempotency)
Type: PARENT
Status: PROPOSED

Dependencies: TC-PGH-016 CLOSED (Pilot 7 needs Pilot 1 artifacts; Pilot 10 needs all tools)
              TC-PGH-012 CLOSED (reopening_detector.py for Pilot 6)

Child taskcards:
  - TC-PGH-017-01: Pilot 6 — Promoted Artifact Modification
  - TC-PGH-017-02: Pilot 7 — Release Candidate Eligibility
  - TC-PGH-017-03: Pilot 8 — Generated Output Drift
  - TC-PGH-017-04: Pilot 9 — Long-term Maintenance Fix
  - TC-PGH-017-05: Pilot 10 — Idempotency
```

#### TC-PGH-017-01 — Pilot 6: Promoted Artifact Modification

```
Child Taskcard ID: TC-PGH-017-01
Status: TODO
Source:
  Req: REQ-GOV-023
  Section: §18.6
  NOTE: Uses reopening_detector.py to DETECT a change. Does NOT make an undeclared change.
    Instead, temporarily computes what WOULD happen if a file changed, then proves V159 catches it.

Micro-steps:
  MS-PGH-017-01-01: Run reopening_detector.py scan --base-promotion PROM-FODS-001
    → record current output (likely no conditions if files haven't changed since promotion)
  MS-PGH-017-01-02: Compute sha256 of src/python/fods/models.py current content
    python -c "import hashlib; print(hashlib.sha256(open('src/python/fods/models.py','rb').read()).hexdigest())"
  MS-PGH-017-01-03: Compare with promotion_hash in PROM-FODS-001.yaml
    (PROM-FODS-001 was created AFTER Pilot 1 added get_worksheet_names method,
     so if promotion_hash was computed after Pilot 1, they may match; if computed before,
     they won't match → either way, record what reopening_detector reports)
  MS-PGH-017-01-04: If hash DIFFERS (models.py changed since promotion):
    - reopening_detector scan output shows public_api_change condition triggered
    - Verify V159 would flag this: manually check V159 logic against current declaration
    - Record: "Pilot 6 DEMONSTRATED: reopening condition triggered for public_api_change"
  MS-PGH-017-01-05: If hash MATCHES (no change since promotion):
    - Manually construct a mock test showing what V159 WOULD return if models.py changed
    - Write mock test: echo "mock change" → compute new hash → run detector logic manually
    - Record: "Pilot 6 DEMONSTRATED via controlled test: V159 detects hash mismatch"
  MS-PGH-017-01-06: Write evidence: .local/evidences/pgh-017/pilot-6-evidence.txt
    containing: detector output, sha256 comparison, V159 verification

Acceptance:
  - reopening_detector.py ran without error
  - Either real detection OR controlled test demonstrates V159 logic
  - Evidence file written
```

#### TC-PGH-017-02 — Pilot 7: Release Candidate Eligibility

```
Child Taskcard ID: TC-PGH-017-02
Status: TODO
Source:
  Req: REQ-GOV-024
  Section: §18.7

Micro-steps:
  MS-PGH-017-02-01: Verify RC-FODS-PYREL-001.yaml exists with:
    included_change_ids containing CP-PGH-PILOT-001 (Pilot 1 change — accepted)
    excluded_change_ids containing CP-PGH-PILOT-005 (compat change — not ready)
  MS-PGH-017-02-02: Verify CD-PGH-PILOT-001.yaml final_decision=ACCEPT (included change accepted)
  MS-PGH-017-02-03: Run release_eligibility_checker.py report
    → reports/product-governance/release-eligibility-report.yaml
  MS-PGH-017-02-04: Read release-eligibility-report.yaml
    → verify RC-FODS-PYREL-001 verdict section
  MS-PGH-017-02-05: Confirm 3 RC counters are computable from report:
    RELEASE_CANDIDATES_WITH_UNACCEPTED_CHANGES: 0 (CP-PGH-PILOT-001 is ACCEPTED)
    RELEASE_CANDIDATES_WITH_UNKNOWN_COMPATIBILITY: 0 (PATCH is known)
    RELEASE_CANDIDATES_WITH_STALE_DOCUMENTATION: 0 (doc updated in Pilot 4)
  MS-PGH-017-02-06: Record counter values in evidence
```

#### TC-PGH-017-03 — Pilot 8: Generated Output Drift

```
Child Taskcard ID: TC-PGH-017-03
Status: TODO
Source:
  Req: REQ-GOV-025
  Section: §18.8
  NOTE: Does NOT modify autonomous_cycle.py. Demonstrates detection mechanism.

Micro-steps:
  MS-PGH-017-03-01: Run traceability_chain_builder.py build --format fods
    → save output to .local/evidences/pgh-017/traceability-graph-run1.yaml
  MS-PGH-017-03-02: Run traceability_chain_builder.py build --format fods again
    → save output to .local/evidences/pgh-017/traceability-graph-run2.yaml
  MS-PGH-017-03-03: Diff the two outputs (ignore timestamps):
    python -c "
    import yaml
    r1 = yaml.safe_load(open('.local/evidences/pgh-017/traceability-graph-run1.yaml'))
    r2 = yaml.safe_load(open('.local/evidences/pgh-017/traceability-graph-run2.yaml'))
    print('IDENTICAL' if r1 == r2 else 'DIFFERS')
    "
    Expected: IDENTICAL (idempotent runs)
  MS-PGH-017-03-04: Demonstrate V155 detection logic manually:
    Manually compute sha256 of reports/product-governance/traceability-graph.yaml
    Compare to a hypothetical stored baseline (same file = same hash = no drift)
    Record: "V155 would return PASS: generated output matches baseline"
  MS-PGH-017-03-05: Simulate drift: create a test record where hash differs,
    verify V155 returns WARN for that case
  MS-PGH-017-03-06: Write evidence: pilot-8-evidence.txt with diff output + V155 logic proof
```

#### TC-PGH-017-04 — Pilot 9: Long-term Maintenance Fix

```
Child Taskcard ID: TC-PGH-017-04
Status: TODO
Source:
  Req: REQ-GOV-026
  Section: §18.9
  TARGET: Determined by TC-PGH-003-04 MS-PGH-003-04-05.
  VERIFIED FINDING (C15): All 3 primary FODS model classes (FodsDocument, FodsSheet, FodsCell)
    in src/python/fods/models.py already have spec_qname. The earlier default target
    "fods.models.FodsFormula" does NOT exist in models.py.
  REVISED DEFAULT (if TC-PGH-003-02 finds no missing spec_qname in FODS):
    Look for classes without spec_qname in:
    1. src/python/fods/spec/ subdirectory classes (e.g. Document, Table, TableCell) — check
       if the spec layer has spec_qname or if it's at the domain-model layer only.
    2. Another Python format (e.g. fodt, ods) where TC-PGH-003-02 finds a missing spec_qname.
    3. If still no candidate: add INTENTIONAL_UNMAPPED to a spec/ subclass within FODS
       that intentionally has no direct spec_qname mapping (internal implementation class).
    Fallback of last resort: document this as "ALL FODS MODEL CLASSES HAVE SPEC_QNAME"
    and target an ODS or FODT model class found by TC-PGH-003-02 instead.

PRECONDITION: Read TC-PGH-003-04 result from product-governance-ledger.yaml
  to confirm Pilot 9 target before beginning.

Micro-steps:
  MS-PGH-017-04-01: Read reports/product-governance/product-governance-ledger.yaml
    → find the GOV-GAP entry with category=missing_qname for FODS model class
    → record target class name
  MS-PGH-017-04-02: Write CP-PGH-PILOT-009.yaml:
    title: "Maintenance fix: add INTENTIONAL_UNMAPPED annotation to <target class>"
    maintenance_class: defect_fix  # or specification_alignment if spec is ambiguous
    compatibility_impact: NONE
    status: SUBMITTED
  MS-PGH-017-04-03: Write CI-PGH-PILOT-009.yaml: compatibility_class: NONE
  MS-PGH-017-04-04: Write CD-PGH-PILOT-009.yaml: final_decision: ACCEPT
  MS-PGH-017-04-05: Run maintenance_classifier.py classify --proposal CP-PGH-PILOT-009.yaml
    → verify classified as defect_fix
  MS-PGH-017-04-06: Apply the fix to src/python/fods/models.py:
    Add to the target class: spec_qname: ClassVar[str] = "INTENTIONAL_UNMAPPED"
    (or add actual spec_qname if known from SAL facts)
  MS-PGH-017-04-07: Update file-ownership.yaml for models.py:
    change_proposal_id: CP-PGH-PILOT-009
  MS-PGH-017-04-08: Update CP-PGH-PILOT-009.yaml status: ACCEPTED
  MS-PGH-017-04-09: Run .venv/Scripts/pytest tests/python/fods/ -v → verify no regressions
  MS-PGH-017-04-10: Update PROM-FODS-001.yaml change_ids to include CP-PGH-PILOT-009
  MS-PGH-017-04-11: Record evidence: full lifecycle YAMLs + test output

Acceptance:
  - models.py updated (spec_qname or INTENTIONAL_UNMAPPED added)
  - maintenance_class recorded in CP-PGH-PILOT-009.yaml
  - No test regressions
  - file-ownership.yaml updated
```

#### TC-PGH-017-05 — Pilot 10: Idempotency

```
Child Taskcard ID: TC-PGH-017-05
Status: TODO
Source:
  Req: REQ-GOV-027
  Section: §18.10

Micro-steps:
  MS-PGH-017-05-01: Run traceability_chain_builder.py build --format fods
    → save to pilot10-run1-traceability.yaml
  MS-PGH-017-05-02: Run release_eligibility_checker.py report
    → save to pilot10-run1-eligibility.yaml
  MS-PGH-017-05-03: Run reopening_detector.py scan --base-promotion PROM-FODS-001
    → save output to pilot10-run1-reopening.txt
  MS-PGH-017-05-04: Run change_proposal_manager.py list
    → save count output to pilot10-run1-proposals.txt
  MS-PGH-017-05-05: Run each tool AGAIN (second run):
    Save pilot10-run2-* for each tool
  MS-PGH-017-05-06: Diff run1 vs run2 for each tool output (excluding timestamps):
    → All diffs must be empty or contain only timestamp fields
  MS-PGH-017-05-07: Compute MATERIAL_SECOND_RUN_CHANGES:
    = number of substantive (non-timestamp) lines that differ between run1 and run2
    → must = 0
  MS-PGH-017-05-08: Record all diffs in evidence as pilot-10-idempotency-proof.txt

Acceptance:
  - All 4 tools ran twice
  - MATERIAL_SECOND_RUN_CHANGES = 0
  - Evidence file records proof
```

---

### TC-PGH-018 — Completion Gate — 22 Counters

```
Parent Taskcard ID: TC-PGH-018
Title: completion_gate_checker.py measures all 22 counters; all = 0
Type: PARENT
Status: PROPOSED

Dependencies: TC-PGH-017 CLOSED (all 10 pilots complete)

Child taskcards:
  - TC-PGH-018-01: Write completion_gate_checker.py
  - TC-PGH-018-02: Run checker; verify all 22 counters = 0
  - TC-PGH-018-03: Run checker again (idempotency); verify MATERIAL_SECOND_RUN_CHANGES = 0
```

#### TC-PGH-018-01 — Write completion_gate_checker.py

```
Child Taskcard ID: TC-PGH-018-01
Status: TODO
Micro-steps:
  MS-PGH-018-01-01: Write tools/governance/completion_gate_checker.py:
    CLI: python tools/governance/completion_gate_checker.py [--output-path <yaml>]
    Logic (one measurement per counter):
    1. GOVERNANCE_CONTROLS_NOT_INVENTORIED:
       count stages in governance-control-inventory.yaml where status=DRAFT → expect 0
    2. LIFECYCLE_STAGES_WITHOUT_GOVERNANCE:
       count stages with authority=null → expect 0
    3. MATERIAL_CHANGES_WITHOUT_CHANGE_PROPOSALS:
       count V156 FAIL entries in last validator run output → expect 0
    4. MATERIAL_CHANGES_WITHOUT_IMPACT_ANALYSIS:
       count CP-*.yaml files without matching CI-*.yaml → expect 0
    5. PRODUCT_CHANGES_WITHOUT_QNAME_OR_API_AUTHORITY:
       count V150 FAIL entries → expect 0
    6. PIPELINE_CHANGES_WITHOUT_PRODUCT_IMPACT_PROOF:
       count V154 WARN entries with no pilot recorded → expect 0
    7. CODE_CHANGES_WITHOUT_TRACEABILITY:
       count V157 WARN entries → expect 0
    8. RELEASED_SYMBOLS_WITHOUT_TRACEABILITY:
       count traceability-graph.yaml entries with chain_status=BROKEN → expect 0
    9. CHANGES_WITHOUT_ACCEPT_REJECT_DECISION:
       count CP-*.yaml with status=SUBMITTED but no CD-*.yaml → expect 0
    10. ACCEPTED_CHANGES_WITHOUT_PROOF:
        count CD-*.yaml with final_decision=ACCEPT but evidence=[] → expect 0
    11. PROMOTED_ARTIFACTS_WITHOUT_BASELINE:
        count PROM-*.yaml with promotion_hash=null or missing → expect 0
    12. PROMOTED_ARTIFACTS_CHANGED_WITHOUT_REOPENING:
        count V159 WARN entries → expect 0
    13. RELEASED_ARTIFACTS_CHANGED_WITHOUT_NEW_CHANGE_RECORD:
        count V159 items cross-checked with git blame → expect 0
    14-16. RELEASE_CANDIDATES_WITH_*:
        from release-eligibility-report.yaml → expect 0 each
    17. UNGOVERNED_PIPELINE_COMPONENTS:
        count pipeline-components.yaml entries with artifact_registry_entry=null → expect 0
    18. UNGOVERNED_PRODUCT_ARTIFACTS:
        count format-registry.yaml formats without artifact-registry.yaml entry → expect 0
    19. MATERIAL_FINDINGS_WITHOUT_GAPS:
        count audit findings from TC-PGH-003 without gap record → expect 0
    20. ACTIONABLE_GAPS_WITHOUT_TASKS:
        count product-governance-ledger.yaml CRITICAL gaps with task_ids=[] → expect 0
    21. FAILED_REQUIRED_PILOTS:
        count pilots 1-10 without evidence files → expect 0
    22. MATERIAL_SECOND_RUN_CHANGES:
        read from pilot-10-idempotency-proof.txt → expect 0
    Output: reports/product-governance/completion-gate-status.yaml
  MS-PGH-018-01-02: python tools/governance/completion_gate_checker.py --help → exit 0
```

#### TC-PGH-018-02 — Run checker; verify all 22 = 0

```
Child Taskcard ID: TC-PGH-018-02
Status: TODO
Preconditions: TC-PGH-018-01 CLOSED
Micro-steps:
  MS-PGH-018-02-01: python tools/governance/completion_gate_checker.py
    --output-path reports/product-governance/completion-gate-status.yaml
  MS-PGH-018-02-02: Read completion-gate-status.yaml → verify all_counters_zero: true
  MS-PGH-018-02-03: For any counter > 0, record which counter and its value
  MS-PGH-018-02-04: If any counter > 0 → mark TC-PGH-018-02 REROUTED and
    identify which TC is responsible for fixing it (use the table in PART III above)

Acceptance:
  - completion-gate-status.yaml exists
  - all_counters_zero: true
  - verdict in {FORMAT_FACTORY_PRODUCT_GOVERNANCE_HEALED_TRACEABLE_AND_RELEASE_CONTROLLED,
               GOVERNANCE_BACKFILL_STILL_ACTIVE}
```

#### TC-PGH-018-03 — Second run (idempotency proof)

```
Child Taskcard ID: TC-PGH-018-03
Status: TODO
Preconditions: TC-PGH-018-02 CLOSED
Micro-steps:
  MS-PGH-018-03-01: python tools/governance/completion_gate_checker.py
    --output-path reports/product-governance/completion-gate-status-run2.yaml
  MS-PGH-018-03-02: Diff completion-gate-status.yaml vs completion-gate-status-run2.yaml
    (excluding run_at timestamp)
  MS-PGH-018-03-03: Verify no substantive differences
  MS-PGH-018-03-04: Verify verdict unchanged between runs
```

---

### TC-PGH-019 — Final Governance Report

```
Parent Taskcard ID: TC-PGH-019
Title: Write reports/product-governance/governance-report.md with final verdict
Type: PARENT
Status: PROPOSED

Dependencies: TC-PGH-018 CLOSED

Child taskcards:
  - TC-PGH-019-01: Compile all evidence and counter values
  - TC-PGH-019-02: Write governance-report.md with 17 required sections and verdict
```

#### TC-PGH-019-01 — Compile evidence

```
Child Taskcard ID: TC-PGH-019-01
Status: TODO
Micro-steps:
  MS-PGH-019-01-01: Read completion-gate-status.yaml → extract all 22 counter values
  MS-PGH-019-01-02: Read release-eligibility-report.yaml → extract RC verdict
  MS-PGH-019-01-03: Read product-governance-ledger.yaml → count gaps by severity
  MS-PGH-019-01-04: Count: pilot YAML files in registry/governance/change-proposals/
    change-impacts/, change-decisions/ → verify 10 pilots evidenced
  MS-PGH-019-01-05: Read tests/governance/test_product_gov_validators.py test results
  MS-PGH-019-01-06: Record all absolute evidence paths (starting with
    C:\Users\prora\OneDrive\Documents\GitHub\format-factory\)
```

#### TC-PGH-019-02 — Write governance-report.md

```
Child Taskcard ID: TC-PGH-019-02
Status: TODO
Preconditions: TC-PGH-019-01 CLOSED
Micro-steps:
  MS-PGH-019-02-01: Write reports/product-governance/governance-report.md
    with all 17 required sections from §20 of the governance healing spec:
    1. Current governance architecture
    2. Missing lifecycle controls found and fixed
    3. Product and pipeline artifact model
    4. Change proposal and impact system
    5. Aspose/QName enforcement (V150–V152 results)
    6. Code-writing and maintenance controls
    7. Documentation and traceability
    8. Accept/reject workflow (Pilot 1 ACCEPT, Pilot 2 REJECT)
    9. Promotion and reopening (V159 results, Pilot 6)
    10. Release eligibility (RC-FODS-PYREL-001 verdict)
    11. Pipeline governance (V153–V155 results, Pilot 3)
    12. Existing-state backfill (artifact-registry count)
    13. Pilot results (all 10 pilots with outcomes)
    14. Idempotency (Pilot 10, MATERIAL_SECOND_RUN_CHANGES = 0)
    15. Remaining true external blockers
    16. Exact evidence paths (absolute)
    17. Final verdict
  MS-PGH-019-02-02: Select final verdict from:
    FORMAT_FACTORY_PRODUCT_GOVERNANCE_HEALED_TRACEABLE_AND_RELEASE_CONTROLLED
      (if all 22 counters = 0 AND all 10 pilots complete)
    FORMAT_FACTORY_PRODUCT_GOVERNANCE_REQUIRES_REWORK
      (if any mandatory counter > 0)
    GOVERNANCE_BACKFILL_STILL_ACTIVE
      (if backfill complete but counters not fully verified)
  MS-PGH-019-02-03: Verify report contains all absolute paths from TC-PGH-019-01

Acceptance:
  - Report exists
  - All 17 sections present
  - Final verdict explicitly stated
  - All 22 counter values referenced
  - All 10 pilots referenced
  - All evidence paths are absolute
```

---

## PART IX — VALIDATION MATRIX

| TC-ID | Check | Command/Method | Expected | Mandatory |
|-------|-------|----------------|----------|-----------|
| TC-PGH-001-03 | YAML parses | python -c "import yaml; yaml.safe_load(open('registry/governance/governance-binding.yaml'))" | exit 0 | YES |
| TC-PGH-001-03 | Schema validates | jsonschema.validate(data, schema) | VALID | YES |
| TC-PGH-001-03 | Paths resolve | Glob each path value | all EXISTS | YES |
| TC-PGH-002-03 | 16 stages present | count entries in YAML | 16 | YES |
| TC-PGH-002-03 | No null authority | grep authority: null | zero matches | YES |
| TC-PGH-003-04 | Ledger has entries | count gap records | ≥ 1 | YES |
| TC-PGH-003-04 | CRITICAL gaps tasked | count CRITICAL with empty task_ids | 0 | YES |
| TC-PGH-004-03 | 6+ pilot artifacts | count entries | ≥ 6 | YES |
| TC-PGH-004-03 | All types valid | validate each artifact_type against schema enum | all valid | YES |
| TC-PGH-005-02 | Manager CLI runs | python change_proposal_manager.py --help | exit 0 | YES |
| TC-PGH-005-02 | Manager list runs | python change_proposal_manager.py list | exit 0 | YES |
| TC-PGH-006-04 | CD-002 rejected | CD-PGH-PILOT-002.yaml final_decision=REJECT | REJECT | YES |
| TC-PGH-007-04 | RC record exists | Glob release-candidates/RC-FODS-PYREL-001.yaml | EXISTS | YES |
| TC-PGH-007-04 | Eligibility report | Glob release-eligibility-report.yaml | EXISTS | YES |
| TC-PGH-008-04 | Module importable | python -c "import governance_validators_product_gov" | exit 0 | YES |
| TC-PGH-008-04 | 14 validators | count validate_ functions | 14 | YES |
| TC-PGH-009-01 | Pipeline governor runs | python pipeline_change_governor.py --help | exit 0 | YES |
| TC-PGH-009-01 | 15 components | count entries in pipeline-components.yaml | 15 | YES |
| TC-PGH-014-03 | expected_count = 181 | grep expected_count governance_validator_runner.py | 181 | YES |
| TC-PGH-014-03 | Runner imports OK | python -c "from governance_validator_runner import run_all_governance_validators" | exit 0 | YES |
| TC-PGH-014-04 | Focused tests pass | pytest tests/governance/test_product_gov_validators.py -v | all PASS | YES |
| TC-PGH-015-01 | ≥ 86 artifacts | count entries in artifact-registry.yaml | ≥ 86 | YES |
| TC-PGH-016-01 | Method exists | Grep models.py for "get_worksheet_names" | FOUND | YES |
| TC-PGH-016-01 | No test regressions | pytest tests/python/fods/ -v | 0 FAILED | YES |
| TC-PGH-016-02 | CD-002 REJECT | Read CD-PGH-PILOT-002.yaml | final_decision=REJECT | YES |
| TC-PGH-017-05 | Idempotency | diff run1 vs run2 outputs | 0 substantive diffs | YES |
| TC-PGH-018-02 | All counters = 0 | Read completion-gate-status.yaml | all_counters_zero=true | YES |
| TC-PGH-018-03 | Second run same | diff run1 vs run2 status | identical verdict | YES |
| TC-PGH-019-02 | Report exists | Glob governance-report.md | EXISTS | YES |
| TC-PGH-019-02 | Verdict present | Grep governance-report.md for verdict keywords | FOUND | YES |

---

## PART X — EVIDENCE CONTRACT

Every taskcard must write evidence to `.local/evidences/pgh-{tc-number}/` before closing.

**Evidence structure:**
```
.local/evidences/
  pgh-001/
    path-verification.txt          (TC-PGH-001-01)
    schema-validation-output.txt   (TC-PGH-001-02)
    yaml-validation-output.txt     (TC-PGH-001-03)
  pgh-003/
    python-audit.txt               (TC-PGH-003-02)
    pipeline-audit.txt             (TC-PGH-003-03)
    pilot-9-target.txt             (TC-PGH-003-04)
  pgh-008/
    import-test-output.txt         (TC-PGH-008-04)
  pgh-014/
    test-output.txt                (TC-PGH-014-04)
    validator-count-proof.txt      (TC-PGH-014-01)
  pgh-016/
    pilot-6-evidence.txt           (TC-PGH-017-01)
  pgh-017/
    pilot-8-evidence.txt           (TC-PGH-017-03)
    pilot-10-idempotency-proof.txt (TC-PGH-017-05)
```

Every evidence file must reference:
- authoritative plan: C:/Users/prora/.claude/plans/iterative-mixing-shannon.md
- relevant TC-ID
- date/timestamp

---

## PART XI — QUALITY SCORING

Every child taskcard must be scored before CLOSED. Minimum 4/5 on all mandatory dimensions.

| Dimension | Score | Description |
|-----------|-------|-------------|
| requirement_correctness | 1-5 | Does output match §-spec requirement? |
| implementation_correctness | 1-5 | Is the output accurate and complete? |
| scope_discipline | 1-5 | Were forbidden files untouched? |
| validation_strength | 1-5 | Were all validation commands run? |
| evidence_completeness | 1-5 | Are all evidence files written? |
| regression_safety | 1-5 | Did existing tests still pass? |

**Reroute trigger:** Any dimension ≤ 3/5 → mark REROUTED, record weak dimension, execute fix.

---

## PART XII — PLAN RECONCILIATION CHECKLIST

Before execution begins, confirm:
- [ ] Only one authoritative plan: this file
- [ ] TC-PGH-013 has been REMOVED (folded into TC-PGH-007-04) — ✅ Done in v2
- [ ] Validator module path corrected: tools/supervisor/governance_validators_product_gov.py — ✅
- [ ] expected_count corrected: 167 → 181 — ✅
- [ ] tools/governance/ directory status: EXISTS — ✅
- [ ] Pilot 9 target pre-scoped — ✅
- [ ] Pilot 3 target pre-scoped — ✅
- [ ] lane-scope-registry.yaml flagged as machine-generated — ✅
- [ ] All 18 parent TCs have child TCs — ✅
- [ ] All child TCs have micro-steps — ✅
- [ ] Dependency DAG defined — ✅
- [ ] Machine state rules defined — ✅
- [ ] Validation matrix defined — ✅
- [ ] Evidence contract defined — ✅

---

## PART XIII — EXECUTION HANDOFF

**Active plan path:** `C:/Users/prora/.claude/plans/iterative-mixing-shannon.md`

### First parent taskcard: TC-PGH-001
### First child taskcard: TC-PGH-001-01
### First micro-step: MS-PGH-001-01-01

**Pre-execution checklist (run before first micro-step):**
1. Confirm `git status` shows branch=main, no stale uncommitted plan lock blocking work
2. Run `python tools/supervisor/check_continuation.py` — if STOP due to non-plan-terminal reason, override per CLAUDE.md Supreme Directive
3. Confirm `.local/evidences/` directory exists: `mkdir -p .local/evidences/pgh-001`
4. Confirm `reports/product-governance/` does NOT yet exist (will be created in TC-PGH-002-01)
5. Confirm `registry/governance/` does NOT yet exist (will be created in TC-PGH-001-01)

**Execution protocol (repeat for each micro-step):**
1. Read the parent taskcard in this plan
2. Read the child taskcard
3. Confirm the micro-step ID and action
4. Confirm preconditions are met (prior micro-steps COMPLETE)
5. Confirm allowed files (touch ONLY those listed)
6. Execute exactly one micro-step
7. Capture evidence immediately (write to .local/evidences/pgh-{tc}/)
8. Update micro-step status: ACTIVE → COMPLETE (or FAILED)
9. Run acceptance check for the micro-step
10. Update child taskcard status when all micro-steps COMPLETE → IMPLEMENTED
11. Run child acceptance checks → VERIFIED
12. Score child → SCORED
13. If any score ≤ 3/5 → mark REROUTED; fix before moving forward
14. Mark child CLOSED only after score ≥ 4/5 on all dimensions
15. When all children of a parent CLOSED → run parent integration checks
16. Score parent → if ≥ 4/5 → CLOSED
17. Consult DEPENDENCY DAG → find next valid parent
18. Repeat

**Execution agent must NOT:**
- Choose unrelated work (no next-sprint.md during this plan)
- Skip micro-steps without reason
- Close a child before all micro-steps complete
- Close a parent before all children CLOSED
- Treat "file exists" as "file is correct" — read and verify content
- Treat "test exists" as "test passes" — run tests and capture output
- Work on TC-PGH-016 before all Phase B + C TCs are CLOSED
- Work on TC-PGH-018 before all 10 pilots are evidenced

**True external blockers (will stop execution):**
- git push credentials unavailable — BLOCKED_EXTERNAL: git_push_credentials_unavailable
- Gate 11 execution approval — BLOCKED_EXTERNAL: gate_11_requires_babar_raza
- PyPI publication — BLOCKED_EXTERNAL: publication_credentials_unavailable

**Post-plan closure:**
When TC-PGH-019 CLOSED:
1. Run: `python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/iterative-mixing-shannon.md --terminal`
2. Report: "Plan iterative-mixing-shannon complete. All 18 parent taskcards closed. Verdict: <final_verdict>."
3. STOP — do not start ledger sprints.

---

## APPENDIX A — New Files Summary

### New Schemas (9) in `.supervisor/schemas/`:
`governance-binding.schema.json`, `governance-control.schema.json`, `governance-gap.schema.json`,
`governed-artifact.schema.json`, `change-proposal.schema.json`, `change-impact.schema.json`,
`change-decision.schema.json`, `promotion-record.schema.json`, `release-candidate.schema.json`

### New Tools (11) in `tools/governance/` (extends existing 8):
`change_proposal_manager.py`, `impact_analyzer.py`, `traceability_chain_builder.py`,
`pre_write_checklist.py`, `doc_compliance_checker.py`, `pipeline_change_governor.py`,
`promotion_manager.py`, `release_eligibility_checker.py`, `reopening_detector.py`,
`maintenance_classifier.py`, `completion_gate_checker.py`

### New Validator Module (1) in `tools/supervisor/`:
`governance_validators_product_gov.py` — 14 validators V150–V163

### New Registry Directories and Files in `registry/governance/`:
`governance-binding.yaml`, `artifact-registry.yaml`, `pipeline-components.yaml`,
`file-ownership.yaml`, `change-proposals/` (CP-PILOT-001 through CP-PILOT-009),
`change-impacts/` (CI-PILOT-001 through CI-PILOT-009),
`change-decisions/` (CD-PILOT-001 through CD-PILOT-009),
`promotions/` (PROM-FODS-001), `release-candidates/` (RC-FODS-PYREL-001)

### New Reports in `reports/product-governance/`:
`governance-control-inventory.yaml`, `product-governance-ledger.yaml`,
`traceability-graph.yaml`, `doc-compliance-report.yaml`,
`release-eligibility-report.yaml`, `completion-gate-status.yaml`,
`completion-gate-status-run2.yaml`, `governance-report.md`

### Modified Files:
| File | Modification |
|------|-------------|
| `tools/supervisor/governance_validator_runner.py` | Add lazy import block + 14 calls + expected_count 167→181 |
| `tests/governance/test_product_gov_validators.py` | NEW focused test file |
| `.supervisor/skill-registry.yaml` | Add change_proposal_required field to material-change skills |
| `registry/format-registry.yaml` | Add governance_status section for 4 pilot formats |
| `src/python/fods/models.py` | Pilot 1: add get_worksheet_names() + Pilot 9: add INTENTIONAL_UNMAPPED |
| `src/python/fods/__init__.py` | Pilot 1: ensure get_worksheet_names in __all__ |
| `src/python/fods/parser.py` | Pilot 4: add Returns annotation to docstring |
| `.claude/commands/add-python-api.md` | Pilot 3: add governance comment header |

---

## APPENDIX B — Idempotency Rules

On any rerun of this plan:
1. Re-read this file as the authoritative plan
2. Check TC status table — skip CLOSED taskcards
3. Resume at first non-CLOSED taskcard in DAG order
4. Reuse stable IDs (TC-PGH-*, MS-PGH-*, CP-PGH-*, etc.) — do NOT regenerate
5. Do not duplicate registry/governance/ entries — check existence before appending
6. Validator count: if governance_validators_product_gov.py already exists with 14 validators,
   skip TC-PGH-008-04 through TC-PGH-012-03 and go to TC-PGH-014
7. Any REROUTED taskcard: re-read its reroute_rule, fix the weak dimension, re-verify, re-score

---

## PART XIV — VERIFIED SOURCE CATALOG

**Status:** ANALYSIS_COMPLETE — verified against HEAD af879e55 (2026-07-10)

This section fulfills deliverable requirements for `plan-part-deep-analysis.yaml` and
`phase-section-step-analysis.md`. All artifact-reference entries corrected per C11-C15.

```yaml
authoritative_plan: C:/Users/prora/.claude/plans/iterative-mixing-shannon.md
artifact_role: embedded_analysis_evidence
execution_authority: false

fods_domain_model:
  file: src/python/fods/models.py
  classes:
    - name: FodsDocument
      spec_qname: "office:document"
      methods:
        - "from_file(cls, path) -> FodsDocument"
        - "sheets() -> list[FodsSheet]"
        - "sheet_by_name(name) -> FodsSheet | None"
        - "find_sheet_by_index(index) -> FodsSheet | None"
        - "to_dict() -> dict"
      properties:
        - "format_id: str"
        - "odf_version: str"
        - "sheet_count: int"
        - "warnings: list"
        - "is_empty: bool"
        - "is_single_sheet: bool"
        - "is_multi_sheet: bool"
      pilot_1_addition: "get_worksheet_names(self) -> list[str]"
      pilot_1_implementation: "return [s.name for s in self.sheets()]"
    - name: FodsSheet
      spec_qname: "table:table"
      properties:
        - "name: str"
        - "rows: list"
        - "row_count: int"
    - name: FodsCell
      spec_qname: "table:table-cell"
      properties:
        - "value: Any"
        - "value_type: str"
        - "text: str"
        - "formula: str | None"
        - "repeated: int"
  pilot_9_status: "ALL 3 classes have spec_qname — NO missing spec_qname in FODS models.py"
  pilot_9_action: "TC-PGH-003-02 must scan OTHER formats (fodt, ods, csv, tsv, etc.) for missing spec_qname"

fods_parser:
  file: src/python/fods/parser.py
  exports:
    - "parse_fods(file_path) -> dict"  # returns neutral model dict, NOT FodsDocument
    - "parse_fods_strict(file_path) -> dict"  # raises on error
  pilot_4_docstring_note: "parse_fods returns dict, not FodsDocument. Docstring must document actual return type."

fods_writer:
  file: src/python/fods/writer.py
  exports:
    - "write_fods(workbook, file_path)"
    - "workbook_to_xml(workbook) -> str"

fods_init:
  file: src/python/fods/__init__.py
  api_style: "wildcard imports from all submodules; __all__ generated dynamically"
  primary_class_export: "FodsDocument exported via 'from .models import *'"
  version: "0.1.0"

fods_tests:
  directory: tests/python/fods/
  count: "90+ test files"
  key_files:
    - "test_fods_domain_models.py"
    - "test_fods_primary_api.py"
    - "test_fods_spec_qname.py"
    - "test_public_api.py"
    - "test_parser_basic.py"

existing_schemas:
  count: 25
  directory: .supervisor/schemas/

existing_governance_tools:
  count: 8
  directory: tools/governance/
  files:
    - check_docs_placement.py
    - check_git_safety.py
    - check_methodology_links.py
    - ci_skill_attribution_check.py
    - install_hooks.py
    - pre_mutation_guard.py
    - run_ci_governance_check.py
    - validate_taskcard_execution_contract.py

governance_runner:
  file: tools/supervisor/governance_validator_runner.py
  expected_count_line: 813
  current_value: 167
  comment: "# V149 added (TC-PFF-R1, 2026-07-09)"
  target_value: 181
  import_pattern: "lazy imports inside run_all_governance_validators() function body"

validator_style_reference:
  file: tools/supervisor/governance_validators_ext4.py
  pattern: "module docstring → from governance_validators_contract import validator → impl functions"
  function_signature: "def validate_X(declaration, repo_root) -> dict"
  return_keys: "validator_id, result (PASS/FAIL/WARN), summary, blocks_sprint, ..."

non_existent_paths:
  - registry/governance/  # MUST be created in TC-PGH-001-01
  - reports/product-governance/  # MUST be created in TC-PGH-002-01
  - tools/supervisor/governance_validators_product_gov.py  # MUST be created in TC-PGH-008-04
```

---

## PART XV — SECTION PROCESSING LEDGER

**Status:** ANALYSIS_COMPLETE

```yaml
authoritative_plan: C:/Users/prora/.claude/plans/iterative-mixing-shannon.md
artifact_role: section_processing_ledger
execution_authority: false

sections:
  - id: PART-I
    title: Preflight Analysis
    type: analysis_recon
    analysis_completed: yes
    corrections_found: 15  # C1-C15 (v2 added C1-C10; this pass added C11-C15)
    actionable_items: 0  # analysis only
    enhancement_required: DONE  # C11-C15 added
    reconciliation_status: COMPLETE

  - id: PART-II
    title: Preserved Context
    type: background_rationale
    analysis_completed: yes
    actionable_items: 0
    enhancement_required: NONE
    reconciliation_status: COMPLETE

  - id: PART-III
    title: Normalized Requirements Inventory
    type: requirements
    analysis_completed: yes
    items: 29  # REQ-GOV-001 through REQ-GOV-029
    all_mapped_to_taskcards: yes
    enhancement_required: NONE
    reconciliation_status: COMPLETE

  - id: PART-IV
    title: Solution Options
    type: design_decisions
    analysis_completed: yes
    decisions: 5  # D1-D5
    all_selected: yes
    enhancement_required: NONE
    reconciliation_status: COMPLETE

  - id: PART-V
    title: Taskcard Master Table
    type: execution_summary
    analysis_completed: yes
    parent_taskcards: 18
    tc_pgh_013_removed: yes
    enhancement_required: NONE
    reconciliation_status: COMPLETE

  - id: PART-VI
    title: Dependency DAG
    type: execution_ordering
    analysis_completed: yes
    groups: 7
    file_locks_defined: yes
    enhancement_required: NONE
    reconciliation_status: COMPLETE

  - id: PART-VII
    title: Machine State Rules
    type: state_machine
    analysis_completed: yes
    parent_transitions: 9
    child_transitions: 7
    micro_step_transitions: 5
    invalid_transitions_listed: yes
    enhancement_required: NONE
    reconciliation_status: COMPLETE

  - id: PART-VIII
    title: Enhanced Taskcards
    type: execution_taskcards
    analysis_completed: yes
    parent_taskcards: 18
    child_taskcards: 62  # approx (3-5 per parent)
    micro_steps: 200+
    c11_c15_corrections_applied: yes
    enhancement_required: DONE  # FodsDocument, parser.py, writer.py corrections applied
    reconciliation_status: COMPLETE

  - id: PART-IX
    title: Validation Matrix
    type: verification
    analysis_completed: yes
    checks: 30
    all_mandatory_flagged: yes
    enhancement_required: NONE
    reconciliation_status: COMPLETE

  - id: PART-X
    title: Evidence Contract
    type: evidence_obligations
    analysis_completed: yes
    directories_defined: 8
    per_file_tc_references: yes
    enhancement_required: NONE
    reconciliation_status: COMPLETE

  - id: PART-XI
    title: Quality Scoring
    type: quality_gates
    analysis_completed: yes
    dimensions: 6
    threshold: "4/5 all mandatory"
    reroute_rule_defined: yes
    enhancement_required: NONE
    reconciliation_status: COMPLETE

  - id: PART-XII
    title: Plan Reconciliation Checklist
    type: self_check
    analysis_completed: yes
    items: 14
    all_checked: yes
    enhancement_required: NONE
    reconciliation_status: COMPLETE

  - id: PART-XIII
    title: Execution Handoff
    type: handoff
    analysis_completed: yes
    first_taskcard: TC-PGH-001
    first_child: TC-PGH-001-01
    first_micro_step: MS-PGH-001-01-01
    pre_execution_checklist: 5 items
    execution_protocol: 18 steps
    enhancement_required: NONE
    reconciliation_status: COMPLETE

  - id: APPENDIX-A
    title: New Files Summary
    type: deliverable_inventory
    schemas: 9
    tools: 11
    validator_module: 1
    registry_directories: 9
    report_files: 8
    modified_files: 8
    c11_c15_corrections_applied: yes  # parser.py, writer.py, FodsDocument corrected
    enhancement_required: DONE
    reconciliation_status: COMPLETE

  - id: APPENDIX-B
    title: Idempotency Rules
    type: rerun_protocol
    rules: 7
    enhancement_required: NONE
    reconciliation_status: COMPLETE
```

---

## PART XVI — EXECUTION READINESS VERDICT

```yaml
authoritative_plan: C:/Users/prora/.claude/plans/iterative-mixing-shannon.md
artifact_role: execution_readiness_verdict
execution_authority: false

verdict: PLAN_MICRO_TASKCARDIZED_READY_FOR_EXECUTION

active_plan:
  authoritative_path: C:/Users/prora/.claude/plans/iterative-mixing-shannon.md
  authority_source: plan mode, current conversation
  duplicate_active_plans_found: NONE
  duplicate_risk_resolved: YES

plan_analysis:
  sections_analyzed: 15  # PART I–XIII + APPENDIX A–B
  phases_analyzed: 6  # A–F
  lanes_workstreams_analyzed: governance_lane (single lane)
  actionables_extracted: 46 deliverables embedded in plan
  ambiguous_actionables: 0 (C10-C15 resolved all ambiguities)
  investigation_taskcards_created: TC-PGH-003-02 (audit), TC-PGH-008-01 (source reading)

surgical_enhancements:
  sections_preserved: 15
  sections_expanded: 1  # PART I (added C11-C15)
  stale_details_replaced: 5  # FodsSpreadsheet→FodsDocument, fods_parser.py→parser.py,
                               # fods_writer.py→writer.py, load_fods→parse_fods, FodsFormula→revised
  contradictions_resolved: 5  # C11 through C15
  execution_sections_normalized: NONE needed (already normalized in v2)

decomposition:
  parent_taskcards: 18
  child_taskcards: 62 (approx)
  micro_steps: 200+
  broad_taskcards_split: 1  # TC-PGH-013 folded into TC-PGH-007-04
  smallest_step_quality: ACCEPTABLE — each micro-step is one file/one action/one output

machine_state:
  state_machine_added_or_updated: YES (PART VII)
  invalid_transitions_blocked: YES
  dependency_dag_created: YES (PART VI — 7 groups)
  file_ownership_defined: YES (PART VI locks table)

traceability:
  all_actionables_mapped: yes
  all_child_taskcards_linked_to_parents: yes
  all_micro_steps_linked_to_children: yes
  all_validations_linked: yes  # PART IX — 30 checks
  all_evidence_obligations_linked: yes  # PART X

single_plan_authority:
  one_authoritative_plan: yes
  competing_plan_versions_created: no
  supporting_artifacts_marked_non_authoritative: yes  # PART XIV, XV, XVI each marked

validation_and_evidence:
  verification_matrix: PART IX — 30 mandatory checks
  negative_controls: embedded in TC-PGH-016-02 (Pilot 2 rejection), TC-PGH-016-05 (gating)
  evidence_contract: PART X
  quality_scoring: PART XI — 6 dimensions, 4/5 threshold
  reroute_rules: embedded in every parent and child taskcard

execution_readiness:
  ready: yes
  blockers: NONE (all TRUE_EXTERNAL_GATEs are named: git push, Gate 11, PyPI)
  deferred_items: NONE
  next_valid_parent_taskcard: TC-PGH-001
  next_valid_child_taskcard: TC-PGH-001-01
  first_micro_step: MS-PGH-001-01-01 (Check if oracle/schemas/odf-1.3-relaxng/ exists)

files_changed:
  - C:/Users/prora/.claude/plans/iterative-mixing-shannon.md

supporting_artifacts_embedded:
  - PART I: preflight analysis + corrections table (15 corrections)
  - PART II: preserved context
  - PART III: normalized requirements inventory (29 requirements)
  - PART IV: solution options analysis + selection rationale
  - PART V: taskcard master table (18 parents)
  - PART VI: execution DAG + file ownership locks
  - PART VII: taskcard state machine + transition rules
  - PART VIII: all parent taskcards (18) + child taskcards (62) + micro-steps (200+)
  - PART IX: verification matrix (30 checks)
  - PART X: evidence contract
  - PART XI: quality scoring rubric
  - PART XII: plan reconciliation checklist
  - PART XIII: execution handoff (first micro-step identified)
  - PART XIV: verified source catalog (this pass — C11-C15 evidence)
  - PART XV: section processing ledger (this pass)
  - PART XVI: execution readiness verdict (this document)

final_self_review:
  entire_plan_read: yes
  every_relevant_plan_part_individually_analyzed: yes
  every_actionable_item_represented: yes
  every_broad_actionable_decomposed: yes
  micro_steps_are_smallest_meaningful_units: yes
  scope_drift_controls_present: yes  # allowed/forbidden file lists per taskcard
  parent_child_hierarchy_valid: yes
  taskcard_state_machine_valid: yes
  evidence_retained: yes
  only_one_authoritative_plan_remains: yes
  plan_ready_for_execution: yes

key_source_corrections_applied:
  C11: "FodsSpreadsheet → FodsDocument (primary class, verified in models.py)"
  C12: "fods_parser.py → parser.py (verified file, exports parse_fods)"
  C13: "fods_writer.py → writer.py (verified file, exports write_fods)"
  C14: "get_worksheet_names implementation: [s.name for s in self.sheets()] (not self.worksheets)"
  C15: "FodsFormula does not exist; Pilot 9 target revised to use TC-PGH-003-02 audit result"
```

---

*Plan v2.1 — Enhanced with additional source corrections C11-C15 (verified against HEAD),
embedded analysis catalog (PART XIV), section processing ledger (PART XV), and execution
readiness verdict (PART XVI). All 46 deliverables embedded. Supersedes v2.0.*
*authoritative_plan: C:/Users/prora/.claude/plans/iterative-mixing-shannon.md*
*supporting_artifacts: all analysis content embedded in this file; no external plan documents*
*execution_authority: TRUE*
