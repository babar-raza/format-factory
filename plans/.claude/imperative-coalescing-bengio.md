# Format Factory — Espanso Capability Integration
# plan_id: imperative-coalescing-bengio
# type: espanso_integration
# status: IN_PROGRESS
# revised: 2026-07-10 (deep reassessment + micro-taskcardization pass)
# authoritative_plan: plans/.claude/imperative-coalescing-bengio.md
# execution_authority: true

---

## PART A — PRESERVED ANALYSIS

### A.1 Honest Diagnosis

The original plan proposed creating 20 new prompt files, extending 5 registries, and adding a
"source map" to track all 107 Espanso entries. That plan was wrong. Before designing a solution
it is necessary to state clearly what is actually true about the system.

**What already exists and works (verified by file-level audit):**

- **`espanso-provenance-map.yaml` already exists** in `.supervisor/prompts/` with 118 entries
  (61 COVERED_BY_EXISTING, 16 GAP_NEW_ASSET, 16 POLICY_ONLY, 13 PARTIAL_COVERAGE, 12 DUPLICATE_OF).
  Extraction date 2026-07-03 when source was 126,293 lines. File is now 141,698 lines — confirmed
  grown since last extraction. Prior integration pass happened; new entries are untracked.
- **Zero broken references** across all registries. 123 capabilities map to 123 skills map to
  123 command files. All 23 prompt files referenced in the prompt registry exist on disk.
- **8 canonical ESP prompts exist** with complete YAML front matter. The actual front matter
  schema (from bounded-executor.md) has 8 fields: espanso_provenance (nested object), prompt_id,
  title, version, status, mutating, context_profile. Additional content (when_to_use,
  prerequisites, etc.) lives in the prompt BODY, not the front matter.
- **Conflict resolution doc** documents 13 resolved duplicate triggers.
- **Registry sync is healthy**: 1:1:1 parity, no orphans.
- **pre-commit hook exists**: `pre-commit-skill-guard` guards src/ mutations.
- **jsonschema IS installed** in `.venv/Lib/site-packages/`.
- **Phase 12 of sprint_executor_validate.py is at line 667**.
- **CLAUDE.md Governance section is at line 460; Human-Free Autonomy Doctrine at line 468**.

**The system is structurally healthy. The prior integration pass covered the framework and 8
highest-value prompts. What remains is gap-filling within the existing structure.**

### A.2 Root Causes (structural weaknesses)

**RC-1: Staleness is undetectable**
Provenance map is dated 2026-07-03 at 126,293 lines. File is now 141,698 lines (+15,405 lines
in 7 days). No hash comparison, no CI check. The map has no `body_sha256` field — it stores
`line_range` for each block. This means: (a) the map can't detect whether an existing block's
body has changed, and (b) ~15,405 lines of new content (likely 5–15 new Espanso entries) are
entirely untracked. The staleness detection tool must compute SHA256 of each block's body
lines (as stored in `line_range`) and write those hashes back, then compare on future runs.

**RC-2: Policy rules live only in Espanso, not in CLAUDE.md**
Five genuine policy rules are in the Espanso file but absent from CLAUDE.md:
- EP-1: Zero-stub enforcement (`:ff-zero-stub`, ~85KB body)
- EP-2: Finding-to-execution lifecycle (`:heal-finding-to-execution-governance`)
- EP-3: Skill-driven architecture — no direct src/ edits (`:ffrepeatable`, `:fflanes`)
- EP-4: Machinery readiness before product work (`:ff-machinery-readiness`)
- EP-5: Per-work-item grading, not per-sprint (`:ff-autonomous-sprint-engine`, `:fflanes`)

CLAUDE.md is read every session and is binding. Espanso is optional. This is the primary
cause of inconsistent agent behavior across sessions.

**RC-3: Schema definitions are advisory, not enforced**
25 JSON schema files exist but the audit found no confirmed validation gate during sprint
closeout. sprint_executor_validate.py has 12 phases. No Phase 13 for schema validation.
`jsonschema` is installed, so enforcement is feasible without new dependencies.

**RC-4: Legacy prompts can't be validated programmatically**
15 of 23 prompt files have no YAML front matter. No programmatic way to distinguish a legacy
template from a new prompt that forgot its front matter. A validator can use the
`existing_prompts` section in prompt-registry.yaml as the exemption list, but that section
must be frozen from future additions.

**RC-5: ~85 Espanso entries are one-time missions with no canonical equivalent**
~50-60 are one-time investigations (oracle, canary, session forensics). ~10-15 are direction
reminders that belong in CLAUDE.md. ~8 are already canonicalized. ~12+ are duplicates. The
provenance map classifies 61 as COVERED_BY_EXISTING — but no verification that the referenced
canonical asset still matches the Espanso body.

**RC-6: Espanso file has no governance gate**
Nothing prevents new entries from accumulating. 15,405 lines were added in 7 days. The
staleness checker addresses detection but not prevention.

### A.3 What Breaks Consistency Across Reruns

Session A reads CLAUDE.md (no EP-1 rule), writes stubs, supervisor accepts. Session B uses
`:ff-zero-stub`, refuses stubs, reopens Session A's output. The contradiction exists because
the rule only lives in Espanso. Placing EP-1 through EP-5 in CLAUDE.md eliminates this class
of inconsistency. Provenance map staleness compounds this: an agent relying on COVERED_BY_EXISTING
routing may invoke a canonical asset that no longer matches the Espanso entry's evolved body.

**Core problem:** Binding policy lives in multiple places with no single authoritative source
and no enforcement that agents read the authoritative version.

### A.4 What to Preserve (Do Not Modify)

- All existing ESP prompts and their YAML front matter
- The provenance map structure (update, not replace)
- The 118 entries, 5 disposition types, all existing `line_range` fields
- The conflict resolution doc (append only)
- The 123:123:123 capability/skill/command parity
- The existing prompt-registry.yaml and agent-prompt-index.yaml entries (append only)
- The 25 schema files (problem is enforcement, not definition)
- The existing_prompts section of prompt-registry.yaml (must freeze, not expand)

### A.5 Tradeoffs and Risks (Preserved)

**Tradeoff 1: Rules in CLAUDE.md vs. prompt files**
CLAUDE.md is binding and read every session. Prompt files need explicit loading. EP-1 through
EP-5 belong in CLAUDE.md. Risk: CLAUDE.md is already >600 lines and loads into context at
session start. Adding ~60 lines is acceptable; beyond ~700 lines total, EP-4 and EP-5 should
move to AGENTS.md. Mitigate: write the 5 rules as compact blocks (no prose preamble).

**Tradeoff 2: 3 new prompts vs. 12**
9 fewer workflows have repository canonical representation. Mitigated: provenance map ARCHIVED
disposition signals agents that no active canonical equivalent exists.

**Tradeoff 3: Schema validation as WARN not FAIL**
Malformed evidence can still be submitted. Intentional: FAIL would break existing sprints
predating the schema addition. Risk: WARN is ignored. Mitigate: log WARN prominently.

**Tradeoff 4: Hash comparison fragility**
Cosmetic Espanso reformats (whitespace) register as MODIFIED. Accept as cost of correctness —
false positives require human review, which is the right behavior anyway.

**Tradeoff 5: Provenance map uses line_range, not body content**
The staleness tool must extract body content from the Espanso file at the stored line_range,
compute SHA256, and write it back. If lines shift (new entries inserted before existing ones),
line_range values become wrong and all hashes will appear MODIFIED. Mitigate: treat MODIFIED
as a signal for human review, not automated blocking.

**Likely limits:**
- Espanso file will keep growing — staleness checker detects but does not prevent
- CLAUDE.md rules enforced only if agents read and follow them
- Registry validator catches structural problems, not semantic prompt body correctness
- Phase 6 schema enforcement WARN may be ignored

---

## PART B — ANALYSIS ARTIFACTS (Preflight)

### B.1 Taskcardization Preflight

```yaml
taskcardization_preflight:
  repository_root: "C:\\Users\\prora\\OneDrive\\Documents\\GitHub\\format-factory"
  branch: main
  head_commit: "af879e55"   # at session start
  active_plan_path: "plans/.claude/imperative-coalescing-bengio.md"
  active_plan_title: "Format Factory — Espanso Capability Integration"
  plan_format: markdown_with_yaml_frontmatter
  plan_authority_source: plan_mode_loaded_file
  plan_size_lines: 750      # pre-enhancement
  major_section_count: 8
  existing_taskcard_sections: 0
  existing_taskcard_format: none
  existing_lanes: 6_phases
  existing_gates: 8_completion_gate_items
  existing_state_vocabulary: none
  existing_validation_model: inline_python_snippets
  existing_evidence_model: implicit_only
  existing_execution_handoff: none
  duplicate_plan_risk: LOW   # only one .claude/plans/ file for this mission
  bugs_found:
    - id: BUG-001
      desc: "Front matter template specifies fields not matching actual bounded-executor.md format"
      fix: "Replace Phase 4 front matter spec with exact 8-field format from bounded-executor.md"
    - id: BUG-002
      desc: "Implementation order circular dependency: Phase 4 uses Phase 5 validator but plan says Phase 5 depends on Phase 4"
      fix: "Phase 5 tool is built FIRST (before Phase 4 creates files)"
    - id: BUG-003
      desc: "No --backfill-hashes mode: provenance map uses line_range, not body_sha256; Phase 1 tool must extract body content at stored line ranges and write initial sha256 values"
      fix: "Add --backfill-hashes flag to Phase 1 tool design"
    - id: BUG-004
      desc: "Phase 3 disposition table only covers ~15 of 118 entries; no default rule stated"
      fix: "Add explicit default: entries not in explicit table retain their current disposition"
    - id: BUG-005
      desc: "CLAUDE.md insertion point is only 8 lines wide between Governance (460) and Human-Free Autonomy Doctrine (468); Phase 2 needs ~60 lines"
      fix: "Section is inserted as a NEW section between the two existing sections, not within the gap. The gap is irrelevant — Edit tool appends after line 460."
```

### B.2 Active Plan Authority Verdict

```
AUTHORITATIVE_PLAN: plans/.claude/imperative-coalescing-bengio.md
AUTHORITY_SOURCE: plan_mode_loaded
DUPLICATE_PLANS_FOUND: 0
DUPLICATE_RISK: RESOLVED
STATUS: SINGLE_AUTHORITATIVE_PLAN_CONFIRMED
```

### B.3 Section Inventory

| Section | Type | Actionable | Issues Found | Enhancement |
|---|---|---|---|---|
| A.1 Honest Diagnosis | Analysis | No | None | Preserve |
| A.2 Root Causes (RC-1 to RC-6) | Analysis | No | BUG-003 added to RC-1 | Preserve + fix |
| A.3 What Breaks Consistency | Analysis | No | None | Preserve |
| A.4 What to Preserve | Constraint | No | None | Preserve |
| Phase 1 — Staleness Tool | Execution | Yes | BUG-003: missing --backfill-hashes | Taskcardize + fix |
| Phase 2 — CLAUDE.md Rules | Execution | Yes | None major | Taskcardize |
| Phase 3 — Provenance Map Update | Execution | Yes | BUG-004: missing default rule | Taskcardize + fix |
| Phase 4 — 3 New Prompts | Execution | Yes | BUG-001 (wrong front matter), BUG-002 (order) | Taskcardize + fix |
| Phase 5 — Registry Validator | Execution | Yes | BUG-002 (must build first) | Taskcardize + reorder |
| Phase 6 — Schema Enforcement | Execution | Yes | None (jsonschema confirmed present) | Taskcardize |
| Implementation Order | DAG | No | BUG-002 corrects this | Replace with corrected DAG |
| Verification Controls | Testing | Yes | Inline scripts → formal validation matrix | Expand |
| Tradeoffs | Analysis | No | None | Preserve |
| Completion Gate | Gate | Yes | None | Preserve as parent acceptance criteria |
| What Is NOT Built | Constraint | No | None | Preserve |

### B.4 Corrected Implementation Order (Bug Fix for BUG-002)

The original order was: Phase 1 + Phase 2 (parallel) → Phase 3 → Phase 4 → Phase 5 → Phase 6.
This is wrong: Phase 4 uses the Phase 5 validator after each prompt file is created.

**Corrected execution sequence:**
```
STEP 0:  Build Phase 5 validator tool (validate_prompt_registry.py + tests)
         Run against current system → confirm exit 0 (baseline)

STEP 1:  Build Phase 1 staleness tool (espanso_staleness_checker.py + tests)
         [PARALLEL with STEP 0 — different files, no shared state]

STEP 2:  Add Phase 2 CLAUDE.md rules (EP-1 through EP-5)

STEP 3:  Run Phase 1 tool --backfill-hashes mode
         → Populates body_sha256 on all 118 provenance map entries

STEP 4:  Phase 3 provenance map disposition updates
         → Mark SUPERSEDED_BY_CLAUDE_MD for EP source entries
         → Mark CANDIDATE_ESP9/10/11 for 3 new prompt sources
         → Update extraction_date

STEP 5:  Run Phase 1 tool (no flags) → confirm exit 0 after backfill

STEP 6A: Read source Espanso entries for product-deepening.md
         Write product-deepening.md, register in both YAMLs
         Run Phase 5 validator → exit 0

STEP 6B: Read source Espanso entries for format-readme-governance.md
         Write format-readme-governance.md, register in both YAMLs
         Run Phase 5 validator → exit 0

STEP 6C: Read source Espanso entries for analytics-migration.md
         Write analytics-migration.md, register in both YAMLs
         Run Phase 5 validator → exit 0

STEP 7:  Phase 6 schema enforcement (add Phase 13 to sprint_executor_validate.py)

STEP 8:  Full verification pass (all 8 completion gate items)
```

---

## PART C — REQUIREMENTS

### C.1 Normalized Requirements Inventory

| REQ-ID | Source Section | Description | Phase |
|---|---|---|---|
| REQ-STALE-001 | RC-1 | Detect new/modified Espanso blocks since last provenance map extraction | P1 |
| REQ-STALE-002 | RC-1 | Backfill body_sha256 into provenance map from stored line_range data | P1 |
| REQ-STALE-003 | RC-1 | Tool must be idempotent: second run on unchanged files exits 0 | P1 |
| REQ-STALE-004 | RC-6 | --update-map flag appends NEW entries only, never overwrites existing | P1 |
| REQ-POLICY-001 | RC-2 | EP-1 zero-stub rule present in CLAUDE.md | P2 |
| REQ-POLICY-002 | RC-2 | EP-2 finding-to-execution lifecycle in CLAUDE.md | P2 |
| REQ-POLICY-003 | RC-2 | EP-3 skill-driven architecture rule in CLAUDE.md | P2 |
| REQ-POLICY-004 | RC-2 | EP-4 machinery readiness rule in CLAUDE.md | P2 |
| REQ-POLICY-005 | RC-2 | EP-5 per-work-item grading rule in CLAUDE.md | P2 |
| REQ-POLICY-006 | A.5 Tradeoff 1 | Total CLAUDE.md must not exceed ~700 lines | P2 |
| REQ-MAP-001 | RC-1 | All 118 provenance entries have body_sha256 field after backfill | P3 |
| REQ-MAP-002 | Phase 3 | SUPERSEDED_BY_CLAUDE_MD disposition on EP source blocks | P3 |
| REQ-MAP-003 | Phase 3 | CANDIDATE_ESP9/10/11 disposition on 3 new prompt source blocks | P3 |
| REQ-MAP-004 | Phase 3 | extraction_date updated to 2026-07-10 | P3 |
| REQ-MAP-005 | BUG-004 | Default rule: entries not in explicit triage table keep current disposition | P3 |
| REQ-PROMPT-001 | Phase 4 | product-deepening.md exists with correct 8-field front matter | P4 |
| REQ-PROMPT-002 | Phase 4 | format-readme-governance.md exists with correct 8-field front matter | P4 |
| REQ-PROMPT-003 | Phase 4 | analytics-migration.md exists with correct 8-field front matter | P4 |
| REQ-PROMPT-004 | Phase 4 | Each prompt registered in prompt-registry.yaml using ESP-PROMPT-8 format | P4 |
| REQ-PROMPT-005 | Phase 4 | Each prompt has routing entry in agent-prompt-index.yaml | P4 |
| REQ-PROMPT-006 | BUG-001 | Front matter matches 8-field actual format from bounded-executor.md | P4 |
| REQ-VAL-001 | Phase 5 | validate_prompt_registry.py Check 1: all file: entries resolve | P5 |
| REQ-VAL-002 | Phase 5 | Check 2: all non-legacy prompts have required front matter fields | P5 |
| REQ-VAL-003 | Phase 5 | Check 3: all prompt_id values unique | P5 |
| REQ-VAL-004 | Phase 5 | Check 4: all non-null capability_id values exist in capabilities registry | P5 |
| REQ-VAL-005 | Phase 5 | Check 5: routing entries reference valid prompt_ids | P5 |
| REQ-VAL-006 | Phase 5 | Validator exits 0 on current system before any Phase 4 changes | P5 |
| REQ-VAL-007 | RC-4 | existing_prompts section frozen: validator docs this constraint in registry | P5 |
| REQ-SCHEMA-001 | RC-3 | Phase 13 added to sprint_executor_validate.py after line 667 | P6 |
| REQ-SCHEMA-002 | Phase 6 | Phase 13 exits WARN not FAIL for schema violations | P6 |
| REQ-SCHEMA-003 | Phase 6 | Phase 13 outputs SKIP_NO_JSONSCHEMA if jsonschema import fails | P6 |

---

## PART D — TASKCARDS

### Taskcard State Machine

**Parent states:** PROPOSED → READY → IN_PROGRESS → CHILDREN_IN_PROGRESS →
INTEGRATION_PENDING → VERIFIED → SCORED → CLOSED | BLOCKED | REROUTED

**Child states:** TODO → READY → IN_PROGRESS → IMPLEMENTED → VERIFIED → SCORED →
CLOSED | REROUTED | BLOCKED

**Micro-step states:** PENDING → READY → ACTIVE → COMPLETE | FAILED | BLOCKED |
SKIPPED_NOT_APPLICABLE (must record reason)

**Invalid transitions (blocked):**
- TODO → CLOSED (must pass through IMPLEMENTED → VERIFIED → SCORED)
- Child CLOSED while any mandatory micro-step is not COMPLETE
- Parent CLOSED while any mandatory child is not CLOSED
- REROUTED → CLOSED without rework evidence
- SKIPPED_NOT_APPLICABLE without recorded reason

**Reroute rule:** Any required quality gate score < 4/5 marks the taskcard REROUTED.
Rerouted taskcards create or reopen the smallest corrective child before proceeding.

---

### TC-P5-001 — Build Prompt Registry Validator

```yaml
taskcard:
  id: TC-P5-001
  type: PARENT
  status: PROPOSED
  title: "Build validate_prompt_registry.py and confirm baseline passes"
  execution_step: STEP 0 (first in corrected order)
  source_requirements: [REQ-VAL-001, REQ-VAL-002, REQ-VAL-003, REQ-VAL-004, REQ-VAL-005, REQ-VAL-006, REQ-VAL-007]
  rationale: "Built first so Phase 4 can use it after each prompt file creation"
  allowed_paths:
    - tools/supervisor/validate_prompt_registry.py
    - tests/supervisor/test_validate_prompt_registry.py
    - .supervisor/prompts/prompt-registry.yaml  # append frozen-section comment only
  forbidden_paths:
    - .supervisor/prompts/*.md  # no prompt files yet
    - .supervisor/prompts/espanso-provenance-map.yaml
    - CLAUDE.md
  preserved_behavior:
    - "All existing prompt-registry.yaml entries must still pass after validator exists"
    - "existing_prompts section entries remain exempt from front matter check"
  outputs:
    - tools/supervisor/validate_prompt_registry.py
    - tests/supervisor/test_validate_prompt_registry.py
    - evidence: "python tools/supervisor/validate_prompt_registry.py exits 0"
  parent_acceptance_criteria:
    - "validate_prompt_registry.py exits 0 against current unmodified system"
    - "4 test cases pass"
    - "existing_prompts freeze constraint documented in prompt-registry.yaml"
  children:
    - TC-P5-001-01
    - TC-P5-001-02
    - TC-P5-001-03
    - TC-P5-001-04
    - TC-P5-001-05
    - TC-P5-001-06
    - TC-P5-001-07
  quality_dimensions:
    requirement_correctness: 0    # pending
    implementation_correctness: 0
    test_coverage: 0
    evidence_completeness: 0
    regression_safety: 0
  rollback: "Delete tools/supervisor/validate_prompt_registry.py and test file"
```

**TC-P5-001-01 — Inspect existing prompt registry schemas**
```yaml
child_taskcard:
  id: TC-P5-001-01
  parent: TC-P5-001
  status: TODO
  title: "Read prompt-registry.yaml and agent-prompt-index.yaml to understand exact structure"
  purpose: "Validator must read the actual YAML keys, not assumed keys"
  allowed_files:
    - .supervisor/prompts/prompt-registry.yaml
    - .supervisor/prompts/agent-prompt-index.yaml
    - .supervisor/prompts/bounded-executor.md
  forbidden: "No file mutations"
  micro_steps:
    - id: MS-P5-001-01-01
      action: "Read .supervisor/prompts/prompt-registry.yaml in full"
      expected_output: "Confirm key names: prompts section uses 'id' not 'prompt_id'; operational_prompts section uses 'id'; existing_prompts section uses 'id'"
      completion_check: "Know exact YAML key for file reference field (is it 'file' or 'path'?)"
    - id: MS-P5-001-01-02
      action: "Read .supervisor/prompts/agent-prompt-index.yaml routing_decision_table section"
      expected_output: "Know exact field name for prompt reference in routing entries (is it 'action' or 'prompt_id'?)"
      completion_check: "Can write Check 5 comparison logic with correct field names"
    - id: MS-P5-001-01-03
      action: "Read first 25 lines of .supervisor/prompts/bounded-executor.md"
      expected_output: "Confirm exact 8 front matter fields: espanso_provenance (nested), prompt_id, title, version, status, mutating, context_profile"
      completion_check: "Can write Check 2 field validation list"
    - id: MS-P5-001-01-04
      action: "Record findings in taskcard evidence note before proceeding to TC-P5-001-02"
      expected_output: "Field name map recorded: registry_file_key, routing_ref_key, required_frontmatter_fields"
  evidence_required: "Field name map produced before implementation begins"
  next_valid: TC-P5-001-02
```

**TC-P5-001-02 — Implement validator Checks 1 and 3 (file existence, unique IDs)**
```yaml
child_taskcard:
  id: TC-P5-001-02
  parent: TC-P5-001
  status: TODO
  preconditions: [TC-P5-001-01 CLOSED]
  title: "Implement Check 1 (file: entries resolve) and Check 3 (unique prompt_ids)"
  allowed_files:
    - tools/supervisor/validate_prompt_registry.py  (create)
  micro_steps:
    - id: MS-P5-001-02-01
      action: "Create tools/supervisor/validate_prompt_registry.py with shebang, argparse (--registry, --index, --prompts-dir flags with defaults), and main() entry point"
      expected_output: "File exists, imports: yaml, pathlib, sys, argparse"
    - id: MS-P5-001-02-02
      action: "Implement check_file_references(registry_path, prompts_dir) → list[str]: reads all three sections (prompts, operational_prompts, existing_prompts), extracts 'file' field, checks Path(prompts_dir / file).exists()"
      expected_output: "Function returns list of error strings; empty list = pass"
    - id: MS-P5-001-02-03
      action: "Implement check_unique_ids(registry_path) → list[str]: collects all 'id' values from all three sections, detects duplicates"
      expected_output: "Function returns ['DUPLICATE prompt_id: X in sections Y and Z'] for each duplicate"
    - id: MS-P5-001-02-04
      action: "Add main() call: run check_file_references + check_unique_ids, print errors, exit 1 if any errors, exit 0 if none"
      expected_output: "Script runnable: python tools/supervisor/validate_prompt_registry.py exits 0 against current system"
    - id: MS-P5-001-02-05
      action: "Run: python tools/supervisor/validate_prompt_registry.py"
      expected_output: "Exit 0. If exit 1: read errors, identify mismatched field names, fix the field name in the implementation."
      failure_handling: "If exit 1 due to wrong key name: fix the key in check_file_references using findings from TC-P5-001-01. Do NOT change the YAML."
  evidence_required: "exit 0 terminal output captured"
  next_valid: TC-P5-001-03
```

**TC-P5-001-03 — Implement Checks 2, 4, 5 (front matter, capability IDs, routing)**
```yaml
child_taskcard:
  id: TC-P5-001-03
  parent: TC-P5-001
  status: TODO
  preconditions: [TC-P5-001-02 CLOSED]
  title: "Implement Check 2 (front matter), Check 4 (capability_ids), Check 5 (routing)"
  allowed_files:
    - tools/supervisor/validate_prompt_registry.py  (edit)
  micro_steps:
    - id: MS-P5-001-03-01
      action: "Implement check_frontmatter(registry_path, prompts_dir) → list[str]: for each entry in prompts + operational_prompts sections (NOT existing_prompts), open the .md file, parse YAML front matter between --- markers, check for fields: espanso_provenance, prompt_id, title, version, status, mutating, context_profile"
      expected_output: "Missing field errors: 'MISSING_FRONTMATTER_FIELD: {field} in {file}'"
    - id: MS-P5-001-03-02
      action: "Implement check_capability_ids(registry_path, prompts_dir, capabilities_registry_path) → list[str]: for each non-null capability_id field in front matter, verify it exists in .governance/capabilities/registry.yaml"
      expected_output: "Error: 'UNKNOWN_CAPABILITY_ID: X in file Y'"
    - id: MS-P5-001-03-03
      action: "Implement check_routing_references(index_path, registry_path) → list[str]: read agent-prompt-index.yaml routing_decision_table, extract all prompt references, confirm each is a valid prompt id from the registry"
      expected_output: "Error: 'ROUTING_REFS_UNKNOWN_PROMPT: X in routing entry Y'"
    - id: MS-P5-001-03-04
      action: "Add three new checks to main() call chain"
      expected_output: "Script still exits 0 against current system"
    - id: MS-P5-001-03-05
      action: "Run: python tools/supervisor/validate_prompt_registry.py"
      expected_output: "Exit 0 (all current prompts have correct front matter for ESP prompts)"
      failure_handling: "If any existing ESP prompt fails front matter check: read the specific error, inspect the file, add the field name to the REQUIRED_FIELDS list only if the field genuinely exists in the actual files."
  evidence_required: "exit 0 confirmed"
  next_valid: TC-P5-001-04
```

**TC-P5-001-04 — Write and run 4 tests**
```yaml
child_taskcard:
  id: TC-P5-001-04
  parent: TC-P5-001
  status: TODO
  preconditions: [TC-P5-001-03 CLOSED]
  allowed_files:
    - tests/supervisor/test_validate_prompt_registry.py  (create)
  micro_steps:
    - id: MS-P5-001-04-01
      action: "Create tests/supervisor/test_validate_prompt_registry.py with imports: subprocess, pathlib, yaml, textwrap, tmp_path fixture"
    - id: MS-P5-001-04-02
      action: "Write test_all_current_registrations_pass(): run subprocess(['python', 'tools/supervisor/validate_prompt_registry.py']); assert returncode == 0"
    - id: MS-P5-001-04-03
      action: "Write test_missing_file_fails(tmp_path): create temp registry YAML with a 'file' entry pointing to nonexistent .md; run validator with --registry pointing to temp file; assert returncode == 1"
    - id: MS-P5-001-04-04
      action: "Write test_missing_front_matter_fails(tmp_path): create temp .md without --- front matter block; create temp registry listing it in operational_prompts; run validator; assert returncode == 1"
    - id: MS-P5-001-04-05
      action: "Write test_duplicate_id_fails(tmp_path): create temp registry with same id in two sections; run validator; assert returncode == 1"
    - id: MS-P5-001-04-06
      action: "Run: .venv/Scripts/pytest tests/supervisor/test_validate_prompt_registry.py -v"
      expected_output: "4/4 PASSED"
      failure_handling: "If test_all_current_registrations_pass fails: debug the validator check that's failing against the live system — do NOT weaken the check. Fix the validator to correctly read the existing format."
  evidence_required: "pytest output showing 4 PASSED"
  next_valid: TC-P5-001-05
```

**TC-P5-001-05 — Freeze existing_prompts section with comment**
```yaml
child_taskcard:
  id: TC-P5-001-05
  parent: TC-P5-001
  status: TODO
  preconditions: [TC-P5-001-04 CLOSED]
  title: "Add freeze comment to prompt-registry.yaml existing_prompts section"
  allowed_files:
    - .supervisor/prompts/prompt-registry.yaml  (edit, comment only)
  micro_steps:
    - id: MS-P5-001-05-01
      action: "Read .supervisor/prompts/prompt-registry.yaml to find existing_prompts: section header line number"
    - id: MS-P5-001-05-02
      action: "Add YAML comment immediately above existing_prompts: key: '# FROZEN: No new entries may be added to this section. Entries here are exempt from front matter validation. Add new prompts to operational_prompts instead.'"
    - id: MS-P5-001-05-03
      action: "Run validate_prompt_registry.py to confirm adding a comment did not break anything (exit 0)"
  evidence_required: "validate_prompt_registry.py still exits 0"
  closeout_criteria: "Comment present, validator passes"
  next_valid: TC-P1-001 (can run in parallel with TC-P5 test suite)
```

---

### TC-P1-001 — Build Espanso Staleness Detection Tool

```yaml
taskcard:
  id: TC-P1-001
  type: PARENT
  status: PROPOSED
  title: "Build espanso_staleness_checker.py with backfill, detection, and update modes"
  execution_step: STEP 1 (parallel with TC-P5-001)
  source_requirements: [REQ-STALE-001, REQ-STALE-002, REQ-STALE-003, REQ-STALE-004]
  allowed_paths:
    - tools/supervisor/espanso_staleness_checker.py
    - tests/supervisor/test_espanso_staleness_checker.py
  forbidden_paths:
    - .supervisor/prompts/espanso-provenance-map.yaml  # modified only in TC-P3-001
    - CLAUDE.md
    - src/
  critical_design_note: |
    The provenance map stores line_range: [start, end] for each block's body in the
    Espanso file. The --backfill-hashes mode must:
    1. Read the Espanso file
    2. For each entry in the provenance map, extract lines[start:end] from the file
    3. Normalize whitespace (strip trailing spaces, normalize CRLF to LF)
    4. Compute SHA256 of the normalized body
    5. Write body_sha256 field to that entry in the map
    The --detect mode (default) reads existing body_sha256 values and compares to
    current file content at the stored line_range positions.
    The --update-map mode appends NEW blocks (in file but not in map) with status=UNREVIEWED.
  outputs:
    - tools/supervisor/espanso_staleness_checker.py
    - tests/supervisor/test_espanso_staleness_checker.py
  parent_acceptance_criteria:
    - "4 tests pass"
    - "--backfill-hashes: all 118 provenance map entries get body_sha256"
    - "--detect (no flags): exits 0 after backfill on unchanged file"
    - "--update-map: appends NEW entries, never overwrites"
  children:
    - TC-P1-001-01
    - TC-P1-001-02
    - TC-P1-001-03
    - TC-P1-001-04
  rollback: "Delete tools/supervisor/espanso_staleness_checker.py and test file"
```

**TC-P1-001-01 — Implement Espanso YAML parser and body extractor**
```yaml
child_taskcard:
  id: TC-P1-001-01
  parent: TC-P1-001
  status: TODO
  title: "Parse Espanso file: extract trigger lists and body content"
  allowed_files:
    - tools/supervisor/espanso_staleness_checker.py  (create)
  micro_steps:
    - id: MS-P1-001-01-01
      action: "Create tools/supervisor/espanso_staleness_checker.py: imports (yaml, hashlib, sys, pathlib, argparse, re), constants (DEFAULT_ESPANSO_PATH, DEFAULT_PROVENANCE_MAP)"
    - id: MS-P1-001-01-02
      action: "Implement parse_espanso_blocks(espanso_path: Path) → list[dict]: load YAML with yaml.safe_load, iterate matches list, for each item extract: triggers (list), replace body (str), line_range (approximate: count lines to reconstruct). NOTE: YAML loading gives body content directly; line positions must be found separately."
      critical_note: |
        The Espanso file is YAML. yaml.safe_load gives the replace field as a string directly.
        But the provenance map stores line_range [start, end] referring to the RAW file lines,
        not the parsed body. To compute sha256 consistently with --backfill-hashes mode, we
        must extract the raw text at the stored line_range positions, NOT use yaml-parsed body.
        Implementation: read raw file as lines list; for backfill mode, use line_range from map
        to extract raw body text; normalize and hash it.
    - id: MS-P1-001-01-03
      action: "Implement load_provenance_map(map_path: Path) → dict: read YAML, return the full document. Key fields per entry: block_id, line_range (list of 2 ints), disposition, body_sha256 (optional)."
    - id: MS-P1-001-01-04
      action: "Implement extract_body_at_range(file_lines: list[str], line_range: list) → str: given line_range [start, end] (1-indexed or 0-indexed — verify against map), extract lines[start:end], join, strip trailing whitespace per line, normalize CRLF to LF."
      critical_note: "Check whether the stored line_range values are 1-indexed or 0-indexed by comparing a known block's triggers text against the file content at that range."
    - id: MS-P1-001-01-05
      action: "Implement compute_body_sha256(body_text: str) → str: hashlib.sha256(body_text.encode('utf-8')).hexdigest()"
  evidence_required: "Function parse_espanso_blocks runs without exception on the Espanso file"
  next_valid: TC-P1-001-02
```

**TC-P1-001-02 — Implement --backfill-hashes mode**
```yaml
child_taskcard:
  id: TC-P1-001-02
  parent: TC-P1-001
  status: TODO
  preconditions: [TC-P1-001-01 CLOSED]
  title: "Implement --backfill-hashes: write initial body_sha256 to all map entries without one"
  allowed_files:
    - tools/supervisor/espanso_staleness_checker.py  (edit)
    - .supervisor/prompts/espanso-provenance-map.yaml  (written ONLY when this mode is invoked)
  micro_steps:
    - id: MS-P1-001-02-01
      action: "Implement backfill_hashes(espanso_path, map_path): read Espanso file as raw lines; load provenance map; for each entry in map that has no body_sha256: extract body at line_range, compute sha256, write to entry dict; save updated map back to YAML"
    - id: MS-P1-001-02-02
      action: "Add --backfill-hashes flag to argparse and dispatch in main()"
    - id: MS-P1-001-02-03
      action: "Run: python tools/supervisor/espanso_staleness_checker.py --backfill-hashes --espanso 'C:\\Users\\prora\\AppData\\Roaming\\espanso\\match\\format-factory.yml' --provenance-map .supervisor/prompts/espanso-provenance-map.yaml"
      expected_output: "Output like: 'Backfilled body_sha256 for 118 entries. 0 entries already had hashes.'"
      failure_handling: "If line_range indexing is off (getting wrong lines): print first 5 lines of extracted body for block_id=1 and compare to expected content. Adjust 1-indexed vs 0-indexed offset."
    - id: MS-P1-001-02-04
      action: "Verify: python -c \"import yaml; m=yaml.safe_load(open('.supervisor/prompts/espanso-provenance-map.yaml')); entries=[e for e in m.get('entries', m.get('blocks', [])) if not e.get('body_sha256')]; assert not entries, f'{len(entries)} missing'; print('PASS')\""
      expected_output: "PASS"
  evidence_required: "All 118 entries have body_sha256 confirmed by verification script"
  rollback: "git checkout .supervisor/prompts/espanso-provenance-map.yaml (if backfill produces wrong content)"
  next_valid: TC-P1-001-03
```

**TC-P1-001-03 — Implement --detect mode (default) and --update-map**
```yaml
child_taskcard:
  id: TC-P1-001-03
  parent: TC-P1-001
  status: TODO
  preconditions: [TC-P1-001-02 CLOSED]
  title: "Implement default detection mode and --update-map for new entries"
  allowed_files:
    - tools/supervisor/espanso_staleness_checker.py  (edit)
  micro_steps:
    - id: MS-P1-001-03-01
      action: "Implement detect_staleness(espanso_path, map_path) → dict: returns {UNCHANGED: [], MODIFIED: [], NEW: [], REMOVED: []}. UNCHANGED: body_sha256 matches computed hash at same line_range. MODIFIED: sha256 differs. NEW: block in Espanso file but no matching block_id in map. REMOVED: block_id in map but cannot find matching trigger in Espanso file."
      note: "For NEW blocks: must first parse all triggers from Espanso YAML to compare against map's primary_trigger fields. Block identification uses primary_trigger as the stable key."
    - id: MS-P1-001-03-02
      action: "Implement --update-map mode: for each NEW block in detection result, append an entry to provenance map with: block_id (next available), primary_trigger, all_triggers, line_range, disposition=UNREVIEWED, body_sha256 (compute now). Save map."
    - id: MS-P1-001-03-03
      action: "Implement report output: print counts per category; list MODIFIED and NEW triggers. Exit 0 if 0 MODIFIED and 0 NEW (or all NEW were updated with --update-map); Exit 2 if any MODIFIED or NEW remain; Exit 1 on error."
    - id: MS-P1-001-03-04
      action: "Run detect mode: python tools/supervisor/espanso_staleness_checker.py (no flags)"
      expected_output: "After backfill: 118 UNCHANGED, 0 MODIFIED, N NEW (for entries added after line 126293). Exit 2 if N>0."
      note: "N may be >0 since file grew from 126293 to 141698 lines. That is expected — new entries will be reported as NEW."
    - id: MS-P1-001-03-05
      action: "Run with --update-map to register the NEW entries"
      expected_output: "NEW entries appended to provenance map; now exits 2 only if MODIFIED entries exist"
  evidence_required: "Detection mode output showing correct categorization"
  next_valid: TC-P1-001-04
```

**TC-P1-001-04 — Write and run 4 tests**
```yaml
child_taskcard:
  id: TC-P1-001-04
  parent: TC-P1-001
  status: TODO
  preconditions: [TC-P1-001-03 CLOSED]
  allowed_files:
    - tests/supervisor/test_espanso_staleness_checker.py  (create)
  micro_steps:
    - id: MS-P1-001-04-01
      action: "Create test file with imports and helper create_synthetic_espanso(tmp_path, entries) that writes a minimal valid Espanso YAML with one 'matches' list entry per entry dict"
    - id: MS-P1-001-04-02
      action: "Write test_unchanged_entry_reports_unchanged(tmp_path): create synthetic Espanso with one block, backfill its sha256, run detect → UNCHANGED count == 1"
    - id: MS-P1-001-04-03
      action: "Write test_new_entry_detected(tmp_path): create map with 1 block, Espanso file with 2 blocks → NEW count == 1, exit code 2"
    - id: MS-P1-001-04-04
      action: "Write test_modified_entry_detected(tmp_path): create map with sha256 for old body, Espanso with changed body at same trigger → MODIFIED count == 1, exit code 2"
    - id: MS-P1-001-04-05
      action: "Write test_missing_espanso_file_exits_gracefully(): call with nonexistent path → exit code 1 with message"
    - id: MS-P1-001-04-06
      action: "Run: .venv/Scripts/pytest tests/supervisor/test_espanso_staleness_checker.py -v"
      expected_output: "4/4 PASSED"
  evidence_required: "pytest output showing 4 PASSED"
  next_valid: TC-P2-001
```

---

### TC-P2-001 — Extract Policy Rules to CLAUDE.md

```yaml
taskcard:
  id: TC-P2-001
  type: PARENT
  status: PROPOSED
  title: "Add EP-1 through EP-5 policy rules to CLAUDE.md"
  execution_step: STEP 2 (after STEP 0/1, can run after TC-P5 tests pass)
  source_requirements: [REQ-POLICY-001 through REQ-POLICY-006]
  allowed_paths:
    - CLAUDE.md
  forbidden_paths:
    - src/
    - .supervisor/prompts/
    - tools/
  critical_constraint: |
    Insert new section AFTER line 460 (## Governance) and BEFORE line 468
    (## Human-Free Autonomy Doctrine). The "## Governance" section has 7 lines of
    content. Insert the new section AFTER the full Governance section ends, not within it.
    Use Edit tool with old_string = the text immediately before the Human-Free Autonomy
    Doctrine header.
  parent_acceptance_criteria:
    - "python -c check for EP-1 through EP-5 exits 0"
    - "Total CLAUDE.md lines <= 700"
    - "CLAUDE.md still parseable (no YAML or markdown syntax errors)"
  children:
    - TC-P2-001-01
    - TC-P2-001-02
    - TC-P2-001-03
  rollback: "git checkout CLAUDE.md"
```

**TC-P2-001-01 — Read CLAUDE.md and identify exact insertion point**
```yaml
child_taskcard:
  id: TC-P2-001-01
  parent: TC-P2-001
  status: TODO
  allowed_files: [CLAUDE.md] (read only)
  micro_steps:
    - id: MS-P2-001-01-01
      action: "Read CLAUDE.md lines 455-475 to see the exact text around the insertion point"
      expected_output: "Know the 3-4 lines of text immediately before '## Human-Free Autonomy Doctrine' that will serve as old_string in Edit tool"
    - id: MS-P2-001-01-02
      action: "Count total lines in CLAUDE.md"
      expected_output: "Know current line count; confirm target <= current + 70"
    - id: MS-P2-001-01-03
      action: "Verify `:ffrepeatable` source text in Espanso file around line 140774: read 10 lines to confirm EP-3 rule text is accurate"
      expected_output: "EP-3 rule accurately reflects the source"
  evidence_required: "Insertion point confirmed, source text verified"
  next_valid: TC-P2-001-02
```

**TC-P2-001-02 — Write the 5 policy rules**
```yaml
child_taskcard:
  id: TC-P2-001-02
  parent: TC-P2-001
  status: TODO
  preconditions: [TC-P2-001-01 CLOSED]
  allowed_files: [CLAUDE.md] (edit)
  micro_steps:
    - id: MS-P2-001-02-01
      action: "Use Edit tool to insert new section before '## Human-Free Autonomy Doctrine'. old_string = the text before that header. new_string = old_string prepended with the new section."
      new_section_content: |
        ## Espanso-Sourced Production Rules

        These rules are extracted from Espanso operational entries. They are binding in every
        session. Source: integration plan imperative-coalescing-bengio (2026-07-10).

        **EP-1 Zero-Stub Enforcement:** Production source under `src/` must not contain
        stubs, placeholders, `raise NotImplementedError()` in non-abstract methods, or
        `# TODO: implement` in product code. If stubs are found: root-cause the generator
        that created them, repair the generator first, then heal the product.
        Detection: `grep -r "NotImplementedError\|pass  # stub\|TODO.*implement" src/`

        **EP-2 Finding-to-Execution Lifecycle:** Every audit/review finding must become:
        FINDING → CLASSIFICATION → ROOT CAUSE → GAP ENTRY → TASKCARD → EXECUTION → VERIFICATION.
        A finding is NOT closed by writing it to a report only. It IS closed by a CLOSED taskcard
        with evidence proving the root cause was eliminated.

        **EP-3 Skill-Driven Architecture:** Agents MUST NOT directly edit files under `src/`
        without invoking a governed skill (`/add-python-api`, `/product-source-task`,
        `/format-feature-expansion`, etc.). If no skill exists for the operation: create or
        register the missing skill first, then invoke it. Manual `src/` edits cannot be
        replayed by the supervisor and will fail the EP-3 audit.

        **EP-4 Machinery Readiness Before Product Work:** Before product deepening on any
        format, verify: (1) oracle is VERIFIED or CASES_DEFINED; (2) the skill to be invoked
        exists; (3) SAL fact count > 0; (4) governance validator does not block. Fix machinery
        defects first. Do not produce product code through broken machinery.

        **EP-5 Per-Work-Item Grading:** The supervisor grades EACH work item independently.
        Evidence declarations must declare one item per logical unit of work — not one item
        per sprint. Items graded below `completed_verified` become rework regardless of
        sprint-level narrative success.

      note: "Keep rules compact. No prose preamble per line. Aim for ~40 total lines."
    - id: MS-P2-001-02-02
      action: "Count lines added: wc -l CLAUDE.md; confirm new total <= 700"
  evidence_required: "Edit succeeded; line count within budget"
  next_valid: TC-P2-001-03
```

**TC-P2-001-03 — Verify all 5 rules present**
```yaml
child_taskcard:
  id: TC-P2-001-03
  parent: TC-P2-001
  status: TODO
  preconditions: [TC-P2-001-02 CLOSED]
  allowed_files: [] (verification only)
  micro_steps:
    - id: MS-P2-001-03-01
      action: "Run verification: python -c \"text=open('CLAUDE.md').read(); rules=['EP-1','EP-2','EP-3','EP-4','EP-5']; missing=[r for r in rules if r not in text]; assert not missing,f'Missing: {missing}'; print('PASS')\""
      expected_output: "PASS"
      failure_handling: "If any rule missing: re-read CLAUDE.md to locate where the edit was applied and verify the full text was written. Re-apply the Edit if content was truncated."
    - id: MS-P2-001-03-02
      action: "Run validate_prompt_registry.py to confirm CLAUDE.md change did not affect prompt registry (exit 0)"
      expected_output: "Exit 0"
  closeout_criteria: "Both checks pass"
  next_valid: TC-P3-001
```

---

### TC-P3-001 — Update Provenance Map Dispositions

```yaml
taskcard:
  id: TC-P3-001
  type: PARENT
  status: PROPOSED
  title: "Update espanso-provenance-map.yaml: dispositions for EP-sourced and candidate entries"
  execution_step: STEP 4 (after TC-P1-001 backfill completes)
  source_requirements: [REQ-MAP-001, REQ-MAP-002, REQ-MAP-003, REQ-MAP-004, REQ-MAP-005]
  allowed_paths:
    - .supervisor/prompts/espanso-provenance-map.yaml
  forbidden_paths:
    - .supervisor/prompts/*.md
    - tools/
    - CLAUDE.md
  default_rule_for_undiscussed_entries: |
    Entries NOT in the explicit triage table below retain their current disposition.
    Do NOT change COVERED_BY_EXISTING, PARTIAL_COVERAGE, DUPLICATE_OF, or POLICY_ONLY
    entries unless they are explicitly in the triage table.
  triage_table:
    SUPERSEDED_BY_CLAUDE_MD_EP1:
      - primary_trigger: ":ff-zero-stub"   # both variant entries
    SUPERSEDED_BY_CLAUDE_MD_EP2:
      - primary_trigger: ":heal-finding-to-execution-governance"
      - primary_trigger: ":prevent-report-only-deferrals"
    SUPERSEDED_BY_CLAUDE_MD_EP3:
      - primary_trigger: ":ffrepeatable"
      - primary_trigger: ":fflanes"
    SUPERSEDED_BY_CLAUDE_MD_EP5:
      - primary_trigger: ":ff-autonomous-sprint-engine"
    CANDIDATE_ESP9:
      - primary_trigger: ":ff-two-lane-product-deepening"
      - primary_trigger: ":ff-product-deepening-train"
      - primary_trigger: ":ff-resume-product-deepening"
    CANDIDATE_ESP10:
      - primary_trigger: ":ff-format-readme-hardening"
      - primary_trigger: ":ffsrn"
    CANDIDATE_ESP11:
      - primary_trigger: ":ff-inventory-analytics"
      - primary_trigger: ":ff-decide-analytics-migrations"
      - primary_trigger: ":ff-migrate-analytics-batches"
      - primary_trigger: ":ff-verify-no-analytics"
      - primary_trigger: ":ff-remove-analytics-safely"
  parent_acceptance_criteria:
    - "All entries with SUPERSEDED_BY_CLAUDE_MD disposition have a superseded_by field referencing the correct CLAUDE.md rule"
    - "CANDIDATE_ESP entries have disposition updated"
    - "extraction_date updated to 2026-07-10"
    - "Staleness checker exits 0 (or exits 2 only for genuinely MODIFIED entries)"
  children:
    - TC-P3-001-01
    - TC-P3-001-02
    - TC-P3-001-03
  rollback: "git checkout .supervisor/prompts/espanso-provenance-map.yaml"
```

**TC-P3-001-01 — Verify backfill completed and staleness state**
```yaml
child_taskcard:
  id: TC-P3-001-01
  parent: TC-P3-001
  status: TODO
  preconditions: [TC-P1-001 CLOSED (backfill run complete)]
  micro_steps:
    - id: MS-P3-001-01-01
      action: "Run verification: python -c \"import yaml; m=yaml.safe_load(open('.supervisor/prompts/espanso-provenance-map.yaml')); entries=m.get('entries', m.get('blocks',[])); no_hash=[e for e in entries if not e.get('body_sha256')]; assert not no_hash,f'{len(no_hash)} missing sha256'; print(f'PASS: {len(entries)} entries all have body_sha256')\""
      expected_output: "PASS: N entries all have body_sha256"
    - id: MS-P3-001-01-02
      action: "Run staleness checker detect mode; capture output"
      expected_output: "Shows counts for UNCHANGED, MODIFIED, NEW. Record these numbers."
      note: "If NEW entries exist (added since line 126293): they were already registered via --update-map in TC-P1-001-03. They should show as UNCHANGED now."
  evidence_required: "Backfill confirmation pass output + staleness detect output recorded"
  next_valid: TC-P3-001-02
```

**TC-P3-001-02 — Apply disposition updates from triage table**
```yaml
child_taskcard:
  id: TC-P3-001-02
  parent: TC-P3-001
  status: TODO
  preconditions: [TC-P3-001-01 CLOSED]
  allowed_files:
    - .supervisor/prompts/espanso-provenance-map.yaml
  micro_steps:
    - id: MS-P3-001-02-01
      action: "Read espanso-provenance-map.yaml in full to find entries matching the triage table triggers"
    - id: MS-P3-001-02-02
      action: "For each SUPERSEDED_BY_CLAUDE_MD entry: change disposition field to the correct SUPERSEDED_BY_CLAUDE_MD_EPn value; add field superseded_by: 'CLAUDE.md#EP-N'; add field note with date"
    - id: MS-P3-001-02-03
      action: "For each CANDIDATE_ESPn entry: change disposition field to CANDIDATE_ESP9/10/11 as appropriate; add field note with date and which new prompt will be created"
    - id: MS-P3-001-02-04
      action: "Update extraction_date: '2026-07-10' in the map's meta section"
    - id: MS-P3-001-02-05
      action: "Run validate_prompt_registry.py to confirm map changes did not affect prompt registry (exit 0)"
  evidence_required: "Updated map saved; validator exits 0"
  next_valid: TC-P3-001-03
```

**TC-P3-001-03 — Final verification of provenance map**
```yaml
child_taskcard:
  id: TC-P3-001-03
  parent: TC-P3-001
  status: TODO
  preconditions: [TC-P3-001-02 CLOSED]
  micro_steps:
    - id: MS-P3-001-03-01
      action: "Count entries with SUPERSEDED_BY_CLAUDE_MD disposition: python -c \"import yaml; m=yaml.safe_load(open('.supervisor/prompts/espanso-provenance-map.yaml')); entries=m.get('entries',m.get('blocks',[])); sup=[e for e in entries if 'SUPERSEDED_BY_CLAUDE_MD' in str(e.get('disposition',''))]; print(f'{len(sup)} SUPERSEDED_BY_CLAUDE_MD entries')\""
      expected_output: "At least 5 entries (one per EP rule)"
    - id: MS-P3-001-03-02
      action: "Count entries with CANDIDATE_ESP disposition: python -c similar to above but filtering for CANDIDATE_ESP"
      expected_output: "At least 3 entries (for ESP9, ESP10, ESP11)"
    - id: MS-P3-001-03-03
      action: "Run staleness checker detect mode again; confirm exit 0 (all UNCHANGED after disposition updates)"
  closeout_criteria: "Disposition counts match expectations; staleness checker exits 0"
  next_valid: TC-P4-001
```

---

### TC-P4-001 — Create 3 Canonical Prompt Files

```yaml
taskcard:
  id: TC-P4-001
  type: PARENT
  status: PROPOSED
  title: "Create product-deepening.md, format-readme-governance.md, analytics-migration.md"
  execution_step: STEP 6 (after TC-P3-001 completes)
  source_requirements: [REQ-PROMPT-001 through REQ-PROMPT-006]
  critical_front_matter_fix: |
    BUG-001 FIX: The correct front matter format (from actual bounded-executor.md) is:
    ---
    espanso_provenance:
      source_trigger: ":primary-trigger-here"
      source_block: N   (block_id from provenance map)
      source_line_range: [start, end]
      gap_id: GAP-ESP-009/010/011
      extraction_date: "2026-07-10"
      capability_id: null   (no matching product capability for these prompts)
    prompt_id: ESP-PROMPT-9/10/11
    title: "..."
    version: "1.0"
    status: ACTIVE
    mutating: true
    context_profile: full
    ---
    The body of the prompt contains: when_to_use, when_not_to_use, prerequisites,
    allowed_paths, forbidden_paths, inputs, outputs, completion_gate sections.
    These are BODY content, NOT front matter fields.
  allowed_paths:
    - .supervisor/prompts/product-deepening.md
    - .supervisor/prompts/format-readme-governance.md
    - .supervisor/prompts/analytics-migration.md
    - .supervisor/prompts/prompt-registry.yaml  (append 3 new entries)
    - .supervisor/prompts/agent-prompt-index.yaml  (append 3 new routing entries)
  forbidden_paths:
    - .supervisor/prompts/espanso-provenance-map.yaml  (already updated)
    - .supervisor/prompts/*.md (existing files — do not modify)
    - CLAUDE.md
    - tools/
    - src/
  parent_acceptance_criteria:
    - "3 new .md files exist with correct 8-field front matter"
    - "3 new entries in prompt-registry.yaml using id/name/file/description/stage/mode format"
    - "3 new routing entries in agent-prompt-index.yaml"
    - "validate_prompt_registry.py exits 0 after all 3 prompts registered"
  children:
    - TC-P4-001-01  (product-deepening.md)
    - TC-P4-001-02  (format-readme-governance.md)
    - TC-P4-001-03  (analytics-migration.md)
```

**TC-P4-001-01 — Create product-deepening.md (ESP-PROMPT-9)**
```yaml
child_taskcard:
  id: TC-P4-001-01
  parent: TC-P4-001
  status: TODO
  preconditions: [TC-P3-001 CLOSED, TC-P5-001 CLOSED]
  title: "Create .supervisor/prompts/product-deepening.md and register"
  allowed_files:
    - .supervisor/prompts/product-deepening.md  (create)
    - .supervisor/prompts/prompt-registry.yaml  (append)
    - .supervisor/prompts/agent-prompt-index.yaml  (append)
  micro_steps:
    - id: MS-P4-001-01-01
      action: "Read Espanso file at provenance map line_range for entries with CANDIDATE_ESP9 disposition. Read body content of ':ff-two-lane-product-deepening', ':ff-product-deepening-train', and ':ff-resume-product-deepening' entries."
      purpose: "Synthesize canonical protocol body from actual source entries"
    - id: MS-P4-001-01-02
      action: "Create .supervisor/prompts/product-deepening.md with exact front matter format (8 fields as specified in BUG-001 fix above). prompt_id=ESP-PROMPT-9, title='Product Deepening (Two-Lane)', context_profile=full, mutating=true, source_trigger=':ff-two-lane-product-deepening', gap_id=GAP-ESP-009"
    - id: MS-P4-001-01-03
      action: "Write prompt body with sections: ## When to Use, ## When NOT to Use, ## Prerequisites (EP-4 machinery readiness check), ## Two-Lane Discipline (feature deepening = /format-feature-expansion; DOM deepening = /select-deepening-lane based on FULL_DOM/PARTIAL_DOM/FLAT classification), ## Evidence Filing (one item per format per lane per sprint), ## Autonomous Continuation (check_continuation.py → next-sprint.md), ## Forbidden Actions (do not use direction reminders as protocols; do not skip lane selection), ## Completion Gate (evidence declaration filed; autonomous-cycle exits 0 or 3)"
    - id: MS-P4-001-01-04
      action: "Append ESP-PROMPT-9 entry to .supervisor/prompts/prompt-registry.yaml using exact ESP-PROMPT-8 format: id: ESP-PROMPT-9, name: product-deepening, file: .supervisor/prompts/product-deepening.md, description, stage: product_deepening, mode: mutation, inputs, outputs, output_schema: null, successor_rules: [], validation_rules: ['MUST check EP-4 machinery readiness before product mutations'], espanso_source_trigger: ':ff-two-lane-product-deepening', espanso_gap_id: GAP-ESP-009"
    - id: MS-P4-001-01-05
      action: "Append routing entry to .supervisor/prompts/agent-prompt-index.yaml routing_decision_table: condition: 'product format features or DOM need deepening', action: 'use ESP-PROMPT-9 (product-deepening.md); check EP-4 machinery readiness first'"
    - id: MS-P4-001-01-06
      action: "Run: python tools/supervisor/validate_prompt_registry.py"
      expected_output: "Exit 0"
      failure_handling: "If exit 1: read the error message. If 'MISSING_FRONTMATTER_FIELD': the .md front matter has a wrong or missing field. Fix the specific field, not the validator."
  evidence_required: "product-deepening.md exists with front matter; validator exits 0"
  next_valid: TC-P4-001-02
```

**TC-P4-001-02 — Create format-readme-governance.md (ESP-PROMPT-10)**
```yaml
child_taskcard:
  id: TC-P4-001-02
  parent: TC-P4-001
  status: TODO
  preconditions: [TC-P4-001-01 CLOSED]
  title: "Create .supervisor/prompts/format-readme-governance.md and register"
  allowed_files:
    - .supervisor/prompts/format-readme-governance.md  (create)
    - .supervisor/prompts/prompt-registry.yaml  (append)
    - .supervisor/prompts/agent-prompt-index.yaml  (append)
  scope_note: "DISTINCT from readme-governance.md (ESP-PROMPT-2) which governs the ROOT README. This governs per-format src/python/{format}/README.md files."
  micro_steps:
    - id: MS-P4-001-02-01
      action: "Read Espanso source entries for CANDIDATE_ESP10: ':ff-format-readme-hardening' (new variant, entry 56 — newer one is canonical per conflict resolution). Extract body content."
    - id: MS-P4-001-02-02
      action: "Create .supervisor/prompts/format-readme-governance.md with 8-field front matter: prompt_id=ESP-PROMPT-10, title='Per-Format README Governance', context_profile=full, mutating=true"
    - id: MS-P4-001-02-03
      action: "Write body: ## Scope (ONLY src/python/{format}/README.md — NOT root README, which is ESP-PROMPT-2), ## Preservation Rules (no section removed without evidence it is false/obsolete/contradictory), ## Key Difference from Root README (format READMEs contain API examples that must be tested against installed package), ## Execution Protocol (read current README; inventory sections; verify API examples with installed package; update stale examples; add missing sections), ## Forbidden (replacing README from scratch; removing human-authored context without evidence), ## Completion Gate (README updated; API examples verified against installed package)"
    - id: MS-P4-001-02-04
      action: "Append ESP-PROMPT-10 entry to prompt-registry.yaml"
    - id: MS-P4-001-02-05
      action: "Append routing entry to agent-prompt-index.yaml: condition: 'per-format src/python/{format}/README.md needs governance (NOT root README)', action: 'use ESP-PROMPT-10 (format-readme-governance.md); for root README use ESP-PROMPT-2'"
    - id: MS-P4-001-02-06
      action: "Run: python tools/supervisor/validate_prompt_registry.py → exit 0"
  evidence_required: "format-readme-governance.md exists; validator exits 0"
  next_valid: TC-P4-001-03
```

**TC-P4-001-03 — Create analytics-migration.md (ESP-PROMPT-11)**
```yaml
child_taskcard:
  id: TC-P4-001-03
  parent: TC-P4-001
  status: TODO
  preconditions: [TC-P4-001-02 CLOSED]
  title: "Create .supervisor/prompts/analytics-migration.md and register"
  borderline_note: "This is borderline CANDIDATE vs ARCHIVED. Include because the migration is active. If migration completes before this sprint, update disposition to ARCHIVED."
  allowed_files:
    - .supervisor/prompts/analytics-migration.md  (create)
    - .supervisor/prompts/prompt-registry.yaml  (append)
    - .supervisor/prompts/agent-prompt-index.yaml  (append)
  micro_steps:
    - id: MS-P4-001-03-01
      action: "Read Espanso source entries for CANDIDATE_ESP11: ':ff-inventory-analytics', ':ff-decide-analytics-migrations', ':ff-migrate-analytics-batches', ':ff-verify-no-analytics'"
    - id: MS-P4-001-03-02
      action: "Create .supervisor/prompts/analytics-migration.md with 8-field front matter: prompt_id=ESP-PROMPT-11, title='Analytics Migration Protocol (4-Phase)', context_profile=full, mutating=true"
    - id: MS-P4-001-03-03
      action: "Write body with 4 phases: Phase 1 Inventory (read-only: catalog every _analytics file, symbol, caller, test, fixture, template, generator — produce decision candidates), Phase 2 Decision (assign disposition per symbol: RETAIN_IN_PLACE/MERGE_INTO_CLASS/REMOVE/SERVICE_EXTRACT — each must trace to GAP-* + spec fact; analytics suspension note: mod_prime_times_multiplier functions permanently forbidden per MEMORY.md), Phase 3 Migration (repair generators and templates first; execute pilots; migrate retained behavior with its tests; remove obsolete behavior only after closeout), Phase 4 Verification (scan src/, tests/, fixtures/, generated/, templates/, imports, packages — zero residuals required; verify no machinery can regenerate _analytics), ## Completion Gate (Phase 4 passes with 0 residuals)"
    - id: MS-P4-001-03-04
      action: "Append ESP-PROMPT-11 entry to prompt-registry.yaml"
    - id: MS-P4-001-03-05
      action: "Append routing entry to agent-prompt-index.yaml: condition: '_analytics migration is needed', action: 'use ESP-PROMPT-11 (analytics-migration.md); check analytics suspension rule first'"
    - id: MS-P4-001-03-06
      action: "Run: python tools/supervisor/validate_prompt_registry.py → exit 0"
  evidence_required: "analytics-migration.md exists; validator exits 0"
  next_valid: TC-P6-001
```

---

### TC-P6-001 — Add Schema Enforcement Phase 13

```yaml
taskcard:
  id: TC-P6-001
  type: PARENT
  status: PROPOSED
  title: "Add Phase 13 (schema validation) to sprint_executor_validate.py"
  execution_step: STEP 7 (after TC-P4-001; independent of P1-P5 but lower priority)
  source_requirements: [REQ-SCHEMA-001, REQ-SCHEMA-002, REQ-SCHEMA-003]
  allowed_paths:
    - tools/supervisor/sprint_executor_validate.py  (edit, insert after line 667)
  forbidden_paths:
    - .supervisor/schemas/  (schemas must not be modified)
    - .supervisor/prompts/
    - CLAUDE.md
    - src/
  phase_12_location: line 667 in sprint_executor_validate.py
  jsonschema_status: INSTALLED (confirmed in .venv/Lib/site-packages/jsonschema/)
  parent_acceptance_criteria:
    - "Phase 13 appears in validator output when run against a recent evidence declaration"
    - "Output shows PASS, WARN, or SKIP (never unhandled exception)"
    - "Existing validator behavior (exit codes for phases 1-12) unchanged"
  children:
    - TC-P6-001-01
    - TC-P6-001-02
```

**TC-P6-001-01 — Implement Phase 13 function and insert**
```yaml
child_taskcard:
  id: TC-P6-001-01
  parent: TC-P6-001
  status: TODO
  allowed_files:
    - tools/supervisor/sprint_executor_validate.py  (edit)
  micro_steps:
    - id: MS-P6-001-01-01
      action: "Read tools/supervisor/sprint_executor_validate.py lines 660-690 to see exact text of Phase 12 block and what follows it"
      expected_output: "Know the exact text at line 667 and the lines immediately following it"
    - id: MS-P6-001-01-02
      action: "Write function validate_against_schema(doc: dict, schema_path: Path) → tuple[str, list[str]]: try to import jsonschema; if ImportError return ('SKIP_NO_JSONSCHEMA', []); load schema JSON from schema_path; call jsonschema.validate(doc, schema); return ('PASS', []) on success; on ValidationError return ('WARN', [f'Schema violation: {e.message} at {path}']); on other Exception return ('SKIP_ERROR', [str(e)])"
    - id: MS-P6-001-01-03
      action: "Use Edit tool to add Phase 13 block AFTER the Phase 12 block (after line 667). The new block: '# --- Phase 13: JSON Schema validation (WARN only) ---', schema_path = REPO_ROOT / '.supervisor/schemas/evidence-declaration.schema.json', phase13_status, phase13_warns = validate_against_schema(doc, schema_path), warnings.extend(phase13_warns)"
      note: "The function must be inserted ABOVE the call site (Python reads top to bottom). Add the function definition before the main validation function or in a helper section."
    - id: MS-P6-001-01-04
      action: "Run: python tools/supervisor/sprint_executor_validate.py --help to confirm no import errors"
      expected_output: "Help text displayed; no exception"
  evidence_required: "No import errors; Phase 13 function exists"
  next_valid: TC-P6-001-02
```

**TC-P6-001-02 — Run against real evidence declaration and verify output**
```yaml
child_taskcard:
  id: TC-P6-001-02
  parent: TC-P6-001
  status: TODO
  preconditions: [TC-P6-001-01 CLOSED]
  allowed_files: [] (read-only; runs tool against existing evidence)
  micro_steps:
    - id: MS-P6-001-02-01
      action: "Find most recent evidence declaration: ls -t .local/evidences/ | head -1 then: python tools/supervisor/sprint_executor_validate.py .local/evidences/{that_run}/evidence-declaration.yaml"
      expected_output: "Output contains 'Phase 13' line with status PASS, WARN, or SKIP"
      failure_handling: "If output does not contain 'Phase 13': the insert was in the wrong location or the phase block is not reached. Read the file around line 667 again and verify the insertion."
    - id: MS-P6-001-02-02
      action: "Confirm exit code is same as before the change (exit 0 if the declaration was valid before)"
  evidence_required: "Phase 13 line visible in output; exit code unchanged from pre-change"
  closeout_criteria: "Both checks pass"
```

---

## PART E — EXECUTION CONTROL

### E.1 Dependency DAG

```yaml
execution_dag:
  nodes:
    - id: TC-P5-001
      description: "Build validate_prompt_registry.py"
      execution_step: 0
      depends_on: []
    - id: TC-P1-001
      description: "Build espanso_staleness_checker.py"
      execution_step: 1
      depends_on: []
      parallel_safe_with: [TC-P5-001]
    - id: TC-P2-001
      description: "Add EP-1 to EP-5 to CLAUDE.md"
      execution_step: 2
      depends_on: [TC-P5-001]
      note: "Depends on TC-P5-001 so validator can be run after to confirm no breakage"
    - id: TC-P1-001-backfill-run
      description: "Run staleness checker --backfill-hashes"
      execution_step: 3
      depends_on: [TC-P1-001]
      note: "This is the first EXECUTION of TC-P1-001 tool, after it's built"
    - id: TC-P3-001
      description: "Update provenance map dispositions"
      execution_step: 4
      depends_on: [TC-P1-001-backfill-run, TC-P2-001]
    - id: TC-P4-001
      description: "Create 3 new canonical prompts"
      execution_step: 6
      depends_on: [TC-P3-001, TC-P5-001]
    - id: TC-P6-001
      description: "Add Phase 13 to sprint_executor_validate.py"
      execution_step: 7
      depends_on: []
      parallel_safe_with: [all other TCs]
  critical_path: [TC-P5-001] → [TC-P2-001] → [TC-P3-001] → [TC-P4-001]
  file_ownership_locks:
    - file: tools/supervisor/validate_prompt_registry.py
      owner: TC-P5-001
    - file: tools/supervisor/espanso_staleness_checker.py
      owner: TC-P1-001
    - file: CLAUDE.md
      owner: TC-P2-001
    - file: .supervisor/prompts/espanso-provenance-map.yaml
      owner: TC-P1-001 (backfill), TC-P3-001 (dispositions)
      sequential: true
    - file: .supervisor/prompts/product-deepening.md
      owner: TC-P4-001-01
    - file: .supervisor/prompts/format-readme-governance.md
      owner: TC-P4-001-02
    - file: .supervisor/prompts/analytics-migration.md
      owner: TC-P4-001-03
    - file: .supervisor/prompts/prompt-registry.yaml
      owner: TC-P4-001 (append only)
    - file: .supervisor/prompts/agent-prompt-index.yaml
      owner: TC-P4-001 (append only)
    - file: tools/supervisor/sprint_executor_validate.py
      owner: TC-P6-001
  parallel_execution_safety:
    safe: [TC-P5-001 + TC-P1-001]
    safe: [TC-P6-001 + any other TC]
    unsafe: [TC-P3-001 + TC-P4-001 on provenance map — must be sequential]
    unsafe: [TC-P2-001 + TC-P3-001 on CLAUDE.md — P2 must complete first]
```

### E.2 Validation Matrix

| Check | Command | Expected | Failure Action | Mandatory |
|---|---|---|---|---|
| P5 baseline | `python tools/supervisor/validate_prompt_registry.py` | Exit 0 | Debug — do not skip | YES |
| P5 tests | `.venv/Scripts/pytest tests/supervisor/test_validate_prompt_registry.py -v` | 4 PASSED | Debug — do not skip | YES |
| P1 tests | `.venv/Scripts/pytest tests/supervisor/test_espanso_staleness_checker.py -v` | 4 PASSED | Debug — do not skip | YES |
| P1 backfill | `python tools/supervisor/espanso_staleness_checker.py --backfill-hashes ...` | 118 entries populated | Check line_range indexing | YES |
| P2 rules | `python -c "text=open('CLAUDE.md').read(); rules=['EP-1','EP-2','EP-3','EP-4','EP-5']; [assert r in text for r in rules]"` | No assertion error | Re-apply edit | YES |
| P2 budget | `python -c "print(len(open('CLAUDE.md').readlines()))"` | <= 700 | Compress rules | YES |
| P3 sha256 | `python -c "... check all entries have body_sha256 ..."` | PASS | Run backfill again | YES |
| P3 detect | `python tools/supervisor/espanso_staleness_checker.py` | Exit 0 (or 2 with only expected NEW) | Investigate MODIFIED entries | YES |
| P4-9 front matter | Check each .md file front matter | 8 fields correct | Fix specific file | YES |
| P4-9 validator | `python tools/supervisor/validate_prompt_registry.py` | Exit 0 | Debug specific failure | YES |
| P4-10 validator | Same | Exit 0 | Debug | YES |
| P4-11 validator | Same | Exit 0 | Debug | YES |
| P6 phase 13 | Run validator against evidence declaration | Phase 13 in output | Check insertion point | YES |
| Idempotency | Run all validators twice | Same result | Investigate mutation | YES |

### E.3 Negative Controls

| Control | What It Detects | How to Test |
|---|---|---|
| Missing file reference | Check 1 in validate_prompt_registry.py | Add nonexistent file to registry; confirm exit 1 |
| Missing front matter | Check 2 | Create .md without ---; add to registry; confirm exit 1 |
| Duplicate prompt_id | Check 3 | Register same id twice; confirm exit 1 |
| MODIFIED Espanso body | Staleness checker | Change one character in Espanso file body; confirm MODIFIED reported |
| NEW Espanso entry untracked | Staleness checker | Add entry to synthetic file; confirm NEW reported |
| Schema violation | Phase 13 | Manually remove required field from evidence declaration copy; confirm WARN |

### E.4 Evidence Contract

```yaml
evidence_contract:
  authoritative_plan: "plans/.claude/imperative-coalescing-bengio.md"
  evidence_root: ".local/evidences/{run_id}/"
  required_evidence_per_taskcard:
    TC-P5-001:
      - pytest 4 PASSED output for test_validate_prompt_registry.py
      - validate_prompt_registry.py exits 0 on live system
    TC-P1-001:
      - pytest 4 PASSED output for test_espanso_staleness_checker.py
      - backfill run output (118 entries populated)
    TC-P2-001:
      - EP-1 through EP-5 verification python -c output
      - CLAUDE.md line count <= 700
    TC-P3-001:
      - sha256 presence verification pass
      - detect mode output showing expected UNCHANGED count
    TC-P4-001:
      - For each prompt: .md file exists + front matter fields verified
      - validate_prompt_registry.py exit 0 after each prompt registered
    TC-P6-001:
      - sprint_executor_validate.py output showing Phase 13 line
      - Exit code unchanged
  evidence_must_not_contain:
    - Alternative execution instructions
    - Competing plan references
    - Claims of completion without terminal output
```

### E.5 Quality Scoring Dimensions (Acceptance Threshold: 4/5)

| Dimension | TC-P5 | TC-P1 | TC-P2 | TC-P3 | TC-P4 | TC-P6 |
|---|---|---|---|---|---|---|
| Requirement correctness | 5 checks implemented | 4 modes implemented | 5 rules present | Dispositions correct | 8-field format correct | WARN not FAIL |
| Implementation correctness | Exit codes correct | SHA256 idempotent | Rules are accurate | Default rule applied | Body content synthesized from source | Phase 13 inserted correctly |
| Test coverage | 4 test cases | 4 test cases | Verification script | detect mode output | validator exit 0 | Phase 13 in output |
| Evidence completeness | pytest output | pytest + backfill output | verification output | detect output | per-prompt evidence | tool output |
| Regression safety | Existing registry passes | Map unchanged in detect mode | CLAUDE.md parseable | Existing entries unchanged | Existing prompts unchanged | Exit codes unchanged |

---

## PART F — COMPLETION GATE AND EXECUTION HANDOFF

### F.1 Completion Gate (Unchanged from original)

The mission closes when ALL of the following are confirmed:

- [ ] `tools/supervisor/espanso_staleness_checker.py` exists and 4 tests pass
- [ ] `--backfill-hashes` run: all 118 provenance map entries have `body_sha256`
- [ ] Staleness checker exits 0 after backfill on current Espanso file
  (exits 2 only for new entries since last extraction, which should be registered)
- [ ] 5 policy rules EP-1 through EP-5 present in CLAUDE.md
- [ ] CLAUDE.md total lines <= 700
- [ ] Provenance map: all EP-sourced entries have SUPERSEDED_BY_CLAUDE_MD disposition
- [ ] Provenance map: CANDIDATE_ESP9/10/11 dispositions applied
- [ ] `tools/supervisor/validate_prompt_registry.py` exists and 4 tests pass
- [ ] Validator exits 0 on unmodified current system (baseline)
- [ ] 3 new prompt files exist with correct 8-field front matter:
  - `product-deepening.md` (ESP-PROMPT-9)
  - `format-readme-governance.md` (ESP-PROMPT-10)
  - `analytics-migration.md` (ESP-PROMPT-11)
- [ ] 3 new entries in `prompt-registry.yaml`
- [ ] 3 new routing entries in `agent-prompt-index.yaml`
- [ ] Validator exits 0 after all 3 prompts registered
- [ ] Phase 13 present in `sprint_executor_validate.py`; output shows Phase 13 result
- [ ] Second run of staleness checker exits 0 (idempotency confirmed)
- [ ] Second run of registry validator exits 0 (idempotency confirmed)

**NOT in completion gate (explicit non-goals):**
- All 107 Espanso entries need NO canonical files. 3 prompts + 5 CLAUDE.md rules cover the gaps.
- No human-readable prompt catalog required.
- No new skills or capabilities registered (no new orphaned 1:1:1 parity entries).
- No changes to existing ESP-PROMPT-1 through ESP-PROMPT-8 files.

### F.2 Execution Handoff

**For the execution agent beginning work on this plan:**

1. Read this plan file completely before starting.
2. Identify the first PROPOSED parent taskcard in the corrected execution order: **TC-P5-001** (build the registry validator).
3. Select child taskcard **TC-P5-001-01** (inspect existing schemas).
4. Confirm preconditions: no preconditions for TC-P5-001-01.
5. Confirm allowed files: `.supervisor/prompts/prompt-registry.yaml`, `.supervisor/prompts/agent-prompt-index.yaml`, `.supervisor/prompts/bounded-executor.md` (read only).
6. Execute micro-step MS-P5-001-01-01 and only that step. Capture output before proceeding.
7. Update TC-P5-001-01 status to IN_PROGRESS before starting. Update each micro-step to ACTIVE/COMPLETE as you go.
8. Do not mark a child CLOSED until all its micro-steps are COMPLETE and the evidence requirement is met.
9. Do not mark a parent CLOSED until all its children are CLOSED and the parent acceptance criteria pass.
10. After TC-P5-001 is CLOSED: start TC-P1-001 in parallel. Both can proceed simultaneously since they touch different files.
11. After TC-P5-001 and TC-P1-001 are CLOSED: run TC-P2-001 (CLAUDE.md rules).
12. The backfill run (TC-P1-001 tool execution) is part of TC-P3-001-01's precondition.
13. TC-P4-001 starts only after TC-P3-001 and TC-P5-001 are both CLOSED.
14. TC-P6-001 can run at any point but is lowest priority.
15. After all parents are CLOSED: verify the completion gate checklist. Do not close the mission until every item is confirmed.

**The execution agent must NOT:**
- Choose work not in this plan's taskcard hierarchy
- Edit existing ESP prompt .md files
- Register new skills or capability_ids (breaks 1:1:1 parity)
- Add entries to the `existing_prompts` (frozen) section of prompt-registry.yaml
- Mark a taskcard CLOSED without running the associated verification commands and capturing the output

---

## PART G — RECONCILIATION

### G.1 Single Plan Authority Audit

- One authoritative plan: YES — `plans/.claude/imperative-coalescing-bengio.md`
- Competing plan versions created: NO
- Prior draft in `~/.claude/plans/`: superseded by in-repo copy (per MEMORY.md Step 0 rule)
- Supporting artifacts: embedded in this plan (not separate executable plans)

### G.2 No-Actionable-Item-Loss Audit

| Plan Actionable | Represented By | Status |
|---|---|---|
| Build staleness tool | TC-P1-001 | COVERED |
| Build --backfill-hashes mode | TC-P1-001-02 | COVERED |
| Build --update-map mode | TC-P1-001-03 | COVERED |
| 4 staleness tests | TC-P1-001-04 | COVERED |
| Add EP-1 rule to CLAUDE.md | TC-P2-001-02 | COVERED |
| Add EP-2 through EP-5 rules | TC-P2-001-02 | COVERED |
| Verify line budget | TC-P2-001-02 + TC-P2-001-03 | COVERED |
| Backfill SHA256 on map | TC-P3-001-01 | COVERED |
| Update dispositions | TC-P3-001-02 | COVERED |
| Apply default rule for undiscussed entries | TC-P3-001-02 (note) | COVERED |
| Create product-deepening.md | TC-P4-001-01 | COVERED |
| Create format-readme-governance.md | TC-P4-001-02 | COVERED |
| Create analytics-migration.md | TC-P4-001-03 | COVERED |
| Register 3 prompts in registries | TC-P4-001-01/02/03 steps 04-05 | COVERED |
| Build registry validator | TC-P5-001 | COVERED |
| 4 registry validator tests | TC-P5-001-04 | COVERED |
| Freeze existing_prompts section | TC-P5-001-05 | COVERED |
| Add Phase 13 to sprint_executor_validate.py | TC-P6-001-01 | COVERED |
| Verify Phase 13 in output | TC-P6-001-02 | COVERED |
| Idempotency verification | Completion gate item + G.2 | COVERED |

### G.3 Bug Fix Confirmation

| Bug | Fix | Taskcard |
|---|---|---|
| BUG-001: Wrong front matter template | Corrected to 8-field actual format | TC-P4-001 critical_front_matter_fix |
| BUG-002: Circular dependency Phase 4/5 | Phase 5 built first (STEP 0) | Corrected DAG in E.1 |
| BUG-003: No --backfill-hashes mode | Added to Phase 1 tool design | TC-P1-001-02 |
| BUG-004: No default rule for undiscussed entries | Explicit default in TC-P3-001 | TC-P3-001-02 note |
| BUG-005: CLAUDE.md insertion "gap" concern | Insertion is after Governance section content, not squeezed into 8-line gap | TC-P2-001-01 |

### G.4 Idempotency Rules

- Taskcard IDs are stable: TC-P1-001 through TC-P6-001 + children. Rerun re-identifies these exact IDs.
- Staleness checker: second run on unchanged files exits 0 (idempotent by SHA256 comparison)
- Registry validator: exits 0 on any system where all constraints are satisfied (idempotent)
- provenance map backfill: second run skips entries that already have body_sha256 (idempotent)
- CLAUDE.md rules: second run verification script exits 0 (rules already present)
- New prompt files: already-existing files are not recreated (must check existence before creating)

---

## PART H — WHAT IS NOT BUILT (Preserved)

| Proposed Item | Rejected Because |
|---|---|
| 20 new canonical prompt files | Creates maintenance burden without adding missing capabilities |
| Human-readable prompt catalog | Goes stale immediately; agent-prompt-index.yaml is machine-readable |
| New skills for ESP-PROMPT-9 through 11 | Breaks 1:1:1 parity; these prompts orchestrate existing skills |
| Prompt family register YAML | Provenance map disposition encodes family membership |
| YAML schema for prompt front matter | Phase 5 validator validates front matter directly in Python |
| New routing in capability-routing-registry.yaml | Routing already in agent-prompt-index.yaml; double-registration creates sync problem |

---

## Final Verdict Template

`ESPANSO_PROMPTS_CANONICALIZED_WIRED_AND_AUTONOMOUSLY_DISCOVERABLE`
