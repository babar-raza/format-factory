# Playbook Validation Engine Hardening + Pilot Re-execution
# Plan: playbook-vhrd-001
# Type: machinery_hardening
# Mission ID: FF-PLAYBOOK-VHRD-001
# Parent: FF-PLAYBOOK-SYSTEM-001 (bright-marinating-map — TERMINAL_CLOSED)
# Supersedes: bright-marinating-map.md (this file is now the active plan)

## Context

Pilot rerun comparison (r001→r005) identified two unresolved gaps that were incorrectly
classified as "by design" or "low risk":

**Gap 1 — System Python → fallback_structural (NOT by design)**
Root causes (confirmed via source inspection):
- `jsonschema` is NOT listed in pyproject.toml at all — not even in optional-dependencies
- `validation_commands` in `acquisition-packs/_families/odf-flat/playbook.yaml` uses `python`
  (no `--engine` flag) → auto-detection silently falls back forever, regardless of Python env
- The tool exits 0 when falling back — no signal to CI or calling code that compliance is degraded
- Claims about "documenting use of .venv/Scripts/python" are insufficient: the embedded
  self-validation command does NOT document this and will silently PASS on any environment
  without jsonschema

**Gap 2 — Pilots 2, 3, 5 weakly verified (NOT safe to skip)**
- Pilot 2 (new-format-kickstart): taskcard artifact exists but step evidence is stated, not logged
- Pilot 3 (product-source-task): same — step claims are assertions, not captured command output
- Pilot 5 (failure/heal/resume): explicitly labeled "simulated" in evidence; execution log has
  contradictory state (write_tests in BOTH successful_phases and failed_phases); recovery cycle
  is not proven by real tool invocation
- Pilots 6, 7: genuinely proven real execution — no re-run needed

**Intended Outcome:**
- jsonschema is a documented optional dependency (pip install format-factory[validation])
- odf-flat validation_commands explicitly uses --engine jsonschema (fails loudly when not installed)
- Pilots 2, 3, 5 re-executed with real tool output captured as evidence (not stated claims)
- r006 idempotency confirms MATERIAL_SECOND_RUN_CHANGES = 0

## Mission Binding

```yaml
mission_binding:
  mission_id: FF-PLAYBOOK-VHRD-001
  parent_mission_id: FF-PLAYBOOK-SYSTEM-001
  repository: c:/Users/prora/OneDrive/Documents/GitHub/format-factory
  branch: main
  plan_path: plans/.claude/playbook-vhrd-001.md
  plan_id: playbook-vhrd-001
  source_of_authority: BOUND_CREATED_PLAN
  mandatory_outcomes:
    - jsonschema documented in pyproject.toml optional-dependencies
    - odf-flat validation_commands uses --engine jsonschema
    - Pilot 2 re-executed with real command output in evidence
    - Pilot 3 re-executed with real command output in evidence
    - Pilot 5 executed for real (not simulated)
    - MATERIAL_SECOND_RUN_CHANGES = 0 (r006)
  non_goals:
    - Changing the auto-engine fallback behavior in validate_playbook.py
    - Making jsonschema a hard (non-optional) dependency
    - Re-executing Pilots 1, 4, 6, 7, 8 (already proven in r001/r004/r005)
  confidence: HIGH
```

## Taskcard Status Table

| TC-ID | Status |
|---|---|
| TC-VH-001 | CLOSED |
| TC-VH-002 | CLOSED |
| TC-VH-003 | CLOSED |
| TC-VH-004 | CLOSED |
| TC-VH-005 | CLOSED |
| TC-VH-006 | CLOSED |

---

## TC-VH-001 — Document jsonschema in pyproject.toml

**Status:** OPEN
**Priority:** HIGH (foundational — unblocks tool dependency clarity)
**Lane:** machinery/deps

**Root cause:** `jsonschema` is imported with a bare `try/except ImportError` and is not
listed anywhere in pyproject.toml. Users and CI cannot `pip install format-factory` and
expect jsonschema to be available.

**Required work:**

Edit `pyproject.toml` — add to `[project.optional-dependencies]`:
```toml
validation = [
    "jsonschema>=4.0.0",
]
```

This allows `pip install format-factory[validation]` and documents that jsonschema is
required for full JSON Schema compliance checking (vs structural fallback).

**File to modify:** `pyproject.toml`

**Required verification:**
```
grep -A3 "validation" pyproject.toml | grep jsonschema
→ must show jsonschema>=4.0.0

.venv/Scripts/python -c "import importlib.metadata; print(importlib.metadata.requires('format-factory'))"
→ must include jsonschema conditional on [validation] extra
```

**Acceptance criteria:**
- `[project.optional-dependencies]` has `validation = ["jsonschema>=4.0.0"]`
- `pip install -e .[validation]` would install jsonschema
- No existing dependency entries changed

**Rollback:** Remove the `validation` key from `[project.optional-dependencies]`

---

## TC-VH-002 — Fix odf-flat validation_commands to enforce jsonschema engine

**Status:** OPEN
**Priority:** HIGH
**Lane:** acquisition-packs
**Dependencies:** TC-VH-001 (so the error message refers to the correct install command)

**Root cause:** `acquisition-packs/_families/odf-flat/playbook.yaml` `validation_commands`
uses `python ... --kind acquisition-playbook` with NO `--engine` flag. Auto-detection
silently falls back to `fallback_structural` on any Python without jsonschema. The embedded
command always exits 0, giving false confidence in "PASS" regardless of engine.

**Required work:**

Edit `acquisition-packs/_families/odf-flat/playbook.yaml` `validation_commands[0]`:
- Add `--engine jsonschema` to the command
- Update `purpose` to explain the intent
- Update `notes` field to state the install requirement

**Result:** If jsonschema is not installed, the command exits with:
```
ENGINE_ERROR: --engine jsonschema requested but jsonschema is not installed.
Install with: pip install format-factory[validation]  OR  use --engine structural
```
Exit code: non-zero (currently: exits 0 regardless of engine).

Wait — need to verify: does `--engine jsonschema` without jsonschema exit non-zero?

Looking at the source (lines 506-518 of validate_playbook.py):
```python
elif engine == ENGINE_JSONSCHEMA:
    if not JSONSCHEMA_AVAILABLE:
        return False, ["ENGINE_ERROR: ..."], {...}
```
→ Returns `passed=False` → exits 1.

So adding `--engine jsonschema` makes the embedded command fail loudly when jsonschema
is missing, instead of silently passing with degraded validation.

**File to modify:** `acquisition-packs/_families/odf-flat/playbook.yaml`

**Required verification:**
```
grep -A6 "validation_commands:" acquisition-packs/_families/odf-flat/playbook.yaml | grep "engine jsonschema"
→ must show --engine jsonschema

.venv/Scripts/python tools/playbook/validate_playbook.py \
  --schema schemas/playbook/acquisition-playbook.schema.json \
  --input acquisition-packs/_families/odf-flat/playbook.yaml \
  --kind acquisition-playbook --engine jsonschema
→ exits 0, engine=jsonschema, errors=[]
```

**Acceptance criteria:**
- `--engine jsonschema` appears in the embedded validation command
- Running with `.venv/Scripts/python`: exits 0, engine=jsonschema
- Running with system Python (no jsonschema): exits 1, ENGINE_ERROR in output

---

## TC-VH-003 — Re-execute Pilot 2 with captured output (new-format-kickstart)

**Status:** OPEN
**Priority:** MEDIUM
**Lane:** pilots
**Dependencies:** none

**Root cause:** Pilot 2 (r001) evidence states "PASS" for steps like
`contract_front_matter_parseable` and `prerequisite_check` but does NOT capture actual
command stdout/stderr. Evidence is stated assertion, not logged execution output.

**Required work:**

1. Run: `python tools/playbook/generate_playbook_taskcards.py \
   --playbook playbooks/format-factory/new-format-kickstart-template.md \
   --plan-id FF-PILOT-R006 \
   --parameters format_name=test_xyz file_extensions=.txyz format_spec_ref=none detection_signature=magic_bytes stdlib_module=json`
2. Capture full stdout (first 40 lines) in evidence
3. Verify: PASS header, 7 taskcards, `playbook_version='1.1'`, `no_gate_approval=true`
4. Run a second time with same params → confirm structural hash matches (idempotency)

**Output:** `.local/evidences/playbook-pilots-r006/pilot-2-evidence.yaml`

**Required fields in evidence:**
- `engine_output_sample`: first 30 lines of actual stdout
- `taskcard_count`: must be 7
- `playbook_version`: must be 1.1
- `no_gate_approval_per_taskcard`: true
- `r001_vs_r006_taskcard_count_match`: true
- `idempotency_hash_match`: true

**Acceptance criteria:**
- Evidence contains actual tool stdout (not stated claims)
- taskcard_count=7, version=1.1, all no_gate_approval=true

---

## TC-VH-004 — Re-execute Pilot 3 with captured output (product-source-task)

**Status:** OPEN
**Priority:** MEDIUM
**Lane:** pilots
**Dependencies:** none

**Root cause:** Same as TC-VH-003. Pilot 3 (r001) evidence states supervisor_integration_logged
and scope_boundary_clarified without showing actual invocation output from
`playbook_selector.py` or `generate_playbook_taskcards.py`.

**Required work:**

1. Run: `python tools/playbook/generate_playbook_taskcards.py \
   --playbook playbooks/format-factory/product-source-task-template.md \
   --plan-id FF-PILOT-R006 \
   --parameters format_name=tsv function_name=get_tsv_metadata function_signature="(path: str) -> dict" capability_label=tsv_metadata`
2. Capture full stdout (first 40 lines)
3. Verify: PASS header, 8 taskcards, `playbook_version='1.1'`, `no_gate_approval=true`
4. Run selector explicitly: `python -c "from tools.playbook.playbook_selector import select_playbook; print(select_playbook('PRODUCT_SOURCE_PATCH_BOUNDED'))"`
5. Capture selector output in evidence

**Output:** `.local/evidences/playbook-pilots-r006/pilot-3-evidence.yaml`

**Required fields:**
- `generator_output_sample`: actual stdout
- `taskcard_count`: 8
- `selector_output`: actual selector stdout showing the selected path
- `no_gate_approval_per_taskcard`: true

**Acceptance criteria:**
- Evidence contains actual command output (not stated claims)
- taskcard_count=8, all no_gate_approval=true, selector returns product-source-task path

---

## TC-VH-005 — Execute Pilot 5 for Real (failure/heal/resume — not simulated)

**Status:** OPEN
**Priority:** HIGH (the r001 evidence is contradictory — write_tests in both success and failure)
**Lane:** pilots
**Dependencies:** none

**Root cause:** Pilot 5 (r001) evidence says "Simulated: required skill 'add-python-api'
unavailable." The execution log (EXEC-B46DBDFD.yaml) has write_tests in BOTH
`successful_phases` and `failed_phases` — contradictory state proves it was synthetic.
The actual failure/heal/resume cycle was never executed.

**What the pilot must prove (real execution):**
1. **Failure introduction:** Temporarily modify `.supervisor/skill-registry.yaml` to rename
   `add-python-api` to `add-python-api-DISABLED` (or remove it)
2. **Failure detection:** Run `generate_playbook_taskcards.py` on `format-feature-expansion.md`
   — it must log a WARNING about missing required skill
3. **Gap creation:** Confirm warning is logged (or gap YAML written to `.local/`)
4. **Restoration:** Restore `add-python-api` in registry
5. **Resume:** Re-run generator after restoration — PASS, all taskcards generated, no warnings
6. **Contradictory-state test:** Confirm the execution log does NOT have the same phase in
   both successful_phases and failed_phases

**Implementation note:** Use `generate_playbook_taskcards.py` which validates required_skills
against the registry (line ~100 in the tool). The tool should warn when a required skill is
missing from the registry, not hard-fail.

If the generator does NOT currently check required_skills against the registry:
- Add the check (or confirm it exists) FIRST
- The check should: log WARNING, continue generation, include `missing_skills` in output
- This is the minimum viable implementation for the pilot to be meaningful

**Output:** `.local/evidences/playbook-pilots-r006/pilot-5-evidence.yaml`

**Required fields:**
- `failure_phase`: actual stdout showing missing-skill warning
- `registry_state_before`: skill count before removal
- `registry_state_after_removal`: skill count with skill removed
- `registry_state_after_restore`: skill count restored
- `resume_result`: PASS with all taskcards after restoration
- `contradictory_state_test`: confirms no phase appears in both success and failure lists

**Acceptance criteria:**
- Actual stdout captured for failure and resume steps
- registry modified, warning logged, registry restored
- No contradictory phase state in execution log
- Non-simulated: the word "Simulated" does NOT appear in evidence

---

## TC-VH-006 — r006 Idempotency + Full Pilot Suite Verdict

**Status:** OPEN
**Priority:** MEDIUM
**Lane:** pilots
**Dependencies:** TC-VH-003, TC-VH-004, TC-VH-005

**Goal:** Confirm MATERIAL_SECOND_RUN_CHANGES=0 after all TC-VH work.

**Steps:**
1. Run TC-VH-003 operations twice → compare structural hashes
2. Run TC-VH-004 operations twice → compare structural hashes
3. Verify odf-flat validation (TC-VH-002) still exits 0 with jsonschema engine
4. Run full playbook test suite → 225+ PASS, 0 FAIL

**Output:** `.local/evidences/playbook-pilots-r006/pilot-8-idempotency-report.yaml`

**Required counter:** MATERIAL_SECOND_RUN_CHANGES = 0

---

## Files to Modify

| File | TC | Change |
|---|---|---|
| `pyproject.toml` | TC-VH-001 | Add `[project.optional-dependencies] validation = ["jsonschema>=4.0.0"]` |
| `acquisition-packs/_families/odf-flat/playbook.yaml` | TC-VH-002 | Add `--engine jsonschema` to validation_commands |
| `plans/.claude/playbook-vhrd-001.md` | all | In-repo copy of this plan |
| `.local/evidences/playbook-pilots-r006/` | TC-VH-003..006 | Evidence files |

## Proof Matrix

| TC | Proof Level | Evidence Required |
|---|---|---|
| TC-VH-001 | 2 (focused validation) | grep in pyproject.toml, pip install dry-run |
| TC-VH-002 | 3 (real execution) | actual venv Python stdout showing jsonschema engine |
| TC-VH-003 | 3 (real execution) | captured tool stdout in evidence YAML |
| TC-VH-004 | 3 (real execution) | captured tool stdout + selector output in evidence YAML |
| TC-VH-005 | 3 (real execution) | actual registry modification + tool warning + restoration + resume |
| TC-VH-006 | 3 (real execution) | hash match, test count, 0 fail |

## Adversarial Controls

- Pilot 5 evidence must NOT contain the word "Simulated"
- Execution log must NOT have any phase in both successful_phases and failed_phases
- Test suite must be run with `.venv/Scripts/pytest`, not system Python
- odf-flat validation_commands must fail with system Python after TC-VH-002 (prove the change works)

## Completion Gate Counters

| Counter | Target |
|---|---|
| JSONSCHEMA_UNDOCUMENTED_IN_PYPROJECT | 0 |
| VALIDATION_COMMANDS_WITHOUT_ENGINE_SPEC | 0 |
| PILOTS_WITH_SIMULATED_OR_STATED_EVIDENCE | 0 |
| CONTRADICTORY_EXECUTION_LOG_STATE | 0 |
| MATERIAL_SECOND_RUN_CHANGES | 0 |

<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  reason: "TC-VH-001..006 not yet executed"
  locked_at: "2026-07-02"
  mutation_policy: "close TC-VH-001..006 then run lifecycle_audit + write_plan_lock --terminal --audit-gate"
-->

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
- S-F2F-01 CLOSED: `schemas/playbook/acquisition-playbook.schema.json` + `review-queue.schema.json` + `docs/playbook-layer.md`
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
| TC-PB-013 | CLOSED |
| TC-PB-014 | CLOSED |
| TC-PB-015 | CLOSED |
| TC-VS-001 | CLOSED |
| TC-VS-002 | CLOSED |
| TC-VS-003 | CLOSED |
| TC-VS-004 | CLOSED |
| TC-VS-005 | CLOSED |

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
- `docs/playbook-layer.md`
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
- `docs/playbook-layer.md` (existing governance policy)
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
- `tools/governance/governance_validators_ext2.py` — add V92-V99 (plan originally listed V86-V93; actual implementation is V92-V99)
- New test files listed above

**Verification:** All new validators (V92-V99) have tests that PASS. All idempotency tests confirm zero material changes on second run.

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
- `docs/playbook-layer.md` — add section on Sprint Task Template layer (Model C disambiguation); update S-F2F phase statuses
- `AGENTS.md §AA` — update to reflect: (1) S-F2F-03 tools are NOW authorized (Pilot 4 proves it); (2) Sprint Task Templates in playbooks/ are separate layer from acquisition playbooks; (3) new skills registered
- `GOVERNANCE.md` — update playbook section with canonical authority model decision
- Supervisor routing (comment in `autonomous_cycle.py`) — reference `playbook_selector.py`

**Files to modify:**
- `playbooks/_readme.md`
- `docs/playbook-layer.md`
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
4. Run `docs/playbook-layer.md` sync check
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
- `tools/governance/governance_validators_ext2.py` — add V92-V99 (plan originally listed V86-V93; actual implementation is V92-V99)
- `tools/supervisor/autonomous_cycle.py` — add best-effort playbook hook
- `docs/playbook-layer.md` — update S-F2F phase statuses, add Model C disambiguation
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
13. TC-PB-013 (contract version bump) [follow_up]
14. TC-PB-014 (coverage report refresh) [follow_up]
15. TC-PB-015 (plan lock repair) [follow_up]

---

## Plan File Hardening Change Log

**Hardening run:** 2026-07-01 (post r002 pilot rerun)
**Source:** Assistant pilot rerun comparison (r001 vs r002) and in-session execution summary

### Sources Reviewed

- `plans/.claude/bright-marinating-map.md` (in-repo, 693 lines, plan_terminal_lock=ITERATION_REQUIRED)
- `.local/evidences/playbook-pilots-r001/` (13 files: pilot-1 through pilot-8 evidence)
- `.local/evidences/playbook-pilots-r002/pilot-8-idempotency-report.yaml`
- Assistant execution summary (r001 vs r002 before/after comparison table)
- `tests/supervisor/test_governance_validators.py` + `tests/playbook/` run result: 380 passed, 1 skipped
- `tools/supervisor/governance_validator_runner.py` (V92-V99 registration confirmed)
- `tools/governance/governance_validators_ext2.py` (V92-V99 implementations confirmed)
- `.supervisor/skill-registry.yaml` (7 playbook skills confirmed)
- `playbooks/format-factory/format-feature-expansion.md` (version 1.1, phases changed)

### Claim Audit Findings

```
claim_id: C1
exact_claim: "8 new V92-V99 governance validators registered and passing (0 FAIL)"
claimed_status: CLOSED
proof_level: 3 (integration — test runner confirmed 106 validators, 0 FAIL)
disposition: VERIFIED_AND_PRESERVE
```

```
claim_id: C2
exact_claim: "7 playbook skills now registered in .supervisor/skill-registry.yaml"
claimed_status: CLOSED
proof_level: 2 (focused validation — grep confirmed 7 entries in registry)
disposition: VERIFIED_AND_PRESERVE
```

```
claim_id: C3
exact_claim: "phase hash change is deliberate TC-PB-004 contract update, not a regression"
claimed_status: CLOSED
proof_level: 1 (assertion only — no contract version bump to signal the change)
disposition: IMPLEMENTED_NOT_VERIFIED
plan_action: TC-PB-013 — bump format-feature-expansion.md version 1.1 → 1.2
```

```
claim_id: C4
exact_claim: "MATERIAL_SECOND_RUN_CHANGES = 0"
claimed_status: CLOSED
proof_level: 3 (structural idempotency confirmed with timestamps stripped)
disposition: VERIFIED_AND_PRESERVE
note: "Volatile fields (timestamps, random binding IDs) stripped before hash comparison — correct methodology"
```

```
claim_id: C5
exact_claim: "V99 warns: coverage report older than 6 templates — non-blocking"
claimed_status: advisory
proof_level: 2 (validator confirmed WARN, blocks_sprint=False)
disposition: ACTIONABLE_GAP
plan_action: TC-PB-014 — re-run coverage audit to refresh report
```

```
claim_id: C6
exact_claim: "Plan lock ITERATION_REQUIRED from session 34c4217ef0bd"
claimed_status: contradicted
contradiction: "All 12 taskcards CLOSED, r002 confirms work done"
disposition: CONTRADICTED
plan_action: TC-PB-015 — repair plan lock to TERMINAL_CLOSED
```

```
claim_id: C7
exact_claim: "Plan says add V86-V93 but actual implementation is V92-V99"
claimed_status: stale
disposition: STALE
plan_action: CORRECTED in this hardening (both occurrences updated)
```

```
claim_id: C8
exact_claim: "Pilots 2, 3, 5, 6, 7 not re-executed in r002 rerun"
claimed_status: partial
proof_level: 2 (r001 evidence exists for all 8; r002 only reran pilots 1, 4, 8)
disposition: PARTIAL
rationale: "r001 evidence is the original proof-of-record; r002 rerun targeted the most
  structurally impactful pilots (selector routing, YAML validation, idempotency). Pilots
  2/3/5/6/7 use synthetic fixtures and deprecated-state tests that do not change between
  r001 and r002. Risk: LOW."
plan_action: NOT_REQUIRED_FOLLOW_UP (r001 evidence remains valid for stable pilots)
```

```
claim_id: C9
exact_claim: "test count: 217 (r001) → 380 (r002) (+163 tests)"
claimed_status: needs_clarification
note: "r001 baseline 217 was test_governance_validators.py ONLY. r002 380 includes
  test_governance_validators.py + tests/playbook/ (163 new playbook tests). These are
  different scopes. The increase is expected and correct — not a regression."
disposition: VERIFIED_AND_PRESERVE
```

### Contradictions Reconciled

1. **Status table vs plan lock:** All 12 TC-PB-001..012 CLOSED in status table, but
   plan_terminal_lock=ITERATION_REQUIRED. Root cause: lifecycle_audit parsed 0 taskcards
   (3-column table not parsed by regex) before table was corrected. Lock was set by a
   different session (34c4217ef0bd) with cross-session GOV_BLOCK contamination.
   Resolution: TC-PB-015 repairs the lock.

2. **V86-V93 vs V92-V99:** Plan prose said V86-V93 but implementation registered V92-V99.
   Resolution: Both occurrences corrected in this hardening.

3. **Phase content vs contract version:** TC-PB-004 hardened format-feature-expansion.md
   phases but did not bump version from 1.1. Resolution: TC-PB-013 bumps to 1.2.

### Unresolved Work Register

| Item | Taskcard | Priority | Status |
|---|---|---|---|
| Contract version not bumped after phase change | TC-PB-013 | LOW | follow_up |
| V99 WARN: coverage report stale | TC-PB-014 | LOW | follow_up |
| Plan lock stuck at ITERATION_REQUIRED | TC-PB-015 | MEDIUM | follow_up |

### Anti-Overclaim Rules (confirmed active)

- `blocks_sprint=False` on ALL V92-V99 validators — advisory only, not enforcement
- Pilot evidence marked `authority_note: "Does NOT approve gates"` in every pilot file
- Taskcard generator outputs `no_gate_approval=true` in every generated taskcard
- MATERIAL_SECOND_RUN_CHANGES=0 was proven with volatile-field stripping, not raw hash

---

## TC-PB-013 — Contract Version Bump (format-feature-expansion)

**Source finding:** C3 — contract phases changed in TC-PB-004 but version not incremented
**Status:** follow_up
**Priority:** LOW
**Lane owner:** product_source / playbook_machinery
**Dependencies:** TC-PB-004 (CLOSED)

**Why it matters:** When contract content changes (phase list changed from 6 original phases
to 6 new phases), the version field must increment so that downstream consumers (taskcard
generator, idempotency tests, execution log) can detect the change. Staying at v1.1 while
content changes violates the provenance contract and makes cross-run hash comparison ambiguous.

**Required work:**
- Edit `playbooks/format-factory/format-feature-expansion.md` YAML front-matter: change `version: "1.1"` to `version: "1.2"`
- Add a `changelog:` entry: `"1.2: TC-PB-004 hardening — phase list updated to canonical 6 phases"`
- Re-run `tests/playbook/test_rendering.py` to confirm front-matter parse stable

**Required verification:**
- `grep 'version.*1.2' playbooks/format-factory/format-feature-expansion.md` → match
- `python tools/playbook/generate_playbook_taskcards.py --playbook playbooks/format-factory/format-feature-expansion.md` → shows version=1.2 in output header
- `tests/playbook/test_rendering.py` PASS

**Required evidence:**
- Diff showing version 1.1 → 1.2 in front-matter
- generate_playbook_taskcards.py output showing version=1.2

**Proof level target:** 2 (focused validation)
**Rollback:** revert version change in front-matter

**Acceptance criteria:**
- format-feature-expansion.md front-matter version = "1.2"
- changelog entry present explaining the phase change
- test_rendering.py passes
- taskcard generator outputs version=1.2

**Exact next action:** Edit `playbooks/format-factory/format-feature-expansion.md` YAML block, change version from "1.1" to "1.2", add changelog entry.

---

## TC-PB-014 — Coverage Report Refresh

**Source finding:** C5 — V99 WARN: 6 templates newer than coverage report
**Status:** follow_up
**Priority:** LOW
**Lane owner:** playbook_machinery / governance
**Dependencies:** TC-PB-006 (CLOSED), TC-PB-009 (CLOSED)

**Why it matters:** V99 (`validate_playbook_coverage_report_current`) fires a WARN whenever
any playbook template file is newer than `reports/playbooks/playbook-coverage-universe.yaml`.
TC-PB-004 and TC-PB-006 modified templates after the coverage report was generated, leaving
6 templates marked as newer. V99 is advisory-only (`blocks_sprint=False`) but produces noise
in every governance validator run. Re-running the coverage audit silences it.

**Required work:**
- Identify the coverage audit script or generator (likely a section in TC-PB-006 outputs)
- Re-run to regenerate `reports/playbooks/playbook-coverage-universe.yaml` with current timestamps
- Confirm V99 WARN count drops to 0

**Required verification:**
- `python -c "from tools.governance.governance_validators_ext2 import validate_playbook_coverage_report_current; ..."` → PASS (not WARN)
- V99 result: PASS in governance validator run

**Required evidence:**
- Updated `reports/playbooks/playbook-coverage-universe.yaml` with timestamp newer than all templates
- Governance run output showing V99=PASS

**Proof level target:** 2 (focused validation)
**Rollback:** Not needed — coverage report is a generated artifact; old version recoverable from git

**Acceptance criteria:**
- V99 result = PASS (not WARN) in governance validator run
- Coverage universe report `generated_at` timestamp newer than newest template file

**Exact next action:** Re-run coverage audit generator, verify V99 changes from WARN to PASS.

---

## TC-PB-015 — Plan Lock Repair

**Source finding:** C6 — plan_terminal_lock=ITERATION_REQUIRED contradicts all-CLOSED status table
**Status:** follow_up
**Priority:** MEDIUM
**Lane owner:** playbook_machinery / supervisor
**Dependencies:** TC-PB-013, TC-PB-014 (these should be CLOSED first for clean closure)

**Why it matters:** The plan lock stuck at `ITERATION_REQUIRED` was set by session `34c4217ef0bd`
before: (a) the taskcard status table was reformatted to 2-column (required for lifecycle_audit
regex), and (b) the cross-session GOV_BLOCK from `validate_readme_freshness` was cleared.
While all 12 original taskcards are CLOSED and r002 confirms all work is verified,
`check_continuation.py` and `lifecycle_audit.py` will read the stale ITERATION_REQUIRED lock
and return CONTINUE — causing the session to loop on a plan that is actually complete.

**Required work:**
1. Close TC-PB-013 and TC-PB-014 (the two remaining follow-up items)
2. Run `python tools/supervisor/lifecycle_audit.py --mission-id FF-PLAYBOOK-SYSTEM-001 --sprint-id TC-PB-015`
   - Confirm it parses all 15 taskcards (2-column table)
   - Confirm audit result = AUDIT_PASS (not AUDIT_PASS_VACUOUS)
3. Run `python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/bright-marinating-map.md --terminal --audit-gate`
   - Confirm lock written as TERMINAL_CLOSED

**Required verification:**
- `lifecycle_audit.py` output shows `taskcards_parsed: 15`
- `lifecycle_audit.py` result: `AUDIT_PASS`
- `active-plan-lock.json` contains `"status": "TERMINAL_CLOSED"`
- `check_continuation.py` returns `verdict: STOP, reason: POST_PLAN_TERMINAL`

**Required evidence:**
- `.local/supervisor/lifecycle-audit-results.json` with AUDIT_PASS
- `.local/supervisor/active-plan-lock.json` with TERMINAL_CLOSED

**Proof level target:** 3 (real execution — lifecycle_audit runs against actual plan file)
**Rollback:** If audit finds unexpected OPEN items, add taskcards, do not force-close

**Acceptance criteria:**
- lifecycle_audit parses 15 taskcards (not 0 or 12)
- audit result = AUDIT_PASS
- plan lock = TERMINAL_CLOSED
- check_continuation returns POST_PLAN_TERMINAL

**Exact next action:** Close TC-PB-013 and TC-PB-014 first, then run lifecycle_audit + write_plan_lock --terminal --audit-gate.

---

---

## Hardening Addendum — JSON Schema Validation Engine (2026-07-02)

**Source finding:** Pilot rerun r002/r003 confirmed `validate_playbook.py` used `fallback_structural` engine in all pilots. Root cause: three distinct issues found during investigation.

**Root cause 1 — invocation path:** `validate_playbook.py` switches engine based on `import jsonschema` success. System Python (`python`) lacks `jsonschema`; venv Python (`.venv/Scripts/python`) has `jsonschema` 4.26.0. Pilots used system Python invocation.

**Root cause 2 — odf-flat playbook bug:** `acquisition-packs/_families/odf-flat/playbook.yaml` `validation_commands` specifies `--kind family_playbook` but `validate_playbook.py` argparse `choices=` only accepts `acquisition-playbook` or `review-queue`. This would exit 2 (argparse error), never reaching validation.

**Root cause 3 — zero jsonschema-path test coverage:** All tests in `tests/playbook/` run with default auto engine, which resolves to `fallback_structural` in CI/system contexts. No test exercises `Draft7Validator` or the schema constraints it enforces (additionalProperties: false, ID patterns, integer range, minLength, enum).

**Schema constraints active only under jsonschema engine (not structural):**
- `additionalProperties: false` at top-level and all nested objects
- `playbook_id` pattern: `^[a-z0-9][a-z0-9-]*[a-z0-9]$`
- `playbook_version` pattern: `^[0-9]+\.[0-9]+$`
- `operation_id` pattern: `^[a-z0-9][a-z0-9-]*[a-z0-9]$`
- gate_number integer range 1-11
- operation.title minLength: 5
- operation.description minLength: 10
- evidence_requirements[].artifact_type enum (6 values)

---

## TC-VS-001 — Prove odf-flat Passes Full JSON Schema Validation

**Status:** OPEN
**Source finding:** Pilot 4 evidence (all runs r001-r003) claims `PASS (fallback_structural)` — full schema compliance was never proven with jsonschema engine.

**Goal:** Execute `validate_playbook.py` against `acquisition-packs/_families/odf-flat/playbook.yaml` using venv Python and confirm PASS under jsonschema engine.

**Prerequisite:** TC-VS-002 must complete first (fix `--kind` bug, otherwise command exits 2 before validation).

**Steps:**
1. Run: `.venv/Scripts/python tools/playbook/validate_playbook.py --schema schemas/playbook/acquisition-playbook.schema.json --input acquisition-packs/_families/odf-flat/playbook.yaml --engine jsonschema`
2. Capture exit code, engine used, errors list.
3. Expected: exit 0, engine=jsonschema, errors=[].

**Output:** `.local/evidences/playbook-pilots-r004/pilot-4-evidence-jsonschema.yaml`
- Fields: pilot_id, run_id=r004, engine_used=jsonschema, exit_code=0, errors=[], jsonschema_version

**Required verification:**
- `engine_used: jsonschema` (not `fallback_structural`) in evidence
- `exit_code: 0`
- `errors: []`
- `JSONSCHEMA_AVAILABLE: true` logged by tool

**Acceptance criteria:** Pilot 4 evidence explicitly states jsonschema engine, not structural.

---

## TC-VS-002 — Fix `--kind family_playbook` Bug in odf-flat Playbook

**Status:** OPEN
**Source finding:** `acquisition-packs/_families/odf-flat/playbook.yaml` `validation_commands` specifies `--kind family_playbook` but CLI argparse rejects this with exit 2. Bug exists in all prior runs.

**Goal:** Correct `validation_commands` in odf-flat playbook so the embedded command is actually executable.

**File to modify:** `acquisition-packs/_families/odf-flat/playbook.yaml`

**Change:** In `validation_commands[0].command`, replace `--kind family_playbook` with `--kind acquisition-playbook`.

**Rationale:** `family_playbook` is a valid `playbook_kind` enum value in the schema but NOT a valid `--kind` CLI argument. The CLI `--kind` controls which schema to load (`acquisition-playbook.schema.json` vs `review-queue.schema.json`). Family playbooks use the acquisition schema. The correct CLI value is `acquisition-playbook`.

**Also update:** `validation_commands[0].notes` if present — remove any reference to `family_playbook` as a CLI argument.

**Required verification:**
- Run the corrected command with system Python: `python tools/playbook/validate_playbook.py --schema schemas/playbook/acquisition-playbook.schema.json --input acquisition-packs/_families/odf-flat/playbook.yaml --kind acquisition-playbook`
- Expected exit code: 0
- No argparse error in stderr

**Acceptance criteria:**
- `--kind family_playbook` does not appear in any `validation_commands` block in odf-flat playbook
- Corrected command exits 0 with system Python

---

## TC-VS-003 — Add jsonschema-Path Tests

**Status:** OPEN
**Source finding:** Zero tests in `tests/playbook/` exercise the jsonschema engine explicitly. Schema constraints enforced only by jsonschema (additionalProperties, patterns, ranges) are untested.

**Goal:** Add a test module that explicitly invokes `--engine jsonschema` and proves key schema constraints are enforced.

**File to create:** `tests/playbook/test_jsonschema_engine.py`

**Test cases (minimum 6):**

1. `test_odf_flat_passes_jsonschema_engine` — odf-flat playbook against jsonschema engine → exit 0, engine=jsonschema
2. `test_playbook_id_pattern_rejected` — playbook with `playbook_id: "INVALID_UPPER"` → jsonschema engine raises error with "playbook_id" in message (structural passes this silently)
3. `test_unknown_top_level_field_rejected` — playbook with extra field `unknown_field: true` → jsonschema engine rejects (`additionalProperties: false`), structural passes silently
4. `test_gate_number_out_of_range_rejected` — gate with `gate_number: 0` or `gate_number: 12` → jsonschema engine rejects, structural passes silently
5. `test_operation_title_too_short_rejected` — operation with `title: "X"` (1 char < minLength: 5) → jsonschema engine rejects
6. `test_invalid_artifact_type_rejected` — evidence_requirement with `artifact_type: "not_a_real_type"` → jsonschema engine rejects enum

**Fixtures:** Use minimal valid playbook dict from existing test helpers; mutate per test case.

**Engine invocation pattern:** Call `validate_playbook` Python API directly with `engine="jsonschema"`, not via subprocess.

**Skip condition:** `@pytest.mark.skipif(not JSONSCHEMA_AVAILABLE, reason="jsonschema not installed")`

**Required verification:** All 6 tests PASS in venv context (`.venv/Scripts/pytest tests/playbook/test_jsonschema_engine.py`).

**Acceptance criteria:** `test_jsonschema_engine.py` exists, 6+ tests, all PASS in venv.

---

## TC-VS-004 — Negative Control: Extra Fields Pass Structural, Fail JSON Schema

**Status:** OPEN
**Goal:** Prove the structural fallback is permissive in the specific ways the schema is strict. These are the "negative controls" that make TC-VS-003 meaningful.

**File to modify:** `tests/playbook/test_jsonschema_engine.py` (extend TC-VS-003 file)

**Additional test cases (2 negative controls):**

1. `test_extra_field_passes_structural` — same invalid playbook from TC-VS-003 test 3 (`unknown_field: true`) → structural engine returns PASS (confirms structural is permissive)
2. `test_invalid_id_passes_structural` — playbook with `playbook_id: "INVALID_UPPER"` → structural engine returns PASS (confirms structural doesn't enforce pattern)

**Why these matter:** They prove the jsonschema tests are detecting real gaps, not false positives.

**Required verification:** Both negative-control tests PASS (confirming structural IS permissive where schema IS strict).

**Acceptance criteria:** 2 negative-control tests in same file, all PASS.

---

## TC-VS-005 — Re-run Pilot 4 with jsonschema Engine (r004 Evidence)

**Status:** OPEN
**Dependencies:** TC-VS-001 (proof of jsonschema pass), TC-VS-002 (bug fix so command is valid)

**Goal:** Create r004 pilot evidence proving Pilot 4 was re-executed with jsonschema engine, not structural fallback.

**Steps:**
1. Re-run validate_playbook with `.venv/Scripts/python` and `--engine jsonschema`
2. Capture exact output (exit code, engine, errors, jsonschema_version)
3. Write evidence file at `.local/evidences/playbook-pilots-r004/pilot-4-evidence.yaml`

**Evidence file content:**
```yaml
schema: playbook-pilot-evidence/1.0
pilot_id: pilot-4
pilot_name: "YAML Acquisition Playbook (odf-flat) — jsonschema engine"
run_id: r004
executed_at: "2026-07-02"
comparison:
  r001_r002_r003_engine: fallback_structural
  r004_engine: jsonschema
  improvement: "Full JSON Schema compliance now verified — additionalProperties, patterns, ranges all enforced"

steps_completed:
  - step: validate_playbook_pass_jsonschema
    result: PASS
    engine: jsonschema
    jsonschema_version: "4.26.0"
    errors: []
    exit_code: 0
    invocation: ".venv/Scripts/python tools/playbook/validate_playbook.py --engine jsonschema ..."

verdict: PASS
authority_note: "Pilot evidence is informational. Does NOT approve gates or mark gates PASSED."
```

**Required counter:** PILOTS_STILL_USING_FALLBACK_STRUCTURAL = 0

**Acceptance criteria:**
- r004 evidence file exists at `.local/evidences/playbook-pilots-r004/pilot-4-evidence.yaml`
- `engine: jsonschema` (not `fallback_structural`)
- `exit_code: 0`
- `errors: []`

**Post-completion action:** After TC-VS-005 closes, run lifecycle_audit (all 20 taskcards: TC-PB-001..015 + TC-VS-001..005) then `write_plan_lock.py --terminal --audit-gate`.

---

## Plan Hardening Validation

```yaml
plan_hardening_validation:
  plan_path: plans/.claude/bright-marinating-map.md
  external_seed_path: C:/Users/prora/.claude/plans/bright-marinating-map.md
  hardening_date: "2026-07-01"
  claims_reviewed: 9
  explicit_findings: 5
  implied_findings: 4
  contradictions: 3
  taskcards_added: 3
  taskcards_updated: 0
  findings_without_taskcards: 0
  gates_updated: 0
  evidence_rules_updated: 1
  stale_references_corrected: 2
  blockers: []
  verdict: PLAN_FILE_HARDENED_READY_FOR_EXECUTION
```

<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  reason: "TC-VS-001..005 are open — jsonschema engine hardening not yet complete"
  locked_at: "2026-07-02"
  locked_by: "current-session"
  current_cause: "5 new taskcards added for jsonschema validation engine hardening"
  mutation_policy: "close TC-VS-001..005 then run lifecycle_audit + write_plan_lock --terminal --audit-gate"
-->
