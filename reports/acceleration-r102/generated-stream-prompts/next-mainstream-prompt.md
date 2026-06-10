# Next Sprint Prompt: MAINSTREAM Stream
Sprint: R103
Generated: 2026-06-03T08:05:18.409074+00:00

## Focus
Product capability implementation: save, export, dogfood, package

## File Boundaries
- Allowed source: src/net/, src/python/
- Allowed tests: tests/net/, tests/python/
- Forbidden: tools/supervisor/

## 3-Sprint Forecast
- **R103**: dogfood_status.fods_to_csv_dotnet, dogfood_status.fods_to_html_dotnet, dogfood_status.fodt_to_markdown_dotnet
- **R104**: dogfood_status.fodt_to_txt_dotnet, blockers.1, blockers.1
- **R105**: blockers.1

## Hard Quota
- min_capabilities_implemented: 3
- min_tests_per_capability: 8
- required_package_proof: True
- required_capability_matrix_update: True

## Priority Actions
- [implement_capability] commercial-net-fods-dogfood-status-fods-to-csv-dotnet — FODS dogfood_status.fods_to_csv_dotnet is GAP_DOGFOOD_EXTERNAL
- [implement_capability] commercial-net-fods-dogfood-status-fods-to-html-dotnet — FODS dogfood_status.fods_to_html_dotnet is GAP_DOGFOOD_EXTERNAL
- [implement_capability] commercial-net-fodt-dogfood-status-fodt-to-markdown-dotnet — FODT dogfood_status.fodt_to_markdown_dotnet is GAP_DOGFOOD_EXTERNAL
- [implement_capability] commercial-net-fodt-dogfood-status-fodt-to-txt-dotnet — FODT dogfood_status.fodt_to_txt_dotnet is GAP_DOGFOOD_EXTERNAL
- [implement_capability] foss-reduced-sylk-blockers-1 — SYLK blockers.1 is BLOCKED

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
