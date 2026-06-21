# TC-SRC-REVIEW-001: Build-Artifact Audit and Ignore Rules

**Lane**: SRC-REVIEW
**Status**: backlog
**Owner**: autonomous agent
**Prerequisites**: none
**item_type**: GOVERNANCE_ASSET

## Objective

Verify that build artifacts (`bin/`, `obj/`, `build/`, `*.egg-info`, `__pycache__`) are not tracked
in git or counted in source metrics. Ensure `.gitignore` excludes them and baseline skip patterns match.

## Execution Steps

1. `git ls-files -- 'src/net/*/obj/' 'src/net/*/bin/'` — report what's tracked
2. Check `.gitignore` for `obj/`, `bin/`, `build/`, `*.egg-info`, `__pycache__` patterns
3. If artifacts tracked: add `.gitignore` patterns (git rm --cached, do NOT delete files)
4. Update `registry/source-structure-baseline.json` skip patterns to exclude build dirs

## Validation

- `git ls-files -- '*.egg-info'` returns empty
- `git ls-files -- '*/__pycache__/'` returns empty
- `git ls-files -- '*/obj/'` returns empty

## Evidence Required

- git ls-files output (before and after)
- Updated .gitignore diff if changes made

## Rollback

Revert `.gitignore` changes

## Completion Criteria

No build artifacts tracked in git; source metrics exclude build dirs
