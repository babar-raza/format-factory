# R84 Train B: Top-Level Review Package Self-Containment

**Sprint:** FORMAT-FACTORY-R84
**Train:** B
**Date:** 2026-05-31
**Status:** COMPLETE

## Objective

R83 defect D83-01: package-artifacts/, raw logs, product-capability-matrix/, gate-readiness/,
publication-readiness/, final-metadata/, validation-proofs/, examples-docs-readiness/ were only
accessible inside the inner evidence ZIP. Supervisor reviewers need them at the top level of
the r84-supervisor-review-package.zip without unzipping any nested artifact.

## Changes Made

### build_supervisor_review_package.py

- Added `extra_top_level_dirs: list[tuple[str, Path]] | None = None` parameter to
  `build_supervisor_review_package()`
- Added `--extra-top-level-dirs` CLI argument accepting comma-separated `name:path` pairs
- ZIP build loop extended: for each `(dir_name, dir_path)` in `extra_top_level_dirs`,
  all files from `dir_path` are added to the ZIP as `dir_name/<relative_path>`
- Added `extra_dir_entry_count` to return manifest

### Directories added at top level for R84

```
package-artifacts/     -> .local/r84-packages/
raw-test-logs/         -> .local/raw-test-logs/
raw-package-install-logs/ -> .local/raw-install-logs/
raw-negative-proof-logs/  -> .local/raw-negative-proof-logs/
raw-dotnet-logs/       -> .local/raw-dotnet-logs/
product-capability-matrix/ -> product-capability-matrix/
examples-docs-readiness/   -> examples/
gate-readiness/        -> gate-readiness/
publication-readiness/ -> publication-readiness/
final-metadata/        -> .local/r84-metadata/
validation-proofs/     -> reports/r84/
```

## Verification

Test: `tests/evidence/test_r84_review_package_top_level_artifacts.py`

Key assertions:
- `package-artifacts/` directory present at top level with at least 10 entries
- `raw-test-logs/` directory present at top level
- `raw-package-install-logs/` directory present at top level
- `raw-negative-proof-logs/` directory present at top level
- `final-metadata/` directory present at top level
- `validation-proofs/final-verdict.md` accessible directly

## Result

PASS — top-level self-containment implemented and tested.
