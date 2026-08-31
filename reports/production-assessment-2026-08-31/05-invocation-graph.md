# 05 — Invocation Graph

**Baseline commit:** dd909cf3a

## Official Entry Points

### Entry Point A: CLAUDE.md Autonomous Loop (Interactive)
```
User message / "continue"
  → CLAUDE.md Session Start
    → Step 0: Plan Lock Check
      → IF plan loaded: write_plan_lock.py → plan execution exclusively
      → IF no plan: read session-resume.md
    → FF6 Mission Resume: goal_driver.py resume
      → Reads: controller-state.yaml, product-goal.yaml, obligations/*.yaml
      → Returns: CONTINUE (work remains) or GOAL_ACHIEVED (6/6) or BLOCKED
    → Sprint Execution (skill-governed, EP-3)
    → Sprint Closeout (best-effort):
      1. evidence-declaration.yaml write
      1b. sprint_executor_validate.py --repair
      2. supervisor_loop.py autonomous-cycle
        → autonomous_cycle.py
          → Step 2e: governance_validator_runner (POST-sprint)
          → Step 8: write continuation-signal.json
        → generate_next_worker_prompt.py → next-sprint.md
      3. check_continuation.py
        → Reads: continuation-signal.json
        → Returns: CONTINUE or STOP (23+ reasons)
        → 17/23 STOP reasons overridden → read next-sprint.md directly
      4. build_declaration_review_package.py
    → Loop: next sprint
```

### Entry Point B: FF6 Goal Driver (State-Derived)
```
python -m tools.ff6.goal_driver resume
  → Reads: controller-state.yaml (committed)
    → product-goal.yaml → format list
    → obligations/{fmt}.yaml → obligation counts
    → promotion block → certification labels (BROKEN: reads label not proof)
  → Returns: CONTINUE / GOAL_ACHIEVED / BLOCKED
  → No .local/ dependency
  → No continuation signal dependency
  → Deterministic from committed state
```

### Entry Point C: Headless Sprint Executor
```
python tools/supervisor/sprint_executor.py run-loop
  → Reads: next-sprint.md
  → Spawns: claude --print subprocess
  → After each sprint: autonomous_cycle.py
  → Override logic: only TRUE_EXTERNAL_GATES stop (5 members)
  → Resets iteration on MAX_ITERATIONS
```

### Entry Point D: Generic Product Deepening
```
autonomous_task_generator.py
  → lane_selector.py → product-deepening-ledger.yaml (gen-1 only)
  → Hardcoded _EXPANSION_GOALS (ABW, DIF, FODG, TSV, NDJSON, Gnumeric)
  → dom_gap_generator.py → capability gaps
  → product_deepening_gate.py → readiness check
  → Output: product-task-candidates.json
  → FF6 formats: format_not_found (PROVEN)
```

### Entry Point E: Plan Control
```
python -m tools.plan_control doctor
  → Reads: plans/.control/config.json
  → Missing: events.jsonl, projections/
  → Returns: ok=false, 0 plans, 0 tasks
  → COMPLETELY INERT
```

### Entry Point F: CI Pipeline
```
.github/workflows/ci.yml
  → pip install -e ".[dev]" (root only, no gen-2 packages)
  → pytest (runs against source tree, not installed wheels)
  → governance check (continue-on-error on capability-parity)
  → 13+ jobs, zero FF6 package installations
```

## Key Divergence Points

1. **Entry A vs B:** A reads continuation-signal.json (ephemeral, local); B reads controller-state.yaml (committed). Same repo state → potentially different next-task.
2. **Entry A vs D:** A follows FF6 mission; D selects gen-1 formats only. Supreme Directive can route to D when FF6 check returns STOP (even though goal_driver says CONTINUE).
3. **Entry B vs D:** Completely disconnected. B covers 6 FF6 formats; D covers ~15 gen-1 formats. Zero overlap.

## Experimentally Verified

| Path | Verified | Method | Result |
|------|----------|--------|--------|
| A (CLAUDE.md loop) | Architecture inspection | Code reading | 18 bypass rules, post-sprint governance |
| B (goal_driver) | Direct execution | Worktree experiment | CONTINUE, 4/6 (false), deterministic |
| C (sprint_executor) | Architecture inspection | Code reading | 5 TRUE_EXTERNAL_GATES only |
| D (task_generator) | Direct execution | Worktree dry-run | ABW/DIF selected, all FF6 format_not_found |
| E (Plan Control) | Direct execution | Worktree doctor | ok=false, 0/0/0 |
| F (CI) | File inspection | ci.yml grep | Zero gen-2 installs |
