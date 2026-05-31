# R84 Train U: Closeout Automation and Supervisor Loop Integration

**Sprint:** FORMAT-FACTORY-R84
**Train:** U
**Date:** 2026-05-31
**Status:** COMPLETE

## Closeout Driver Steps

1. Run full test suite: `pytest tests/ -q` → capture to `.local/raw-test-logs/r84-full-pytest.log`
2. Build all packages: `python packaging/python/build-local-packages.py`
3. Run .NET tests: `dotnet test src/net/` → capture to `.local/raw-dotnet-logs/r84-dotnet-test.log`
4. Generate raw install logs for each package
5. Run 3-pass evidence bundle build (Train C protocol)
6. Build delivery package
7. Build supervisor review package with `--extra-top-level-dirs`
8. Commit final state

## Primary Artifact Path

```
UPLOAD PRIMARY ARTIFACT: .local/r84-supervisor-review-package.zip
```
(absolute path printed after bundle build completes)

## Supervisor Loop

The supervisor loop is integrated via `tools/supervisor/discover_latest_evidence.py`.
After the final commit, running the supervisor loop will:
- Detect `r84-supervisor-review-package.zip` as the latest primary artifact
- Validate it against the R84 contract
- Generate next-sprint recommendations

## Result

PASS — closeout automation steps documented and executable.
