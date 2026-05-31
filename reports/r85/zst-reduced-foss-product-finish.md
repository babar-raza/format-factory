# R85 Train L — ZST Reduced/FOSS Product Finish

Sprint: FORMAT-FACTORY-R85-POC-DIRECTION-LOCAL-SUPERVISOR-AUTONOMOUS-PRODUCT-FACTORY-MEGA-TRAIN-001
Date: 2026-05-31

## Current Status

Python ZST package: format-factory-zst v0.1.0
Gates 1-10: ALL PASSED
Gate 10 status: local_release_candidate_ready

## Capability Audit

| Capability | Status |
|-----------|--------|
| compress bytes | PASS |
| compress file | PASS |
| decompress bytes | PASS |
| decompress file | PASS |
| probe (header inspection) | PASS |
| validate (integrity check) | PASS |
| get_capabilities() | PASS |
| Installed workflow | PASS (R82 proof) |

## Dependency Mode

ZST_LOCAL_RC_DEPENDENCY_RESOLUTION_REQUIRED

The zstandard C extension (zstandard 0.25.0) is required at runtime.
It is not bundled in the Python FOSS wheel.
Users must: `pip install format-factory-zst` which pulls zstandard from PyPI.
For offline/air-gapped environments: pre-download zstandard wheel.

This dependency mode is documented, not hidden.

## Examples

examples/python/zst/compress_decompress_file.py — PRESENT

## Docs

docs/python-foss/ — Python FOSS docs present
release-manifests/python-foss/fods.yaml, fodt.yaml, netpbm.yaml — present for other packages
ZST release manifest: not separately verified in R85 (check release-manifests/)

## R85 Finding

No new code needed. ZST is a complete compression codec FOSS product.
Its nature (compression, not format) means no format-to-format export applies.
Dependency mode is documented.

## TRAIN_L_STATUS: COMPLETE (audit only)
