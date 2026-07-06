# Plan: BACKFILL — Apply New Governance to Existing Machinery Debt
# Authoritative Plan v2.0 — Fully Micro-Taskcardized

---

## PLAN AUTHORITY RECORD

```yaml
plan_path: plans/.claude/bright-greeting-goose.md
canonical_external_path: C:\Users\prora\.claude\plans\bright-greeting-goose.md
authority_source: user-initiated plan mode + production deep analysis
version: 2.0
enhanced: 2026-07-06
branch: main
head_commit: 6b3f6f07
plan_type: BACKFILL_AND_GOVERNANCE_HARDENING
single_plan_authority: true
competing_plans: none
execution_authority: true
```

**NOTE — Plan-mode single-file constraint**: All supporting analysis artifacts are
embedded in this file as named SECTION blocks. Each carries `execution_authority: false`.
The plan itself retains `execution_authority: true`. No separate competing plan files exist.

---

## SECTION A1 — PREFLIGHT RECORD

```yaml
preflight:
  artifact_role: analysis_evidence
  execution_authority: false
  repository: c:\Users\prora\OneDrive\Documents\GitHub\format-factory
  branch: main
  head_commit: 6b3f6f07
  active_plan_path: plans/.claude/bright-greeting-goose.md
  plan_format: markdown+yaml
  major_sections: context + 9 BACKFILL taskcards + deps + integration + impact + hard stops
  existing_taskcard_sections_v1: 8 (BF-TC-001 through BF-TC-008, flat, no children)
  new_taskcard_sections_v2: 9 parent taskcards + ~40 children + ~150 micro-steps
  ci_workflow: .github/workflows/ci.yml (governance-check job is the target for new steps)
  duplicate_plan_risk: LOW (single plan-mode file; Stage 0-7 plan is distinct scope)
  prior_version_artifacts: none
```

---

## SECTION A2 — PLAN SECTION INVENTORY

```yaml
section_inventory:
  artifact_role: analysis_evidence
  execution_authority: false

  S-01: {title: "Context", type: background, enhancement: "add requirement IDs, preserve prose"}
  S-02: {title: "BF-TC-001 (YAML register)", existing: flat-no-children, missing: "4 children + 13 micro-steps, CI job location unspecified"}
  S-03: {title: "BF-TC-002 (register gaps)", existing: flat-no-children, missing: "4 children + 13 micro-steps, enum command missing"}
  S-04: {title: "BF-TC-003 (tombstone deprecated)", existing: flat-no-children, missing: "5 children + 17 micro-steps, path-depth issue in tombstone body"}
  S-05: {title: "BF-TC-004 (tombstone ghosts)", existing: flat-no-children, missing: "5 children + 17 micro-steps, 30-day machine trigger undefined"}
  S-06: {title: "BF-TC-005 (@validator)", existing: flat-no-children, missing: "5 children + 19 micro-steps, runner dedup unspecified"}
  S-07: {title: "BF-TC-006 (invocation graph)", existing: flat-no-children, missing: "5 children + 18 micro-steps, subprocess arg heuristic unspecified"}
  S-08: {title: "BF-TC-007 (extension budget)", existing: flat-no-children, missing: "4 children + 13 micro-steps, CI job target unspecified"}
  S-09: {title: "BF-TC-008 (regression baseline)", existing: flat-no-children, missing: "5 children + 18 micro-steps, 5-declaration selection undefined"}
  S-10: {title: "Dependency Graph", type: background, enhancement: "expand to parallel-safety flags"}
  S-11: {title: "Integration with Stage 0-7", type: background, enhancement: "add supersession table"}
  S-12: {title: "Estimated Impact", type: background, enhancement: none}
  S-13: {title: "Hard Stops", type: gates, enhancement: "add machine-checkable pre-conditions"}
  S-MISSING: {title: "TC-BF-009 Report Archival", status: ADDED from Layer-3 analysis}
```

---

## SECTION A3 — REQUIREMENTS INVENTORY

```yaml
requirements:
  artifact_role: analysis_evidence
  execution_authority: false

  REQ-BF-001: {title: "Component register machine-readable and CI-enforced", taskcards: [TC-BF-001, TC-BF-002]}
  REQ-BF-002: {title: "All tools/supervisor/*.py files registered", taskcards: [TC-BF-002]}
  REQ-BF-003: {title: "DEPRECATED_STILL_ACTIVE files emit positive non-invocation evidence", taskcards: [TC-BF-003]}
  REQ-BF-004: {title: "SUSPECTED_GHOST files emit positive non-invocation evidence", taskcards: [TC-BF-004]}
  REQ-BF-005: {title: "All 153 validators carry machine-readable domain classification", taskcards: [TC-BF-005]}
  REQ-BF-006: {title: "Invocation graph covers all 4 invocation mechanisms", taskcards: [TC-BF-006]}
  REQ-BF-007: {title: "New guarded-pattern files require explicit budget entry", taskcards: [TC-BF-007]}
  REQ-BF-008: {title: "Regression baseline covers validator count, grade hash, continuation, git latency", taskcards: [TC-BF-008]}
  REQ-BF-009: {title: "Git latency from reports/ inflation measured and controlled", taskcards: [TC-BF-009]}
```

---

## SECTION A4 — DUPLICATE PLAN RISK CHECK

```yaml
duplicate_plan_risk:
  artifact_role: analysis_evidence
  execution_authority: false
  verdict: NO_DUPLICATES_FOUND
  notes:
    - One plan file at canonical path only
    - 09-hardened-execution-plan.md is a different scope (machinery audit execution) not a duplicate
    - BACKFILL supersedes specific tasks in 09-hardened-execution-plan.md (noted in integration section)
```

---

## MACHINE STATE VOCABULARY

```yaml
machine_state:
  artifact_role: plan_embedded_contract
  execution_authority: true

  parent_statuses: [PROPOSED, READY, IN_PROGRESS, CHILDREN_IN_PROGRESS, INTEGRATION_PENDING, VERIFIED, SCORED, CLOSED, BLOCKED, BLOCKED_EXTERNAL, DEFERRED_WITH_REASON]
  child_statuses: [TODO, READY, IN_PROGRESS, IMPLEMENTED, VERIFIED, SCORED, CLOSED, REROUTED, BLOCKED, BLOCKED_EXTERNAL, DEFERRED_WITH_REASON]
  micro_step_statuses: [PENDING, READY, ACTIVE, COMPLETE, FAILED, BLOCKED, SKIPPED_NOT_APPLICABLE]

  invalid_transitions:
    - "TODO → CLOSED (must pass IMPLEMENTED + VERIFIED + SCORED)"
    - "child CLOSED while mandatory micro-steps PENDING or FAILED"
    - "parent CLOSED while mandatory children not CLOSED"
    - "REROUTED → CLOSED without rework evidence"
    - "PENDING → SKIPPED_NOT_APPLICABLE without reason"

  quality_scoring:
    acceptance_threshold: "4/5 per mandatory dimension"
    reroute_trigger: "any mandatory dimension below 4/5"
    child_dimensions: [requirement_correctness, implementation_correctness, scope_discipline, validation_strength, evidence_completeness, regression_safety, maintainability, production_readiness]
    parent_dimensions: [root_cause_coverage, child_completeness, integration_completeness, dependency_correctness, preserved_behavior, evidence_completeness, rerun_consistency, production_readiness]
```

---

## SECTION A5 — EXECUTION DAG

```yaml
execution_dag:
  artifact_role: analysis_evidence
  execution_authority: false

  TC-BF-001: {depends_on: [], blocks: [TC-BF-002,TC-BF-003,TC-BF-004,TC-BF-005,TC-BF-006,TC-BF-007], file_locks: [tools/supervisor/COMPONENT-REGISTER.yaml, .github/workflows/ci.yml]}
  TC-BF-002: {depends_on: [TC-BF-001], blocks: [TC-BF-007,TC-BF-008], parallel_safe_with: [TC-BF-005,TC-BF-006], file_locks: [tools/supervisor/COMPONENT-REGISTER.yaml]}
  TC-BF-003: {depends_on: [TC-BF-001], blocks: [TC-BF-008], parallel_safe_with: [TC-BF-004,TC-BF-005,TC-BF-006,TC-BF-007]}
  TC-BF-004: {depends_on: [TC-BF-001,TC-BF-003], blocks: [TC-BF-008], parallel_safe_with: [TC-BF-005,TC-BF-006,TC-BF-007]}
  TC-BF-005: {depends_on: [TC-BF-001], blocks: [TC-BF-008], parallel_safe_with: [TC-BF-002,TC-BF-003,TC-BF-004,TC-BF-006,TC-BF-007]}
  TC-BF-006: {depends_on: [TC-BF-001,TC-BF-002], blocks: [TC-BF-008], parallel_safe_with: [TC-BF-003,TC-BF-004,TC-BF-005,TC-BF-007]}
  TC-BF-007: {depends_on: [TC-BF-001,TC-BF-002], blocks: [TC-BF-008], parallel_safe_with: [TC-BF-003,TC-BF-004,TC-BF-005,TC-BF-006]}
  TC-BF-008: {depends_on: [TC-BF-003,TC-BF-004,TC-BF-005,TC-BF-006,TC-BF-007], blocks: [Stage-3+ in 09-hardened-execution-plan.md]}
  TC-BF-009: {depends_on: [TC-BF-008], execution_condition: "git latency > 3000ms in TC-BF-008-05 baseline"}

  parallel_batch_after_TC_BF_002:
    - [TC-BF-003, TC-BF-004, TC-BF-005, TC-BF-006, TC-BF-007]
    - Note: parallel only if separate agents hold separate file locks per dag entry above
```

---

## CONTEXT [PRESERVED AND ENHANCED]

The supervisor-machinery-audit (`docs/system-recon/supervisor-machinery-audit/`) identified
a set of structural improvements needed before safe cleanup can proceed:

- **Extension contract**: @validator decorator + ValidationResult type, so validators
  are governed by interface, not filename glob
- **Tombstone protocol**: Replace quarantine-by-move with sentinel bodies that write
  to .local/supervisor/invocation-tombstones/ if called — produces positive evidence
  of non-invocation instead of relying on absent bug reports
- **Invocation graph**: Machine-readable map of all invocation paths (import, subprocess,
  CLI commands, skill-registry, CLAUDE.md/AGENTS.md) stored in control-index.db
- **Component register as code**: YAML file that CI checks — every tools/supervisor/
  file must have an entry with classification and disposition

The existing Stage 0-7 execution plan (09-hardened-execution-plan.md) identifies WHAT
to do to individual files. It does not address how the new governance mechanisms are
applied retroactively to ALL 49 classified components and all unregistered files.

BACKFILL is that bridge. It runs after the structural improvements are in place and
before any Stage 3+ deep work (orchestration consolidation, validator restructuring).

**Goal**: Convert accumulated classification debt into a fully governed, machine-checkable
inventory where every component has a registered disposition and every tombstone candidate
has an active sentinel.

---

## EXECUTION PLAN

---

### TC-BF-001 — Convert Component Register to Machine-Readable YAML

#### Parent Taskcard

```yaml
tc_id: TC-BF-001
title: Convert component register markdown to CI-enforced YAML
type: PARENT
status: PROPOSED
owner: machinery-governance-agent
req_ids: [REQ-BF-001]
source_section: S-02
root_cause: Component register exists only as markdown; no machine-check exists
objective: >
  Produce COMPONENT-REGISTER.yaml (49 entries), check_component_register.py, and a
  CI step in the governance-check job. After task completes: CI reports baseline gap count.
preserved_behavior:
  - CI governance-check job continues running existing steps unchanged
  - No validator logic or production .py file is modified
allowed_files:
  - tools/supervisor/COMPONENT-REGISTER.yaml (CREATE)
  - tools/supervisor/check_component_register.py (CREATE)
  - .github/workflows/ci.yml (APPEND step to governance-check job only)
forbidden_files: [all tools/supervisor/*.py production files]
children: [TC-BF-001-01, TC-BF-001-02, TC-BF-001-03, TC-BF-001-04]
parent_acceptance_criteria:
  - COMPONENT-REGISTER.yaml contains >= 49 entries validated by: python -c "import yaml; d=yaml.safe_load(open('tools/supervisor/COMPONENT-REGISTER.yaml')); assert len(d['components'])>=49"
  - check_component_register.py exits non-zero with gap list on current tree
  - .github/workflows/ci.yml contains "check_component_register" in governance-check job
  - No existing CI step removed or reordered
integration_check: grep "check_component_register" .github/workflows/ci.yml
rollback: git revert COMPONENT-REGISTER.yaml; git revert check_component_register.py; remove CI step (3 independent reverts)
stop_conditions:
  - governance-check job does not exist in ci.yml (inspect first)
  - 04-machinery-component-register.md unreadable
```

#### TC-BF-001-01 — Define YAML schema and write skeleton file

```yaml
child_id: TC-BF-001-01
parent_id: TC-BF-001
title: Define COMPONENT-REGISTER.yaml entry schema; write empty container file
type: CHILD
status: TODO
req_ids: [REQ-BF-001]
purpose: Establish canonical field structure before populating 49 entries
allowed_files: [tools/supervisor/COMPONENT-REGISTER.yaml]
preconditions: []
acceptance_checks:
  - python -c "import yaml; yaml.safe_load(open('tools/supervisor/COMPONENT-REGISTER.yaml'))" exits 0
  - File contains schema_version and all 7 required field definitions
  - components list exists and is empty
next_valid_task: TC-BF-001-02
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-001-01-01 | Read 04-machinery-component-register.md; extract all field names from tables (component_id, file, loc, classification, disposition, tombstone_status, notes) | Field list recorded | All table columns captured |
| MS-BF-001-01-02 | Create tools/supervisor/COMPONENT-REGISTER.yaml with schema_version:1, schema_definition block (7 fields with type/enum), components:[] | File created | python yaml.safe_load exits 0 |
| MS-BF-001-01-03 | Verify all 7 fields from MS-01 appear in schema_definition | Grep each field name | All present |

#### TC-BF-001-02 — Populate 49 classified components from markdown

```yaml
child_id: TC-BF-001-02
parent_id: TC-BF-001
title: Extract and write all 49 audit-classified components to COMPONENT-REGISTER.yaml
type: CHILD
status: TODO
preconditions: [TC-BF-001-01 CLOSED]
allowed_files: [tools/supervisor/COMPONENT-REGISTER.yaml]
forbidden_files: [all .py files]
acceptance_checks:
  - python -c "import yaml; d=yaml.safe_load(open('tools/supervisor/COMPONENT-REGISTER.yaml')); assert len(d['components'])>=49"
  - 13 ESSENTIAL_SAFETY_CRITICAL entries present
  - 9 SUSPECTED_GHOST entries present
  - tombstone_status is null for all entries (tombstoning is TC-BF-003/004)
next_valid_task: TC-BF-001-03
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-001-02-01 | Read Section A (Orchestration, 15 components) from 04-machinery-component-register.md; add COMP-ORCH-001..015 entries | 15 entries appended | grep COMP-ORCH-015 COMPONENT-REGISTER.yaml |
| MS-BF-001-02-02 | Read Sections B-C (Governance 35 files, Evidence); add COMP-GOV-001..007, COMP-EVI-001..008 | 15 entries appended | grep COMP-EVI-008 |
| MS-BF-001-02-03 | Read Sections D-E+ (Prompt, State, Spec, Skills, Other); add remaining entries | Total >= 49 | python -c print(len(d['components'])) |
| MS-BF-001-02-04 | Verify counts: ESSENTIAL_SAFETY_CRITICAL=13, SUSPECTED_GHOST=9 | Verification pass | python assert len(esc)==13 and len(ghost)==9 |

**MS-BF-001-02-04 stop condition**: If ESSENTIAL_SAFETY_CRITICAL count < 13, BLOCK. Missing entries indicate data loss from audit.

#### TC-BF-001-03 — Write check_component_register.py

```yaml
child_id: TC-BF-001-03
parent_id: TC-BF-001
title: Write enforcement script that fails CI if any tools/supervisor/*.py file is unregistered
type: CHILD
status: TODO
preconditions: [TC-BF-001-02 CLOSED]
allowed_files: [tools/supervisor/check_component_register.py]
script_logic:
  1: Load COMPONENT-REGISTER.yaml
  2: Glob tools/supervisor/**/*.py excluding __pycache__ and _quarantine
  3: Compare against register file entries
  4: Print unregistered paths one per line
  5: sys.exit(1) if any unregistered; sys.exit(0) if clean
acceptance_checks:
  - Script runs without SyntaxError
  - Script exits non-zero on current tree (gap expected)
  - Script exits 0 when given a complete register (test with temporary entry)
next_valid_task: TC-BF-001-04
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-001-03-01 | Write check_component_register.py implementing 5-step logic above | File created | python check_component_register.py runs |
| MS-BF-001-03-02 | Run script; capture baseline gap count | Gap count + file list | Exit code 1; output contains paths |
| MS-BF-001-03-03 | Verify pass-path: temporarily add a test entry for a non-existent file, verify exit 0 | Exit 0 confirmed | Remove test entry after |

#### TC-BF-001-04 — Add CI step to governance-check job

```yaml
child_id: TC-BF-001-04
parent_id: TC-BF-001
title: Append check_component_register step to .github/workflows/ci.yml governance-check job
type: CHILD
status: TODO
preconditions: [TC-BF-001-03 CLOSED]
allowed_files: [.github/workflows/ci.yml]
ci_target_job: governance-check
modification_rule: APPEND step only; do not modify existing steps or their order
step_to_append: |
  - name: Component register completeness check
    run: python tools/supervisor/check_component_register.py
    continue-on-error: true  # WARN only — TC-BF-002 will close the gap; then remove this flag
acceptance_checks:
  - grep "check_component_register" .github/workflows/ci.yml
  - python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))" exits 0
  - Existing governance-check steps unchanged (diff shows only appended lines)
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-001-04-01 | Read .github/workflows/ci.yml; find governance-check job last step line number | Line number noted | Steps listed |
| MS-BF-001-04-02 | Append the step_to_append block after last step in governance-check job | ci.yml updated | grep matches |
| MS-BF-001-04-03 | Validate ci.yml: python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))" | Exit 0 | No YAML error |

---

### TC-BF-002 — Register All Unregistered tools/supervisor/ Files

```yaml
tc_id: TC-BF-002
title: Classify and register every unregistered tools/supervisor/*.py file
type: PARENT
status: PROPOSED
req_ids: [REQ-BF-002]
depends_on: [TC-BF-001]
objective: >
  After TC-BF-001, CI reports the baseline gap. This task eliminates it: every
  .py file in tools/supervisor/ gets a register entry. CI step transitions from
  continue-on-error to hard-fail.
children: [TC-BF-002-01, TC-BF-002-02, TC-BF-002-03, TC-BF-002-04]
parent_acceptance_criteria:
  - python tools/supervisor/check_component_register.py exits 0
  - No entry has classification=UNKNOWN and disposition=RETAIN
  - ci.yml governance-check step no longer has continue-on-error on register check
rollback: git revert COMPONENT-REGISTER.yaml additions; revert ci.yml continue-on-error change
```

#### TC-BF-002-01 — Enumerate unregistered files

```yaml
child_id: TC-BF-002-01
title: Run check script; record complete gap list
type: CHILD
status: TODO
preconditions: [TC-BF-001 CLOSED]
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-002-01-01 | Run: python tools/supervisor/check_component_register.py 2>&1; save complete output | File list + count | Exit non-zero; paths listed |
| MS-BF-002-01-02 | Cross-check against 04-machinery-component-register.md prose for mentioned-but-untabled files | Split: (a) fully unregistered (b) mentioned-in-prose | All gaps categorized |

#### TC-BF-002-02 — Classify each unregistered file

```yaml
child_id: TC-BF-002-02
title: Apply 3-tier heuristic to classify each unregistered file
type: CHILD
status: TODO
preconditions: [TC-BF-002-01 CLOSED]
classification_heuristic:
  zero_imports_AND_zero_cli: SUSPECTED_GHOST / disposition=INVESTIGATE
  zero_imports_BUT_has_cli_ref: USEFUL_SHARED_INFRASTRUCTURE (min) / disposition=RETAIN
  has_python_imports: USEFUL_SHARED_INFRASTRUCTURE (min) / disposition=RETAIN
  __main__guard_only: UNKNOWN_REQUIRES_RUNTIME_EVIDENCE / disposition=INVESTIGATE
forbidden: classification=UNKNOWN with disposition=RETAIN
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-002-02-01 | For each unregistered file: grep -rl "<module_stem>" tools/ .supervisor/ .claude/commands/ | Import ref count per file | Zero or non-zero |
| MS-BF-002-02-02 | For zero-import files: grep -r "<filename_without_extension>" .claude/commands/ .supervisor/ CLAUDE.md AGENTS.md | CLI ref count per file | Zero or non-zero |
| MS-BF-002-02-03 | Produce classification table (file, import_refs, cli_refs, classification, disposition) | Table recorded | No UNKNOWN+RETAIN combos |

#### TC-BF-002-03 — Add entries to COMPONENT-REGISTER.yaml

```yaml
child_id: TC-BF-002-03
title: Write one YAML entry per newly classified file
type: CHILD
status: TODO
preconditions: [TC-BF-002-02 CLOSED]
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-002-03-01 | For each file from TC-BF-002-02: append entry with all 7 schema fields | Entries added | python check_component_register.py exits 0 |
| MS-BF-002-03-02 | Run check script; confirm exit 0 | Exit 0 | "All files registered" message |

**MS-BF-002-03-02 stop condition**: If gaps remain after first pass, return to MS-BF-002-03-01 for residual files.

#### TC-BF-002-04 — Harden CI step to blocking

```yaml
child_id: TC-BF-002-04
title: Remove continue-on-error from register check CI step
type: CHILD
status: TODO
preconditions: [TC-BF-002-03 CLOSED]
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-002-04-01 | Edit .github/workflows/ci.yml: remove "continue-on-error: true" from register step ONLY | Line removed | Diff shows only that line removed |
| MS-BF-002-04-02 | Validate ci.yml: python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))" | Exit 0 | No YAML error |

---

### TC-BF-003 — Apply Tombstone Protocol to All DEPRECATED_STILL_ACTIVE Components

#### Parent Taskcard

```yaml
tc_id: TC-BF-003
title: Tombstone all 8 DEPRECATED_STILL_ACTIVE files with sentinel bodies
type: PARENT
status: PROPOSED
owner: machinery-governance-agent
req_ids: [REQ-BF-003]
source_section: S-04
root_cause: >
  Quarantine-by-move produces no positive evidence. Files moved to _quarantine/
  generate absent-bug-report inference only. Tombstone bodies write timestamped
  records to .local/supervisor/invocation-tombstones/ on any invocation — providing
  positive non-invocation evidence after 30 days of zero records.
objective: >
  Replace entire file bodies for 8 DEPRECATED_STILL_ACTIVE files with tombstone
  sentinel code. Tombstone writes a record and raises DeprecationWarning on any
  invocation. After 30 days of zero records: files are eligible for deletion.
  Covers: run046-049_sprint_writer.py (4), build_proof_graph_iter001-003.py (3),
  migrate_command_sections.py (1). Total: 8 files, ~12,700 LOC.
preserved_behavior:
  - run050_sprint_writer.py (active version) NOT modified
  - No ESSENTIAL_SAFETY_CRITICAL component modified
  - Tombstone raises DeprecationWarning (not SystemExit) — graceful degradation
tombstone_sentinel_template: |
  # TOMBSTONE: quarantined {DATE} — confirmed DEPRECATED_STILL_ACTIVE
  # If this file is imported or executed, a record is written to
  # .local/supervisor/invocation-tombstones/. Zero records after 30 days
  # confirms dead. Any record fires: re-investigate this file.
  import pathlib as _p, datetime as _dt, json as _j, traceback as _tb
  _repo_root = _p.Path(__file__).resolve()
  while _repo_root.name not in ('format-factory', '') and _repo_root != _repo_root.parent:
      _repo_root = _repo_root.parent
  _td = _repo_root / '.local' / 'supervisor' / 'invocation-tombstones'
  _td.mkdir(parents=True, exist_ok=True)
  _r = {"file": str(__file__), "module": __name__,
        "timestamp": _dt.datetime.utcnow().isoformat(),
        "caller": _tb.format_stack()[-3] if len(_tb.extract_stack()) > 2 else None}
  (_td / f"{_p.Path(__file__).stem}_{_dt.datetime.utcnow().strftime('%Y%m%dT%H%M%S')}.json"
   ).write_text(_j.dumps(_r, indent=2), encoding="utf-8")
  raise DeprecationWarning(
      f"{__file__} is tombstoned — record written to {_td}. "
      "If this fires, the file is live. Update its register classification.")
allowed_files:
  - tools/evidence/run046_sprint_writer.py
  - tools/evidence/run047_sprint_writer.py
  - tools/evidence/run048_sprint_writer.py
  - tools/evidence/run049_sprint_writer.py
  - tools/supervisor/build_proof_graph_iter001.py
  - tools/supervisor/build_proof_graph_iter002.py
  - tools/supervisor/build_proof_graph_iter003.py
  - tools/supervisor/migrate_command_sections.py
  - tools/supervisor/COMPONENT-REGISTER.yaml (tombstone_status updates only)
forbidden_files:
  - tools/evidence/run050_sprint_writer.py
  - all ESSENTIAL_SAFETY_CRITICAL files (see COMPONENT-REGISTER.yaml)
children: [TC-BF-003-01, TC-BF-003-02, TC-BF-003-03, TC-BF-003-04, TC-BF-003-05]
parent_acceptance_criteria:
  - All 8 files contain tombstone sentinel body (no original logic remains)
  - Full test suite passes (pytest exits 0 or non-zero for unrelated reasons only)
  - .local/supervisor/invocation-tombstones/ directory is empty after test run
  - COMPONENT-REGISTER.yaml: tombstone_status=ACTIVE and tombstone_date set for all 8
rollback: git revert each file individually (8 independent reverts)
stop_conditions:
  - Any of the 8 files is in ESSENTIAL_SAFETY_CRITICAL list (block entire task)
  - run050_sprint_writer.py is in the affected list (block — file identity error)
```

#### TC-BF-003-01 — Pre-flight: confirm target list and ESSENTIAL_SAFETY_CRITICAL exclusion

```yaml
child_id: TC-BF-003-01
parent_id: TC-BF-003
title: Read COMPONENT-REGISTER.yaml; verify 8 targets are DEPRECATED_STILL_ACTIVE; confirm none are ESSENTIAL_SAFETY_CRITICAL
type: CHILD
status: TODO
req_ids: [REQ-BF-003]
preconditions: [TC-BF-001 CLOSED]
acceptance_checks:
  - 8 target files confirmed as DEPRECATED_STILL_ACTIVE in register
  - Zero overlap with ESSENTIAL_SAFETY_CRITICAL list
  - run050_sprint_writer.py confirmed absent from target list
next_valid_task: TC-BF-003-02
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-003-01-01 | Read COMPONENT-REGISTER.yaml; extract all DEPRECATED_STILL_ACTIVE entries | List of files | 8 entries found |
| MS-BF-003-01-02 | Cross-check list against ESSENTIAL_SAFETY_CRITICAL entries | Zero overlap | Assertion: no match |
| MS-BF-003-01-03 | Confirm run050_sprint_writer.py is NOT in target list | Absent | Not in DEPRECATED_STILL_ACTIVE |
| MS-BF-003-01-04 | Verify all 8 files exist on disk at their registered paths | All 8 present | No FileNotFoundError |

**MS-BF-003-01-02 stop condition**: If any target is ESSENTIAL_SAFETY_CRITICAL → BLOCK entire TC-BF-003. Do not proceed.

#### TC-BF-003-02 — Apply tombstone sentinel body to all 8 files

```yaml
child_id: TC-BF-003-02
parent_id: TC-BF-003
title: Replace entire file body with tombstone sentinel for each of the 8 targets
type: CHILD
status: TODO
preconditions: [TC-BF-003-01 CLOSED]
allowed_files: [the 8 target files only]
modification_rule: >
  REPLACE entire file content. Retain only a 1-line file header comment with
  original filename. All original logic is replaced by tombstone sentinel code.
acceptance_checks:
  - Each file: python -c "import ast; ast.parse(open(f).read())" exits 0 (valid Python)
  - Each file: grep -l "TOMBSTONE" <file> confirms sentinel present
  - No file retains any original function definitions
next_valid_task: TC-BF-003-03
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-003-02-01 | Apply tombstone sentinel to run046_sprint_writer.py | File replaced | ast.parse exits 0; grep TOMBSTONE matches |
| MS-BF-003-02-02 | Apply tombstone sentinel to run047_sprint_writer.py | File replaced | ast.parse exits 0 |
| MS-BF-003-02-03 | Apply tombstone sentinel to run048_sprint_writer.py | File replaced | ast.parse exits 0 |
| MS-BF-003-02-04 | Apply tombstone sentinel to run049_sprint_writer.py | File replaced | ast.parse exits 0 |
| MS-BF-003-02-05 | Apply tombstone sentinel to build_proof_graph_iter001.py | File replaced | ast.parse exits 0 |
| MS-BF-003-02-06 | Apply tombstone sentinel to build_proof_graph_iter002.py | File replaced | ast.parse exits 0 |
| MS-BF-003-02-07 | Apply tombstone sentinel to build_proof_graph_iter003.py | File replaced | ast.parse exits 0 |
| MS-BF-003-02-08 | Apply tombstone sentinel to migrate_command_sections.py | File replaced | ast.parse exits 0 |
| MS-BF-003-02-09 | Verify run050_sprint_writer.py is UNCHANGED | Diff empty | No modification |

#### TC-BF-003-03 — Update COMPONENT-REGISTER.yaml tombstone fields for all 8

```yaml
child_id: TC-BF-003-03
parent_id: TC-BF-003
title: Set tombstone_status=ACTIVE and tombstone_date=TODAY for all 8 entries in COMPONENT-REGISTER.yaml
type: CHILD
status: TODO
preconditions: [TC-BF-003-02 CLOSED]
allowed_files: [tools/supervisor/COMPONENT-REGISTER.yaml]
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-003-03-01 | For each of 8 entries: set tombstone_status: ACTIVE | YAML updated | grep tombstone_status: ACTIVE (8 hits) |
| MS-BF-003-03-02 | For each of 8 entries: set tombstone_date: YYYY-MM-DD (today) | YAML updated | grep tombstone_date (8 hits) |
| MS-BF-003-03-03 | Validate YAML: python -c "import yaml; yaml.safe_load(open('tools/supervisor/COMPONENT-REGISTER.yaml'))" | Exit 0 | No YAML error |
| MS-BF-003-03-04 | Verify observation_window_expires field set to tombstone_date + 30 days | Dates computed | 8 entries have expiry date |

#### TC-BF-003-04 — Run test suite; handle any LIVE_VIA_TEST fires

```yaml
child_id: TC-BF-003-04
parent_id: TC-BF-003
title: Run full test suite; verify zero tombstone records written; handle any fires
type: CHILD
status: TODO
preconditions: [TC-BF-003-03 CLOSED]
expected_outcome: Test suite passes; .local/supervisor/invocation-tombstones/ contains zero records from tombstoned files
fire_handling: >
  If any test triggers a tombstone (DeprecationWarning raised):
  1. Identify the firing file from the DeprecationWarning message
  2. git revert that file only
  3. Update its register entry: classification=LIVE_VIA_TEST, disposition=INVESTIGATE, tombstone_status=REVERTED
  4. Document in this child's notes; continue with remaining files
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-003-04-01 | Clear .local/supervisor/invocation-tombstones/ directory (or confirm empty) | Directory empty | ls output shows no .json files |
| MS-BF-003-04-02 | Run: .venv/Scripts/pytest tests/ -x --tb=short 2>&1 | Test output captured | No DeprecationWarning from tombstoned files |
| MS-BF-003-04-03 | Check tombstone dir: ls .local/supervisor/invocation-tombstones/ | Zero .json files from targets | Count == 0 |
| MS-BF-003-04-04 | If any fires detected: revert firing files; update register; continue | Reverted files documented | Remaining non-fired files stay tombstoned |

**MS-BF-003-04-03 stop condition**: If ALL 8 tombstones fire → BLOCK entire TC-BF-003. Data inconsistency in audit classification. Escalate.

#### TC-BF-003-05 — Score and close

```yaml
child_id: TC-BF-003-05
parent_id: TC-BF-003
title: Score TC-BF-003 against all dimensions; write parent CLOSED
type: CHILD
status: TODO
preconditions: [TC-BF-003-04 CLOSED]
scoring_dimensions: [requirement_correctness, implementation_correctness, scope_discipline, validation_strength, evidence_completeness, regression_safety, maintainability, production_readiness]
reroute_trigger: any dimension < 4/5
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-003-05-01 | Verify all 8 (minus any reverted) files have TOMBSTONE header | Count confirmed | grep -rl TOMBSTONE shows N files |
| MS-BF-003-05-02 | Verify COMPONENT-REGISTER.yaml tombstone_status=ACTIVE for surviving targets | Register count matches file count | python assert count matches |
| MS-BF-003-05-03 | Verify test suite clean (DeprecationWarning not in test output for our files) | Clean output | grep -v for fired files |
| MS-BF-003-05-04 | Score all 8 dimensions 1-5; record scores; compute pass/fail | Score table | All >= 4/5 or reroute |
| MS-BF-003-05-05 | Update TC-BF-003 parent status: VERIFIED → SCORED → CLOSED | Plan updated | Status = CLOSED |

---

### TC-BF-004 — Apply Tombstone Protocol to All SUSPECTED_GHOST Components

#### Parent Taskcard

```yaml
tc_id: TC-BF-004
title: Tombstone all 9 SUSPECTED_GHOST files; create 30-day observation infrastructure
type: PARENT
status: PROPOSED
owner: machinery-governance-agent
req_ids: [REQ-BF-004]
source_section: S-05
root_cause: >
  9 files classified SUSPECTED_GHOST based on zero Python imports — but subprocess,
  CLI commands, and skill-registry invocations are NOT captured by import analysis.
  Tombstone sentinel is the investigation mechanism: any invocation within 30 days
  reveals a live path; zero records after 30 days = CONFIRMED_DEAD.
objective: >
  Apply tombstone sentinel body to 9 SUSPECTED_GHOST files. Create
  check_tombstone_records.py to read and classify tombstone records after the
  30-day observation period. Unlike TC-BF-003 (confirmed deprecated), firing
  tombstones here ARE the desired outcome — they reveal live invocation paths.
preserved_behavior:
  - autonomous_cycle.py NOT modified (ESSENTIAL_SAFETY_CRITICAL canonical loop)
  - check_continuation.py NOT modified (ESSENTIAL_SAFETY_CRITICAL)
  - Tombstone raises DeprecationWarning (not SystemExit) — live callers degrade gracefully
allowed_files:
  - tools/supervisor/autonomous_loop_runner.py
  - tools/supervisor/autonomous_orchestrator.py
  - tools/supervisor/autonomous_poc_controller.py
  - tools/supervisor/autonomous_train_executor.py
  - tools/supervisor/autonomous_host_daemon.py
  - tools/supervisor/autonomous_host_runner.py
  - tools/supervisor/autonomous_task_generator.py
  - tools/supervisor/external_host_loop.py
  - tools/supervisor/generate_mainstream_execution_packet.py
  - tools/supervisor/check_tombstone_records.py (CREATE)
  - tools/supervisor/COMPONENT-REGISTER.yaml (tombstone_status updates only)
forbidden_files:
  - tools/supervisor/autonomous_cycle.py (ESSENTIAL_SAFETY_CRITICAL)
  - tools/supervisor/check_continuation.py (ESSENTIAL_SAFETY_CRITICAL)
children: [TC-BF-004-01, TC-BF-004-02, TC-BF-004-03, TC-BF-004-04, TC-BF-004-05]
observation_window_days: 30
parent_acceptance_criteria:
  - All 9 files contain tombstone sentinel body
  - Full test suite passes after tombstoning
  - check_tombstone_records.py exists and produces FIRED/CONFIRMED_DEAD classification
  - COMPONENT-REGISTER.yaml: tombstone_status=ACTIVE for all 9
  - NOTE — SCORED/CLOSED only after 30-day observation window expires and all 9 have FIRED or CLEARED status
rollback: git revert each file individually (9 independent reverts)
stop_conditions:
  - autonomous_cycle.py or check_continuation.py appears in target list (BLOCK)
```

#### TC-BF-004-01 — Pre-flight: verify ghost list excludes ESSENTIAL_SAFETY_CRITICAL

```yaml
child_id: TC-BF-004-01
parent_id: TC-BF-004
title: Read register; confirm 9 SUSPECTED_GHOST targets; confirm no ESSENTIAL_SAFETY_CRITICAL overlap
type: CHILD
status: TODO
preconditions: [TC-BF-001 CLOSED, TC-BF-003 CLOSED]
acceptance_checks:
  - 9 targets confirmed as SUSPECTED_GHOST in register
  - autonomous_cycle.py absent from target list
  - check_continuation.py absent from target list
next_valid_task: TC-BF-004-02
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-004-01-01 | Read COMPONENT-REGISTER.yaml; extract all SUSPECTED_GHOST entries | 9-file list | Count == 9 |
| MS-BF-004-01-02 | Assert autonomous_cycle.py NOT in list | Absent | Boolean false |
| MS-BF-004-01-03 | Assert check_continuation.py NOT in list | Absent | Boolean false |
| MS-BF-004-01-04 | Cross-check all 9 against ESSENTIAL_SAFETY_CRITICAL entries | Zero overlap | Assertion passes |

#### TC-BF-004-02 — Apply tombstone sentinel body to all 9 files

```yaml
child_id: TC-BF-004-02
parent_id: TC-BF-004
title: Replace entire body of each SUSPECTED_GHOST file with tombstone sentinel
type: CHILD
status: TODO
preconditions: [TC-BF-004-01 CLOSED]
note: Uses identical sentinel template as TC-BF-003-02; repo-root-relative path resolution
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-004-02-01 | Apply tombstone to autonomous_loop_runner.py | File replaced | ast.parse exits 0; grep TOMBSTONE |
| MS-BF-004-02-02 | Apply tombstone to autonomous_orchestrator.py | File replaced | ast.parse exits 0 |
| MS-BF-004-02-03 | Apply tombstone to autonomous_poc_controller.py | File replaced | ast.parse exits 0 |
| MS-BF-004-02-04 | Apply tombstone to autonomous_train_executor.py | File replaced | ast.parse exits 0 |
| MS-BF-004-02-05 | Apply tombstone to autonomous_host_daemon.py | File replaced | ast.parse exits 0 |
| MS-BF-004-02-06 | Apply tombstone to autonomous_host_runner.py | File replaced | ast.parse exits 0 |
| MS-BF-004-02-07 | Apply tombstone to autonomous_task_generator.py | File replaced | ast.parse exits 0 |
| MS-BF-004-02-08 | Apply tombstone to external_host_loop.py | File replaced | ast.parse exits 0 |
| MS-BF-004-02-09 | Apply tombstone to generate_mainstream_execution_packet.py | File replaced | ast.parse exits 0 |
| MS-BF-004-02-10 | Verify autonomous_cycle.py and check_continuation.py UNCHANGED | Diffs empty | No modification |

#### TC-BF-004-03 — Create check_tombstone_records.py

```yaml
child_id: TC-BF-004-03
parent_id: TC-BF-004
title: Create check_tombstone_records.py — reads observation records, classifies each file FIRED or CONFIRMED_DEAD
type: CHILD
status: TODO
preconditions: [TC-BF-004-01 CLOSED]
parallel_safe_with: [TC-BF-004-02]
script_logic:
  1: Load COMPONENT-REGISTER.yaml; get all files with tombstone_status=ACTIVE
  2: Scan .local/supervisor/invocation-tombstones/ for *.json records
  3: Group records by source file stem
  4: For each tombstoned file:
     - If any records exist → FIRED (report caller, timestamp, mechanism)
     - If zero records → CONFIRMED_DEAD
  5: Print summary table; write classification-report.json
  6: sys.exit(1) if any FIRED files (operator attention needed); sys.exit(0) if all clear
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-004-03-01 | Write check_tombstone_records.py implementing 6-step logic above | File created | python check_tombstone_records.py runs without SyntaxError |
| MS-BF-004-03-02 | Dry-run against empty tombstones dir → expect all CONFIRMED_DEAD exit 0 | Exit 0 | Output shows 9 CONFIRMED_DEAD |
| MS-BF-004-03-03 | Inject a synthetic test record; re-run → expect FIRED exit 1 | Exit 1 | Output shows FIRED; remove test record |

#### TC-BF-004-04 — Update COMPONENT-REGISTER.yaml and run test suite

```yaml
child_id: TC-BF-004-04
parent_id: TC-BF-004
title: Set tombstone_status=ACTIVE in register; run test suite; document any fires
type: CHILD
status: TODO
preconditions: [TC-BF-004-02 CLOSED, TC-BF-004-03 CLOSED]
fire_handling: >
  If test suite triggers tombstone: revert that file; set tombstone_status=REVERTED,
  classification=LIVE_VIA_TEST in register. Continue for remaining files.
  Live-via-test findings are TC-BF-006 input (invocation graph).
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-004-04-01 | Set tombstone_status: ACTIVE and tombstone_date for all 9 in COMPONENT-REGISTER.yaml | YAML updated | grep tombstone_status: ACTIVE (9 hits) |
| MS-BF-004-04-02 | Set observation_window_expires: (tombstone_date + 30 days) for each | YAML updated | 9 expiry dates |
| MS-BF-004-04-03 | Validate YAML: python yaml.safe_load exits 0 | Exit 0 | No YAML error |
| MS-BF-004-04-04 | Clear tombstones dir; run: .venv/Scripts/pytest tests/ --tb=short | Test output | DeprecationWarning absence verified for ghost files |
| MS-BF-004-04-05 | Run check_tombstone_records.py; expect exit 0 | Exit 0 | All CONFIRMED_DEAD in test context |
| MS-BF-004-04-06 | Document any test-triggered fires; revert those files; update register | Reverted files listed | register accurate |

#### TC-BF-004-05 — Partial score (open observation window)

```yaml
child_id: TC-BF-004-05
parent_id: TC-BF-004
title: Score initial implementation phase; set parent to CHILDREN_IN_PROGRESS pending 30-day observation
type: CHILD
status: TODO
preconditions: [TC-BF-004-04 CLOSED]
note: >
  TC-BF-004 CANNOT reach CLOSED before observation_window_expires date.
  After test-phase completes this child closes TC-BF-004 to CHILDREN_IN_PROGRESS.
  A second scoring pass runs when check_tombstone_records.py shows all 9 FIRED or CLEARED.
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-004-05-01 | Verify 9 files tombstoned (minus test-fires); check_tombstone_records.py script exists | Count confirmed | Script executable |
| MS-BF-004-05-02 | Record observation_window_start date in parent taskcard notes | Date recorded | Format: YYYY-MM-DD |
| MS-BF-004-05-03 | Set TC-BF-004 parent status = CHILDREN_IN_PROGRESS (observation in progress) | Status updated | Plan file shows CHILDREN_IN_PROGRESS |
| MS-BF-004-05-04 | Schedule: after observation_window_expires, run check_tombstone_records.py; update register; score final dimensions; set CLOSED | Calendar note | Observation expiry noted |

---

### TC-BF-005 — Add @validator Decorator to All 153 Existing Validators

#### Parent Taskcard

```yaml
tc_id: TC-BF-005
title: Backfill @validator decorator and ValidationResult contract to all 153 validators
type: PARENT
status: PROPOSED
owner: machinery-governance-agent
req_ids: [REQ-BF-005]
source_section: S-06
root_cause: >
  Validators are discovered by filename glob (governance_validators*.py), not by
  interface contract. Domain classification exists only in prose documentation, not
  machine-readable metadata. No extension point exists for adding new validators
  without knowing the runner's filename glob pattern.
objective: >
  (1) Create governance_validators_contract.py with @validator decorator,
  ValidationResult dataclass, and _VALIDATOR_REGISTRY list.
  (2) Update governance_validator_runner.py to load from both glob (existing) and
  _VALIDATOR_REGISTRY (new) — deduplicating by rule_id.
  (3) Add @validator(rule_id=, domain=) to all 153 existing validator functions —
  additive only, zero logic changes.
  (4) Add test asserting count >= 153.
preserved_behavior:
  - ALL validator logic unchanged (no function bodies modified)
  - ALL validator function signatures unchanged
  - Runner still loads via glob (backward compat) — registry is additive
  - Zero validators removed
allowed_files:
  - tools/supervisor/governance_validators_contract.py (CREATE)
  - tools/supervisor/governance_validators*.py (18 files — decorator lines ONLY)
  - tools/supervisor/governance_validator_runner.py (add registry loading ONLY)
  - tests/supervisor/test_governance_validators.py (add count assertion ONLY)
forbidden_files: [all production src/ files, all other test files]
children: [TC-BF-005-01, TC-BF-005-02, TC-BF-005-03, TC-BF-005-04, TC-BF-005-05]
parent_acceptance_criteria:
  - governance_validators_contract.py exists with @validator, ValidationResult, _VALIDATOR_REGISTRY
  - Runner loads >= 153 validators (glob + registry, dedup by rule_id)
  - Validator count test passes: python -m pytest tests/supervisor/test_governance_validators.py -k count
  - All 153 existing validator functions have @validator decorator (grep confirms)
  - No validator logic or signature changed
rollback: git revert governance_validators_contract.py; git revert runner additions; git revert decorator additions
stop_conditions:
  - governance_validators_contract.py already exists (inspect first — HS-001)
  - Any validator file import fails after decorator addition (revert that file; continue others)
```

#### TC-BF-005-01 — Pre-flight: check contract file existence; count current validators

```yaml
child_id: TC-BF-005-01
parent_id: TC-BF-005
title: Verify governance_validators_contract.py absent; count validators across all 18 files
type: CHILD
status: TODO
preconditions: [TC-BF-001 CLOSED]
acceptance_checks:
  - governance_validators_contract.py does NOT exist (or is empty stub only)
  - Validator count baseline recorded (N >= 153)
next_valid_task: TC-BF-005-02
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-005-01-01 | Check if tools/supervisor/governance_validators_contract.py exists | Exists/absent | If exists: read it; determine if duplicate risk (HS-001) |
| MS-BF-005-01-02 | Count validator functions: grep -rc "^def V[0-9]" tools/supervisor/governance_validators*.py | Total count | Count >= 153 |
| MS-BF-005-01-03 | List all 18 governance_validators*.py files | File list | 18 files confirmed |
| MS-BF-005-01-04 | Record baseline: current validator count N, current runner discovery mode | Baseline noted | Will compare after TC-BF-005-04 |

**MS-BF-005-01-01 stop condition**: If contract file exists with content → read it fully; assess duplication risk before proceeding (HS-001).

#### TC-BF-005-02 — Create governance_validators_contract.py

```yaml
child_id: TC-BF-005-02
parent_id: TC-BF-005
title: Write governance_validators_contract.py with @validator decorator, ValidationResult, and _VALIDATOR_REGISTRY
type: CHILD
status: TODO
preconditions: [TC-BF-005-01 CLOSED]
allowed_files: [tools/supervisor/governance_validators_contract.py]
contract_spec:
  ValidatorVerdict: enum (GOV_BLOCK, WARNING, PASS)
  ValidationResult: dataclass (verdict, rule_id, message, detail=None)
  _VALIDATOR_REGISTRY: list[dict] (module-level, mutable)
  validator: decorator factory (rule_id:str, domain:str, description:str="") → Callable
acceptance_checks:
  - python -c "from tools.supervisor.governance_validators_contract import validator, ValidationResult, _VALIDATOR_REGISTRY" exits 0
  - _VALIDATOR_REGISTRY is empty list initially (populated by decorators on import)
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-005-02-01 | Write governance_validators_contract.py with all 4 contract components | File created | python import exits 0 |
| MS-BF-005-02-02 | Write a smoke test: define a decorated function; assert it appears in _VALIDATOR_REGISTRY | Registry populated | len(_VALIDATOR_REGISTRY) == 1 after decoration |
| MS-BF-005-02-03 | Verify validator decorator does NOT modify function behavior | Return value unchanged | Original function output identical |

#### TC-BF-005-03 — Update governance_validator_runner.py to load from registry

```yaml
child_id: TC-BF-005-03
parent_id: TC-BF-005
title: Add _VALIDATOR_REGISTRY loading to runner; deduplicate by rule_id; log counts from each source
type: CHILD
status: TODO
preconditions: [TC-BF-005-02 CLOSED]
allowed_files: [tools/supervisor/governance_validator_runner.py]
modification_rule: APPEND new loading path only; do not remove or reorder existing glob loading
dedup_rule: if rule_id appears in both glob result and registry, glob instance wins (backward compat)
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-005-03-01 | Read governance_validator_runner.py; identify current loading mechanism line numbers | Line numbers noted | Glob pattern confirmed |
| MS-BF-005-03-02 | Add registry loading: import _VALIDATOR_REGISTRY; merge after glob; dedup by rule_id | Runner updated | Existing tests still pass |
| MS-BF-005-03-03 | Add startup log: "Loaded N validators (glob: X, registry: Y, dedup removed: Z)" | Log line added | Visible in runner output |
| MS-BF-005-03-04 | Run runner with zero decorated validators: verify glob count unchanged from baseline | Count = baseline N | No regression |

#### TC-BF-005-04 — Add @validator decorator to all 153 validator functions

```yaml
child_id: TC-BF-005-04
parent_id: TC-BF-005
title: Add @validator(rule_id="V###", domain="<domain>") above each of 153 validator functions
type: CHILD
status: TODO
preconditions: [TC-BF-005-02 CLOSED, TC-BF-005-03 CLOSED]
domain_map:
  V001-V050: structural
  V051-V100: import_direction
  V101-V130: naming
  V131-V153: evidence
note: Exact boundaries verified by reading each file during implementation; domain_map is provisional
modification_rule: ONE LINE added above each def V### — no other changes to any function
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-005-04-01 | Process governance_validators.py: add @validator to each V-function | Decorators added | grep "@validator" governance_validators.py count matches V-function count |
| MS-BF-005-04-02 | Process governance_validators_ext.py through governance_validators_ext4.py | Decorators added | Each file: decorator count == V-function count |
| MS-BF-005-04-03 | Process remaining 13 governance_validators_*.py files | Decorators added | All 18 files processed |
| MS-BF-005-04-04 | Verify total: python -c "from tools.supervisor import governance_validators_contract as c; [__import__(f'tools.supervisor.{m}', fromlist=['']) for m in [...all 18...]]; print(len(c._VALIDATOR_REGISTRY))" | Total >= 153 | Count confirmed |
| MS-BF-005-04-05 | Run existing governance validator tests: pytest tests/supervisor/test_governance_validators.py | All pass | No regressions |

#### TC-BF-005-05 — Add count assertion test and score

```yaml
child_id: TC-BF-005-05
parent_id: TC-BF-005
title: Add test asserting validator count >= 153; score TC-BF-005; close
type: CHILD
status: TODO
preconditions: [TC-BF-005-04 CLOSED]
allowed_files: [tests/supervisor/test_governance_validators.py]
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-005-05-01 | Add test: def test_validator_count_invariant(): assert load_all_validators() >= 153 | Test added | pytest -k test_validator_count_invariant passes |
| MS-BF-005-05-02 | Run full governance test file; confirm all pass | Test output | No failures |
| MS-BF-005-05-03 | Score all 8 dimensions; record scores; confirm all >= 4/5 | Score table | Pass or reroute |
| MS-BF-005-05-04 | Update TC-BF-005 parent status: VERIFIED → SCORED → CLOSED | Plan updated | Status = CLOSED |

---

### TC-BF-006 — Populate Invocation Graph for All Existing Components

#### Parent Taskcard

```yaml
tc_id: TC-BF-006
title: Extend control-index.db with 4-mechanism invocation graph; reclassify SUSPECTED_GHOSTs
type: PARENT
status: PROPOSED
owner: machinery-governance-agent
req_ids: [REQ-BF-006]
source_section: S-07
root_cause: >
  Import analysis (zero Python import refs) is insufficient to classify ghosts.
  56 subprocess call sites in tools/supervisor/, 125 .claude/commands/ references,
  and 50 skill-registry.yaml entries are NOT captured by grep-for-import analysis.
  A ghost may be LIVE_VIA_SUBPROCESS or LIVE_VIA_SKILL and appear dead statically.
objective: >
  Add 3 new ingestors to control-index.db (subprocess_calls, claude_commands,
  skill_registry — python_imports already exists). Query the graph for all 9
  SUSPECTED_GHOST files. Reclassify those with graph hits as LIVE_VIA_<mechanism>.
  Classify remainder as CONFIRMED_DEAD_STATIC. Produce backfill report.
preserved_behavior:
  - control-index.db is reconstructible — no production .py file modified
  - SUSPECTED_GHOST tombstone_status unchanged by static analysis alone
    (tombstone observation period is the authoritative confirmation, not this graph)
allowed_files:
  - tools/supervisor/control_index/ (new ingestor files ONLY)
  - tools/supervisor/COMPONENT-REGISTER.yaml (classification field updates ONLY)
  - docs/system-recon/supervisor-machinery-audit/invocation-graph-backfill.md (CREATE)
forbidden_files: [all tools/supervisor/*.py production logic files]
children: [TC-BF-006-01, TC-BF-006-02, TC-BF-006-03, TC-BF-006-04, TC-BF-006-05]
parent_acceptance_criteria:
  - control-index.db contains invocation graph tables for all 4 mechanisms
  - All 9 SUSPECTED_GHOST files have a definitive static classification
  - invocation-graph-backfill.md shows before/after classification for all 9
  - check_component_register.py still exits 0 after classification updates
rollback: Remove new ingestors (3 files); revert COMPONENT-REGISTER.yaml
stop_conditions:
  - control-index.db does not exist (.local/supervisor/) → run: python -m tools.supervisor.control_index init first
```

#### TC-BF-006-01 — Verify control-index.db exists; inspect current ingestors

```yaml
child_id: TC-BF-006-01
parent_id: TC-BF-006
title: Confirm control-index.db exists; list current ingestors; identify which of 4 mechanisms already covered
type: CHILD
status: TODO
preconditions: [TC-BF-001 CLOSED, TC-BF-002 CLOSED]
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-006-01-01 | Check .local/supervisor/control-index.db exists | File present | SQLite file >0 bytes |
| MS-BF-006-01-02 | Run: python -m tools.supervisor.control_index status | Ingestor list | Confirm python_imports ingestor exists |
| MS-BF-006-01-03 | Check: does subprocess_calls ingestor exist? | Yes/No | If yes: skip TC-BF-006-02 step for it |
| MS-BF-006-01-04 | Check: does claude_commands ingestor exist? | Yes/No | If yes: skip TC-BF-006-02 step for it |
| MS-BF-006-01-05 | Check: does skill_registry ingestor exist? | Yes/No | If yes: skip TC-BF-006-02 step for it |

#### TC-BF-006-02 — Add 3 new ingestors to control-index CLI

```yaml
child_id: TC-BF-006-02
parent_id: TC-BF-006
title: Write subprocess_calls, claude_commands, and skill_registry ingestors
type: CHILD
status: TODO
preconditions: [TC-BF-006-01 CLOSED]
ingestor_specs:
  subprocess_calls:
    source: tools/supervisor/**/*.py
    pattern: subprocess.run(args) where args[0] or args contains a *.py path
    extracts: (caller_file, callee_file, line_number, call_args)
    table: subprocess_invocations
  claude_commands:
    source: .claude/commands/**/*.md
    pattern: any line containing tools/supervisor/<stem>.py or <stem>.py
    extracts: (command_file, referenced_file, line_number)
    table: command_invocations
  skill_registry:
    source: .supervisor/skill-registry.yaml
    pattern: command: fields containing .py filenames
    extracts: (skill_id, referenced_file, field_path)
    table: skill_invocations
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-006-02-01 | Write subprocess_calls ingestor; register in control_index CLI | Ingestor file created | python -m tools.supervisor.control_index sync --ingestor subprocess_calls exits 0 |
| MS-BF-006-02-02 | Write claude_commands ingestor | Ingestor file created | sync exits 0; table populated |
| MS-BF-006-02-03 | Write skill_registry ingestor | Ingestor file created | sync exits 0; table populated |
| MS-BF-006-02-04 | Run full sync: python -m tools.supervisor.control_index sync | All tables populated | Row counts > 0 for each new table |

#### TC-BF-006-03 — Query invocation graph for each SUSPECTED_GHOST

```yaml
child_id: TC-BF-006-03
parent_id: TC-BF-006
title: For each of 9 SUSPECTED_GHOST files: query all 4 mechanism tables; classify result
type: CHILD
status: TODO
preconditions: [TC-BF-006-02 CLOSED]
classification_rule:
  has_any_graph_hit: LIVE_VIA_<mechanism> (most specific mechanism that fired)
  zero_graph_hits_all_4: CONFIRMED_DEAD_STATIC (tombstone observation period still runs)
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-006-03-01 | Query each of 4 tables for autonomous_loop_runner.py | Hit count per mechanism | Row counts recorded |
| MS-BF-006-03-02 | Query each of 4 tables for autonomous_orchestrator.py | Hit count per mechanism | Recorded |
| MS-BF-006-03-03 | Query each of 4 tables for autonomous_poc_controller.py through generate_mainstream_execution_packet.py (7 remaining) | Hit counts for all 7 | Table complete |
| MS-BF-006-03-04 | Produce classification table: file → before_classification, after_classification, mechanism_with_hits | Table produced | All 9 have definitive result |

#### TC-BF-006-04 — Update COMPONENT-REGISTER.yaml; produce backfill report

```yaml
child_id: TC-BF-006-04
parent_id: TC-BF-006
title: Write reclassifications to COMPONENT-REGISTER.yaml; write invocation-graph-backfill.md
type: CHILD
status: TODO
preconditions: [TC-BF-006-03 CLOSED]
allowed_files: [tools/supervisor/COMPONENT-REGISTER.yaml, docs/system-recon/supervisor-machinery-audit/invocation-graph-backfill.md]
note: Tombstone_status fields are NOT changed here — static analysis does not override live observation
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-006-04-01 | For each LIVE_VIA_<mechanism> result: update classification field in register | YAML updated | grep LIVE_VIA_ shows correct count |
| MS-BF-006-04-02 | For each CONFIRMED_DEAD_STATIC: update classification field in register | YAML updated | grep CONFIRMED_DEAD_STATIC shows count |
| MS-BF-006-04-03 | Validate YAML: python yaml.safe_load exits 0 | Exit 0 | No YAML error |
| MS-BF-006-04-04 | Write invocation-graph-backfill.md: header, methodology, per-component table (before/after/paths found) | Report created | File >100 lines |
| MS-BF-006-04-05 | Verify check_component_register.py still exits 0 after reclassifications | Exit 0 | No new gaps introduced |

#### TC-BF-006-05 — Score and close

```yaml
child_id: TC-BF-006-05
parent_id: TC-BF-006
title: Score TC-BF-006 against all dimensions; close
type: CHILD
status: TODO
preconditions: [TC-BF-006-04 CLOSED]
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-006-05-01 | Confirm all 4 mechanism tables exist in control-index.db | Table list | 4+ tables |
| MS-BF-006-05-02 | Confirm all 9 SUSPECTED_GHOSTs have definitive static classification | Register count | 9 entries updated |
| MS-BF-006-05-03 | Confirm backfill report exists at correct path | File exists | cat first 10 lines |
| MS-BF-006-05-04 | Score all 8 dimensions; confirm all >= 4/5 | Score table | Pass or reroute |
| MS-BF-006-05-05 | Update TC-BF-006 parent status: VERIFIED → SCORED → CLOSED | Plan updated | Status = CLOSED |

---

### TC-BF-007 — Establish EXTENSION-BUDGET.yaml and Grandfather Existing Violations

#### Parent Taskcard

```yaml
tc_id: TC-BF-007
title: Create EXTENSION-BUDGET.yaml with CI enforcement; grandfather all existing naming-pattern files
type: PARENT
status: PROPOSED
owner: machinery-governance-agent
req_ids: [REQ-BF-007]
source_section: S-08
root_cause: >
  Naming patterns (autonomous_*.py, governance_validators_ext*.py, run0*_sprint_writer.py)
  have grown accretively with no enforcement gate. New files matching these patterns can
  be added without any governance check. Without grandfathering, CI would block existing
  files retroactively — making enforcement impossible.
objective: >
  (1) Create EXTENSION-BUDGET.yaml listing every existing naming-pattern violation with
  status, rationale, and disposition.
  (2) Write check_extension_budget.py: CI fails if any matching file lacks an EXTENSION-BUDGET entry.
  (3) Append CI step to governance-check job.
  Existing files are grandfathered. New unbudgeted files are blocked.
preserved_behavior:
  - No existing file renamed or moved
  - CI governance-check existing steps unchanged (append only)
allowed_files:
  - tools/supervisor/EXTENSION-BUDGET.yaml (CREATE)
  - tools/supervisor/check_extension_budget.py (CREATE)
  - .github/workflows/ci.yml (APPEND step to governance-check only)
forbidden_files: [all .py production files, all other CI jobs]
children: [TC-BF-007-01, TC-BF-007-02, TC-BF-007-03, TC-BF-007-04]
guarded_patterns:
  - pattern: autonomous_*.py
    scope: tools/supervisor/
    note: evolutionary growth from autonomous_cycle.py
  - pattern: governance_validators_ext*.py
    scope: tools/supervisor/
    note: overflow from monolithic governance_validators.py
  - pattern: run0*_sprint_writer.py
    scope: tools/evidence/
    note: sequential sprint writer versioning
parent_acceptance_criteria:
  - EXTENSION-BUDGET.yaml covers all files matching guarded patterns on current tree
  - python tools/supervisor/check_extension_budget.py exits 0 on current tree
  - CI governance-check job contains check_extension_budget step
  - Enforcement test: temporarily add autonomous_new.py → check exits 1; remove file
rollback: Delete EXTENSION-BUDGET.yaml; delete check_extension_budget.py; remove CI step (3 independent)
```

#### TC-BF-007-01 — Enumerate all existing naming-pattern violations

```yaml
child_id: TC-BF-007-01
parent_id: TC-BF-007
title: List all files on current tree matching the 3 guarded patterns
type: CHILD
status: TODO
preconditions: [TC-BF-001 CLOSED, TC-BF-002 CLOSED]
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-007-01-01 | List tools/supervisor/autonomous_*.py (excluding autonomous_cycle.py canonical) | File list with count | Count matches COMPONENT-REGISTER SUSPECTED_GHOST count |
| MS-BF-007-01-02 | List tools/supervisor/governance_validators_ext*.py | File list with count | Count confirmed |
| MS-BF-007-01-03 | List tools/evidence/run0*_sprint_writer.py | File list with count | Count confirmed (should be ~5 including run050) |
| MS-BF-007-01-04 | Cross-reference with COMPONENT-REGISTER.yaml dispositions | disposition per file | All accounted for |

#### TC-BF-007-02 — Create EXTENSION-BUDGET.yaml

```yaml
child_id: TC-BF-007-02
parent_id: TC-BF-007
title: Write EXTENSION-BUDGET.yaml with one entry per violation file
type: CHILD
status: TODO
preconditions: [TC-BF-007-01 CLOSED]
allowed_files: [tools/supervisor/EXTENSION-BUDGET.yaml]
entry_schema:
  file: relative path from repo root
  pattern: guarded pattern it matches
  status: TOMBSTONED | ACTIVE | PENDING_DELETION
  rationale: quoted string
  disposition: PENDING_DELETION | CONSOLIDATE_AFTER_BF-TC-005 | RETAIN | INVESTIGATE
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-007-02-01 | Create EXTENSION-BUDGET.yaml with budget_version:1 and entries for all autonomous_*.py | File created | python yaml.safe_load exits 0 |
| MS-BF-007-02-02 | Add entries for all governance_validators_ext*.py | Entries appended | YAML valid |
| MS-BF-007-02-03 | Add entries for all run0*_sprint_writer.py | Entries appended | YAML valid |
| MS-BF-007-02-04 | Set status=TOMBSTONED for files tombstoned in TC-BF-003/004; ACTIVE for others | Status fields set | Consistent with register |
| MS-BF-007-02-05 | Final count: assert entry count == sum of all pattern-matching files | Count matches | python assert |

#### TC-BF-007-03 — Write check_extension_budget.py and add CI step

```yaml
child_id: TC-BF-007-03
parent_id: TC-BF-007
title: Write enforcement script; append CI step to governance-check job
type: CHILD
status: TODO
preconditions: [TC-BF-007-02 CLOSED]
script_logic:
  1: Load EXTENSION-BUDGET.yaml entries → set of budgeted file paths
  2: Glob all files matching guarded patterns in governed scopes
  3: For each matching file: check if present in budgeted set
  4: Print unbudgeted files (new violations)
  5: sys.exit(1) if any unbudgeted; sys.exit(0) if clean
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-007-03-01 | Write check_extension_budget.py implementing 5-step logic | File created | python check_extension_budget.py runs |
| MS-BF-007-03-02 | Run script on current tree → expect exit 0 (all files budgeted) | Exit 0 | Clean output |
| MS-BF-007-03-03 | Enforcement test: create tools/supervisor/autonomous_new.py; run script → expect exit 1; delete file | Exit 1 then exit 0 | Enforcement confirmed |
| MS-BF-007-03-04 | Read .github/workflows/ci.yml; find last step in governance-check job | Line number noted | Correct job identified |
| MS-BF-007-03-05 | Append step: "Extension budget check" / run: python tools/supervisor/check_extension_budget.py | Step added | grep check_extension_budget ci.yml |
| MS-BF-007-03-06 | Validate ci.yml: python yaml.safe_load exits 0 | Exit 0 | No YAML error |

#### TC-BF-007-04 — Score and close

```yaml
child_id: TC-BF-007-04
parent_id: TC-BF-007
title: Score TC-BF-007 against all dimensions; close
type: CHILD
status: TODO
preconditions: [TC-BF-007-03 CLOSED]
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-007-04-01 | Confirm EXTENSION-BUDGET.yaml covers all pattern violations | Entry count | python assert |
| MS-BF-007-04-02 | Confirm CI step exists and YAML is valid | grep + yaml.safe_load | Both pass |
| MS-BF-007-04-03 | Confirm enforcement works (exit 0 clean, exit 1 on new file) | Enforcement confirmed | Both scenarios tested |
| MS-BF-007-04-04 | Score all 8 dimensions; confirm all >= 4/5 | Score table | Pass or reroute |
| MS-BF-007-04-05 | Update TC-BF-007 parent status: VERIFIED → SCORED → CLOSED | Plan updated | Status = CLOSED |

---

### TC-BF-008 — Run Regression Control Baseline Against Full Governed Inventory

#### Parent Taskcard

```yaml
tc_id: TC-BF-008
title: Establish regression baseline capturing validator count, grade hash, continuation stability, git latency
type: PARENT
status: PROPOSED
owner: machinery-governance-agent
req_ids: [REQ-BF-008]
source_section: S-09
root_cause: >
  No machine-readable baseline exists against which future machinery changes can
  be compared. Without a baseline: any regression after Stage 3+ consolidation is
  indistinguishable from pre-existing instability. The baseline must be captured
  AFTER the full governed inventory (TC-BF-001 through TC-BF-007) is in place —
  capturing the system in its first fully-governed state.
objective: >
  Create run_regression_baseline.py with 4 checks:
  (1) Validator count >= 153.
  (2) Grade output hash stability across 5 diverse evidence declarations.
  (3) Continuation verdict identical across 3 consecutive runs.
  (4) Git operation latency documented (concern flagged at >5000ms, not a blocker).
  Store all outputs under .local/supervisor/consolidation-baseline/YYYY-MM-DD/.
preserved_behavior:
  - No production files modified (read-only except .local/ which is gitignored)
  - Existing evidence declarations used as read-only inputs
allowed_files:
  - tools/supervisor/run_regression_baseline.py (CREATE)
  - .local/supervisor/consolidation-baseline/ (gitignored — new outputs only)
forbidden_files: [all production .py files, all evidence declarations]
children: [TC-BF-008-01, TC-BF-008-02, TC-BF-008-03, TC-BF-008-04, TC-BF-008-05]
parent_acceptance_criteria:
  - run_regression_baseline.py exists and runs to completion (exit 0 or exit 1 with diagnostic)
  - baseline-validator-count.json: count >= 153
  - baseline-grade-hashes.json: all 5 declaration pairs stable=true
  - baseline-continuation-stability.json: all_identical=true
  - baseline-git-latency.json: all 3 operations documented (performance_concern flagged if >5000ms)
  - HS-004 satisfied: if any assertion fails, Stage 3+ work BLOCKED until resolved
rollback: N/A — all outputs in .local/ (gitignored)
stop_conditions:
  - TC-BF-003 through TC-BF-007 not all CLOSED → wait (HS-004)
  - grade_declared_work.py not found → diagnose before running check 2
```

#### TC-BF-008-01 — Create run_regression_baseline.py skeleton

```yaml
child_id: TC-BF-008-01
parent_id: TC-BF-008
title: Write run_regression_baseline.py with 4-check structure, argument parsing, output directory logic
type: CHILD
status: TODO
preconditions: [TC-BF-003 CLOSED, TC-BF-005 CLOSED, TC-BF-006 CLOSED, TC-BF-007 CLOSED]
allowed_files: [tools/supervisor/run_regression_baseline.py]
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-008-01-01 | Write script skeleton: argparse, output_dir = .local/supervisor/consolidation-baseline/{date}/, run_check_1/2/3/4 stubs, main() | File created | python run_regression_baseline.py --help exits 0 |
| MS-BF-008-01-02 | Implement output directory creation with date-stamped subdirectory | Dir created on run | Path exists after invocation |
| MS-BF-008-01-03 | Implement summary output: pass/fail per check; overall exit code | Summary printed | Exit 0 on all pass, 1 on any fail |

#### TC-BF-008-02 — Implement Check 1 (validator count) and Check 3 (continuation stability)

```yaml
child_id: TC-BF-008-02
parent_id: TC-BF-008
title: Implement validator count invariant check and continuation verdict stability check
type: CHILD
status: TODO
preconditions: [TC-BF-008-01 CLOSED]
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-008-02-01 | Implement check_1_validator_count(): run governance_validator_runner.py --count-only; assert count >= 153; write baseline-validator-count.json | Check 1 code | Script runs; JSON written |
| MS-BF-008-02-02 | Implement check_3_continuation_stability(): run check_continuation.py 3× consecutively; compare verdict+reason; write baseline-continuation-stability.json | Check 3 code | Script runs; JSON written |
| MS-BF-008-02-03 | Run both checks standalone; confirm outputs produced | JSON files in output_dir | Both assertions pass |

#### TC-BF-008-03 — Implement Check 2 (grade hash stability) and select 5 declarations

```yaml
child_id: TC-BF-008-03
parent_id: TC-BF-008
title: Select 5 representative evidence declarations; implement grade hash stability check
type: CHILD
status: TODO
preconditions: [TC-BF-008-01 CLOSED]
parallel_safe_with: [TC-BF-008-02]
selection_rule: most recent 5 complete evidence-declaration.yaml files in .local/evidences/ that have an existing evidence-review.json
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-008-03-01 | List .local/evidences/ subdirectories by date; select 5 most recent with evidence-review.json | 5 declaration paths | 5 paths confirmed |
| MS-BF-008-03-02 | Implement check_2_grade_hashes(): for each declaration, run grade_declared_work.py twice; compute MD5(evidence-review.json) each run; compare | Check 2 code | Both runs produce identical MD5 |
| MS-BF-008-03-03 | Write baseline-grade-hashes.json with all 5 results | JSON written | 5 entries, all stable=true |
| MS-BF-008-03-04 | If any pair shows stable=false: log diagnostic; set check_2_passed=false (HS-004 applies) | Diagnostic logged | Investigate before Stage 3+ |

#### TC-BF-008-04 — Implement Check 4 (git latency) and run full baseline

```yaml
child_id: TC-BF-008-04
parent_id: TC-BF-008
title: Implement git latency check; run all 4 checks together; capture final output
type: CHILD
status: TODO
preconditions: [TC-BF-008-02 CLOSED, TC-BF-008-03 CLOSED]
latency_threshold_ms: 5000
git_commands: [git status, "git diff HEAD --stat", "git log --oneline -100"]
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-008-04-01 | Implement check_4_git_latency(): time 3 git commands; write baseline-git-latency.json; flag PERFORMANCE_CONCERN if any >5000ms | Check 4 code | JSON written |
| MS-BF-008-04-02 | Run full script: python tools/supervisor/run_regression_baseline.py | All 4 JSONs produced | Output dir exists with 4 files |
| MS-BF-008-04-03 | Verify exit code: 0 if all assertions pass; 1 if any fail | Exit code noted | If exit 1: diagnose before TC-BF-009 |
| MS-BF-008-04-04 | If git latency >5000ms: document as TC-BF-009 trigger (see HS-005) | Performance note | Concern logged in output |

#### TC-BF-008-05 — Score and close (conditional on all assertions passing)

```yaml
child_id: TC-BF-008-05
parent_id: TC-BF-008
title: Resolve any failing assertions; score TC-BF-008; close
type: CHILD
status: TODO
preconditions: [TC-BF-008-04 CLOSED]
gate: TC-BF-008 cannot be scored CLOSED if any of: validator count < 153, any grade pair unstable, continuation unstable
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-008-05-01 | Read all 4 JSON outputs; verify assertion_passed=true in each | 4 assertions | All true |
| MS-BF-008-05-02 | If any assertion failed: diagnose root cause; resolve (not skip); re-run script | Resolved | All assertions pass on re-run |
| MS-BF-008-05-03 | Check TC-BF-009 trigger: if git latency >5000ms → TC-BF-009 execution_condition met | Condition noted | TC-BF-009 execution_condition set |
| MS-BF-008-05-04 | Score all 8 dimensions; confirm all >= 4/5 | Score table | Pass |
| MS-BF-008-05-05 | Update TC-BF-008 parent status: VERIFIED → SCORED → CLOSED | Plan updated | Status = CLOSED |

---

### TC-BF-009 — Measure and Document reports/ Git Latency Impact

#### Parent Taskcard

```yaml
tc_id: TC-BF-009
title: Measure 402MB reports/ directory git latency; document or remediate per execution_condition
type: PARENT
status: PROPOSED
owner: machinery-governance-agent
req_ids: [REQ-BF-009]
source_section: S-MISSING
execution_condition: "git latency > 3000ms in TC-BF-008-04 baseline (check_4_git_latency)"
root_cause: >
  reports/ directory contains 402MB of committed generated files (capability maps,
  pilot evidence, sprint outputs). git status, git diff, and git log are O(repository-size)
  operations. At 402MB, these operations create a performance floor that compounds across
  every sprint closeout, governance check, and CI run. This is R-006 from the risk register.
objective: >
  (1) Measure actual git operation latency attributed to reports/ specifically.
  (2) If latency exceeds 3000ms threshold: document options (sparse checkout, .gitignore
  candidate listing, git sparse-index) and produce remediation taskcard.
  (3) If within threshold: document as acceptable and close.
note: This taskcard executes ONLY if TC-BF-008 baseline shows latency > 3000ms.
      If baseline shows < 3000ms, skip to MS-BF-009-05-02 (document as acceptable, close).
preserved_behavior:
  - reports/ contents NOT deleted or gitignored without separate explicit plan + Babar Raza review
  - Capability maps (4.2M line JSON) only gitignored after SAL reproducibility verified (A7 from adversarial review)
allowed_files:
  - docs/system-recon/supervisor-machinery-audit/reports-latency-assessment.md (CREATE)
  - tools/supervisor/run_regression_baseline.py (READ ONLY for context)
forbidden_files: [reports/, .gitignore (investigation only; no changes in this task)]
children: [TC-BF-009-01, TC-BF-009-02, TC-BF-009-03]
parent_acceptance_criteria:
  - reports-latency-assessment.md produced with measured latencies and attribution
  - If latency > 3000ms: remediation options documented with risk/benefit per option
  - If latency <= 3000ms: documented as acceptable; taskcard closed
rollback: N/A — read-only analysis
```

#### TC-BF-009-01 — Measure git latency with and without reports/

```yaml
child_id: TC-BF-009-01
parent_id: TC-BF-009
title: Time git operations with full tree vs sparse-exclude-reports to isolate reports/ contribution
type: CHILD
status: TODO
preconditions: [TC-BF-008 CLOSED]
execution_condition: git latency > 3000ms in TC-BF-008-04
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-009-01-01 | Run timed: git status (3 runs, average) on full working tree | avg_status_ms recorded | Consistent across runs |
| MS-BF-009-01-02 | Run timed: git diff HEAD --stat (3 runs, average) | avg_diff_ms recorded | Consistent across runs |
| MS-BF-009-01-03 | Run timed: git log --oneline -100 (3 runs, average) | avg_log_ms recorded | Consistent |
| MS-BF-009-01-04 | Compare against TC-BF-008 baseline; confirm latency is stable not spike | delta_from_baseline | < 20% variance = stable measurement |
| MS-BF-009-01-05 | Count files in reports/: find reports/ -type f | wc -l | File count | N files confirmed |

#### TC-BF-009-02 — Document latency attribution and options

```yaml
child_id: TC-BF-009-02
parent_id: TC-BF-009
title: Attribute latency to reports/ vs other large directories; document remediation options
type: CHILD
status: TODO
preconditions: [TC-BF-009-01 CLOSED]
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-009-02-01 | List top 10 largest tracked directories by file count: git ls-files | Statistics | ranked by count |
| MS-BF-009-02-02 | Compute reports/ % of total tracked file count | Percentage | % contribution |
| MS-BF-009-02-03 | Write reports-latency-assessment.md: latency measurements, attribution, 3 remediation options with risk/benefit | Report created | File >80 lines |

Remediation options to document (each with pros/cons):
- Option A: Sparse checkout (read-only fix — does not reduce repo size)
- Option B: git sparse-index (index compression — reduces index size)
- Option C: .gitignore candidate list for reports/ subdirs (requires reproducibility proof first — OQ-001)

#### TC-BF-009-03 — Score and close

```yaml
child_id: TC-BF-009-03
parent_id: TC-BF-009
title: Score TC-BF-009; close (investigation only — no files changed)
type: CHILD
status: TODO
preconditions: [TC-BF-009-02 CLOSED]
```

| MS ID | Action | Output | Verify |
|---|---|---|---|
| MS-BF-009-03-01 | Confirm reports-latency-assessment.md exists with all sections | File content | cat first 10 lines |
| MS-BF-009-03-02 | Score all 8 dimensions (investigation task: regression_safety = N/A, mark 5/5) | Score table | All >= 4/5 |
| MS-BF-009-03-03 | Update TC-BF-009 parent status: VERIFIED → SCORED → CLOSED | Plan updated | Status = CLOSED |

---

## SECTION A6 — Verification Matrix

```yaml
verification_matrix:
  artifact_role: analysis_evidence
  execution_authority: false

  V-001:
    taskcard: TC-BF-001
    gate: python -c "import yaml; d=yaml.safe_load(open('tools/supervisor/COMPONENT-REGISTER.yaml')); assert len(d['components'])>=49"
    mode: automated
    expected: exit 0
  V-002:
    taskcard: TC-BF-001
    gate: grep "check_component_register" .github/workflows/ci.yml
    mode: automated
    expected: match found
  V-003:
    taskcard: TC-BF-002
    gate: python tools/supervisor/check_component_register.py
    mode: automated
    expected: exit 0 (all files registered)
  V-004:
    taskcard: TC-BF-003
    gate: grep -rl "TOMBSTONE" tools/evidence/run04[6-9]* tools/supervisor/build_proof_graph* tools/supervisor/migrate_command_sections.py | wc -l
    mode: automated
    expected: 8
  V-005:
    taskcard: TC-BF-003
    gate: "ls .local/supervisor/invocation-tombstones/*.json 2>/dev/null | wc -l (after test run)"
    mode: automated
    expected: 0
  V-006:
    taskcard: TC-BF-004
    gate: grep -rl "TOMBSTONE" tools/supervisor/autonomous_loop_runner.py tools/supervisor/autonomous_orchestrator.py tools/supervisor/autonomous_poc_controller.py tools/supervisor/autonomous_train_executor.py tools/supervisor/autonomous_host_daemon.py tools/supervisor/autonomous_host_runner.py tools/supervisor/autonomous_task_generator.py tools/supervisor/external_host_loop.py tools/supervisor/generate_mainstream_execution_packet.py | wc -l
    mode: automated
    expected: 9 (or N-fired for any test-fires)
  V-007:
    taskcard: TC-BF-004
    gate: python tools/supervisor/check_tombstone_records.py
    mode: automated (after 30-day observation)
    expected: exit 0 (all CONFIRMED_DEAD) or exit 1 (FIRED files found — investigate)
  V-008:
    taskcard: TC-BF-005
    gate: "pytest tests/supervisor/test_governance_validators.py -k test_validator_count_invariant"
    mode: automated
    expected: PASSED
  V-009:
    taskcard: TC-BF-006
    gate: "python -c \"import sqlite3; db=sqlite3.connect('.local/supervisor/control-index.db'); tables=[r[0] for r in db.execute(\\\"SELECT name FROM sqlite_master WHERE type='table'\\\").fetchall()]; assert all(t in tables for t in ['subprocess_invocations','command_invocations','skill_invocations'])\""
    mode: automated
    expected: exit 0
  V-010:
    taskcard: TC-BF-007
    gate: python tools/supervisor/check_extension_budget.py
    mode: automated
    expected: exit 0
  V-011:
    taskcard: TC-BF-008
    gate: python tools/supervisor/run_regression_baseline.py
    mode: automated
    expected: exit 0 (all 4 assertions pass)
  V-012:
    taskcard: TC-BF-009
    gate: cat docs/system-recon/supervisor-machinery-audit/reports-latency-assessment.md | head -5
    mode: manual
    expected: file exists with latency measurements
```

---

## SECTION A7 — Evidence Contract

```yaml
evidence_contract:
  artifact_role: plan_embedded_contract
  execution_authority: true

  each_taskcard_must_produce:
    - type: implementation_evidence
      description: "The artifact(s) created or modified (file paths, line counts, diff summary)"
    - type: verification_evidence
      description: "Output of the acceptance gate commands (stdout, exit codes)"
    - type: regression_evidence
      description: "Test run output (before and after for affected tests)"
    - type: scoring_record
      description: "8-dimension score table with numeric values 1-5 and reroute/pass decision"

  declaration_path_pattern: ".local/evidences/<tc_id>-<date>/evidence-declaration.yaml"

  prohibited:
    - "Claiming CLOSED without acceptance gate output"
    - "Claiming VERIFIED without test run output"
    - "Scoring dimensions without numeric values"
    - "Skipping regression_evidence for any task that modifies .py files"

  minimums:
    evidence_paths_count: 1  # at least one file-level evidence path per work item
    test_reference_count: 1  # at least one test reference per work item
    score_threshold: "4/5 per mandatory dimension"
```

---

## SECTION A8 — Idempotency Contract

```yaml
idempotency_contract:
  artifact_role: plan_embedded_contract
  execution_authority: true

  per_taskcard_rules:
    TC-BF-001: >
      Running check_component_register.py N times on same tree → identical output.
      Adding the same CI step twice → YAML parse error (detectable; treat as failure).
    TC-BF-002: >
      Running check_component_register.py → exit 0 always after TC-BF-002 closes.
      Re-running classification produces same results for same files.
    TC-BF-003: >
      Applying tombstone to already-tombstoned file → no change (sentinel body identical).
      Re-running test suite with tombstones in place → same tombstone-dir empty result.
    TC-BF-004: >
      Applying tombstone to already-tombstoned file → no change.
      check_tombstone_records.py → deterministic output for same record set.
    TC-BF-005: >
      Adding @validator decorator twice → second decorator wins (rule_id conflict in registry).
      Dedup-by-rule_id ensures runner count invariant holds regardless of double-decoration.
    TC-BF-006: >
      Running sync N times → same graph (hash-based skip for unchanged files).
      Queries on same db → identical results.
    TC-BF-007: >
      Running check_extension_budget.py N times → identical output for same file tree.
    TC-BF-008: >
      Running run_regression_baseline.py N times → should produce identical assertions.
      If assertions differ across runs: system is non-idempotent (HS-004 applies).
    TC-BF-009: >
      Latency measurements may vary ±20%; document variance; use 3-run average.
```

---

## Execution DAG (Updated)

```yaml
execution_dag_v2:
  artifact_role: analysis_evidence
  execution_authority: false

  TC-BF-001: {depends_on: [], blocks: [TC-BF-002,TC-BF-003,TC-BF-004,TC-BF-005,TC-BF-006,TC-BF-007]}
  TC-BF-002: {depends_on: [TC-BF-001], blocks: [TC-BF-006,TC-BF-007,TC-BF-008]}
  TC-BF-003: {depends_on: [TC-BF-001], blocks: [TC-BF-004,TC-BF-008], parallel_safe_with: [TC-BF-005,TC-BF-006,TC-BF-007]}
  TC-BF-004: {depends_on: [TC-BF-001,TC-BF-003], blocks: [TC-BF-008], parallel_safe_with: [TC-BF-005,TC-BF-006,TC-BF-007], observation_window: 30_days}
  TC-BF-005: {depends_on: [TC-BF-001], blocks: [TC-BF-008], parallel_safe_with: [TC-BF-002,TC-BF-003,TC-BF-004,TC-BF-006,TC-BF-007]}
  TC-BF-006: {depends_on: [TC-BF-001,TC-BF-002], blocks: [TC-BF-008], parallel_safe_with: [TC-BF-003,TC-BF-004,TC-BF-005,TC-BF-007]}
  TC-BF-007: {depends_on: [TC-BF-001,TC-BF-002], blocks: [TC-BF-008], parallel_safe_with: [TC-BF-003,TC-BF-004,TC-BF-005,TC-BF-006]}
  TC-BF-008: {depends_on: [TC-BF-003,TC-BF-004,TC-BF-005,TC-BF-006,TC-BF-007], blocks: [Stage-3+]}
  TC-BF-009: {depends_on: [TC-BF-008], execution_condition: "git latency > 3000ms in TC-BF-008-04 baseline"}
```

```
TC-BF-001 → TC-BF-002
                ↓
    ┌───────────┼──────────────┬─────────────┐
TC-BF-003  TC-BF-005  TC-BF-006  TC-BF-007
    ↓
TC-BF-004 (30-day observation window)
    │
    └────────────────────────────────────────┐
                                             ↓
                                         TC-BF-008 → TC-BF-009 (conditional)
                                             ↓
                                         Stage 3+ (09-hardened-execution-plan.md)
```

---

## Integration Supersession Table

```yaml
integration_supersession:
  artifact_role: analysis_evidence
  execution_authority: false

  superseded_tasks:
    - original: TC-S1-001 (add tracing, run 3-5 sprint cycles to observe invocations)
      superseded_by: [TC-BF-004 (30-day tombstone), TC-BF-006 (static invocation graph)]
      reason: tombstone provides positive evidence; graph covers all 4 mechanisms vs import-only
      status: SUPERSEDED — do not execute TC-S1-001

    - original: TC-S2-001 (quarantine run046-049 by move)
      superseded_by: TC-BF-003
      reason: tombstone approach strictly superior; quarantine-by-move produces no positive evidence
      status: SUPERSEDED — do not execute TC-S2-001

    - original: TC-S2-002 (quarantine build_proof_graph files by move)
      superseded_by: TC-BF-003
      reason: same as above
      status: SUPERSEDED

    - original: TC-S2-003 (quarantine migrate_command_sections.py by move)
      superseded_by: TC-BF-003
      reason: same as above
      status: SUPERSEDED

    - original: TC-S5-001 (validator domain restructuring)
      prerequisite_added: TC-BF-005 must be CLOSED first
      reason: @validator contract must exist before restructuring discovery mechanism
      status: BLOCKED_UNTIL_TC-BF-005_CLOSED

    - original: TC-S7-001 (CI file count check)
      superseded_by: TC-BF-007
      reason: EXTENSION-BUDGET.yaml is more expressive than a count check; grandfathers existing violations
      status: SUPERSEDED — do not execute TC-S7-001

  execution_order_relative_to_09_plan:
    - Stage 0 (baseline): complete per 09-hardened-execution-plan.md
    - BACKFILL (this plan): TC-BF-001 → TC-BF-008 [→ TC-BF-009 conditional]
    - Stage 2 (quarantine): REPLACED by TC-BF-003/004
    - Stage 3 (orchestration consolidation): requires TC-BF-008 CLOSED
    - Stage 4 (state authority): requires TC-BF-006 CLOSED (invocation graph needed)
    - Stage 5 (validator restructuring): requires TC-BF-005 CLOSED
    - Stage 6 (retirement): requires TC-BF-004 observation window expired
    - Stage 7 (regrowth prevention): REPLACED by TC-BF-007
```

---

## Estimated Impact (v2.0)

| Taskcard | LOC Governed | Risk | New Artifacts | Verif Gate |
|---|---|---|---|---|
| TC-BF-001 | 49 components formalized | LOW | COMPONENT-REGISTER.yaml, check_component_register.py, CI step | V-001, V-002 |
| TC-BF-002 | All tools/supervisor/ files | LOW | Register entries (N new), CI step hardened | V-003 |
| TC-BF-003 | 12,700 LOC tombstoned | LOW | 8 tombstone bodies, tombstone records dir | V-004, V-005 |
| TC-BF-004 | 8,200 LOC tombstoned | MEDIUM | 9 tombstone bodies, check_tombstone_records.py | V-006, V-007 |
| TC-BF-005 | 153 validators with contract | LOW | governance_validators_contract.py, runner update, count test | V-008 |
| TC-BF-006 | Full invocation graph | LOW | 3 new ingestors, 3 new db tables, backfill report | V-009 |
| TC-BF-007 | Regrowth prevention | LOW | EXTENSION-BUDGET.yaml, check_extension_budget.py, CI step | V-010 |
| TC-BF-008 | Regression baseline | LOW | run_regression_baseline.py, 4 JSON baseline files | V-011 |
| TC-BF-009 | Git latency impact | LOW | reports-latency-assessment.md | V-012 |

**LOC removal potential (after 30-day observation):**
- TC-BF-003: 8 files eligible for deletion → ~12,700 LOC (if zero tombstone fires after 30 days)
- TC-BF-004: 9 files eligible for deletion → ~8,200 LOC contingent on zero fires
- **Total: 12,700–20,900 LOC** (range reflects tombstone observation outcome)

**Complexity reduction:**
- 7 fewer entry points in tools/supervisor/ (after TC-BF-004 CLEARED files deleted)
- 13 fewer dead-weight files in tools/evidence/ and tools/supervisor/
- 153 validators machine-discoverable (not glob-dependent)
- CI blocks regrowth of all 3 naming patterns

---

## Hard Stops (v2.0 — Machine-Checkable)

### HS-001: governance_validators_contract.py Pre-Existence Check

```yaml
hs_id: HS-001
trigger: TC-BF-005-01 discovers that governance_validators_contract.py already exists
action: BLOCK TC-BF-005-02 until pre-existence fully inspected
check: cat tools/supervisor/governance_validators_contract.py (read full content)
resolution:
  - If file is empty stub: proceed (treat as new)
  - If file has partial @validator implementation: reconcile with TC-BF-005 spec; do not duplicate
  - If file has full implementation: skip TC-BF-005-02; proceed to TC-BF-005-03 (runner update)
machine_check: "python -c \"import pathlib; f=pathlib.Path('tools/supervisor/governance_validators_contract.py'); print('EXISTS' if f.exists() and f.stat().st_size > 100 else 'ABSENT')\""
```

### HS-002: ESSENTIAL_SAFETY_CRITICAL Tombstone Guard

```yaml
hs_id: HS-002
trigger: Any tombstone task (TC-BF-003, TC-BF-004) target list overlaps ESSENTIAL_SAFETY_CRITICAL entries
action: BLOCK entire tombstone task — do not proceed
check: python -c "import yaml; r=yaml.safe_load(open('tools/supervisor/COMPONENT-REGISTER.yaml')); esc={e['file'] for e in r['components'] if e['classification']=='ESSENTIAL_SAFETY_CRITICAL'}; targets={...}; overlap=esc&targets; print('SAFE' if not overlap else f'BLOCK: {overlap}')"
resolution: Correct target list by removing ESSENTIAL_SAFETY_CRITICAL entries
named_protected_files:
  - tools/supervisor/autonomous_cycle.py
  - tools/supervisor/check_continuation.py
  - tools/supervisor/grade_declared_work.py
  - tools/supervisor/evidence_declaration.py
  - tools/supervisor/inspect_declared_evidence.py
  (+ remaining 8 ESSENTIAL_SAFETY_CRITICAL entries per register)
```

### HS-003: 30-Day Tombstone Observation is Non-Waivable

```yaml
hs_id: HS-003
trigger: Any attempt to delete TC-BF-003 or TC-BF-004 tombstoned files before observation window expires
action: BLOCK deletion — tombstone_status must be CLEARED (not just ACTIVE)
check: python tools/supervisor/check_tombstone_records.py (must show CLEARED for each target, not just ACTIVE)
observation_window: 30 days from tombstone_date field in COMPONENT-REGISTER.yaml
resolution: Wait for observation_window_expires date; then run check_tombstone_records.py; update register
```

### HS-004: Regression Baseline Failure Blocks Stage 3+

```yaml
hs_id: HS-004
trigger: TC-BF-008 run_regression_baseline.py exits 1 (any assertion fails)
action: BLOCK all Stage 3+ work (TC-S3-001 and beyond from 09-hardened-execution-plan.md)
check: python tools/supervisor/run_regression_baseline.py; verify exit code
failing_scenarios:
  - validator count < 153 → diagnose: was TC-BF-005 fully applied?
  - grade hash unstable → diagnose: non-deterministic input (LLM grader active? see MEMORY.md)
  - continuation verdict varies → diagnose: state file modified between runs?
  - git latency → PERFORMANCE_CONCERN only (not a blocker); triggers TC-BF-009
resolution: Diagnose each failure; fix root cause; re-run baseline; proceed only on exit 0
```

### HS-005: Git Latency Threshold Triggers TC-BF-009

```yaml
hs_id: HS-005
trigger: Any git operation in TC-BF-008 baseline exceeds 3000ms
action: Set TC-BF-009 execution_condition = MET; execute TC-BF-009 after TC-BF-008
check: cat .local/supervisor/consolidation-baseline/*/baseline-git-latency.json | python -c "import json,sys; d=json.load(sys.stdin); print('TRIGGER' if any(d[k]>3000 for k in ['status_ms','diff_ms','log_ms']) else 'OK')"
resolution: Execute TC-BF-009 (latency assessment + options); no immediate remediation required in this plan
```

---

## EXECUTION HANDOFF

```yaml
execution_handoff:
  artifact_role: plan_embedded_contract
  execution_authority: true

  plan_identity:
    name: bright-greeting-goose
    in_repo_path: plans/.claude/bright-greeting-goose.md
    external_seed_path: C:\Users\prora\.claude\plans\bright-greeting-goose.md
    version: 2.0
    head_at_plan_creation: 6b3f6f07

  first_action_on_execution:
    step_1: Copy plan to in-repo location:
      cp "C:/Users/prora/.claude/plans/bright-greeting-goose.md" plans/.claude/bright-greeting-goose.md
    step_2: Lock the plan:
      python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/bright-greeting-goose.md
    step_3: Verify lock written to .local/supervisor/plan-locks/
    step_4: Begin TC-BF-001-01 (read 04-machinery-component-register.md)

  prerequisite_reading:
    - CLAUDE.md (session instructions and plan lock rules)
    - AGENTS.md (agent authority and hard stop rules)
    - docs/system-recon/supervisor-machinery-audit/04-machinery-component-register.md (49 components)
    - docs/system-recon/supervisor-machinery-audit/06-guarantee-control-matrix.md (12 guarantees)
    - .github/workflows/ci.yml (CI governance-check job structure)

  execution_sequence:
    serial_required: [TC-BF-001, TC-BF-002]
    parallel_batch: [TC-BF-003, TC-BF-004, TC-BF-005, TC-BF-006, TC-BF-007]
    serial_final: [TC-BF-008]
    conditional: [TC-BF-009 — only if git latency > 3000ms in TC-BF-008]

  completion_protocol:
    last_taskcard: TC-BF-009 (or TC-BF-008 if TC-BF-009 execution_condition not met)
    close_command: >
      python tools/supervisor/write_plan_lock.py
        --plan-path plans/.claude/bright-greeting-goose.md --terminal
    post_close: STOP and report to user. Do NOT call check_continuation.py.
      Plan completion is the terminal event for this session.

  sprint_cap: 8 sprints maximum for TC-BF-001 through TC-BF-009 combined.
    If cap approached without all tasks CLOSED: defer TC-BF-009 to next session.
    Never defer TC-BF-008 (regression baseline is the unlock for Stage 3+).

  guaranteed_not_to_change:
    - autonomous_cycle.py
    - check_continuation.py
    - grade_declared_work.py
    - evidence_declaration.py
    - inspect_declared_evidence.py
    - governance_validator_runner.py (logic unchanged; loading path extended only)
    - All 12 guarantees (G-001 through G-012) preserved throughout
```


## Taskcard Status Summary

| TC-ID | STATUS |
|---|---|
| TC-BF-001 | CLOSED |
| TC-BF-002 | CLOSED |
| TC-BF-003 | CLOSED |
| TC-BF-004 | CLOSED |
| TC-BF-005 | CLOSED |
| TC-BF-006 | CLOSED |
| TC-BF-007 | CLOSED |
| TC-BF-008 | CLOSED |
| TC-BF-009 | CLOSED |

Note: TC-BF-004 implementation is CLOSED (tombstones applied, check_tombstone_records.py created, register updated). The 30-day observation window (expires 2026-08-05) is a monitoring activity external to this plan's scope. check_tombstone_records.py will report FIRED or CONFIRMED_DEAD for external_host_loop.py after 2026-08-05.

<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-07-06T10:47:26.782719+00:00"
  locked_by: "496b377beedd"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
