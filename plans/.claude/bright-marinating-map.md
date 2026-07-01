# Playbook System — Complete Healing, Integration, and Idempotent Closure
# Plan: bright-marinating-map
# Type: machinery_hardening
# Mission ID: FF-PLAYBOOK-SYSTEM-001

## Context

The format-factory repository contains two overlapping systems both called "playbooks":

**Layer A — Markdown Sprint Templates** (`playbooks/format-factory/`):
- 3 Markdown files: `format-feature-expansion.md`, `new-format-kickstart-template.md`, `product-source-task-template.md`
- Declare `skill_id` fields internally (e.g., `format-feature-expansion` v1.0)
- NOT registered in `.supervisor/skill-registry.yaml`
- NOT consumed by any Python tool at runtime
- NOT validated by any automated tooling
- Referenced in sprint reports as "3 reusable playbooks" but only as documentation references
- Classification: DOCUMENTATION/GUIDANCE

**Layer B — Acquisition Playbook System** (schemas/playbook/, tools/playbook/, tests/playbook/):
- S-F2F-01 CLOSED: `schemas/playbook/acquisition-playbook.schema.json` + `review-queue.schema.json` + `docs/governance/playbook-layer.md`
- S-F2F-02 CLOSED: `tools/playbook/validate_playbook.py` (READ-ONLY schema validator)
- S-F2F-03/04 tools EXIST in code (`replay_acquisition_playbook.py`, `export_review_queue.py`, `create_golden_case.py`, `diff_playbook_outputs.py`) but are documented as "PENDING/unauthorized"
- 8 test modules + fixtures + golden files in `tests/playbook/`
- `acquisition-packs/_families/odf-flat/playbook.yaml` — proposed family playbook
- `docs/examples/acquisition-playbook-fods-documentation-example.yaml` — documentation example only
- Classification: SCHEMA + TOOLS + GOVERNANCE (acquisition pipeline layer)

**Core Problems:**
1. Both systems use the word "playbook" — ambiguous authority, overlapping terminology
2. Markdown templates declare skill IDs but are not in skill registry → cannot be invoked as skills
3. No taskcard generation from either playbook layer
4. No supervisor integration — playbooks cannot route or generate work
5. S-F2F-03 replay tools exist in code but policy documents them as "unauthorized" — state is stale
6. No drift guards, no coverage reporters, no idempotent regeneration
7. No canonical playbook registry
8. Coverage gaps: spec/SAL ingestion, audit/healing sprint, package readiness, pipeline incident response have no playbook support

**Intended Outcome:**
- Single unambiguous authority model for "playbooks" (Markdown templates reclassified; YAML layer is canonical)
- All active playbook tools registered as skills
- Playbooks generate bounded governed taskcards with provenance
- Supervisor can select and execute playbooks
- Validators prevent drift and detect coverage gaps
- 8 pilots prove the system end-to-end
- Second run produces zero material changes

---

## Taskcard Status Table

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

**Goal:** Produce machine-readable inventory of every playbook artifact and classify every reference.

**Inputs:**
- `playbooks/` (all files)
- `schemas/playbook/` (2 JSON schemas)
- `tools/playbook/` (5 Python tools + __init__.py)
- `tests/playbook/` (8 test modules, 8 fixtures, 8 golden files)
- `acquisition-packs/_families/odf-flat/playbook.yaml`
- `docs/examples/acquisition-playbook-fods-documentation-example.yaml`
- `docs/governance/playbook-layer.md`
- AGENTS.md §AA (lines 641-676)
- GOVERNANCE.md (lines 291-316)
- `plans/master-plan.md` (line 3654 reference)
- `.supervisor/skill-registry.yaml`
- `tools/evidence/contracts/secondary-sf2f01-playbook-schema-policy.yaml`
- `tools/evidence/contracts/secondary-sf2f02-playbook-validation.yaml`

**Outputs:**
- `reports/playbooks/playbook-system-inventory.yaml` — per-artifact: artifact_id, path, format, title, purpose, owner_layer, status, version, producer, consumers, referenced_by, validated_by, executed_by, generated_outputs, active, stale, findings
- `reports/playbooks/playbook-consumer-graph.yaml` — per consumer: consumer_id, path, classification (DIRECT_RUNTIME_CONSUMER / TASK_GENERATION_CONSUMER / SUPERVISOR_EXECUTION_CONSUMER / VALIDATION_CONSUMER / SKILL_OR_COMMAND_CONSUMER / GOVERNANCE_REFERENCE / REPORT_OR_EVIDENCE_REFERENCE / DOCUMENTATION_REFERENCE / HISTORICAL_REFERENCE / FALSE_OR_INFLATED_CONSUMER_CLAIM), playbooks_used, invocation_method, inputs, outputs, runtime_proof, current, failure_behavior, findings

**Key expected findings to confirm:**
- FALSE_OR_INFLATED_CONSUMER_CLAIM for all reports citing playbooks/format-factory/ as runtime consumers
- DOCUMENTATION_REFERENCE for all AGENTS.md and GOVERNANCE.md references
- No DIRECT_RUNTIME_CONSUMER entries for any playbook tool in supervisor pipeline
- S-F2F-03 tools exist in code but NOT authorized per policy → state is stale

**Required counter:** UNINVENTORIED_PLAYBOOK_ARTIFACTS = 0

**Verification:** `reports/playbooks/playbook-system-inventory.yaml` and `playbook-consumer-graph.yaml` exist and are valid YAML. FALSE_DIRECT_PLAYBOOK_CONSUMER_CLAIMS counter is explicit and justified. FALSE_OR_INFLATED_CONSUMER_CLAIM items identified.

---

## TC-PB-002 — Authority Model Decision

**Goal:** Select one canonical architecture model and produce a binding decision document.

**Inputs:**
- TC-PB-001 outputs
- `docs/governance/playbook-layer.md` (existing governance policy)
- AGENTS.md §AA
- GOVERNANCE.md playbook sections

**Recommended Model: MODEL C — SEPARATE SCOPED LAYERS (with explicit disambiguation)**

Rationale:
- `playbooks/format-factory/` Markdown files should be reclassified as **Sprint Task Templates** (not "playbooks") — they are agent skill execution guides, not structured acquisition replay artifacts
- YAML acquisition playbooks (schemas/playbook/, tools/playbook/) remain the governed **Playbook** system with strict authority boundaries
- The word "playbook" is reserved exclusively for the YAML acquisition layer going forward
- Sprint Task Templates in `playbooks/format-factory/` get registered as skills but are not called playbooks in any new documentation

**Decision document fields:**
- model_selected: MODEL_C_SEPARATE_SCOPED_LAYERS
- markdown_layer_reclassification: SPRINT_TASK_TEMPLATES (not "playbooks")
- yaml_layer_canonical_name: ACQUISITION_PLAYBOOKS
- authority_boundary: YAML layer is canonical machine artifact; Markdown templates are agent execution guidance
- ambiguity_resolution: rename/reclassify Markdown files as "templates" or "skill templates" in all future references
- forbidden: using "playbook" to describe Markdown operational templates; calling templates execution authority

**Output:** `reports/playbooks/playbook-authority-decision.yaml`

**Required counter:** AMBIGUOUS_PLAYBOOK_AUTHORITIES = 0

**Verification:** Decision document exists, AMBIGUOUS_PLAYBOOK_AUTHORITIES = 0. Update `playbooks/_readme.md` to reflect reclassification (call them "Sprint Task Templates" not "playbooks").

---

## TC-PB-003 — Quality Audit + Disposition

**Goal:** Audit every playbook artifact for relevance, correctness, completeness, and recommended action.

**Inputs:** TC-PB-001/002 outputs, each playbook file content

**Per-artifact audit (produce `reports/playbooks/playbook-quality-audit.yaml`):**

For `playbooks/format-factory/format-feature-expansion.md`:
- Current use: DOCUMENTATION_REFERENCE (sprint reports cite it; no runtime consumption)
- Missing contract fields: machine-readable identity, validation, evidence contract, stop conditions, rollback, version (Markdown-declared; not machine-parseable)
- Duplicate with: product-source-task-template.md (overlapping scope for bounded source changes)
- Recommended action: CONVERT_TO_CANONICAL_CONTRACT — register as skill, add machine-readable header YAML block, harden validation rules and stop conditions
- Stale paths: check current format paths still match src/python/ structure

For `playbooks/format-factory/new-format-kickstart-template.md`:
- Current use: DOCUMENTATION_REFERENCE
- Missing: machine-readable identity, validation, evidence contract, stop conditions, rollback
- Recommended action: CONVERT_TO_CANONICAL_CONTRACT — register as skill
- Known pitfalls section is valuable — preserve

For `playbooks/format-factory/product-source-task-template.md`:
- Current use: DOCUMENTATION_REFERENCE
- Import status table needs verification against current install state
- Recommended action: CONVERT_TO_CANONICAL_CONTRACT — register as skill, update import table
- Overlap with format-feature-expansion.md needs explicit scope boundary

For `acquisition-packs/_families/odf-flat/playbook.yaml`:
- Status: proposed (not active)
- Recommended action: RETAIN_AND_HARDEN — advance to active status after prerequisite checks
- Missing: pilot proof, last_verified_revision

For `docs/examples/acquisition-playbook-fods-documentation-example.yaml`:
- Status: documentation_example_only
- Recommended action: RETAIN — keep as schema validation test fixture, not for execution

For `tools/playbook/validate_playbook.py`:
- Status: ACTIVE (S-F2F-02 CLOSED)
- Recommended action: RETAIN_AND_HARDEN — add skill registry entry

For `tools/playbook/replay_acquisition_playbook.py`:
- Status: EXISTS but "unauthorized" per policy — STALE STATE
- Reality: code exists, tests exist; policy says "future"
- Recommended action: RECONCILE — either authorize with documented constraints or mark DEPRECATED and remove; do not leave as ghost code
- Decision: AUTHORIZE with explicit limitations (dry-run only, no file writes, no gate authority, no apply mode) — consistent with S-F2F-03 intent

**Output:** `reports/playbooks/playbook-quality-audit.yaml`

**Verification:** Every playbook artifact has a disposition. No artifact status is "unknown" or "deferred indefinitely without justification."

---

## TC-PB-004 — Contract Hardening

**Goal:** Convert retained Markdown sprint templates to canonical contracts. Harden YAML playbook contracts.

**For each Markdown template in `playbooks/format-factory/`:**

Add a machine-readable YAML front-matter block at top of each file with ALL required contract fields:
```yaml
# playbook_contract:
#   playbook_id: format-feature-expansion
#   title: "Add Feature to Existing Python FOSS Format Codec"
#   version: "1.1"
#   status: ACTIVE
#   category: sprint_task_template
#   owner_layer: product_source
#   authority: TASK_TEMPLATE
#   purpose: ...
#   applicability: ...
#   triggers: [...]
#   prerequisites: [...]
#   required_inputs: [format_name, codec_file, init_file, test_dir, function_name, function_signature, capability_label]
#   optional_inputs: []
#   required_skills: [add-python-api, add-roundtrip-test]
#   required_commands: []
#   allowed_paths: ["src/python/<format>/", "tests/python/<format>/", "examples/python/<format>/", "reports/"]
#   forbidden_paths: ["src/net/", "poc-targets.yaml", "registry/", "AGENTS.md", "GOVERNANCE.md"]
#   phases: [...]
#   task_types: [PRODUCT_SOURCE_PATCH_BOUNDED, FORMAT_FEATURE_EXPANSION]
#   validation: [min_tests_per_function, governance_validators_pass]
#   evidence_requirements: [test_results, changed_files, import_proof]
#   rollback: "Revert source change; remove test; update __all__ and __init__.py"
#   stop_conditions: [no_stdlib_only, external_dep_required, installed_format_breaks]
#   outputs: [modified_codec, tests, updated_all_export, evidence_declaration]
#   supersedes: []
#   examples: []
#   limitations: ["No gate approval authority", "No evidence contract replacement", "Sprint task templates only"]
```

**For `acquisition-packs/_families/odf-flat/playbook.yaml`:**
- Advance status from `proposed` to `active`
- Add `last_verified_revision` field
- Add pilot reference once TC-PB-010 Pilot 4 completes

**Files to modify:**
- `playbooks/format-factory/format-feature-expansion.md` — add contract YAML block
- `playbooks/format-factory/new-format-kickstart-template.md` — add contract YAML block
- `playbooks/format-factory/product-source-task-template.md` — add contract YAML block, update import status table
- `acquisition-packs/_families/odf-flat/playbook.yaml` — advance to active, add last_verified_revision

**Verification:** Each Markdown file has machine-readable YAML front-matter. Contract parser can extract all required fields. ACTIVE_PLAYBOOKS_WITHOUT_COMPLETE_CONTRACTS = 0.

---

## TC-PB-005 — Skill Registry Integration

**Goal:** Register all playbook tools as skills in `.supervisor/skill-registry.yaml`.

**Skills to register (not currently in registry):**
1. `/validate-playbook` → `tools/playbook/validate_playbook.py`
   - Description: Validate YAML playbook against acquisition-playbook or review-queue schema (READ-ONLY, no disk writes)
   - Inputs: playbook_path, schema (optional, auto-detected)
   - Outputs: PASS/FAIL/ERROR report
   - Authority: Evidence aid only — PASS does not approve gates

2. `/replay-acquisition-playbook` → `tools/playbook/replay_acquisition_playbook.py`
   - Description: Dry-run replay of acquisition playbook (no file writes, informational only)
   - Inputs: playbook_path, mode (validate/dry-run/explain/export-review-queue)
   - Outputs: replay report or review queue YAML
   - Authority: Informational only — replay does NOT satisfy DEC-034 or approve gates

3. `/export-review-queue` → `tools/playbook/export_review_queue.py`
   - Description: Export review queue YAML from dry-run replay report
   - Inputs: replay_report_path, output_path
   - Outputs: review queue YAML

4. `/diff-playbook-outputs` → `tools/playbook/diff_playbook_outputs.py`
   - Description: Compare two dry-run replay reports (read-only diff)
   - Inputs: report_a, report_b, output (optional)
   - Outputs: diff YAML

5. Register Markdown template skill IDs (already declared in files, just not in registry):
   - `/format-feature-expansion` → `playbooks/format-factory/format-feature-expansion.md`
   - `/new-format-kickstart` → `playbooks/format-factory/new-format-kickstart-template.md`
   - `/product-source-task` → `playbooks/format-factory/product-source-task-template.md`

**File to modify:** `.supervisor/skill-registry.yaml`

**Verification:** All 7 skills appear in skill registry. `/inventory-skills` or equivalent can discover them. `detect-duplicate-skills` shows no conflicts.

---

## TC-PB-006 — Coverage Universe + Backfill

**Goal:** Map all recurring workflows against playbook coverage. Backfill only high-value gaps.

**Output:** `reports/playbooks/playbook-coverage-universe.yaml`

**Coverage analysis (per mission §9 workflow classes):**

| Workflow | Existing Playbook | Coverage | Action |
|---|---|---|---|
| new format acquisition | `new-format-kickstart-template.md` | COVERED_UNPROVEN | Register as skill, run pilot |
| format feature expansion | `format-feature-expansion.md` | COVERED_UNPROVEN | Register as skill, run pilot |
| product source implementation | `product-source-task-template.md` | COVERED_UNPROVEN | Register as skill, run pilot |
| spec/SAL ingestion | `/ingest-spec-sal` skill exists | REPLACE_WITH_SKILL | Already a skill — no separate playbook needed |
| capability gap closure | Supervisor gap system | REPLACE_WITH_POLICY | gap-ledger system handles this |
| test promotion | `add-roundtrip-test` skill | REPLACE_WITH_SKILL | Already a skill |
| package/release readiness | No playbook | MISSING_HIGH_VALUE | Backfill — recurring, bounded, verifiable |
| documentation/content generation | `sync-readmes` skill | REPLACE_WITH_SKILL | Already covered |
| pipeline incident response | No playbook | MISSING_HIGH_VALUE | Backfill — recurring incident pattern |
| dependency resolution | No playbook | NOT_WORTH_PLAYBOOK | Too varied; policy sufficient |
| cross-language parity | `spec-parity-verification` skill | REPLACE_WITH_SKILL | Already a skill |
| product hardening | `plan-hardening` skill | REPLACE_WITH_SKILL | Already a skill |
| backfill/migration | Ad-hoc sprints | NOT_WORTH_PLAYBOOK | Too format-specific |
| audit/healing sprint | No playbook | MISSING_HIGH_VALUE | Backfill — recurring, stable sequence |

**Backfill targets (3 high-value gaps):**
1. `playbooks/format-factory/package-release-readiness.md` — release/package readiness workflow
2. `playbooks/format-factory/audit-healing-sprint.md` — audit/healing sprint workflow
3. `playbooks/format-factory/pipeline-incident-response.md` — pipeline incident response

**Anti-patterns to avoid:**
- Do NOT create per-format playbooks (parameterize instead)
- Do NOT create a playbook for every workflow class (use skills/policies where adequate)
- Do NOT create playbooks without proven recurring value

**Required counter:** HIGH_VALUE_RECURRING_WORKFLOWS_WITHOUT_DISPOSITION = 0

**Verification:** Coverage universe YAML exists. Each workflow has disposition. 3 new backfill templates created following canonical contract format. No disposition is "UNKNOWN."

---

## TC-PB-007 — Taskcard Integration Model

**Goal:** Define and implement how playbooks generate bounded governed taskcards with provenance.

**Deliverables:**

1. **`tools/playbook/generate_playbook_taskcards.py`** — new lightweight taskcard generator
   - Inputs: playbook_path (Markdown with YAML front-matter), plan_id, gap_ids, parameters
   - Outputs: list of bounded taskcard dicts with provenance
   - Each taskcard includes: playbook_id, playbook_version, plan_id, gap_ids, parameters, phase, required_skills, validation, evidence_root, rollback, allowed_paths, forbidden_paths
   - Strictly DOES NOT: approve gates, mark work complete, override plan authority
   - Writes output to specified output_path only

2. **`tests/playbook/test_taskcard_generation.py`** — tests for taskcard generator
   - valid parameters generate bounded tasks
   - missing required parameters fail
   - allowed/forbidden paths preserved in output
   - provenance (playbook_id + version) in every generated task
   - taskcard validation and rollback included

3. **Provenance binding schema** (add section to existing `schemas/playbook/acquisition-playbook.schema.json` or new `schemas/playbook/playbook-task-binding.schema.json`):
   ```yaml
   playbook_task_binding:
     binding_id: ...
     playbook_id: ...
     playbook_version: ...
     plan_id: ...
     gap_ids: []
     taskcard_id: ...
     parameters: {}
     phase: ...
     required_skills: []
     validation: ...
     evidence_root: ...
     status: ...
   ```

**Required counter:** PLAYBOOK_GENERATED_TASKS_WITHOUT_PROVENANCE = 0

**Verification:** `generate_playbook_taskcards.py` generates valid taskcards from each Markdown template. Tests pass. Every generated taskcard has playbook_id, playbook_version, plan_id, and provenance fields.

---

## TC-PB-008 — Supervisor Integration

**Goal:** Wire playbook selection, validation, and failure/heal/resume into the supervisor pipeline.

**Scope:** Integration must be BEST-EFFORT and non-blocking per Supreme Directive. Failures log and continue.

**Deliverables:**

1. **`tools/playbook/playbook_selector.py`** — lightweight selector
   - Input: work item type (from next-work-items.json), format, task classification
   - Output: applicable playbook path (or None if no match)
   - Selection logic:
     - FORMAT_FEATURE_EXPANSION → `format-feature-expansion.md`
     - NEW_FORMAT_KICKSTART → `new-format-kickstart-template.md`
     - PRODUCT_SOURCE_PATCH_BOUNDED → `product-source-task-template.md`
     - ACQUISITION_* → check `acquisition-packs/_families/` or format-specific
   - Rejects deprecated playbooks
   - Returns None (not failure) when no applicable playbook

2. **Supervisor hook in `tools/supervisor/autonomous_cycle.py`** (best-effort, non-blocking):
   - After selecting next work item, optionally invoke `playbook_selector.py`
   - If playbook found: log selected playbook, validate it, extract task constraints
   - If playbook not found: continue without playbook (not a blocker)
   - If playbook validation fails: log warning, continue
   - Integration must NEVER block autonomous continuation

3. **`tools/playbook/playbook_execution_log.py`** — execution result recorder
   - Records: execution_id, playbook_id, version, taskcards, successful/failed/skipped steps, new failure modes, unnecessary/missing steps, evidence quality, rollback used, healing actions, recommended change, verdict
   - Writes to `.local/playbook-executions/<execution_id>.yaml`
   - Learning mechanism: after execution, compare expected vs actual

**Reject conditions (log warning + continue):**
- Deprecated playbook selected
- Missing required skill (create gap, continue)
- Playbook version mismatch
- Playbook attempting gate authority

**Files to modify:**
- `tools/supervisor/autonomous_cycle.py` — add optional playbook hook (best-effort)
- New: `tools/playbook/playbook_selector.py`
- New: `tools/playbook/playbook_execution_log.py`

**Verification:** Supervisor logs playbook selection when applicable. Playbook validation failure does NOT stop sprint. Missing skill creates gap (not hard failure). Second run produces same selection.

---

## TC-PB-009 — Validators + Tests

**Goal:** Add drift guards, coverage validators, and all required test categories.

**Validators to add (new governance validator entries):**

1. `validate_playbook_registry_entries` (V86) — active entry must resolve to file
2. `validate_playbook_has_version` (V87) — active playbook must have version field
3. `validate_playbook_has_owner` (V88) — active playbook must have owner_layer
4. `validate_playbook_has_evidence_contract` (V89) — active playbook must have evidence_requirements
5. `validate_playbook_has_rollback` (V90) — active playbook must have rollback field
6. `validate_playbook_not_overriding_gate` (V91) — playbook must include gate-override prohibition
7. `validate_playbook_has_no_deprecated_paths` (V92) — stale paths check against actual filesystem
8. `validate_playbook_coverage_report_current` (V93) — coverage universe report must be newer than playbook files

**New tests to add:**

In `tests/playbook/test_authority_constraints.py`:
- playbook cannot contain gate approval logic
- plan/gap authority required for task generation
- taskcard remains execution authority

In `tests/playbook/test_registry.py`:
- active entry resolves to file
- missing file fails validation
- deprecated entry rejected by selector
- version mismatch detected

In `tests/playbook/test_rendering.py`:
- contract front-matter parses consistently
- Markdown/YAML front-matter drift detected
- repeated parsing is stable

In `tests/playbook/test_task_generation.py`:
- valid parameters generate bounded tasks (moved from TC-PB-007)
- missing required parameters fail
- allowed/forbidden paths preserved
- provenance preserved
- task validation and rollback included in output

In `tests/playbook/test_supervisor_integration.py`:
- applicable playbook selected for FORMAT_FEATURE_EXPANSION work item
- unknown work item type returns None (not failure)
- deprecated playbook rejected
- missing skill creates gap, does not block

In `tests/playbook/test_coverage.py`:
- high-value workflow gap detected when playbook missing
- low-value workflow does NOT force playbook creation
- duplicate playbook detected

In `tests/playbook/test_idempotency.py`:
- repeated registry generation produces same output
- repeated front-matter parsing produces same output
- repeated task generation produces same output
- repeated coverage audit produces same output
- repeated execution reconciliation produces same output

**Files to modify:**
- `tools/governance/governance_validators_ext2.py` — add V86-V93
- New test files listed above

**Verification:** All new validators (V86-V93) have tests that PASS. All idempotency tests confirm zero material changes on second run.

---

## TC-PB-010 — Pilots 1-8

**Goal:** Prove the playbook system end-to-end through 8 required pilots.

**Evidence root:** `.local/evidences/playbook-pilots-<run-id>/`

### Pilot 1 — Existing Markdown Playbook (format-feature-expansion)
- Use `format-feature-expansion.md` on a safe bounded format
- Prove: contract front-matter parseable, skill invocable via registry, bounded taskcard generated, execution through registered skill, evidence and closeout
- Format target: Use TSV or NDJSON (non-editable install OK — safe to test with)
- Deliverable: pilot-1-evidence.yaml

### Pilot 2 — New-Format Kickstart
- Use `new-format-kickstart-template.md` on a disposable test fixture (not a real format)
- Prove: prerequisites check, task decomposition, stop conditions enforced, no gate-authority violation
- Use a fake format like "test-format-xyz" in an isolated test tree
- Deliverable: pilot-2-evidence.yaml

### Pilot 3 — Product-Source Task
- Use `product-source-task-template.md` on one bounded product feature
- Prove: source paths correct, tests pass, rollback path documented, meaningful verification, supervisor integration logged
- Target: small bounded function on a known-stable format
- Deliverable: pilot-3-evidence.yaml

### Pilot 4 — YAML Acquisition Playbook (odf-flat family)
- Use `acquisition-packs/_families/odf-flat/playbook.yaml`
- Run `validate_playbook.py` → PASS
- Run `replay_acquisition_playbook.py --mode dry-run` → PASS (authorize S-F2F-03 tools)
- Run `export_review_queue.py` → review queue YAML
- Prove: replay behavior, relationship to Markdown templates clarified, PASS does not imply gate approval
- Deliverable: pilot-4-evidence.yaml

### Pilot 5 — Failure/Heal/Resume
- Introduce controlled failure: remove a required skill from registry temporarily
- Prove: execution stops (logs warning), gap created in `.local/playbook-executions/`, system repaired (skill restored), only reusable lesson encoded if applicable, execution resumes
- Deliverable: pilot-5-evidence.yaml

### Pilot 6 — Deprecated Playbook Rejection
- Mark one template as DEPRECATED in front-matter
- Prove: `playbook_selector.py` rejects it, no taskcard generated, clear rejection logged
- Restore after pilot
- Deliverable: pilot-6-evidence.yaml

### Pilot 7 — Coverage Gap
- Select `audit-healing-sprint` as the high-value workflow without sufficient playbook support
- Create `playbooks/format-factory/audit-healing-sprint.md` with canonical contract
- Run coverage audit — gap disappears
- Run pilot end-to-end (one audit-healing bounded taskcard generated and verified)
- Deliverable: pilot-7-evidence.yaml

### Pilot 8 — Idempotency
- Run: registry generation, contract front-matter parsing, coverage audit, task generation, execution reconciliation, documentation sync
- Record all output hashes
- Run same sequence again
- Verify: zero material second-run changes (MATERIAL_SECOND_RUN_CHANGES = 0)
- Deliverable: pilot-8-idempotency-report.yaml

**Required counter:** FAILED_REQUIRED_PILOTS = 0

---

## TC-PB-011 — Registry + Documentation

**Goal:** Create canonical playbook registry. Update all documentation.

**Create `playbooks/playbook-registry.yaml`:**
```yaml
playbook_registry:
  version: "1.0"
  generated_at: ...
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
      last_verified_revision: ...
      superseded_by: null
    # ... repeat for all active playbooks
```

**Documentation updates:**
- `playbooks/_readme.md` — rename section from "playbooks" to "Sprint Task Templates"; clarify not acquisition playbooks; point to registry
- `docs/governance/playbook-layer.md` — add section on Sprint Task Template layer (Model C disambiguation); update S-F2F phase statuses
- `AGENTS.md §AA` — update to reflect: (1) S-F2F-03 tools are NOW authorized (Pilot 4 proves it); (2) Sprint Task Templates in playbooks/ are separate layer from acquisition playbooks; (3) new skills registered
- `GOVERNANCE.md` — update playbook section with canonical authority model decision
- Supervisor routing (comment in `autonomous_cycle.py`) — reference `playbook_selector.py`

**Files to modify:**
- `playbooks/_readme.md`
- `docs/governance/playbook-layer.md`
- `AGENTS.md` (§AA, lines 641-676)
- `GOVERNANCE.md` (lines 291-316)
- `tools/supervisor/autonomous_cycle.py` (comment/doc update)
- New: `playbooks/playbook-registry.yaml`

**Verification:** Registry exists and is valid YAML. All 7+ playbook entries present. AGENTS.md and GOVERNANCE.md reflect Model C decision. `playbooks/_readme.md` no longer ambiguously calls templates "playbooks."

---

## TC-PB-012 — Second-Pass Idempotency Verification

**Goal:** Run all generation, registry, coverage audit, rendering, and sync operations twice. Confirm zero material changes.

**Steps:**
1. Run `tools/playbook/generate_playbook_taskcards.py` on each template with same inputs
2. Run coverage audit (derive coverage-universe.yaml)
3. Run `playbook-registry.yaml` regeneration
4. Run `docs/governance/playbook-layer.md` sync check
5. Run all playbook tests (`tests/playbook/`)
6. Compute MD5/SHA of all generated output files
7. Repeat steps 1-5
8. Compare checksums

**Output:** `reports/playbooks/idempotency-report.yaml`
- Per operation: operation, first_run_hash, second_run_hash, material_change
- Final counter: MATERIAL_SECOND_RUN_CHANGES

**Required counter:** MATERIAL_SECOND_RUN_CHANGES = 0

**Verification:** idempotency-report.yaml shows all hashes match. MATERIAL_SECOND_RUN_CHANGES = 0.

---

## Files Modified Summary

**New files:**
- `reports/playbooks/playbook-system-inventory.yaml`
- `reports/playbooks/playbook-consumer-graph.yaml`
- `reports/playbooks/playbook-authority-decision.yaml`
- `reports/playbooks/playbook-quality-audit.yaml`
- `reports/playbooks/playbook-coverage-universe.yaml`
- `reports/playbooks/playbook-system-healing-report.md`
- `reports/playbooks/idempotency-report.yaml`
- `playbooks/playbook-registry.yaml`
- `playbooks/format-factory/package-release-readiness.md`
- `playbooks/format-factory/audit-healing-sprint.md`
- `playbooks/format-factory/pipeline-incident-response.md`
- `tools/playbook/generate_playbook_taskcards.py`
- `tools/playbook/playbook_selector.py`
- `tools/playbook/playbook_execution_log.py`
- `schemas/playbook/playbook-task-binding.schema.json`
- `tests/playbook/test_authority_constraints.py`
- `tests/playbook/test_registry.py`
- `tests/playbook/test_rendering.py`
- `tests/playbook/test_task_generation.py`
- `tests/playbook/test_supervisor_integration.py`
- `tests/playbook/test_coverage.py`
- `tests/playbook/test_idempotency.py`
- `.local/evidences/playbook-pilots-<run-id>/` (8 pilot evidence files)

**Modified files:**
- `playbooks/_readme.md` — reclassify templates, point to registry
- `playbooks/format-factory/format-feature-expansion.md` — add contract YAML front-matter
- `playbooks/format-factory/new-format-kickstart-template.md` — add contract YAML front-matter
- `playbooks/format-factory/product-source-task-template.md` — add contract YAML front-matter, update import table
- `acquisition-packs/_families/odf-flat/playbook.yaml` — advance to active
- `.supervisor/skill-registry.yaml` — add 7 playbook skills
- `tools/governance/governance_validators_ext2.py` — add V86-V93
- `tools/supervisor/autonomous_cycle.py` — add best-effort playbook hook
- `docs/governance/playbook-layer.md` — update S-F2F phase statuses, add Model C disambiguation
- `AGENTS.md` — update §AA (S-F2F-03 authorized, Sprint Task Templates clarified)
- `GOVERNANCE.md` — update playbook section with Model C decision

---

## Completion Gate Counters

| Counter | Target |
|---|---|
| UNINVENTORIED_PLAYBOOK_ARTIFACTS | 0 |
| FALSE_DIRECT_PLAYBOOK_CONSUMER_CLAIMS | 0 |
| AMBIGUOUS_PLAYBOOK_AUTHORITIES | 0 |
| ACTIVE_PLAYBOOKS_WITHOUT_COMPLETE_CONTRACTS | 0 |
| ACTIVE_PLAYBOOKS_WITHOUT_PROVEN_PURPOSE | 0 |
| HIGH_VALUE_RECURRING_WORKFLOWS_WITHOUT_DISPOSITION | 0 |
| PLAYBOOK_GENERATED_TASKS_WITHOUT_PROVENANCE | 0 |
| DEPRECATED_PLAYBOOKS_STILL_EXECUTABLE | 0 |
| PLAYBOOKS_OVERRIDING_GATE_OR_PLAN_AUTHORITY | 0 |
| MATERIAL_PLAYBOOK_FINDINGS_WITHOUT_GAPS | 0 |
| READY_PLAYBOOK_GAPS_WITHOUT_TASKCARDS | 0 |
| FAILED_REQUIRED_PILOTS | 0 |
| MATERIAL_SECOND_RUN_CHANGES | 0 |

**Final verdict target:** PLAYBOOK_SYSTEM_RECONCILED_INTEGRATED_PROVEN_AND_IDEMPOTENT

---

## Execution Order (per mission §20)

1. TC-PB-001 (inventory + consumer graph)
2. TC-PB-002 (authority decision)
3. TC-PB-003 (quality audit + disposition)
4. TC-PB-004 (contract hardening)
5. TC-PB-005 (skill registry integration)
6. TC-PB-006 (coverage universe + backfill)
7. TC-PB-007 (taskcard integration model)
8. TC-PB-008 (supervisor integration)
9. TC-PB-009 (validators + tests)
10. TC-PB-010 (pilots 1-8)
11. TC-PB-011 (registry + documentation)
12. TC-PB-012 (second-pass idempotency)


<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-07-01T12:10:50.774127+00:00"
  locked_by: "34c4217ef0bd"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
