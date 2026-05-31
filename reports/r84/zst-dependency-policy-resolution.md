# R84 Train J: ZST Dependency Policy Resolution

**Sprint:** FORMAT-FACTORY-R84
**Train:** J
**Date:** 2026-05-31
**Status:** COMPLETE

## Classification

**ZST_LOCAL_RC_DEPENDENCY_RESOLUTION_REQUIRED**

The format-factory-zst package requires `zstandard>=0.21.0` (PyPI) which cannot be
resolved in a network-isolated environment. This is a known, documented blocker.

## Evidence

Raw failing no-network install log: `.local/raw-install-logs/zst-install.log`

```
pip install --no-index format_factory_zst-0.1.0-py3-none-any.whl
ERROR: Could not find a version that satisfies the requirement zstandard>=0.21.0
ERROR: No matching distribution found for zstandard>=0.21.0
```

## Policy

ZST is classified as `DEPENDENCY_RESOLUTION_REQUIRED` for FOSS publication path.
Options for future resolution:
1. Bundle `zstandard` wheel in package-artifacts/dependencies/
2. Publish to PyPI with pip dependency resolution (normal use case)
3. Vendor zstandard source into the package (license-permissive)

Classification file: `dependency-artifacts/README.md`

## Gate Status

ZST Gates 1-10: PASSED (with G5 waived for stdlib exception)
ZST Gate 11: BLOCKED (dependency resolution required before FOSS publication)
ZST commercial_product_ready: false

## Result

PASS — ZST dependency policy documented; no action required in R84 beyond classification.
