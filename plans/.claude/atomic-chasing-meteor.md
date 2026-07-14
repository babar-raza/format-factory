# Gate 4 Prototype Coverage — Production-Grade Hardening
# AUTHORITATIVE PLAN: plans/.claude/atomic-chasing-meteor.md
# Mission: FF-G4-HARDEN-001 | Mode: MICRO_TASKCARDIZED_EXECUTION_READY

# ─────────────────────────────────────────────────────────────────────────────
# §0  PLAN AUTHORITY
# ─────────────────────────────────────────────────────────────────────────────

authoritative_plan: plans/.claude/atomic-chasing-meteor.md
artifact_role: primary_execution_plan
execution_authority: true
competing_plans: NONE
prior_plan_superseded: plans/.claude/atomic-stargazing-nest.md (FF-G4-BACKFILL-001, TERMINAL_CLOSED)
duplicate_risk: LOW — prior plan is terminal-closed; no competing active plan found

# ─────────────────────────────────────────────────────────────────────────────
# §1  PREFLIGHT RECORD
# ─────────────────────────────────────────────────────────────────────────────

## Preflight Record

repository_root: c:\Users\prora\OneDrive\Documents\GitHub\format-factory
branch: main
head_commit: af879e55 (feat(vwl): close vast-weaving-lampson machinery hardening plan)
git_status: several modified supervisor/reporting files; no conflicts on target task files
active_plan_path: plans/.claude/atomic-chasing-meteor.md
active_plan_title: Gate 4 Prototype Coverage — Production-Grade Hardening
plan_authority_source: user-created via plan mode
plan_line_count_pre_enhancement: 844
major_sections: 7 (Context, Root Cause Analysis, Structural Weaknesses, What to Preserve,
  Solution Design, Taskcards, Completion Criteria)
existing_taskcard_count: 7 (TC-G4H-001 through TC-G4H-007 — FLAT, no parent/child)
existing_taskcard_format: flat prose with embedded code — NOT hierarchical, NOT machine-state
existing_gates: "Done when:" prose per taskcard — NOT executable gate criteria
existing_state_vocabulary: NONE — no status fields on taskcards
existing_validation_model: per-taskcard prose ("Run: pytest ...") — not structured matrix
existing_evidence_model: "Evidence bundle at .local/evidences/gate4-harden-001/" — no contract
existing_execution_handoff: NONE
existing_dag: NONE
normalization_conventions: snake_case task IDs (TC-G4H-NNN), sequential numbering
naming_conventions: TC-G4H-NNN parent, TC-G4H-NNN-NN child, MS-G4H-NNN-NN-NN micro-step

section_processing_ledger:
  # See §8 for full ledger table
  sections_analyzed: 9
  actionables_extracted: 31
  broad_taskcards_requiring_split: 7 (all existing taskcards)
  investigation_items: 2 (matrix schema, STE parser function names)
  contradictions: 0
  stale_items: 0

# ─────────────────────────────────────────────────────────────────────────────
# §2  CONTEXT  [PRESERVED — do not alter]
# ─────────────────────────────────────────────────────────────────────────────

## Context

The prior backfill mission FF-G4-BACKFILL-001 (2026-07-01) delivered all 15 phases with final
verdict GATE4_COVERAGE_NORMALIZED_BACKFILLED_PROVEN_AND_IDEMPOTENT and all 8 counters at zero.
The structural artifacts — prototypes, evidence wrappers, registry blocks, validator tools —
are present and well-formed.

The problem is not "more artifacts needed." The problem is that the existing validation chain
only reaches as deep as declaration soundness. It confirms fields are present and paths exist on
disk. It does not confirm that parsers run, that corpus directories contain files, or that
evidence wrappers actually delegate to their declared sources. A Gate 4 "PASS" verdict today
means "these registry fields are populated and these file paths exist" — not "this parser
successfully processes the corpus."

This plan fixes the validation depth problem, closes two specific code bugs in the current
validator, and adds the pre-commit gate that prevents future drift. It is a targeted structural
fix, not a re-execution of the backfill.

# ─────────────────────────────────────────────────────────────────────────────
# §3  ROOT CAUSE ANALYSIS  [PRESERVED — do not alter]
# ─────────────────────────────────────────────────────────────────────────────

## Root Cause Analysis

### Symptoms

- The validator (`tools/gates/validate_gate4_evidence.py`) returns 25/25 PASS.
- The governance tests (`test_gate4_governance.py`) pass.
- Yet no test anywhere actually imports a parser and runs it against a corpus sample to confirm
  Gate 4 is behaviorally satisfied.
- Idempotency was "proven" by running the tools twice in the same agent session — not by a
  fresh clone + fresh run.

### Root Causes

**RC-1: Validation depth stops at file existence (core problem)**

The validator has two inspection depths:
1. Structural: checks that `gate_4.evidence_type` is present and is a known value.
2. File existence: checks that `prototype_path`, `delegated_source_path`, and individual test
   files exist on disk (for STANDALONE_PROTOTYPE and EVIDENCE_WRAPPER).

It never reaches:
3. Corpus existence: are the declared corpus directories non-empty?
4. Symbol existence: do the declared `delegated_symbols` actually exist in the delegated module?
5. Execution: does importing the wrapper and calling `compatibility_check()` succeed?
6. Behavioral: does the parser return a usable result on a corpus sample?

Gate 4 claims parsing feasibility. The current system validates that the claim is structurally
complete. It does not validate that the claim is true.

**RC-2: Corpus paths are never checked (code bug)**

In all three passing-evidence validators, corpus is checked for field presence only:
  `if not g4.get("corpus"): errors.append(...)`
The `_check_file_exists()` function is never called on corpus entries. A format can declare
`corpus: ["samples/by-format/does_not_exist/"]` and pass validation. Compare this to test files
(STANDALONE_PROTOTYPE, lines 55–58) where each entry is individually checked.

**RC-3: SOURCE_TRACK_EQUIVALENT test files not individually checked (code inconsistency)**

`_validate_standalone_prototype` iterates each test file and calls `_check_file_exists()` per
entry. `_validate_source_track_equivalent` only checks `if not g4.get("tests")` — it never
checks that the listed test files actually exist on disk. This inconsistency is a latent bug
that will surface when a source-track test file is renamed or moved.

**RC-4: BLOCKED_FORMATS hardcoded in governance test (brittleness)**

`test_gate4_governance.py` line 19: `BLOCKED_FORMATS = {"zpaq", "ora"}`
If a new format is added with `evidence_type: BLOCKED_BEFORE_GATE4` and `status: blocked`, and
then someone mistakenly sets `status: passed`, `test_blocked_formats_not_passed` will not catch
it because the new format is not in the hardcoded set.

**RC-5: No pre-commit gate on format-registry.yaml or prototypes/**

The existing `.pre-commit-config.yaml` has hooks for `src/python/`, capability registries,
source architecture, and PROJECT_STATUS.md — but nothing for `registry/format-registry.yaml`
or `prototypes/by-format/`. Adding a new format without a gate_4 block is not blocked at
commit time. Drift accumulates silently.

**RC-6: Evidence wrapper valid_sample_results are prose narratives (unverifiable claims)**
[DEFERRED — execution probe in TC-G4H-004 supersedes need for YAML snapshot cleanup]

**RC-7: Completion matrix is a manually-maintained parallel document**

`registry/format-completion-matrix.yaml` is maintained separately from `format-registry.yaml`.
No tool enforces that gate_4_status in the matrix matches gate_4.status in the registry.

### Structural Weaknesses

**SW-1: Idempotency was tested session-internally** — second run in same session is not
sufficient proof. True idempotency requires: fresh session + same tools → zero material changes.

**SW-2: Evidence execution is optional and peripheral** — csv_gate4_probe.py has
`compatibility_check()` and `probe()` but these are never called by the validator or governance
tests. They exist but are not in the enforcement chain.

**SW-3: SOURCE_TRACK_EQUIVALENT passes Gate 4 by category, not by execution** — addressed
by TC-G4H-004 (execution probe), not by creating new prototype parsers (would duplicate).

# ─────────────────────────────────────────────────────────────────────────────
# §4  WHAT TO PRESERVE  [PRESERVED — do not alter]
# ─────────────────────────────────────────────────────────────────────────────

## What to Preserve

- Evidence type taxonomy (STANDALONE_PROTOTYPE, EVIDENCE_WRAPPER, SOURCE_TRACK_EQUIVALENT,
  BLOCKED_BEFORE_GATE4, NOT_APPLICABLE) — correct, do not change
- Evidence wrapper pattern (csv_gate4_probe.py: probe(), probe_invalid(), compatibility_check())
  — correct model, extend enforcement to call these from the validator
- Prototype structure — standalone parsers in prototypes/by-format/ with READMEs
- Existing declaration-level validation (layers 1–2) — correct; extend, do not replace
- Existing 94+ prototype tests — correct; do not remove or modify existing assertions
- Skill registration (.supervisor/skill-registry.yaml entry)

# ─────────────────────────────────────────────────────────────────────────────
# §5  SOLUTION DESIGN  [PRESERVED + OPTIONS SUMMARY]
# ─────────────────────────────────────────────────────────────────────────────

## Solution Design

### Selected Approach: Surgical Depth Extension + Continuous Enforcement

Extend the validator from declaration-checking to execution-checking via an `--mode execute`
flag. Fix two code bugs (corpus existence, STE test-file consistency). De-hardcode BLOCKED_FORMATS.
Add pre-commit gate on registry and prototype files. Add completion-matrix sync check.

Options considered (all evaluated; this is the selected hybrid):

| Option | Coverage | Safety | Complexity | Selected |
|--------|----------|--------|------------|----------|
| A: Fix two bugs only (RC-2, RC-3) | partial | high | low | NO — leaves RC-1,4,5,7 open |
| B: Full execution probe + pre-commit (RC-1 through RC-7) | full | medium | high | PARTIAL |
| C: Redesign entire validation model | full | low | very high | NO — overkill |
| D: Hybrid (A + execution probe + pre-commit + matrix sync) | full | high | medium | YES |
| E: Status quo + additional governance tests | partial | high | low | NO — doesn't fix core depth |

Selected = Option D. Defers RC-6 (prose YAML cleanup) as cosmetic.

### Two-Mode Validator

**`--mode declaration`** (fast, ~1s): current structural + file-existence checks + RC-2/RC-3 fixes.
Used in pre-commit and quick local checks.

**`--mode execute`** (thorough, ~30–60s): declaration mode PLUS live probe execution.
- EVIDENCE_WRAPPER: import probe, call compatibility_check(), probe(valid_sample), probe_invalid()
- STANDALONE_PROTOTYPE: import parser via importlib, find + call parse function on valid sample
- SOURCE_TRACK_EQUIVALENT: import delegated parser, find + call parse function
- BLOCKED_BEFORE_GATE4: SKIPPED (no parser)
- Failures → PROBE_FAILED (non-exception); validator continues through all formats

# ─────────────────────────────────────────────────────────────────────────────
# §6  TRADEOFFS AND RISKS  [PRESERVED — do not alter]
# ─────────────────────────────────────────────────────────────────────────────

## Tradeoffs and Risks

**TC-G4H-004 (execution mode) — highest value, highest risk:**
- Probe imports in same process: misbehaving parser could corrupt sys.path.
  Mitigation: broad Exception catch → PROBE_FAILED; validator continues.
- SOURCE_TRACK_EQUIVALENT function discovery heuristic may miss class-based APIs.
  Mitigation: SKIPPED is acceptable; TC-G4H-004-01 includes investigation of actual API names.
- 30–60s runtime: too slow for pre-commit.
  Mitigation: pre-commit uses --mode declaration only.

**TC-G4H-005 (pre-commit) — blocks valid-work commits if corpus temporarily empty:**
  Mitigation: hook fires only when corpus path IS listed in registry (not on empty new formats).

**TC-G4H-002 (STE test file check) — may surface pre-existing stale test paths in registry:**
  Mitigation: treat as surfaced pre-existing bugs; fix registry entries, not the validator logic.

**SW-3 gap remains:** SOURCE_TRACK_EQUIVALENT still passes Gate 4 without Gate-4-specific
prototype. TC-G4H-004 execution probe provides sufficient behavioral evidence; creating 9
duplicate prototype parsers would violate INV-G4-003. Deferred by design.

# ─────────────────────────────────────────────────────────────────────────────
# §7  REQUIREMENTS INVENTORY
# ─────────────────────────────────────────────────────────────────────────────

## Requirements Inventory

| REQ-ID | RC/SW | Requirement | Addressed by |
|--------|-------|-------------|-------------|
| REQ-G4H-001 | RC-2 | Validator must verify corpus paths exist on disk and are non-empty | TC-G4H-001 |
| REQ-G4H-002 | RC-3 | SOURCE_TRACK_EQUIVALENT must individually check each test file exists | TC-G4H-002 |
| REQ-G4H-003 | RC-4 | BLOCKED_FORMATS detection must be derived from registry, never hardcoded | TC-G4H-003 |
| REQ-G4H-004 | RC-1,SW-2 | Validator must have --mode execute that runs live parser probes on corpus | TC-G4H-004 |
| REQ-G4H-005 | RC-5 | Pre-commit hook must block commits that break Gate 4 declarations | TC-G4H-005 |
| REQ-G4H-006 | RC-7 | Tool must verify completion matrix is consistent with registry | TC-G4H-006 |
| REQ-G4H-007 | SW-1 | Fresh verification run + attested evidence bundle must be produced | TC-G4H-007 |

# ─────────────────────────────────────────────────────────────────────────────
# §8  SECTION PROCESSING LEDGER
# ─────────────────────────────────────────────────────────────────────────────

## Section Processing Ledger

| Sec | Title | Actionables | Missing | Enhancement |
|-----|-------|-------------|---------|-------------|
| §2 | Context | 0 | — | PRESERVED |
| §3 | Root Cause Analysis (RC-1..7, SW-1..3) | 7 RCs addressed | — | PRESERVED; RC-6 deferred |
| §4 | What to Preserve | 0 | — | PRESERVED |
| §5 | Solution Design | 1 (mode split) | options analysis | EXPANDED with options table |
| §6 | Tradeoffs | 0 | — | PRESERVED |
| §7 | Requirements | 7 | REQ IDs missing | ADDED §7 requirements table |
| Old TC-G4H-001 | Corpus check bug fix | 5 child items | no decomp, no state | REPLACED with §9.1 |
| Old TC-G4H-002 | STE test file fix | 2 child items | no decomp, no state | REPLACED with §9.2 |
| Old TC-G4H-003 | BLOCKED_FORMATS | 3 child items | no decomp, no state | REPLACED with §9.3 |
| Old TC-G4H-004 | Execution probe | 11 child items | no decomp, too broad | REPLACED with §9.4 |
| Old TC-G4H-005 | Pre-commit | 2 child items | no state, no demo | REPLACED with §9.5 |
| Old TC-G4H-006 | Matrix sync | 4 child items (incl. invest.) | no schema invest. | REPLACED with §9.6 |
| Old TC-G4H-007 | Verification run | 8 child items | no state, no handoff | REPLACED with §9.7 |

# ─────────────────────────────────────────────────────────────────────────────
# §9  EXECUTION CONTROL — HIERARCHICAL TASKCARDS
# ─────────────────────────────────────────────────────────────────────────────
#
# Execution wave order (respects file ownership):
#   Wave 1 (no cross-dep): TC-G4H-003, TC-G4H-005 (different files, parallel-safe)
#   Wave 2 (same file sequence): TC-G4H-001 THEN TC-G4H-002 (both own validate_gate4_evidence.py)
#   Wave 3: TC-G4H-006 (depends on TC-G4H-003 + TC-G4H-005 closing)
#   Wave 4: TC-G4H-004 (depends on TC-G4H-001 + TC-G4H-002 closing)
#   Wave 5: TC-G4H-007 (depends on ALL prior taskcards closing)
# ─────────────────────────────────────────────────────────────────────────────

## §9.1  TC-G4H-001 — Fix Corpus Existence Verification

Parent Taskcard ID: TC-G4H-001
Title: Add corpus path existence and non-empty checks to Gate 4 validator
Type: PARENT
Status: READY
Source requirement: REQ-G4H-001 (RC-2)
Root cause addressed: Corpus field presence ≠ corpus paths exist on disk and are non-empty
Selected solution: Add _check_corpus_populated() helper; apply in all three passing-evidence validators

Objective: validate_gate4_evidence.py rejects any format whose corpus[] entries point to
non-existent or empty directories.

Scope:
  Allowed files: tools/gates/validate_gate4_evidence.py, tests/python/test_gate4_contract.py
  Forbidden files: ALL other files
  Forbidden: do not alter existing error messages for RC-3 (STE test files — that is TC-G4H-002)

Preserved behavior:
  - All existing validation logic for prototype_path, delegated_source_path, tests[] unchanged
  - No changes to evidence type taxonomy
  - Existing test assertions in test_gate4_contract.py must not regress

Dependencies: NONE (first wave — no prerequisite taskcards)
Child taskcards: TC-G4H-001-01, TC-G4H-001-02, TC-G4H-001-03, TC-G4H-001-04, TC-G4H-001-05

Parent acceptance criteria:
  - `python tools/gates/validate_gate4_evidence.py --mode declaration` still passes 25/25
  - A format with corpus pointing to nonexistent dir → FAIL result with "corpus" in error
  - A format with corpus pointing to empty dir → FAIL result with "corpus" in error
  - All existing test_gate4_contract.py tests still pass
  - New corpus-related tests pass

Evidence required:
  - pytest output for test_gate4_contract.py (all tests passing)
  - validator output showing 25/25 PASS on real registry
  - Two negative proof runs: nonexistent corpus path → FAIL; empty corpus dir → FAIL

Rollback: Revert changes to validate_gate4_evidence.py; tests were additive so no test rollback needed

Closeout: All 5 children CLOSED + parent acceptance criteria met + evidence captured

---

### TC-G4H-001-01 — Add _check_corpus_populated() helper function

Child Taskcard ID: TC-G4H-001-01
Parent Taskcard ID: TC-G4H-001
Title: Add _check_corpus_populated() helper after _check_file_exists() in validator
Type: CHILD
Status: TODO
Purpose: Provide the corpus existence + non-empty check used by the three validator functions

Scope:
  Allowed files: tools/gates/validate_gate4_evidence.py
  Forbidden: all other files; do not modify _check_file_exists()
  Target symbol: insert new function at line ~32 (after _check_file_exists, before _validate_source_track_equivalent)

Preconditions:
  - Read tools/gates/validate_gate4_evidence.py lines 28–33 to confirm exact insertion point
  - Confirm _check_file_exists() returns bool (not tuple)

Micro-steps:
  MS-G4H-001-01-01 [PENDING]: Read validate_gate4_evidence.py lines 1–45
    → Confirm: (a) _check_file_exists at line 28; (b) _validate_source_track_equivalent at line 34
    → Record exact insertion line for new function
  MS-G4H-001-01-02 [PENDING]: Insert _check_corpus_populated() after line 31 (end of _check_file_exists)
    → New function signature: def _check_corpus_populated(path_str: str | None) -> tuple[bool, str]
    → Logic: if None → (False, "empty path"); if not p.exists() → (False, "does not exist"); if p.is_dir() and not any(p.iterdir()) → (False, "empty dir"); else → (True, "")
    → File: tools/gates/validate_gate4_evidence.py
  MS-G4H-001-01-03 [PENDING]: Run `python -c "from tools.gates.validate_gate4_evidence import _check_corpus_populated; print('import ok')"` from repo root
    → Expected output: "import ok" (no ImportError)
  MS-G4H-001-01-04 [PENDING]: Capture output as micro-step evidence note

Acceptance checks:
  - _check_corpus_populated can be imported without error
  - Function returns (False, non-empty-string) for None input
  - Function returns (False, non-empty-string) for path that doesn't exist
  - Function returns (False, non-empty-string) for existing empty directory
  - Function returns (True, "") for directory with at least one file
Dependencies: NONE
Next valid task: TC-G4H-001-02

---

### TC-G4H-001-02 — Apply corpus check in _validate_source_track_equivalent

Child Taskcard ID: TC-G4H-001-02
Parent Taskcard ID: TC-G4H-001
Title: Replace corpus presence-only check with _check_corpus_populated loop in _validate_source_track_equivalent
Type: CHILD
Status: TODO

Scope:
  Allowed files: tools/gates/validate_gate4_evidence.py
  Forbidden: do not touch _validate_standalone_prototype or _validate_evidence_wrapper here
  Target: _validate_source_track_equivalent lines 40–43 (the `if not g4.get("corpus")` block)

Preconditions: TC-G4H-001-01 CLOSED (helper function exists in file)

Micro-steps:
  MS-G4H-001-02-01 [PENDING]: Read lines 34–44 of validate_gate4_evidence.py
    → Confirm exact location of `if not g4.get("corpus"):` in _validate_source_track_equivalent
  MS-G4H-001-02-02 [PENDING]: Replace the corpus check block (lines ~40–43) with:
    ```
    if not g4.get("corpus"):
        errors.append(f"{fid}: SOURCE_TRACK_EQUIVALENT missing corpus[]")
    else:
        for corpus_path in g4["corpus"]:
            ok, reason = _check_corpus_populated(corpus_path)
            if not ok:
                errors.append(f"{fid}: corpus check failed — {reason}")
    ```
  MS-G4H-001-02-03 [PENDING]: Run `python tools/gates/validate_gate4_evidence.py` on real registry
    → Expected: still 25/25 PASS (all current corpus paths are valid)
    → If any FAIL appears: investigate; do NOT remove the check — fix the registry entry

Acceptance checks: 25/25 PASS on real registry; corpus-absent format → error with "corpus"
Dependencies: TC-G4H-001-01
Next valid task: TC-G4H-001-03

---

### TC-G4H-001-03 — Apply corpus check in _validate_standalone_prototype

Child Taskcard ID: TC-G4H-001-03
Parent Taskcard ID: TC-G4H-001
Title: Replace corpus presence-only check with _check_corpus_populated loop in _validate_standalone_prototype
Type: CHILD
Status: TODO

Scope:
  Allowed files: tools/gates/validate_gate4_evidence.py
  Target: _validate_standalone_prototype — the `if not g4.get("corpus"):` block (~line 59)

Preconditions: TC-G4H-001-02 CLOSED

Micro-steps:
  MS-G4H-001-03-01 [PENDING]: Read _validate_standalone_prototype (lines 47–63) to find corpus block
  MS-G4H-001-03-02 [PENDING]: Apply same replacement pattern as TC-G4H-001-02 to this function
  MS-G4H-001-03-03 [PENDING]: Run validator on real registry → confirm still 25/25 PASS

Acceptance checks: 25/25 PASS; corpus-absent standalone → error
Dependencies: TC-G4H-001-02
Next valid task: TC-G4H-001-04

---

### TC-G4H-001-04 — Apply corpus check in _validate_evidence_wrapper

Child Taskcard ID: TC-G4H-001-04
Parent Taskcard ID: TC-G4H-001
Title: Replace corpus presence-only check with _check_corpus_populated loop in _validate_evidence_wrapper
Type: CHILD
Status: TODO

Scope:
  Allowed files: tools/gates/validate_gate4_evidence.py
  Target: _validate_evidence_wrapper — the `if not g4.get("corpus"):` block (~line 78)

Preconditions: TC-G4H-001-03 CLOSED

Micro-steps:
  MS-G4H-001-04-01 [PENDING]: Read _validate_evidence_wrapper (lines 66–80) to find corpus block
  MS-G4H-001-04-02 [PENDING]: Apply same replacement pattern
  MS-G4H-001-04-03 [PENDING]: Run validator on real registry → confirm still 25/25 PASS

Acceptance checks: 25/25 PASS; corpus-absent wrapper → error
Dependencies: TC-G4H-001-03
Next valid task: TC-G4H-001-05

---

### TC-G4H-001-05 — Add corpus existence regression tests

Child Taskcard ID: TC-G4H-001-05
Parent Taskcard ID: TC-G4H-001
Title: Add focused corpus-existence tests to test_gate4_contract.py
Type: CHILD
Status: TODO

Scope:
  Allowed files: tests/python/test_gate4_contract.py
  Forbidden: do not modify existing test functions; only ADD new functions at end of file

Preconditions: TC-G4H-001-04 CLOSED

Micro-steps:
  MS-G4H-001-05-01 [PENDING]: Read tests/python/test_gate4_contract.py to find last line
  MS-G4H-001-05-02 [PENDING]: Add test_corpus_nonexistent_path_rejected():
    → Create _fmt with corpus: ["samples/by-format/DOES_NOT_EXIST_G4H001/"]
    → call validate_gate4("csv", fmt) with EVIDENCE_WRAPPER evidence type + all required fields
    → assert _has_error(errors, "corpus")
  MS-G4H-001-05-03 [PENDING]: Add test_corpus_empty_dir_rejected() using tempfile.mkdtemp():
    → Create temp empty dir; pass its relative path (or absolute) as corpus
    → assert _has_error(errors, "corpus")
    → Use try/finally to clean up temp dir
  MS-G4H-001-05-04 [PENDING]: Run `.venv/Scripts/pytest tests/python/test_gate4_contract.py -v`
    → Expected: all existing tests pass + 2 new tests pass

Acceptance checks: All prior tests pass; 2 new corpus tests pass
Evidence: pytest output captured
Dependencies: TC-G4H-001-04
Next valid task: TC-G4H-001 parent close → TC-G4H-002

---

## §9.2  TC-G4H-002 — Fix SOURCE_TRACK_EQUIVALENT Test File Consistency

Parent Taskcard ID: TC-G4H-002
Title: Make _validate_source_track_equivalent check each test file exists on disk
Type: PARENT
Status: READY
Source requirement: REQ-G4H-002 (RC-3)
Root cause: _validate_source_track_equivalent only checks list is non-empty; does not iterate files

Scope:
  Allowed files: tools/gates/validate_gate4_evidence.py, tests/python/test_gate4_contract.py
  Forbidden: do not alter _validate_standalone_prototype (already correct) or _validate_evidence_wrapper

WARNING: TC-G4H-002 MUST execute AFTER TC-G4H-001 (both own validate_gate4_evidence.py).
  Apply TC-G4H-002 edits to the ALREADY-MODIFIED file from TC-G4H-001, not a fresh copy.

Dependencies: TC-G4H-001 CLOSED
Child taskcards: TC-G4H-002-01, TC-G4H-002-02

Parent acceptance criteria:
  - If a SOURCE_TRACK_EQUIVALENT format lists a test file that doesn't exist → FAIL with "does not exist on disk"
  - Real registry: 25/25 PASS (all currently listed STE test files exist)
  - New test for missing STE test file passes

Rollback: Revert only the STE test-iteration change added in TC-G4H-002-01; TC-G4H-001 changes stay
Closeout: Both children CLOSED + parent acceptance criteria met

---

### TC-G4H-002-01 — Add per-file test existence check to _validate_source_track_equivalent

Child Taskcard ID: TC-G4H-002-01
Parent Taskcard ID: TC-G4H-002
Title: Replace `if not g4.get("tests")` with iterating loop in _validate_source_track_equivalent
Type: CHILD
Status: TODO

Preconditions: TC-G4H-001 CLOSED (file already modified; working on post-001 state)

Micro-steps:
  MS-G4H-002-01-01 [PENDING]: Read the current _validate_source_track_equivalent in the MODIFIED file
    → Confirm: corpus check is now the loop pattern from TC-G4H-001-02
    → Locate the `if not g4.get("tests"):` line
  MS-G4H-002-01-02 [PENDING]: Replace the tests block with:
    ```
    if not g4.get("tests"):
        errors.append(f"{fid}: SOURCE_TRACK_EQUIVALENT missing tests[]")
    else:
        for t in g4["tests"]:
            if not _check_file_exists(t):
                errors.append(f"{fid}: test '{t}' does not exist on disk")
    ```
  MS-G4H-002-01-03 [PENDING]: Run `python tools/gates/validate_gate4_evidence.py` on real registry
    → Expected: 25/25 PASS (all STE test files currently exist)
    → If any FAIL: do NOT remove the check — it has surfaced a real pre-existing stale test path;
      record the failing format ID and fix that format's registry entry before proceeding

Acceptance checks: 25/25 PASS on real registry; missing-test format → error with "does not exist on disk"
Dependencies: TC-G4H-001 CLOSED
Next valid task: TC-G4H-002-02

---

### TC-G4H-002-02 — Add STE missing-test-file regression test

Child Taskcard ID: TC-G4H-002-02
Parent Taskcard ID: TC-G4H-002
Title: Add test_source_track_equivalent_missing_test_file_rejected to test_gate4_contract.py
Type: CHILD
Status: TODO

Preconditions: TC-G4H-002-01 CLOSED

Micro-steps:
  MS-G4H-002-02-01 [PENDING]: Add at end of test_gate4_contract.py:
    ```python
    def test_source_track_equivalent_missing_test_file_rejected():
        fmt = _fmt("ods", {
            "status": "passed",
            "evidence_type": "SOURCE_TRACK_EQUIVALENT",
            "delegated_source_path": "src/python/ods/ods_parser.py",
            "corpus": ["samples/by-format/ods/"],
            "tests": ["tests/python/ods/this_file_does_not_exist_tc_g4h002.py"],
        })
        errors = validate_gate4("ods", fmt)
        assert _has_error(errors, "does not exist on disk")
    ```
  MS-G4H-002-02-02 [PENDING]: Run `.venv/Scripts/pytest tests/python/test_gate4_contract.py -v`
    → All prior tests pass; new test passes

Acceptance checks: pytest shows new test PASS; no regressions
Dependencies: TC-G4H-002-01
Next valid task: TC-G4H-002 parent close → TC-G4H-004 (depends on 001+002)

---

## §9.3  TC-G4H-003 — De-hardcode BLOCKED_FORMATS in Governance Test

Parent Taskcard ID: TC-G4H-003
Title: Replace hardcoded BLOCKED_FORMATS set with registry-derived detection in test_gate4_governance.py
Type: PARENT
Status: READY
Source requirement: REQ-G4H-003 (RC-4)

Scope:
  Allowed files: tests/python/test_gate4_governance.py
  Forbidden: do not modify validate_gate4_evidence.py or format-registry.yaml

Dependencies: NONE (independent file — wave 1 parallel with TC-G4H-005)
Child taskcards: TC-G4H-003-01, TC-G4H-003-02, TC-G4H-003-03

Parent acceptance criteria:
  - No `BLOCKED_FORMATS = {...}` static set anywhere in test_gate4_governance.py
  - test_blocked_formats_not_passed uses _get_blocked_formats(data)
  - New test_blocked_formats_derived_from_registry passes and asserts zpaq, ora in set
  - Adding a new blocked format to registry is automatically tested without code change

Rollback: Revert test_gate4_governance.py to prior state (only additive changes)
Closeout: All 3 children CLOSED + governance tests pass

---

### TC-G4H-003-01 — Add _get_blocked_formats() to test_gate4_governance.py

Child Taskcard ID: TC-G4H-003-01
Parent Taskcard ID: TC-G4H-003
Title: Add _get_blocked_formats(data) function that reads BLOCKED_BEFORE_GATE4 formats from registry
Type: CHILD
Status: TODO

Micro-steps:
  MS-G4H-003-01-01 [PENDING]: Read tests/python/test_gate4_governance.py lines 1–30
    → Note exact location of `BLOCKED_FORMATS = {"zpaq", "ora"}` (line 19)
    → Note that _load_registry() is defined at line 29
  MS-G4H-003-01-02 [PENDING]: After _load_registry() definition (line ~31), insert:
    ```python
    def _get_blocked_formats(data: dict) -> set[str]:
        """Derive blocked formats from registry — formats with BLOCKED_BEFORE_GATE4."""
        blocked = set()
        for fmt in data["formats"]:
            g4 = fmt.get("gates", {}).get("gate_4", {})
            if g4 and g4.get("evidence_type") == "BLOCKED_BEFORE_GATE4":
                blocked.add(fmt["format_id"])
        return blocked
    ```
  MS-G4H-003-01-03 [PENDING]: Remove or comment out `BLOCKED_FORMATS = {"zpaq", "ora"}` on line 19
    → Do NOT remove yet if test_blocked_formats_not_passed still references it — handle in 003-02

Acceptance checks: File imports without error; _get_blocked_formats can be called
Dependencies: NONE
Next valid task: TC-G4H-003-02

---

### TC-G4H-003-02 — Update test_blocked_formats_not_passed to use dynamic set

Child Taskcard ID: TC-G4H-003-02
Parent Taskcard ID: TC-G4H-003
Title: Replace static BLOCKED_FORMATS reference with _get_blocked_formats(data) call in existing test
Type: CHILD
Status: TODO

Preconditions: TC-G4H-003-01 CLOSED

Micro-steps:
  MS-G4H-003-02-01 [PENDING]: Read test_blocked_formats_not_passed (lines ~78–89)
    → Note that it currently iterates `BLOCKED_FORMATS` from the module-level set
  MS-G4H-003-02-02 [PENDING]: Modify the test to:
    ```python
    def test_blocked_formats_not_passed():
        data = _load_registry()
        blocked = _get_blocked_formats(data)
        false_passes = []
        for fmt in data["formats"]:
            fid = fmt["format_id"]
            if fid not in blocked:
                continue
            g4 = fmt.get("gates", {}).get("gate_4", {})
            if g4 and g4.get("status") == "passed":
                false_passes.append(fid)
        assert false_passes == [], f"Blocked formats incorrectly marked passed: {false_passes}"
    ```
  MS-G4H-003-02-03 [PENDING]: Now remove the `BLOCKED_FORMATS = {"zpaq", "ora"}` line (it is no longer used)
  MS-G4H-003-02-04 [PENDING]: Run `.venv/Scripts/pytest tests/python/test_gate4_governance.py -v`
    → All existing tests pass

Acceptance checks: No hardcoded set remains; existing test passes
Dependencies: TC-G4H-003-01
Next valid task: TC-G4H-003-03

---

### TC-G4H-003-03 — Add test_blocked_formats_derived_from_registry

Child Taskcard ID: TC-G4H-003-03
Parent Taskcard ID: TC-G4H-003
Title: Add regression guard test asserting zpaq/ora always appear as blocked
Type: CHILD
Status: TODO

Preconditions: TC-G4H-003-02 CLOSED

Micro-steps:
  MS-G4H-003-03-01 [PENDING]: Append to test_gate4_governance.py:
    ```python
    def test_blocked_formats_derived_from_registry():
        """Registry-derived blocked set must always include zpaq and ora (regression guard)."""
        data = _load_registry()
        blocked = _get_blocked_formats(data)
        assert "zpaq" in blocked, "zpaq must remain BLOCKED_BEFORE_GATE4"
        assert "ora" in blocked, "ora must remain BLOCKED_BEFORE_GATE4"
        for fmt in data["formats"]:
            fid = fmt["format_id"]
            if fid not in blocked:
                continue
            g4 = fmt.get("gates", {}).get("gate_4", {})
            assert g4.get("next_gate"), f"{fid}: blocked format missing next_gate"
            assert g4.get("blocker"), f"{fid}: blocked format missing blocker"
    ```
  MS-G4H-003-03-02 [PENDING]: Run `.venv/Scripts/pytest tests/python/test_gate4_governance.py -v`
    → All tests pass including new one

Acceptance checks: New test passes; zpaq and ora confirmed blocked in real registry
Evidence: pytest -v output
Dependencies: TC-G4H-003-02
Next valid task: TC-G4H-003 parent close → TC-G4H-006 (depends on 003+005)

---

## §9.4  TC-G4H-004 — Add Execution Probe Mode to Validator

Parent Taskcard ID: TC-G4H-004
Title: Create gate4_execution_probe.py and integrate --mode execute into validate_gate4_evidence.py
Type: PARENT
Status: READY
Source requirement: REQ-G4H-004 (RC-1, SW-2)
Root cause: Validator never imports or calls any parser; Gate 4 PASS is a declaration, not execution

CRITICAL DEPENDENCY: TC-G4H-001 AND TC-G4H-002 must both be CLOSED before TC-G4H-004.
Rationale: TC-G4H-004-06 modifies validate_gate4_evidence.py; must not conflict with TC-G4H-001/002.

Scope:
  Allowed files (new): tools/gates/gate4_execution_probe.py, tests/python/test_gate4_execution_probe.py
  Allowed files (modify): tools/gates/validate_gate4_evidence.py
  Forbidden: do not modify existing probe files (csv_gate4_probe.py etc.), existing validators, or tests

Dependencies: TC-G4H-001 CLOSED, TC-G4H-002 CLOSED
Child taskcards:
  TC-G4H-004-01: INVESTIGATION + skeleton (ProbeResult, _first_corpus_sample)
  TC-G4H-004-02: Implement probe_evidence_wrapper()
  TC-G4H-004-03: Implement probe_standalone_prototype()
  TC-G4H-004-04: Implement probe_source_track_equivalent()
  TC-G4H-004-05: Implement run_all_probes()
  TC-G4H-004-06: Add --mode flag integration to validate_gate4_evidence.py
  TC-G4H-004-07: Create test_gate4_execution_probe.py + EVIDENCE_WRAPPER test (CSV)
  TC-G4H-004-08: Add STANDALONE_PROTOTYPE probe tests (XPM, PAM)
  TC-G4H-004-09: Add SOURCE_TRACK_EQUIVALENT probe test (ODS)
  TC-G4H-004-10: Add negative control tests

Parent acceptance criteria:
  - `python tools/gates/validate_gate4_evidence.py --mode declaration` → 25/25 PASS (unchanged)
  - `python tools/gates/validate_gate4_evidence.py --mode execute` → zero PROBE_FAILED
    (CSV/TSV/NDJSON/TOML → PASS via wrapper; FODS/FODT/XPM/PAM/etc. → PASS via standalone;
     ODS/ODT/QOI/etc. → PASS or SKIPPED via source-track; ZPAQ/ORA → SKIPPED)
  - test_gate4_execution_probe.py all tests pass

Rollback: Delete tools/gates/gate4_execution_probe.py; revert validate_gate4_evidence.py to pre-004 state

---

### TC-G4H-004-01 — INVESTIGATION + Create gate4_execution_probe.py skeleton

Child Taskcard ID: TC-G4H-004-01
Parent Taskcard ID: TC-G4H-004
Title: Investigate parser API names in prototype directories; create skeleton with ProbeResult + _first_corpus_sample
Type: CHILD (INVESTIGATION + IMPLEMENTATION)
Status: TODO

INVESTIGATION REQUIREMENT: Before implementing probe_standalone_prototype() and
probe_source_track_equivalent(), the actual parser function names in each prototype directory
and src/python/ package must be confirmed. The current plan uses naming heuristics
(parse_{fid}, probe_{fid}, parse, load, decode) — these must be verified against real files.

Scope:
  Read-only investigation: prototypes/by-format/*/
  Read-only investigation: src/python/{ods,odt,qoi,xcf,dif,ppm,pgm,pbm,sylk}/
  New file creation: tools/gates/gate4_execution_probe.py

Micro-steps:
  MS-G4H-004-01-01 [PENDING]: INVESTIGATE — for each STANDALONE_PROTOTYPE format, record:
    - prototype directory path
    - parser file name (e.g., fods_parser.py, xpm_parser.py, pam_parser.py, zst_probe.py?)
    - primary callable name (e.g., parse_fods, parse_xpm, probe_zst?)
    Action: `ls prototypes/by-format/{fods,fodt,zst,fodp,fodg,gnumeric,abw,xpm,pam}/`
    Record findings in child taskcard evidence note
  MS-G4H-004-01-02 [PENDING]: INVESTIGATE — for each SOURCE_TRACK_EQUIVALENT format, record:
    - delegated parser file name
    - primary callable name
    Action: `grep -n "^def " src/python/ods/ods_parser.py` (and same for odt/qoi/xcf/dif/ppm/pgm/pbm/sylk)
    Record findings; identify any class-based APIs (→ will return SKIPPED, not PROBE_FAILED)
  MS-G4H-004-01-03 [PENDING]: Document findings table:
    Format | Parser file | Callable name | Expected probe outcome
    Update the heuristic function-name list in probe_standalone_prototype() and
    probe_source_track_equivalent() if needed based on actual API names
  MS-G4H-004-01-04 [PENDING]: Create tools/gates/gate4_execution_probe.py with:
    - Module docstring (references TC-G4H-004, FF-G4-HARDEN-001)
    - Imports: __future__, importlib.util, sys, dataclasses, pathlib, typing
    - REPO constant: Path(__file__).resolve().parents[2]
    - ProbeResult dataclass with fields: format_id: str, evidence_type: str, status: str, detail: str = ""
    - _first_corpus_sample(corpus_paths, repo) function — finds first non-invalid file in corpus dirs
    [NOTE: probe functions added in TC-G4H-004-02 through TC-G4H-004-05]
  MS-G4H-004-01-05 [PENDING]: Verify: `python -c "from tools.gates.gate4_execution_probe import ProbeResult, _first_corpus_sample; print('ok')"`
    → Expected: "ok"

Investigation output required:
  - Table of format → callable name mapping for all 23 passing formats
  - List of formats that will return SKIPPED (class-based APIs)
  - Confirmed heuristic order for parse function discovery

Acceptance checks: File creates without error; ProbeResult importable; investigation table recorded
Dependencies: TC-G4H-001 CLOSED, TC-G4H-002 CLOSED
Next valid task: TC-G4H-004-02

---

### TC-G4H-004-02 — Implement probe_evidence_wrapper()

Child Taskcard ID: TC-G4H-004-02
Parent Taskcard ID: TC-G4H-004
Title: Add probe_evidence_wrapper() to gate4_execution_probe.py
Type: CHILD
Status: TODO

Preconditions: TC-G4H-004-01 CLOSED

Micro-steps:
  MS-G4H-004-02-01 [PENDING]: Append probe_evidence_wrapper(fid, g4) to gate4_execution_probe.py
    Logic: (1) find probe file via f"{fid}_gate4_probe.py" in proto_path, fallback to glob *gate4_probe.py
           (2) importlib.util.spec_from_file_location + exec_module; catch → PROBE_FAILED
           (3) call compatibility_check() if exists; catch → PROBE_FAILED
           (4) call probe(first_corpus_sample) if exists; assert returns dict; catch → PROBE_FAILED
           (5) call probe_invalid() if exists; catch AssertionError → PROBE_FAILED; other exc → pass
           (6) return ProbeResult(fid, "EVIDENCE_WRAPPER", "PASS")
  MS-G4H-004-02-02 [PENDING]: Smoke test: `python -c "from tools.gates.gate4_execution_probe import probe_evidence_wrapper; print('ok')"`
  MS-G4H-004-02-03 [PENDING]: Manual probe test for CSV:
    `python -c "import yaml; from tools.gates.gate4_execution_probe import probe_evidence_wrapper; from pathlib import Path; reg=yaml.safe_load(Path('registry/format-registry.yaml').read_text()); csv_fmt=[f for f in reg['formats'] if f['format_id']=='csv'][0]; g4=csv_fmt.get('gates',{}).get('gate_4',{}); r=probe_evidence_wrapper('csv',g4); print(r)"`
    → Expected: ProbeResult(format_id='csv', evidence_type='EVIDENCE_WRAPPER', status='PASS', detail='')

Acceptance checks: probe_evidence_wrapper('csv', g4) returns PASS; import succeeds
Dependencies: TC-G4H-004-01
Next valid task: TC-G4H-004-03

---

### TC-G4H-004-03 — Implement probe_standalone_prototype()

Child Taskcard ID: TC-G4H-004-03
Parent Taskcard ID: TC-G4H-004
Title: Add probe_standalone_prototype() using investigation findings from TC-G4H-004-01
Type: CHILD
Status: TODO

Preconditions: TC-G4H-004-02 CLOSED; investigation findings from TC-G4H-004-01 recorded

Micro-steps:
  MS-G4H-004-03-01 [PENDING]: Consult TC-G4H-004-01 investigation findings for prototype callable names
  MS-G4H-004-03-02 [PENDING]: Append probe_standalone_prototype(fid, g4) to gate4_execution_probe.py
    Logic: (1) find first corpus sample; (2) find parser file via glob (use actual names from investigation);
           (3) add proto_dir to sys.path temporarily; (4) importlib exec; catch → PROBE_FAILED;
           (5) find parse function using heuristic list confirmed by investigation;
           (6) call parse_fn(sample); check result is not None and no error key; catch → PROBE_FAILED;
           (7) return PASS
    IMPORTANT: The function-name heuristic order must reflect investigation findings. If zst uses
    probe_zst() or a different name, include that explicitly before generic fallbacks.
  MS-G4H-004-03-03 [PENDING]: Manual probe test for XPM:
    (Similar command as TC-G4H-004-02-03 but for 'xpm')
    → Expected: ProbeResult status='PASS'
  MS-G4H-004-03-04 [PENDING]: Manual probe test for PAM:
    → Expected: ProbeResult status='PASS'

Acceptance checks: XPM and PAM return PASS; import succeeds
Dependencies: TC-G4H-004-02
Next valid task: TC-G4H-004-04

---

### TC-G4H-004-04 — Implement probe_source_track_equivalent()

Child Taskcard ID: TC-G4H-004-04
Parent Taskcard ID: TC-G4H-004
Title: Add probe_source_track_equivalent() using investigation findings from TC-G4H-004-01
Type: CHILD
Status: TODO

Preconditions: TC-G4H-004-03 CLOSED

Micro-steps:
  MS-G4H-004-04-01 [PENDING]: Consult TC-G4H-004-01 for STE callable names and class-based API formats
  MS-G4H-004-04-02 [PENDING]: Append probe_source_track_equivalent(fid, g4) to gate4_execution_probe.py
    Logic: (1) get delegated path; (2) add src/python to sys.path temporarily;
           (3) importlib exec delegated module; catch → PROBE_FAILED;
           (4) find parse function using confirmed heuristic;
           (5) if no function found → SKIPPED (class-based API); do NOT fail;
           (6) call parse_fn(first_corpus_sample); result not None → PASS; else PROBE_FAILED
  MS-G4H-004-04-03 [PENDING]: Manual probe test for ODS:
    → Expected: ProbeResult status='PASS' OR 'SKIPPED' (either is acceptable — PROBE_FAILED is not)

Acceptance checks: ODS → PASS or SKIPPED (not PROBE_FAILED); import succeeds
Dependencies: TC-G4H-004-03
Next valid task: TC-G4H-004-05

---

### TC-G4H-004-05 — Implement run_all_probes()

Child Taskcard ID: TC-G4H-004-05
Parent Taskcard ID: TC-G4H-004
Title: Add run_all_probes() dispatcher to gate4_execution_probe.py
Type: CHILD
Status: TODO

Preconditions: TC-G4H-004-04 CLOSED

Micro-steps:
  MS-G4H-004-05-01 [PENDING]: Append run_all_probes(formats: list[dict]) -> list[ProbeResult]:
    For each format: if status != "passed" → SKIPPED; elif EVIDENCE_WRAPPER → probe_evidence_wrapper;
    elif STANDALONE_PROTOTYPE → probe_standalone_prototype; elif SOURCE_TRACK_EQUIVALENT →
    probe_source_track_equivalent; else → SKIPPED
  MS-G4H-004-05-02 [PENDING]: Manual full-registry probe run:
    `python -c "import yaml; from tools.gates.gate4_execution_probe import run_all_probes; from pathlib import Path; reg=yaml.safe_load(Path('registry/format-registry.yaml').read_text()); results=run_all_probes(reg['formats']); failures=[r for r in results if r.status=='PROBE_FAILED']; print(f'{len(failures)} PROBE_FAILED'); [print(r) for r in failures]"`
    → Expected: 0 PROBE_FAILED

Acceptance checks: 0 PROBE_FAILED on real registry
Dependencies: TC-G4H-004-04
Next valid task: TC-G4H-004-06

---

### TC-G4H-004-06 — Add --mode flag to validate_gate4_evidence.py

Child Taskcard ID: TC-G4H-004-06
Parent Taskcard ID: TC-G4H-004
Title: Integrate --mode declaration|execute into validate_gate4_evidence.py main()
Type: CHILD
Status: TODO

Preconditions: TC-G4H-004-05 CLOSED (probe module complete); TC-G4H-001 CLOSED; TC-G4H-002 CLOSED

Micro-steps:
  MS-G4H-004-06-01 [PENDING]: Read validate_gate4_evidence.py main() (lines 144–193)
    → Confirm current argv handling (currently: no argparse, argv parameter is unused)
  MS-G4H-004-06-02 [PENDING]: Wrap existing main body with argparse:
    - Add `import argparse` at top of main()
    - Add `parser.add_argument("--mode", choices=["declaration","execute"], default="declaration")`
    - After `args = parser.parse_args(argv)`, run existing declaration logic as before
    - After declaration logic, if `args.mode == "execute"`: import run_all_probes, run probes,
      print probe table, return 1 if any PROBE_FAILED
    - Keep existing return code: 0 if not all_errors else 1 (declaration always checked)
  MS-G4H-004-06-03 [PENDING]: Run `python tools/gates/validate_gate4_evidence.py --mode declaration`
    → Expected: 25/25 PASS (unchanged behavior)
  MS-G4H-004-06-04 [PENDING]: Run `python tools/gates/validate_gate4_evidence.py --mode execute`
    → Expected: 25/25 PASS on declarations + 0 PROBE_FAILED on probes
  MS-G4H-004-06-05 [PENDING]: Run `python tools/gates/validate_gate4_evidence.py` (no flag)
    → Expected: behaves as --mode declaration (default)

Acceptance checks: both modes work; no-flag defaults to declaration; exit code 0 on clean registry
Dependencies: TC-G4H-004-05 CLOSED; TC-G4H-001 CLOSED; TC-G4H-002 CLOSED
Next valid task: TC-G4H-004-07

---

### TC-G4H-004-07 — Create test_gate4_execution_probe.py + EVIDENCE_WRAPPER tests

Child Taskcard ID: TC-G4H-004-07
Parent Taskcard ID: TC-G4H-004
Title: Create tests/python/test_gate4_execution_probe.py with CSV evidence wrapper probe test
Type: CHILD
Status: TODO

Preconditions: TC-G4H-004-06 CLOSED

Micro-steps:
  MS-G4H-004-07-01 [PENDING]: Create tests/python/test_gate4_execution_probe.py with:
    - Module docstring, imports (yaml, Path, sys, pytest)
    - REPO_ROOT constant
    - _load_g4_block(fid) helper: loads registry and returns gate_4 block for given format_id
  MS-G4H-004-07-02 [PENDING]: Add test_probe_evidence_wrapper_csv():
    ```python
    def test_probe_evidence_wrapper_csv():
        from tools.gates.gate4_execution_probe import probe_evidence_wrapper
        g4 = _load_g4_block("csv")
        result = probe_evidence_wrapper("csv", g4)
        assert result.status == "PASS", f"CSV wrapper probe failed: {result.detail}"
    ```
  MS-G4H-004-07-03 [PENDING]: Add test_probe_evidence_wrapper_tsv() (same pattern for TSV)
  MS-G4H-004-07-04 [PENDING]: Run `.venv/Scripts/pytest tests/python/test_gate4_execution_probe.py -v`
    → Both tests pass

Acceptance checks: CSV and TSV wrapper probes return PASS
Dependencies: TC-G4H-004-06
Next valid task: TC-G4H-004-08

---

### TC-G4H-004-08 — Add STANDALONE_PROTOTYPE probe tests (XPM, PAM)

Child Taskcard ID: TC-G4H-004-08
Parent Taskcard ID: TC-G4H-004
Title: Add probe_standalone_prototype tests for XPM and PAM
Type: CHILD
Status: TODO

Preconditions: TC-G4H-004-07 CLOSED

Micro-steps:
  MS-G4H-004-08-01 [PENDING]: Add test_probe_standalone_prototype_xpm():
    ```python
    def test_probe_standalone_prototype_xpm():
        from tools.gates.gate4_execution_probe import probe_standalone_prototype
        g4 = _load_g4_block("xpm")
        result = probe_standalone_prototype("xpm", g4)
        assert result.status == "PASS", f"XPM standalone probe failed: {result.detail}"
    ```
  MS-G4H-004-08-02 [PENDING]: Add test_probe_standalone_prototype_pam() (same for PAM)
  MS-G4H-004-08-03 [PENDING]: Run `.venv/Scripts/pytest tests/python/test_gate4_execution_probe.py -v`
    → 4 tests pass (CSV, TSV, XPM, PAM)

Dependencies: TC-G4H-004-07
Next valid task: TC-G4H-004-09

---

### TC-G4H-004-09 — Add SOURCE_TRACK_EQUIVALENT probe test (ODS)

Child Taskcard ID: TC-G4H-004-09
Parent Taskcard ID: TC-G4H-004
Title: Add probe_source_track_equivalent test for ODS (PASS or SKIPPED acceptable)
Type: CHILD
Status: TODO

Preconditions: TC-G4H-004-08 CLOSED

Micro-steps:
  MS-G4H-004-09-01 [PENDING]: Add test_probe_source_track_equivalent_ods():
    ```python
    def test_probe_source_track_equivalent_ods():
        from tools.gates.gate4_execution_probe import probe_source_track_equivalent
        g4 = _load_g4_block("ods")
        result = probe_source_track_equivalent("ods", g4)
        # PASS or SKIPPED (class-based API) — never PROBE_FAILED
        assert result.status in ("PASS", "SKIPPED"), \
            f"ODS source-track probe unexpectedly failed: {result.detail}"
    ```
  MS-G4H-004-09-02 [PENDING]: Run pytest → 5 tests pass

Dependencies: TC-G4H-004-08
Next valid task: TC-G4H-004-10

---

### TC-G4H-004-10 — Add negative control tests

Child Taskcard ID: TC-G4H-004-10
Parent Taskcard ID: TC-G4H-004
Title: Add probe negative control tests: missing corpus, missing probe file, blocked format skipped
Type: CHILD
Status: TODO

Preconditions: TC-G4H-004-09 CLOSED

Micro-steps:
  MS-G4H-004-10-01 [PENDING]: Add test_probe_fails_on_missing_corpus_sample():
    - Construct synthetic g4 dict for STANDALONE_PROTOTYPE with corpus: ["samples/by-format/DOES_NOT_EXIST_G4H004/"]
    - result = probe_standalone_prototype("xpm", synthetic_g4)
    - assert result.status == "PROBE_FAILED"
  MS-G4H-004-10-02 [PENDING]: Add test_probe_skipped_for_blocked_format():
    - Construct g4 with evidence_type="BLOCKED_BEFORE_GATE4", status="blocked"
    - run_all_probes([{"format_id":"zpaq","gates":{"gate_4":g4}}])
    - assert result[0].status == "SKIPPED"
  MS-G4H-004-10-03 [PENDING]: Run pytest → all tests pass including 2 new negatives

Acceptance checks: Negative controls confirm probes reject bad inputs; blocked → SKIPPED
Dependencies: TC-G4H-004-09
Next valid task: TC-G4H-004 parent close → TC-G4H-007

---

## §9.5  TC-G4H-005 — Add Pre-Commit Gate

Parent Taskcard ID: TC-G4H-005
Title: Add gate4-evidence-validator hook to .pre-commit-config.yaml
Type: PARENT
Status: READY
Source requirement: REQ-G4H-005 (RC-5)

Scope:
  Allowed files: .pre-commit-config.yaml
  Forbidden: do not modify tools/ or tests/ in this taskcard

Dependencies: NONE (wave 1 independent; but note TC-G4H-006-04 will later modify this hook)
Child taskcards: TC-G4H-005-01, TC-G4H-005-02

Parent acceptance criteria:
  - New hook appears in .pre-commit-config.yaml under `repo: local`
  - Hook fires on changes to registry/format-registry.yaml
  - A commit that adds a format without gate_4 block is blocked

Rollback: Remove the added hook entry from .pre-commit-config.yaml
Closeout: Both children CLOSED; hook confirmed blocking

---

### TC-G4H-005-01 — Add gate4-evidence-validator hook

Child Taskcard ID: TC-G4H-005-01
Parent Taskcard ID: TC-G4H-005
Title: Add gate4-evidence-validator pre-commit hook to .pre-commit-config.yaml
Type: CHILD
Status: TODO

Micro-steps:
  MS-G4H-005-01-01 [PENDING]: Read .pre-commit-config.yaml (67 lines) to find last hook in `repo: local`
    → Confirm last hook ends around line 66
    → Note indentation style (2 spaces, 6 spaces for hook content)
  MS-G4H-005-01-02 [PENDING]: Append new hook after the last existing local hook (after line 66):
    ```yaml
      - id: gate4-evidence-validator
        name: Gate 4 evidence validator (declaration mode)
        entry: python tools/gates/validate_gate4_evidence.py --mode declaration
        language: system
        pass_filenames: false
        always_run: false
        files: >
          (?x)^(
            registry/format-registry\.yaml|
            registry/format-completion-matrix\.yaml|
            prototypes/by-format/.*|
            samples/by-format/.*
          )$
        stages: [pre-commit]
    ```
  MS-G4H-005-01-03 [PENDING]: Verify YAML syntax: `python -c "import yaml; yaml.safe_load(open('.pre-commit-config.yaml').read()); print('valid yaml')"`

Acceptance checks: .pre-commit-config.yaml parses as valid YAML; hook entry present
Dependencies: NONE
Next valid task: TC-G4H-005-02

---

### TC-G4H-005-02 — Verify hook blocks malformed registry commit

Child Taskcard ID: TC-G4H-005-02
Parent Taskcard ID: TC-G4H-005
Title: Demonstrate that the pre-commit hook fires and blocks a format missing gate_4 block
Type: CHILD
Status: TODO

Preconditions: TC-G4H-005-01 CLOSED; TC-G4H-001 + TC-G4H-002 CLOSED (validator has corpus fixes)

Micro-steps:
  MS-G4H-005-02-01 [PENDING]: In registry/format-registry.yaml, temporarily append a minimal format
    entry WITHOUT a gate_4 block (e.g., format_id: test-format-g4h005, under formats list)
  MS-G4H-005-02-02 [PENDING]: Stage the change: `git add registry/format-registry.yaml`
  MS-G4H-005-02-03 [PENDING]: Run pre-commit on staged file:
    `pre-commit run gate4-evidence-validator --files registry/format-registry.yaml`
    → Expected: exit code 1; output contains "gate_4 block ABSENT" or similar error for test-format-g4h005
  MS-G4H-005-02-04 [PENDING]: Revert the test change immediately:
    `git restore registry/format-registry.yaml`
  MS-G4H-005-02-05 [PENDING]: Run `python tools/gates/validate_gate4_evidence.py --mode declaration`
    → Confirm 25/25 PASS after revert

Acceptance checks: Hook fires and exits non-zero on missing gate_4; registry restored to clean state
Evidence: Terminal output of pre-commit run showing error
Dependencies: TC-G4H-005-01 CLOSED; TC-G4H-001 CLOSED; TC-G4H-002 CLOSED
Next valid task: TC-G4H-005 parent close → TC-G4H-006

---

## §9.6  TC-G4H-006 — Completion Matrix Sync Check

Parent Taskcard ID: TC-G4H-006
Title: Create check_completion_matrix.py and add it to governance tests and pre-commit
Type: PARENT
Status: READY
Source requirement: REQ-G4H-006 (RC-7)

INVESTIGATION REQUIRED: The exact YAML schema of format-completion-matrix.yaml is not
confirmed. TC-G4H-006-01 is a mandatory investigation before implementation.

Scope:
  Allowed files (read): registry/format-completion-matrix.yaml
  Allowed files (new): tools/gates/check_completion_matrix.py
  Allowed files (modify): tests/python/test_gate4_governance.py, .pre-commit-config.yaml

Dependencies: TC-G4H-003 CLOSED; TC-G4H-005 CLOSED (adds to same pre-commit file)
Child taskcards: TC-G4H-006-01, TC-G4H-006-02, TC-G4H-006-03, TC-G4H-006-04

Parent acceptance criteria:
  - check_completion_matrix.py exits 0 on current clean registry+matrix
  - test_completion_matrix_consistent_with_registry passes
  - A manually-introduced gate_4_status mismatch → tool exits 1 with clear message

Rollback: Delete check_completion_matrix.py; revert test_gate4_governance.py; remove hook update
Closeout: All 4 children CLOSED; matrix check passes + governance test passes

---

### TC-G4H-006-01 — INVESTIGATION: Read format-completion-matrix.yaml schema

Child Taskcard ID: TC-G4H-006-01
Parent Taskcard ID: TC-G4H-006
Title: Inspect format-completion-matrix.yaml to determine exact schema for gate_4_status field
Type: CHILD (INVESTIGATION)
Status: TODO

IMPORTANT: Do NOT implement check_completion_matrix.py until this investigation is complete.
The tool in §5 (Solution Design) assumes a `formats` list with `format_id + gate_4_status +
gate_4_evidence_type`. This must be confirmed against the actual file structure.

Micro-steps:
  MS-G4H-006-01-01 [PENDING]: Read registry/format-completion-matrix.yaml lines 1–50
    → Record: top-level key name(s), per-format entry structure
  MS-G4H-006-01-02 [PENDING]: Read lines 51–120 (find a few format entries)
    → Record: exact field names used for gate_4 status and evidence_type
  MS-G4H-006-01-03 [PENDING]: Record findings:
    top_level_key: <confirmed>
    per_format_id_field: <confirmed>
    gate_4_status_field: <confirmed>
    gate_4_evidence_type_field: <confirmed>
    total_formats_in_matrix: <count>
  MS-G4H-006-01-04 [PENDING]: Compare total formats in matrix vs. format-registry.yaml
    → If counts differ: record the difference as a pre-existing gap

Investigation output: Schema fact record embedded in child evidence
Acceptance checks: All 4 facts above recorded; schema assumptions confirmed or corrected
Dependencies: NONE
Next valid task: TC-G4H-006-02

---

### TC-G4H-006-02 — Create check_completion_matrix.py

Child Taskcard ID: TC-G4H-006-02
Parent Taskcard ID: TC-G4H-006
Title: Implement check_completion_matrix.py using confirmed schema from TC-G4H-006-01
Type: CHILD
Status: TODO

Preconditions: TC-G4H-006-01 CLOSED; schema facts confirmed

IMPLEMENTATION GUIDANCE (adjust field names based on TC-G4H-006-01 findings):
  - REPO constant (parents[2] from tools/gates/)
  - REGISTRY = REPO / "registry" / "format-registry.yaml"
  - MATRIX = REPO / "registry" / "format-completion-matrix.yaml"
  - Load both; build registry lookup: {format_id → {gate_4_status, gate_4_evidence_type}}
  - Iterate matrix entries; compare status + evidence_type; collect mismatches
  - Exit 0 if no mismatches; exit 1 with clear mismatch list
  - Also check: formats in registry not in matrix (new format gap)
  - Also check: formats in matrix not in registry (stale matrix entry)

Micro-steps:
  MS-G4H-006-02-01 [PENDING]: Create tools/gates/check_completion_matrix.py using confirmed schema
  MS-G4H-006-02-02 [PENDING]: Run `python tools/gates/check_completion_matrix.py`
    → Expected: exit 0 with message "Completion matrix consistent with registry"
    → If mismatches found: DO NOT fix them in this taskcard — record as pre-existing gap and
      add a note; fix the matrix entries manually in a separate focused edit before proceeding

Acceptance checks: Script exits 0 on clean state; mismatches produce clear output
Dependencies: TC-G4H-006-01
Next valid task: TC-G4H-006-03

---

### TC-G4H-006-03 — Add completion matrix governance test

Child Taskcard ID: TC-G4H-006-03
Parent Taskcard ID: TC-G4H-006
Title: Add test_completion_matrix_consistent_with_registry to test_gate4_governance.py
Type: CHILD
Status: TODO

Preconditions: TC-G4H-006-02 CLOSED; check_completion_matrix.py exits 0 on real registry

Micro-steps:
  MS-G4H-006-03-01 [PENDING]: Refactor check_completion_matrix.py to expose a testable function:
    ```python
    def check(registry_path=REGISTRY, matrix_path=MATRIX) -> list[str]:
        """Return list of mismatch strings (empty = consistent)."""
        ...
    def main() -> int:
        mismatches = check()
        if mismatches: [print(m) for m in mismatches]; return 1
        print("Consistent."); return 0
    ```
  MS-G4H-006-03-02 [PENDING]: Add to test_gate4_governance.py:
    ```python
    def test_completion_matrix_consistent_with_registry():
        """format-completion-matrix.yaml gate_4 fields must match format-registry.yaml."""
        from tools.gates.check_completion_matrix import check
        mismatches = check()
        assert mismatches == [], "Matrix/registry inconsistency:\n" + "\n".join(mismatches)
    ```
  MS-G4H-006-03-03 [PENDING]: Run `.venv/Scripts/pytest tests/python/test_gate4_governance.py -v`
    → All tests pass including new one

Acceptance checks: New governance test passes; no regressions
Dependencies: TC-G4H-006-02; TC-G4H-003 CLOSED (test file edits don't conflict if sequential)
Next valid task: TC-G4H-006-04

---

### TC-G4H-006-04 — Add check_completion_matrix to pre-commit hook

Child Taskcard ID: TC-G4H-006-04
Parent Taskcard ID: TC-G4H-006
Title: Update the gate4-evidence-validator pre-commit hook to also run check_completion_matrix.py
Type: CHILD
Status: TODO

Preconditions: TC-G4H-005-01 CLOSED (hook exists); TC-G4H-006-02 CLOSED (tool works)

Micro-steps:
  MS-G4H-006-04-01 [PENDING]: Read .pre-commit-config.yaml to find the gate4-evidence-validator hook
  MS-G4H-006-04-02 [PENDING]: Update the entry field from:
    `entry: python tools/gates/validate_gate4_evidence.py --mode declaration`
    to:
    `entry: bash -c 'python tools/gates/validate_gate4_evidence.py --mode declaration && python tools/gates/check_completion_matrix.py'`
    (Or add as a separate hook named `gate4-matrix-sync-check` targeting only the matrix file)
    DECISION: Prefer separate hook for clarity:
    ```yaml
      - id: gate4-matrix-sync-check
        name: Gate 4 completion matrix sync check
        entry: python tools/gates/check_completion_matrix.py
        language: system
        pass_filenames: false
        always_run: false
        files: >
          (?x)^(
            registry/format-registry\.yaml|
            registry/format-completion-matrix\.yaml
          )$
        stages: [pre-commit]
    ```
  MS-G4H-006-04-03 [PENDING]: Verify YAML validity of .pre-commit-config.yaml

Acceptance checks: YAML valid; both hooks appear in local section
Dependencies: TC-G4H-005-01, TC-G4H-006-02
Next valid task: TC-G4H-006 parent close → TC-G4H-007

---

## §9.7  TC-G4H-007 — Fresh Verification Run and Evidence Bundle

Parent Taskcard ID: TC-G4H-007
Title: Run full verification suite; confirm all completion criteria; produce attested evidence bundle
Type: PARENT
Status: READY
Source requirement: REQ-G4H-007 (SW-1)

Dependencies: TC-G4H-001, TC-G4H-002, TC-G4H-003, TC-G4H-004, TC-G4H-005, TC-G4H-006 — ALL CLOSED
Child taskcards: TC-G4H-007-01 through TC-G4H-007-08

Parent acceptance criteria:
  ALL completion counters = 0:
  - UNCLASSIFIED_SUPPORTED_FORMATS = 0
  - GATE4_PASS_WITHOUT_EXECUTABLE_EVIDENCE = 0
  - GATE4_REGISTRY_ACQUISITION_MISMATCHES = 0
  - DUPLICATED_PARSER_IMPLEMENTATIONS_CREATED = 0
  - READY_GATE4_GAPS_WITHOUT_TASKCARDS = 0
  - FALSE_GATE4_PASSES_FOR_BLOCKED_FORMATS = 0
  - FAILED_REQUIRED_PILOTS = 0 (pre-commit demo counts as Pilot gate)
  - MATERIAL_SECOND_RUN_CHANGES = 0

Rollback: Evidence bundle is additive only; delete .local/evidences/gate4-harden-001/ if needed

---

### TC-G4H-007-01 — Run test_gate4_contract.py

Child Taskcard ID: TC-G4H-007-01
Status: TODO
Micro-steps:
  MS-G4H-007-01-01 [PENDING]: `.venv/Scripts/pytest tests/python/test_gate4_contract.py -v --tb=short`
    → Record: total tests, passed, failed (expected: all pass including new corpus tests)
  MS-G4H-007-01-02 [PENDING]: If any failures: diagnose; fix before proceeding; do not skip
Dependencies: TC-G4H-001, TC-G4H-002 CLOSED
Next: TC-G4H-007-02

---

### TC-G4H-007-02 — Run test_gate4_governance.py

Child Taskcard ID: TC-G4H-007-02
Status: TODO
Micro-steps:
  MS-G4H-007-02-01 [PENDING]: `.venv/Scripts/pytest tests/python/test_gate4_governance.py -v --tb=short`
    → Record: total tests, passed, failed (expected: all pass including BLOCKED_FORMATS + matrix tests)
  MS-G4H-007-02-02 [PENDING]: If any failures: diagnose; fix before proceeding
Dependencies: TC-G4H-003, TC-G4H-006-03 CLOSED
Next: TC-G4H-007-03

---

### TC-G4H-007-03 — Run test_gate4_execution_probe.py

Child Taskcard ID: TC-G4H-007-03
Status: TODO
Micro-steps:
  MS-G4H-007-03-01 [PENDING]: `.venv/Scripts/pytest tests/python/test_gate4_execution_probe.py -v --tb=short`
    → Record: total tests, passed, failed (expected: all 7+ tests pass)
  MS-G4H-007-03-02 [PENDING]: If any PROBE_FAILED unexpected: investigate probe function; fix
Dependencies: TC-G4H-004 CLOSED
Next: TC-G4H-007-04

---

### TC-G4H-007-04 — Run validator declaration mode

Child Taskcard ID: TC-G4H-007-04
Status: TODO
Micro-steps:
  MS-G4H-007-04-01 [PENDING]: `python tools/gates/validate_gate4_evidence.py --mode declaration`
    → Expected: 25/25 PASS; exit code 0; capture full output
  MS-G4H-007-04-02 [PENDING]: Also run `python tools/gates/check_completion_matrix.py`
    → Expected: "Consistent" message; exit code 0
Dependencies: TC-G4H-001, TC-G4H-002, TC-G4H-006 CLOSED
Next: TC-G4H-007-05

---

### TC-G4H-007-05 — Run validator execute mode

Child Taskcard ID: TC-G4H-007-05
Status: TODO
Micro-steps:
  MS-G4H-007-05-01 [PENDING]: `python tools/gates/validate_gate4_evidence.py --mode execute`
    → Expected: 25/25 PASS declarations + 0 PROBE_FAILED + exit code 0
    → Capture probe results table (format | PASS|SKIPPED | detail)
  MS-G4H-007-05-02 [PENDING]: If any PROBE_FAILED: diagnose; fix in probe module; rerun until clean
Dependencies: TC-G4H-004 CLOSED; TC-G4H-007-04 complete
Next: TC-G4H-007-06

---

### TC-G4H-007-06 — Run full Gate 4 skill tests

Child Taskcard ID: TC-G4H-007-06
Status: TODO
Micro-steps:
  MS-G4H-007-06-01 [PENDING]: `.venv/Scripts/pytest tests/skills/ -k "gate4" -v --tb=short`
    → Record: total tests, passed, pre-existing known failures
    → Known pre-existing failure: test_no_src_net_zst (src/net/zst/ exists) — do NOT fix here
    → All other tests must pass
Dependencies: NONE (skill tests are independent; but run after probe module complete)
Next: TC-G4H-007-07

---

### TC-G4H-007-07 — Confirm pre-commit gate blocking (idempotency pilot)

Child Taskcard ID: TC-G4H-007-07
Status: TODO
Micro-steps:
  MS-G4H-007-07-01 [PENDING]: Run second validator pass to confirm zero material registry changes:
    `python tools/gates/validate_gate4_evidence.py --mode declaration`
    `git diff registry/format-registry.yaml registry/format-completion-matrix.yaml`
    → Expected: no diff (or only whitespace); MATERIAL_SECOND_RUN_CHANGES = 0
  MS-G4H-007-07-02 [PENDING]: Run `pre-commit run gate4-evidence-validator --all-files`
    → Expected: exit 0 (all files pass declaration validation)
  MS-G4H-007-07-03 [PENDING]: Run `pre-commit run gate4-matrix-sync-check --all-files`
    → Expected: exit 0
Dependencies: TC-G4H-005, TC-G4H-006 CLOSED
Next: TC-G4H-007-08

---

### TC-G4H-007-08 — Create evidence bundle and terminal-closeout.yaml

Child Taskcard ID: TC-G4H-007-08
Status: TODO
Micro-steps:
  MS-G4H-007-08-01 [PENDING]: Create directory .local/evidences/gate4-harden-001/
  MS-G4H-007-08-02 [PENDING]: Write .local/evidences/gate4-harden-001/evidence-declaration.yaml:
    Fields: mission_id, plan, closed_at (ISO timestamp), test results per file,
    validator_declaration_result, validator_execute_result (probe counts), pre_commit_demo,
    completion_counters (all 8 at zero), final_verdict
  MS-G4H-007-08-03 [PENDING]: Write .local/evidences/gate4-harden-001/terminal-closeout.yaml:
    Fields: mission_id, plan, prior_mission (FF-G4-BACKFILL-001), verdict,
    formats_verified (25), idempotency_result (PASS), drift_gaps_found (0)
  MS-G4H-007-08-04 [PENDING]: Print SHA-256 of evidence-declaration.yaml:
    `python -c "import hashlib; print(hashlib.sha256(open('.local/evidences/gate4-harden-001/evidence-declaration.yaml','rb').read()).hexdigest())"`
  MS-G4H-007-08-05 [PENDING]: Run `python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/atomic-chasing-meteor.md --terminal`
    → This is the POST-PLAN TERMINAL action. Execute only after ALL prior children closed.
    → After this: STOP. Report to user. Do NOT start any further work.

Dependencies: TC-G4H-007-01 through TC-G4H-007-07 ALL CLOSED
Final action: write_plan_lock --terminal; STOP

# ─────────────────────────────────────────────────────────────────────────────
# §10  MACHINE STATE MODEL
# ─────────────────────────────────────────────────────────────────────────────

## Machine State Model

### Valid Status Values

Parent statuses: PROPOSED | READY | IN_PROGRESS | CHILDREN_IN_PROGRESS |
  INTEGRATION_PENDING | VERIFIED | SCORED | CLOSED | BLOCKED | BLOCKED_EXTERNAL | DEFERRED_WITH_REASON

Child statuses: TODO | READY | IN_PROGRESS | IMPLEMENTED | VERIFIED | SCORED |
  CLOSED | REROUTED | BLOCKED | BLOCKED_EXTERNAL | DEFERRED_WITH_REASON

Micro-step statuses: PENDING | READY | ACTIVE | COMPLETE | FAILED | BLOCKED | SKIPPED_NOT_APPLICABLE

### Current State Table

| TC-ID | Type | Status | Depends On | Wave |
|-------|------|--------|------------|------|
| TC-G4H-001 | PARENT | READY | — | 2 |
| TC-G4H-001-01 | CHILD | TODO | — | 2a |
| TC-G4H-001-02 | CHILD | TODO | TC-G4H-001-01 | 2b |
| TC-G4H-001-03 | CHILD | TODO | TC-G4H-001-02 | 2c |
| TC-G4H-001-04 | CHILD | TODO | TC-G4H-001-03 | 2d |
| TC-G4H-001-05 | CHILD | TODO | TC-G4H-001-04 | 2e |
| TC-G4H-002 | PARENT | READY | TC-G4H-001 | 2 |
| TC-G4H-002-01 | CHILD | TODO | TC-G4H-001 CLOSED | 2f |
| TC-G4H-002-02 | CHILD | TODO | TC-G4H-002-01 | 2g |
| TC-G4H-003 | PARENT | READY | — | 1 |
| TC-G4H-003-01 | CHILD | TODO | — | 1a |
| TC-G4H-003-02 | CHILD | TODO | TC-G4H-003-01 | 1b |
| TC-G4H-003-03 | CHILD | TODO | TC-G4H-003-02 | 1c |
| TC-G4H-004 | PARENT | READY | TC-G4H-001+002 | 4 |
| TC-G4H-004-01 | CHILD | TODO | TC-G4H-001+002 CLOSED | 4a |
| TC-G4H-004-02 | CHILD | TODO | TC-G4H-004-01 | 4b |
| TC-G4H-004-03 | CHILD | TODO | TC-G4H-004-02 | 4c |
| TC-G4H-004-04 | CHILD | TODO | TC-G4H-004-03 | 4d |
| TC-G4H-004-05 | CHILD | TODO | TC-G4H-004-04 | 4e |
| TC-G4H-004-06 | CHILD | TODO | TC-G4H-004-05 | 4f |
| TC-G4H-004-07 | CHILD | TODO | TC-G4H-004-06 | 4g |
| TC-G4H-004-08 | CHILD | TODO | TC-G4H-004-07 | 4h |
| TC-G4H-004-09 | CHILD | TODO | TC-G4H-004-08 | 4i |
| TC-G4H-004-10 | CHILD | TODO | TC-G4H-004-09 | 4j |
| TC-G4H-005 | PARENT | READY | — | 1 |
| TC-G4H-005-01 | CHILD | TODO | — | 1d |
| TC-G4H-005-02 | CHILD | TODO | TC-G4H-005-01; TC-G4H-001+002 | 3a |
| TC-G4H-006 | PARENT | READY | TC-G4H-003+005 | 3 |
| TC-G4H-006-01 | CHILD | TODO | — | 3b |
| TC-G4H-006-02 | CHILD | TODO | TC-G4H-006-01 | 3c |
| TC-G4H-006-03 | CHILD | TODO | TC-G4H-006-02; TC-G4H-003 | 3d |
| TC-G4H-006-04 | CHILD | TODO | TC-G4H-005-01; TC-G4H-006-02 | 3e |
| TC-G4H-007 | PARENT | READY | ALL others | 5 |
| TC-G4H-007-01 through 007-08 | CHILD | TODO | see §9.7 | 5a-h |

### Invalid Transition Rules (BLOCKED)

- NEVER: Child CLOSED while any mandatory micro-step is PENDING or FAILED
- NEVER: Parent CLOSED while any mandatory child is not CLOSED
- NEVER: TC-G4H-002 starts before TC-G4H-001 is CLOSED (same file ownership)
- NEVER: TC-G4H-004 starts before TC-G4H-001 AND TC-G4H-002 are both CLOSED
- NEVER: TC-G4H-006-04 modifies .pre-commit-config.yaml before TC-G4H-005-01 is CLOSED
- NEVER: TC-G4H-007-08 writes terminal-closeout before TC-G4H-007-01 through 007-07 are CLOSED
- NEVER: REROUTED → CLOSED without re-execution and new quality score

# ─────────────────────────────────────────────────────────────────────────────
# §11  EXECUTION DAG
# ─────────────────────────────────────────────────────────────────────────────

## Execution DAG

Wave 1 (parallel-safe — different files):
  TC-G4H-003-01 → TC-G4H-003-02 → TC-G4H-003-03 [owns: test_gate4_governance.py]
  TC-G4H-005-01                                    [owns: .pre-commit-config.yaml]
  TC-G4H-006-01 (investigation only — read-only)   [owns: nothing yet]

Wave 2 (sequential — same file validate_gate4_evidence.py):
  TC-G4H-001-01 → 001-02 → 001-03 → 001-04 → 001-05
  THEN TC-G4H-002-01 → 002-02

Wave 3 (depends on Wave 1+2 items):
  TC-G4H-005-02 [needs TC-G4H-005-01 + TC-G4H-001+002 closed]
  TC-G4H-006-02 [needs TC-G4H-006-01 investigation]
  TC-G4H-006-03 [needs TC-G4H-006-02 + TC-G4H-003 closed]
  TC-G4H-006-04 [needs TC-G4H-005-01 + TC-G4H-006-02]

Wave 4 (depends on Wave 2):
  TC-G4H-004-01 → 004-02 → 004-03 → 004-04 → 004-05 → 004-06 → 004-07 → 004-08 → 004-09 → 004-10

Wave 5 (ALL prior waves complete):
  TC-G4H-007-01 → 007-02 → 007-03 → 007-04 → 007-05 → 007-06 → 007-07 → 007-08

File ownership locks (never edit simultaneously):
  validate_gate4_evidence.py: TC-G4H-001 (wave 2a-e), then TC-G4H-002 (wave 2f-g), then TC-G4H-004-06 (wave 4f)
  test_gate4_contract.py: TC-G4H-001-05 (wave 2e), TC-G4H-002-02 (wave 2g)
  test_gate4_governance.py: TC-G4H-003-01,02,03 (wave 1a-c), TC-G4H-006-03 (wave 3d)
  .pre-commit-config.yaml: TC-G4H-005-01 (wave 1d), TC-G4H-006-04 (wave 3e)

Recommended execution order for single-agent sequential:
  1. TC-G4H-003-01 → 02 → 03
  2. TC-G4H-005-01
  3. TC-G4H-006-01 (investigation)
  4. TC-G4H-001-01 → 02 → 03 → 04 → 05
  5. TC-G4H-002-01 → 02
  6. TC-G4H-005-02
  7. TC-G4H-006-02 → 03 → 04
  8. TC-G4H-004-01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10
  9. TC-G4H-007-01 → 02 → 03 → 04 → 05 → 06 → 07 → 08

# ─────────────────────────────────────────────────────────────────────────────
# §12  VALIDATION MATRIX
# ─────────────────────────────────────────────────────────────────────────────

## Validation Matrix

| TC-ID | Validation Type | Command / Method | Expected Result | Mandatory | Evidence |
|-------|----------------|-----------------|-----------------|-----------|---------|
| TC-G4H-001 | Unit | pytest test_gate4_contract.py -v | All pass incl. 2 new | YES | pytest -v output |
| TC-G4H-001 | Integration | python validate_gate4_evidence.py | 25/25 PASS | YES | validator stdout |
| TC-G4H-001-01 | Import check | python -c "from ... import _check_corpus_populated" | "import ok" | YES | terminal output |
| TC-G4H-001-02,03,04 | Regression | python validate_gate4_evidence.py (after each change) | 25/25 PASS | YES | stdout each time |
| TC-G4H-001-05 | Unit (negative) | pytest test_gate4_contract.py::test_corpus_nonexistent* | PASS | YES | pytest output |
| TC-G4H-002 | Unit | pytest test_gate4_contract.py -v | All pass | YES | pytest -v output |
| TC-G4H-002-01 | Regression | python validate_gate4_evidence.py | 25/25 PASS | YES | validator stdout |
| TC-G4H-003 | Unit | pytest test_gate4_governance.py -v | All pass incl. 2 new | YES | pytest -v output |
| TC-G4H-004 | Unit | pytest test_gate4_execution_probe.py -v | All pass | YES | pytest -v output |
| TC-G4H-004 | Integration | python validate_gate4_evidence.py --mode execute | 0 PROBE_FAILED | YES | validator stdout |
| TC-G4H-004-02 | Manual probe | python -c "...probe_evidence_wrapper('csv',g4)..." | status='PASS' | YES | terminal output |
| TC-G4H-004-03 | Manual probe | probe_standalone_prototype('xpm',g4) | status='PASS' | YES | terminal output |
| TC-G4H-004-04 | Manual probe | probe_source_track_equivalent('ods',g4) | PASS or SKIPPED | YES | terminal output |
| TC-G4H-005 | Hook fire test | pre-commit run gate4-evidence-validator --files registry/... | exit 1 on bad input | YES | terminal output |
| TC-G4H-005 | Hook clean test | pre-commit run gate4-evidence-validator --all-files | exit 0 on clean | YES | terminal output |
| TC-G4H-006 | Unit | pytest test_gate4_governance.py::test_completion_matrix* | PASS | YES | pytest output |
| TC-G4H-006 | Integration | python check_completion_matrix.py | exit 0, "Consistent" | YES | stdout |
| TC-G4H-007 | Full suite | pytest tests/python/test_gate4_*.py -v | All pass | YES | full output |
| TC-G4H-007 | Idempotency | git diff registry/*.yaml after 2nd tool run | Zero material diff | YES | git diff output |
| TC-G4H-007 | Skill tests | pytest tests/skills/ -k gate4 -v | All pass (excl. known) | YES | pytest -v output |

Negative controls:
  - corpus nonexistent path → FAIL with "corpus" in error (TC-G4H-001-05)
  - corpus empty dir → FAIL (TC-G4H-001-05)
  - STE missing test file → FAIL with "does not exist on disk" (TC-G4H-002-02)
  - New format without gate_4 → pre-commit blocks (TC-G4H-005-02)
  - Probe on missing corpus → PROBE_FAILED (TC-G4H-004-10)
  - Blocked format probe → SKIPPED (TC-G4H-004-10)

# ─────────────────────────────────────────────────────────────────────────────
# §13  EVIDENCE CONTRACT
# ─────────────────────────────────────────────────────────────────────────────

## Evidence Contract

Evidence root: .local/evidences/gate4-harden-001/
Required files:
  evidence-declaration.yaml — mission, tests, validator results, probe results, counters, verdict
  terminal-closeout.yaml — mission, plan path, prior mission, formats verified, idempotency

Required evidence fields in evidence-declaration.yaml:
  mission_id: FF-G4-HARDEN-001
  plan: plans/.claude/atomic-chasing-meteor.md
  closed_at: <ISO 8601 UTC>
  tests:
    test_gate4_contract: {count: N, passed: N, failed: 0}
    test_gate4_governance: {count: N, passed: N, failed: 0}
    test_gate4_execution_probe: {count: N, passed: N, failed: 0}
    gate4_skill_tests: {count: N, passed: N, known_failures: ["test_no_src_net_zst"]}
  validator_declaration: {formats: 25, passed: 25, failed: 0}
  validator_execute: {probes_run: N, passed: N, skipped: N, probe_failed: 0}
  pre_commit_demo: {status: CONFIRMED_BLOCKING}
  matrix_check: {status: CONSISTENT}
  idempotency: {material_changes: 0}
  completion_counters:
    UNCLASSIFIED_SUPPORTED_FORMATS: 0
    GATE4_PASS_WITHOUT_EXECUTABLE_EVIDENCE: 0
    GATE4_REGISTRY_ACQUISITION_MISMATCHES: 0
    DUPLICATED_PARSER_IMPLEMENTATIONS_CREATED: 0
    READY_GATE4_GAPS_WITHOUT_TASKCARDS: 0
    FALSE_GATE4_PASSES_FOR_BLOCKED_FORMATS: 0
    FAILED_REQUIRED_PILOTS: 0
    MATERIAL_SECOND_RUN_CHANGES: 0
  final_verdict: GATE4_COVERAGE_HARDENED_EXECUTION_PROVEN_AND_CONTINUOUSLY_ENFORCED

Every evidence artifact must reference:
  authoritative_plan: plans/.claude/atomic-chasing-meteor.md
  artifact_role: evidence_only
  execution_authority: false

# ─────────────────────────────────────────────────────────────────────────────
# §14  TRACEABILITY MAP
# ─────────────────────────────────────────────────────────────────────────────

## Traceability Map

| REQ-ID | Root Cause | Parent TC | Children | Files Modified |
|--------|-----------|-----------|----------|----------------|
| REQ-G4H-001 | RC-2 | TC-G4H-001 | 001-01..05 | validate_gate4_evidence.py, test_gate4_contract.py |
| REQ-G4H-002 | RC-3 | TC-G4H-002 | 002-01..02 | validate_gate4_evidence.py, test_gate4_contract.py |
| REQ-G4H-003 | RC-4 | TC-G4H-003 | 003-01..03 | test_gate4_governance.py |
| REQ-G4H-004 | RC-1,SW-2 | TC-G4H-004 | 004-01..10 | gate4_execution_probe.py (NEW), validate_gate4_evidence.py, test_gate4_execution_probe.py (NEW) |
| REQ-G4H-005 | RC-5 | TC-G4H-005 | 005-01..02 | .pre-commit-config.yaml |
| REQ-G4H-006 | RC-7 | TC-G4H-006 | 006-01..04 | check_completion_matrix.py (NEW), test_gate4_governance.py, .pre-commit-config.yaml |
| REQ-G4H-007 | SW-1 | TC-G4H-007 | 007-01..08 | .local/evidences/gate4-harden-001/ (NEW) |

# ─────────────────────────────────────────────────────────────────────────────
# §15  CRITICAL FILE PATHS
# ─────────────────────────────────────────────────────────────────────────────

## Critical File Paths

| File | Action | Owner TC |
|------|--------|----------|
| tools/gates/validate_gate4_evidence.py | Modify (bugs + --mode flag) | TC-G4H-001, TC-G4H-002, TC-G4H-004-06 |
| tools/gates/gate4_execution_probe.py | Create (NEW) | TC-G4H-004-01..05 |
| tools/gates/check_completion_matrix.py | Create (NEW) | TC-G4H-006-02 |
| tests/python/test_gate4_contract.py | Extend (add 3 new tests) | TC-G4H-001-05, TC-G4H-002-02 |
| tests/python/test_gate4_governance.py | Modify + extend | TC-G4H-003-01..03, TC-G4H-006-03 |
| tests/python/test_gate4_execution_probe.py | Create (NEW) | TC-G4H-004-07..10 |
| .pre-commit-config.yaml | Extend (2 new hooks) | TC-G4H-005-01, TC-G4H-006-04 |
| .local/evidences/gate4-harden-001/ | Create (NEW dir + 2 files) | TC-G4H-007-08 |

Read-only (investigation only):
| registry/format-registry.yaml | READ | TC-G4H-004-01, TC-G4H-006-01 |
| registry/format-completion-matrix.yaml | READ | TC-G4H-006-01 |
| prototypes/by-format/*/ | READ | TC-G4H-004-01 |
| src/python/{ods,odt,...}/  | READ | TC-G4H-004-01 |

# ─────────────────────────────────────────────────────────────────────────────
# §16  COMPLETION CRITERIA
# ─────────────────────────────────────────────────────────────────────────────

## Completion Criteria

ALL of the following must be true before TC-G4H-007 can close:

1. `python tools/gates/validate_gate4_evidence.py --mode declaration` → 25/25 PASS
2. `python tools/gates/validate_gate4_evidence.py --mode execute` → 0 PROBE_FAILED
3. `python tools/gates/check_completion_matrix.py` → exit 0 "Consistent"
4. pytest test_gate4_contract.py → all pass (including 3 new corpus/STE tests)
5. pytest test_gate4_governance.py → all pass (including BLOCKED dynamic + matrix tests)
6. pytest test_gate4_execution_probe.py → all 7+ tests pass
7. pytest tests/skills/ -k gate4 → all pass except known test_no_src_net_zst
8. pre-commit run gate4-evidence-validator --all-files → exit 0
9. pre-commit demo: bad format addition → hook exits non-zero
10. git diff registry/*.yaml → 0 material changes on 2nd validator run
11. Evidence bundle complete at .local/evidences/gate4-harden-001/

# ─────────────────────────────────────────────────────────────────────────────
# §17  EXECUTION HANDOFF
# ─────────────────────────────────────────────────────────────────────────────

## Execution Handoff

This is the instruction set for the future execution agent.

AUTHORITATIVE PLAN: plans/.claude/atomic-chasing-meteor.md
MISSION: FF-G4-HARDEN-001

BEFORE STARTING ANY TASKCARD:
  1. Read this plan from top to bottom.
  2. Check §10 Machine State Table — find the next taskcard in TODO status.
  3. Confirm all prerequisites for that taskcard are CLOSED.
  4. Read the parent taskcard section in §9.
  5. Read the child taskcard section.
  6. Confirm allowed files and forbidden files.
  7. Confirm all preconditions are met.
  8. Execute exactly one micro-step at a time.

FOR EACH MICRO-STEP:
  1. Read the micro-step ID and action.
  2. Confirm the target file and symbol.
  3. Execute the action.
  4. Run the completion check.
  5. If check fails: do NOT proceed to next micro-step — diagnose and fix first.
  6. Record evidence (terminal output, file state).
  7. Mark micro-step COMPLETE.
  8. Proceed to next micro-step in the same child.

AFTER ALL MICRO-STEPS IN A CHILD:
  1. Run the child's acceptance checks.
  2. If all pass: mark child CLOSED.
  3. If any fail: mark child REROUTED, diagnose, fix, re-run affected micro-steps.
  4. Update the Machine State Table in §10.

AFTER ALL CHILDREN OF A PARENT CLOSE:
  1. Run the parent acceptance criteria.
  2. Run the parent integration checks.
  3. If all pass: mark parent CLOSED.
  4. Move to next taskcard per DAG in §11.

FORBIDDEN ACTIONS (execution agent must NEVER do these):
  - Close a child taskcard based on code existence alone (without running the acceptance check)
  - Close a parent while any mandatory child is not CLOSED
  - Skip an investigation taskcard (TC-G4H-004-01, TC-G4H-006-01) and jump to implementation
  - Edit validate_gate4_evidence.py while TC-G4H-001 or TC-G4H-002 is still IN_PROGRESS
  - Start TC-G4H-004 before TC-G4H-001 AND TC-G4H-002 are both CLOSED
  - Start TC-G4H-007 before all other parents are CLOSED
  - Run write_plan_lock --terminal before TC-G4H-007-08 is CLOSED

FINAL ACTION SEQUENCE:
  After TC-G4H-007-08 CLOSED:
  1. Print evidence bundle path + SHA-256
  2. Run: python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/atomic-chasing-meteor.md --terminal
  3. Report: "Plan atomic-chasing-meteor complete. All 7 parent taskcards closed.
              32 child taskcards closed. Evidence at .local/evidences/gate4-harden-001/."
  4. STOP. Do NOT start any product deepening, rotation, or ledger work.

NEXT VALID PARENT TASKCARD: TC-G4H-003 (wave 1, independent)
NEXT VALID CHILD TASKCARD: TC-G4H-003-01
FIRST MICRO-STEP: MS-G4H-003-01-01

# ─────────────────────────────────────────────────────────────────────────────
# §18  RECONCILIATION AND CHANGE LEDGER
# ─────────────────────────────────────────────────────────────────────────────

## Reconciliation and Change Ledger

Prior flat taskcards (TC-G4H-001 through TC-G4H-007) replaced by hierarchical structure.
No analysis, rationale, or design content was removed.

| Section | Change type | Reason |
|---------|-------------|--------|
| §0 Plan Authority | ADDED | Required by single-plan rule |
| §1 Preflight Record | ADDED | Required by taskcardization prompt |
| §2 Context | PRESERVED | No defects |
| §3 Root Cause Analysis | PRESERVED; RC-6 marked DEFERRED | RC-6 is cosmetic; probe supersedes |
| §4 What to Preserve | PRESERVED | No defects |
| §5 Solution Design | EXPANDED | Added options table; solution selected explicitly |
| §6 Tradeoffs | PRESERVED | No defects |
| §7 Requirements Inventory | ADDED | REQ IDs missing from prior version |
| §8 Section Processing Ledger | ADDED | Required by taskcardization prompt |
| Prior §9 Taskcards | REPLACED with §9.1–9.7 | Flat prose → hierarchical parent/child/micro-step |
| §10 Machine State | ADDED | No state machine existed |
| §11 Execution DAG | ADDED | No dependency model existed |
| §12 Validation Matrix | ADDED | Validation was scattered prose |
| §13 Evidence Contract | ADDED | Evidence obligations not formalized |
| §14 Traceability Map | ADDED | No REQ→TC mapping existed |
| §15 Critical File Paths | PRESERVED from prior version | Correct |
| §16 Completion Criteria | PRESERVED from prior version | Correct |
| §17 Execution Handoff | ADDED | No handoff existed |
| §18 Reconciliation | ADDED | Required by taskcardization prompt |
| §19 Post-Plan Terminal Rule | MOVED from bottom; kept | No change |

Single-plan authority audit: ONE active plan only. plans/.claude/atomic-stargazing-nest.md is
TERMINAL_CLOSED (prior mission). No duplicate active plan exists. CONFIRMED.

# ─────────────────────────────────────────────────────────────────────────────
# §19  POST-PLAN TERMINAL RULE
# ─────────────────────────────────────────────────────────────────────────────

When TC-G4H-007 is CLOSED and TC-G4H-007-08 is COMPLETE:
  Run: python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/atomic-chasing-meteor.md --terminal
  Then STOP. Report completion to user.
  Do NOT start product deepening or any other sprint work.
  POST_PLAN_TERMINAL is a named legitimate stop per CLAUDE.md §Supreme Directive.
