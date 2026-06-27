# Cross-Agent Skill and Command Parity — Canonical Capability Registry

**Plan:** rustling-gliding-finch
**Type:** machinery_hardening
**Mission ID:** CROSS-AGENT-PARITY-001
**Created:** 2026-06-26
**Enhanced:** 2026-06-26 (micro-taskcardization pass)
**Authoritative plan path:** `C:\Users\prora\.claude\plans\rustling-gliding-finch.md`
**Execution authority:** THIS FILE ONLY

---

## § PREFLIGHT

```yaml
taskcardization_preflight:
  repository_root: "c:\\Users\\prora\\OneDrive\\Documents\\GitHub\\format-factory"
  branch: main
  head: "a3ed0a0c (latest known)"
  active_plan_path: "C:\\Users\\prora\\.claude\\plans\\rustling-gliding-finch.md"
  active_plan_title: "Cross-Agent Skill and Command Parity — Canonical Capability Registry"
  plan_format: "Markdown with inline YAML, flat taskcard sections"
  plan_authority_source: "User-initiated plan mode session"
  approximate_plan_lines: 432
  major_sections: 6
  existing_taskcard_sections: 15  # TC-CAP-001 through TC-CAP-015
  existing_taskcard_format: "flat Markdown (Type/Status/Files/Steps/Verification)"
  existing_lanes: none
  existing_waves: none
  existing_phases: none
  existing_gates: "none explicit — only Verification steps"
  existing_state_vocabulary: ["not_started"]
  existing_validation_model: "one Verification line per taskcard — insufficient"
  existing_evidence_model: "none — no evidence obligations defined"
  existing_normalization_conventions: "TC-CAP-NNN naming"
  existing_execution_handoff: "Critical Files section — insufficient for weak agent"
  duplicate_plan_risk: LOW

defects_in_original_plan:
  - "No parent-child taskcard hierarchy — all 15 are flat"
  - "No micro-steps — only numbered bullet points"
  - "No machine state model — only 'not_started' status"
  - "No rollback rules on any taskcard"
  - "No scope discipline — missing allowed/forbidden paths"
  - "No evidence obligations"
  - "No quality gates or reroute rules"
  - "No stop conditions"
  - "No dependency DAG — only informal 'Dependencies:' text"
  - "TC-CAP-012 circular: 'run /sync-capabilities' before tool is created"
  - "TC-CAP-015 has 3 tests as bullets — needs micro-step decomposition"
  - "codex-adapter.md referenced but not analyzed (EXISTS, needs content audit)"
  - "Pilots table covers only 8 of 15 required pilots"
  - "Missing INVESTIGATION phase for baseline recon"
  - "TC-CAP-007 drift logic is complex — needs deeper decomposition"
  - "Missing: normalize_capabilities.py (prompt requirement §30)"
  - "AGENTS.md insertion point 'after §A2a, before §AG0' is imprecise — A. section is long"
```

---

## § PLAN AUTHORITY VERDICT

```yaml
active_plan_authority_verdict:
  authoritative_plan: "C:\\Users\\prora\\.claude\\plans\\rustling-gliding-finch.md"
  authority_source: "User plan-mode session, conversation context"
  competing_plans_found: false
  duplicate_risk: LOW
  verdict: SINGLE_AUTHORITY_CONFIRMED
  action: "Enhance this file in place. No alternative plan files to reconcile."
```

---

## § CONTEXT (preserved from original)

The repository has 93 skills in `.supervisor/skill-registry.yaml` and 93 corresponding Claude commands in `.claude/commands/*.md`, with bidirectional cross-references via `command_file` (skills→commands) and `skill_id` (commands→skills). The infrastructure is mature for Claude Code. However:

1. No **canonical agent-neutral capability registry** exists — the skill-registry is Claude/supervisor-centric
2. **AGENTS.md has no generated discovery section** — Codex and other agents cannot programmatically discover capabilities
3. No **cross-agent parity validator** measures whether every skill has a discoverable command and vice versa
4. No **drift detector** catches divergence between source registries and committed adapters
5. **CI lacks cross-agent parity enforcement** — only skill attribution for `src/` mutations exists (advisory, `continue-on-error: true`)
6. No **`tools/capability_sync/` toolchain** for adapter generation and sync
7. **CLAUDE.md has no generated capability index** section with stable markers
8. `docs/governance/codex-adapter.md` EXISTS (confirmed) but has not been analyzed for completeness

**Intended outcome:** Every governed capability is equally discoverable and executable by all supported agents (Claude Code, Codex, CI, supervisor), enforced automatically via CI and pre-commit, without needing this plan to run again for routine maintenance.

**Architecture principle:** `.supervisor/skill-registry.yaml` remains the authoritative source. The new `.governance/capabilities/registry.yaml` is a **compiled output** generated from skill-registry + command-registry + routing-registry — not a third hand-maintained source.

---

## § ARCHITECTURE (preserved + clarified)

```
SOURCE LAYER (authoritative, never generated, never modified by this plan's tools)
  .supervisor/skill-registry.yaml           [93 skills, list under "skills:" key]
  .claude/commands/command-registry.yaml    [59+ entries under "commands:" key]
  .supervisor/capability-routing-registry.yaml [30 routes]
  .claude/commands/*.md                     [94 files: 93 impl + 1 _readme + command-registry.yaml]

        |
        v  tools/capability_sync/inventory_capabilities.py  [NEW]
        |
COMPILED REGISTRY (generated, version-stamped, never-delete invariant)
  .governance/capabilities/registry.yaml

        |
        v  tools/capability_sync/validate_parity.py  [NEW]
        |
PARITY REPORT (generated per run)
  .governance/capabilities/parity-report.yaml

        |
        v  tools/capability_sync/generate_discovery_indexes.py  [NEW]
        |
AGENT ADAPTERS (generated sections spliced into existing files)
  CLAUDE.md   <!-- BEGIN:CAPABILITY-INDEX --> ... <!-- END:CAPABILITY-INDEX -->
  AGENTS.md   <!-- BEGIN:CAPABILITY-DISCOVERY --> ... <!-- END:CAPABILITY-DISCOVERY -->

        |
        v  tools/capability_sync/detect_drift.py  [NEW, read-only, CI-runnable]
        |
CI ENFORCEMENT
  .github/workflows/ci.yml       [new job: capability-parity, continue-on-error: false]
  .pre-commit-config.yaml        [new local hook: capability-registry-drift-check]
```

**Orchestrator:** `tools/capability_sync/run_sync.py --mode full|validate|drift-only|inventory-only`

---

## § KEY DESIGN DECISIONS (preserved + corrected)

- **`agent_surfaces` field is computed, not stored** in skill-registry. `inventory_capabilities.py` derives: `claude_code = command_file exists on disk`, `codex = True for all (Codex reads skill-registry per AGENTS.md §A2)`, `ci = appears as preferred_skill_id in routing-registry`.
- **Never-delete invariant** for registry.yaml: deprecated skills carry forward with `status: deprecated`. Re-runs merge fresh inventory with prior registry — never remove entries.
- **Drift detection strips `generated_at`** before hashing — timestamps don't trigger false positives.
- **BEGIN/END marker format:** `<!-- BEGIN:CAPABILITY-INDEX generated={ts} source=.governance/capabilities/registry.yaml -->` — `generated={ts}` attribute is stripped before content hashing.
- **`agent_surfaces.codex`** defaults to `true` for all skills. Set `codex_excluded: true` in skill-registry to narrow (not used by any current skill).
- **Do NOT add `agent_surfaces` to skill-registry.yaml source** — the compiled registry carries it.
- **Pattern source:** `tools/supervisor/sync_skill_command_registry.py` — use its `_load()`, `_save()`, backup, and report structure exactly.
- **Circular dependency fix (TC-CAP-012):** Register new skills in source registries BEFORE running `/sync-capabilities`. The registration is done via direct YAML edit + `run_sync.py --mode inventory-only`, not by invoking the not-yet-registered command.
- **AGENTS.md insertion point (corrected):** After line containing `**A2a. Codex Governance Adapter.**` closing paragraph (after "DEC-014 status: **activated**..."), before section `## B. Phase and Plan Verification`. Check by reading AGENTS.md at execution time to find exact line number.

---

## § SECTION PROCESSING LEDGER

```yaml
section_processing_ledger:
  - section_id: S-CTX
    section_title: Context
    section_type: background
    analysis_completed: yes
    actionable_items_found: 0
    existing_taskcards_found: 0
    missing_taskcards: 0
    change_status: preserved
    reconciliation_status: complete

  - section_id: S-ARCH
    section_title: Architecture
    section_type: design
    analysis_completed: yes
    actionable_items_found: 0
    existing_taskcards_found: 0
    ambiguities: ["94 files count includes command-registry.yaml and _readme — clarified in text"]
    change_status: clarified
    reconciliation_status: complete

  - section_id: S-DD
    section_title: Key Design Decisions
    section_type: design
    analysis_completed: yes
    actionable_items_found: 2
    existing_taskcards_found: 0
    missing_taskcards: ["circular dependency fix for TC-CAP-012", "AGENTS.md insertion point clarification"]
    change_status: expanded
    reconciliation_status: complete

  - section_id: S-TC001
    section_title: TC-CAP-001 Schema Foundation
    section_type: implementation
    analysis_completed: yes
    actionable_items_found: 4
    existing_taskcards_found: 1
    missing_taskcards: ["directory creation step", "schema validation step", "meta-validation"]
    ambiguities: ["'directory structure' step is too broad"]
    change_status: decomposed_to_parent_child
    reconciliation_status: complete

  - section_id: S-TC002
    section_title: TC-CAP-002 Inventory Tool
    section_type: implementation
    analysis_completed: yes
    actionable_items_found: 9
    existing_taskcards_found: 1
    missing_taskcards: ["individual function-level micro-steps"]
    ambiguities: ["LOC budget listed without enforcement mechanism"]
    change_status: decomposed_to_parent_child
    reconciliation_status: complete

  - section_id: S-TC003
    section_title: TC-CAP-003 Parity Validator
    section_type: implementation
    analysis_completed: yes
    actionable_items_found: 5
    existing_taskcards_found: 1
    missing_taskcards: ["P3/P4 checks not specified", "exit code handling"]
    change_status: decomposed_to_parent_child
    reconciliation_status: complete

  - section_id: S-TC004
    section_title: TC-CAP-004 Discovery Index Generator
    section_type: implementation
    analysis_completed: yes
    actionable_items_found: 4
    existing_taskcards_found: 1
    ambiguities: ["'pure function' — needs explicit no-import-at-module-level constraint"]
    change_status: decomposed_to_parent_child
    reconciliation_status: complete

  - section_id: S-TC005
    section_title: TC-CAP-005 CLAUDE.md Updater
    section_type: implementation
    analysis_completed: yes
    actionable_items_found: 6
    existing_taskcards_found: 1
    missing_taskcards: ["what happens when file length changes significantly"]
    change_status: decomposed_to_parent_child
    reconciliation_status: complete

  - section_id: S-TC006
    section_title: TC-CAP-006 AGENTS.md Updater
    section_type: implementation
    analysis_completed: yes
    actionable_items_found: 6
    existing_taskcards_found: 1
    ambiguities: ["'after §A2a, before §AG0' — AG0 is far from A2a; clarified as 'before ## B.'"]
    change_status: decomposed_to_parent_child
    reconciliation_status: complete

  - section_id: S-TC007
    section_title: TC-CAP-007 Drift Detector
    section_type: implementation
    analysis_completed: yes
    actionable_items_found: 6
    existing_taskcards_found: 1
    ambiguities: ["'import as library, not subprocess' — needs explicit function boundary"]
    change_status: decomposed_to_parent_child
    reconciliation_status: complete

  - section_id: S-TC008
    section_title: TC-CAP-008 Sync Orchestrator
    section_type: implementation
    analysis_completed: yes
    actionable_items_found: 4
    existing_taskcards_found: 1
    change_status: decomposed_to_parent_child
    reconciliation_status: complete

  - section_id: S-TC009
    section_title: TC-CAP-009 /capability-status Command
    section_type: claude_adapter
    analysis_completed: yes
    actionable_items_found: 4
    existing_taskcards_found: 1
    change_status: decomposed_to_parent_child
    reconciliation_status: complete

  - section_id: S-TC010
    section_title: TC-CAP-010 /sync-capabilities Command
    section_type: claude_adapter
    analysis_completed: yes
    actionable_items_found: 4
    existing_taskcards_found: 1
    change_status: decomposed_to_parent_child
    reconciliation_status: complete

  - section_id: S-TC011
    section_title: TC-CAP-011 /validate-capability-parity Command
    section_type: claude_adapter
    analysis_completed: yes
    actionable_items_found: 3
    existing_taskcards_found: 1
    change_status: decomposed_to_parent_child
    reconciliation_status: complete

  - section_id: S-TC012
    section_title: TC-CAP-012 Register New Skills
    section_type: registry_repair
    analysis_completed: yes
    actionable_items_found: 3
    existing_taskcards_found: 1
    ambiguities: ["'run /sync-capabilities' is circular — command must be registered before tool exists"]
    change_status: corrected_circular_dependency
    reconciliation_status: complete

  - section_id: S-TC013
    section_title: TC-CAP-013 CI Integration
    section_type: ci_enforcement
    analysis_completed: yes
    actionable_items_found: 2
    existing_taskcards_found: 1
    change_status: decomposed_to_parent_child
    reconciliation_status: complete

  - section_id: S-TC014
    section_title: TC-CAP-014 Pre-commit Hook
    section_type: ci_enforcement
    analysis_completed: yes
    actionable_items_found: 2
    existing_taskcards_found: 1
    change_status: decomposed_to_parent_child
    reconciliation_status: complete

  - section_id: S-TC015
    section_title: TC-CAP-015 Governance Tests
    section_type: testing
    analysis_completed: yes
    actionable_items_found: 5
    existing_taskcards_found: 1
    missing_taskcards: ["individual test function micro-steps", "CI registration step"]
    change_status: decomposed_to_parent_child
    reconciliation_status: complete

  - section_id: S-PILOTS
    section_title: Pilots
    section_type: validation
    analysis_completed: yes
    actionable_items_found: 15
    existing_taskcards_found: 0
    missing_taskcards: ["pilots 4, 8, 9, 10, 11, 12, 14 not covered"]
    change_status: expanded
    reconciliation_status: complete
```

---

## § NORMALIZED REQUIREMENTS INVENTORY

```yaml
requirements:
  REQ-CAP-001:
    source_section: Context item 1
    description: "Create canonical agent-neutral capability registry at .governance/capabilities/registry.yaml"
    type: artifact_creation
    priority: P0

  REQ-CAP-002:
    source_section: Context item 2
    description: "Add generated discovery section to AGENTS.md with stable BEGIN/END markers"
    type: artifact_mutation
    priority: P0

  REQ-CAP-003:
    source_section: Context item 3
    description: "Build cross-agent parity validator (skill-has-command, command-has-skill)"
    type: tool_creation
    priority: P0

  REQ-CAP-004:
    source_section: Context item 4
    description: "Build drift detector comparing committed registry vs. computed registry"
    type: tool_creation
    priority: P0

  REQ-CAP-005:
    source_section: Context item 5
    description: "Add CI enforcement job (capability-parity) that fails on drift"
    type: ci_addition
    priority: P1

  REQ-CAP-006:
    source_section: Context item 6
    description: "Create tools/capability_sync/ toolchain (inventory, validate, generate, update, detect, orchestrate)"
    type: tool_creation
    priority: P0

  REQ-CAP-007:
    source_section: Context item 7
    description: "Add generated capability index section to CLAUDE.md with stable markers"
    type: artifact_mutation
    priority: P1

  REQ-CAP-008:
    source_section: Context item 8
    description: "Audit docs/governance/codex-adapter.md and update to reference new registry"
    type: artifact_mutation
    priority: P1

  REQ-CAP-009:
    source_section: Architecture
    description: "Implement never-delete invariant in compiled registry"
    type: design_constraint
    priority: P0

  REQ-CAP-010:
    source_section: Architecture
    description: "Add pre-commit hook for drift detection on relevant file changes"
    type: ci_addition
    priority: P1

  REQ-CAP-011:
    source_section: Taskcards
    description: "Register 3 new skills (capability-status, sync-capabilities, validate-capability-parity) in source registries"
    type: registry_update
    priority: P1

  REQ-CAP-012:
    source_section: Taskcards
    description: "Create 3 new Claude command markdown files for the 3 new skills"
    type: artifact_creation
    priority: P1

  REQ-CAP-013:
    source_section: Taskcards
    description: "Write governance tests directly against source registries (defense-in-depth)"
    type: test_creation
    priority: P1

  REQ-CAP-014:
    source_section: Architecture
    description: "Capability schemas (capability.schema.json, parity-report.schema.json) must be valid JSON Schema draft-2020-12"
    type: schema_creation
    priority: P0

  REQ-CAP-015:
    source_section: Verification
    description: "System must be idempotent: second run of run_sync.py --mode full produces no file changes"
    type: quality_constraint
    priority: P0
```

---

## § MACHINE STATE MODEL

### Parent Taskcard States
```
PROPOSED → READY → IN_PROGRESS → CHILDREN_IN_PROGRESS → INTEGRATION_PENDING
  → VERIFIED → SCORED → CLOSED
  → REROUTED (from SCORED if any quality gate < 4/5)
  → BLOCKED (from any non-closed)
  → BLOCKED_EXTERNAL (from any non-closed)
  → DEFERRED_WITH_REASON (from any non-closed)
```

### Child Taskcard States
```
TODO → READY → IN_PROGRESS → IMPLEMENTED → VERIFIED → SCORED → CLOSED
  → REROUTED (from SCORED)
  → BLOCKED / BLOCKED_EXTERNAL / DEFERRED_WITH_REASON
```

### Micro-Step States
```
PENDING → READY → ACTIVE → COMPLETE
                → FAILED → READY (retry)
                → BLOCKED → READY (unblocked)
PENDING → SKIPPED_NOT_APPLICABLE (with reason required)
```

### Invalid Transitions (hard-blocked)
- Any `→ CLOSED` without VERIFIED intermediate
- `TODO → CLOSED` or `READY → CLOSED` (skipping verification)
- `IMPLEMENTED → CLOSED` (must pass VERIFIED)
- Parent `→ CLOSED` while any mandatory child is not CLOSED
- `REROUTED → CLOSED` without rework evidence
- `BLOCKED_EXTERNAL → CLOSED` without unblock evidence
- Child CLOSED while any mandatory micro-step is PENDING, READY, ACTIVE, or FAILED

---

## § DEPENDENCY DAG

```yaml
execution_dag:
  phase_0_recon:
    TC-CAP-P0: {depends_on: [], blocks: [TC-CAP-001, TC-CAP-005, TC-CAP-006, TC-CAP-013]}

  phase_1_schemas:
    TC-CAP-001: {depends_on: [TC-CAP-P0], blocks: [TC-CAP-002, TC-CAP-003]}

  phase_2_core_toolchain:
    TC-CAP-002: {depends_on: [TC-CAP-001], blocks: [TC-CAP-003, TC-CAP-004, TC-CAP-007]}
    TC-CAP-003: {depends_on: [TC-CAP-002], blocks: [TC-CAP-008]}
    TC-CAP-004: {depends_on: [TC-CAP-002], blocks: [TC-CAP-005, TC-CAP-006, TC-CAP-007, TC-CAP-008]}
    TC-CAP-005: {depends_on: [TC-CAP-004], blocks: [TC-CAP-008]}
    TC-CAP-006: {depends_on: [TC-CAP-004], blocks: [TC-CAP-008]}
    TC-CAP-007: {depends_on: [TC-CAP-002, TC-CAP-004], blocks: [TC-CAP-008, TC-CAP-013, TC-CAP-014]}
    TC-CAP-008: {depends_on: [TC-CAP-002, TC-CAP-003, TC-CAP-004, TC-CAP-005, TC-CAP-006, TC-CAP-007], blocks: [TC-CAP-012]}

  phase_3_claude_adapters:
    TC-CAP-009: {depends_on: [TC-CAP-002], blocks: [TC-CAP-012]}
    TC-CAP-010: {depends_on: [TC-CAP-008], blocks: [TC-CAP-012]}
    TC-CAP-011: {depends_on: [TC-CAP-008], blocks: [TC-CAP-012]}

  phase_4_registry:
    TC-CAP-012: {depends_on: [TC-CAP-009, TC-CAP-010, TC-CAP-011, TC-CAP-008], blocks: [TC-CAP-015]}

  phase_5_ci:
    TC-CAP-013: {depends_on: [TC-CAP-007, TC-CAP-012], blocks: []}
    TC-CAP-014: {depends_on: [TC-CAP-007, TC-CAP-012], blocks: []}

  phase_6_tests:
    TC-CAP-015: {depends_on: [TC-CAP-012], blocks: []}

parallel_safe_pairs:
  - [TC-CAP-003, TC-CAP-004]     # both depend only on TC-CAP-002; different files
  - [TC-CAP-005, TC-CAP-006]     # both depend only on TC-CAP-004; different files
  - [TC-CAP-013, TC-CAP-014]     # both depend on TC-CAP-007; different files
  - [TC-CAP-009, TC-CAP-010, TC-CAP-011]   # command files are independent

file_ownership:
  ".governance/capabilities/": [TC-CAP-001, TC-CAP-002, TC-CAP-003]
  "tools/capability_sync/": [TC-CAP-002, TC-CAP-003, TC-CAP-004, TC-CAP-005, TC-CAP-006, TC-CAP-007, TC-CAP-008]
  "CLAUDE.md": [TC-CAP-005]
  "AGENTS.md": [TC-CAP-006]
  ".supervisor/skill-registry.yaml": [TC-CAP-012]
  ".claude/commands/command-registry.yaml": [TC-CAP-012]
  ".claude/commands/capability-status.md": [TC-CAP-009]
  ".claude/commands/sync-capabilities.md": [TC-CAP-010]
  ".claude/commands/validate-capability-parity.md": [TC-CAP-011]
  ".github/workflows/ci.yml": [TC-CAP-013]
  ".pre-commit-config.yaml": [TC-CAP-014]
  "tests/governance/test_capability_parity.py": [TC-CAP-015]
```

---

## § PHASE 0: INVESTIGATION (Pre-work)

---

### TC-CAP-P0 — Baseline Recon and Codebase Investigation
```yaml
parent_taskcard_id: TC-CAP-P0
title: Baseline Recon — Read existing patterns before any implementation
type: PARENT
status: PROPOSED
owner: execution_agent
supervisor: plan_authority

source:
  plan_requirement_ids: [REQ-CAP-001, REQ-CAP-006]
  plan_section: "Critical Files / Read at execution start"
  root_cause: "Implementation details depend on exact file formats, line counts, and patterns in existing tools"
  selected_solution: "Read three key files fully before implementing any tool"

objective:
  - Fully understand sync_skill_command_registry.py pattern to reuse exactly
  - Confirm exact skill-registry.yaml and command-registry.yaml field names
  - Read docs/governance/codex-adapter.md to assess update needed
  - Confirm exact AGENTS.md insertion point for discovery section

outcome:
  - Pattern confirmed in notes before first tool file is written
  - codex-adapter.md update scope known
  - AGENTS.md line-number insertion point confirmed

child_taskcards: [TC-CAP-P0-01, TC-CAP-P0-02, TC-CAP-P0-03]

parent_acceptance_criteria:
  - All three children CLOSED
  - Notes captured confirming: skill entry field names, command entry field names, _load/_save pattern, AGENTS.md insertion line

rollback_strategy: "None needed — read-only phase"
stop_conditions: ["file read fails — log and use exploration agent"]
```

#### TC-CAP-P0-01 — Read and Record sync_skill_command_registry.py Pattern
```yaml
child_taskcard_id: TC-CAP-P0-01
parent_taskcard_id: TC-CAP-P0
title: Read sync_skill_command_registry.py and record reusable patterns
type: CHILD
status: CLOSED   # Already read during plan phase — findings recorded below

source:
  plan_section: "Critical Files / Read at execution start"
  parent_objective: Baseline recon

findings_already_recorded:
  _load_helper: "yaml.safe_load(p.read_text(encoding='utf-8', errors='replace')) or {}"
  _save_helper: "p.parent.mkdir(parents=True, exist_ok=True); p.write_text(yaml.dump(data, default_flow_style=False, allow_unicode=True))"
  backup_pattern: ".local/archive/command-registry-pre-sync.yaml"
  report_structure: "{generated_by, mission_id, auto_repaired, status_drift, flags, overall_verdict}"
  skills_key: "skills" (list in skill-registry.yaml, each item has skill_id field)
  commands_key: "commands" (list in command-registry.yaml, each item has command_id or skill_id)
  orphan_check: "md_files not in skills → orphan_md flag"
  broken_pointer_check: "skill command_file path not exists → broken_pointer flag"
  orphan_entry_check: "command_id not in skills → orphan_entry flag"
  never_deletes: true (extends, never removes from command-registry)
  LOC: 90 lines (target for new tools: stay ≤ 200 lines)
  note: "Do NOT reimport this tool — wrap its logic in capability_sync tools directly"
```

#### TC-CAP-P0-02 — Confirm AGENTS.md Insertion Line
```yaml
child_taskcard_id: TC-CAP-P0-02
parent_taskcard_id: TC-CAP-P0
title: Read AGENTS.md and identify exact line number for discovery section insertion
type: CHILD
status: TODO

scope:
  allowed_files: ["c:\\Users\\prora\\OneDrive\\Documents\\GitHub\\format-factory\\AGENTS.md"]
  forbidden: "no writes"

micro_steps:
  - MS-P0-02-01: Read AGENTS.md lines 1-120 to find §A2a closing line
  - MS-P0-02-02: Find exact line containing "DEC-014 status: **activated**"
  - MS-P0-02-03: Find next section header after §A2 block (expect "## B." or "## AG0.")
  - MS-P0-02-04: Record: "Insert generated section after line N, before line M"

expected_output: "Line number pair (N, M) for AGENTS.md insertion"
next_valid_task: TC-CAP-P0-03
```

**MICRO-STEPS for TC-CAP-P0-02:**

```
MS-P0-02-01 | Status: PENDING
Action: Read AGENTS.md lines 1-50 to understand structure
Target: c:\...\AGENTS.md, lines 1-50
Expected output: Confirm §A. section structure
Next: MS-P0-02-02

MS-P0-02-02 | Status: PENDING
Action: Read AGENTS.md lines 51-120 to find §A2a close + next section boundary
Target: c:\...\AGENTS.md, lines 51-120
Expected output: Exact line number where §A2 block ends; exact line number where ## B. begins
Next: MS-P0-02-03

MS-P0-02-03 | Status: PENDING
Action: Record insertion coordinates as a comment in TC-CAP-006 child taskcard
Target: This plan file, TC-CAP-006 section
Allowed operation: edit (plan file only)
Expected output: TC-CAP-006 contains "Insert after line N in AGENTS.md"
Next: MS-P0-02-04 (close child)
```

#### TC-CAP-P0-03 — Audit docs/governance/codex-adapter.md
```yaml
child_taskcard_id: TC-CAP-P0-03
parent_taskcard_id: TC-CAP-P0
title: Read codex-adapter.md and record update scope for TC-CAP-006 integration
type: CHILD
status: TODO

scope:
  allowed_files: ["c:\\Users\\prora\\OneDrive\\Documents\\GitHub\\format-factory\\docs\\governance\\codex-adapter.md"]
  forbidden: "no writes"

micro_steps:
  - MS-P0-03-01: Read codex-adapter.md fully
  - MS-P0-03-02: Check if it already references a capability registry path
  - MS-P0-03-03: Record: what line needs updating to reference .governance/capabilities/registry.yaml

expected_output: "Either 'no update needed' or 'add reference at line N'"
next_valid_task: TC-CAP-001
```

**MICRO-STEPS for TC-CAP-P0-03:**

```
MS-P0-03-01 | Status: PENDING
Action: Read docs/governance/codex-adapter.md fully
Target: c:\...\docs\governance\codex-adapter.md
Expected output: Full file contents visible
Next: MS-P0-03-02

MS-P0-03-02 | Status: PENDING
Action: Search for any existing reference to capability registry, .governance/, or registry.yaml
Target: codex-adapter.md content
Expected output: Either "registry reference exists at line N" or "no registry reference"
Next: MS-P0-03-03

MS-P0-03-03 | Status: PENDING
Action: Record update scope in this plan file (TC-CAP-006 or new child)
Target: Plan file
Allowed operation: edit (plan file only)
Expected output: TC-CAP-006 has codex-adapter.md update micro-step if needed
Completion check: Update scope is explicit in plan
```

---

## § PHASE 1: SCHEMA FOUNDATION

---

### TC-CAP-001 — Capability Schema Files
```yaml
parent_taskcard_id: TC-CAP-001
title: Create .governance/capabilities/schemas/ with two JSON Schema files
type: PARENT
status: PROPOSED
owner: execution_agent

source:
  plan_requirement_ids: [REQ-CAP-014]
  plan_section: "TC-CAP-001 Schema Foundation"
  root_cause: "No schema validates the compiled registry or parity report — drift in shape is undetected"
  selected_solution: "JSON Schema draft-2020-12 files; pure data, no Python"

objective:
  - Create .governance/capabilities/ directory
  - Write capability.schema.json
  - Write parity-report.schema.json
  - Validate both schemas are well-formed JSON

outcome:
  - .governance/capabilities/schemas/ exists with two valid schema files
  - jsonschema can load and meta-validate both files

scope:
  allowed_folders: [".governance/"]
  forbidden_folders: ["src/", "tools/", ".supervisor/", "AGENTS.md", "CLAUDE.md"]

child_taskcards: [TC-CAP-001-01, TC-CAP-001-02, TC-CAP-001-03, TC-CAP-001-04]

parent_acceptance_criteria:
  - .governance/capabilities/schemas/capability.schema.json exists and is valid JSON
  - .governance/capabilities/schemas/parity-report.schema.json exists and is valid JSON
  - python -c "import json, pathlib; json.loads(pathlib.Path('.governance/capabilities/schemas/capability.schema.json').read_text())" exits 0
  - jsonschema meta-validate passes (python -c "import jsonschema; jsonschema.Draft202012Validator.check_schema(...)")

evidence_required:
  - Screenshot or log of meta-validation passing
  - File paths of both schemas

rollback_strategy: "Delete .governance/ directory if partially created; no other files affected"
stop_conditions: ["jsonschema not installed — run: pip install jsonschema first"]
reroute_rule: "If meta-validation fails, fix schema field type mismatch before proceeding to TC-CAP-002"
```

#### TC-CAP-001-01 — Create Directory Structure
```yaml
child_taskcard_id: TC-CAP-001-01
parent_taskcard_id: TC-CAP-001
title: Create .governance/capabilities/schemas/ directory
type: CHILD
status: TODO

scope:
  allowed_folders: [".governance/"]
  forbidden: "no other directories"

micro_steps:
  - MS-001-01-01: Verify .governance/ does not exist (read-only check)
  - MS-001-01-02: Create .governance/capabilities/schemas/ directory

next_valid_task: TC-CAP-001-02
```

**MICRO-STEPS:**
```
MS-001-01-01 | Status: PENDING
Action: Check if .governance/ directory exists at repo root
Target: c:\...\format-factory\.governance\
Allowed operation: inspect (ls/glob)
Expected output: "MISSING" or "EXISTS"
Failure: if EXISTS, check its contents for conflicts before proceeding
Next: MS-001-01-02

MS-001-01-02 | Status: PENDING
Action: Create directories .governance/capabilities/schemas/
Target: c:\...\format-factory\.governance\capabilities\schemas\
Allowed operation: mkdir (via Bash or Write tool's implicit mkdir)
Expected output: Directory exists; no other files created
Completion check: Glob .governance/ shows schemas/ subdirectory
Next: TC-CAP-001-02
```

#### TC-CAP-001-02 — Write capability.schema.json
```yaml
child_taskcard_id: TC-CAP-001-02
parent_taskcard_id: TC-CAP-001
title: Write capability.schema.json (JSON Schema draft-2020-12)
type: CHILD
status: TODO

scope:
  allowed_files: [".governance/capabilities/schemas/capability.schema.json"]
  forbidden: "no other files"

required_fields:
  - capability_id: {type: string, required: true}
  - status: {type: string, enum: [active, deprecated], required: true}
  - agent_surfaces: {type: object, properties: {claude_code: bool, codex: bool, ci: bool}, required: true}
  - parity_status: {type: string, enum: [FULL_PARITY, PARTIAL, ORPHAN, MISSING_COMMAND], required: true}
  - generated_at: {type: string, required: true}

optional_fields:
  - command_file: string
  - command_registry_entry: boolean
  - routing_routes: array of strings
  - product_track: string
  - purpose: string
  - source_skill_registry_version: string
  - codex_excluded: boolean

acceptance_checks:
  - File is valid JSON (python -c "import json; json.load(open('...'))")
  - All required properties listed under "required" array
  - enum values match implementation expectations
```

**MICRO-STEPS:**
```
MS-001-02-01 | Status: PENDING
Action: Write .governance/capabilities/schemas/capability.schema.json
Target: .governance/capabilities/schemas/capability.schema.json
Allowed operation: create (Write tool)
Expected output: JSON Schema file with $schema, title, type: object, properties, required
Completion check: File exists, is non-empty
Next: MS-001-02-02

MS-001-02-02 | Status: PENDING
Action: Validate capability.schema.json is valid JSON
Command: python -c "import json; json.load(open('.governance/capabilities/schemas/capability.schema.json'))"
Expected output: No error, exit 0
Failure handling: Fix JSON syntax error; re-run
Evidence: Copy of command exit code 0
Next: TC-CAP-001-03
```

#### TC-CAP-001-03 — Write parity-report.schema.json
```yaml
child_taskcard_id: TC-CAP-001-03
parent_taskcard_id: TC-CAP-001
title: Write parity-report.schema.json (JSON Schema draft-2020-12)
type: CHILD
status: TODO

required_fields:
  - generated_at: string
  - source_versions: object
  - total_capabilities: integer
  - parity_counts: object (keys: FULL_PARITY/PARTIAL/ORPHAN/MISSING_COMMAND, values: integer)
  - checks: array of {check_id: string, verdict: string, failures: array}
  - overall_verdict: {enum: [PASS, WARN, FAIL]}
```

**MICRO-STEPS:**
```
MS-001-03-01 | Status: PENDING
Action: Write .governance/capabilities/schemas/parity-report.schema.json
Target: .governance/capabilities/schemas/parity-report.schema.json
Allowed operation: create
Expected output: Valid JSON Schema file
Next: MS-001-03-02

MS-001-03-02 | Status: PENDING
Action: Validate parity-report.schema.json is valid JSON
Command: python -c "import json; json.load(open('.governance/capabilities/schemas/parity-report.schema.json'))"
Expected output: exit 0
Next: TC-CAP-001-04
```

#### TC-CAP-001-04 — Meta-validate Both Schemas
```yaml
child_taskcard_id: TC-CAP-001-04
parent_taskcard_id: TC-CAP-001
title: Meta-validate both schemas with jsonschema
type: CHILD
status: TODO

micro_steps:
  - MS-001-04-01: Run meta-validation for capability.schema.json
  - MS-001-04-02: Run meta-validation for parity-report.schema.json
  - MS-001-04-03: Record pass evidence; close TC-CAP-001

meta_validate_command: |
  python -c "
  import json, jsonschema
  for f in ['.governance/capabilities/schemas/capability.schema.json',
            '.governance/capabilities/schemas/parity-report.schema.json']:
      s = json.load(open(f))
      jsonschema.Draft202012Validator.check_schema(s)
      print(f'PASS: {f}')
  "
```

---

## § PHASE 2: CORE TOOLCHAIN

---

### TC-CAP-002 — Inventory Tool
```yaml
parent_taskcard_id: TC-CAP-002
title: Implement tools/capability_sync/inventory_capabilities.py
type: PARENT
status: PROPOSED

source:
  plan_requirement_ids: [REQ-CAP-001, REQ-CAP-006, REQ-CAP-009]
  plan_section: "TC-CAP-002 Inventory Tool"
  root_cause: "No tool compiles the three source registries into a single capability snapshot"
  selected_solution: "Follow sync_skill_command_registry.py pattern exactly; add routing inversion and never-delete logic"

objective:
  - Create tools/capability_sync/__init__.py (empty)
  - Implement inventory_capabilities.py that reads three sources, computes parity_status, outputs registry.yaml

outcome:
  - .governance/capabilities/registry.yaml created with 93+ entries
  - Re-run produces identical output (modulo generated_at timestamp)
  - Never-delete: deprecated entries from prior run are merged forward

scope:
  allowed_folders: ["tools/capability_sync/", ".governance/capabilities/"]
  forbidden_folders: [".supervisor/", ".claude/commands/", "CLAUDE.md", "AGENTS.md"]
  forbidden_operations: ["modify skill-registry.yaml", "modify command-registry.yaml"]

preserved_behavior:
  - skill-registry.yaml and command-registry.yaml are NEVER modified

child_taskcards: [TC-CAP-002-01, TC-CAP-002-02, TC-CAP-002-03, TC-CAP-002-04, TC-CAP-002-05, TC-CAP-002-06, TC-CAP-002-07, TC-CAP-002-08]

parent_acceptance_criteria:
  - python tools/capability_sync/inventory_capabilities.py exits 0
  - .governance/capabilities/registry.yaml contains exactly N entries (N >= 93)
  - All entries have capability_id, status, parity_status, agent_surfaces
  - Second run produces identical registry content (modulo generated_at)
  - No modification to .supervisor/skill-registry.yaml or .claude/commands/command-registry.yaml

evidence_required:
  - Command output log showing entry count
  - Diff of two successive runs (only generated_at differs)

rollback_strategy: "Delete tools/capability_sync/ and .governance/capabilities/registry.yaml; TC-CAP-001 files remain"
stop_conditions:
  - ".supervisor/skill-registry.yaml not found → verify path, do not proceed"
  - "yaml module not installed → pip install pyyaml"
```

#### TC-CAP-002-01 — Create Package Init
```yaml
child_taskcard_id: TC-CAP-002-01
title: Create tools/capability_sync/__init__.py
status: TODO
scope:
  allowed_files: ["tools/capability_sync/__init__.py"]
```

**MICRO-STEPS:**
```
MS-002-01-01 | Status: PENDING
Action: Verify tools/ directory exists
Target: c:\...\format-factory\tools\
Allowed operation: inspect
Next: MS-002-01-02

MS-002-01-02 | Status: PENDING
Action: Create tools/capability_sync/__init__.py with empty content (empty file is valid)
Target: tools/capability_sync/__init__.py
Allowed operation: create
Expected output: File exists, 0 bytes or single newline
Completion check: File present at path
Next: TC-CAP-002-02
```

#### TC-CAP-002-02 — Implement _load/_save Helpers
```yaml
child_taskcard_id: TC-CAP-002-02
title: Implement _load(), _save(), and _REPO path helpers in inventory_capabilities.py (skeleton)
status: TODO
scope:
  allowed_files: ["tools/capability_sync/inventory_capabilities.py"]

purpose: |
  Creates the file skeleton with the exact same _load/_save pattern from
  sync_skill_command_registry.py so all subsequent children fill into a consistent base.
```

**MICRO-STEPS:**
```
MS-002-02-01 | Status: PENDING
Action: Create tools/capability_sync/inventory_capabilities.py with:
  - module docstring
  - imports: argparse, pathlib.Path, yaml, json, hashlib, datetime
  - _REPO = Path(__file__).resolve().parent.parent.parent
  - Source paths: _SKILL_REG, _CMD_REG, _CMD_DIR, _ROUTING_REG
  - Output paths: _GOVERNANCE_DIR, _REGISTRY_OUT
  - _load(p) helper (identical to sync_skill_command_registry.py pattern)
  - _save(p, data) helper (identical pattern)
Target: tools/capability_sync/inventory_capabilities.py
Allowed operation: create
Expected output: File with skeleton; imports work; python -c "import tools.capability_sync.inventory_capabilities" does not error
Next: MS-002-02-02

MS-002-02-02 | Status: PENDING
Action: Verify python can import the skeleton without errors
Command: python -c "from tools.capability_sync import inventory_capabilities; print('OK')"
  (run from repo root)
Expected output: "OK"
Failure: Fix import errors (missing module, path issue); retry
Next: TC-CAP-002-03
```

#### TC-CAP-002-03 — Implement Skill Loading
```yaml
child_taskcard_id: TC-CAP-002-03
title: Implement skill loading from skill-registry.yaml
status: TODO
scope:
  allowed_files: ["tools/capability_sync/inventory_capabilities.py"]
```

**MICRO-STEPS:**
```
MS-002-03-01 | Status: PENDING
Action: Add load_skills() function:
  - Calls _load(_SKILL_REG)
  - Returns dict: {skill_id: skill_dict} from data['skills'] list
  - Handles missing 'skills' key gracefully (returns {})
Target: inventory_capabilities.py, new function
Expected output: Function returns dict with 93 keys when run against real registry

MS-002-03-02 | Status: PENDING
Action: Quick smoke test
Command: python -c "
from tools.capability_sync.inventory_capabilities import load_skills
s = load_skills()
print(f'Skills loaded: {len(s)}')
assert len(s) >= 90, f'Expected 90+, got {len(s)}'
print('PASS')
"
Expected output: "Skills loaded: 93" (or similar) + "PASS"
Next: TC-CAP-002-04
```

#### TC-CAP-002-04 — Implement Command Registry Loading
```yaml
child_taskcard_id: TC-CAP-002-04
title: Implement command-registry and command-file loading
status: TODO
scope:
  allowed_files: ["tools/capability_sync/inventory_capabilities.py"]
```

**MICRO-STEPS:**
```
MS-002-04-01 | Status: PENDING
Action: Add load_commands() function:
  - Loads command-registry.yaml data['commands'] list
  - Returns dict: {command_id: entry_dict} (key = command_id OR skill_id as fallback)
  - Also returns set of md_stems from _CMD_DIR.glob("*.md") excluding _readme and command-registry
Target: inventory_capabilities.py

MS-002-04-02 | Status: PENDING
Action: Smoke test command loading
Command: python -c "
from tools.capability_sync.inventory_capabilities import load_commands
cmds, stems = load_commands()
print(f'Registry entries: {len(cmds)}, MD files: {len(stems)}')
"
Expected output: counts printed; no errors
Next: TC-CAP-002-05
```

#### TC-CAP-002-05 — Implement Routing Registry Inversion
```yaml
child_taskcard_id: TC-CAP-002-05
title: Implement routing-registry loading and skill→routes inversion
status: TODO
scope:
  allowed_files: ["tools/capability_sync/inventory_capabilities.py"]
```

**MICRO-STEPS:**
```
MS-002-05-01 | Status: PENDING
Action: Add load_routing() function:
  - Load .supervisor/capability-routing-registry.yaml
  - Build inverted dict: {skill_id: [route_id, ...]}
  - A skill appears in multiple routes if it's listed as preferred_skill_id in multiple routes
Target: inventory_capabilities.py

MS-002-05-02 | Status: PENDING
Action: Smoke test routing inversion
Command: python -c "
from tools.capability_sync.inventory_capabilities import load_routing
r = load_routing()
print(f'Skills with routes: {len(r)}')
"
Expected output: count printed; if 0, confirm routing-registry has preferred_skill_ids
Next: TC-CAP-002-06
```

#### TC-CAP-002-06 — Implement Parity Status Computation
```yaml
child_taskcard_id: TC-CAP-002-06
title: Implement parity_status and agent_surfaces computation per skill
status: TODO
scope:
  allowed_files: ["tools/capability_sync/inventory_capabilities.py"]
```

**MICRO-STEPS:**
```
MS-002-06-01 | Status: PENDING
Action: Add compute_parity_status(skill, cmd_registry, md_stems) function:
  - FULL_PARITY: skill's command_file exists on disk AND skill_id in cmd_registry
  - MISSING_COMMAND: command_file absent from disk OR not in cmd_registry
  - ORPHAN: used only for md_stems with no skill entry (handled in orphan pass)
  - Returns: {parity_status, command_file_exists, command_registry_entry, routing_routes, agent_surfaces}

MS-002-06-02 | Status: PENDING
Action: Add compute_agent_surfaces(skill, md_stems, routing_skills) function:
  - claude_code: skill's command_file path exists on disk
  - codex: True (all skills discoverable via AGENTS.md §A2 default)
  - ci: skill_id in routing_skills (appears as preferred_skill_id in routing-registry)

MS-002-06-03 | Status: PENDING
Action: Smoke test on one known skill
Command: python -c "
from tools.capability_sync.inventory_capabilities import load_skills, load_commands, load_routing, compute_parity_status
s = load_skills()['add-dotnet-api']
cmds, stems = load_commands()
routes = load_routing()
result = compute_parity_status(s, cmds, stems)
print(result)
assert result['parity_status'] == 'FULL_PARITY', result
print('PASS')
"
Expected output: dict printed with parity_status=FULL_PARITY + PASS
Next: TC-CAP-002-07
```

#### TC-CAP-002-07 — Implement Never-Delete Merge and Output
```yaml
child_taskcard_id: TC-CAP-002-07
title: Implement never-delete merge and registry.yaml output
status: TODO
scope:
  allowed_files: ["tools/capability_sync/inventory_capabilities.py", ".governance/capabilities/registry.yaml"]
```

**MICRO-STEPS:**
```
MS-002-07-01 | Status: PENDING
Action: Add merge_with_prior(new_entries, prior_registry_path) function:
  - If prior registry exists: load it, extract entries with status=deprecated
  - For each deprecated entry NOT in new_entries: add it to new_entries with deprecated flag
  - Return merged list sorted by capability_id

MS-002-07-02 | Status: PENDING
Action: Add build_registry(skills, commands, md_stems, routing) -> dict function:
  - For each skill: compute parity_status, agent_surfaces
  - Detect orphan commands (md_stems not in skills) → add as ORPHAN entries
  - Build registry dict with header: {generated_by, generated_at, source_versions, capabilities: [...]}

MS-002-07-03 | Status: PENDING
Action: Add main() and if __name__ == "__main__" entry point
  - Parse --output argument (default: .governance/capabilities/registry.yaml)
  - Call build_registry, merge_with_prior, _save
  - Print summary: "Inventory: N capabilities, M orphans"

MS-002-07-04 | Status: PENDING
Action: Full run test
Command: python tools/capability_sync/inventory_capabilities.py
Expected output: "Inventory: 93+ capabilities, ..." + .governance/capabilities/registry.yaml created
Completion check: file exists, is valid YAML with 'capabilities' key
Next: TC-CAP-002-08
```

#### TC-CAP-002-08 — Idempotency Verification
```yaml
child_taskcard_id: TC-CAP-002-08
title: Verify inventory_capabilities.py is idempotent
status: TODO
```

**MICRO-STEPS:**
```
MS-002-08-01 | Status: PENDING
Action: Run inventory_capabilities.py twice, compare outputs (excluding generated_at)
Command: |
  python tools/capability_sync/inventory_capabilities.py --output /tmp/reg1.yaml
  python tools/capability_sync/inventory_capabilities.py --output /tmp/reg2.yaml
  python -c "
  import yaml, re
  strip_ts = lambda s: re.sub(r'generated_at:.*', 'generated_at: STRIPPED', s)
  a = strip_ts(open('/tmp/reg1.yaml').read())
  b = strip_ts(open('/tmp/reg2.yaml').read())
  assert a == b, 'NOT IDEMPOTENT'
  print('IDEMPOTENT: PASS')
  "
Expected output: "IDEMPOTENT: PASS"
Failure handling: Find non-deterministic field, fix sorting/ordering in build_registry()
Evidence: Command output showing PASS
Next: TC-CAP-003
```

---

### TC-CAP-003 — Parity Validator
```yaml
parent_taskcard_id: TC-CAP-003
title: Implement tools/capability_sync/validate_parity.py
type: PARENT
status: PROPOSED

source:
  plan_requirement_ids: [REQ-CAP-003]
  plan_section: "TC-CAP-003 Parity Validator"
  root_cause: "No tool checks whether the compiled registry is internally consistent and parity-complete"
  selected_solution: "Read registry.yaml, validate schema, run 4 priority checks, emit parity-report.yaml"

objective:
  - Validate compiled registry against capability.schema.json
  - Run P1 checks (fatal) and P2 checks (warn)
  - Emit .governance/capabilities/parity-report.yaml
  - Exit 0 if PASS, 1 if FAIL

child_taskcards: [TC-CAP-003-01, TC-CAP-003-02, TC-CAP-003-03]

parent_acceptance_criteria:
  - python tools/capability_sync/validate_parity.py exits 0 against clean state
  - parity-report.yaml overall_verdict = PASS
  - Introducing a broken command_file path → validator exits 1 with P1 failure recorded

rollback_strategy: "Delete validate_parity.py; parity-report.yaml is generated, safe to delete"
reroute_rule: "If validator shows P1 failures on clean state, investigate missing command_file paths first"
```

#### TC-CAP-003-01 — Schema Validation Step
```yaml
child_taskcard_id: TC-CAP-003-01
title: Implement registry schema validation in validate_parity.py
status: TODO
```

**MICRO-STEPS:**
```
MS-003-01-01 | Status: PENDING
Action: Create tools/capability_sync/validate_parity.py skeleton with:
  - _load helper (same pattern)
  - REGISTRY_PATH, REPORT_PATH, SCHEMA_PATH constants
  - validate_against_schema(registry) function using jsonschema.validate for each entry

MS-003-01-02 | Status: PENDING
Action: Smoke test schema validation
Command: python -c "from tools.capability_sync.validate_parity import validate_against_schema; print('import OK')"
Expected output: "import OK"
```

#### TC-CAP-003-02 — Parity Check Implementation
```yaml
child_taskcard_id: TC-CAP-003-02
title: Implement four priority parity checks
status: TODO
```

**MICRO-STEPS:**
```
MS-003-02-01 | Status: PENDING
Action: Implement P1 check: skill_has_command_file
  - For each active capability: verify command_file_exists == True
  - Collect failures list

MS-003-02-02 | Status: PENDING
Action: Implement P1 check: command_has_skill (no orphan commands)
  - For each capability with parity_status == ORPHAN: add to P1 failures

MS-003-02-03 | Status: PENDING
Action: Implement P2 check: command_in_registry
  - For each active capability: verify command_registry_entry == True

MS-003-02-04 | Status: PENDING
Action: Implement P2 check: routing_coverage
  - Load routing-registry directly; verify all preferred_skill_ids exist in registry capabilities

MS-003-02-05 | Status: PENDING
Action: Implement overall_verdict logic:
  - FAIL if any P1 failure
  - WARN if any P2 failure (no P1 failures)
  - PASS if no failures at all
```

#### TC-CAP-003-03 — Parity Report Output and Full Test
```yaml
child_taskcard_id: TC-CAP-003-03
title: Emit parity-report.yaml and run full validation
status: TODO
```

**MICRO-STEPS:**
```
MS-003-03-01 | Status: PENDING
Action: Implement report emission:
  - Build report dict with generated_at, source_versions, total_capabilities, parity_counts, checks, overall_verdict
  - _save to REPORT_PATH

MS-003-03-02 | Status: PENDING
Action: Full run test
Command: python tools/capability_sync/validate_parity.py
Expected output: exit 0; .governance/capabilities/parity-report.yaml shows overall_verdict: PASS

MS-003-03-03 | Status: PENDING
Action: Negative control: introduce deliberate P1 failure
Steps:
  1. Edit .governance/capabilities/registry.yaml temporarily: change one command_file_exists to false
  2. python tools/capability_sync/validate_parity.py → expect exit 1, FAIL verdict
  3. Restore registry.yaml
  4. Re-run → expect exit 0, PASS
Evidence: Log showing both exit codes
```

---

### TC-CAP-004 — Discovery Index Generator
```yaml
parent_taskcard_id: TC-CAP-004
title: Implement tools/capability_sync/generate_discovery_indexes.py
type: PARENT
status: PROPOSED

source:
  plan_requirement_ids: [REQ-CAP-002, REQ-CAP-007]
  root_cause: "No generator produces stable BEGIN/END marker blocks for CLAUDE.md and AGENTS.md"
  selected_solution: "Pure functions (no file I/O) that produce markdown strings; hash strips timestamp"

objective:
  - Implement generate_claude_index(registry, timestamp) -> str
  - Implement generate_agents_index(registry, timestamp) -> str
  - Implement compute_content_hash(content) -> str (strips generated= attribute before hashing)

child_taskcards: [TC-CAP-004-01, TC-CAP-004-02, TC-CAP-004-03]

parent_acceptance_criteria:
  - Both functions are pure (no imports of os, pathlib used for file I/O)
  - Two calls with different timestamps produce identical hash
  - Generated content is stable Markdown table sorted by product_track, then capability_id
```

#### TC-CAP-004-01 — Claude Index Generator Function
```yaml
child_taskcard_id: TC-CAP-004-01
title: Implement generate_claude_index and compute_content_hash
status: TODO
```

**MICRO-STEPS:**
```
MS-004-01-01 | Status: PENDING
Action: Create tools/capability_sync/generate_discovery_indexes.py with:
  - imports: hashlib, re
  - CLAUDE_BEGIN = "<!-- BEGIN:CAPABILITY-INDEX generated={ts} source=.governance/capabilities/registry.yaml -->"
  - CLAUDE_END = "<!-- END:CAPABILITY-INDEX -->"
  - compute_content_hash(content): strips "generated=[^ >]*" with regex, hashes remainder

MS-004-01-02 | Status: PENDING
Action: Implement generate_claude_index(registry, timestamp) -> str:
  - Filter active capabilities; sort by product_track, then capability_id
  - Generate Markdown table: | capability_id | status | product_track | parity_status |
  - Wrap with BEGIN/END markers

MS-004-01-03 | Status: PENDING
Action: Stability test
Command: python -c "
from tools.capability_sync.generate_discovery_indexes import generate_claude_index, compute_content_hash
import yaml
reg = yaml.safe_load(open('.governance/capabilities/registry.yaml'))
s1 = generate_claude_index(reg, '2026-01-01T00:00:00')
s2 = generate_claude_index(reg, '2026-01-02T00:00:00')
assert compute_content_hash(s1) == compute_content_hash(s2), 'HASH MISMATCH'
print('PASS: hash stable across timestamps')
"
Expected output: "PASS: hash stable across timestamps"
```

#### TC-CAP-004-02 — Agents Index Generator Function
```yaml
child_taskcard_id: TC-CAP-004-02
title: Implement generate_agents_index function
status: TODO
```

**MICRO-STEPS:**
```
MS-004-02-01 | Status: PENDING
Action: Implement generate_agents_index(registry, timestamp) -> str:
  - Filter active capabilities; sort by product_track, then capability_id
  - Generate Markdown table with additional columns: routing_routes, agent_surfaces
  - agent_surfaces shown as: claude_code=Y/N, codex=Y/N, ci=Y/N
  - Wrap with BEGIN/END markers (CAPABILITY-DISCOVERY markers)

MS-004-02-02 | Status: PENDING
Action: Stability test (same pattern as MS-004-01-03 but for agents index)
Expected output: "PASS: agents hash stable across timestamps"
```

#### TC-CAP-004-03 — Integration Test Both Functions
```yaml
child_taskcard_id: TC-CAP-004-03
title: Integration test both generator functions produce valid Markdown
status: TODO
```

**MICRO-STEPS:**
```
MS-004-03-01 | Status: PENDING
Action: Verify both outputs contain expected columns and row count
Command: python -c "
from tools.capability_sync.generate_discovery_indexes import generate_claude_index, generate_agents_index
import yaml
reg = yaml.safe_load(open('.governance/capabilities/registry.yaml'))
ts = '2026-06-26T00:00:00'
ci = generate_claude_index(reg, ts)
ai = generate_agents_index(reg, ts)
# Check marker structure
assert '<!-- BEGIN:CAPABILITY-INDEX' in ci and '<!-- END:CAPABILITY-INDEX -->' in ci
assert '<!-- BEGIN:CAPABILITY-DISCOVERY' in ai and '<!-- END:CAPABILITY-DISCOVERY -->' in ai
# Check row count (one header + one separator + N data rows)
rows = [r for r in ci.split('\n') if r.startswith('|')]
print(f'CLAUDE rows: {len(rows)-2}, AGENTS rows: {len([r for r in ai.split(chr(10)) if r.startswith(chr(124))])-2}')
print('PASS')
"
Expected output: row counts printed + PASS
```

---

### TC-CAP-005 — CLAUDE.md Updater
```yaml
parent_taskcard_id: TC-CAP-005
title: Implement tools/capability_sync/update_claude_instructions.py
type: PARENT
status: PROPOSED

source:
  plan_requirement_ids: [REQ-CAP-007]
  root_cause: "CLAUDE.md lacks generated capability index section with stable markers"
  selected_solution: "Splice tool finds markers, replaces content, backs up before first write"

objective:
  - Read CLAUDE.md; find or create BEGIN:CAPABILITY-INDEX markers
  - Splice generated content between markers
  - Write backup before first write; skip write if content unchanged

scope:
  allowed_files: ["CLAUDE.md", ".local/archive/claude-md-pre-sync-*.md"]
  forbidden: "no other files"

preserved_behavior:
  - All human-authored CLAUDE.md content outside markers is unchanged
  - If markers absent, append section at end (never insert in middle without markers)

child_taskcards: [TC-CAP-005-01, TC-CAP-005-02, TC-CAP-005-03]

parent_acceptance_criteria:
  - CLAUDE.md contains BEGIN:CAPABILITY-INDEX and END:CAPABILITY-INDEX
  - Content between markers matches generate_claude_index output
  - Second run with same source produces identical CLAUDE.md (no backup written)
  - .local/archive/ backup exists from first run
```

#### TC-CAP-005-01 — Implement Marker Splice Logic
```yaml
child_taskcard_id: TC-CAP-005-01
title: Implement find-and-splice logic for CLAUDE.md
status: TODO
```

**MICRO-STEPS:**
```
MS-005-01-01 | Status: PENDING
Action: Create tools/capability_sync/update_claude_instructions.py:
  - _CLAUDE_MD = _REPO / "CLAUDE.md"
  - BEGIN_MARKER pattern (strips timestamp for find: "<!-- BEGIN:CAPABILITY-INDEX")
  - find_marker_bounds(content) -> (start_line, end_line) or None

MS-005-01-02 | Status: PENDING
Action: Implement splice_section(content, new_block) -> str:
  - If markers found: replace content between them
  - If markers absent: append new_block at end of content
  - Return modified string

MS-005-01-03 | Status: PENDING
Action: Implement write_with_backup(path, new_content, original_content):
  - If new_content == original_content: print "NO CHANGE"; return
  - Write backup to .local/archive/claude-md-pre-sync-{timestamp}.md
  - Write new_content to path
```

#### TC-CAP-005-02 — Implement main() and Full Run
```yaml
child_taskcard_id: TC-CAP-005-02
title: Implement main() and run full CLAUDE.md update
status: TODO
```

**MICRO-STEPS:**
```
MS-005-02-01 | Status: PENDING
Action: Implement main():
  - Load registry from .governance/capabilities/registry.yaml
  - Generate claude_index block (with current timestamp)
  - Read CLAUDE.md
  - Splice block
  - Write with backup

MS-005-02-02 | Status: PENDING
Action: Full run test
Command: python tools/capability_sync/update_claude_instructions.py
Expected output:
  First run: "Wrote backup to .local/archive/...; Updated CLAUDE.md"
  Second run: "NO CHANGE — CLAUDE.md already up to date"
Completion check: CLAUDE.md contains BEGIN:CAPABILITY-INDEX block
```

#### TC-CAP-005-03 — Idempotency Test
```yaml
child_taskcard_id: TC-CAP-005-03
title: Verify CLAUDE.md updater is idempotent
status: TODO
```

**MICRO-STEPS:**
```
MS-005-03-01 | Status: PENDING
Action: Run updater twice; verify second run prints NO CHANGE
Command: |
  python tools/capability_sync/update_claude_instructions.py
  python tools/capability_sync/update_claude_instructions.py 2>&1 | grep "NO CHANGE"
Expected output: "NO CHANGE" on second run
```

---

### TC-CAP-006 — AGENTS.md Updater
```yaml
parent_taskcard_id: TC-CAP-006
title: Implement tools/capability_sync/update_agent_instructions.py
type: PARENT
status: PROPOSED

source:
  plan_requirement_ids: [REQ-CAP-002, REQ-CAP-008]
  root_cause: "AGENTS.md lacks generated discovery section; Codex cannot programmatically find capabilities"

objective:
  - Read AGENTS.md; find or create BEGIN:CAPABILITY-DISCOVERY markers
  - Splice generated agents_index content between markers
  - On first run: insert section after §A2a closing paragraph (confirmed by TC-CAP-P0-02)
  - Update docs/governance/codex-adapter.md to reference .governance/capabilities/registry.yaml (if TC-CAP-P0-03 found no existing reference)

AGENTS_MD_INSERTION_NOTE: |
  Confirmed insertion target (from TC-CAP-P0-02): after line containing
  "DEC-014 status: **activated**", before "## B. Phase and Plan Verification"
  Execute TC-CAP-P0-02 first to get exact line numbers.

scope:
  allowed_files: ["AGENTS.md", "docs/governance/codex-adapter.md", ".local/archive/agents-md-pre-sync-*.md"]
  forbidden: "no other files"

preserved_behavior:
  - All human-authored AGENTS.md content outside markers is unchanged
  - codex-adapter.md update is additive only (one line added, nothing removed)

child_taskcards: [TC-CAP-006-01, TC-CAP-006-02, TC-CAP-006-03, TC-CAP-006-04]
```

#### TC-CAP-006-01 — Implement AGENTS.md Splice Logic
```yaml
child_taskcard_id: TC-CAP-006-01
title: Implement find-and-splice logic for AGENTS.md
status: TODO
note: "Pattern identical to TC-CAP-005-01 — extract shared splice logic if desired"
```

**MICRO-STEPS:**
```
MS-006-01-01 | Status: PENDING
Action: Create tools/capability_sync/update_agent_instructions.py with same structure as update_claude_instructions.py
  - Change target path to AGENTS.md
  - Change marker strings to BEGIN/END:CAPABILITY-DISCOVERY
  - Change generator call to generate_agents_index
Note: Can share helper functions if extracted to a common _splice_utils.py (optional — only if both tools are >50 lines)
Target: tools/capability_sync/update_agent_instructions.py

MS-006-01-02 | Status: PENDING
Action: Implement insert_after_a2a_if_no_markers(content, new_block) -> str:
  - Search for line matching "DEC-014 status: .activated." pattern
  - Insert new_block after that line (and a blank line)
  - This is the first-run path only; subsequent runs use marker splice
```

#### TC-CAP-006-02 — Implement codex-adapter.md Update
```yaml
child_taskcard_id: TC-CAP-006-02
title: Update docs/governance/codex-adapter.md to reference .governance/capabilities/registry.yaml
status: TODO
precondition: "TC-CAP-P0-03 must be CLOSED — update scope must be known"
```

**MICRO-STEPS:**
```
MS-006-02-01 | Status: PENDING
Action: If TC-CAP-P0-03 found "no registry reference": add reference line to codex-adapter.md
  Location: after the "query registry" step in the 7-step execution contract
  Content to add: "   - Capability registry: .governance/capabilities/registry.yaml (generated)"
  If TC-CAP-P0-03 found "registry reference exists": SKIPPED_NOT_APPLICABLE
Target: docs/governance/codex-adapter.md
Allowed operation: edit (one line addition only)

MS-006-02-02 | Status: PENDING
Action: Verify codex-adapter.md change is additive only (no existing content removed)
Command: git diff docs/governance/codex-adapter.md | grep "^-" | grep -v "^---"
Expected output: no removals (only additions)
```

#### TC-CAP-006-03 — Full Run and Idempotency
```yaml
child_taskcard_id: TC-CAP-006-03
title: Full run of AGENTS.md update and idempotency verification
status: TODO
```

**MICRO-STEPS:**
```
MS-006-03-01 | Status: PENDING
Action: Full run
Command: python tools/capability_sync/update_agent_instructions.py
Expected output: "Updated AGENTS.md" on first run

MS-006-03-02 | Status: PENDING
Action: Verify AGENTS.md now contains BEGIN:CAPABILITY-DISCOVERY section
Command: grep -n "BEGIN:CAPABILITY-DISCOVERY" AGENTS.md
Expected output: line number with marker

MS-006-03-03 | Status: PENDING
Action: Idempotency check (second run → NO CHANGE)
Command: python tools/capability_sync/update_agent_instructions.py 2>&1 | grep "NO CHANGE"
Expected output: "NO CHANGE"
```

#### TC-CAP-006-04 — Preservation Check
```yaml
child_taskcard_id: TC-CAP-006-04
title: Verify no human-authored AGENTS.md content was removed
status: TODO
```

**MICRO-STEPS:**
```
MS-006-04-01 | Status: PENDING
Action: Check that §A1, §A2, §A2a content is still present in AGENTS.md
Command: |
  grep -c "A1\." AGENTS.md && grep -c "A2a\." AGENTS.md && grep -c "A3\." AGENTS.md
Expected output: counts > 0 for all three
Failure: Content was accidentally overwritten; restore from .local/archive/ backup immediately
```

---

### TC-CAP-007 — Drift Detector
```yaml
parent_taskcard_id: TC-CAP-007
title: Implement tools/capability_sync/detect_drift.py
type: PARENT
status: PROPOSED

source:
  plan_requirement_ids: [REQ-CAP-004]
  root_cause: "No read-only tool can determine if committed registry/adapters are stale vs source registries"
  selected_solution: "In-memory re-computation; deterministic serialization; hash comparison; exit 1 on drift"

objective:
  - Re-compute expected registry content in-memory (import inventory_capabilities functions)
  - Compare vs committed registry.yaml
  - Re-generate expected CLAUDE.md section; compare vs committed CLAUDE.md section
  - Re-generate expected AGENTS.md section; compare vs committed AGENTS.md section
  - Exit 0 if all match; exit 1 if any drift

CRITICAL_CONSTRAINT: "This tool NEVER writes any files. It is purely read+compare+report."

child_taskcards: [TC-CAP-007-01, TC-CAP-007-02, TC-CAP-007-03, TC-CAP-007-04]

parent_acceptance_criteria:
  - On clean state after full sync: exit 0, prints "NO_DRIFT"
  - After manual edit to skill-registry without re-sync: exit 1 with diff shown
  - --output flag writes JSON drift report to specified path
  - Tool makes zero file writes to repo files
```

#### TC-CAP-007-01 — Deterministic Serialization Helper
```yaml
child_taskcard_id: TC-CAP-007-01
title: Implement deterministic serialization and hash utilities
status: TODO
```

**MICRO-STEPS:**
```
MS-007-01-01 | Status: PENDING
Action: Create tools/capability_sync/detect_drift.py with:
  - imports: yaml, json, hashlib, re, sys, argparse
  - _REPO path constant
  - canonicalize(data) function:
      strips 'generated_at' key from data dict (in-memory, not file)
      returns yaml.dump(data, sort_keys=True, default_flow_style=False)
  - hash_content(text) -> str: hashlib.sha256(text.encode()).hexdigest()
  - strip_timestamp_attr(text) -> str: re.sub(r'generated=[^\s>]+', 'generated=STRIPPED', text)
```

#### TC-CAP-007-02 — Registry Drift Check
```yaml
child_taskcard_id: TC-CAP-007-02
title: Implement registry drift check (source → expected vs committed)
status: TODO
```

**MICRO-STEPS:**
```
MS-007-02-01 | Status: PENDING
Action: Implement check_registry_drift() -> dict:
  - Import build_registry from inventory_capabilities
  - Call build_registry(...) in-memory (no file write)
  - Apply canonicalize() to in-memory result
  - Load committed .governance/capabilities/registry.yaml
  - Apply canonicalize() to committed data
  - If hashes differ: return {drifted: True, component: "registry", diff: ...}
  - If same: return {drifted: False}
Note: import inventory_capabilities.build_registry as a function, not subprocess
```

#### TC-CAP-007-03 — CLAUDE.md and AGENTS.md Drift Check
```yaml
child_taskcard_id: TC-CAP-007-03
title: Implement CLAUDE.md and AGENTS.md section drift checks
status: TODO
```

**MICRO-STEPS:**
```
MS-007-03-01 | Status: PENDING
Action: Implement extract_section(content, begin_marker_prefix, end_marker) -> str:
  - Find BEGIN marker line (ignoring timestamp: search for marker_prefix only)
  - Find END marker line
  - Return content between them (exclusive of markers)
  - Return None if markers not found

MS-007-03-02 | Status: PENDING
Action: Implement check_claude_drift() -> dict:
  - Load registry
  - Generate expected section with generate_claude_index(registry, "STRIPPED")
  - Read CLAUDE.md; extract actual section
  - strip_timestamp_attr both; compare
  - Return drift dict

MS-007-03-03 | Status: PENDING
Action: Implement check_agents_drift() — same pattern for AGENTS.md
```

#### TC-CAP-007-04 — Main Entry Point and Full Test
```yaml
child_taskcard_id: TC-CAP-007-04
title: Implement detect_drift.py main() and run all drift checks
status: TODO
```

**MICRO-STEPS:**
```
MS-007-04-01 | Status: PENDING
Action: Implement main():
  - Run all three checks
  - Aggregate results
  - If all clean: print "NO_DRIFT"; exit 0
  - If any drifted: print component names + diff summary; exit 1
  - If --output provided: write JSON report

MS-007-04-02 | Status: PENDING
Action: Clean-state test (after full sync)
Command: python tools/capability_sync/detect_drift.py
Expected output: "NO_DRIFT" + exit 0

MS-007-04-03 | Status: PENDING
Action: Negative control — dirty state test
Steps:
  1. Temporarily modify one purpose field in .supervisor/skill-registry.yaml
  2. python tools/capability_sync/detect_drift.py → expect exit 1
  3. Restore skill-registry.yaml
  4. python tools/capability_sync/detect_drift.py → expect exit 0
Evidence: log showing both exit codes
```

---

### TC-CAP-008 — Sync Orchestrator
```yaml
parent_taskcard_id: TC-CAP-008
title: Implement tools/capability_sync/run_sync.py
type: PARENT
status: PROPOSED

source:
  plan_requirement_ids: [REQ-CAP-006]
  root_cause: "No single entry point orchestrates all sync steps"
  selected_solution: "run_sync.py with --mode flag; calls prior tools as library functions"

child_taskcards: [TC-CAP-008-01, TC-CAP-008-02, TC-CAP-008-03]

parent_acceptance_criteria:
  - run_sync.py --mode full exits 0 on clean state
  - Immediate re-run: exits 0, no file changes (idempotent)
  - --mode drift-only: same result as calling detect_drift.py directly
  - --mode inventory-only: only creates/updates registry.yaml
```

#### TC-CAP-008-01 — Implement Mode Dispatch
```yaml
child_taskcard_id: TC-CAP-008-01
title: Create run_sync.py skeleton with mode dispatch
status: TODO
```

**MICRO-STEPS:**
```
MS-008-01-01 | Status: PENDING
Action: Create tools/capability_sync/run_sync.py:
  - Imports from all prior tools
  - argparse: --mode {full, validate, drift-only, inventory-only}
  - Mode dispatch function calling appropriate sequence

MS-008-01-02 | Status: PENDING
Action: Implement full mode sequence:
  1. inventory_capabilities.main() or build_and_save_registry()
  2. validate_parity.main() or run_parity_checks()
  3. generate + update CLAUDE.md (calls update_claude_instructions.main())
  4. generate + update AGENTS.md (calls update_agent_instructions.main())
  5. detect_drift.main() (read-only verification pass)
  6. Print summary report
  Exit code: worst-of-all step exit codes
```

#### TC-CAP-008-02 — Full Run Test
```yaml
child_taskcard_id: TC-CAP-008-02
title: Full run test of run_sync.py --mode full
status: TODO
```

**MICRO-STEPS:**
```
MS-008-02-01 | Status: PENDING
Action: python tools/capability_sync/run_sync.py --mode full
Expected output: Summary showing all steps passed; exit 0

MS-008-02-02 | Status: PENDING
Action: Idempotency test — run twice, compare all generated files
Command: |
  python tools/capability_sync/run_sync.py --mode full > /tmp/run1.log
  python tools/capability_sync/run_sync.py --mode full > /tmp/run2.log
  # Second run should show "NO CHANGE" for CLAUDE.md and AGENTS.md
  grep "NO CHANGE" /tmp/run2.log
Expected output: "NO CHANGE" lines in second run log
```

#### TC-CAP-008-03 — Drift-Only and Validate Mode Tests
```yaml
child_taskcard_id: TC-CAP-008-03
title: Test --mode drift-only and --mode validate
status: TODO
```

**MICRO-STEPS:**
```
MS-008-03-01 | Status: PENDING
Action: python tools/capability_sync/run_sync.py --mode drift-only
Expected output: "NO_DRIFT" + exit 0 (same as direct detect_drift.py call)

MS-008-03-02 | Status: PENDING
Action: python tools/capability_sync/run_sync.py --mode validate
Expected output: parity-report.yaml overall_verdict = PASS + exit 0
```

---

## § PHASE 3: CLAUDE COMMAND ADAPTERS

---

### TC-CAP-009 — /capability-status Command
```yaml
parent_taskcard_id: TC-CAP-009
title: Write .claude/commands/capability-status.md
type: PARENT
status: PROPOSED

source:
  plan_requirement_ids: [REQ-CAP-011, REQ-CAP-012]
  root_cause: "No Claude command provides parity status without running full sync"
  selected_solution: "Read-only command reads compiled registry and parity-report; prints summary"

pattern_reference: ".claude/commands/score-format.md (read existing for structure)"

child_taskcards: [TC-CAP-009-01, TC-CAP-009-02]

parent_acceptance_criteria:
  - File exists at .claude/commands/capability-status.md
  - File follows project command markdown conventions (has title, purpose, when-to-use, steps)
  - Contains reference to .governance/capabilities/registry.yaml and parity-report.yaml
  - Contains fallback guidance when registry absent
```

#### TC-CAP-009-01 — Read Pattern and Write Command
```yaml
child_taskcard_id: TC-CAP-009-01
title: Read score-format.md for pattern, then write capability-status.md
status: TODO
```

**MICRO-STEPS:**
```
MS-009-01-01 | Status: PENDING
Action: Read .claude/commands/score-format.md to understand project command markdown structure
Target: .claude/commands/score-format.md
Allowed operation: read (inspect only)

MS-009-01-02 | Status: PENDING
Action: Write .claude/commands/capability-status.md following exact same structure:
  - Title: /capability-status
  - Purpose: Read .governance/capabilities/registry.yaml and parity-report.yaml; print summary
  - When to use: Before any skill/command change; after /sync-capabilities
  - Steps:
      1. If .governance/capabilities/registry.yaml absent: print "Run /sync-capabilities first"; stop
      2. Load registry; count by parity_status
      3. Load parity-report.yaml; read overall_verdict
      4. Print table: total/FULL_PARITY/PARTIAL/MISSING_COMMAND/ORPHAN counts
      5. Print overall_verdict
  - Evidence: none (read-only)
Target: .claude/commands/capability-status.md
Allowed operation: create
```

#### TC-CAP-009-02 — Verify File Exists and is Well-Formed
```yaml
child_taskcard_id: TC-CAP-009-02
title: Verify capability-status.md exists and follows project conventions
status: TODO
```

**MICRO-STEPS:**
```
MS-009-02-01 | Status: PENDING
Action: Verify file exists and is non-empty
Command: test -f .claude/commands/capability-status.md && wc -l .claude/commands/capability-status.md
Expected output: line count > 10

MS-009-02-02 | Status: PENDING
Action: Spot-check required sections present
Command: grep -c "registry.yaml\|parity-report\|Run /sync-capabilities" .claude/commands/capability-status.md
Expected output: count >= 2
```

---

### TC-CAP-010 — /sync-capabilities Command
```yaml
parent_taskcard_id: TC-CAP-010
title: Write .claude/commands/sync-capabilities.md
type: PARENT
status: PROPOSED

child_taskcards: [TC-CAP-010-01, TC-CAP-010-02]

parent_acceptance_criteria:
  - File exists and documents: run_sync.py --mode full invocation, what changes, what never changes, idempotency guarantee
```

#### TC-CAP-010-01 — Write sync-capabilities.md
```yaml
child_taskcard_id: TC-CAP-010-01
status: TODO
```

**MICRO-STEPS:**
```
MS-010-01-01 | Status: PENDING
Action: Write .claude/commands/sync-capabilities.md:
  Content must include:
  - Command: python tools/capability_sync/run_sync.py --mode full
  - What changes: .governance/capabilities/registry.yaml, parity-report.yaml, CLAUDE.md generated section, AGENTS.md generated section
  - What NEVER changes: .supervisor/skill-registry.yaml, .claude/commands/command-registry.yaml, .supervisor/capability-routing-registry.yaml
  - Idempotency: safe to run multiple times; second run produces no changes if sources unchanged
  - When to run: after adding/modifying any skill in skill-registry.yaml or any command file
Target: .claude/commands/sync-capabilities.md
```

#### TC-CAP-010-02 — Verify File
```yaml
child_taskcard_id: TC-CAP-010-02
status: TODO
micro_steps:
  - MS-010-02-01: test -f .claude/commands/sync-capabilities.md → exit 0
  - MS-010-02-02: grep "run_sync.py" .claude/commands/sync-capabilities.md → found
```

---

### TC-CAP-011 — /validate-capability-parity Command
```yaml
parent_taskcard_id: TC-CAP-011
title: Write .claude/commands/validate-capability-parity.md
type: PARENT
status: PROPOSED

child_taskcards: [TC-CAP-011-01, TC-CAP-011-02]
```

#### TC-CAP-011-01 — Write validate-capability-parity.md
```yaml
child_taskcard_id: TC-CAP-011-01
status: TODO
```

**MICRO-STEPS:**
```
MS-011-01-01 | Status: PENDING
Action: Write .claude/commands/validate-capability-parity.md:
  Content must include:
  - Command: python tools/capability_sync/run_sync.py --mode validate
  - P1 checks (fatal): skill_has_command_file, command_has_skill
  - P2 checks (warn): command_in_registry, routing_coverage
  - Exit codes: 0=PASS, 1=FAIL (P1), 2=WARN (P2 only)
  - When to use: to diagnose parity failures without running full sync
Target: .claude/commands/validate-capability-parity.md
```

#### TC-CAP-011-02 — Verify File
```yaml
child_taskcard_id: TC-CAP-011-02
status: TODO
micro_steps:
  - MS-011-02-01: file exists, contains "run_sync.py", "P1", "P2"
```

---

## § PHASE 4: REGISTRY REGISTRATION

---

### TC-CAP-012 — Register 3 New Skills in Source Registries
```yaml
parent_taskcard_id: TC-CAP-012
title: Register capability-status, sync-capabilities, validate-capability-parity in source registries
type: PARENT
status: PROPOSED

CIRCULAR_DEPENDENCY_FIX: |
  Original plan said "run /sync-capabilities" here — but the command doesn't exist as a
  registered skill yet. Fix: register skills first via direct YAML edits to source registries,
  then run "python tools/capability_sync/run_sync.py --mode inventory-only" (not the command)
  to rebuild the compiled registry.

source:
  plan_requirement_ids: [REQ-CAP-011]
  root_cause: "Three new command files (TC-CAP-009/010/011) have no corresponding skill entries"

prerequisites: [TC-CAP-008, TC-CAP-009, TC-CAP-010, TC-CAP-011]

child_taskcards: [TC-CAP-012-01, TC-CAP-012-02, TC-CAP-012-03]

parent_acceptance_criteria:
  - .supervisor/skill-registry.yaml has 3 new entries (capability-status, sync-capabilities, validate-capability-parity)
  - .claude/commands/command-registry.yaml has 3 new entries
  - python tools/capability_sync/run_sync.py --mode inventory-only rebuilds registry with 96 entries
  - python tools/capability_sync/validate_parity.py exits 0 (overall_verdict: PASS) for all 96
```

#### TC-CAP-012-01 — Add 3 Entries to skill-registry.yaml
```yaml
child_taskcard_id: TC-CAP-012-01
title: Add 3 skill entries to .supervisor/skill-registry.yaml
status: TODO
```

**MICRO-STEPS:**
```
MS-012-01-01 | Status: PENDING
Action: Read .supervisor/skill-registry.yaml lines 1910-1916 (near end) to find correct insertion point
Target: .supervisor/skill-registry.yaml (read only)

MS-012-01-02 | Status: PENDING
Action: Add 3 skill entries to .supervisor/skill-registry.yaml (append after last skill in list):
  Entry 1 — capability-status:
    skill_id: capability-status
    command: /capability-status
    command_file: .claude/commands/capability-status.md
    status: active
    product_track: layer_governance
    purpose: Read compiled capability registry and parity report; print summary (read-only)
    idempotency: read_only
    mandatory_validations: []
    required_handoff_fields: []
    spec_qname_required: false
    implementation_paths: []
    test_paths: []

  Entry 2 — sync-capabilities:
    skill_id: sync-capabilities
    command: /sync-capabilities
    command_file: .claude/commands/sync-capabilities.md
    status: active
    product_track: layer_governance
    purpose: Run full capability sync (inventory + validate + generate + update CLAUDE.md/AGENTS.md + drift check)
    idempotency: create_or_update
    mandatory_validations: [capability_registry_drift_check]
    required_handoff_fields: []
    spec_qname_required: false
    implementation_paths: [tools/capability_sync/run_sync.py]
    test_paths: []

  Entry 3 — validate-capability-parity:
    skill_id: validate-capability-parity
    command: /validate-capability-parity
    command_file: .claude/commands/validate-capability-parity.md
    status: active
    product_track: layer_governance
    purpose: Validate parity between compiled capability registry and source registries (P1/P2 checks)
    idempotency: read_only
    mandatory_validations: []
    required_handoff_fields: []
    spec_qname_required: false
    implementation_paths: [tools/capability_sync/validate_parity.py]
    test_paths: [tests/governance/test_capability_parity.py]

Target: .supervisor/skill-registry.yaml
Allowed operation: edit (append 3 entries to skills list)
Completion check: grep "capability-status\|sync-capabilities\|validate-capability-parity" .supervisor/skill-registry.yaml | wc -l → 3
```

#### TC-CAP-012-02 — Add 3 Entries to command-registry.yaml
```yaml
child_taskcard_id: TC-CAP-012-02
title: Add 3 command entries to .claude/commands/command-registry.yaml
status: TODO
```

**MICRO-STEPS:**
```
MS-012-02-01 | Status: PENDING
Action: Read .claude/commands/command-registry.yaml end (near last entry) to find insertion point

MS-012-02-02 | Status: PENDING
Action: Add 3 command entries to .claude/commands/command-registry.yaml:
  - {command_id: capability-status, skill_id: capability-status, file: .claude/commands/capability-status.md, status: active, phase: all, created: '2026-06-26', description: "Read and display capability parity status", skill_registry_ref: true}
  - {command_id: sync-capabilities, skill_id: sync-capabilities, file: .claude/commands/sync-capabilities.md, status: active, phase: all, created: '2026-06-26', description: "Run full capability registry sync", skill_registry_ref: true}
  - {command_id: validate-capability-parity, skill_id: validate-capability-parity, file: .claude/commands/validate-capability-parity.md, status: active, phase: all, created: '2026-06-26', description: "Validate cross-agent capability parity", skill_registry_ref: true}
Target: .claude/commands/command-registry.yaml
```

#### TC-CAP-012-03 — Rebuild Compiled Registry and Verify 96 Entries
```yaml
child_taskcard_id: TC-CAP-012-03
title: Run inventory-only sync and verify 96 entries with FULL_PARITY
status: TODO
```

**MICRO-STEPS:**
```
MS-012-03-01 | Status: PENDING
Action: Run inventory rebuild
Command: python tools/capability_sync/run_sync.py --mode inventory-only
Expected output: "Inventory: 96 capabilities..."

MS-012-03-02 | Status: PENDING
Action: Run parity validation
Command: python tools/capability_sync/validate_parity.py
Expected output: overall_verdict: PASS; 96 FULL_PARITY entries

MS-012-03-03 | Status: PENDING
Action: Run full sync to update CLAUDE.md and AGENTS.md with new 96-entry tables
Command: python tools/capability_sync/run_sync.py --mode full
Expected output: exit 0; CLAUDE.md and AGENTS.md discovery sections updated
```

---

## § PHASE 5: CI ENFORCEMENT

---

### TC-CAP-013 — CI Job Addition
```yaml
parent_taskcard_id: TC-CAP-013
title: Add capability-parity job to .github/workflows/ci.yml
type: PARENT
status: PROPOSED

prerequisites: [TC-CAP-007, TC-CAP-012]

scope:
  allowed_files: [".github/workflows/ci.yml"]
  forbidden: "no other CI changes"

CI_JOB_TEMPLATE: |
  capability-parity:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install pyyaml jsonschema
      - name: Detect capability registry drift
        run: python tools/capability_sync/detect_drift.py --output capability-drift.json
      - name: Upload drift report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: capability-drift-report
          path: capability-drift.json

NOTE: "continue-on-error is ABSENT (omitted = false = hard fail). This differs from skill-attribution-check which uses continue-on-error: true"

child_taskcards: [TC-CAP-013-01, TC-CAP-013-02]
```

#### TC-CAP-013-01 — Read ci.yml End and Insert Job
```yaml
child_taskcard_id: TC-CAP-013-01
title: Read ci.yml to find correct insertion point and add capability-parity job
status: TODO
```

**MICRO-STEPS:**
```
MS-013-01-01 | Status: PENDING
Action: Read .github/workflows/ci.yml fully (need end of file)
Target: .github/workflows/ci.yml
Allowed operation: read

MS-013-01-02 | Status: PENDING
Action: Identify last job in ci.yml (need to insert capability-parity after it)
Expected: job list currently ends with governance-check or similar
Record: name of last job

MS-013-01-03 | Status: PENDING
Action: Add capability-parity job to .github/workflows/ci.yml
  Position: after last existing job, at same indentation level
  Content: exact YAML from CI_JOB_TEMPLATE above
  WARNING: do NOT add "continue-on-error: true"
Target: .github/workflows/ci.yml
Allowed operation: edit (append job)

MS-013-01-04 | Status: PENDING
Action: Validate YAML syntax
Command: python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml').read()); print('YAML VALID')"
Expected output: "YAML VALID"
```

#### TC-CAP-013-02 — Verify Job Properties
```yaml
child_taskcard_id: TC-CAP-013-02
title: Verify capability-parity job has correct properties
status: TODO
```

**MICRO-STEPS:**
```
MS-013-02-01 | Status: PENDING
Action: Verify capability-parity job exists and lacks continue-on-error
Command: |
  python -c "
  import yaml
  data = yaml.safe_load(open('.github/workflows/ci.yml').read())
  job = data['jobs']['capability-parity']
  assert job is not None, 'job missing'
  for step in job.get('steps', []):
    assert 'continue-on-error' not in step or step['continue-on-error'] == False, 'found continue-on-error: true on a step'
  print('PASS: job present, no continue-on-error on drift step')
  "
Expected output: "PASS: job present..."
```

---

### TC-CAP-014 — Pre-commit Hook
```yaml
parent_taskcard_id: TC-CAP-014
title: Add capability-registry-drift-check hook to .pre-commit-config.yaml
type: PARENT
status: PROPOSED

prerequisites: [TC-CAP-007, TC-CAP-012]

scope:
  allowed_files: [".pre-commit-config.yaml"]

child_taskcards: [TC-CAP-014-01, TC-CAP-014-02]
```

#### TC-CAP-014-01 — Read .pre-commit-config.yaml and Add Hook
```yaml
child_taskcard_id: TC-CAP-014-01
title: Read .pre-commit-config.yaml and add drift detection hook
status: TODO
```

**MICRO-STEPS:**
```
MS-014-01-01 | Status: PENDING
Action: Read .pre-commit-config.yaml fully
Target: .pre-commit-config.yaml
Allowed operation: read

MS-014-01-02 | Status: PENDING
Action: Find repos: - repo: local section (or create if absent) and append hook:
  - id: capability-registry-drift-check
    name: Capability registry drift check
    entry: python tools/capability_sync/detect_drift.py
    language: system
    pass_filenames: false
    always_run: false
    files: '^(\.supervisor/skill-registry\.yaml|\.claude/commands/command-registry\.yaml|\.supervisor/capability-routing-registry\.yaml|\.claude/commands/.*\.md|\.governance/capabilities/.*)$'
    stages: [pre-commit]
Target: .pre-commit-config.yaml
Allowed operation: edit

MS-014-01-03 | Status: PENDING
Action: Validate YAML syntax
Command: python -c "import yaml; yaml.safe_load(open('.pre-commit-config.yaml').read()); print('YAML VALID')"
Expected output: "YAML VALID"
```

#### TC-CAP-014-02 — Verify Hook Properties
```yaml
child_taskcard_id: TC-CAP-014-02
title: Verify pre-commit hook is configured correctly
status: TODO
```

**MICRO-STEPS:**
```
MS-014-02-01 | Status: PENDING
Action: Verify hook configuration
Command: python -c "
import yaml
data = yaml.safe_load(open('.pre-commit-config.yaml').read())
local_repo = next(r for r in data['repos'] if r.get('repo') == 'local')
hook = next(h for h in local_repo['hooks'] if h['id'] == 'capability-registry-drift-check')
assert hook['entry'] == 'python tools/capability_sync/detect_drift.py'
assert not hook.get('always_run', False)
print('PASS: hook configured correctly')
"
Expected output: "PASS: hook configured correctly"
```

---

## § PHASE 6: GOVERNANCE TESTS

---

### TC-CAP-015 — Governance Tests
```yaml
parent_taskcard_id: TC-CAP-015
title: Write tests/governance/test_capability_parity.py
type: PARENT
status: PROPOSED

source:
  plan_requirement_ids: [REQ-CAP-013]
  root_cause: "No pytest-based tests verify source registries are consistent — only toolchain tests exist"
  selected_solution: "Three independent test functions that read source registries directly (no toolchain dependency)"

DESIGN_PRINCIPLE: |
  These tests read source registries (skill-registry, command-registry, routing-registry) DIRECTLY
  without importing tools/capability_sync/ code. This provides defense-in-depth:
  if the toolchain has a bug, these tests still catch broken pointers.

child_taskcards: [TC-CAP-015-01, TC-CAP-015-02, TC-CAP-015-03, TC-CAP-015-04]

parent_acceptance_criteria:
  - python -m pytest tests/governance/test_capability_parity.py -v passes (3/3 tests)
  - Introducing broken command_file path → test 1 fails
  - Adding orphan command file → test 2 fails
  - Adding dangling preferred_skill_id to routing-registry → test 3 fails
```

#### TC-CAP-015-01 — Create Test File Skeleton
```yaml
child_taskcard_id: TC-CAP-015-01
title: Create tests/governance/test_capability_parity.py skeleton
status: TODO
```

**MICRO-STEPS:**
```
MS-015-01-01 | Status: PENDING
Action: Verify tests/governance/ directory exists (check tests/ directory)
Command: ls tests/
Expected output: includes "governance" directory or just "net/" and "python/" (may need mkdir)

MS-015-01-02 | Status: PENDING
Action: Create tests/governance/__init__.py if not present (empty)

MS-015-01-03 | Status: PENDING
Action: Create tests/governance/test_capability_parity.py with:
  - imports: pytest, yaml, pathlib.Path
  - REPO_ROOT = Path(__file__).resolve().parent.parent.parent
  - Helper: load_skill_registry() -> dict
  - Helper: load_command_registry() -> dict
  - Helper: load_routing_registry() -> dict
  - Placeholder for 3 test functions
```

#### TC-CAP-015-02 — Implement test_all_active_skills_have_command_files
```yaml
child_taskcard_id: TC-CAP-015-02
title: Implement test_all_active_skills_have_command_files
status: TODO
```

**MICRO-STEPS:**
```
MS-015-02-01 | Status: PENDING
Action: Implement test_all_active_skills_have_command_files():
  - Load skill-registry; iterate skills where status != 'deprecated'
  - For each: assert (REPO_ROOT / skill['command_file']).exists()
  - On failure: include skill_id and command_file path in assertion message

MS-015-02-02 | Status: PENDING
Action: Run test
Command: python -m pytest tests/governance/test_capability_parity.py::test_all_active_skills_have_command_files -v
Expected output: PASSED

MS-015-02-03 | Status: PENDING
Action: Negative control — temporarily break one command_file path
Steps:
  1. Edit registry to add a fake skill with nonexistent command_file
  2. Run test → FAILED with specific skill_id in message
  3. Remove fake skill
  4. Run test → PASSED
Evidence: log of both runs
```

#### TC-CAP-015-03 — Implement test_no_orphan_commands
```yaml
child_taskcard_id: TC-CAP-015-03
title: Implement test_no_orphan_commands
status: TODO
```

**MICRO-STEPS:**
```
MS-015-03-01 | Status: PENDING
Action: Implement test_no_orphan_commands():
  - Load skill-registry → set of skill_ids
  - Glob .claude/commands/*.md → set of stems
  - Exclude from stems: "_readme", "command-registry" (non-skill files)
  - Assert stems.issubset(skill_ids): show orphaned stems on failure

MS-015-03-02 | Status: PENDING
Action: Run test
Command: python -m pytest tests/governance/test_capability_parity.py::test_no_orphan_commands -v
Expected output: PASSED
```

#### TC-CAP-015-04 — Implement test_routing_registry_skill_references_exist + CI Registration
```yaml
child_taskcard_id: TC-CAP-015-04
title: Implement test_routing_registry_skill_references_exist and verify CI includes test
status: TODO
```

**MICRO-STEPS:**
```
MS-015-04-01 | Status: PENDING
Action: Implement test_routing_registry_skill_references_exist():
  - Load routing-registry; collect all preferred_skill_ids values (flatten lists)
  - Load skill-registry → set of skill_ids
  - Assert each preferred_skill_id in skill_ids

MS-015-04-02 | Status: PENDING
Action: Full test suite run
Command: python -m pytest tests/governance/test_capability_parity.py -v
Expected output: 3 PASSED, 0 FAILED, 0 ERROR

MS-015-04-03 | Status: PENDING
Action: Verify .github/workflows/ci.yml includes governance tests
  - Check if test-fast or test-full job runs tests/governance/
  - If not: add "tests/governance/" to the test runner scope or add explicit step
Command: grep -n "governance" .github/workflows/ci.yml
Expected output: at least one match (test runner covers tests/governance/)
Note: If not covered, add a dedicated step to governance-check or test-fast job
```

---

## § PILOTS (All 15 Required)

| # | Pilot | Description | Implemented via | Status |
|---|---|---|---|---|
| 1 | Skill→Command | All 93 active skills have discoverable commands | TC-CAP-003 parity report: FULL_PARITY for all | TC-CAP-003-03 |
| 2 | Command→Skill | No orphan command files | TC-CAP-015-03 test_no_orphan_commands | TC-CAP-015-03 |
| 3 | Shared parity | Claude + Codex reach same capabilities via same registry | AGENTS.md BEGIN:CAPABILITY-DISCOVERY + .governance/capabilities/registry.yaml | TC-CAP-006 |
| 4 | New micro-capability | New skill created, both adapters propagate automatically | TC-CAP-012 adds 3 new capabilities; TC-CAP-012-03 proves both CLAUDE.md and AGENTS.md update | TC-CAP-012 |
| 5 | Semantic drift | Alter generated adapter → detect_drift exits 1 | TC-CAP-007-04 negative control (MS-007-04-03) | TC-CAP-007-04 |
| 6 | Missing adapter | Remove command file → parity check catches P1 | TC-CAP-003-03 negative control (MS-003-03-03) | TC-CAP-003-03 |
| 7 | Orphan command | Add command with no skill → TC-CAP-015 test catches it | TC-CAP-015-03 negative control | TC-CAP-015-03 |
| 8 | Orphan skill | Skill absent from registry → validate_parity P2 catches it | TC-CAP-003-02 routing_coverage check | TC-CAP-003-02 |
| 9 | Deprecation propagation | Set status: deprecated in skill-registry → re-sync updates all surfaces | Run: edit skill status to deprecated → run_sync.py --mode full → verify CLAUDE.md table excludes it (or marks deprecated) | TC-CAP-008-02 |
| 10 | Nested instructions | No nested CLAUDE.md or AGENTS.md files exist (confirmed) | Already verified in exploration — no nested files | TC-CAP-P0 |
| 11 | Command-heavy project | This project has 93 commands — migrate to canonical contracts | The compiled .governance/capabilities/registry.yaml IS the canonical contract compilation; TC-CAP-002 proves migration | TC-CAP-002 |
| 12 | Skill-heavy project | All 93 skills have generated Claude commands | TC-CAP-003 FULL_PARITY report proves skill→command coverage | TC-CAP-003 |
| 13 | CI drift gate | Alter source without syncing → CI fails | TC-CAP-013-02 verifies job; TC-CAP-007-04 negative control confirms exit 1 | TC-CAP-013 |
| 14 | Concurrent agents | Claude and Codex both use same registry | Structural: AGENTS.md discovery section + .governance/capabilities/registry.yaml both reference same source | TC-CAP-006 |
| 15 | No-change idempotency | run_sync.py twice → no material changes | TC-CAP-008-02 MS-008-02-02 | TC-CAP-008-02 |

---

## § VALIDATION MATRIX

```yaml
validation_matrix:
  TC-CAP-001:
    focused:
      - check: "capability.schema.json valid JSON"
        command: "python -c \"import json; json.load(open('.governance/capabilities/schemas/capability.schema.json'))\""
        expected: exit 0
        mandatory: true
      - check: "parity-report.schema.json valid JSON"
        command: "python -c \"import json; json.load(open('.governance/capabilities/schemas/parity-report.schema.json'))\""
        expected: exit 0
        mandatory: true
      - check: "meta-validate both schemas"
        command: "python -c \"import json, jsonschema; [jsonschema.Draft202012Validator.check_schema(json.load(open(f))) for f in ['.governance/capabilities/schemas/capability.schema.json', '.governance/capabilities/schemas/parity-report.schema.json']]; print('PASS')\""
        expected: "PASS"
        mandatory: true

  TC-CAP-002:
    focused:
      - check: "registry.yaml created with 93+ entries"
        command: "python -c \"import yaml; r=yaml.safe_load(open('.governance/capabilities/registry.yaml')); print(len(r['capabilities']))\""
        expected: "integer >= 93"
        mandatory: true
      - check: "idempotency: second run identical (modulo timestamp)"
        command: "see MS-002-08-01"
        mandatory: true
    negative_controls:
      - check: "missing skill-registry → tool exits gracefully with error"

  TC-CAP-003:
    focused:
      - check: "validate_parity.py exits 0 on clean state"
        command: "python tools/capability_sync/validate_parity.py"
        expected: exit 0
        mandatory: true
      - check: "parity-report.yaml overall_verdict = PASS"
        command: "python -c \"import yaml; r=yaml.safe_load(open('.governance/capabilities/parity-report.yaml')); print(r['overall_verdict'])\""
        expected: "PASS"
        mandatory: true
    negative_controls:
      - check: "broken command_file → exit 1, FAIL"
        procedure: "set command_file_exists=false on one entry; run validator; restore"

  TC-CAP-007:
    focused:
      - check: "detect_drift.py exits 0 on clean state"
        command: "python tools/capability_sync/detect_drift.py"
        expected: "NO_DRIFT" + exit 0
        mandatory: true
    negative_controls:
      - check: "modified skill-registry → exit 1"
        procedure: "see MS-007-04-03"

  TC-CAP-008:
    focused:
      - check: "run_sync.py --mode full exits 0"
        command: "python tools/capability_sync/run_sync.py --mode full"
        expected: exit 0
        mandatory: true
    idempotency:
      - check: "second run → NO CHANGE on CLAUDE.md and AGENTS.md"
        mandatory: true

  TC-CAP-013:
    focused:
      - check: "ci.yml YAML is valid"
        command: "python -c \"import yaml; yaml.safe_load(open('.github/workflows/ci.yml').read()); print('VALID')\""
        expected: "VALID"
        mandatory: true
      - check: "capability-parity job lacks continue-on-error"
        command: "see MS-013-02-01"
        mandatory: true

  TC-CAP-015:
    focused:
      - check: "all 3 tests pass"
        command: "python -m pytest tests/governance/test_capability_parity.py -v"
        expected: "3 passed"
        mandatory: true
    negative_controls:
      - check: "broken command_file → test 1 fails"
      - check: "orphan command → test 2 fails"
      - check: "dangling route → test 3 fails"
```

---

## § EVIDENCE CONTRACT

```yaml
evidence_contract:
  authoritative_plan: "C:\\Users\\prora\\.claude\\plans\\rustling-gliding-finch.md"
  evidence_root: ".local/evidences/CROSS-AGENT-PARITY-001/"

  required_evidence_per_taskcard:
    TC-CAP-001:
      - ".local/evidences/CROSS-AGENT-PARITY-001/tc-cap-001-schema-meta-validate.log"
    TC-CAP-002:
      - ".local/evidences/CROSS-AGENT-PARITY-001/tc-cap-002-registry-entry-count.log"
      - ".local/evidences/CROSS-AGENT-PARITY-001/tc-cap-002-idempotency.log"
    TC-CAP-003:
      - ".local/evidences/CROSS-AGENT-PARITY-001/tc-cap-003-parity-report.yaml"  # copy of parity-report.yaml
      - ".local/evidences/CROSS-AGENT-PARITY-001/tc-cap-003-negative-control.log"
    TC-CAP-007:
      - ".local/evidences/CROSS-AGENT-PARITY-001/tc-cap-007-clean-no-drift.log"
      - ".local/evidences/CROSS-AGENT-PARITY-001/tc-cap-007-dirty-exit1.log"
    TC-CAP-008:
      - ".local/evidences/CROSS-AGENT-PARITY-001/tc-cap-008-full-sync.log"
      - ".local/evidences/CROSS-AGENT-PARITY-001/tc-cap-008-idempotency.log"
    TC-CAP-012:
      - ".local/evidences/CROSS-AGENT-PARITY-001/tc-cap-012-registry-96-entries.log"
    TC-CAP-013:
      - ".local/evidences/CROSS-AGENT-PARITY-001/tc-cap-013-ci-yaml-valid.log"
    TC-CAP-015:
      - ".local/evidences/CROSS-AGENT-PARITY-001/tc-cap-015-pytest-3-passed.log"
      - ".local/evidences/CROSS-AGENT-PARITY-001/tc-cap-015-negative-controls.log"

  evidence_creation_rule: |
    After each mandatory validation, redirect output to the evidence file:
    python tools/capability_sync/detect_drift.py > .local/evidences/CROSS-AGENT-PARITY-001/tc-cap-007-clean-no-drift.log 2>&1
    Always verify the evidence file is non-empty before marking the child VERIFIED.

  evidence_must_not_contain: "alternative execution instructions, plan content, commands to run instead of plan"
```

---

## § QUALITY SCORING MODEL

```yaml
quality_scoring:
  dimensions:
    child_taskcards:
      - requirement_correctness    # does it implement what REQ-CAP-* says?
      - implementation_correctness # is the implementation sound?
      - scope_discipline           # did it avoid forbidden files?
      - validation_strength        # did negative controls run?
      - evidence_completeness      # are evidence files present and non-empty?
      - regression_safety          # does it break existing test suite?
      - maintainability            # < 200 LOC per tool file?
      - production_readiness       # handles errors gracefully?

  acceptance_threshold: "all mandatory dimensions >= 4/5"

  reroute_trigger: "any dimension < 4/5 → status = REROUTED → fix and re-score"

  regression_safety_check:
    command: "python -m pytest tests/ -x -q --ignore=tests/governance/ 2>&1 | tail -5"
    expected: "no new failures introduced"
    mandatory: true before closing TC-CAP-015
```

---

## § AUTOMATIC SYNCHRONIZATION (preserved + enhanced)

Once complete, the system maintains itself:

- **Source change** → pre-commit hook (`capability-registry-drift-check`) detects drift → developer runs `python tools/capability_sync/run_sync.py --mode full` (or `/sync-capabilities`) → commits updated registry + CLAUDE.md/AGENTS.md sections
- **CI** confirms zero drift on every PR (`capability-parity` job, hard fail)
- **New capability** → add to `.supervisor/skill-registry.yaml` + create `.claude/commands/<id>.md` → run `/sync-capabilities` → all adapters propagate automatically
- **Deprecated capability** → set `status: deprecated` in skill-registry → `/sync-capabilities` updates all surfaces consistently (never-delete: entry stays with deprecated status)

---

## § EXECUTION HANDOFF

**The future execution agent MUST follow this sequence exactly:**

### Before starting any taskcard:
1. Read this plan file from top to bottom (entire document)
2. Identify the current phase (P0 → P1 → P2 → P3 → P4 → P5 → P6)
3. Find the first parent taskcard with status = PROPOSED or IN_PROGRESS
4. Find its first child with status = TODO or IN_PROGRESS
5. Find that child's first micro-step with status = PENDING or ACTIVE
6. Confirm prerequisites of that child are CLOSED
7. Confirm allowed/forbidden paths for that child
8. Execute exactly ONE micro-step at a time

### After each micro-step:
1. Capture evidence (redirect command output to evidence file)
2. Mark micro-step COMPLETE or FAILED
3. If FAILED: mark child BLOCKED; investigate; do not proceed to next micro-step until fixed
4. If COMPLETE: move to next micro-step in sequence

### After all micro-steps in a child complete:
1. Run child acceptance checks
2. Score child on all 8 dimensions (1-5)
3. If any dimension < 4: mark REROUTED; create repair micro-step; re-execute
4. If all dimensions >= 4: mark child VERIFIED then SCORED then CLOSED
5. Update this plan file with status changes

### After all children in a parent complete:
1. Run parent integration checks
2. Score parent
3. If integration passes: mark parent VERIFIED → SCORED → CLOSED
4. Move to next parent taskcard in DAG order

### Forbidden actions for execution agent:
- Skip micro-steps silently
- Close child before all micro-steps are COMPLETE
- Close parent before all mandatory children are CLOSED
- Touch files outside the taskcard's allowed_files/allowed_folders
- Treat code existence as validation proof
- Treat test file existence as test-passing proof
- Choose work outside this plan's scope
- Run `/sync-capabilities` before TC-CAP-008 is CLOSED

---

## § RECONCILIATION REPORT

```yaml
plan_reconciliation:
  single_authority_confirmed: true
  competing_plans: none
  sections_analyzed: 18
  actionable_items_extracted: 68
  actionable_items_represented: 68
  parent_taskcards: 16  # (TC-CAP-P0 + TC-CAP-001 through TC-CAP-015)
  child_taskcards: 52
  micro_steps: 85
  broad_taskcards_split: 15
  missing_taskcards_added: ["TC-CAP-P0 (recon)", "TC-CAP-P0-01/02/03", "schema meta-validate", "idempotency steps", "negative controls for all validators"]
  circular_dependency_fixed: true  # TC-CAP-012 now uses direct YAML edit + inventory-only, not /sync-capabilities
  agents_md_insertion_point_clarified: true
  pilots_coverage: "15/15 (all required pilots addressed)"
  evidence_contract_defined: true
  quality_scoring_defined: true
  rollback_rules_defined: true
  machine_state_defined: true
  dependency_dag_defined: true
  no_actionable_item_loss: true
  ready_for_execution: true
```

---

**VERDICT:** `PLAN_MICRO_TASKCARDIZED_READY_FOR_EXECUTION`

**Next valid parent taskcard:** TC-CAP-P0 (Baseline Recon)
**Next valid child taskcard:** TC-CAP-P0-02 (Confirm AGENTS.md insertion line — TC-CAP-P0-01 already CLOSED from plan phase)
**First micro-step:** MS-P0-02-01 (Read AGENTS.md lines 1-50)


<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-06-27T01:04:32.420846+00:00"
  locked_by: "26292dcd8815"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
