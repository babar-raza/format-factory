# Plan: shimmering-rolling-meerkat
# Type: product_deepening + structural_repair
# Mission ID: SMR-001
# Authorization: Explicit user request — new conversation, product-deepening resumption

---

## PART 1 — TRUE CURRENT STATE (corrected after two-pass audit)

My first exploration captured the system mid-pipeline. Between the two exploration
rounds, sprint `PQ-BUNDLE-FORENSICS-REPAIR-001` ran autonomously and materially changed
the state. The plan I initially drafted was solving a problem that no longer existed.

### What is actually true right now:

| Signal | Initial Read | After Deep Audit | Explanation |
|--------|-------------|-----------------|-------------|
| `check_continuation.py` | STOP / POST_PLAN_TERMINAL | **CONTINUE** (exit 0) | PQ-BUNDLE ran between reads and reset signal |
| Last sprint | vast-weaving-lampson | **PQ-BUNDLE-FORENSICS-REPAIR-001** | Autonomous sprint ran between reads |
| Test count | 1,169 | **21,558** | PQ-BUNDLE added 20,389 tests |
| Continuation state | blocked | **YES_WITH_REWORK** (iteration 6/12) | Fresh signal generated at 16:49 |
| Rework items | [] | **["PQ-019-020-CLI-STUBS"]** | One outstanding rework item |
| Post-plan-terminal block | present | **not blocking** | check_continuation returns CONTINUE |
| Uncommitted files | 17 modified | **17 still uncommitted** | Supervisor pipeline outputs not committed |

### Committed plan closures (today, 2026-07-10):
- **gov-window-fix-001** — locked 08:09 (session 033f6a1ae2f3) — extended V105/V106 windows
- **vast-weaving-lampson** — locked 09:28 (session 033f6a1ae2f3) — committed at af879e55 14:54
- **parallel-foraging-fairy v2** — locked 2026-07-09 (session 0031a2fb6fcd) — V149 cleanup

### Architectural fact that changes the dogfood/package analysis:
Both `/add-dogfood-export` and `/package-install-proof` are marked `advisory_only: true`
in `.supervisor/skill-registry.yaml`. They generate guidance, not execution. My original
TC-SMR-004/005 assumed they would execute — they would not.

Dogfood exports are also NOT in separate directories. They are embedded in each format
package: `src/python/fods/csv_exporter.py`, `src/python/fodt/exporters.py`, etc.
There is no `dogfood/` directory structure to "advance."

---

## PART 2 — SYMPTOMS, ROOT CAUSES, STRUCTURAL WEAKNESSES

### Symptoms (visible surface problems)

1. `check_continuation.py` returned a different verdict on two reads minutes apart.
2. 17 supervisor-generated files are uncommitted and accumulating.
3. `next-work-items.json` contains items titled "Implement unknown for ABW/CSV/DIF."
4. Rework item `PQ-019-020-CLI-STUBS` appears in the queue but has not been executed.
5. Layer plans reference commit `a7744cf6` but HEAD is `af879e55` (stale by 20+ commits).
6. Validator expected counts have been manually corrected in recent commits:
   183 → 166 → 165 → 166 — across multiple files.

### Root Causes (what actually produces those symptoms)

**RC-001 — Capability-compiler generates work from unresolved spec gaps**

The `TC-GAP-CHAIN-ABW-SAL-MRH-001` items all have `title: "Implement unknown for ABW"`.
The word "unknown" comes from the capability fact name — the SAL pipeline has not yet
ingested the spec for ABW, CSV (chain-gaps), DIF (chain-gaps), etc. The capability
compiler faithfully turns these into work items, producing structurally valid tasks that
are semantically empty. Implementing "unknown" cannot satisfy RULE-LIB-002 (every public
symbol must trace to a spec QName) because there is no QName to trace to.

This is not a compiler bug. The compiler is working correctly. The root cause is that
**the SAL pipeline has not ingested authoritative spec facts for most formats**.
The layer plan (L01-SAL) acknowledges this: status HARDENING_REQUIRED, health DEGRADED,
TC-SAL-001 is TODO. Without SAL facts, the capability chain is broken upstream, and
everything downstream (capability → feature → product work) is guesswork.

Impact: Every sprint receives a queue polluted with un-implementable work items.

**RC-002 — Rework item PQ-019-020-CLI-STUBS is never the sprint focus**

CLI entry points and type stubs for 20 packages is real, bounded, implementable work.
It does not require spec facts. It does not require human approval. It is not blocked.
But it has survived at least 3 sprint cycles as rework without being selected as the
primary focus. The sprint prompt always presents it as "rework" (secondary to new work),
and agents select new capability-compiler items instead.

The structural cause: the sprint priority model treats rework as lower-priority than
new product work, even when the rework is more clearly specified than the new work.

**RC-003 — Supervisor pipeline state is not committed between sprints**

The supervisor pipeline (autonomous_cycle) generates ~15 reports files (session-resume,
approval-gates, next-sprint, evidence-review, etc.) after each sprint. These are left
in the modified working tree. They accumulate until a human or the next plan closure
triggers a commit. This causes confusion: the "last sprint" shown in the repo HEAD
lags behind the actual last sprint run.

There is no automatic commit of supervisor state. The sprint-closeout checklist does
not include a "commit supervisor outputs" step as a separate action from the sprint's
own product commits.

**RC-004 — Validator count is tracked redundantly across multiple files**

`governance_validator_runner.py` has an `expected_count` hardcoded. Test assertions
also hardcode it. The README references it. When a new validator is added:
1. The validator file gets the new function
2. expected_count in runner.py is updated
3. Test assertion is updated
4. README is updated
5. CI check is updated

Any mismatch causes test failures. Recent git history shows 5 commits in 2 weeks
manually correcting these counts (183→166, 166→165, 165→166). This is brittle.

**RC-005 — Layer plans are not updated as part of sprint closeout**

Layer plans in `plans/layers/` were created on 2026-06-26 at commit `a7744cf6`.
Current HEAD is `af879e55`. The layer plans reference stale commit hashes, validator
counts (86 vs 165 actual), test counts, and task states. No sprint closeout step
updates them. They are referenced in governance but are unreliable as reality signals.

**RC-006 — `active-plan-lock.json` is a cross-session state singleton**

When a per-chat plan completes with `--terminal`, it writes TERMINAL_CLOSED to a
GLOBAL file. The next session's `check_continuation.py` hits this global file and
returns POST_PLAN_TERMINAL — even though that plan belongs to a different session.
MEMORY.md documents the workaround as a "recurring 2026-06-25/26" pattern (mark as
SUPERSEDED). The issue recurs because the fix is applied per-session, not to the design.

Note: In this specific case, the issue resolved itself because PQ-BUNDLE-FORENSICS ran
and generated a fresh continuation signal. But the underlying design flaw persists.

---

### What to Preserve vs Redesign

**PRESERVE (working correctly):**
- Evidence declaration + `autonomous_cycle.py` pipeline — reliable, generates good output
- 165 governance validators — catching real issues (V105/V106 extension is evidence)
- Per-chat plan structure — effective for focused, auditable work
- Product-code-change-ledger.json — good audit trail for all src/ changes
- Oracle verification system (20 formats, 73/73 PASS)
- `no_stub_scan.py` V149 validator — newly upgraded to blocking, working correctly
- The capability-compiler itself — structurally sound, just needs a quality gate upstream

**REDESIGN / FIX:**
These are the concrete structural changes that would prevent the symptoms from recurring.

---

## PART 3 — CONCRETE STRUCTURAL FIXES

Each fix addresses one root cause. These are bounded, testable, regression-controlled.

### Fix-RC-001: Capability-Compiler Quality Gate

**File to modify:** `tools/supervisor/capability_feature_compiler.py` (the PIPELINE tool,
not `tools/capability_layer/capability_to_feature_compiler.py` which is planning-only)

**Change:** Before writing a work item to next-work-items.json, check whether the
`spec_fact_name` (or `feature_name`) is "unknown", None, or empty. If so, route the
item to a `quarantine-needs-sal` lane instead of the `capability-compiler` lane.

```python
# In generate_work_item() or equivalent:
if feature_name in ("unknown", None, "") or "unknown" in feature_name.lower():
    item["lane"] = "quarantine-needs-sal"
    item["quarantine_reason"] = "spec_fact_not_established"
    item["blocked_by"] = "TC-SAL-001"
    item["agent_can_execute"] = False
    item["execution_status"] = "blocked-missing-spec-authority"
    return item  # Still emit for visibility, but not as executable work
```

**Test:** Run capability-compiler and confirm no executable items with "unknown" in title
appear in the `capability-compiler` lane.

**Regression control:** Existing non-unknown items must still appear as executable. Run
with a known-good format (CSV with 55 SAL facts) and confirm items remain executable.

**Risk:** Some legitimate feature names might contain the word "unknown" (edge case).
Keep the gate narrow: check `spec_fact_name == "unknown"` exactly, not substring match.

---

### Fix-RC-002: Rework-First Sprint Selection Protocol

**File to modify:** `tools/supervisor/next_sprint_generator.py` (or equivalent that
generates the `next-sprint.md` priority ordering)

**Change:** When `rework_items` is non-empty in the continuation signal, the generated
next-sprint.md should list rework as **Section 0** (not Section 2), and explicitly
say: "Address rework before selecting new work." The TASK numbering should start with
rework items.

Additionally, if a rework item has survived ≥ 3 sprint cycles without resolution,
add a `[STALE_REWORK]` tag and elevate to P0. Emit a warning in the next-sprint.md:
"STALE_REWORK: PQ-019-020-CLI-STUBS has survived N sprints — must be addressed THIS sprint."

**Test:** Inject a known rework item into the continuation signal, run next-sprint
generator, confirm it appears as TASK-000 or TASK-001 before any new-work items.

**Risk:** This changes the sprint prompt format. Any tools that parse next-sprint.md
by section number would need updating.

---

### Fix-RC-003: Supervisor State Auto-Commit in Sprint Closeout

**File to create:** `tools/supervisor/commit_supervisor_state.py`

**Purpose:** After `autonomous_cycle.py` generates supervisor outputs, automatically
stage and commit the generated files without touching product source.

```python
SUPERVISOR_STATE_FILES = [
    "reports/supervisor/session-resume.md",
    "reports/supervisor/approval-gates.md",
    "reports/supervisor/next-sprint.md",
    "reports/supervisor/next-sprint-taskmaster.json",
    "reports/supervisor/next-ruflo-lanes.json",
    "reports/supervisor/evidence-review.json",
    "reports/supervisor/evidence-review.md",
    "reports/supervisor/contradictions.json",
    "reports/supervisor/contradictions.md",
    "reports/supervisor/discovery-summary.md",
    "reports/supervisor/memory-sync-report.md",
    ".supervisor/project-memory.md",
    ".supervisor/state/current-run.json",
    ".supervisor/state/watcher.json",
]

def commit_supervisor_state(sprint_id: str) -> bool:
    """Stage and commit supervisor-generated state files.
    Returns True on success, False on failure (caller skips gracefully)."""
    ...
```

**Call site:** In `autonomous_cycle.py`'s post-evidence step, after the review package
is built:
```python
# Best-effort — never blocks continuation
try:
    commit_supervisor_state(sprint_id)
except Exception as e:
    logger.warning(f"Supervisor state commit failed: {e} — continuing")
```

**Test:** Run autonomous_cycle on a test sprint. After completion, confirm `git status`
shows supervisor state files as committed.

**Risk:** Automated commits are sensitive. The commit must only touch the whitelist of
supervisor state files. A bug that stages product source accidentally would be bad.
Mitigation: Use explicit `git add <file>` for each whitelisted file (not `git add .`).
Add a pre-commit check that refuses to commit files not in SUPERVISOR_STATE_FILES.

**Tradeoff:** This changes git history by adding frequent small "supervisor state"
commits between product commits. Reviewers would see more noise. Acceptable because
these commits are clearly labeled and reflect real system state.

---

### Fix-RC-004: Validator Count — Single Source of Truth

**Current situation:** `expected_count` is hardcoded in:
- `tools/supervisor/governance_validator_runner.py`
- `tests/supervisor/test_governance_validators.py`
- `docs/` README
- CLAUDE.md Capability Index table

**Fix:** Make `governance_validator_runner.py` the ONLY source of truth.
Add a function: `get_expected_validator_count() -> int` that returns the count.
All tests import this function instead of hardcoding.

```python
# In governance_validator_runner.py
EXPECTED_VALIDATOR_COUNT = 165  # Single source of truth

def get_expected_validator_count() -> int:
    return EXPECTED_VALIDATOR_COUNT
```

```python
# In tests:
from tools.supervisor.governance_validator_runner import get_expected_validator_count

def test_validator_count():
    assert count == get_expected_validator_count()
```

**Test:** Add a new validator. Confirm only one file needs updating.

**Risk:** Low. This is a pure refactor with no behavior change.
Limit: Does not fix README/CLAUDE.md documentation sync (those are still manual).

---

### Fix-RC-005: Layer Plan Sync in Sprint Closeout

**File to create:** `tools/supervisor/sync_layer_plans.py`

**Purpose:** After each sprint, update the `repository_revision` in `plans/layers/master.md`
and `plans/layers/index.yaml` to match current HEAD.

```python
def sync_layer_plan_revision() -> None:
    """Update repository_revision in layer control plane to current HEAD."""
    head = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).strip()
    # Update plans/layers/master.md line: head: <hash>
    # Update plans/layers/index.yaml line: repository_revision: "<hash>"
```

**Note:** This only updates the revision hash. Full layer plan content (validator counts,
task states, maturity levels) requires a more extensive update process (TC-LA series).
The sync_layer_plans.py tool addresses the stale hash issue only, not full staleness.

**Test:** After a commit, run sync_layer_plans.py, confirm the hash in master.md matches HEAD.

**Risk:** Low for hash update. Higher for content updates (don't auto-update task states).

---

### Fix-RC-006: Plan Lock Cross-Session Auto-Recovery

**File to modify:** `tools/supervisor/check_continuation.py`

**Change:** In the plan lock check (Check 1b), before returning POST_PLAN_TERMINAL,
compare the lock's `session_id` with the current session's ID. If they differ, treat
the lock as STALE_DIFFERENT_SESSION, log a warning, and return CONTINUE instead of STOP.

```python
# In check_continuation.py Check 1b:
if lock.get("status") == "TERMINAL_CLOSED":
    lock_session = lock.get("session_id")
    current_session = get_current_session_id()
    if lock_session and current_session and lock_session != current_session:
        logger.warning(
            f"Plan lock TERMINAL_CLOSED belongs to session {lock_session}, "
            f"current session is {current_session}. Treating as STALE — continuing."
        )
        return verdict_continue(reason="STALE_TERMINAL_LOCK_DIFFERENT_SESSION")
    else:
        return verdict_stop(reason="POST_PLAN_TERMINAL")
```

**Test:** Write a TERMINAL_CLOSED lock with session_id "abc123". Run check_continuation
as session "def456". Confirm verdict is CONTINUE. Run as "abc123". Confirm STOP.

**Risk:** The session ID detection mechanism must be reliable. If `get_current_session_id()`
returns None or empty (e.g., in headless mode), the comparison fails and falls back to
the existing POST_PLAN_TERMINAL stop — which is the safe default.

**Limit:** This fix only prevents cross-session false stops. Within-session plan
completion still correctly returns POST_PLAN_TERMINAL (as designed by CLAUDE.md).

---

## PART 4 — EXECUTION PLAN (Taskcards)

### Priority Order (production-grade rationale)

1. Commit accumulated supervisor state (removes drift, gets repo into clean state)
2. Execute `PQ-019-020-CLI-STUBS` rework (highest-priority actionable item, no spec dependency)
3. Implement Fix-RC-001 (quality gate) — prevents next sprint from getting garbage work items
4. Implement Fix-RC-004 (validator count single source of truth) — low-risk, high leverage
5. Sprint closeout
6. Fixes RC-002, RC-003, RC-005, RC-006 go into future plan taskcards (bounded to this session's capacity)

### Taskcard Status Table (lifecycle_audit.py format)

| Taskcard | Title | Status |
|---|---|---|
| TC-SMR-001 | Commit accumulated supervisor state + evaluate .runner_system_id | CLOSED |
| TC-SMR-002 | Execute REWORK-PQ-019-020-CLI-STUBS (CLI entry points + type stubs, 20 packages) | CLOSED |
| TC-SMR-003 | Implement Fix-RC-001: Capability-compiler quality gate for "unknown" features | CLOSED |
| TC-SMR-004 | Implement Fix-RC-004: Single source of truth for validator expected_count | CLOSED |
| TC-SMR-005 | Persist remaining fixes as governed taskcards (RC-002, RC-003, RC-005, RC-006) | CLOSED |
| TC-SMR-006 | Sprint closeout: evidence declaration + autonomous-cycle + review package | CLOSED |

---

## TC-SMR-001: Commit Accumulated Supervisor State

**Why first:** The 17 uncommitted files create a dirty worktree that interferes with
governance validators and creates confusion about what's in HEAD vs what's pending.

**Files to commit (verified from git status):**
```
Group A — Supervisor pipeline outputs (auto-generated, safe to commit):
.supervisor/project-memory.md
.supervisor/state/current-run.json
.supervisor/state/watcher.json
reports/supervisor/approval-gates.md
reports/supervisor/contradictions.json
reports/supervisor/contradictions.md
reports/supervisor/discovery-summary.md
reports/supervisor/evidence-review.json
reports/supervisor/evidence-review.md
reports/supervisor/memory-sync-report.md
reports/supervisor/next-ruflo-lanes.json
reports/supervisor/next-sprint-taskmaster.json
reports/supervisor/next-sprint.md
reports/supervisor/session-resume.md

Group B — Plan state updates (from parallel-foraging-fairy v2 closeout):
plans/.claude/parallel-foraging-fairy.md

Group C — Tool fixes from parallel-foraging-fairy v2 (V149 upgrade):
tools/review/no_stub_scan.py
tools/supervisor/governance_validators_ext4.py
```

**Evaluate before committing:**
- `.runner_system_id` (untracked): Read its content. If it's a machine ID, add to
  `.gitignore` (not a repo artifact). If it's sprint-specific data, evaluate whether
  it belongs in `.local/` (gitignored) or `reports/`.

**Pre-commit check:**
```
python tools/supervisor/governance_validator_runner.py 2>&1 | tail -5
```
Confirm 0 blocking failures before committing tool modifications.

**Commit message:**
```
chore(supervisor): commit pipeline state and governance tool fixes from PFF+VWL sprints

Supervisor state: session-resume, approval-gates, next-sprint, evidence-review updated
Tool fixes (parallel-foraging-fairy v2):
- no_stub_scan.py: add NamedTemporaryFile/ruff-noqa allowlist, fods/fods exclude
- governance_validators_ext4.py: upgrade V149 validate_source_stubs to blocking FAIL

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

**Verification:** `git status` shows only .runner_system_id or gitignored files remaining.

---

## TC-SMR-002: Execute REWORK-PQ-019-020-CLI-STUBS

**What this is:** Extend CLI entry points and Python type stubs (`.pyi` files) to
all 20 Python format packages. This is the priority-1 rework item from next-work-items.json.

**Why this matters for production consistency:**
Without CLI entry points, installed packages don't register commands. Without type stubs,
IDEs can't provide completion and type checking. These are minimum viable professional
library features.

**Decomposition (20 packages × 2 concerns):**

**Part A — CLI Entry Points:**
For each format package, verify `pyproject.toml` or `setup.cfg` has a `[console_scripts]`
section. Minimum entry point: `format-factory-{fmt} = {fmt}.cli:main` where a `cli.py`
with a `main()` function exists.

Priority: packages that currently have NO cli.py. Check each of the 20 with:
```
ls src/python/*/cli.py 2>/dev/null
```

**Part B — Type Stubs:**
For each package's public API module, verify a `.pyi` stub file exists OR that
the package is typed (has `py.typed` marker). Minimum: `py.typed` marker file for
packages with complete type annotations.

```
ls src/python/**/py.typed 2>/dev/null
```

**Skill to use:** This task does NOT have a single registered skill that fully covers it.
The closest match is `add-python-api` (for adding API surface). Since no skill covers
CLI stubs exactly, generate an execution handoff via `tools/supervisor/choose_skill_or_handoff.py`:
```
python tools/supervisor/choose_skill_or_handoff.py \
  --task "PQ-019-020-CLI-STUBS" \
  --scope "cli entry points and type stubs, 20 packages"
```

**Constraint:** Every src/ change must be recorded in `reports/r90/product-code-change-ledger.json`.

**Execution approach:**
1. Audit which of 20 packages have cli.py (fast read-only pass)
2. Add `py.typed` markers to fully-typed packages (safest, lowest risk)
3. Add minimal cli.py with `main()` to packages that lack it (bounded)
4. Update pyproject.toml console_scripts for packages with cli.py
5. Run `.venv/Scripts/pytest tests/ -x -q` — confirm 0 failures
6. Record all changes in product-code-change-ledger.json

**Verification:** After execution, confirm:
- `python -m pip install src/python/fods -e . && format-factory-fods --help` works
- Or equivalent for at least 3 representative packages

**Risk:** 20 packages is broad scope. If any package has a cli.py conflict or test
failures, scope down to highest-priority packages (fods, fodt, csv, zst) and document
the partial completion honestly.

---

## TC-SMR-003: Implement Fix-RC-001 — Capability-Compiler Quality Gate

**File to modify:** Find the pipeline capability compiler first:
```
python -c "from tools.supervisor.capability_feature_compiler import *; print('found')"
# OR
ls tools/supervisor/capability*
```

**Then implement the quality gate** as described in Part 3 Fix-RC-001.

**Test it:**
```python
# Test: generate work items with known-unknown gap
# Confirm "unknown" items go to quarantine-needs-sal lane, not capability-compiler lane
```

**Verification:**
1. Run the compiler on current gap data
2. Confirm ABW/CSV chain items appear in quarantine-needs-sal lane
3. Confirm legitimate items (where spec_fact_name is known) remain executable
4. Run `next-work-items.json` generation — confirm no "Implement unknown" items in executable lanes

**Record change in product-code-change-ledger.json** if this touches `tools/supervisor/`.
(Check: does the ledger require entries for tools/ changes? If only src/ → skip ledger,
just add governance validator test.)

---

## TC-SMR-004: Implement Fix-RC-004 — Validator Count Single Source of Truth

**Files to modify:**
- `tools/supervisor/governance_validator_runner.py` — add `get_expected_validator_count()`
- `tests/supervisor/test_governance_validators.py` — import from runner, remove hardcode

**Implementation:**
```python
# governance_validator_runner.py
EXPECTED_VALIDATOR_COUNT = 165  # Update here only when adding validators

def get_expected_validator_count() -> int:
    """Single source of truth for expected governance validator count."""
    return EXPECTED_VALIDATOR_COUNT
```

```python
# test_governance_validators.py
from tools.supervisor.governance_validator_runner import get_expected_validator_count

def test_validator_count():
    # ... existing test logic ...
    assert count == get_expected_validator_count()  # No hardcode
```

**Verification:** Add a dummy validator, update EXPECTED_VALIDATOR_COUNT in one place,
confirm tests pass without editing the test file.

**Run tests:**
```
.venv/Scripts/pytest tests/supervisor/test_governance_validators.py -v
```

Expected: all pass.

---

## TC-SMR-005: Persist Remaining Fixes as Governed Taskcards

The remaining structural fixes (RC-002, RC-003, RC-005, RC-006) are out of scope
for this sprint's execution budget. They must become tracked taskcards.

**For each fix, register in `plans/layers/task-register.yaml`:**

RC-002 — Rework-first sprint selection:
```yaml
- task_id: TC-SMR-SUP-001
  stable_semantic_key: "rework-first-sprint-selection-protocol"
  primary_layer_id: L11
  title: "Add rework-first ordering to next-sprint generator"
  task_type: GOVERNANCE_INFRASTRUCTURE
  severity: HIGH
  priority: P1
  status: TODO
  fix_ref: SMR-RC-002
```

RC-003 — Supervisor state auto-commit:
```yaml
- task_id: TC-SMR-SUP-002
  stable_semantic_key: "supervisor-state-auto-commit"
  primary_layer_id: L09
  title: "Create commit_supervisor_state.py and wire into autonomous_cycle"
  task_type: GOVERNANCE_INFRASTRUCTURE
  severity: MEDIUM
  priority: P2
  status: TODO
  fix_ref: SMR-RC-003
```

RC-005 — Layer plan sync:
```yaml
- task_id: TC-SMR-SUP-003
  stable_semantic_key: "layer-plan-revision-sync"
  primary_layer_id: L10
  title: "Create sync_layer_plans.py to update HEAD revision in layer control plane"
  task_type: GOVERNANCE_INFRASTRUCTURE
  severity: MEDIUM
  priority: P2
  status: TODO
  fix_ref: SMR-RC-005
```

RC-006 — Plan lock cross-session auto-recovery:
```yaml
- task_id: TC-SMR-SUP-004
  stable_semantic_key: "plan-lock-cross-session-auto-recovery"
  primary_layer_id: L09
  title: "Modify check_continuation.py to auto-supersede TERMINAL_CLOSED locks from different sessions"
  task_type: MACHINERY_HEALING
  severity: HIGH
  priority: P1
  status: TODO
  fix_ref: SMR-RC-006
```

**Verification:** Open `plans/layers/task-register.yaml`, confirm 4 new entries are
syntactically valid YAML and readable by the task register tools.

---

## TC-SMR-006: Sprint Closeout

**Run ID:** `smr-001-{date}` (e.g., `smr-001-20260710`)

**Steps in order:**

1. Run full test suite and confirm 0 failures:
   ```
   .venv/Scripts/pytest tests/ -q 2>&1 | tail -10
   ```

2. Run governance validators and confirm ≤ 0 blocking failures:
   ```
   python tools/supervisor/governance_validator_runner.py 2>&1 | tail -10
   ```

3. Write evidence declaration:
   ```
   .local/evidences/smr-001-20260710/evidence-declaration.yaml
   ```
   Declare all work items (TC-SMR-001 through TC-SMR-005) with honest status.
   Use `sprint_executor_validate.py --repair` to validate before submission.

4. Run autonomous-cycle (NOT supervisor_loop.py — times out at 120s):
   ```
   python tools/supervisor/autonomous_cycle.py \
     --declaration .local/evidences/smr-001-20260710/evidence-declaration.yaml
   ```
   Exit 0 → continue. Exit 3 → log rework, continue. Exit 1/9 → log, continue.

5. Build review package:
   ```
   python tools/supervisor/build_declaration_review_package.py \
     --declaration .local/evidences/smr-001-20260710/evidence-declaration.yaml
   ```
   Print **absolute path** (C:\Users\prora\OneDrive\...) and SHA-256.

6. Run check_continuation.py:
   - CONTINUE → proceed to next sprint
   - POST_PLAN_TERMINAL → this plan has completed all taskcards, use --terminal flag below

7. Write plan lock:
   ```
   python tools/supervisor/write_plan_lock.py \
     --plan-path plans/.claude/shimmering-rolling-meerkat.md \
     --terminal
   ```
   (Note: this is product_deepening type, NOT machinery_hardening, so lifecycle_audit.py
   is not mandatory before --terminal. If `--audit-gate` is attempted and fails due to
   non-machinery plan type, fall back to plain `--terminal`.)

8. Final commit:
   ```
   git add plans/.claude/shimmering-rolling-meerkat.md \
     .local/evidences/smr-001-20260710/ \
     plans/layers/task-register.yaml \
     [any tool files modified by TC-SMR-003/004]
   ```
   Commit message: `feat(smr): product deepening + structural repair — cli stubs + quality gate`

9. Report to user with:
   - Review package absolute path + SHA-256
   - Test count (before and after)
   - Which structural fixes were implemented vs deferred to taskcards
   - "Plan shimmering-rolling-meerkat complete. All 6 taskcards closed."

---

## PART 5 — TRADEOFFS, RISKS, AND HONEST LIMITS

### What this plan cannot guarantee:

1. **TC-SMR-002 full completion across 20 packages** — if packages have significant
   variation in their public API surface, type stub generation could expand into a
   multi-session task. Acceptable partial completion: py.typed markers for all 20,
   cli.py for ≥ 10 most-used packages, documented list of remaining packages.

2. **Fix-RC-001 (quality gate) coverage** — the gate prevents new "unknown" items but
   does not remove existing unknown items already in the gap ledger. Those will need
   SAL ingestion (TC-SAL-001) to become real. The gate stops the bleeding; it doesn't
   heal the existing wound.

3. **Fix-RC-004 (validator count source of truth)** — only addresses the count tracking
   in governance_validator_runner.py and test files. The README and CLAUDE.md still
   require manual updates. Full fix requires either generated docs or CI that checks
   documentation count against the runtime value.

4. **The SAL pipeline gap (L01-SAL, TC-SAL-001)** — the root cause of the "unknown"
   feature problem in RC-001 is that spec facts haven't been ingested. This plan does
   NOT ingest spec facts. That work is TC-SAL-001, which is CRITICAL/P0 but requires
   a separate sprint with significant scope (17 dormant tools to activate, 20 formats
   to process). Without SAL ingestion, the capability-compiler will keep generating
   quarantined items indefinitely.

5. **Fix-RC-006 (plan lock cross-session auto-recovery)** — modifying `check_continuation.py`
   requires understanding the full session ID lifecycle. If the tool doesn't have a
   reliable way to get `current_session_id`, the fix can't be implemented safely without
   fallback testing. This is why it goes to a taskcard (TC-SMR-SUP-004) rather than
   being executed immediately.

### Likely limits of this sprint's impact:

This sprint addresses:
- Immediate state cleanup (uncommitted files) ✓
- One real product work item (CLI stubs) ✓
- One structural fix (quality gate) — prevents future symptom recurrence ✓
- One refactor fix (validator count) — reduces maintenance burden ✓
- Defers 4 structural fixes to governed taskcards ✓

This sprint does NOT address:
- SAL pipeline activation (biggest upstream blocker)
- Layer plan staleness (needs dedicated sync sprint)
- Rework accumulation protocol (governed taskcard)
- Supervisor state commit automation (governed taskcard)

### Confidence levels:

- TC-SMR-001 (commit state): HIGH confidence — mechanical, well-understood
- TC-SMR-002 (CLI stubs): MEDIUM confidence — 20 packages, some variance expected
- TC-SMR-003 (quality gate): HIGH confidence — bounded, testable change
- TC-SMR-004 (validator source of truth): HIGH confidence — pure refactor
- TC-SMR-005 (taskcard registration): HIGH confidence — mechanical YAML update
- TC-SMR-006 (closeout): HIGH confidence if tests pass — standard procedure

---

## PART 6 — KEY FILE PATHS (for navigation during execution)

| File | Role |
|---|---|
| plans/.claude/shimmering-rolling-meerkat.md | This plan (in-repo copy after TC-SMR-001) |
| .local/supervisor/next-work-items.json | Structured work queue (89 items) |
| .local/supervisor/continuation-signal.json | Continuation state (CONTINUE, iteration 6/12) |
| .local/supervisor/active-plan-lock.json | Plan lock (TERMINAL_CLOSED from VWL — stale, different session) |
| reports/supervisor/next-sprint.md | Advisory sprint context |
| reports/r90/product-code-change-ledger.json | Product change audit trail |
| plans/layers/task-register.yaml | Layer task register (add RC-002/003/005/006 taskcards here) |
| tools/supervisor/governance_validator_runner.py | Add get_expected_validator_count() here |
| tests/supervisor/test_governance_validators.py | Import from runner instead of hardcode |
| tools/supervisor/autonomous_cycle.py | Sprint closeout tool (NOT supervisor_loop.py) |
| tools/supervisor/check_continuation.py | Continuation verdict — returns CONTINUE as of deep audit |
| .supervisor/skill-registry.yaml | Skill registry (both dogfood skills are advisory_only: true) |

---

## MIGRATION NOTE (plan file)

Per MEMORY.md §MANDATORY: At session start, copy this plan to the in-repo location
and write the lock. This should happen as part of TC-SMR-001:
```
cp C:\Users\prora\.claude\plans\shimmering-rolling-meerkat.md \
   plans/.claude/shimmering-rolling-meerkat.md
python tools/supervisor/write_plan_lock.py \
  --plan-path plans/.claude/shimmering-rolling-meerkat.md
```
