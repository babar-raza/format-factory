# Next Sprint Prompt: ACCELERATION Stream
Sprint: R103
Generated: 2026-06-03T08:42:57.171413+00:00

## Focus
Acceleration tooling: gap selection, routing, handoff generation, learning

## File Boundaries
- Allowed source: tools/supervisor/
- Allowed tests: tests/supervisor/acceleration/
- Forbidden: src/net/, src/python/

## 3-Sprint Forecast
- **R103**: , , 
- **R104**: , , 
- **R105**: , 

## Hard Quota
- min_tools_improved: 4
- min_tools_with_pos_neg_tests: 3
- min_sample_outputs: 3
- required_raw_logs: True

## Priority Actions
- [implement_capability] acceleration-tool-untested-select-poc-gaps-py — None None is PARTIAL
- [implement_capability] acceleration-tool-untested-choose-skill-or-handoff-py — None None is PARTIAL
- [implement_capability] acceleration-tool-untested-detect-product-progress-py — None None is PARTIAL
- [implement_capability] acceleration-tool-untested-materialize-and-review-py — None None is PARTIAL
- [implement_capability] acceleration-tool-untested-build-declaration-review-package-py — None None is PARTIAL

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
