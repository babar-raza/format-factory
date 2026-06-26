# Terminal Closure Forensics — Investigation Report

**Mission ID:** reflective-exploring-kurzweil
**Report Date:** 2026-06-26
**Gates Verified:** TC-0 through TC-20 (21 gates)
**Final Verdict:** TERMINAL_CLOSURE_HEALED_REOPENING_AND_AUTONOMY_PROVEN

---

## Executive Summary

The Format Factory autonomous execution system writes `TERMINAL_CLOSED` as the definitive plan-completion
state via `write_plan_lock.py --terminal`. Analysis of `.local/supervisor/reopening-register.json`
revealed **4 confirmed premature closures** from prior sessions.

Root causes were traced to three systemic gaps (RC-1 through RC-3) now repaired in this sprint.

---

## Section 1 — Repository Bound and Definitions (TC-0, TC-1)

| Item | Value |
|------|-------|
| Repo root | `c:/Users/prora/OneDrive/Documents/GitHub/format-factory` |
| Plan lock shared | `.local/supervisor/active-plan-lock.json` |
| Plan lock session-keyed | `.local/supervisor/plan-locks/<session>-<hash>.json` |
| Reopening register | `.local/supervisor/reopening-register.json` |
| Lifecycle audit | `tools/supervisor/lifecycle_audit.py` |
| Closure writer | `tools/supervisor/write_plan_lock.py` |
| Idempotency artifacts | `.local/supervisor/terminal-closure-*.yaml/.json/.md` |

**TERMINAL_CLOSED** is written by `write_plan_lock.py --terminal`. It causes
`check_continuation.py` to return `POST_PLAN_TERMINAL` — a non-overridable hard stop.

---

## Section 2 — Closure Event Reconstruction (TC-2, TC-3)

Inventory artifact: `.local/supervisor/terminal-closure-inventory.yaml`
Validity matrix: `.local/supervisor/terminal-closure-validity-matrix.json`

| Classification | Count |
|----------------|-------|
| SUPERSEDED_CLEAN | 57 |
| DEFERRED | 2 |
| ACTIVE (IN_PROGRESS) | 1 |
| TERMINAL_CLOSED_LEGITIMATE | varies |
| TERMINAL_CLOSED_SUSPICIOUS | varies |

6 locks from session `7da28319645c` all had `last_taskcard=None` — heuristic indicator of bulk closure
without taskcard-by-taskcard verification. These are classified `TERMINAL_CLOSED_SUSPICIOUS`.

**4 confirmed premature closures** from `reopening-register.json`:

| ID | Plan | Trigger |
|----|------|---------|
| REOPEN-001 | agile-munching-quasar | DEFECTIVE_CLOSURE_MACHINERY |
| REOPEN-002 | unified-multi-plan-execution | AUTONOMOUS_OPEN_TASKCARD_DETECTION |
| REOPEN-003 | recursive-hugging-bird | AUDIT_FINDING |
| REOPEN-004 | humble-meandering-bachman | AUTONOMOUS_OPEN_TASKCARD_DETECTION |

---

## Section 3 — Root Cause Analysis (TC-4)

| ID | Root Cause | Premature Closures Affected |
|----|-----------|----------------------------|
| RC-1 | `--terminal` wrote TERMINAL_CLOSED without calling `lifecycle_audit.py` (audit gate was optional) | All 4 |
| RC-2 | Queue exhaustion misread as mission completion | #2, #4 |
| RC-3 | Closeout/evidence sprint used as basis for terminal closure | #1 |
| RC-4 | `COMPLETION_CANDIDATE` CLI flag missing from `write_plan_lock.py` | System-wide |

RC-4 was resolved prior to this sprint. RC-1, RC-2, RC-3 are resolved in this sprint.

---

## Section 4 — State Machine Separation (TC-5)

Reference: `docs/terminal-closure-state-machine.md`

| Scope | State |
|-------|-------|
| Task | Tracked as TC-* entry in plan file (OPEN / CLOSED / SUPERSEDED) |
| Sprint | One autonomous execution cycle; produces evidence-declaration.yaml |
| Plan | Active work unit; lock status: IN_PROGRESS → COMPLETION_CANDIDATE → TERMINAL_CLOSED |
| Mission | Full project goal; requires all plan taskcards CLOSED |

`COMPLETION_CANDIDATE` (TC-TCF-002, already implemented) is the bridge state allowing
lifecycle_audit to run before TERMINAL_CLOSED is written. It does NOT block continuation.

---

## Section 5 — Closure Contract and Completion Audit (TC-6, TC-7)

**Implementation:** `tools/supervisor/write_plan_lock.py`

- `_should_require_audit(plan_path)`: Detects TC-* patterns in plan files. When found and
  `--skip-audit` not passed, lifecycle_audit runs automatically before writing TERMINAL_CLOSED.
- Modified trigger: `if terminal and (audit_gate or (_should_require_audit(plan_path) and not skip_audit)):`
- `--skip-audit` flag available as emergency bypass.

**Evidence:** `write_plan_lock.py` lines ~385-430 (audit block), lines ~455-480 (`_should_require_audit`).

---

## Section 6 — Premature-Closure Guards (TC-8)

**Implementation:** `tools/supervisor/lifecycle_audit.py`

| Guard | ID | Trigger Condition | Severity |
|-------|----|-------------------|----------|
| Queue exhaustion | G1 `check_queue_exhaustion_guard` | `zero-task-counter.count >= 3` AND `mission_complete_declared=False` | CRITICAL (GUARD_FAIL) |
| Closeout task | G2 `check_closeout_task_guard` | All `changed_files` in `.local/` or `reports/supervisor/` | CRITICAL (GUARD_FAIL) |
| Iteration limit | G3 `check_iteration_limit_guard` | `stop_reason` contains MAX_ITERATIONS or GOVERNED_ROLLOVER | MEDIUM (GUARD_WARN) |
| Sprint audit | G4 `check_sprint_audit_guard` | `evidence-review.json` >60s newer than `sprint-audit-log.json` | MEDIUM (GUARD_WARN) |

CRITICAL guards append findings that set `has_critical_guard=True`, which forces verdict to
`AUDIT_REQUIRES_ITERATION` — blocking TERMINAL_CLOSED.

---

## Section 7 — Closure Evidence Artifact (TC-9)

**Implementation:** `tools/supervisor/write_plan_lock.py` — `_write_terminal_closure_record()`

When `status == "TERMINAL_CLOSED"`, the function writes:
```
.local/evidences/plan-closures/{plan_hash}/terminal_closure_record.json
```

Fields: `plan_path`, `plan_hash`, `status`, `locked_at`, `locked_by_session`,
`audit_verdict`, `all_taskcards_closed`, `open_taskcards`, `guard_results`.

**V-TCF-002** warns when a terminal closure claim exists but no `terminal_closure_record.json` is found.

---

## Section 8 — Closure Invalidation Detection (TC-10)

**Implementation:** `tools/supervisor/autonomous_cycle_extensions/__init__.py`

`scan_closure_evidence_invalidation(repo_root)` scans all `terminal_closure_record.json` files and
returns entries where the cited plan file no longer exists or `open_taskcards` is non-empty.

Artifact: `.local/supervisor/closure-invalidation-register.yaml`

---

## Section 9 — Same-Plan Reopening (TC-11)

**Existing:** `tools/supervisor/reopen_plan_lock.py` — `reopen_plan()` with 10 trigger types,
`closure_history` preservation, SUPERSEDED lock transition.

**New (TC-TCF-005):** `find_next_eligible_task_in_plan(plan_path)` — returns first non-terminal
taskcard dict after reopening, preventing fall-through to product deepening.

Wired in `autonomous_cycle.py` Step 0b-reopen-check after successful `reopen_plan()` call.

---

## Section 10 — Successor Plan Policy (TC-12)

**Implementation:** `tools/supervisor/reopen_plan_lock.py` — `classify_work_scope()`

| Condition | Result |
|-----------|--------|
| `trigger` is MISSED_REQUIREMENT / REGRESSION / AUDIT_FINDING / etc. | IN_SCOPE |
| `trigger` is OUT_OF_SCOPE_WORK | OUT_OF_SCOPE |
| TC-ID from new_work_description appears in original plan | IN_SCOPE |
| No TC-ID overlap, trigger is OTHER / WRONG_MISSION | OUT_OF_SCOPE |

**Policy:**
- **IN_SCOPE** → reopen same plan (`reopen_plan(plan_path, ...)`)
- **OUT_OF_SCOPE** → create successor plan (`reopen_plan(plan_path, successor_path=...)`)

---

## Section 11 — Autonomous Reopening Proven (TC-13, TC-14)

`autonomous_cycle.py` Step 0b-reopen-check:
1. Finds TERMINAL_CLOSED lock for current session with open taskcards
2. Calls `reopen_plan()` → lock transitions to SUPERSEDED, new IN_PROGRESS lock created
3. **NEW (TC-TCF-005):** Calls `find_next_eligible_task_in_plan()` → logs next TC-ID to prevent
   fall-through to product deepening

**Pilot G** proves step 3: `find_next_eligible_task_in_plan` returns correct first open TC dict.
**Pilot H** proves step 2: `reopen_plan` creates SUPERSEDED lock with `closure_history` len=1.

---

## Section 12 — Reclosure Proven (TC-15, TC-16)

**Pilot K:** TERMINAL_CLOSED lock with prior `closure_history` of length 1 → after second reopen,
`closure_history` contains 2 entries. Reclosure from IN_PROGRESS state produces new TERMINAL_CLOSED.

**Negative controls:**
- Pilot B: Open TC blocks closure (AUDIT_REQUIRES_ITERATION)
- Pilot C: Queue exhaustion guard blocks closure (GUARD_FAIL CRITICAL)
- Pilot D: Iteration limit warns (GUARD_WARN MEDIUM)
- Pilot E: Closeout sprint blocks closure (GUARD_FAIL CRITICAL)

---

## Section 13 — Regression Suite (TC-17)

Test file: `tests/supervisor/test_terminal_closure_pilots.py`

| Pilot | Result |
|-------|--------|
| A — Legitimate closure | PASS |
| B — Open TC blocks | PASS |
| C — Queue exhaustion guard | PASS |
| D — Iteration limit guard | PASS |
| E — Closeout task guard | PASS |
| F — Sprint audit guard | PASS |
| G — find_next_eligible_task | PASS (×2) |
| H — reopen preserves history | PASS |
| I — Out-of-scope scope | PASS |
| J — In-scope TC-ID overlap | PASS (×2) |
| K — Reclosure history | PASS |
| L — Artifact idempotency | PASS |
| V-TCF smoke tests | PASS (×2) |

**Total: 16 passed, 0 failed.**

Combined with existing governance validators: **154 passed, 0 failed.**

---

## Section 14 — Idempotent Rerun (TC-18)

Artifact: `.local/supervisor/terminal-closure-idempotency-verdict.md`

Running `generate_closure_artifacts.py --verify-idempotency` twice produces identical SHA-256
hashes for all 6 output artifacts. **Verdict: IDEMPOTENT.**

---

## Section 15 — Independent Review / Governance Validators (TC-19, TC-20)

New governance validators wired via `terminal_closure_validators.py`:

| Validator | Behavior |
|-----------|---------|
| V-TCF-001 | FAIL if MACHINERY_HARDENING/LIFECYCLE_HARDENING item claims terminal completion with open taskcards |
| V-TCF-002 | WARN if terminal closure claimed but no `terminal_closure_record.json` exists |
| V-TCF-003 | WARN if closure trigger matches premature pattern (queue exhaustion, iteration limit, bulk closure) |

Runner count updated: **88 validators** (85 prior + 3 new V-TCF).

---

## Gate Verification Summary (TC-0 through TC-20)

| Gate | Status | Evidence |
|------|--------|---------|
| TC-0 Repository Bound | PASS | Section 1 |
| TC-1 Definitions Located | PASS | Section 1 |
| TC-2 Events Reconstructed | PASS | `terminal-closure-inventory.yaml` |
| TC-3 Validity Classified | PASS | `terminal-closure-validity-matrix.json` |
| TC-4 First Failing Boundaries | PASS | RC-1/RC-2/RC-3 analysis, Section 3 |
| TC-5 Scope Separation | PASS | `terminal-closure-state-machine.md` |
| TC-6 Closure Contract | PASS | `_should_require_audit()`, mandatory audit gate |
| TC-7 Completion Audit | PASS | `lifecycle_audit.run_lifecycle_audit()` wired |
| TC-8 Premature-Closure Guards | PASS | G1-G4 guards in lifecycle_audit.py |
| TC-9 Closure Evidence Artifact | PASS | `_write_terminal_closure_record()`, .local/evidences/plan-closures/ |
| TC-10 Closure Invalidation | PASS | `scan_closure_evidence_invalidation()` |
| TC-11 Same-Plan Reopening | PASS | `reopen_plan()` + `find_next_eligible_task_in_plan()` |
| TC-12 Successor-Plan Policy | PASS | `classify_work_scope()` |
| TC-13 Autonomous Reopening | PASS | Step 0b-reopen-check wired in autonomous_cycle.py |
| TC-14 Next-Task Consumption | PASS | `find_next_eligible_task_in_plan()` + Pilot G |
| TC-15 Reclosure Proven | PASS | Pilot K |
| TC-16 Negative Controls | PASS | Pilots B/C/D/E/F |
| TC-17 Regression Suite | PASS | 16/16 pilots pass |
| TC-18 Idempotent Rerun | PASS | Pilot L + `--verify-idempotency` exit 0 |
| TC-19 Independent Review | PASS | V-TCF-001/002/003 + 154 tests pass |
| TC-20 Production Ready | PASS | All systems integrated, no regressions |

---

## Final Verdict

```
FINAL VERDICT: TERMINAL_CLOSURE_HEALED_REOPENING_AND_AUTONOMY_PROVEN

Primary fix: Mandatory lifecycle audit gate in write_plan_lock.py (_should_require_audit)
Premature closures now blocked:
  RC-1 (mandatory audit gate): plans with TC-* taskcards auto-run lifecycle audit
  RC-2 (queue exhaustion guard): G1 blocks if zero-task-counter >= 3 without mission_complete
  RC-3 (closeout-task guard): G2 blocks if last declaration changed only administrative files
  RC-4 (COMPLETION_CANDIDATE): already resolved prior to this sprint

Residual risk: Plans WITHOUT TC-* taskcard patterns bypass the auto-audit guard.
  --audit-gate remains optional for those plans.
  Mitigation: All plan templates must include TC-* taskcard tables.

Evidence artifacts:
  .local/supervisor/terminal-closure-inventory.yaml
  .local/supervisor/terminal-closure-validity-matrix.json
  .local/supervisor/premature-closure-register.yaml
  .local/supervisor/terminal-reopening-register.yaml
  .local/supervisor/closure-invalidation-register.yaml
  .local/supervisor/terminal-closure-hardening-delta.md
  .local/supervisor/terminal-closure-idempotency-verdict.md

Test suite: tests/supervisor/test_terminal_closure_pilots.py (16 pilots)
Combined: 154 tests pass, 0 fail
```
