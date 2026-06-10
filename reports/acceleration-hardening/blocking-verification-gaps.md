# Blocking Verification Gaps

**Sprint:** FORMAT-FACTORY-ACCELERATION-HARDENING-IV-AND-CONSUMPTION-CONTRACT-001

## BLOCKING: ai_rationale = [fixture_error]

All 4 packets contain `[fixture_error] ModuleNotFoundError: No module named 'pydantic'` in
the `ai_rationale` field.

- **Cause:** Packet generated with system Python (no pydantic). Venv Python works correctly.
- **Effect:** ai_rationale is garbage text, not an AI-generated rationale.
- **Rule violation:** A packet with `fixture_error` must not claim `directly_consumable=true`.
- **Fix:** Regenerate packets using venv Python; add `runtime_status` and `stale_or_error_flags` fields.

## BLOCKING: test_plan_path = null

All 4 packets have `test_plan_path: null` even though test plans exist at:
- `reports/acceleration-product-first/test-plans/fods-dogfood-csv-test-plan.json`
- `reports/acceleration-product-first/test-plans/fodt-dogfood-markdown-test-plan.json`
- `reports/acceleration-product-first/test-plans/netpbm-export-test-plan.json`
- `reports/acceleration-product-first/test-plans/sylk-csv-export-test-plan.json`

- **Cause:** Path discovery uses `{capability_path.replace('.', '-')}-test-plan.json` pattern
  which produces `dogfood_status-fods_to_csv_dotnet-test-plan.json` — file does not exist.
- **Effect:** Mainstream worker cannot find the test plan from the packet.
- **Fix:** Add format-based fallback discovery in `_find_test_plan()`.

## BLOCKING: 8 Missing Schema Fields

All 4 packets are missing:
- `packet_version` — version string for schema compatibility
- `stream` — must be "acceleration"
- `test_plan_exists` — boolean
- `skills_handoff_compatibility` — dict
- `supervisor_routing_compatibility` — dict
- `required_mainstream_validation` — list
- `runtime_status` — "ok" | "degraded" | "error"
- `stale_or_error_flags` — list

- **Fix:** Add all fields in `build_packet()` function.
