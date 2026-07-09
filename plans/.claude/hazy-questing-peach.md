# Format Factory — Production-Grade System Healing Plan
# Mission: hazy-questing-peach
# Operating doctrine: SYSTEM-FIRST HEALING
# Created: 2026-07-09
# Scope: Structural machinery redesign + immediate unblock + product sprint

---

## Context: What Is Actually Broken

The previous plan treated SESSION_MISMATCH as a one-off nuisance to step around.
It is not. It is a symptom of a fundamental design conflict that will recur on every
session boundary until the machinery is fixed at the root.

This plan separates symptoms from root causes, proposes durable fixes, and executes
product work through the healed system.

---

## Diagnosis: Symptoms, Root Causes, Structural Weaknesses

### Visible Symptoms

| Symptom | Observable Evidence |
|---|---|
| `check_continuation.py` → STOP(SESSION_MISMATCH) | `continuation-signal.json` session_id=496b377beedd vs active session f0490ee640cf |
| `next-work-items.json` points to closed plan | `active_plan=stateless-juggling-robin.md`, `ledger_items_suppressed=true` |
| `selected-product-gaps.json` appears empty | Contains `[]` — no gaps available for selection |
| Untracked fods source files since Jul 6 | 19 Python files + Compat/ + spec/ showing as `??` in git status |
| `action-queue.jsonl` has 33-day-old entries | Queue grows monotonically, oldest from 2026-06-06 |

### Root Causes (confirmed from code)

**RC-1: The continuation signal encodes the CURRENT session ID, not the next session's.**

`autonomous_cycle.py` line 2085-2092 calls `get_or_create_session_identity()` for the
session currently running the cycle. This session_id is embedded in `continuation-signal.json`
at line 2120 and written at line 2155. Future sessions ALWAYS have a different session_id.
CCI-MVP's SESSION_MISMATCH check correctly detects this — but that means EVERY autonomous
sprint → new session transition hits SESSION_MISMATCH. The system cannot cross session
boundaries without manual intervention (`reset_track_signal.py`).

This is not a bug in the mismatch detector. It is a **design conflict** between two
simultaneously held rules:
- "Sessions must be isolated to prevent cross-chat state contamination" (CCI-MVP)
- "Autonomous execution never stops across session boundaries" (Supreme Directive)

These two rules are mutually incompatible with a session-scoped signal. The current
architecture resolves the conflict by requiring a manual reset step — but that step is
undocumented in the session startup checklist, not automatic, and breaks the "never stop"
promise silently.

**RC-2: `next-work-items.json` is stale because plan completion does not trigger refresh.**

`next-work-items.json` is written by `generate_next_worker_prompt.py` inside `autonomous_cycle.py`
(Step 4). It sets `ledger_items_suppressed=true` when a per-chat plan is IN_PROGRESS.
When `write_plan_lock.py --terminal` closes the plan, it DOES NOT call the capability compiler
or regenerate next-work-items.json. The suppression flag stays `true` until the NEXT
autonomous_cycle run — which requires an evidence declaration — which requires sprint work —
which requires a non-suppressed work item list. This is a **circular dependency / chicken-and-egg**.

**RC-3: `selected-product-gaps.json` is downstream of the suppression flag.**

The file does not fail to populate independently. The capability compiler skips writing
to selected-product-gaps.json when `ledger_items_suppressed=true`. The gaps exist in
`next-work-items.json`'s `gap_sourced_items` array (20+ entries), but are invisible to
work selection. Fixing RC-2 fixes this automatically.

**RC-4: Production Python source is gitignored by policy (`.gitignore` lines 113-114).**

Commit `9a9ff060` (2026-07-03) added:
```
src/python/fods/fods/
src/python/fods/fods/fods/
```
to `.gitignore`. The intent was to suppress pip editable-install build artifacts
(`src/python/{format}/{format}/{format}/` — the nested triple). But the pattern
`src/python/fods/fods/` also matches and excludes the actual source tree
(`src/python/fods/fods/models.py`, `spec/`, `Compat/` etc.).

The files ARE governance-compliant (spec_qname on all domain classes, Compat/ facades,
LOC within baseline caps), but they are NOT in git. This means:
- The repo is not reproducible from HEAD
- CI cannot verify source changes or test coverage
- Git status shows them as `??` (untracked, not hidden) — the gitignore was either
  recently added or is being partially overridden by another pattern

Evidence: Files modified 2026-07-03/04, gitignore pattern added 2026-07-03 in same
commit. The pattern suppression and the file creation happened in the same sprint but
the source wasn't committed before the gitignore took effect.

**RC-5: `action-queue.jsonl` grows unbounded with no aging or deduplication.**

The queue is append-only. Entries from 2026-06-06 (33 days old) are still present.
There is no consumer that marks entries as consumed, no TTL, and no deduplication guard.
This does not cause immediate failures but degrades performance of any queue scanner
and will produce false-positive stale-signal detections as the queue grows.

### Structural Weaknesses (root of recurrence)

**SW-1: Session-scoped signal vs. session-agnostic product work.**

Product ledger work (gap selection, feature implementation, sprint deepening) does not
belong to a single chat session. It is continuous, cross-session work. Per-chat PLANS
do belong to a single session. The current architecture incorrectly applies
session-scoping to the product signal, not just to plan locks.

**SW-2: No cross-artifact synchronization.**

Four state artifacts (continuation-signal.json, active-plan-lock.json,
next-work-items.json, approval-gates.md) are written by DIFFERENT tools at DIFFERENT
times with NO cross-triggering. Plan completion does not update the signal. Signal
reset does not refresh work items. The system relies on the correct SEQUENCE of
autonomous_cycle runs to maintain consistency — and any deviation (skip, crash, best-
effort skip) leaves them out of sync indefinitely.

**SW-3: Best-effort closeout creates compounding state debt.**

CLAUDE.md instructs: "if any closeout step fails, skip and continue." This means a
failed autonomous_cycle leaves:
- Stale session_id in signal
- Stale next-work-items.json (suppression flag wrong)
- Missing evidence declaration
- No guidance for the next sprint on what was done

Each "skip and continue" accumulates debt that the next sprint must clear before doing
real work — but the next sprint doesn't know debt exists (it starts from stale state).

**SW-4: SESSION_MISMATCH blocks too early.**

`check_continuation.py` runs the SESSION_MISMATCH check at Check 0b (lines 57-94),
before Check 7 (next-work-items validation at lines 466-483). When SESSION_MISMATCH
fires, the stale next-work-items state is never detected, reported, or diagnosed.
The agent sees one symptom and stops; the upstream cause (stale suppression flag)
is invisible.

---

## What Must Be Preserved

- CCI-MVP isolation for PER-CHAT PLANS (per-session plan locks work correctly)
- `active-plan-lock.json` and `plan-locks/*.json` mechanics (correct, well-tested)
- All 165 governance validators (passing)
- TERMINAL_CLOSED / SUPERSEDED lock semantics (correct)
- Oracle verification (73/73 PASS)
- Spec-to-feature correction plan architecture (spec_qname, Compat/, import direction)
- The Supreme Directive's hierarchy: TRUE_EXTERNAL_GATEs > POST_PLAN_TERMINAL > others

---

## What Must Be Redesigned

### Design Decision: Plan-Level Isolation, Signal-Level Continuity

The correct fix separates two concerns that are currently conflated:

1. **Per-chat plan lifecycle** → MUST be session-scoped (existing mechanism is correct)
2. **Product ledger continuation** → MUST be session-agnostic (current mechanism is wrong)

**Proposed: Two-tier session scoping**

| Artifact | Session scope | Rationale |
|---|---|---|
| `plan-locks/*.json` | PER-SESSION | Plans belong to one chat; isolation is correct |
| `active-plan-lock.json` | Shared (no session_id) | Already correct — mirrors the session lock |
| `continuation-signal.json` | SESSION-AGNOSTIC | Product ledger is continuous, not per-chat |
| `next-work-items.json` | SESSION-AGNOSTIC | Work items are product-level, not per-chat |

**Implementation: Remove session_id from continuation-signal.json (or make null for product track)**

In `autonomous_cycle.py` Step 8 (lines 2085-2092):
- If the signal is for product-track ledger work (no active plan): write `"session_id": null`
- If the signal is for an active per-chat plan: write current session_id (existing behavior)

In `check_continuation.py` Check 0b (SESSION_MISMATCH check):
- If `signal.session_id is null` → SKIP mismatch check (product signal, session-agnostic)
- If `signal.session_id is set AND a per-chat plan lock with that session_id is ACTIVE` → STOP(SESSION_MISMATCH)
- If `signal.session_id is set AND no per-chat plan is active` → allow continuation (stale session_id from prior plan run, but plan is closed)

This is **backwards compatible**: all existing SESSION_MISMATCH enforcement for active
per-chat plans is preserved. Only product-track signals lose the session lock.

### Design Decision: Plan Completion Must Trigger next-work-items Refresh

In `write_plan_lock.py --terminal` (or `--complete`):
- After writing the lock, call the minimum capability compiler to regenerate
  next-work-items.json with `ledger_items_suppressed=false`
- This breaks the circular dependency in RC-2/RC-3

Tradeoff: `write_plan_lock.py` gains a dependency on the capability compiler.
If the compiler fails, the lock is still written (plan is still closed), but
next-work-items refresh is best-effort (existing behavior preserved for lock writes).

### Design Decision: `.gitignore` Pattern Must Distinguish Build Artifacts from Source

The pattern `src/python/fods/fods/` excludes both:
- `src/python/fods/fods/build/` (legitimate build artifact to ignore)
- `src/python/fods/fods/models.py`, `spec/`, `Compat/` (production source to track)

Fix: Replace broad directory exclusion with specific artifact subdirectory exclusion:
```
# Before (too broad):
src/python/fods/fods/

# After (precise):
src/python/fods/fods/build/
src/python/fods/fods/__pycache__/
src/python/fods/fods/fods/        # nested package from pip install -e
```

This applies to ALL formats under `src/python/{format}/{format}/` — not just fods.
The pattern needs to be audited repo-wide before changing.

---

## Taskcard Status Table (required for lifecycle_audit.py)

| Taskcard | Status |
|---|---|
| TC-HQP-001 | CLOSED |
| TC-HQP-002 | CLOSED |
| TC-HQP-003 | CLOSED |
| TC-HQP-004 | CLOSED |
| TC-HQP-005 | CLOSED |
| TC-HQP-006 | CLOSED |
| TC-HQP-007 | CLOSED |
| TC-HQP-008 | CLOSED |

---

## TC-HQP-001 — Immediate Session Unblock

**Goal:** Unblock the current session so product work can proceed while the structural
fixes are implemented. This is a one-time manual step, NOT the permanent fix.

**Why this is safe:** `active-plan-lock.json` shows TERMINAL_CLOSED with the current
session_id (f0490ee640cf). No per-chat plan is active. Resetting the track signal does
not break any plan isolation guarantee.

**Steps:**
1. `python tools/supervisor/reset_track_signal.py --track product`
2. `python tools/supervisor/check_continuation.py` → must return `verdict=CONTINUE`
3. Record: expected `verdict=CONTINUE`, `session_id` updated to current session
4. If still STOP: read reason, diagnose, do NOT retry blindly

**Acceptance:** `check_continuation.py` exits 0, `verdict=CONTINUE`.
**Does not fix:** RC-1 (structural). Next session transition will hit SESSION_MISMATCH again.

---

## TC-HQP-002 — Fix `.gitignore` for Python Source Directories

**Goal:** Repair the `.gitignore` pattern that excludes production source from git tracking.

**Investigation first (read-only):**
1. Read `.gitignore` lines 110-120 exactly
2. Run `git check-ignore -v src/python/fods/fods/models.py` — confirm it IS ignored
3. Run `git check-ignore -v src/python/fods/fods/build/` — confirm build IS ignored
4. List all other formats: `src/python/*/` and check which ones have the same pattern

**If confirmed that source is gitignored:**

Edit `.gitignore`: Replace broad per-format directory exclusions with precise subdirectory
exclusions for build artifacts only. Pattern to apply for EACH affected format:

```gitignore
# Build artifacts only — NOT the source tree
src/python/{format}/{format}/build/
src/python/{format}/{format}/__pycache__/
src/python/{format}/{format}/{format}/   # nested package from pip install -e
```

Then untrack/re-track:
```bash
git rm -r --cached src/python/fods/fods/models.py  # if currently tracked (unlikely)
# OR: just add the file — git will track it after gitignore is fixed
git add src/python/fods/fods/models.py src/python/fods/fods/__init__.py \
        src/python/fods/fods/constants.py src/python/fods/fods/exceptions.py \
        src/python/fods/fods/parser.py src/python/fods/fods/writer.py \
        src/python/fods/fods/neutral_model.py src/python/fods/fods/fods_analytics.py \
        src/python/fods/fods/fods_analytics_extended.py \
        src/python/fods/fods/cli.py src/python/fods/fods/csv_exporter.py \
        src/python/fods/fods/fods_to_tsv.py src/python/fods/fods/fods_workflow.py \
        src/python/fods/fods/fods_cell_iterator.py src/python/fods/fods/fods_sheet_iterator.py \
        "src/python/fods/fods/spec/" "src/python/fods/fods/Compat/"
```

**Tradeoff:** If other formats have the same `.gitignore` pattern, they also have source
excluded from git. Audit ALL `src/python/` format directories before changing. The fix
must be global or the problem just shifts to other formats.

**Risk:** If `pip install -e` on the monorepo creates nested packages that git then tracks,
CI may pick up duplicated files. The `src/python/{format}/{format}/{format}/` nested
pattern guards against this — keep that exclusion.

**Acceptance:**
- `git check-ignore -v src/python/fods/fods/models.py` → returns nothing (not ignored)
- `git check-ignore -v src/python/fods/fods/build/` → returns the gitignore rule
- `git status` shows fods source files as ready to stage (not `??` but stageable)
- `git add` succeeds for all 15+ production source files

---

## TC-HQP-003 — Fix: Plan Completion Triggers next-work-items Refresh

**Goal:** Break the circular dependency (RC-2). When a per-chat plan completes,
next-work-items.json must be regenerated with ledger_items_suppressed=false.

**File to modify:** `tools/supervisor/write_plan_lock.py`

**Change:** After writing the TERMINAL_CLOSED or COMPLETE lock status, call the
minimum regeneration needed to update next-work-items.json:

```python
# After writing lock with status in ("COMPLETE", "TERMINAL_CLOSED"):
# Regenerate next-work-items.json with correct suppression flag
try:
    from pathlib import Path
    import json
    nwi_path = Path(".local/supervisor/next-work-items.json")
    if nwi_path.exists():
        nwi = json.loads(nwi_path.read_text())
        # Clear the active plan references since plan is now closed
        nwi["active_plan"] = None
        nwi["ledger_items_suppressed"] = False
        nwi["last_taskcard"] = None
        # Promote gap_sourced_items to items if items only has PLAN-ACTIVE
        if (len(nwi.get("items", [])) == 1
                and nwi["items"][0].get("item_id") == "PLAN-ACTIVE"):
            nwi["items"] = nwi.get("gap_sourced_items", [])
        nwi_path.write_text(json.dumps(nwi, indent=2))
        print(f"[write_plan_lock] next-work-items.json refreshed: ledger_items_suppressed=False")
except Exception as e:
    print(f"[write_plan_lock] WARN: could not refresh next-work-items.json: {e}")
    # Non-blocking — plan lock was already written successfully
```

**Test:** After running `write_plan_lock.py --terminal` on any test plan:
- `next-work-items.json` → `active_plan=null`, `ledger_items_suppressed=false`
- `items` list has real gap-sourced items (not just PLAN-ACTIVE)
- `check_continuation.py` after reset returns CONTINUE with real work items

**Regression:** Existing test for `write_plan_lock.py` must still pass.
Add new test case: plan close → next-work-items refreshed.

---

## TC-HQP-004 — Fix: Decouple Product Signal from Session ID (RC-1)

**Goal:** Remove session_id from product-track continuation signals so SESSION_MISMATCH
only fires when a per-chat plan is truly active and owned by a specific session.

**Files to modify:**
- `tools/supervisor/autonomous_cycle.py` — Step 8 signal writing (lines 2085-2155)
- `tools/supervisor/check_continuation.py` — Check 0b SESSION_MISMATCH logic (lines 57-94)

**Change in autonomous_cycle.py:**

```python
# Step 8: Determine session_id for signal
# Only embed session_id when a per-chat plan is currently IN_PROGRESS
# For product-track (no active plan), emit null session_id
active_lock = _read_active_plan_lock()  # existing helper or add one
plan_is_active = (
    active_lock is not None
    and active_lock.get("status") == "IN_PROGRESS"
)
if plan_is_active:
    # Per-chat plan is running — session-scope the signal
    session_id = _cci_identity.session_id
else:
    # Product track — session-agnostic
    session_id = None
```

**Change in check_continuation.py Check 0b:**

```python
# SESSION_MISMATCH check — only enforce when signal is session-scoped
signal_session = signal.get("session_id")
caller_session = get_current_session_id()

if signal_session is None:
    # Product-track signal (session-agnostic) — no mismatch possible
    pass
elif signal_session != caller_session:
    # Check whether a per-chat plan was IN_PROGRESS for that session
    # If the plan is CLOSED (TERMINAL_CLOSED/COMPLETE/SUPERSEDED), allow continuation
    prior_lock = find_plan_lock_for_session(signal_session)
    prior_plan_active = (
        prior_lock is not None
        and prior_lock.get("status") == "IN_PROGRESS"
    )
    if prior_plan_active:
        # Prior session still owns an active plan — hard stop
        return stop_result("SESSION_MISMATCH", detail=f"Prior session {signal_session} has active plan")
    # Prior plan is closed or never existed — allow continuation
    # (stale session_id from a completed plan run, safe to proceed)
```

**Tradeoff:**
- Weakens isolation slightly for the product track between two simultaneous chat sessions
  both doing product work. In practice this is rare (one conversation at a time) and the
  plan lock mechanism still prevents per-chat plans from interfering.
- Preserves full SESSION_MISMATCH enforcement for the case that actually matters: when
  one session has an IN_PROGRESS per-chat plan and another session tries to consume it.

**Test cases to add:**
1. Signal with `session_id=null` + any caller session → CONTINUE (product track)
2. Signal with `session_id=A` + plan for A is IN_PROGRESS + caller is B → STOP(SESSION_MISMATCH)
3. Signal with `session_id=A` + plan for A is TERMINAL_CLOSED + caller is B → CONTINUE
4. Signal with `session_id=A` + no plan lock for A + caller is B → CONTINUE

**Regression:** All existing SESSION_MISMATCH tests must pass (they test the case where
plan IS IN_PROGRESS, which is still enforced).

---

## TC-HQP-005 — Fix: action-queue.jsonl Aging + Deduplication

**Goal:** Prevent unbounded growth of action-queue.jsonl (33-day-old entries present).

**File:** `.local/supervisor/action-queue.jsonl`

**Change:** Add a GC step to `autonomous_cycle.py` Step 0-pre (alongside existing lock GC):

```python
# GC action-queue.jsonl: remove entries older than 7 days
_gc_action_queue(queue_path, max_age_days=7)
```

```python
def _gc_action_queue(queue_path: Path, max_age_days: int = 7) -> None:
    if not queue_path.exists():
        return
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
    lines = queue_path.read_text(encoding="utf-8").splitlines()
    kept = []
    for line in lines:
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
            queued_at_str = entry.get("queued_at") or entry.get("created_at")
            if queued_at_str:
                queued_at = datetime.fromisoformat(queued_at_str)
                if queued_at.tzinfo is None:
                    queued_at = queued_at.replace(tzinfo=timezone.utc)
                if queued_at < cutoff:
                    continue  # drop old entry
        except Exception:
            pass
        kept.append(line)
    queue_path.write_text("\n".join(kept) + "\n", encoding="utf-8")
```

**Acceptance:** After running autonomous_cycle, entries older than 7 days are removed.
**Test:** Write queue with known-old entries → run GC → old entries removed, recent kept.

---

## TC-HQP-006 — Commit Untracked fods Source (After gitignore Fix)

**Goal:** After TC-HQP-002 resolves the gitignore, commit the fods production source
to make HEAD reproducible.

**Pre-flight governance checks (all must pass before commit):**
1. `python tools/supervisor/governance_validator_runner.py` → all 165 validators PASS
2. `.venv/Scripts/pytest tests/python/fods/ -x -q` → 0 failures
3. Source baseline: `src/python/fods/fods/fods_analytics.py` cap=1121 (MUST NOT increase)
4. Verify spec_qname on all new classes committed (V111 must pass)
5. Every staged source file must have a ledger entry in `reports/r90/product-code-change-ledger.json`

**Ledger entries required:**
- One entry per new module added: models.py, Compat/ (16 files), spec/ subtree
- `traceability_chain`: spec_fact_id → qname → capability_id → taskcard_id → source file
- Include test file references

**Files explicitly NOT to commit:**
- `src/python/fods/fods/build/` (build artifact)
- `src/python/fods/fods/__pycache__/` (build artifact)
- `src/python/fods/fods/fods/` (nested package from pip install)

**Commit message must include:**
- "feat(fods): add spec-shaped domain model, Compat facades, and spec/ hierarchy"
- Reference: TC-HQP-006, spec_qname mappings, capability_ids

**Acceptance:** `git log --oneline -1` shows the commit; `git status` shows clean tree for
fods source; `git show --stat HEAD` lists the fods source files.

---

## TC-HQP-007 — Product Gap Selection and Sprint Work

**Goal:** Execute at least one governed product gap after the system is healed.
All work must flow through the healed system, not around it.

**Pre-conditions:** TC-HQP-001 through TC-HQP-003 must be complete (system healed).

**Steps:**
1. Run `python tools/supervisor/check_continuation.py`
   → Must return CONTINUE with non-empty work items
   → `selected-product-gaps.json` must have at least one entry (not `[]`)
2. Load highest-priority gap from `selected-product-gaps.json`
3. Run the appropriate governed skill (per capability_id in the gap entry)
4. Every `src/` change requires a ledger entry in `reports/r90/product-code-change-ledger.json`
5. Run `governance_validator_runner.py` after each file change
6. Run `.venv/Scripts/pytest tests/{format}/ -x` after each source change
7. Apply SYSTEM-FIRST HEALING: if tests fail → trace to first failing boundary →
   heal shared test machinery OR fix source → re-run → never patch derived output only

**Traceability chain required per RULE-LIB-010:**
`spec_fact_id → qname → capability_id → taskcard_id → source file`

**Acceptance:** At least 1 gap closed; 0 test failures; ledger entry written;
governance validators all pass.

---

## TC-HQP-008 — Sprint Closeout with Healed Signal

**Goal:** Close the sprint using the healed autonomous_cycle (TC-HQP-004 in place),
confirming that the new signal is session-agnostic.

**Steps:**
1. Run new-violation detector (inline Python from CLAUDE.md Step 0)
2. Write `.local/evidences/hazy-questing-peach-{timestamp}/evidence-declaration.yaml`
3. Validate: `python tools/supervisor/sprint_executor_validate.py <decl> --repair`
4. Run: `python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration <decl>`
5. **Verify the new signal:** `cat .local/supervisor/continuation-signal.json | python -c "import sys,json; s=json.load(sys.stdin); print('session_id:', s.get('session_id')); assert s.get('session_id') is None, 'FAIL: session_id should be null for product track'"`
6. Run: `python tools/supervisor/check_continuation.py` from THIS session → CONTINUE
7. **Regression test (simulate next session):** Temporarily set env var to a fake session_id and run check_continuation → should still return CONTINUE (not SESSION_MISMATCH) because signal has null session_id
8. Build review package: `python tools/supervisor/build_declaration_review_package.py --declaration <decl>`
9. Print absolute path + SHA-256 of ZIP
10. Run: `python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/hazy-questing-peach.md --terminal`

**Acceptance:** autonomous-cycle exits 0; signal has `session_id=null`; check_continuation
returns CONTINUE from a simulated different session; ZIP generated with absolute path printed.

---

## Implementation Order and Dependencies

```
TC-HQP-001 (session unblock — immediate)
    ↓
TC-HQP-002 (gitignore fix — foundational for TC-HQP-006)
TC-HQP-003 (next-work-items refresh — foundational for TC-HQP-007)
TC-HQP-004 (signal session decoupling — foundational for TC-HQP-008)
TC-HQP-005 (queue GC — independent, can run anytime)
    ↓
TC-HQP-006 (fods commit — requires TC-HQP-002)
TC-HQP-007 (product work — requires TC-HQP-001 + TC-HQP-003)
    ↓
TC-HQP-008 (closeout with healed system — requires TC-HQP-004)
```

TC-HQP-002/003/004/005 can execute in parallel (independent files).

---

## Validation Plan (End-to-End)

| Test | Expected Outcome | Regression Risk |
|---|---|---|
| `check_continuation.py` after TC-HQP-001 | `verdict=CONTINUE` | Low |
| `git check-ignore` on fods source after TC-HQP-002 | Not ignored | Medium — other formats |
| `next-work-items.json` after TC-HQP-003 plan close | `ledger_items_suppressed=false` | Medium — work selection |
| `continuation-signal.json` after TC-HQP-004 cycle | `session_id=null` | High — existing SESSION_MISMATCH tests |
| SESSION_MISMATCH still fires for active plans | STOP(SESSION_MISMATCH) | High — must not weaken |
| `action-queue.jsonl` after TC-HQP-005 GC | Entries < 7 days old only | Low |
| `git status` after TC-HQP-006 commit | fods source files tracked and committed | Low |
| `governance_validator_runner.py` throughout | All 165 validators PASS | Medium |
| `.venv/Scripts/pytest -q` throughout | 0 failures (baseline: 1634 pass) | Medium |

---

## Tradeoffs and Honest Limits

**What this plan does NOT solve:**

1. **Best-effort closeout compounding debt (SW-3):** The Supreme Directive's "skip closeout
   and continue" policy will continue to create state divergence whenever autonomous_cycle
   is skipped. The fixes in TC-HQP-003/004 reduce the blast radius of a skipped cycle,
   but do not eliminate it. A more durable fix would require autonomous_cycle to be
   mandatory (not best-effort) — which conflicts with the Supreme Directive. This tension
   is unresolved and must be accepted as a known limit.

2. **Signal deduplication across stream paths:** autonomous_cycle.py writes the signal to
   three paths (signal_path, _legacy_signal_path, streams/{stream}/continuation-signal.json).
   These writes are sequential, not atomic. A crash between writes leaves inconsistent state.
   Full fix requires transactional state writes (e.g., write to a .tmp file, then rename).
   This is out of scope for this plan but should be tracked as a known structural gap.

3. **TC-HQP-004 weakens isolation in theory:** If two simultaneous chat sessions run product
   ledger work without per-chat plans, they could corrupt each other's state. In practice this
   doesn't happen (one conversation at a time), but the architectural risk is real. Accepted
   tradeoff: correctness in the common case over theoretical purity in the impossible case.

4. **gitignore audit scope:** TC-HQP-002 may discover that other format packages
   (`csv`, `tsv`, `ods`, etc.) have the same problematic gitignore pattern. The scope of
   the fix could expand significantly. If more than 3 formats are affected, this taskcard
   should be extended before the commit step.

5. **action-queue.jsonl consumer is undefined:** The GC in TC-HQP-005 removes old entries
   but does not validate that entries are being consumed in order or at all. If the queue
   consumer is broken, GC just delays the symptom. This should be investigated separately.

---

## Critical Files

| File | Role | Taskcard |
|---|---|---|
| `tools/supervisor/check_continuation.py` lines 57-94 | SESSION_MISMATCH check | TC-HQP-004 |
| `tools/supervisor/autonomous_cycle.py` lines 2085-2155 | Signal writing | TC-HQP-004 |
| `tools/supervisor/write_plan_lock.py` | Plan lock + next-work-items refresh | TC-HQP-003 |
| `.gitignore` lines 113-114 | Source exclusion | TC-HQP-002 |
| `.local/supervisor/continuation-signal.json` | Stale signal | TC-HQP-001 (immediate) |
| `.local/supervisor/next-work-items.json` | Suppressed work items | TC-HQP-003 |
| `.local/supervisor/action-queue.jsonl` | Unbounded queue | TC-HQP-005 |
| `src/python/fods/fods/` (all source) | Untracked production source | TC-HQP-006 |
| `reports/r90/product-code-change-ledger.json` | Source change audit trail | TC-HQP-007 |


<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-07-09T13:36:50.366647+00:00"
  locked_by: "f0490ee640cf"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->


---

## CLOSURE_RECORD

status: CONVERGENCE_COMPLETE_ALL_GREEN_AND_TASK_CLOSED
closed_at: 2026-07-09T14:00:00Z
commits:
  - 5eae2cd7  fix(fods): repair gitignore + commit spec-shaped source (TC-HQP-002/006)
  - 3683579e  fix(supervisor): heal TC-PGI-041, decouple session_id, add queue GC (TC-HQP-003/004/005)
  - d8c105db  feat(dif): 3 gap closures + in-repo plan (TC-HQP-007/step-0)
  - aec0e84d  chore(ledger): DIF gap closure entry
  - cec008c6  chore: supervisor state + oracle reports
  - 3f5d13f2  chore: SAL/QName audit reports + DIF fixture
verification:
  governance_validators: 194 passed, 0 failed
  dif_gap_tests: 14 passed, 0 failed
  fods_tests: 1571 passed, 0 failed
  plan_lock: TERMINAL_CLOSED
  signal_session_id: null
  nwi_suppressed: false
  git_status: clean (only gitignored state files remain)
convergence_iterations: 1
findings_consumed: 5  # L1-001..003, L2-001..002 (uncommitted deliverables)
