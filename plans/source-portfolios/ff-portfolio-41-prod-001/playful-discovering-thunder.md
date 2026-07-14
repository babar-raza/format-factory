# Root Folder Reconnaissance — Production-Grade Redesign
# Plan: playful-discovering-thunder
# Authority: this file is the SOLE execution authority for mission ROOT-RECON-001
# Supporting artifacts: execution-only, non-authoritative

---

## PREFLIGHT RECORD

```
repository_root: C:\Users\prora\OneDrive\Documents\GitHub\format-factory
branch: main
head: af879e55 (as of plan authoring 2026-07-10)
active_plan_path: plans/.claude/playful-discovering-thunder.md
plan_title: Root Folder Reconnaissance — Production-Grade Redesign
plan_format: markdown with inline YAML blocks
authority_source: plan-mode system message
plan_size_lines: ~600 (current), ~1200 (after taskcardization)
major_sections: 9
existing_taskcard_sections: 1 (Implementation Plan — high-level only)
existing_taskcard_format: flat list (no hierarchy, no machine state)
existing_gates: none defined
existing_state_vocabulary: none
existing_validation_model: bash snippets only
existing_evidence_model: none
duplicate_plan_risk: LOW (one plan file confirmed, no competing authorities)
```

---

## CORRECTIONS FROM CODE AUDIT (applied before taskcardization)

### Correction 1 — C3 design was infeasible

The C3 function `_derive_format_coverage()` as previously written relied on
`f.get("active")` and `f.get("languages", [])` fields in `registry/format-registry.yaml`.
These fields do not exist. The format registry contains only `format_id`, scoring, and
gate fields — no language assignment and no active boolean.

**Corrected C3 approach:**
Derive format coverage by scanning actual product directories and checking test parity:
- For every `src/python/{fmt}/` that exists → check `tests/python/{fmt}/` exists.
- For every `src/net/{fmt}/` that exists → check `tests/net/{fmt}/` exists.
- Report missing test directories as FORMAT_COVERAGE_GAP (WARN, non-blocking).
- This is the useful coverage contract: every product directory must have a test directory.
- No external file dependency. No format-registry.yaml field dependency.

### Correction 2 — TC-RR-001 producer investigation was wrong

The plan stated "Read tools/state/state_snapshot.py and tools/state/state_linter.py".
The directory `tools/state/` does NOT exist in the repository.

**Corrected TC-RR-001 scope:**
- Search the entire codebase (tools/, tests/, .supervisor/) for any reference to `state/`
  as a write target.
- Read `state/current-state.json` and `state/current-state.md` to understand their content.
- Determine whether any currently-executable code writes to `state/`.
- If no active producer is found: the files are legacy orphans. Safe to delete.
- If an active producer is found: redirect it to `.supervisor/state/` before deleting.

### Correction 3 — test_pass_on_real_repo must be updated AFTER state/ is resolved

`tests/supervisor/test_validate_root_structure.py` line 121 explicitly tolerates WARN
for the state/ resurrection:
```python
assert result["result"] in ("PASS", "WARN")
```
This test must be updated to `assert result["result"] == "PASS"` AFTER state/ is resolved
(TC-RR-002) and AFTER resurrection severity is changed to FAIL (TC-RR-003). Order matters.

---

## WHAT THE PREVIOUS PLAN GOT WRONG

The first-pass plan treated this as an inventory-and-documentation exercise. It proposed adding
more static files (freshness manifests, coverage contracts, README schemas) and extending an
already-fragile validator with more checks. That approach would not produce durable results.
It would produce a brief period of apparent compliance followed by the same drift it set out
to fix, because it did not address why the system drifts.

---

## ACTUAL STATE OF THE SYSTEM (Evidence-Based)

### What the deep audit found that the surface audit missed:

**V91 validates disk against the catalog. It never validates the catalog itself.**
- Every check V91 performs assumes the registry entry is correct.
- A deliberately or accidentally wrong registry entry passes V91 cleanly.
- Producer/consumer lists in the registry are never validated against actual tool paths.
- `format_scope_paths` entries are template strings that V91 never resolves.
- `tracked_files` counts are snapshots frozen at time of authoring.
- `readme_exists: true` is a flag set manually and never re-verified.

**V91 only runs during sprint closeout. Not at commit time.**
- `.pre-commit-config.yaml` does not include V91. Confirmed by code read.
- Five existing hooks: scope-guard (WARN mode), source-structure-baseline-check,
  validate-source-architecture, capability-registry-drift-check, project-status-structure-check.
  None check for unregistered root directories.
- Problems accumulate between sprints with no mechanical gate.

**The `state/` folder is a diagnostic specimen, not an isolated bug.**
- Registry marks `state/` as `retention: DELETED` since TC-ROOT-002.
- Confirmed on disk: two files — `state/current-state.json` and `state/current-state.md`.
- `tools/state/` does NOT exist — the presumed producer directory is absent.
- V91 detects the contradiction but only WARNs (non-blocking).
- The test for V91 at line 118 explicitly comments "Allow WARN-severity items (e.g.
  resurrected_deleted for state/ dir)" — documenting that the team knows and tolerates it.
- This pattern — deletion planned, producer not fixed, WARN issued, WARN accepted, explicitly
  tolerated in tests — is the reproducible failure mode.

**README existence passes V91. README content is never inspected.**
- Confirmed by reading governance_validators_root_struct.py (170 lines, full source).
- Check 2 (README presence) only verifies `readme_path.exists()`.
- Assessed tests/_readme.md, tools/_readme.md, src/README.md directly.
- All pass V91. None tell an agent where to put a new file.
- `src/README.md` lists format names but provides zero structural guidance.

**Format coverage validation requires an external file that does not exist.**
- V91 Check 4 requires `reports/repository-structure/format-folder-coverage.yaml`.
- Confirmed: that file does not exist on disk.
- The check silently skips with no warning when the file is absent.
- Format coverage validation is effectively not running. At all.

**The catalog is 100% manually authored with no regeneration mechanism.**
- Confirmed: no tool writes to `registry/repository-root-folders.yaml`.
- All 51 entries are human-curated. Field values like `tracked_files: 509` are snapshots.
- `readme_exists: true` flag appears on some entries (tests/) but not others (src/).
- No integrity check exists for catalog accuracy.

---

## SEPARATED ANALYSIS

### Symptoms (visible)
1. `state/` folder exists but is marked DELETED → V91 WARN (not FAIL), test tolerates it
2. READMEs exist but don't answer agent navigation questions
3. Format coverage validation silently skipped (external file does not exist)
4. `readme_exists` flags inconsistently populated across registry entries
5. Tracked file counts in registry are stale snapshots
6. No recon report, no terminal closeout record

### Root Causes
1. **Producer-first ordering never enforced.** Directories are marked for deletion before
   their producers are fixed. V91 then WARNs instead of FAILing, and the test explicitly
   tolerates the WARN. Result: violations persist indefinitely.
2. **Catalog self-referential trust.** V91 trusts registry entries without validating them.
   A wrong entry (wrong producers, template paths, stale counts) passes V91 cleanly.
3. **Wrong enforcement cadence.** Sprint-closeout governance catches drift only after it
   accumulates. Pre-commit hooks exist for source quality but not for directory registration.
4. **WARN structurally equivalent to silence.** Non-blocking WARNs for policy violations
   that are explicitly tolerated in tests are no enforcement at all.
5. **README quality check is binary.** Existence (1 byte or 10,000 bytes) produces the same
   validator result.

### Structural Weaknesses
1. **Self-referential catalog trust.** Registry is the validator's truth source but has no
   validator of its own.
2. **Static declarations for dynamic state.** Producer lists, file counts, README flags are
   declared once and drift silently.
3. **No README feedback loop.** System has no way to detect when READMEs become misleading
   as directory contents evolve.
4. **Taskcards without enforcement loops.** TC-ROOT-002 planned deletion of state/; state/
   still exists. No mechanism forced execution.

---

## WHAT TO PRESERVE

- `registry/repository-root-folders.yaml` — 51-entry catalog. Keep and repair.
- V91 core — Check 1 (unregistered directory detection). Correct design. Extend in-place.
- `registry/format-registry.yaml` — authoritative format ID list. Read-only.
- `tools/supervisor/path_resolver.py` — canonical path resolution. Reuse.
- All existing README files — preserve content. Augment only.
- `tests/supervisor/test_validate_root_structure.py` — existing 7 tests. Extend, don't replace.
- Sprint enforcement model (validator → runner → block) — architecture is correct.

## WHAT MUST BE REDESIGNED

1. V91 severity policy: resurrections must FAIL (not WARN) to be enforceable.
2. V91 format coverage check: must derive from actual directory scan (not a missing file).
3. The deletion workflow: producers must be identified and resolved before marking DELETED.
4. README quality check: must verify a minimal content floor (3 markers), not existence.
5. Enforcement cadence: pre-commit hook must catch unregistered directories at commit time.

---

## PRODUCTION SOLUTION DESIGN

### Design Principle: Fix the enforcement contract, not the catalog content.

Adding more static files that need to be maintained will reproduce the same drift. The durable
fix is making the enforcement contract stronger so violations cannot accumulate silently.

### Change Set (finalized after code audit corrections)

**C1 — Fix deletion enforcement severity: WARN → FAIL**
In `tools/supervisor/governance_validators_root_struct.py`, line 109:
Change `"severity": "WARN"` for `resurrected_deleted` items to `"severity": "FAIL"`.
Change `has_fail = True` for this case.
Update `test_warn_resurrected_deleted` to `test_fail_resurrected_deleted` with
`assert result["result"] == "FAIL"` and `assert result["blocks_sprint"] is True`.
Update `test_pass_on_real_repo` to `assert result["result"] == "PASS"` after state/ resolved.

Tradeoff: next sprint after this change will FAIL if any other DELETED folders exist on disk
beyond state/. Mitigation: audit all DELETED entries before applying (TC-RR-001b).

**C2 — Resolve state/ with producer-first order**
Precondition: TC-RR-001 investigation complete.
Steps (after investigation):
- If no active producer found: `git rm -r state/` (safe — orphan files).
- If active producer found: redirect writes to `.supervisor/state/`, then delete.
- Update registry entry from `retention: DELETED` to confirm deletion applied.
After deletion: C1 will no longer trigger on state/.

**C3 (corrected) — In-memory format coverage: source-to-test parity check**
In `tools/supervisor/governance_validators_root_struct.py`, add function:

```python
def _check_source_test_parity(repo_root: Path) -> list[dict]:
    """
    For every src/python/{fmt}/ that exists, verify tests/python/{fmt}/ exists.
    For every src/net/{fmt}/ that exists, verify tests/net/{fmt}/ exists.
    No external file dependency. No format-registry.yaml language field required.
    Returns list of FORMAT_COVERAGE_GAP findings (WARN severity, non-blocking).
    """
    findings = []
    skip_prefix = ("_", ".")

    src_python = repo_root / "src" / "python"
    tests_python = repo_root / "tests" / "python"
    if src_python.is_dir():
        for fmt_dir in sorted(src_python.iterdir()):
            if not fmt_dir.is_dir():
                continue
            if any(fmt_dir.name.startswith(p) for p in skip_prefix):
                continue
            expected_test = tests_python / fmt_dir.name
            if not expected_test.is_dir():
                findings.append({
                    "check": "format_coverage_gap",
                    "path": f"tests/python/{fmt_dir.name}",
                    "severity": "WARN",
                    "category": "FORMAT_COVERAGE_GAP",
                    "message": f"src/python/{fmt_dir.name} exists but tests/python/{fmt_dir.name} is missing",
                })

    src_net = repo_root / "src" / "net"
    tests_net = repo_root / "tests" / "net"
    if src_net.is_dir():
        for fmt_dir in sorted(src_net.iterdir()):
            if not fmt_dir.is_dir():
                continue
            if any(fmt_dir.name.startswith(p) for p in skip_prefix):
                continue
            expected_test = tests_net / fmt_dir.name
            if not expected_test.is_dir():
                findings.append({
                    "check": "format_coverage_gap",
                    "path": f"tests/net/{fmt_dir.name}",
                    "severity": "WARN",
                    "category": "FORMAT_COVERAGE_GAP",
                    "message": f"src/net/{fmt_dir.name} exists but tests/net/{fmt_dir.name} is missing",
                })

    return findings
```

Replace V91 Check 4 with a call to `_check_source_test_parity()`.
This eliminates the silent-skip-if-file-absent failure mode entirely.

**C4 — README content floor check in V91**
Add function (WARN severity, non-blocking initially):

```python
def _check_readme_content_floor(readme_path: Path) -> list[str]:
    """
    Returns list of missing structural markers. Empty = passes floor.
    Only catches absolute floor failures (stubs, empty files).
    """
    try:
        size = readme_path.stat().st_size
    except OSError:
        return ["file_unreadable"]
    if size < 200:
        return ["too_short"]
    try:
        content = readme_path.read_text(encoding="utf-8", errors="replace").lower()
    except OSError:
        return ["file_unreadable"]
    missing = []
    if not any(kw in content for kw in
               ["purpose", "what this", "this folder", "this directory", "# "]):
        missing.append("no_purpose_statement")
    if not any(kw in content for kw in
               ["producer", "created by", "written by", "generated by",
                "who creates", "origin", "source:"]):
        missing.append("no_producer_declaration")
    if not any(kw in content for kw in
               ["agent", "validation", "command", "run ", "python ", "pytest"]):
        missing.append("no_actionable_guidance")
    return missing
```

Severity: WARN (non-blocking). After README repair is complete, severity can be elevated.

Known limit: keyword matching is coarse. Catches stubs and empty files. Does not catch
misleading or outdated content. This is the intended scope.

**C5 — Pre-commit unregistered-directory check**
New file: `tools/supervisor/check_new_root_dirs.py`

```python
#!/usr/bin/env python3
"""
Fast pre-commit check: detect new unregistered top-level directories.
Runs in < 2 seconds. Reads git staging area, not full disk scan.
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    # Fail open: if yaml unavailable, do not block commit
    sys.exit(0)

repo_root = Path(__file__).resolve().parents[2]
registry_path = repo_root / "registry" / "repository-root-folders.yaml"

if not registry_path.exists():
    # No registry yet — cannot validate
    sys.exit(0)

data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
registered = {
    e.get("folder_path", "").strip("/")
    for e in data.get("folders", [])
}

result = subprocess.run(
    ["git", "diff", "--cached", "--name-only"],
    capture_output=True, text=True, cwd=str(repo_root)
)
staged_paths = result.stdout.splitlines()

new_unregistered: set[str] = set()
for path_str in staged_paths:
    parts = Path(path_str).parts
    if not parts:
        continue
    top = parts[0]
    if top in registered:
        continue
    if top.startswith("."):
        # dot-dirs that aren't tracked (e.g. .local) — skip
        full = repo_root / top
        if full.is_dir() and top not in registered:
            new_unregistered.add(top)
        continue
    full = repo_root / top
    if full.is_dir():
        new_unregistered.add(top)

if new_unregistered:
    print(
        f"ERROR: Unregistered top-level directories staged for commit: "
        f"{sorted(new_unregistered)}"
    )
    print(
        "Add entries to registry/repository-root-folders.yaml "
        "before committing."
    )
    sys.exit(1)
```

Wire in `.pre-commit-config.yaml`:
```yaml
      - id: check-root-dirs
        name: Check for unregistered root directories
        entry: python tools/supervisor/check_new_root_dirs.py
        language: system
        pass_filenames: false
        always_run: false
        stages: [pre-commit]
```

**C6 — Registry producer path validation (lightweight, WARN-only)**
Add to V91: for each RETAIN entry, check whether any listed producer is a resolvable path
rather than a human-readable string:

```python
def _check_registry_producer_integrity(entry: dict, repo_root: Path) -> str | None:
    """
    Returns a warning message if producers list has no resolvable tool path.
    A producer is 'resolvable' if it names a file that exists in the repo.
    """
    producers = entry.get("producers", [])
    if not producers:
        return None
    non_verifiable = {"developers", "humans", "agents", "users", "ci",
                      "source generators", "test generators", "acquisition workflow",
                      "supervisor", "oracle", "spec-parity tools"}
    resolvable = [
        p for p in producers
        if p not in non_verifiable and (repo_root / p).exists()
    ]
    all_non_verifiable = all(p.lower() in non_verifiable for p in producers)
    if all_non_verifiable:
        return (
            f"Folder '{entry['folder_path']}' lists only non-verifiable producers "
            f"{producers}. Consider adding at least one tool path."
        )
    return None
```

WARN-only. Surfaces the producer-list-as-fiction problem without blocking sprints.

**C7 — Repair 6 priority READMEs**
Add `## Agent Navigation` section only. Preserve all existing content.
Priority order (evidence-based):

1. `src/README.md` — add where to create a new format package
2. `tests/_readme.md` — add where to add format tests, what to run
3. `tools/_readme.md` — add subdirectory guide (supervisor/, governance/, validators/)
4. `registry/README.md` — add how to register a format, how to register a folder
5. `plans/README.md` — add where per-chat plans go vs strategic plans
6. `reports/_readme.md` — add what goes in supervisor/ vs .local/evidences/

**C8 — Formal recon report**
Create `reports/repository-structure/root-folder-recon-report.md`.
This is a one-time deliverable documenting the investigation findings.
Live monitoring comes from V91 (C1-C4) and pre-commit hook (C5).

---

## REQUIREMENT REGISTRY

```yaml
# REQ-ROOT-001: Resurrection of deleted folders must block sprints, not warn
req_id: REQ-ROOT-001
source_section: "Root Causes #1, Structural Weaknesses #4"
change_set: C1
priority: P0

# REQ-ROOT-002: state/ folder must be resolved (delete or reclassify with producer fix first)
req_id: REQ-ROOT-002
source_section: "Corrections #2, What Must Be Redesigned #3"
change_set: C2
priority: P0
depends_on: REQ-ROOT-001 (sequence only — resolve before hardening)

# REQ-ROOT-003: Format coverage must derive from disk scan, not a missing file
req_id: REQ-ROOT-003
source_section: "Corrections #1, Root Causes #3, Actual State"
change_set: C3
priority: P1

# REQ-ROOT-004: README content floor must be checked, not just existence
req_id: REQ-ROOT-004
source_section: "Root Causes #5, What Must Be Redesigned #4"
change_set: C4
priority: P1

# REQ-ROOT-005: Unregistered directories must be caught at commit time
req_id: REQ-ROOT-005
source_section: "Root Causes #3, Structural Weaknesses #1"
change_set: C5
priority: P1

# REQ-ROOT-006: Registry producer claims must have at least one verifiable path
req_id: REQ-ROOT-006
source_section: "Structural Weaknesses #2, Actual State"
change_set: C6
priority: P2

# REQ-ROOT-007: 6 priority READMEs must pass content floor and include agent navigation
req_id: REQ-ROOT-007
source_section: "Symptoms #2, What Must Be Redesigned #4"
change_set: C7
priority: P1

# REQ-ROOT-008: Formal recon report must document all findings and resolutions
req_id: REQ-ROOT-008
source_section: "Deliverables"
change_set: C8
priority: P2
```

---

## HIERARCHICAL TASK STRUCTURE

### Execution DAG (dependency order)

```
TC-RR-001 (INVESTIGATION: state/ producer audit)
    └─► TC-RR-002 (RESOLUTION: state/ fix — delete or reclassify)
            └─► TC-RR-003 (CODE: V91 resurrection WARN→FAIL + test update)

TC-RR-004 (CODE: V91 source-test parity check — independent)
TC-RR-005 (CODE: V91 README content floor check — independent)
TC-RR-006 (CODE: check_new_root_dirs.py — independent)
    └─► TC-RR-007 (CONFIG: wire pre-commit hook)
TC-RR-008 (CODE: V91 registry producer integrity — independent)
TC-RR-009 (README: repair 6 priority READMEs — independent)

TC-RR-010 (TEST: new governance test suite)
    depends: TC-RR-003, TC-RR-004, TC-RR-005, TC-RR-006

TC-RR-011 (REPORT: formal recon report)
    depends: TC-RR-002 through TC-RR-009

TC-RR-012 (CLOSEOUT: terminal closeout + idempotency proof)
    depends: TC-RR-011
```

**Parallel execution safe groups:**
- Group A: TC-RR-004, TC-RR-005, TC-RR-006, TC-RR-008, TC-RR-009 (all independent)
- Group B: TC-RR-001 (must complete before TC-RR-002)
- Group C: TC-RR-002 (must complete before TC-RR-003)
- Group D: TC-RR-003 + Group A results → TC-RR-010
- Group E: TC-RR-010 → TC-RR-011 → TC-RR-012

---

## TASKCARD DEFINITIONS

---

### TC-RR-001 — INVESTIGATION: state/ Producer Audit

```
Taskcard ID: TC-RR-001
Type: PARENT / INVESTIGATION
Status: READY
Priority: P0
Owner: execution-agent
Supervisor: governance-validator

Requirement: REQ-ROOT-002
Plan section: "C2 — Resolve state/ correctly"
Root cause: "Producer-first ordering never enforced"

Objective:
  Determine whether any currently-executable code writes to state/ and
  identify the correct resolution path (delete or reclassify).

Outcome:
  Decision record: one of
    DECISION_A: No active producer found → safe to git rm -r state/
    DECISION_B: Active producer found → must redirect first, then delete

Scope:
  Allowed reads: state/current-state.json, state/current-state.md,
    entire repo for write-to-state/ references
  Forbidden: no file mutations in TC-RR-001

Inputs:
  - state/current-state.json (read)
  - state/current-state.md (read)
  - grep results for state/ write patterns

Outputs:
  - Inline decision record in this plan (update TC-RR-002 with DECISION_A or DECISION_B)
  - List of producers found (or empty)
  - Content summary of state/ files

Child taskcards:
  - TC-RR-001-01: Read state/ file contents
  - TC-RR-001-02: Search codebase for state/ write patterns
  - TC-RR-001-03: Check all DELETED registry entries for other resurrections
  - TC-RR-001-04: Record decision and update TC-RR-002 scope

Parent acceptance criteria:
  - Decision record is written (DECISION_A or DECISION_B)
  - All DELETED entries scanned (not just state/)
  - TC-RR-002 scope updated accordingly

Evidence required:
  - Content summary of state/current-state.json
  - Grep output for state/ write patterns
  - List of all DELETED entries on disk

Closeout criteria:
  - All 4 child taskcards CLOSED
  - Decision record present in TC-RR-002
```

#### TC-RR-001-01 — Read state/ file contents

```
Child Taskcard ID: TC-RR-001-01
Parent: TC-RR-001
Status: TODO
Type: INVESTIGATION

Purpose:
  Understand what data state/ contains and whether it is unique or redundant
  with .supervisor/state/.

Scope:
  Allowed reads: state/current-state.json, state/current-state.md
  Forbidden: no edits

Micro-steps:
  MS-001-01-01: Read state/current-state.md (small — read first for summary)
    Action: Read state/current-state.md
    Expected output: understand what this file describes

  MS-001-01-02: Read state/current-state.json (first 100 lines)
    Action: Read state/current-state.json with limit=100
    Expected output: understand schema — is this the same as .supervisor/state/?

  MS-001-01-03: Record whether content is unique vs .supervisor/state/
    Action: Compare field names in state/current-state.json against
      .supervisor/state/current-run.json (read first 50 lines of each)
    Expected output: UNIQUE or REDUNDANT classification

Acceptance checks:
  - Both files read and summarized
  - Uniqueness verdict recorded

Evidence:
  - Content summary (first 20 lines of each file)
  - Uniqueness verdict

Closeout:
  All 3 micro-steps COMPLETE
```

#### TC-RR-001-02 — Search codebase for state/ write patterns

```
Child Taskcard ID: TC-RR-001-02
Parent: TC-RR-001
Status: TODO
Type: INVESTIGATION

Purpose:
  Find any currently-executable tool that writes to state/.

Scope:
  Allowed: grep across tools/, .supervisor/, tests/supervisor/, src/
  Forbidden: no edits

Micro-steps:
  MS-001-02-01: Grep for 'state/' write references in Python files
    Action: grep pattern "state/" in tools/, .supervisor/ (type: py)
    Scope: look for open(...write...) or Path("state/") or similar
    Expected output: list of files with line numbers

  MS-001-02-02: Grep for 'current-state' references
    Action: grep pattern "current-state" across all files
    Expected output: list of files referencing current-state.json or .md

  MS-001-02-03: Grep for write references to 'state/' in YAML/JSON configs
    Action: grep "state/" in .supervisor/policies.yaml and skill-registry.yaml
    Expected output: any config references

  MS-001-02-04: Summarize findings — active producers or none
    Action: Review all grep results and classify:
      ACTIVE_PRODUCER: a .py file that demonstrably writes to state/
      ORPHAN: references are read-only or historical

Acceptance checks:
  - At least 3 search patterns executed
  - Clear ACTIVE_PRODUCER or ORPHAN verdict recorded

Evidence:
  - Grep output snippets for each search
  - Producer classification verdict

Next valid step:
  TC-RR-001-03
```

#### TC-RR-001-03 — Audit all DELETED registry entries

```
Child Taskcard ID: TC-RR-001-03
Parent: TC-RR-001
Status: TODO
Type: INVESTIGATION

Purpose:
  Before changing resurrection from WARN to FAIL (TC-RR-003), confirm that
  no other DELETED entries exist on disk that would immediately block sprints.

Scope:
  Allowed: read registry/repository-root-folders.yaml, check disk for each DELETED entry
  Forbidden: no edits

Micro-steps:
  MS-001-03-01: Extract all DELETED entries from registry
    Action: grep "retention: DELETED" in registry/repository-root-folders.yaml
    Expected output: list of folder_paths with retention=DELETED
    Currently known DELETED entries: skills/, examples-docs-readiness/, state/

  MS-001-03-02: Check each DELETED entry on disk
    Action: For each DELETED folder_path, check if it exists on disk
    Expected output: list of existing vs absent

  MS-001-03-03: Record findings and assess C1 risk
    Action: If any additional DELETED folders exist on disk beyond state/,
      add them to TC-RR-002 scope
    Expected output: complete list of all resurrections

Acceptance checks:
  - All DELETED entries checked
  - Risk assessment complete for TC-RR-003 sequencing

Evidence:
  - List of DELETED entries
  - Disk existence check for each
```

#### TC-RR-001-04 — Record decision and update TC-RR-002

```
Child Taskcard ID: TC-RR-001-04
Parent: TC-RR-001
Status: TODO
Type: DECISION

Purpose:
  Synthesize investigation findings into an actionable decision for TC-RR-002.

Scope:
  Allowed: edit this plan file (TC-RR-002 scope section only)
  Forbidden: no repo file edits

Micro-steps:
  MS-001-04-01: Write DECISION_A or DECISION_B into TC-RR-002
    Action: Based on TC-RR-001-01 through 01-03 findings:
      DECISION_A (no active producer, content redundant): update TC-RR-002 scope to
        "git rm -r state/"
      DECISION_B (active producer found): update TC-RR-002 scope to
        "redirect producer, then git rm -r state/"
    Edit: plan file TC-RR-002 "Decision:" field

  MS-001-04-02: Update TC-RR-002 status from BLOCKED to READY
    Action: Update TC-RR-002 status in this plan file

Closeout: Both micro-steps COMPLETE, TC-RR-002 is READY
```

---

### TC-RR-002 — RESOLUTION: state/ Folder Fix

```
Taskcard ID: TC-RR-002
Type: PARENT
Status: BLOCKED (depends on TC-RR-001)
Priority: P0
Owner: execution-agent

Requirement: REQ-ROOT-002
Root cause: "Producer-first ordering never enforced"

Decision: [TO BE FILLED BY TC-RR-001-04]
  Options: DECISION_A (delete) | DECISION_B (redirect then delete)

Objective:
  Resolve the state/ folder contradiction: either delete it (if safe) or
  reclassify it as RETAIN with proper README and updated registry entry.

Outcome:
  state/ either does not exist on disk, or exists with RETAIN status and README.
  V91 will no longer warn about state/ after this taskcard closes.

Scope:
  Allowed files:
    state/current-state.json (delete only, not edit)
    state/current-state.md (delete only, not edit)
    registry/repository-root-folders.yaml (update retention or confirm DELETED)
    Any producer tool identified in TC-RR-001 (redirect if DECISION_B)
    state/README.md (create if DECISION_B → reclassify)
  Forbidden: no changes to tools/ not identified as the producer

Child taskcards:
  - TC-RR-002-01: Verify no downstream reads depend on state/ files
  - TC-RR-002-02: Execute resolution (DECISION_A or DECISION_B)
  - TC-RR-002-03: Update registry and verify V91 no longer warns

Parent acceptance criteria:
  - state/ either absent or properly classified with README
  - V91 Check 3 no longer triggers for state/
  - Registry entry updated consistently

Rollback strategy:
  - git rm -r state/ is recoverable via git checkout (files are git-tracked)
  - Before rm: record SHA of both files as recovery reference

Depends on: TC-RR-001 (CLOSED)
Unlocks: TC-RR-003
```

#### TC-RR-002-01 — Verify no downstream reads depend on state/

```
Child Taskcard ID: TC-RR-002-01
Parent: TC-RR-002
Status: BLOCKED (depends on TC-RR-001)

Purpose:
  Before deleting state/, confirm no tool currently reads from it at runtime.
  If readers exist, they must be assessed for impact.

Micro-steps:
  MS-002-01-01: Grep for open/read patterns on state/current-state*
    Search: "current-state" with read patterns in tools/, .supervisor/, tests/
    Expected: zero readers OR identified reader list

  MS-002-01-02: Record read-dependency verdict
    SAFE_TO_DELETE: no active readers
    READERS_FOUND: list them, assess impact

Acceptance: verdict recorded
```

#### TC-RR-002-02 — Execute resolution

```
Child Taskcard ID: TC-RR-002-02
Parent: TC-RR-002
Status: BLOCKED (depends on TC-RR-002-01 verdict)

Purpose: Remove or reclassify state/ based on decision.

Precondition: TC-RR-002-01 verdict is SAFE_TO_DELETE or DECISION_B path is ready

Micro-steps:
  MS-002-02-01: Record file SHAs for rollback
    Action: Record git hash of state/current-state.json and state/current-state.md
    Command: git log --oneline -1 -- state/
    Evidence: record in closeout

  MS-002-02-02a (DECISION_A path): git rm -r state/
    Action: git rm -r state/
    Verify: ls state/ → "No such file"

  MS-002-02-02b (DECISION_B path): Redirect producer, then delete
    Sub-steps:
      - Edit identified producer to write to .supervisor/state/ instead
      - Verify producer runs without error
      - git rm -r state/

Acceptance:
  - DECISION_A: state/ does not exist on disk
  - DECISION_B: state/ does not exist, producer writes to .supervisor/state/
```

#### TC-RR-002-03 — Update registry and verify

```
Child Taskcard ID: TC-RR-002-03
Parent: TC-RR-002
Status: TODO (runs after TC-RR-002-02)

Purpose: Ensure registry reflects actual state and V91 agrees.

Micro-steps:
  MS-002-03-01: Update state/ entry in registry/repository-root-folders.yaml
    DECISION_A path: Add field "deleted_executed: true", "deleted_date: 2026-07-10"
    DECISION_B path: Change retention: DELETED → retention: RETAIN, add README path

  MS-002-03-02: Run V91 and confirm state/ no longer appears in WARN items
    Command: python tools/supervisor/governance_validators_root_struct.py --json
    Expected: no item with path="state" in output

  MS-002-03-03: Record evidence
    Evidence: V91 output JSON showing state/ absent from items

Closeout: V91 output confirms state/ resolved
```

---

### TC-RR-003 — CODE: V91 Resurrection WARN → FAIL

```
Taskcard ID: TC-RR-003
Type: PARENT
Status: BLOCKED (depends on TC-RR-002)
Priority: P0
Owner: execution-agent

Requirement: REQ-ROOT-001
Files:
  Primary: tools/supervisor/governance_validators_root_struct.py
  Test:    tests/supervisor/test_validate_root_structure.py

Objective:
  Change resurrection detection severity from WARN to FAIL so that deleted
  folders reappearing on disk block the sprint instead of being silently tolerated.

Outcome:
  - V91 Check 3 items have severity="FAIL" and trigger has_fail=True.
  - test_warn_resurrected_deleted renamed to test_fail_resurrected_deleted,
    asserts blocks_sprint=True.
  - test_pass_on_real_repo asserts result=="PASS" (no WARNs tolerated).
  - All 7 existing V91 tests pass.

Preserved behavior:
  - Check 1 (unregistered dir → FAIL) unchanged
  - Check 2 (missing README → WARN) unchanged
  - Check 3 logic unchanged except severity+has_fail

Scope:
  Allowed: 2 files listed above only
  Forbidden: no changes to any other validator file

Child taskcards:
  - TC-RR-003-01: Edit governance_validators_root_struct.py (2 line changes)
  - TC-RR-003-02: Update test_validate_root_structure.py (test updates)
  - TC-RR-003-03: Run full V91 test suite and verify

Depends on: TC-RR-002 (state/ resolved — so real-repo test can assert PASS)

Quality gates:
  - All 7 original tests pass (updated)
  - 0 regressions introduced
```

#### TC-RR-003-01 — Edit V91 resurrection severity

```
Child Taskcard ID: TC-RR-003-01
Parent: TC-RR-003
Status: TODO

Purpose: Change exactly 2 lines in the validator (severity + has_fail).

Precondition: TC-RR-002 CLOSED (state/ resolved)

Micro-steps:
  MS-003-01-01: Read governance_validators_root_struct.py lines 99-111 (Check 3)
    Confirm current code: severity="WARN", no has_fail=True in this block

  MS-003-01-02: Edit line 109 — change "WARN" to "FAIL"
    old_string: '"severity": "WARN",' (in Check 3 block, resurrected_deleted)
    new_string: '"severity": "FAIL",'
    Verify: unique match in file

  MS-003-01-03: Edit to set has_fail=True in resurrection block
    After the items.append() call for resurrected_deleted, add:
    old_string: (the closing of the if folder.exists(): block without has_fail)
    new_string: (same block with has_fail = True added after append)
    Verify: has_fail=True is now set for Check 3

  MS-003-01-04: Read modified lines 99-115 to confirm changes correct
    Verify: no unintended edits, structure intact

Acceptance:
  - Exactly 2 logical changes: severity value and has_fail assignment
  - File reads correctly after edit

Evidence:
  - Before/after diff of lines 99-115
```

#### TC-RR-003-02 — Update test file

```
Child Taskcard ID: TC-RR-003-02
Parent: TC-RR-003
Status: TODO
Depends on: TC-RR-003-01

Purpose:
  Update the test file to assert FAIL (not WARN) for resurrection, and to
  assert PASS (not WARN-or-PASS) on the real repo.

Micro-steps:
  MS-003-02-01: Read test_validate_root_structure.py fully (confirmed: 129 lines)
    Identify exact strings to change

  MS-003-02-02: Update test_warn_resurrected_deleted
    Rename to test_fail_resurrected_deleted:
    old: assert result["result"] == "WARN"
    new: assert result["result"] == "FAIL"
    old: assert result["blocks_sprint"] is False
    new: assert result["blocks_sprint"] is True

  MS-003-02-03: Update test_pass_on_real_repo
    old: assert result["result"] in ("PASS", "WARN"), ...
    new: assert result["result"] == "PASS", ...
    Remove: the comment about tolerating WARN for state/

  MS-003-02-04: Read test file after edits to verify
    Confirm no unintended changes

Acceptance:
  - test_fail_resurrected_deleted exists with correct assertions
  - test_pass_on_real_repo asserts PASS (not PASS|WARN)

Evidence:
  - Diff of changed lines
```

#### TC-RR-003-03 — Run and verify test suite

```
Child Taskcard ID: TC-RR-003-03
Parent: TC-RR-003
Status: TODO
Depends on: TC-RR-003-01, TC-RR-003-02

Purpose: Confirm all V91 tests pass after the changes.

Micro-steps:
  MS-003-03-01: Run V91 test suite
    Command: .venv/Scripts/pytest tests/supervisor/test_validate_root_structure.py -v
    Expected: 7 tests collected, 7 passed, 0 failed

  MS-003-03-02: Run V91 on real repo and confirm PASS
    Command: python tools/supervisor/governance_validators_root_struct.py --json
    Expected: result=="PASS", items=[]

  MS-003-03-03: Run V91 twice and hash outputs (idempotency spot check)
    Command: two consecutive python invocations, hash comparison
    Expected: hashes match

Acceptance:
  - All 7 tests pass
  - Real-repo result: PASS
  - Idempotency: hashes match

Evidence:
  - pytest output (full -v)
  - V91 JSON output from real repo
  - Idempotency hash comparison
```

---

### TC-RR-004 — CODE: V91 Source-Test Parity Check

```
Taskcard ID: TC-RR-004
Type: PARENT
Status: READY (independent)
Priority: P1
Owner: execution-agent

Requirement: REQ-ROOT-003
Files:
  Primary: tools/supervisor/governance_validators_root_struct.py

Objective:
  Replace the missing-external-file-dependent Check 4 with an in-memory
  source-to-test parity check that always runs.

Preserved behavior:
  - Checks 1, 2, 3 unchanged
  - New check adds WARN items only (non-blocking)
  - Validator remains idempotent

Child taskcards:
  - TC-RR-004-01: Add _check_source_test_parity() function
  - TC-RR-004-02: Replace Check 4 call with new function call
  - TC-RR-004-03: Add unit tests for new check
  - TC-RR-004-04: Run tests and verify
```

#### TC-RR-004-01 — Add _check_source_test_parity()

```
Child Taskcard ID: TC-RR-004-01
Parent: TC-RR-004
Status: TODO

Purpose: Add the new coverage derivation function (C3 corrected design).

Micro-steps:
  MS-004-01-01: Read governance_validators_root_struct.py to find insertion point
    Good insertion: before validate_root_structure(), after module-level constants

  MS-004-01-02: Insert _check_source_test_parity() function
    Content: exact function from C3 corrected design above
    Insert after line 21 (_REPO_ROOT = ...) and before @validator decorator

  MS-004-01-03: Read inserted function to verify
    Confirm indentation, logic, and no syntax errors

Evidence: Function exists, reads correctly
```

#### TC-RR-004-02 — Replace Check 4 with new function

```
Child Taskcard ID: TC-RR-004-02
Parent: TC-RR-004
Depends on: TC-RR-004-01

Micro-steps:
  MS-004-02-01: Read current Check 4 block (lines 113-126)
    Confirm current code: opens coverage_path, silent-skips if absent

  MS-004-02-02: Replace Check 4 block
    Old: the if coverage_path.exists(): block (lines 114-126)
    New:
      # --- Check 4: Source-test parity (derived in-memory, no external file needed) ---
      items.extend(_check_source_test_parity(_r))

  MS-004-02-03: Verify summary line still works
    The fail_count and warn_count counting logic is downstream of items — verify it
    still correctly counts the new items

Evidence: Modified file reads correctly, no syntax errors
```

#### TC-RR-004-03 — Add unit tests for new check

```
Child Taskcard ID: TC-RR-004-03
Parent: TC-RR-004
Depends on: TC-RR-004-01

Purpose:
  Add 2 focused tests for the new parity function to test_validate_root_structure.py.

Micro-steps:
  MS-004-03-01: Add fake_repo_with_coverage fixture
    In test file: a fake_repo that has src/python/csv/ but no tests/python/csv/

  MS-004-03-02: Add test_format_coverage_gap_detected()
    Assert: result contains FORMAT_COVERAGE_GAP item for tests/python/csv
    Assert: result["result"] == "WARN" (non-blocking)

  MS-004-03-03: Add test_format_coverage_no_gap()
    Fixture: fake_repo with src/python/csv/ AND tests/python/csv/
    Assert: no FORMAT_COVERAGE_GAP items in result

Evidence: Tests added, readable
```

#### TC-RR-004-04 — Run tests and verify

```
Child Taskcard ID: TC-RR-004-04
Parent: TC-RR-004
Depends on: TC-RR-004-02, TC-RR-004-03

Micro-steps:
  MS-004-04-01: Run full V91 test suite
    Command: .venv/Scripts/pytest tests/supervisor/test_validate_root_structure.py -v
    Expected: all tests pass (9 total after additions)

  MS-004-04-02: Run V91 on real repo, check for parity findings
    Command: python tools/supervisor/governance_validators_root_struct.py --json
    Expected: any FORMAT_COVERAGE_GAP items have WARN severity (non-blocking)

  MS-004-04-03: Record real-repo parity findings
    Document: which formats (if any) are missing test directories

Evidence: pytest output, real-repo parity report
```

---

### TC-RR-005 — CODE: V91 README Content Floor Check

```
Taskcard ID: TC-RR-005
Type: PARENT
Status: READY (independent)
Priority: P1
Owner: execution-agent

Requirement: REQ-ROOT-004
Files:
  Primary: tools/supervisor/governance_validators_root_struct.py

Objective:
  Add _check_readme_content_floor() and call it for each RETAIN folder's README.
  WARN severity (non-blocking). Catches stubs and empty files.

Known limit: keyword matching catches the floor (stubs/empty), not misleading content.

Child taskcards:
  - TC-RR-005-01: Add _check_readme_content_floor() function
  - TC-RR-005-02: Call floor check inside Check 2 block
  - TC-RR-005-03: Add unit tests
  - TC-RR-005-04: Run tests and verify
```

#### TC-RR-005-01 — Add _check_readme_content_floor()

```
Child Taskcard ID: TC-RR-005-01
Parent: TC-RR-005

Micro-steps:
  MS-005-01-01: Insert _check_readme_content_floor() at same location as TC-RR-004-01
    Content: exact function from C4 design above
    Insert after _check_source_test_parity() (if that exists) or same insertion point

  MS-005-01-02: Read inserted function to verify
    Confirm no syntax errors, correct indentation
```

#### TC-RR-005-02 — Call floor check inside Check 2

```
Child Taskcard ID: TC-RR-005-02
Parent: TC-RR-005
Depends on: TC-RR-005-01

Micro-steps:
  MS-005-02-01: Read Check 2 block (lines 79-97)
    Confirm current code: checks readme.exists() only

  MS-005-02-02: After the readme.exists() block, add floor check
    Location: inside the existing `if not readme.exists(): ... items.append()` block,
    AFTER the existing check, add an else branch:

    else:
        floor_issues = _check_readme_content_floor(readme)
        if floor_issues:
            items.append({
                "check": "readme_floor_fail",
                "path": str(readme.relative_to(_r)),
                "severity": "WARN",
                "message": f"README floor check failed for '{fp}': {floor_issues}",
            })

  MS-005-02-03: Read modified Check 2 block to verify
    Confirm logic: floor check only runs when readme EXISTS
```

#### TC-RR-005-03 — Add unit tests

```
Child Taskcard ID: TC-RR-005-03
Parent: TC-RR-005

Micro-steps:
  MS-005-03-01: Add test_readme_floor_fails_stub()
    Fixture: RETAIN folder with a 10-byte README ("# hi\n")
    Expected: WARN item with check="readme_floor_fail"

  MS-005-03-02: Add test_readme_floor_passes_adequate()
    Fixture: RETAIN folder with README containing "purpose", "producer", "command"
    Expected: no readme_floor_fail item

  MS-005-03-03: Add test_readme_floor_not_run_when_missing()
    Fixture: RETAIN folder with no README at all
    Expected: missing_readme item only, no readme_floor_fail item
```

#### TC-RR-005-04 — Run and verify

```
Child Taskcard ID: TC-RR-005-04
Parent: TC-RR-005
Depends on: TC-RR-005-02, TC-RR-005-03

Micro-steps:
  MS-005-04-01: Run full V91 test suite
    Command: .venv/Scripts/pytest tests/supervisor/test_validate_root_structure.py -v
    Expected: all tests pass

  MS-005-04-02: Run V91 on real repo, count floor failures
    Expected: some WARN items for floor failures (not unexpected — informs C7 work)

  MS-005-04-03: Record which READMEs fail the floor check
    This informs TC-RR-009 priority order (may revise or confirm existing order)
```

---

### TC-RR-006 — CODE: check_new_root_dirs.py Pre-Commit Script

```
Taskcard ID: TC-RR-006
Type: PARENT
Status: READY (independent)
Priority: P1
Owner: execution-agent

Requirement: REQ-ROOT-005
Files:
  New file: tools/supervisor/check_new_root_dirs.py

Objective:
  Create a fast (<2 second) pre-commit script that detects unregistered
  top-level directories in the git staging area.

Child taskcards:
  - TC-RR-006-01: Write check_new_root_dirs.py
  - TC-RR-006-02: Manual smoke test
```

#### TC-RR-006-01 — Write check_new_root_dirs.py

```
Child Taskcard ID: TC-RR-006-01
Parent: TC-RR-006

Micro-steps:
  MS-006-01-01: Create tools/supervisor/check_new_root_dirs.py
    Content: exact C5 script from design above
    Note: repo_root = Path(__file__).resolve().parents[2]
    Verify: parents[2] from tools/supervisor/ = repo root ✓

  MS-006-01-02: Read created file to verify
    Confirm: yaml import has fail-open fallback
    Confirm: handles both dot-dirs and visible dirs
    Confirm: sys.exit(0) for edge cases (no registry, no yaml)
    Confirm: sys.exit(1) only when real unregistered dirs found
```

#### TC-RR-006-02 — Manual smoke test

```
Child Taskcard ID: TC-RR-006-02
Parent: TC-RR-006
Depends on: TC-RR-006-01

Micro-steps:
  MS-006-02-01: Run script directly with no staged changes
    Command: python tools/supervisor/check_new_root_dirs.py
    Expected: exit 0, no output

  MS-006-02-02: Verify script parses registered directories correctly
    Command: python -c "import yaml; d=yaml.safe_load(open('registry/repository-root-folders.yaml')); print(len(d['folders']), 'folders registered')"
    Expected: 51 folders
```

---

### TC-RR-007 — CONFIG: Wire Pre-Commit Hook

```
Taskcard ID: TC-RR-007
Type: PARENT
Status: BLOCKED (depends on TC-RR-006)
Priority: P1
Owner: execution-agent

Requirement: REQ-ROOT-005
Files:
  Primary: .pre-commit-config.yaml

Objective:
  Add check-root-dirs hook to .pre-commit-config.yaml.
  Hook runs on pre-commit stage, not always_run.

Child taskcards:
  - TC-RR-007-01: Edit .pre-commit-config.yaml
  - TC-RR-007-02: Verify hook syntax
```

#### TC-RR-007-01 — Edit .pre-commit-config.yaml

```
Child Taskcard ID: TC-RR-007-01
Parent: TC-RR-007

Micro-steps:
  MS-007-01-01: Read .pre-commit-config.yaml (confirmed: 67 lines)
    Identify correct insertion location: after last local hook entry

  MS-007-01-02: Add hook entry inside the existing "repo: local" block
    Insert after the last existing hook (project-status-structure-check, ends ~line 66)
    New entry:
      - id: check-root-dirs
        name: Check for unregistered root directories
        entry: python tools/supervisor/check_new_root_dirs.py
        language: system
        pass_filenames: false
        always_run: false
        stages: [pre-commit]

  MS-007-01-03: Read .pre-commit-config.yaml after edit to verify structure
    Confirm: YAML is valid (no indentation errors)
    Confirm: new hook is inside "repo: local" block
```

#### TC-RR-007-02 — Verify hook syntax

```
Child Taskcard ID: TC-RR-007-02
Parent: TC-RR-007
Depends on: TC-RR-007-01

Micro-steps:
  MS-007-02-01: Validate YAML syntax
    Command: python -c "import yaml; yaml.safe_load(open('.pre-commit-config.yaml'))"
    Expected: no exception

  MS-007-02-02: Run pre-commit --list-hooks to confirm new hook appears
    Command: .venv/Scripts/pre-commit run check-root-dirs --all-files
    Expected: Passed (no unregistered dirs on clean repo)
```

---

### TC-RR-008 — CODE: V91 Registry Producer Integrity Check

```
Taskcard ID: TC-RR-008
Type: PARENT
Status: READY (independent)
Priority: P2
Owner: execution-agent

Requirement: REQ-ROOT-006
Files:
  Primary: tools/supervisor/governance_validators_root_struct.py

Objective:
  Add lightweight _check_registry_producer_integrity() and surface entries that
  list ONLY non-verifiable producers (WARN-only, non-blocking).

Known limit: Most producer entries will have non-verifiable strings ("developers",
"CI", etc.). This surfaces the systemic issue without claiming to fix it.

Child taskcards:
  - TC-RR-008-01: Add _check_registry_producer_integrity() function
  - TC-RR-008-02: Call it for each RETAIN entry in V91
  - TC-RR-008-03: Add unit test
  - TC-RR-008-04: Run and record real-repo findings
```

#### TC-RR-008-01 — Add integrity check function

```
Child Taskcard ID: TC-RR-008-01
Parent: TC-RR-008

Micro-steps:
  MS-008-01-01: Insert _check_registry_producer_integrity() in governance_validators_root_struct.py
    Content: exact C6 function from design above
    Insert with other helper functions (before @validator decorator)

  MS-008-01-02: Read inserted function to verify
```

#### TC-RR-008-02 — Call in V91 for each RETAIN entry

```
Child Taskcard ID: TC-RR-008-02
Parent: TC-RR-008
Depends on: TC-RR-008-01

Micro-steps:
  MS-008-02-01: Add call inside Check 2 loop (RETAIN entries)
    After the readme floor check, add:
      integrity_warn = _check_registry_producer_integrity(entry, _r)
      if integrity_warn:
          items.append({
              "check": "registry_producer_integrity",
              "path": entry["folder_path"],
              "severity": "WARN",
              "message": integrity_warn,
          })

  MS-008-02-02: Verify modification
    Read modified section
```

#### TC-RR-008-03 — Add unit test

```
Child Taskcard ID: TC-RR-008-03
Parent: TC-RR-008

Micro-steps:
  MS-008-03-01: Add test_registry_producer_integrity_warns_on_fiction()
    Fixture: RETAIN entry with producers: ["developers", "humans"]
    Expected: WARN item with check="registry_producer_integrity"

  MS-008-03-02: Add test_registry_producer_integrity_passes_with_tool_path()
    Fixture: RETAIN entry with producers: ["tools/supervisor/some_tool.py"]
      and create that file in fake_repo
    Expected: no integrity warning
```

#### TC-RR-008-04 — Run and record findings

```
Child Taskcard ID: TC-RR-008-04
Parent: TC-RR-008
Depends on: TC-RR-008-02, TC-RR-008-03

Micro-steps:
  MS-008-04-01: Run tests
    Command: .venv/Scripts/pytest tests/supervisor/test_validate_root_structure.py -v
    Expected: all tests pass

  MS-008-04-02: Run V91 on real repo, count integrity warnings
    Expected: many WARN items (most entries have non-verifiable producers)
    Document: total count for recon report
```

---

### TC-RR-009 — README: Repair 6 Priority READMEs

```
Taskcard ID: TC-RR-009
Type: PARENT
Status: READY (independent, but floor check results from TC-RR-005-04 may refine order)
Priority: P1
Owner: execution-agent

Requirement: REQ-ROOT-007

Objective:
  Add "## Agent Navigation" section to each of 6 priority READMEs.
  Preserve ALL existing content. Augment only.

Constraint: Read each README fully before editing. Never replace content.

Child taskcards:
  One child per README file:
  - TC-RR-009-01: src/README.md
  - TC-RR-009-02: tests/_readme.md
  - TC-RR-009-03: tools/_readme.md
  - TC-RR-009-04: registry/README.md
  - TC-RR-009-05: plans/README.md
  - TC-RR-009-06: reports/_readme.md

Parent acceptance criteria:
  - All 6 READMEs pass _check_readme_content_floor() after repair
  - No existing content removed from any README
```

#### TC-RR-009-01 — src/README.md

```
Child Taskcard ID: TC-RR-009-01
Parent: TC-RR-009

Scope:
  Allowed: src/README.md only
  Forbidden: any src/ source file

Micro-steps:
  MS-009-01-01: Read src/README.md fully
    Note current content, size, headings

  MS-009-01-02: Draft ## Agent Navigation section content
    Must include:
    - Where to create a new Python format: src/python/{format_id}/
    - Required files for new Python format: __init__.py, pyproject.toml
    - Where to create a new .NET format: src/net/{format_id}/
    - Required files for new .NET format: {Name}.csproj + source files
    - Register new format: registry/format-registry.yaml
    - Validation: python tools/supervisor/governance_validators_root_struct.py

  MS-009-01-03: Append section to src/README.md
    Append (do not insert mid-file): ## Agent Navigation + content

  MS-009-01-04: Read src/README.md after edit, verify
    Confirm: original content intact, new section at end

  MS-009-01-05: Run _check_readme_content_floor on updated file
    Command: python -c "
    import sys; sys.path.insert(0,'tools/supervisor')
    from governance_validators_root_struct import _check_readme_content_floor
    from pathlib import Path
    r=_check_readme_content_floor(Path('src/README.md'))
    print('floor issues:', r)
    "
    Expected: [] (empty list = passes)

Closeout: floor check passes, content verified
```

#### TC-RR-009-02 through TC-RR-009-06

```
Same pattern as TC-RR-009-01 applied to each file.
Each child taskcard:
  - Reads the target README fully
  - Drafts ## Agent Navigation with file-specific content
  - Appends (preserves existing content)
  - Reads back to verify
  - Runs floor check to confirm pass

TC-RR-009-02: tests/_readme.md
  Navigation content:
  - Add format test: tests/python/{format_id}/test_{format_id}.py
  - Run tests: .venv/Scripts/pytest tests/python/{format_id}/ -v
  - Governance tests: tests/supervisor/ and tests/governance/

TC-RR-009-03: tools/_readme.md
  Navigation content:
  - Add supervisor automation tool: tools/supervisor/
  - Add governance validator: tools/supervisor/governance_validators_*.py
  - Add packaging tool: tools/packaging/
  - Run validators: python tools/supervisor/governance_validator_runner.py

TC-RR-009-04: registry/README.md
  Navigation content:
  - Register new format: edit registry/format-registry.yaml
  - Register new top-level folder: edit registry/repository-root-folders.yaml
  - Validate registry: python tools/supervisor/governance_validators_root_struct.py

TC-RR-009-05: plans/README.md
  Navigation content:
  - New per-chat plan: plans/.claude/{plan-name}.md
  - New strategic plan: plans/strategic/{plan-name}.md
  - Master plan: plans/master-plan.md (do not rename or move)

TC-RR-009-06: reports/_readme.md
  Navigation content:
  - Supervisor output: reports/supervisor/ (generated by supervisor pipeline)
  - Evidence: .local/evidences/ (gitignored, not in reports/)
  - Repository structure: reports/repository-structure/
```

---

### TC-RR-010 — TEST: Root Folder Governance Test Suite

```
Taskcard ID: TC-RR-010
Type: PARENT
Status: BLOCKED (depends on TC-RR-003, TC-RR-004, TC-RR-005, TC-RR-006)
Priority: P1
Owner: execution-agent

Requirement: REQ-ROOT-001 through REQ-ROOT-005
Files:
  New: tests/supervisor/test_root_folder_governance.py
  Existing: tests/supervisor/test_validate_root_structure.py (already updated by TC-RR-003/004/005)

Objective:
  Add an integration-level test file that covers the new governance behaviors
  end-to-end. Individual unit tests were added per-taskcard above; this file
  covers cross-cutting scenarios.

Child taskcards:
  - TC-RR-010-01: Write test file skeleton
  - TC-RR-010-02: Add pre-commit script tests
  - TC-RR-010-03: Add V91 integration scenarios
  - TC-RR-010-04: Run full suite
```

#### TC-RR-010-01 — Write test file skeleton

```
Child Taskcard ID: TC-RR-010-01
Parent: TC-RR-010

Micro-steps:
  MS-010-01-01: Create tests/supervisor/test_root_folder_governance.py
    Header imports, sys.path, imports from governance_validators_root_struct
    and check_new_root_dirs

  MS-010-01-02: Read created file to verify imports resolve
```

#### TC-RR-010-02 — Pre-commit script tests

```
Child Taskcard ID: TC-RR-010-02
Parent: TC-RR-010

Micro-steps:
  MS-010-02-01: Add test_precommit_rejects_unregistered_dir()
    Use subprocess to call check_new_root_dirs.py with mocked git staging
    OR use tmp_path with a modified registry to simulate detection

  MS-010-02-02: Add test_precommit_passes_clean()
    Call check_new_root_dirs.py on clean repo
    Expected: exit 0

  MS-010-02-03: Add test_precommit_fails_open_without_yaml()
    Import fails gracefully if yaml unavailable (mock yaml import)
    Expected: exit 0 (fail-open policy)
```

#### TC-RR-010-03 — V91 integration scenarios

```
Child Taskcard ID: TC-RR-010-03
Parent: TC-RR-010

Micro-steps:
  MS-010-03-01: Add test_v91_full_scenario_resurrection_now_fails()
    Scenario: repo with DELETED entry that exists on disk
    Expected: FAIL result, blocks_sprint=True
    Confirm this was not possible before TC-RR-003

  MS-010-03-02: Add test_v91_parity_check_real_repo()
    Run V91 on real repo, assert FORMAT_COVERAGE_GAP items have WARN severity
    Assert: no FORMAT_COVERAGE_GAP items with FAIL severity (non-blocking)

  MS-010-03-03: Add test_v91_readme_floor_real_repo()
    After TC-RR-009 repairs, run V91 on real repo
    Assert: 6 priority READMEs produce no readme_floor_fail items
```

#### TC-RR-010-04 — Run full suite

```
Child Taskcard ID: TC-RR-010-04
Parent: TC-RR-010
Depends on: TC-RR-010-01, 010-02, 010-03

Micro-steps:
  MS-010-04-01: Run new test file
    Command: .venv/Scripts/pytest tests/supervisor/test_root_folder_governance.py -v
    Expected: all tests pass

  MS-010-04-02: Run both test files together (regression check)
    Command: .venv/Scripts/pytest tests/supervisor/test_validate_root_structure.py
      tests/supervisor/test_root_folder_governance.py -v
    Expected: all tests pass, no conflicts

  MS-010-04-03: Record total test count
    Expected: original 7 + new checks from 003/004/005/010 ≈ 20+ tests
```

---

### TC-RR-011 — REPORT: Formal Recon Report

```
Taskcard ID: TC-RR-011
Type: PARENT
Status: BLOCKED (depends on TC-RR-002 through TC-RR-010)
Priority: P2
Owner: execution-agent

Requirement: REQ-ROOT-008
Files:
  New: reports/repository-structure/root-folder-recon-report.md

Objective:
  Create the formal one-time documentation of this investigation and its outcomes.
  Not a live monitoring system — that is V91 + pre-commit hook.

Child taskcards:
  - TC-RR-011-01: Create reports/repository-structure/ directory (if absent)
  - TC-RR-011-02: Write recon report with all sections
  - TC-RR-011-03: Verify report completeness

Required sections (§39 structure):
  1. Repository Baseline (branch, HEAD, folder counts)
  2. Folder Summary table (all 51 folders, one row each)
  3. Individual Folder Reviews (abbreviated — key fields per folder)
  4. Format Coverage table (src/python, src/net, tests)
  5. README Backfill table (6 repairs)
  6. Removed/Consolidated/Relocated Folders (state/ action)
  7. Governance System (what was built, what remains)
  8. Agent Discoverability section
  9. Final Verdict
```

#### TC-RR-011-01 — Create directory

```
Child Taskcard ID: TC-RR-011-01
Parent: TC-RR-011

Micro-steps:
  MS-011-01-01: Check if reports/repository-structure/ exists
    Command: ls reports/repository-structure/ 2>&1

  MS-011-01-02: Create directory if absent
    Action: mkdir reports/repository-structure/ (only if needed)
    Note: directory creation does not require registry update
      (reports/ is already RETAIN, subdirs don't need individual entries)
```

#### TC-RR-011-02 — Write recon report

```
Child Taskcard ID: TC-RR-011-02
Parent: TC-RR-011
Depends on: TC-RR-011-01

Micro-steps:
  MS-011-02-01: Gather final V91 output to use as data source
    Command: python tools/supervisor/governance_validators_root_struct.py --json
    Record: result, items, summary

  MS-011-02-02: Write reports/repository-structure/root-folder-recon-report.md
    Include all 9 required sections
    Folder Summary table: all 51 registry entries
    Final Verdict: ROOT_FOLDERS_RECONCILED_DOCUMENTED_GOVERNED_AND_IDEMPOTENT
      (only if all success criteria pass — otherwise ROOT_FOLDER_RECON_ACTIVE_NEXT_TASK_READY)

  MS-011-02-03: Read report to verify completeness
    Confirm: all 9 sections present
    Confirm: Folder Summary table has 51 rows
    Confirm: state/ disposition documented
```

---

### TC-RR-012 — CLOSEOUT: Terminal Closeout and Idempotency

```
Taskcard ID: TC-RR-012
Type: PARENT
Status: BLOCKED (depends on TC-RR-011)
Priority: P2
Owner: execution-agent

Requirement: All requirements
Files:
  New: .local/evidences/root-folder-recon-2026-07-10/terminal-closeout.yaml

Objective:
  Record terminal state, prove idempotency, and confirm closure gate.

Child taskcards:
  - TC-RR-012-01: Idempotency proof (run V91 twice, hash both)
  - TC-RR-012-02: Run complete test suite one final time
  - TC-RR-012-03: Write terminal-closeout.yaml
  - TC-RR-012-04: Verify closure gate

Closure gate (from §40):
  UNCLASSIFIED_TOP_LEVEL_FOLDERS = 0 (registry has all 51)
  RETAINED_FOLDERS_WITHOUT_CURRENT_README = 0 (verified by V91)
  FORMAT_SCOPED_FOLDERS_WITH_UNEXPLAINED_GAPS = 0 (parity check runs, gaps have WARN)
  PROVEN_OBSOLETE_FOLDERS_REMAINING = 0 (state/ resolved)
  BROKEN_ROOT_FOLDER_REFERENCES = 0 (V91 PASS)
  README_STRUCTURE_DRIFT = 0 (floor check PASS for 6 priority)
  MATERIAL_SECOND_RUN_CHANGES = 0 (idempotency hash match)
```

#### TC-RR-012-01 — Idempotency proof

```
Child Taskcard ID: TC-RR-012-01
Parent: TC-RR-012

Micro-steps:
  MS-012-01-01: Run V91 first time, capture JSON, hash it
    Command (Windows):
    python -c "
    import json, hashlib, sys
    sys.path.insert(0,'tools/supervisor')
    from governance_validators_root_struct import validate_root_structure
    r=validate_root_structure({})
    h=hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest()
    print('run1 hash:', h)
    print('run1 result:', r['result'])
    "

  MS-012-01-02: Run V91 second time, capture JSON, hash it
    Same command as above

  MS-012-01-03: Assert hashes match
    Expected: run1 hash == run2 hash
    Evidence: record both hashes

  MS-012-01-04: Run test suite second time, confirm same results
    Command: .venv/Scripts/pytest tests/supervisor/ -v --tb=short
    Expected: same pass/fail count as first run
```

#### TC-RR-012-02 — Final test suite run

```
Child Taskcard ID: TC-RR-012-02
Parent: TC-RR-012

Micro-steps:
  MS-012-02-01: Run complete test suites
    Command: .venv/Scripts/pytest tests/supervisor/test_validate_root_structure.py
      tests/supervisor/test_root_folder_governance.py -v
    Expected: all tests pass
    Record: total count, 0 failures
```

#### TC-RR-012-03 — Write terminal-closeout.yaml

```
Child Taskcard ID: TC-RR-012-03
Parent: TC-RR-012
Depends on: TC-RR-012-01, TC-RR-012-02

Micro-steps:
  MS-012-03-01: Create .local/evidences/root-folder-recon-2026-07-10/ directory

  MS-012-03-02: Write terminal-closeout.yaml
    Content includes:
      mission_id: ROOT-RECON-001
      starting_revision: <baseline HEAD>
      ending_revision: <final HEAD>
      original_top_level_folders: [51 entries]
      final_top_level_folders: [50 entries if state/ deleted, else 51]
      deleted_folders: [state/] (or [] if reclassified)
      readmes_updated: [6 READMEs]
      validators: [tools/supervisor/governance_validators_root_struct.py]
      tests: [tests/supervisor/test_validate_root_structure.py,
              tests/supervisor/test_root_folder_governance.py]
      pre_commit_scripts: [tools/supervisor/check_new_root_dirs.py]
      final_report: reports/repository-structure/root-folder-recon-report.md
      idempotency_hash_run1: <hash>
      idempotency_hash_run2: <hash>
      idempotency_match: true
      unresolved_findings: []
      verdict: ROOT_FOLDERS_RECONCILED_DOCUMENTED_GOVERNED_AND_IDEMPOTENT
      closed: true
```

#### TC-RR-012-04 — Verify closure gate

```
Child Taskcard ID: TC-RR-012-04
Parent: TC-RR-012
Depends on: TC-RR-012-03

Micro-steps:
  MS-012-04-01: Check each closure gate criterion
    UNCLASSIFIED_TOP_LEVEL_FOLDERS = 0: V91 result==PASS (no FAIL items)
    RETAINED_FOLDERS_WITHOUT_CURRENT_README = 0: V91 no missing_readme items
    FORMAT_SCOPED_GAPS = 0 (unexplained): parity items are WARN with known dispositions
    PROVEN_OBSOLETE_FOLDERS_REMAINING = 0: state/ resolved
    MATERIAL_SECOND_RUN_CHANGES = 0: idempotency hash match

  MS-012-04-02: If all gates pass: confirm closed: true in terminal-closeout.yaml
    If any gate fails: set closed: false and list blocking gate(s)
```

---

## TASKCARD STATE MACHINE

```yaml
# Parent transitions (valid only)
parent_transitions:
  - [PROPOSED, READY]
  - [READY, IN_PROGRESS]
  - [IN_PROGRESS, CHILDREN_IN_PROGRESS]
  - [CHILDREN_IN_PROGRESS, INTEGRATION_PENDING]
  - [INTEGRATION_PENDING, VERIFIED]
  - [VERIFIED, SCORED]
  - [SCORED, CLOSED]
  - [SCORED, REROUTED]
  - [any_non_closed, BLOCKED]
  - [BLOCKED, READY]
  - [any_non_closed, BLOCKED_EXTERNAL]
  - [any_non_closed, DEFERRED_WITH_REASON]

# Child transitions (valid only)
child_transitions:
  - [TODO, READY]
  - [READY, IN_PROGRESS]
  - [IN_PROGRESS, IMPLEMENTED]
  - [IMPLEMENTED, VERIFIED]
  - [VERIFIED, SCORED]
  - [SCORED, CLOSED]
  - [SCORED, REROUTED]
  - [REROUTED, IN_PROGRESS]
  - [any_non_closed, BLOCKED]
  - [BLOCKED, READY]
  - [any_non_closed, BLOCKED_EXTERNAL]
  - [any_non_closed, DEFERRED_WITH_REASON]

# INVALID transitions (must never occur)
invalid_transitions:
  - [TODO, CLOSED]
  - [READY, CLOSED]
  - [IMPLEMENTED, CLOSED]
  - [REROUTED, CLOSED]  # without rework evidence
  - parent_CLOSED_while_mandatory_children_incomplete: true
  - child_CLOSED_while_mandatory_micro_steps_incomplete: true
  - BLOCKED_EXTERNAL_to_CLOSED_without_unblock_evidence: true

# Quality scoring (applies to child taskcards)
quality_gates:
  acceptance_threshold: 4  # out of 5
  dimensions:
    - requirement_correctness
    - implementation_correctness
    - scope_discipline
    - validation_strength
    - evidence_completeness
    - regression_safety
  below_threshold_action: REROUTED
```

---

## VALIDATION MATRIX

| Taskcard | Check type | Command | Expected | Blocks |
|----------|-----------|---------|----------|--------|
| TC-RR-003-03 | Unit test | pytest test_validate_root_structure.py -v | 7 pass | YES |
| TC-RR-003-03 | Real repo V91 | python governance_validators_root_struct.py --json | result==PASS | YES |
| TC-RR-004-04 | Unit test | pytest test_validate_root_structure.py -v | 9 pass | YES |
| TC-RR-004-04 | Real repo parity | V91 JSON output | FORMAT_COVERAGE_GAP items ≤ WARN | NO |
| TC-RR-005-04 | Unit test | pytest test_validate_root_structure.py -v | all pass | YES |
| TC-RR-006-02 | Script smoke | python check_new_root_dirs.py | exit 0 | YES |
| TC-RR-007-02 | YAML valid | python -c yaml.safe_load | no exception | YES |
| TC-RR-007-02 | Hook runs | pre-commit run check-root-dirs --all-files | Passed | NO |
| TC-RR-009-01..06 | Floor check | python -c _check_readme_content_floor(...) | [] | NO |
| TC-RR-010-04 | Integration | pytest test_root_folder_governance.py -v | all pass | YES |
| TC-RR-012-01 | Idempotency | hash V91 twice | hash1 == hash2 | YES |
| TC-RR-012-02 | Regression | pytest tests/supervisor/ -v | all pass | YES |

---

## EVIDENCE CONTRACT

```
evidence_root: .local/evidences/root-folder-recon-2026-07-10/

Required evidence artifacts:
  baseline/
    root-tree.txt          (ls -la output at start)
    v91-baseline.json      (V91 output before changes)
    head-revision.txt      (git rev-parse HEAD)

  decisions/
    state-investigation.md (TC-RR-001 findings: DECISION_A or DECISION_B)
    deleted-entries-audit.md (TC-RR-001-03 findings)

  validation/
    v91-after-changes.json  (TC-RR-003-03 real-repo output)
    pytest-v91-run.txt      (TC-RR-003-03 pytest output)
    pytest-governance-run.txt (TC-RR-010-04 output)
    readme-floor-check-results.json (TC-RR-005-04 real-repo results)
    idempotency-hash-comparison.txt (TC-RR-012-01)

  closeout/
    terminal-closeout.yaml  (TC-RR-012-03)

Every artifact must reference:
  authoritative_plan: plans/.claude/playful-discovering-thunder.md
  execution_authority: false  # (for evidence files)
```

---

## FILES CHANGED SUMMARY

| File | Action | Taskcard | Purpose |
|------|--------|----------|---------|
| `tools/supervisor/governance_validators_root_struct.py` | EDIT | TC-RR-003/004/005/008 | C1/C3/C4/C6: severity, parity, floor, integrity |
| `tools/supervisor/check_new_root_dirs.py` | CREATE | TC-RR-006 | C5: pre-commit script |
| `.pre-commit-config.yaml` | EDIT | TC-RR-007 | Wire pre-commit hook |
| `state/` (whole dir) | DELETE or RECLASSIFY | TC-RR-002 | C2: resolve resurrection |
| `state/README.md` | CREATE (if reclassify) | TC-RR-002 | Only if DECISION_B → RETAIN |
| `registry/repository-root-folders.yaml` | EDIT | TC-RR-002-03 | Update state/ entry post-resolution |
| `src/README.md` | EDIT (append) | TC-RR-009-01 | C7: add Agent Navigation |
| `tests/_readme.md` | EDIT (append) | TC-RR-009-02 | C7: add Agent Navigation |
| `tools/_readme.md` | EDIT (append) | TC-RR-009-03 | C7: add Agent Navigation |
| `registry/README.md` | EDIT (append) | TC-RR-009-04 | C7: add Agent Navigation |
| `plans/README.md` | EDIT (append) | TC-RR-009-05 | C7: add Agent Navigation |
| `reports/_readme.md` | EDIT (append) | TC-RR-009-06 | C7: add Agent Navigation |
| `tests/supervisor/test_validate_root_structure.py` | EDIT | TC-RR-003-02/004-03/005-03/008-03 | Update assertions, add tests |
| `tests/supervisor/test_root_folder_governance.py` | CREATE | TC-RR-010 | Integration test suite |
| `reports/repository-structure/root-folder-recon-report.md` | CREATE | TC-RR-011 | C8: formal recon report |
| `.local/evidences/root-folder-recon-2026-07-10/terminal-closeout.yaml` | CREATE | TC-RR-012 | Terminal closeout |

---

## SUCCESS CRITERIA

The system is durable when ALL of:

1. `python tools/supervisor/governance_validators_root_struct.py` exits 0 with `result=="PASS"`.
2. Creating and staging an unregistered directory causes pre-commit to exit 1.
3. Running V91 twice in a row produces identical JSON output (hash match).
4. All tests in `tests/supervisor/test_validate_root_structure.py` and
   `tests/supervisor/test_root_folder_governance.py` pass.
5. The 6 priority READMEs each return `[]` from `_check_readme_content_floor()`.
6. `state/` situation is resolved: either absent or RETAIN with README.
7. Format parity findings (if any) have WARN severity with documented dispositions.

The system is NOT fixed if:
- V91 passes because violations were added to an allowlist.
- Tests pass because they were loosened to accommodate failures.
- READMEs pass the floor check but no agent navigation section was added.

---

## EXECUTION HANDOFF

The execution agent must:

1. Read this plan from `plans/.claude/playful-discovering-thunder.md`.
2. Begin with TC-RR-001 (INVESTIGATION: state/ producer audit).
3. Execute exactly one micro-step at a time.
4. After each micro-step: record evidence, update child status, verify output.
5. Do not close a child taskcard until all its micro-steps are COMPLETE.
6. Do not close a parent taskcard until all its children are CLOSED and integration checks pass.
7. After TC-RR-001 closes: update TC-RR-002 with DECISION_A or DECISION_B, then execute TC-RR-002.
8. After TC-RR-002 closes: execute TC-RR-003 (severity change), then all independent tasks
   in Group A (TC-RR-004/005/006/008/009) may proceed.
9. After all Group A tasks and TC-RR-003 close: execute TC-RR-010.
10. After TC-RR-010 closes: execute TC-RR-011, then TC-RR-012.
11. After TC-RR-012 closes: report completion. Do NOT start ledger work.

The execution agent must NOT:
- Skip TC-RR-001 and assume state/ can be safely deleted.
- Change V91 severity before state/ is resolved (risk: immediately blocks real repo).
- Edit README files without reading them fully first.
- Add the pre-commit hook before check_new_root_dirs.py is confirmed working.
- Close any parent taskcard while mandatory children are incomplete.
- Use `--no-verify` to bypass the pre-commit hook during verification.
- Treat "tests exist" as equivalent to "tests pass."
