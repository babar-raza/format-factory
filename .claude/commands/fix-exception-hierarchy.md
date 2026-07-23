---
version: "1.0"
last-updated: "2026-07-24"
phase-available: "4+"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "A second apply reports no duplicate exception definitions."
risk_level: MEDIUM
generated_by: codex
visibility: generated
---

# /fix-exception-hierarchy

Repair duplicate exception-class definitions in one Python format package while
keeping `exceptions.py` as the only class-definition authority.

## Required input

- `format_id`: physical package directory under `src/python/`

## Execution

1. Run the planner without mutation:
   `python tools/backfill/exception_hierarchy_backfill.py --format <format_id>`.
2. Confirm that `exceptions.py` exists, parses, defines exception classes, and
   every local exception root derives from `FormatFactoryError`.
3. Acquire coordination leases for every file listed in `changed_files`.
4. Apply the exact plan:
   `python tools/backfill/exception_hierarchy_backfill.py --format <format_id> --apply`.
5. Run the command again without `--apply`; `changed_files` must be empty.
6. Run the package's focused exception and installed-wheel tests.

The implementation removes only duplicate class definitions whose names already
exist in `exceptions.py`, then imports those canonical classes using the correct
relative depth. It fails closed on syntax errors, unsafe decorated definitions,
missing canonical roots, or an invalid hierarchy.

## Mandatory validations

- `exception_root_is_format_factory_error`
- `no_shadow_class_redefinition`
- `focused_tests`

## Allowed paths

- `src/python/<format_id>/**/*.py`
- format-focused tests and governed execution receipts

## Prohibited actions

- Do not create a fallback `FormatFactoryError`.
- Do not rewrite canonical exception bodies.
- Do not modify a file not named in the dry-run plan.
- Do not treat importability from the source tree as installed-package proof.

