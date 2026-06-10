# Next Sprint Prompt: SUPERVISOR Stream
Sprint: R103
Generated: 2026-06-03T08:05:18.409140+00:00

## Focus
Supervisor pipeline: grading, materialization, continuation logic

## File Boundaries
- Allowed source: tools/supervisor/
- Allowed tests: tests/supervisor/
- Forbidden: src/net/, src/python/

## 3-Sprint Forecast
- **R103**: blockers.1, blockers.1, blockers.1
- **R104**: gate_11_g11g, gate_11_g11g, gate_11_status
- **R105**: (scope expansion needed)

## Hard Quota
- min_pipeline_improvements: 2
- min_tests: 10
- required_dry_run: True

## Priority Actions
- [implement_capability] commercial-net-fods-blockers-1 — FODS blockers.1 is BLOCKED
- [implement_capability] commercial-net-fodt-blockers-1 — FODT blockers.1 is BLOCKED
- [implement_capability] commercial-net-netpbm-blockers-1 — Netpbm blockers.1 is BLOCKED
- [implement_capability] commercial-net-fods-gate-11-g11g — FODS gate_11_g11g is NOT_STARTED
- [implement_capability] commercial-net-fodt-gate-11-g11g — FODT gate_11_g11g is NOT_STARTED

## Anti-Skip Checks
Before closing this sprint, verify:
- [ ] No stale selected gaps (sprint_id matches)
- [ ] Raw test logs captured
- [ ] No generic next prompt (stream-specific content required)
- [ ] Test content verified (not path-only acceptance)

## Self-Decision Rules
1. If all quota items met and tests pass -> PASS
2. If quota partially met -> PARTIAL (list what's missing)
3. If blocked by external gate -> BLOCKED (state gate)
4. Continue-if-fast: if finished early, pick next action from forecast
