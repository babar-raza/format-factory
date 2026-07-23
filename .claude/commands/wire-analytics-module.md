---
version: "1.0"
last-updated: "2026-07-24"
phase-available: "4+"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "A second apply produces byte-identical package initialization."
risk_level: LOW
generated_by: codex
visibility: generated
---

# /wire-analytics-module

Expose an existing format analytics module through its package `__init__.py`
without moving analytics into the parser, writer, or model layers.

## Required input

- `format_id`: physical package directory under `src/python/`

## Execution

1. Run the deterministic planner:
   `python tools/backfill/analytics_wiring_backfill.py --format <format_id>`.
2. Review the discovered module and explicit export list. The module's
   literal `__all__` is authoritative when present; otherwise only public
   functions and classes defined in that module are exported.
3. Acquire the package `__init__.py` lease and apply:
   `python tools/backfill/analytics_wiring_backfill.py --format <format_id> --apply`.
4. Run the planner again and require `change_required: false`.
5. Verify direct package imports, `__all__`, format tests, and installed-wheel
   imports.

The generated block is marker-delimited, sorted, and replaced atomically, so a
rerun cannot accumulate duplicate imports or exports.

## Mandatory validations

- `analytics_module_reachable_via_import`
- `all_list_updated`
- `focused_tests`

## Allowed paths

- `src/python/<format_id>/__init__.py`
- format-focused tests and governed execution receipts

## Prohibited actions

- Do not infer exports from imported names.
- Do not create an analytics module.
- Do not place format conformance behavior in analytics.
- Do not count CSV/export helpers as format conformance.

