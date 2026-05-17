# Python FOSS Release Process

**Date:** 2026-05-17
**Status:** DEFINED — NOT YET EXECUTED
**publication_authorized:** false

## Current State

No Python FOSS packages are published. All packages are at `local_release_candidate_ready` state,
meaning all artifacts (source, tests, examples, metadata, manifests) are ready, but:

1. Physical wheel/sdist build requires `pip install build` (not yet in environment)
2. PyPI publication requires an explicit authorization prompt
3. `publication_authorized: false` for all packages

## Release Gate Checklist (Not Yet Satisfied)

- [ ] `pip install build` available in CI environment
- [ ] `python packaging/python/build-local-packages.py` runs successfully
- [ ] Wheel imports verified from `.local/package-builds/`
- [ ] Smoke tests pass against installed wheel
- [ ] Explicit human authorization for PyPI publication
- [ ] PyPI API token obtained (through proper channels)
- [ ] Version tag created on git (via proper release process)
- [ ] `publication_authorized: true` set in release manifest

## Release Steps (When Authorized)

1. Install build backend: `pip install build`
2. Run local build: `python packaging/python/build-local-packages.py`
3. Verify each wheel: `pip install --force-reinstall .local/package-builds/{package}/dist/*.whl`
4. Run smoke tests against installed wheel
5. Get explicit human authorization
6. Publish: `twine upload .local/package-builds/{package}/dist/*`

## Package Names

All names are provisional pending naming authority confirmation:
- `aspose-format-factory-zst` (or `format-factory-zst`)
- `aspose-format-factory-fodp`
- `aspose-format-factory-fodg`
- `aspose-format-factory-gnumeric`
- `aspose-format-factory-abw`

## What Must NOT Happen Before Authorization

- No `twine upload` or `pip publish`
- No PyPI account creation or token use
- No git tag for release purposes
- No GitHub release artifacts
- No announcement or documentation claiming packages are available

## Commercial Product Note

These Python FOSS packages have no connection to the commercial Gate 11 product timeline.
The .NET commercial product (FODS/FODT) requires separate G11-G human approval.
