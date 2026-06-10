# Anti-Skip Raw-Log Path Analysis

## Sprint: mainstream-r112

## Failure Summary
- Check: `missing_raw_logs`
- Result: VIOLATION (is_violation: true)
- logs_found: [] (empty)
- Source: `.local/supervisor/reviews/mainstream-r111/anti-skip-check-result.json`

## Actual Raw Logs on Disk
| File | Absolute Path | Size |
|------|---------------|------|
| fods-dotnet-test.log | reports/mainstream-r111/raw-logs/fods-dotnet-test.log | 632 bytes |
| fodt-dotnet-test.log | reports/mainstream-r111/raw-logs/fodt-dotnet-test.log | 632 bytes |
| netpbm-dotnet-test.log | reports/mainstream-r111/raw-logs/netpbm-dotnet-test.log | 650 bytes |
| python-all-test.log | reports/mainstream-r111/raw-logs/python-all-test.log | 3761 bytes |

## Path Mapping

| File | Declaration evidence_paths | Anti-skip expected path | Match? |
|------|---------------------------|------------------------|--------|
| fods-dotnet-test.log | reports/mainstream-r111/raw-logs/fods-dotnet-test.log | (not searched) | NO |
| fodt-dotnet-test.log | reports/mainstream-r111/raw-logs/fodt-dotnet-test.log | (not searched) | NO |
| netpbm-dotnet-test.log | reports/mainstream-r111/raw-logs/netpbm-dotnet-test.log | (not searched) | NO |
| python-all-test.log | reports/mainstream-r111/raw-logs/python-all-test.log | (not searched) | NO |

## Root Cause

The anti-skip `missing_raw_logs` check in `inspect_declared_evidence.py` does NOT scan `evidence_paths` for log files. It looks for a specific field or directory structure under `evidence_root` (`.local/evidences/mainstream-r111/`), not under `reports/mainstream-r111/raw-logs/`.

The R111 declaration correctly lists raw logs in `evidence_paths` of individual work items (e.g., `reports/mainstream-r111/raw-logs/fods-dotnet-test.log`), but the anti-skip check:
1. Does not scan `evidence_paths` for `*.log` files
2. Does not scan `reports/<run_id>/raw-logs/` directory
3. Only looks under `evidence_root` which is `.local/evidences/<run_id>/`

This is the same path-resolution mismatch documented in R111's `acceleration-anti-skip-path-resolution-handoff.md`.

## Classification
- **missing_raw_logs: FALSE POSITIVE** — raw logs exist at `reports/mainstream-r111/raw-logs/` but anti-skip does not search there
- **missing_sample_outputs: TRUE POSITIVE** — no sample outputs were created in R111
- **dirty_git_state: TRUE POSITIVE** — git state is dirty and was not classified in R111

## Acceleration Handoff Required
The anti-skip path resolution must be fixed to search both:
1. `evidence_root` (`.local/evidences/<run_id>/`)
2. `reports/<run_id>/raw-logs/` (where Mainstream actually puts raw logs)
3. `evidence_paths` entries matching `*.log` pattern
