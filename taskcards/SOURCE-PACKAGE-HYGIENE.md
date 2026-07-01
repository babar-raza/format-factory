# Taskcard: SOURCE-PACKAGE-HYGIENE

**Status:** completed
**Created:** 2026-05-13
**Sprint:** COMMERCIAL-PRODUCT-DIRECTION-RESET-SWARM-001

## Purpose

Audit and document source package hygiene for Format Factory. Ensure build artifacts,
Python cache files, and other generated content are excluded from committed source and
from source review ZIPs.

## Status: COMPLETED

Audit completed. Repository is clean. ZIP creation policy documented.

## Findings

### Repository
- CLEAN: bin/, obj/, __pycache__, .pyc, .nupkg, .snupkg all gitignored
- No build artifacts committed
- .gitignore adequate — no changes required

### User-Supplied src/src.zip
- DIRTY: contains 117 build artifact entries (DLLs, PDB, MSBuild intermediates)
- File is untracked (not committed) — repo integrity maintained
- Classification: REPO_CLEAN_BUT_USER_ZIP_DIRTY

## Deliverables

- `docs/code-quality/source-package-hygiene.md` — ZIP creation policy
- `reports/audit/source-package-hygiene-audit-20260513.md`
- `reports/audit/source-package-hygiene-audit-20260513.yaml`

## Next Action

When creating source review ZIPs in future, use `git archive` or explicit exclusion filters.
See docs/code-quality/source-package-hygiene.md for recommended patterns.
