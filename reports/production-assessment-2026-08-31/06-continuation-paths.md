# 06 — Continuation Paths

**Baseline commit:** dd909cf3a

## Path 1: Generic Supervisor Continuation
- **Entry:** check_continuation.py
- **State read:** .local/supervisor/continuation-signal.json (ephemeral, gitignored)
- **State written:** None (read-only check)
- **Task selection:** Reads next_work_items_path from signal
- **Verification gates:** 23+ STOP reasons checked
- **Bypasses:** 17/23 overridden by Supreme Directive
- **Terminal:** TRUE_EXTERNAL_GATEs only (5 members) + 4 CCI non-overridable
- **Restart:** NO_SIGNAL from clean state → overridden → reads next-sprint.md directly
- **Idempotent:** Yes (pure read)
- **Concurrency:** session_id field prevents cross-chat consumption
- **Makes product progress:** No (meta-coordination only)

## Path 2: Per-Chat Plan Locking
- **Entry:** write_plan_lock.py (CLAUDE.md Step 0)
- **State read:** System message for plan path
- **State written:** .local/supervisor/plan-locks/{session_id}.json
- **Task selection:** Plan taskcards in sequential order
- **Verification gates:** Lifecycle audit for machinery plans
- **Bypasses:** None — plan lock is the highest precedence
- **Terminal:** --terminal flag → POST_PLAN_TERMINAL (non-overridable)
- **Restart:** Lock file persists across session restarts
- **Idempotent:** Yes (lock is write-once per session)
- **Concurrency:** Session-scoped locks
- **Makes product progress:** Depends on plan content

## Path 3: FF6 Goal Driver
- **Entry:** goal_driver.py resume
- **State read:** controller-state.yaml + product-goal.yaml + obligations/*.yaml (all committed)
- **State written:** None (read-only)
- **Task selection:** Identifies unassessed/uncertified formats, reports next action
- **Verification gates:** None — reads labels, doesn't verify proof
- **Bypasses:** N/A (no gates to bypass)
- **Terminal:** GOAL_ACHIEVED (6/6 CERTIFIED — but certification is label, not proof)
- **Restart:** Any agent, any machine, computes identical result from committed state
- **Idempotent:** Yes (pure computation from committed files)
- **Concurrency:** Safe (read-only)
- **Makes product progress:** No (state reader only, doesn't execute work)

## Path 4: Generic Product Deepening
- **Entry:** autonomous_task_generator.py → lane_selector.py
- **State read:** product-deepening-ledger.yaml + gap-ledger.json + hardcoded _EXPANSION_GOALS
- **State written:** product-task-candidates.json
- **Task selection:** Lane rotation among gen-1 formats + hardcoded expansion goals
- **Verification gates:** product_deepening_gate.py (gen-1 only)
- **Bypasses:** Supreme Directive routes here when FF6 returns STOP
- **Terminal:** None defined (perpetual rotation)
- **Restart:** Stateless (re-reads ledger)
- **Idempotent:** No (dry-run mutation bug; rotation may select different format)
- **Concurrency:** No coordination with FF6
- **Makes product progress:** For gen-1 formats only; FF6 returns format_not_found

## Path 5: Plan Control
- **Entry:** tools/plan_control/ CLI
- **State read:** plans/.control/config.json, events.jsonl (missing), projections/ (missing)
- **State written:** None (system is inert)
- **Task selection:** Would use journal-driven task queue (not implemented)
- **Verification gates:** None active
- **Terminal:** N/A
- **Restart:** Doctor always returns ok=false
- **Idempotent:** Yes (does nothing)
- **Concurrency:** Lock directory exists but empty
- **Makes product progress:** No (completely inert)

## Path 6: Legacy Sprint Loop
- **Entry:** .supervisor/sprint-loop.md
- **State read:** .supervisor/ config files
- **State written:** Various .supervisor/ state
- **Status:** Superseded by autonomous machinery. Historical artifact.
- **Makes product progress:** No (not actively used)

## Path 7: Headless/External Host
- **Entry:** sprint_executor.py run-loop
- **State read:** next-sprint.md + continuation-signal.json
- **State written:** All cycle mutations via autonomous_cycle.py
- **Override logic:** Only 5 TRUE_EXTERNAL_GATES honored
- **Makes product progress:** Same as Path 1 (wraps autonomous_cycle)

## Path 8: GitHub Actions CI
- **Entry:** .github/workflows/ci.yml (on push/PR)
- **State read:** Repository files
- **State written:** CI status checks
- **Task selection:** Fixed job matrix
- **Bypasses:** continue-on-error on capability-parity
- **Makes product progress:** No (verification only, and incomplete)

## Path 9: Manual Taskcard Execution
- **Entry:** User reads a taskcard, executes manually
- **State read:** Taskcard document
- **State written:** Source code + evidence
- **Makes product progress:** Yes (if execution is genuine)

## Path 10: CLAUDE.md Session-Resume Bootstrap
- **Entry:** Read session-resume.md at session start
- **State read:** reports/supervisor/session-resume.md (committed)
- **Fallback:** plans/master-plan.md if session-resume.md missing
- **Makes product progress:** No (bootstrap context only)
