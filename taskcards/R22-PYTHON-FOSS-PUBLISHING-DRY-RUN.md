# Taskcard: R22-PYTHON-FOSS-PUBLISHING-DRY-RUN

**Sprint:** R22 (planned)
**Date created:** 2026-05-17
**Status:** PENDING EXECUTION

## Objective

Run a local package build and publishing dry-run for all five Python FOSS packages.

## Prerequisites

1. `pip install build` available in environment
2. R21 package matrix and manifests present (DONE)
3. R21 examples smoke tests passing (DONE: 18/18)

## Steps

1. Run `python packaging/python/build-local-packages.py`
2. Verify wheel in `.local/package-builds/`
3. Import test from wheel: `pip install --force-reinstall wheel; python -c "import zst; print(zst.__version__)"`
4. Record sha256 and file sizes
5. Update release manifests with build artifact hashes
6. Gate 10 update: local_release_candidate_built (upgrade from local_release_candidate_ready)

## What R22 Does NOT Do

- No PyPI upload
- No GitHub release
- No credential use
- publication_authorized remains false unless human provides explicit authorization prompt
