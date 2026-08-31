# 00 — Baseline Snapshot

**Assessed commit:** dd909cf3a9586a8a6b7a32c357011cd2557e3fae (HEAD of main)
**Assessment date:** 2026-08-31
**Environment:** Windows 11 Pro 10.0.26200, Python 3.12, .venv with dev extras + zstandard
**CI run inspected:** https://github.com/babar-raza/format-factory/actions/runs/33321372202

## Repository Statistics (at assessed commit)
- Total files: ~19,993
- Supervisor tools: ~290 (tools/supervisor/)
- Claude commands: ~202 (.claude/commands/)
- Governance validators: 226 (expected count in runner)
- FF6 controller events: 522 (hash-chain verified PASS)
- Active capabilities: 195 (per .governance/capabilities/registry.yaml)
- Sprints completed: 849 (per session-resume.md)
- Gen-1 packages: ~21 (flat layout, bare imports)
- Gen-2 packages: 7 (core + 6 FF6 formats, format_factory.* namespace)

## Active Control Systems Identified
1. Generic supervisor loop (supervisor_loop.py → autonomous_cycle.py → check_continuation.py)
2. Per-chat plan locking (write_plan_lock.py → plan-locks/*.json)
3. FF6 mission controller (goal_driver.py → controller-state.yaml, 522 events)
4. Generic product-deepening (lane_selector.py → product-deepening-ledger.yaml)
5. Plan Control (tools/plan_control/ — 12 modules, bootstrapped but inert)
6. Legacy/alternative mechanisms (.supervisor/sprint-loop.md, codex handover)

## Key State Files
- `.local/supervisor/continuation-signal.json` — gitignored, non-bootstrappable
- `plans/strategic/ff6/controller-state.yaml` — committed, CONTRADICTORY
- `reports/supervisor/session-resume.md` — derived, auto-generated, sprint 849
- `.local/supervisor/plan-locks/` — gitignored, session-scoped
- `reports/supervisor/next-sprint.md` — derived, regenerated each cycle
- `registry/product-deepening-ledger.yaml` — committed, no FF6 formats

## Known Contradictions at Baseline
1. controller-state.yaml promotion block (4/6 CERTIFIED) vs truth_boundary (0/6) vs production_certifications (0)
2. product-goal.yaml ORA namespace (format_factory.openraster) vs actual (format_factory.ora)
3. README.md "20/20 certified" vs GAP-008 finding (17 of 20 trace to synthetic manifests)
4. Root pyproject.toml requires-python >=3.9 vs gen-2 packages require >=3.11
5. UBL obligation count: 194 (product-goal.yaml) vs 195 (obligation register)
6. CI does not install any gen-2 package (pip install -e ".[dev]" only)

## Evidence Classification
All findings in this assessment use the standard: PROVEN (executed and observed), INFERRED (derived from code reading without execution), DISPROVEN (tested and found false), UNKNOWN (insufficient evidence).
