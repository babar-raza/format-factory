# Playbook System — Complete Healing, Integration, and Idempotent Closure
# Plan: bright-marinating-map (revised — current-state reassessment 2026-07-01)
# Type: machinery_hardening
# Mission ID: FF-PLAYBOOK-SYSTEM-001

---

## A. Current-State Reassessment

### What changed since the original plan was written

The original plan was written with all 12 taskcards OPEN. This reassessment verifies current system state before any execution begins.

### What was verified

| Artifact | Expected by plan | Actual state | Verdict |
|---------|-----------------|--------------|---------|
| `reports/playbooks/` directory | populated | DOES NOT EXIST | Nothing from TC-PB-001 through TC-PB-003 produced |
| `playbooks/playbook-registry.yaml` | exists | DOES NOT EXIST | TC-PB-011 unresolved |
| `tools/playbook/generate_playbook_taskcards.py` | exists | DOES NOT EXIST | TC-PB-007 unresolved |
| `tools/playbook/playbook_selector.py` | exists | DOES NOT EXIST | TC-PB-008 unresolved |
| `tools/playbook/playbook_execution_log.py` | exists | DOES NOT EXIST | TC-PB-008 unresolved |
| `schemas/playbook/playbook-task-binding.schema.json` | exists | DOES NOT EXIST | TC-PB-007 unresolved |
| Playbook skills in `.supervisor/skill-registry.yaml` | 7 skills | ZERO — none registered | TC-PB-005 unresolved |
| Markdown templates YAML front-matter | present | ABSENT — files begin with `# Playbook:` heading only | TC-PB-004 unresolved |
| `acquisition-packs/_families/odf-flat/playbook.yaml` status | active | `status: proposed` | TC-PB-004 unresolved |
| V86-V93 governance validators (original plan) | new | **COLLISION — V86 through V91 ARE ALREADY IN USE** | CRITICAL DEFECT in original plan |
| `tools/governance/governance_validators_ext2.py` (original plan) | modify | **DOES NOT EXIST** — correct path: `tools/supervisor/governance_validators_ext2.py` | CRITICAL DEFECT in original plan |
| `tests/playbook/test_taskcard_generation.py` vs `test_task_generation.py` | one file | Two different names used in TC-PB-007 vs TC-PB-009 | Name inconsistency in original plan |

### What already exists (foundation — not partial completions)

| Item | Confirmed present |
|------|-----------------|
| `tools/playbook/validate_playbook.py` | YES (S-F2F-02 CLOSED) |
| `tools/playbook/replay_acquisition_playbook.py` | YES (code exists; policy says "unauthorized" — stale) |
| `tools/playbook/export_review_queue.py` | YES |
| `tools/playbook/diff_playbook_outputs.py` | YES |
| `tools/playbook/create_golden_case.py` | YES |
| `schemas/playbook/acquisition-playbook.schema.json` | YES (S-F2F-01 CLOSED) |
| `schemas/playbook/review-queue.schema.json` | YES |
| 8 existing test modules in `tests/playbook/` | YES (cover S-F2F schema/replay/diff tools) |
| 3 Markdown templates in `playbooks/format-factory/` | YES (no YAML front-matter) |
| `acquisition-packs/_families/odf-flat/playbook.yaml` | YES (status: proposed) |
| Current highest governance validator: **V91** | YES (governance_validators_root_struct.py) |

### Critical defects in original plan — corrected in this revision

| Defect | Original | Corrected |
|--------|---------|-----------|
| V-number collision | Proposed V86-V93 (V86-V91 already taken) | Use **V92-V99** |
| Wrong file path | `tools/governance/governance_validators_ext2.py` (DOES NOT EXIST) | `tools/supervisor/governance_validators_ext2.py` |
| Test file name inconsistency | TC-PB-007: `test_taskcard_generation.py`; TC-PB-009: `test_task_generation.py` | Canonical: **`test_task_generation.py`** |

---

## B. Item-by-Item Status

| Taskcard | Status | Evidence |
|----------|--------|---------|
| TC-PB-001 Inventory + Consumer Graph | **CLOSED** | reports/playbooks/playbook-system-inventory.yaml + playbook-consumer-graph.yaml |
| TC-PB-002 Authority Model Decision | **CLOSED** | reports/playbooks/playbook-authority-decision.yaml — Model C selected |
| TC-PB-003 Quality Audit + Disposition | **CLOSED** | reports/playbooks/playbook-quality-audit.yaml |
| TC-PB-004 Contract Hardening | **CLOSED** | YAML front-matter added to all 6 templates; odf-flat status=active |
| TC-PB-005 Skill Registry Integration | **CLOSED** | 7 playbook skills registered in .supervisor/skill-registry.yaml |
| TC-PB-006 Coverage Universe + Backfill | **CLOSED** | reports/playbooks/playbook-coverage-universe.yaml; 3 new templates created |
| TC-PB-007 Taskcard Integration Model | **CLOSED** | tools/playbook/generate_playbook_taskcards.py; schemas/playbook/playbook-task-binding.schema.json |
| TC-PB-008 Supervisor Integration | **CLOSED** | tools/playbook/playbook_selector.py; tools/playbook/playbook_execution_log.py |
| TC-PB-009 Validators + Tests | **CLOSED** | V92-V99 in governance_validators_ext2.py; 7 new test files (217 pass) |
| TC-PB-010 Pilots 1-8 | **CLOSED** | .local/evidences/playbook-pilots-20260701/ (8 pilot files; FAILED_REQUIRED_PILOTS=0) |
| TC-PB-011 Registry + Documentation | **CLOSED** | playbooks/playbook-registry.yaml; AGENTS.md §AA; GOVERNANCE.md §20; docs updated |
| TC-PB-012 Second-Pass Idempotency | **CLOSED** | reports/playbooks/idempotency-report.yaml; MATERIAL_SECOND_RUN_CHANGES=0; 217 pass |

**All 12 taskcards CLOSED. PLAYBOOK_SYSTEM_RECONCILED_INTEGRATED_PROVEN_AND_IDEMPOTENT.**

---

## Context

The repository has two overlapping "playbook" systems:

**Layer A — Markdown Sprint Templates** (`playbooks/format-factory/`): 3 files declaring `skill_id` internally — NOT in skill registry, NOT consumed at runtime.

**Layer B — Acquisition Playbook System** (`schemas/playbook/`, `tools/playbook/`, `tests/playbook/`): S-F2F-01/02 CLOSED (schemas + validator exist). S-F2F-03/04 tools exist in code but are marked "unauthorized" — stale state.

**Core problems:** Ambiguous authority, missing skill registration, no taskcard generation, no drift guards, no coverage reporters, S-F2F-03 stale authorization status.

---

## Taskcard Status Table

| TC-ID | Title | Status |
|---|---|---|
| TC-PB-001 | Inventory + Consumer Graph | CLOSED |
| TC-PB-002 | Authority Model Decision | CLOSED |
| TC-PB-003 | Quality Audit + Disposition | CLOSED |
| TC-PB-004 | Contract Hardening | CLOSED |
| TC-PB-005 | Skill Registry Integration | CLOSED |
| TC-PB-006 | Coverage Universe + Backfill | CLOSED |
| TC-PB-007 | Taskcard Integration Model | CLOSED |
| TC-PB-008 | Supervisor Integration | CLOSED |
| TC-PB-009 | Validators + Tests | CLOSED |
| TC-PB-010 | Pilots 1-8 | CLOSED |
| TC-PB-011 | Registry + Documentation | CLOSED |
| TC-PB-012 | Second-Pass Idempotency | CLOSED |

## Taskcard Closure Summary (machine-readable)

| TC-ID | Status |
|---|---|
| TC-PB-001 | CLOSED |
| TC-PB-002 | CLOSED |
| TC-PB-003 | CLOSED |
| TC-PB-004 | CLOSED |
| TC-PB-005 | CLOSED |
| TC-PB-006 | CLOSED |
| TC-PB-007 | CLOSED |
| TC-PB-008 | CLOSED |
| TC-PB-009 | CLOSED |
| TC-PB-010 | CLOSED |
| TC-PB-011 | CLOSED |
| TC-PB-012 | CLOSED |

---

## TC-PB-001 — Inventory + Consumer Graph

**Goal:** Produce machine-readable inventory of every playbook artifact.

**Inputs (all confirmed present at HEAD):**
- `playbooks/` (3 Markdown templates + `_readme.md`)
- `schemas/playbook/` (2 JSON schemas)
- `tools/playbook/` (5 Python tools + `__init__.py`)
- `tests/playbook/` (8 test modules)
- `acquisition-packs/_families/odf-flat/playbook.yaml`
- `docs/examples/acquisition-playbook-fods-documentation-example.yaml`
- `docs/governance/playbook-layer.md`
- `AGENTS.md §AA`
- `GOVERNANCE.md`
- `.supervisor/skill-registry.yaml`
- `tools/evidence/contracts/secondary-sf2f01-playbook-schema-policy.yaml`
- `tools/evidence/contracts/secondary-sf2f02-playbook-validation.yaml`

**Outputs:**
- `reports/playbooks/playbook-system-inventory.yaml` — per artifact: path, format, purpose, owner_layer, status, consumers, findings
- `reports/playbooks/playbook-consumer-graph.yaml` — per consumer: classification, playbooks_used, runtime_proof, findings

**Consumer classification vocabulary:**
`DIRECT_RUNTIME_CONSUMER` | `TASK_GENERATION_CONSUMER` | `SUPERVISOR_EXECUTION_CONSUMER` | `VALIDATION_CONSUMER` | `SKILL_OR_COMMAND_CONSUMER` | `GOVERNANCE_REFERENCE` | `DOCUMENTATION_REFERENCE` | `FALSE_OR_INFLATED_CONSUMER_CLAIM`

**Key expected findings:**
- FALSE_OR_INFLATED_CONSUMER_CLAIM for any report citing `playbooks/format-factory/` as runtime consumers
- DOCUMENTATION_REFERENCE for AGENTS.md and GOVERNANCE.md references
- No DIRECT_RUNTIME_CONSUMER for any playbook tool in supervisor pipeline
- S-F2F-03 tools exist but policy marks "unauthorized" → stale state to reconcile

**Required counter:** UNINVENTORIED_PLAYBOOK_ARTIFACTS = 0

**Verification:** Both YAML files exist and are valid. FALSE_DIRECT_PLAYBOOK_CONSUMER_CLAIMS counter is explicit.

---

## TC-PB-002 — Authority Model Decision

**Goal:** Produce binding architecture decision selecting one canonical model.

**Depends on:** TC-PB-001

**Model: MODEL C — SEPARATE SCOPED LAYERS**
- `playbooks/format-factory/` Markdown files → reclassified as **Sprint Task Templates** (not "playbooks")
- YAML acquisition playbooks → canonical **Playbook** system
- Word "playbook" reserved for YAML layer going forward

**Output:** `reports/playbooks/playbook-authority-decision.yaml`

**Required counter:** AMBIGUOUS_PLAYBOOK_AUTHORITIES = 0

**Verification:** Decision document exists. Update `playbooks/_readme.md` to reflect reclassification.

---

## TC-PB-003 — Quality Audit + Disposition

**Goal:** Audit every playbook artifact; assign disposition.

**Depends on:** TC-PB-001, TC-PB-002

**Output:** `reports/playbooks/playbook-quality-audit.yaml`

**Pre-determined dispositions:**

| Artifact | Disposition |
|---------|-------------|
| `format-feature-expansion.md` | CONVERT_TO_CANONICAL_CONTRACT — add YAML front-matter, register as skill |
| `new-format-kickstart-template.md` | CONVERT_TO_CANONICAL_CONTRACT — add YAML front-matter, register as skill |
| `product-source-task-template.md` | CONVERT_TO_CANONICAL_CONTRACT — add YAML front-matter, register as skill, update import table |
| `odf-flat/playbook.yaml` | RETAIN_AND_HARDEN — advance to active |
| `docs/examples/...fods-documentation-example.yaml` | RETAIN — schema validation fixture only |
| `validate_playbook.py` | RETAIN_AND_HARDEN — add skill registry entry |
| `replay_acquisition_playbook.py` | AUTHORIZE with limitations: dry-run only, no file writes, no gate authority |
| `export_review_queue.py` | RETAIN — add skill registry entry |
| `diff_playbook_outputs.py` | RETAIN — add skill registry entry |
| `create_golden_case.py` | RETAIN — test fixture tool; audit scope only |

**Verification:** Every artifact has a disposition. No status is "unknown."

---

## TC-PB-004 — Contract Hardening

**Goal:** Add machine-readable YAML front-matter to Markdown templates. Advance odf-flat playbook to active.

**Depends on:** TC-PB-003

**For each Markdown template** — add block at TOP of file (before `# Playbook:` heading):
```yaml
# playbook_contract:
#   playbook_id: <id>
#   title: "<title>"
#   version: "1.1"
#   status: ACTIVE
#   category: sprint_task_template
#   owner_layer: product_source
#   authority: TASK_TEMPLATE
#   required_inputs: [...]
#   required_skills: [...]
#   allowed_paths: ["src/python/<format>/", "tests/python/<format>/", "examples/python/<format>/", "reports/"]
#   forbidden_paths: ["src/net/", "poc-targets.yaml", "registry/", "AGENTS.md", "GOVERNANCE.md"]
#   validation: [min_tests_per_function, governance_validators_pass]
#   evidence_requirements: [test_results, changed_files, import_proof]
#   rollback: "Revert source change; remove test; update __all__ and __init__.py"
#   stop_conditions: [no_stdlib_only, external_dep_required, installed_format_breaks]
#   limitations: ["No gate approval authority", "No evidence contract replacement", "Sprint task templates only"]
```

Adapt `playbook_id`, `title`, `required_inputs`, `required_skills` per template.

**For `acquisition-packs/_families/odf-flat/playbook.yaml`:**
- Change `status: proposed` → `status: active`
- Add `last_verified_revision: <current HEAD>`

**Files to modify:**
- `playbooks/format-factory/format-feature-expansion.md`
- `playbooks/format-factory/new-format-kickstart-template.md`
- `playbooks/format-factory/product-source-task-template.md`
- `acquisition-packs/_families/odf-flat/playbook.yaml`

**Verification:** Each Markdown file has machine-readable YAML block at top. ACTIVE_PLAYBOOKS_WITHOUT_COMPLETE_CONTRACTS = 0.

---

## TC-PB-005 — Skill Registry Integration

**Goal:** Register 7 playbook skills in `.supervisor/skill-registry.yaml`.

**Depends on:** TC-PB-004

**Current state: ZERO playbook skills registered (confirmed by grep).**

**Skills to add:**

| Skill | Target |
|-------|--------|
| `/validate-playbook` | `tools/playbook/validate_playbook.py` — READ-ONLY schema validator; PASS ≠ gate approval |
| `/replay-acquisition-playbook` | `tools/playbook/replay_acquisition_playbook.py` — dry-run only; no file writes; informational |
| `/export-review-queue` | `tools/playbook/export_review_queue.py` |
| `/diff-playbook-outputs` | `tools/playbook/diff_playbook_outputs.py` |
| `/format-feature-expansion` | `playbooks/format-factory/format-feature-expansion.md` |
| `/new-format-kickstart` | `playbooks/format-factory/new-format-kickstart-template.md` |
| `/product-source-task` | `playbooks/format-factory/product-source-task-template.md` |

**File to modify:** `.supervisor/skill-registry.yaml`

**Verification:** All 7 skills in registry. `detect-duplicate-skills` shows no conflicts.

---

## TC-PB-006 — Coverage Universe + Backfill

**Goal:** Map recurring workflows against playbook coverage. Create 3 new templates for high-value gaps.

**Depends on:** TC-PB-005

**Output:** `reports/playbooks/playbook-coverage-universe.yaml`

**Coverage analysis:**

| Workflow | Coverage | Action |
|---------|----------|--------|
| new format acquisition | COVERED_UNPROVEN (new-format-kickstart) | Register as skill, pilot |
| format feature expansion | COVERED_UNPROVEN (format-feature-expansion) | Register as skill, pilot |
| product source implementation | COVERED_UNPROVEN (product-source-task) | Register as skill, pilot |
| spec/SAL ingestion | REPLACE_WITH_SKILL (`/ingest-spec-sal` exists) | No playbook needed |
| test promotion | REPLACE_WITH_SKILL (`add-roundtrip-test` exists) | No playbook needed |
| package/release readiness | **MISSING_HIGH_VALUE** | Backfill |
| pipeline incident response | **MISSING_HIGH_VALUE** | Backfill |
| audit/healing sprint | **MISSING_HIGH_VALUE** | Backfill |

**Backfill targets (follow canonical contract format from TC-PB-004):**
1. `playbooks/format-factory/package-release-readiness.md`
2. `playbooks/format-factory/audit-healing-sprint.md`
3. `playbooks/format-factory/pipeline-incident-response.md`

**Required counter:** HIGH_VALUE_RECURRING_WORKFLOWS_WITHOUT_DISPOSITION = 0

---

## TC-PB-007 — Taskcard Integration Model

**Goal:** Implement playbook → taskcard generation with provenance binding.

**Depends on:** TC-PB-004, TC-PB-006

**Deliverables:**

1. **`tools/playbook/generate_playbook_taskcards.py`**
   - Inputs: playbook_path (Markdown with YAML front-matter), plan_id, gap_ids, parameters
   - Outputs: list of bounded taskcard dicts with provenance
   - Each taskcard: playbook_id, playbook_version, plan_id, gap_ids, phase, required_skills, validation, evidence_root, rollback, allowed_paths, forbidden_paths
   - Strictly DOES NOT: approve gates, mark work complete, override plan authority

2. **`tests/playbook/test_task_generation.py`** ← CANONICAL NAME
   - valid params → bounded tasks
   - missing required params → fail
   - allowed/forbidden paths preserved
   - provenance in every task
   - rollback included

3. **`schemas/playbook/playbook-task-binding.schema.json`**

**Required counter:** PLAYBOOK_GENERATED_TASKS_WITHOUT_PROVENANCE = 0

---

## TC-PB-008 — Supervisor Integration

**Goal:** Wire playbook selection into supervisor pipeline (best-effort, non-blocking).

**Depends on:** TC-PB-005, TC-PB-007

**Deliverables:**

1. **`tools/playbook/playbook_selector.py`**
   - Input: work item type, format, task classification
   - Output: applicable playbook path (or None — not failure)
   - `FORMAT_FEATURE_EXPANSION` → `format-feature-expansion.md`
   - `NEW_FORMAT_KICKSTART` → `new-format-kickstart-template.md`
   - `PRODUCT_SOURCE_PATCH_BOUNDED` → `product-source-task-template.md`
   - `ACQUISITION_*` → check `acquisition-packs/_families/`
   - Rejects deprecated playbooks; returns None when no match

2. **`tools/playbook/playbook_execution_log.py`**
   - Records: execution_id, playbook_id, version, taskcards, steps, evidence quality, verdict
   - Writes to `.local/playbook-executions/<execution_id>.yaml`

3. **Supervisor hook in `tools/supervisor/autonomous_cycle.py`** (best-effort, never blocks):
   - After next work item selected: optionally invoke `playbook_selector.py`
   - If found: log, validate, extract constraints
   - If not found or validation fails: log warning, continue

**Reject conditions (log + continue, never block):** deprecated playbook; missing skill (create gap); gate-authority violation attempt.

---

## TC-PB-009 — Validators + Tests

**Goal:** Add drift guards V92-V99 and 7 new test files.

**Depends on:** TC-PB-007, TC-PB-008

### CORRECTED V-NUMBERS (from reassessment)

**DO NOT use V86-V93. V86 through V91 are already in use:**
- V86: `validate_task_register_cross_reference` (governance_validators_layers.py)
- V87: `validate_readme_freshness` (governance_validators_ext2.py)
- V88: `validate_certification_reports_exist` (governance_validators_ext2.py)
- V89: `validate_certification_matrix_consistent` (governance_validators_ext2.py)
- V90: `validate_plans_root_policy` (governance_validators_ext2.py)
- V91: `validate_root_structure` (governance_validators_root_struct.py)

**New validators use V92-V99. Target file: `tools/supervisor/governance_validators_ext2.py`**

| Validator | V-number |
|-----------|----------|
| `validate_playbook_registry_entries` — active entry resolves to file | **V92** |
| `validate_playbook_has_version` — active playbook has version field | **V93** |
| `validate_playbook_has_owner` — active playbook has owner_layer | **V94** |
| `validate_playbook_has_evidence_contract` — active playbook has evidence_requirements | **V95** |
| `validate_playbook_has_rollback` — active playbook has rollback field | **V96** |
| `validate_playbook_not_overriding_gate` — playbook includes gate-override prohibition | **V97** |
| `validate_playbook_has_no_deprecated_paths` — stale path check vs filesystem | **V98** |
| `validate_playbook_coverage_report_current` — coverage universe newer than playbook files | **V99** |

### New test files (additive — existing 8 test modules unchanged)

- `tests/playbook/test_authority_constraints.py` — cannot contain gate logic; plan/gap authority required
- `tests/playbook/test_registry.py` — active entry resolves; missing file fails; deprecated rejected; version mismatch detected
- `tests/playbook/test_rendering.py` — front-matter parses; drift detected; repeated parsing stable
- `tests/playbook/test_task_generation.py` — from TC-PB-007; valid params; provenance; paths; rollback
- `tests/playbook/test_supervisor_integration.py` — FORMAT_FEATURE_EXPANSION → correct playbook; unknown type → None; deprecated rejected; missing skill → gap not block
- `tests/playbook/test_coverage.py` — high-value gap detected; low-value not forced; duplicate detected
- `tests/playbook/test_idempotency.py` — repeated operations produce same output

**Verification:** V92-V99 pass. No V-number collision. 7 new test files created.

---

## TC-PB-010 — Pilots 1-8

**Goal:** Prove system end-to-end.

**Depends on:** TC-PB-001 through TC-PB-009

**Evidence root:** `.local/evidences/playbook-pilots-<run-id>/`

| Pilot | Target | Deliverable |
|-------|--------|-------------|
| P1 | `format-feature-expansion.md` on TSV or NDJSON; prove skill invocable, taskcard bounded | `pilot-1-evidence.yaml` |
| P2 | `new-format-kickstart-template.md` on fake format "test-format-xyz"; prove stop conditions enforced | `pilot-2-evidence.yaml` |
| P3 | `product-source-task-template.md` on bounded product feature; prove supervisor integration logged | `pilot-3-evidence.yaml` |
| P4 | `odf-flat/playbook.yaml` via validate + replay --mode dry-run + export-review-queue; prove PASS ≠ gate approval | `pilot-4-evidence.yaml` |
| P5 | Controlled failure: remove required skill; prove gap created, system repaired, execution resumes | `pilot-5-evidence.yaml` |
| P6 | Mark template DEPRECATED; prove selector rejects, no taskcard; restore after | `pilot-6-evidence.yaml` |
| P7 | Create `audit-healing-sprint.md`; run coverage audit — gap disappears; run end-to-end | `pilot-7-evidence.yaml` |
| P8 | Run all operations twice; compare checksums; MATERIAL_SECOND_RUN_CHANGES = 0 | `pilot-8-idempotency-report.yaml` |

**Required counter:** FAILED_REQUIRED_PILOTS = 0

---

## TC-PB-011 — Registry + Documentation

**Goal:** Create canonical playbook registry. Update AGENTS.md, GOVERNANCE.md, docs.

**Depends on:** TC-PB-010 (pilots must pass before registry is finalized)

**Create `playbooks/playbook-registry.yaml`:**
```yaml
playbook_registry:
  version: "1.0"
  generated_at: <timestamp>
  entries:
    - playbook_id: format-feature-expansion
      title: "Add Feature to Existing Python FOSS Format Codec"
      version: "1.1"
      status: ACTIVE
      category: sprint_task_template
      canonical_path: playbooks/format-factory/format-feature-expansion.md
      owner_layer: product_source
      authority: TASK_TEMPLATE
      supported_workflows: [FORMAT_FEATURE_EXPANSION]
      required_skills: [add-python-api, add-roundtrip-test]
      tests: [tests/playbook/test_task_generation.py]
      pilots: [pilot-1]
      last_verified_revision: <HEAD>
    # repeat for all 7+ active entries
```

**Files to update:**
- `playbooks/_readme.md` — rename "playbooks" to "Sprint Task Templates"
- `docs/governance/playbook-layer.md` — add Model C section; update S-F2F phase statuses
- `AGENTS.md §AA` — S-F2F-03 NOW authorized (Pilot 4 proves it); Sprint Task Templates are separate layer
- `GOVERNANCE.md` — Model C decision
- `tools/supervisor/autonomous_cycle.py` — doc comment referencing `playbook_selector.py`

**Verification:** Registry exists and is valid YAML. 7+ entries. AGENTS.md/GOVERNANCE.md reflect Model C.

---

## TC-PB-012 — Second-Pass Idempotency Verification

**Goal:** Confirm zero material changes on second run.

**Depends on:** TC-PB-011

**Steps:**
1. Run `generate_playbook_taskcards.py` on each template with same inputs
2. Regenerate `coverage-universe.yaml`
3. Regenerate `playbook-registry.yaml`
4. Run `docs/governance/playbook-layer.md` sync check
5. Run all 15 tests (`tests/playbook/`) — 8 existing + 7 new
6. Compute SHA-256 of all generated output files
7. Repeat steps 1-5
8. Compare checksums

**Output:** `reports/playbooks/idempotency-report.yaml`

**Required counter:** MATERIAL_SECOND_RUN_CHANGES = 0

---

## Files Modified Summary

**New files:**
```
reports/playbooks/playbook-system-inventory.yaml
reports/playbooks/playbook-consumer-graph.yaml
reports/playbooks/playbook-authority-decision.yaml
reports/playbooks/playbook-quality-audit.yaml
reports/playbooks/playbook-coverage-universe.yaml
reports/playbooks/idempotency-report.yaml
playbooks/playbook-registry.yaml
playbooks/format-factory/package-release-readiness.md
playbooks/format-factory/audit-healing-sprint.md
playbooks/format-factory/pipeline-incident-response.md
tools/playbook/generate_playbook_taskcards.py
tools/playbook/playbook_selector.py
tools/playbook/playbook_execution_log.py
schemas/playbook/playbook-task-binding.schema.json
tests/playbook/test_authority_constraints.py
tests/playbook/test_registry.py
tests/playbook/test_rendering.py
tests/playbook/test_task_generation.py
tests/playbook/test_supervisor_integration.py
tests/playbook/test_coverage.py
tests/playbook/test_idempotency.py
.local/evidences/playbook-pilots-<run-id>/ (8 pilot evidence files)
```

**Modified files:**
```
playbooks/_readme.md
playbooks/format-factory/format-feature-expansion.md       (add YAML front-matter)
playbooks/format-factory/new-format-kickstart-template.md  (add YAML front-matter)
playbooks/format-factory/product-source-task-template.md   (add YAML front-matter)
acquisition-packs/_families/odf-flat/playbook.yaml         (advance to active)
.supervisor/skill-registry.yaml                            (add 7 skills)
tools/supervisor/governance_validators_ext2.py             (add V92-V99)   ← CORRECTED PATH
tools/supervisor/autonomous_cycle.py                       (add playbook hook)
docs/governance/playbook-layer.md
AGENTS.md (§AA)
GOVERNANCE.md
```

---

## Completion Gate Counters

| Counter | Target |
|---|---|
| UNINVENTORIED_PLAYBOOK_ARTIFACTS | 0 |
| FALSE_DIRECT_PLAYBOOK_CONSUMER_CLAIMS | 0 |
| AMBIGUOUS_PLAYBOOK_AUTHORITIES | 0 |
| ACTIVE_PLAYBOOKS_WITHOUT_COMPLETE_CONTRACTS | 0 |
| HIGH_VALUE_RECURRING_WORKFLOWS_WITHOUT_DISPOSITION | 0 |
| PLAYBOOK_GENERATED_TASKS_WITHOUT_PROVENANCE | 0 |
| DEPRECATED_PLAYBOOKS_STILL_EXECUTABLE | 0 |
| PLAYBOOKS_OVERRIDING_GATE_OR_PLAN_AUTHORITY | 0 |
| FAILED_REQUIRED_PILOTS | 0 |
| MATERIAL_SECOND_RUN_CHANGES | 0 |

**Final verdict target:** PLAYBOOK_SYSTEM_RECONCILED_INTEGRATED_PROVEN_AND_IDEMPOTENT

---

## Execution Order

```
TC-PB-001 → TC-PB-002 → TC-PB-003 → TC-PB-004 → TC-PB-005 → TC-PB-006
                                                              ↓
                                        TC-PB-007 (depends on 004, 006)
                                                              ↓
                                        TC-PB-008 (depends on 005, 007)
                                                              ↓
                                        TC-PB-009 (depends on 007, 008)
                                                              ↓
                                        TC-PB-010 (depends on 001-009)
                                                              ↓
                                        TC-PB-011 (depends on 010)
                                                              ↓
                                        TC-PB-012 (depends on 011)
```


<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-07-01T12:26:05.189702+00:00"
  locked_by: "34c4217ef0bd"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
