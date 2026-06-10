# Next Sprint Prompt: SUPERVISOR Stream
Sprint: R104
Generated: 2026-06-03T09:19:30.562588+00:00

## Focus
Supervisor pipeline: grading, materialization, continuation logic

## File Boundaries
- Allowed source: tools/supervisor/
- Allowed tests: tests/supervisor/
- Forbidden: src/net/, src/python/

## 3-Sprint Forecast
- **R103**: , , 
- **R104**: , , 
- **R105**: (scope expansion needed)

## Hard Quota
- min_pipeline_improvements: 2
- min_tests: 10
- required_dry_run: True

## Priority Actions
- [implement_capability] supervisor-pipeline-evidence-manifest-in-review-package — None None is GAP
- [implement_capability] supervisor-pipeline-acceleration-report-packaging — None None is GAP
- [implement_capability] supervisor-pipeline-raw-log-packaging — None None is GAP
- [implement_capability] supervisor-pipeline-sample-output-packaging — None None is GAP
- [implement_capability] supervisor-pipeline-lane-ledger-packaging — None None is GAP

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
