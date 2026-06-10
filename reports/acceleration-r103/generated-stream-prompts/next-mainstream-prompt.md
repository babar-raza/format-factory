# Next Sprint Prompt: MAINSTREAM Stream
Sprint: R103
Generated: 2026-06-03T08:42:57.171360+00:00

## Focus
Product capability implementation: save, export, dogfood, package

## File Boundaries
- Allowed source: src/net/, src/python/
- Allowed tests: tests/net/, tests/python/
- Forbidden: tools/supervisor/

## 3-Sprint Forecast
- **R103**: , , 
- **R104**: (scope expansion needed)
- **R105**: (scope expansion needed)

## Hard Quota
- min_capabilities_implemented: 3
- min_tests_per_capability: 8
- required_package_proof: True
- required_capability_matrix_update: True

## Priority Actions
- [implement_capability] mainstream-fods-dogfood-status-fods-to-csv-dotnet — FODS None is GAP_DOGFOOD_EXTERNAL
- [implement_capability] mainstream-fods-dogfood-status-fods-to-html-dotnet — FODS None is GAP_DOGFOOD_EXTERNAL
- [implement_capability] mainstream-fodt-dogfood-status-fodt-to-txt-dotnet — FODT None is GAP_DOGFOOD_EXTERNAL
- [implement_capability] mainstream-fodt-dogfood-status-fodt-to-markdown-dotnet — FODT None is GAP_DOGFOOD_EXTERNAL
- [run_package_proof] package_matrix — Verify all packages build and import after capability changes.

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
