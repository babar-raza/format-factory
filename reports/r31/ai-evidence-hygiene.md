# Lane N: AI Evidence Bundle Hygiene

## __pycache__ Exclusion
The evidence contract will use `exclude_patterns` to exclude:
- `**/__pycache__/**`
- `**/*.pyc`
- `**/.pytest_cache/**`

## Canonical Report Paths
- Final verdict: `reports/r31/final-verdict.md`
- Sprint state: `reports/r31/sprint-state.yaml`
- All lane reports in `reports/r31/`
- Pipeline fixture artifacts in `reports/r31/pipeline-fixture-run/`

## Included Evidence
- Clean-env test log (449 passed in both modes)
- Fixture pipeline replay artifact (JSON)
- Live probe evidence (redacted summaries in reports)
- All 91 new R31 test assertions

## No __pycache__ in Evidence
All evidence is source files and reports only.

## Status: CLEAN
