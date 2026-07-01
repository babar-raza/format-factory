**Document type:** Directory Orientation
**Last reviewed:** 2026-07-01

# Test Drivers

## Purpose

Test generation templates (`.py.tmpl`) for format-specific test scaffolding.
Rendered by `tools/supervisor/test_drivers.py` (direct consumer) and consumed
indirectly via `tools/supervisor/product_feature_factory.py`.

Retention: **RETAIN** — actively consumed by at least two runtime components.

## Language Scope

**PYTHON_ONLY_BY_DESIGN.** Only Python templates exist. Only Python consumers exist.
Explicit language rejection is enforced via `_validate_language()` in `test_drivers.py`.
To add support for another language, register a new driver module — do NOT modify this one.

## Contents

- **`python/`** — Python test templates (append_test, export_csv_test, getter_test, probe_test, roundtrip_test)
- **`python/driver-contracts.yaml`** — machine-readable template/renderer argument contracts

## Consumers

| File | Classification | Evidence |
|---|---|---|
| `tools/supervisor/test_drivers.py` | DIRECT_RUNTIME_CONSUMER | `_DRIVERS_DIR / "python"` + `_load_template()` reads `.tmpl` files |
| `tools/supervisor/product_feature_factory.py` | DIRECT_RUNTIME_CONSUMER | imports all 5 `render_*` functions, calls at runtime |
| `tools/supervisor/libforge_pattern_registry.py` | DECLARATIVE_REFERENCE | PatternRecord metadata only — no runtime coupling |

## Non-Consumers

- `compose_verify_loop.py` — docstring mention only, no import
- Any `.NET` or non-Python tooling — PYTHON_ONLY_BY_DESIGN

## Template/Renderer Contracts

Contracts defined in `drivers/python/driver-contracts.yaml`.
Validated at runtime by `validate_template_renderer_compatibility()` in `test_drivers.py`.
ACTIVE_TEMPLATE_RENDERER_MISMATCHES must = 0.

## Placeholder Policy

All templates emit machine-readable incomplete markers instead of silent weak assertions:

- `# FIXTURE_REQUIRED` — caller must provide real format bytes
- `# EXPECTED_VALUE_REQUIRED` — caller must write a meaningful assertion
- `# ORACLE_REQUIRED` — caller must assert spec-derived expected value
- `# TEST_SCAFFOLD_INCOMPLETE` — scaffold not yet promotion-ready
- `# SCAFFOLD_STATUS: FORMAT_ADAPTATION_REQUIRED` — header on all generated scaffolds

Detected by `scan_for_forbidden_placeholders()`. Gate: `is_maintained_test()` returns False
while any marker remains. FORBIDDEN_PLACEHOLDERS_IN_MAINTAINED_TESTS must = 0.

## Format-Promotion Lifecycle

Scaffolds progress through these states (see `tools/supervisor/drivers_promotion.py`):

```
SCAFFOLD_GENERATED → FORMAT_ADAPTATION_REQUIRED → FIXTURES_READY
  → ASSERTIONS_READY → EXECUTABLE → VERIFIED → MAINTAINED
```

A test file is only MAINTAINED when all markers are removed and real assertions exist.

## Fixture and Assertion Requirements

- Fixtures must come from: `repository_golden_sample`, `deterministic_builder`,
  `spec_example`, `minimal_valid_bytes`, `intentionally_malformed`, or `verified_roundtrip`
- `b""` is only accepted when `fixture_source="empty_input_contract"`
- Enforced by `validate_fixture_contract()` in `test_drivers.py`

## Validation Commands

```bash
# Run driver and promotion tests
.venv/Scripts/pytest tests/supervisor/test_test_drivers.py tests/supervisor/test_drivers_promotion.py -v

# Validate template/renderer contract compatibility
python -c "from tools.supervisor.test_drivers import validate_template_renderer_compatibility; validate_template_renderer_compatibility(); print('OK')"
```

## How to Add a Driver/Template

1. Create `drivers/python/{pattern}_test.py.tmpl`
2. Add `render_{pattern}_test()` function to `test_drivers.py`
3. Add template entry and renderer entry to `drivers/python/driver-contracts.yaml`
4. Add tests in `tests/supervisor/test_test_drivers.py`
5. Run `validate_template_renderer_compatibility()` — must pass

## Known Gaps

- No .NET driver exists (PYTHON_ONLY_BY_DESIGN — by decision)
- Format-test promotion to MAINTAINED requires per-format manual fixture work

## Governance

- **Classification:** SHARED_LIBRARY / TOOLING
- **Retention:** RETAIN
- **Producers:** developers (authors of .py.tmpl files)
- **Registry entry:** `registry/repository-root-folders.yaml`
- **Contracts:** `drivers/python/driver-contracts.yaml`
- **Mission:** DRIVERS-SUBSYSTEM-HEALING-001
