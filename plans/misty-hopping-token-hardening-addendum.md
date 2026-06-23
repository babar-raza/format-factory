# Hardening Addendum: misty-hopping-token (FF-FORENSIC-AUDIT-20260623)

**Parent Plan:** `C:\Users\prora\.claude\plans\misty-hopping-token.md`
**Parent Status:** TERMINAL_CLOSED (2026-06-23)
**Addendum Created:** 2026-06-23
**Mission ID:** FF-FORENSIC-AUDIT-20260623-HARDEN
**Purpose:** Incorporate unresolved audit findings from the evidence-based sprint achievement review into governed taskcards with evidence contracts

---

## Addendum Binding

```yaml
addendum_binding:
  parent_mission_id: FF-FORENSIC-AUDIT-20260623
  addendum_mission_id: FF-FORENSIC-AUDIT-20260623-HARDEN
  repository: format-factory
  branch: main
  parent_plan_status: TERMINAL_CLOSED
  addendum_type: post_audit_hardening
  mandatory_outcomes:
    - All sprint artifacts committed to git (H1)
    - Remaining 40 null python_file entries populated or explicitly deferred (H3)
    - 2 non-canonical python_file entries corrected (H4)
    - V54/V55 promoted from WARN to conditional-blocking (H5)
    - FODT .NET architecture_only markers removed from converted classes (H6)
    - End-to-end consumer wired for audit tools (H7)
    - Phase J skill audit completed (H8)
  explicit_non_goals:
    - Do NOT re-execute completed Phase A-F work
    - Do NOT modify parent plan file (TERMINAL_CLOSED)
    - Do NOT restructure src/ product code (backfill tool required first)
```

---

## Evidence-Based Review Findings (Source of Taskcards)

The following findings were identified in the post-sprint evidence review.
Each finding is classified and converted to a governed taskcard below.

### FINDING-H01: Nothing committed
**Classification:** CRITICAL_PROCESS_GAP
**Detail:** 858 files changed, 41 untracked — all exist only in working tree.
Sprint work has zero git durability. A `git checkout .` destroys everything.

### FINDING-H02: Registry rollout was partial (9/70 corrected, not "full rollout")
**Classification:** OVERCLAIM_CORRECTION
**Detail:** Phase M claimed "full rollout" but only corrected 9 entries that had
Compat/ python_file pointers. 40 entries have null python_file. 2 entries point to
non-canonical paths (dif:cell → dif_parser.py, xcf:image → image_document.py).
The remaining 28/70 correctly point to spec/ paths.

### FINDING-H03: Phases G/H were verifications, not implementations
**Classification:** SCOPE_CORRECTION (not a gap — work was correctly done, scope was smaller than planned)
**Detail:** Phase G found all 9 FODT .NET Spec classes already existed (TC-QHARD-051).
Phase H found covered_table_cell.py already existed (commit 4f66d304).
Both phases correctly verified pre-existing work rather than creating new code.
No taskcard needed — this is a documentation correction only.

### FINDING-H04: FODT .NET Spec classes retain architecture_only markers
**Classification:** INCOMPLETE_IMPLEMENTATION
**Detail:** All 9 classes in `src/net/fodt/Spec/` still carry `// architecture_only`
comment markers despite being claimed as "converted to real model class" in TC-QHARD-051.
Classes have real properties and SpecQName constants but the stale marker contradicts their status.

### FINDING-H05: V54/V55 are WARN-only, not blocking
**Classification:** DEFERRED_BY_DESIGN (per plan rollback spec)
**Detail:** V54 (product touching machinery) and V55 (machinery touching product) were
intentionally created as WARN-only to avoid false positives. Per the plan's Phase K
rollback specification, they should be promoted to conditional-blocking after 3 clean
sprints with no false positives.

### FINDING-H06: No end-to-end consumer for audit tools
**Classification:** PARTIALLY_COMPLETED
**Detail:** 6 audit tools were created (audit_qname_coverage.py, audit_sal_to_qname.py,
audit_gap_ledger_sal_refs.py, audit_parity_compliance.py, gap_ledger_to_work_items.py,
audit_qname_vs_src.py) but none is wired into the autonomous cycle or governance pipeline.
They produce reports but nothing consumes those reports automatically.

### FINDING-H07: Phase J (skill audit) and Phase K (lane enforcement) have no evidence
**Classification:** NOT_ATTEMPTED
**Detail:** Phase J required auditing /qname-backfill skill quality. Phase K required
full lane separation with per-lane evidence directories. Neither was executed.
V54/V55/V56 were created (partial K work) but J and K are incomplete.

### FINDING-H08: Plan lock inconsistency
**Classification:** PROCESS_ANOMALY
**Detail:** After writing TERMINAL_CLOSED for misty-hopping-token, active-plan-lock.json
showed a DIFFERENT plan (capability-fact-to-feature-production-plan.md) IN_PROGRESS.
The session-keyed lock showed tender-finding-wave.md IN_PROGRESS. Multiple concurrent
plan locks exist. This is not a gap created by this sprint but should be cleaned up.

---

## Taskcards

### TASKCARD H1 — Git Commit All Sprint Artifacts

```yaml
taskcard:
  task_id: H1-COMMIT
  mission_id: FF-FORENSIC-AUDIT-20260623-HARDEN
  finding_ref: FINDING-H01
  priority: CRITICAL
  status: TODO
  objective: Commit all forensic audit sprint artifacts to git
  scope: |
    Stage and commit all sprint outputs in logical groups:
    1. QName registry corrections (5 YAML files)
    2. New audit tools (6 Python files)
    3. Migration maps (20 format dirs + summary)
    4. Audit reports (5 JSON files)
    5. Governance extensions (validators_ext.py, runner update, tests)
    6. Evidence declarations (2 YAML files)
  allowed_paths:
    - shared/qname-registry/*.yaml
    - tools/audit_*.py
    - tools/backfill/
    - migration-maps/
    - reports/qname-coverage-*.json
    - reports/sal-qname-gap-*.json
    - reports/parity-gap-*.json
    - reports/capability-layer/gap-sal-traceability-*.json
    - reports/capability-layer/gap-work-items-test.json
    - tools/supervisor/governance_validators_ext.py
    - tools/supervisor/governance_validator_runner.py
    - tools/supervisor/gap_ledger_to_work_items.py
    - tests/supervisor/test_governance_validators.py
    - .local/evidences/FF-FORENSIC-AUDIT-20260623-*/
  forbidden_paths:
    - src/ (no product source changes in this commit)
  implementation_steps:
    - git add shared/qname-registry/{csv,ndjson,xcf,zst,fods}.yaml
    - git add tools/audit_*.py tools/backfill/ tools/supervisor/governance_validators_ext.py
    - git add tools/supervisor/governance_validator_runner.py tools/supervisor/gap_ledger_to_work_items.py
    - git add migration-maps/ reports/qname-coverage-20260623.json reports/sal-qname-gap-20260623.json
    - git add reports/parity-gap-20260623.json reports/capability-layer/gap-sal-traceability-20260623.json
    - git add reports/capability-layer/gap-work-items-test.json
    - git add tests/supervisor/test_governance_validators.py
    - Commit with message referencing FF-FORENSIC-AUDIT-20260623
  focused_verification:
    - git status shows clean for all listed paths
    - git log --oneline -1 shows the commit
  closeout_rules:
    - CLOSED when commit SHA is recorded and git status confirms staged files are committed
```

### TASKCARD H2 — Commit Supervisor/Report State Changes

```yaml
taskcard:
  task_id: H2-COMMIT-STATE
  mission_id: FF-FORENSIC-AUDIT-20260623-HARDEN
  finding_ref: FINDING-H01
  priority: HIGH
  status: TODO
  objective: Commit supervisor state and report changes from prior sprints
  scope: |
    The 858-file diff includes many supervisor state files and reports that accumulated
    across multiple sessions. These should be committed as a separate "state refresh" commit
    to keep the audit artifacts commit (H1) clean and reviewable.
  implementation_steps:
    - Review git diff --name-only for reports/supervisor/ changes
    - Review git diff --name-only for .supervisor/ changes
    - Stage and commit as "chore(reports): supervisor state refresh after forensic audit"
  closeout_rules:
    - CLOSED when state refresh commit is created
```

### TASKCARD H3 — Populate Remaining 40 Null python_file Entries

```yaml
taskcard:
  task_id: H3-REGISTRY-POPULATE
  mission_id: FF-FORENSIC-AUDIT-20260623-HARDEN
  finding_ref: FINDING-H02
  priority: HIGH
  status: TODO
  objective: For each of the 40 qname entries with python_file=null, either set the
    correct spec/ path (if file exists) or explicitly document as DEFERRED with reason
  scope: |
    40 entries across 18 format registries have python_file: null.
    For each:
    1. Check if a spec/ file already exists on disk (may have been created but not registered)
    2. If yes: update python_file to point to it
    3. If no file exists: leave python_file null but add comment "# no spec class yet"
    Run tools/audit_qname_coverage.py after to verify improvement.
  allowed_paths:
    - shared/qname-registry/*.yaml (edit)
    - tools/audit_qname_coverage.py (run, read-only)
  forbidden_paths:
    - src/ (do NOT create new spec files — that's qname-backfill skill work)
  focused_verification:
    - audit_qname_coverage.py shows updated coverage numbers
    - Every null python_file either points to an existing file or has explicit deferral comment
  closeout_rules:
    - CLOSED when all 40 entries audited and either populated or explicitly deferred
```

### TASKCARD H4 — Fix 2 Non-Canonical python_file Paths

```yaml
taskcard:
  task_id: H4-REGISTRY-FIX
  mission_id: FF-FORENSIC-AUDIT-20260623-HARDEN
  finding_ref: FINDING-H02
  priority: MEDIUM
  status: TODO
  objective: Correct dif:cell and xcf:image python_file to point to canonical spec/ paths
  scope: |
    - dif:cell currently points to src/python/dif/dif_parser.py (the parser, not a spec class)
    - xcf:image currently points to src/python/xcf/image_document.py (module, not spec class)
    For each:
    1. Check if a canonical spec/ class exists for these entries
    2. If yes: update python_file
    3. If no: check if the current path has spec_qname assignment; if so, note as
       "non-canonical but functional" with a comment
  allowed_paths:
    - shared/qname-registry/dif.yaml
    - shared/qname-registry/xcf.yaml
    - src/python/dif/ (read-only)
    - src/python/xcf/ (read-only)
  closeout_rules:
    - CLOSED when both entries are corrected or explicitly documented as non-canonical
```

### TASKCARD H5 — V54/V55 Promotion Tracker

```yaml
taskcard:
  task_id: H5-V54V55-PROMOTE
  mission_id: FF-FORENSIC-AUDIT-20260623-HARDEN
  finding_ref: FINDING-H05
  priority: LOW
  status: TODO
  objective: Track V54/V55 for promotion from WARN to conditional-blocking
  scope: |
    Per the parent plan's Phase K rollback specification:
    - V54/V55 should be promoted to conditional-blocking after 3 clean sprints
    - A "clean sprint" = no false GOV_BLOCK from these validators
    - Track sprint count in this taskcard
    Sprint tracking:
      Sprint 1: ___ (date, false positives: Y/N)
      Sprint 2: ___ (date, false positives: Y/N)
      Sprint 3: ___ (date, false positives: Y/N)
    After 3 clean sprints: promote severity from WARN to conditional-blocking
  implementation_steps:
    - After each autonomous sprint, check reports for V54/V55 false positives
    - Update this taskcard with sprint date and result
    - After 3 clean sprints: edit governance_validators_ext.py to change severity
  closeout_rules:
    - CLOSED when 3 clean sprints recorded AND severity promoted
    - OR CLOSED with DEFERRED if false positives found (need exception mechanism)
```

### TASKCARD H6 — Remove architecture_only Markers from FODT .NET Spec Classes

```yaml
taskcard:
  task_id: H6-FODT-MARKERS
  mission_id: FF-FORENSIC-AUDIT-20260623-HARDEN
  finding_ref: FINDING-H04
  priority: MEDIUM
  status: TODO
  objective: Remove stale "architecture_only" comment markers from 9 FODT .NET Spec classes
  scope: |
    Files in src/net/fodt/Spec/:
    - Office/Body.cs, Table/Table.cs, Table/TableCell.cs, Table/TableRow.cs
    - Text/Heading.cs, Text/List.cs, Text/ListItem.cs, Text/Paragraph.cs, Text/Span.cs
    Each has a comment like "// architecture_only" or "// GENERATED - architecture_only".
    These classes have real SpecQName constants and init-only properties — they are NOT
    architecture_only anymore. Remove the stale markers.
  allowed_paths:
    - src/net/fodt/Spec/**/*.cs
  forbidden_paths:
    - Any behavioral changes to these classes
  focused_verification:
    - grep -r "architecture_only" src/net/fodt/Spec/ returns 0 results
    - dotnet build src/net/fodt/ still succeeds (if build available)
  closeout_rules:
    - CLOSED when all 9 files have markers removed and no build regression
```

### TASKCARD H7 — Wire Audit Tools to Governance Pipeline

```yaml
taskcard:
  task_id: H7-WIRE-AUDIT-TOOLS
  mission_id: FF-FORENSIC-AUDIT-20260623-HARDEN
  finding_ref: FINDING-H06
  priority: HIGH
  status: TODO
  objective: Wire at least one audit tool into the autonomous cycle as a governance check
  scope: |
    The most impactful tool to wire is audit_qname_coverage.py:
    - Run it as a pre-sprint check in autonomous_cycle.py (similar to refresh_check.py)
    - If coverage drops below baseline, emit WARNING (not blocking initially)
    - Store baseline in reports/qname-coverage-baseline.json
    Alternative: wire into governance_validator_runner.py as V57
  allowed_paths:
    - tools/supervisor/autonomous_cycle.py (add pre-sprint hook)
    - tools/audit_qname_coverage.py (read-only, invoke)
    - reports/qname-coverage-baseline.json (create)
  implementation_steps:
    - Run audit_qname_coverage.py to get current baseline numbers
    - Save as reports/qname-coverage-baseline.json
    - Add Step 0a-qname block in autonomous_cycle.py (after Step 0a-refresh)
    - Non-blocking WARNING if coverage decreased
    - Test: run autonomous_cycle.py dry-run to verify hook fires
  focused_verification:
    - autonomous_cycle.py contains qname coverage check
    - Baseline JSON exists with per-format data
    - Non-blocking (does not set hard_stops)
  closeout_rules:
    - CLOSED when hook is wired AND baseline is stored AND test confirms it fires
```

### TASKCARD H8 — Phase J Skill Audit (/qname-backfill)

```yaml
taskcard:
  task_id: H8-SKILL-AUDIT
  mission_id: FF-FORENSIC-AUDIT-20260623-HARDEN
  finding_ref: FINDING-H07
  priority: MEDIUM
  status: TODO
  objective: Audit /qname-backfill skill quality using /validate-skill-transcript
  scope: |
    The parent plan's Phase J required auditing the /qname-backfill skill.
    Per FINDING FC-10 in the parent plan, the skill exists and appears production-quality.
    This taskcard validates that claim:
    1. Read .claude/commands/qname-backfill.md
    2. Run /validate-skill-transcript against it (or manual quality check)
    3. Verify: allowed/forbidden paths are correct, evidence requirements exist,
       V53 integration is referenced and V53 exists
    4. If quality is PASS: mark skill as production-ready
    5. If quality is FAIL: document specific gaps
  allowed_paths:
    - .claude/commands/qname-backfill.md (read-only)
    - .supervisor/skill-registry.yaml (read, possibly update status)
    - tools/supervisor/governance_validators.py (verify V53 exists)
  closeout_rules:
    - CLOSED when skill quality verdict is recorded (PASS or FAIL with gaps listed)
```

### TASKCARD H9 — Clean Stale Plan Locks

```yaml
taskcard:
  task_id: H9-CLEAN-LOCKS
  mission_id: FF-FORENSIC-AUDIT-20260623-HARDEN
  finding_ref: FINDING-H08
  priority: LOW
  status: TODO
  objective: Clean up stale/conflicting plan lock files
  scope: |
    Multiple plan lock files exist with inconsistent states:
    - active-plan-lock.json (shows different plan than expected)
    - Session-keyed locks in .local/supervisor/plan-locks/ may be stale
    Audit all lock files, mark stale ones as COMPLETE, ensure only
    currently-active plans have IN_PROGRESS locks.
  allowed_paths:
    - .local/supervisor/plan-locks/*.json
    - .local/supervisor/active-plan-lock.json
  implementation_steps:
    - List all .local/supervisor/plan-locks/*.json
    - For each: check if plan is actually in progress or completed
    - Mark stale locks as COMPLETE
    - Verify active-plan-lock.json reflects actual state
  closeout_rules:
    - CLOSED when no stale IN_PROGRESS locks remain
```

---

## Execution Order and Dependencies

```
H1-COMMIT ──────────────────── (IMMEDIATE, no dependencies)
H2-COMMIT-STATE ────────────── (IMMEDIATE, parallel with H1)
H4-REGISTRY-FIX ────────────── (after H1, small scope)
H3-REGISTRY-POPULATE ───────── (after H4, larger scope, may create spec files)
H6-FODT-MARKERS ────────────── (after H1, independent)
H7-WIRE-AUDIT-TOOLS ───────── (after H1, depends on committed tools)
H8-SKILL-AUDIT ─────────────── (independent, read-only)
H9-CLEAN-LOCKS ─────────────── (independent, housekeeping)
H5-V54V55-PROMOTE ──────────── (LONG-RUNNING, tracked across 3+ sprints)
```

---

## Verification Matrix

| Taskcard | Evidence Required | Negative Control |
|----------|------------------|------------------|
| H1 | git log shows commit SHA | git diff shared/qname-registry/ returns empty |
| H2 | git log shows state refresh commit | reports/supervisor/ changes committed |
| H3 | audit_qname_coverage.py output shows 0 unaudited nulls | Temporarily null a known entry, verify tool catches it |
| H4 | grep "Compat\|parser\|image_document" shared/qname-registry/*.yaml → 0 hits | N/A |
| H5 | 3 sprint dates recorded, V54/V55 severity changed | false_positive_count == 0 for all 3 |
| H6 | grep "architecture_only" src/net/fodt/Spec/ → 0 hits | .NET build passes |
| H7 | autonomous_cycle.py contains qname coverage hook | Hook fires on dry-run |
| H8 | Skill quality verdict recorded (PASS/FAIL) | If PASS: skill runs without error on test format |
| H9 | No stale IN_PROGRESS locks in plan-locks/ | check_continuation.py does not return ACTIVE_PLAN_INCOMPLETE |

---

## Anti-Overclaim Rules

1. **H1/H2 are process tasks, not product achievements.** Committing pre-existing work does not create new value — it preserves existing value.
2. **H3 "populating" a registry entry that already has a file on disk is documentation, not implementation.** Do not claim spec class creation when updating a YAML pointer.
3. **H5 is a tracking taskcard.** It produces no code until 3 sprints are tracked. Do not claim V54/V55 are "blocking" until severity is actually changed in code.
4. **H6 is a comment removal.** Do not claim "FODT .NET classes converted to production" — they were already converted in TC-QHARD-051. This taskcard only removes stale markers.
5. **H7 must produce a RUNNING hook, not just a code change.** Evidence must show the hook fired during a real or simulated autonomous cycle step.

---

## Current State Snapshot (2026-06-23)

```
QName Registry:
  Total entries: 70
  python_file -> spec/: 28 (40.0%) ← CORRECT
  python_file -> Compat/: 0 (0.0%) ← ALL CORRECTED (was 9)
  python_file -> non-canonical: 2 (2.9%) ← NEEDS H4
  python_file -> null: 40 (57.1%) ← NEEDS H3 (audit + populate or defer)

Audit Tools Created: 6 (uncommitted)
Migration Maps: 20 formats + summary (uncommitted)
Governance Validators: V54, V55, V56 added (uncommitted)
Tests Added: 10 V54/V55 tests (uncommitted)
Evidence Declarations: 2 (uncommitted)

Git State: 858 modified + 41 untracked = 899 uncommitted changes
```
