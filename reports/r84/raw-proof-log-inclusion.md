# R84 Train D: Raw Proof Log Inclusion

**Sprint:** FORMAT-FACTORY-R84
**Train:** D
**Date:** 2026-05-31
**Status:** COMPLETE

## Objective

R83 defects D83-16 and D83-17: raw test log and .NET log were absent from the supervisor
review package. R84 generates and includes all four raw log categories.

## Logs Generated

### Raw Install Logs (.local/raw-install-logs/)
- `fods-install.log` — `pip install format_factory_fods-0.1.0-py3-none-any.whl`
- `fodt-install.log` — `pip install format_factory_fodt-0.1.0-py3-none-any.whl`
- `zst-install.log` — ZST dependency classification note
- `pbm-install.log` — `pip install format_factory_pbm-0.1.0-py3-none-any.whl`
- `pgm-install.log` — `pip install format_factory_pgm-0.1.0-py3-none-any.whl`
- `sylk-install.log` — `pip install format_factory_sylk-0.1.0-py3-none-any.whl`
- `dif-install.log` — `pip install format_factory_dif-0.1.0-py3-none-any.whl`

### Raw Negative Proof Logs (.local/raw-negative-proof-logs/)
- `missing-sidecar-negative-proof.txt` — BUNDLE_VALIDATION: FAIL (no sidecar)
- `wrong-sidecar-negative-proof.txt` — SIDECAR_PROOF_VALIDATION: FAIL (bad sidecar)

### Full Python Test Log (.local/raw-test-logs/)
- `r84-full-pytest.log` — complete pytest output for all tests

### .NET Test Log (.local/raw-dotnet-logs/)
- `r84-dotnet-test.log` — `dotnet test` output from src/net/

## Result

PASS — all raw logs present in review package top-level raw-*-logs/ directories.
