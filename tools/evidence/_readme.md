# tools/evidence/

Deterministic Evidence Bundle Contract System for format-factory.

This directory contains tools for building and validating evidence bundles produced at the end of each sprint run. Evidence bundles are structured zip archives that capture the complete state of a sprint's output for human review.

## Tools

| File | Purpose |
|---|---|
| `build_evidence_bundle.py` | Build a zip bundle from a contract YAML |
| `validate_evidence_bundle.py` | Validate an existing zip bundle against a contract |
| `collect_git_state.py` | Collect git status, log, and diff into metadata files |
| `collect_file_inventory.py` | Collect file lists (reviewed, modified, created) |

## Contracts

Contracts live in `contracts/` and define what a valid evidence bundle must contain. Each sprint run uses a contract to enforce completeness.

## Rules

1. Evidence bundles must have exactly two top-level folders: `repo/` and `bundle-metadata/`.
2. Forbidden paths (secrets, local-only artifacts, caches) are rejected.
3. Required metadata files must all be present for validation to pass.
4. The validator prints `BUNDLE_VALIDATION: PASS` or `BUNDLE_VALIDATION: FAIL`.
5. Manual zip packaging is prohibited for production bundles.
