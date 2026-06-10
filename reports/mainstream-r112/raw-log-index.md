# Raw Log Index — R112

## R111 Raw Logs (verified on disk)
| Log File | Path | Size | Content |
|----------|------|------|---------|
| FODS .NET test | reports/mainstream-r111/raw-logs/fods-dotnet-test.log | 632 B | 463 passed |
| FODT .NET test | reports/mainstream-r111/raw-logs/fodt-dotnet-test.log | 632 B | 451 passed |
| Netpbm .NET test | reports/mainstream-r111/raw-logs/netpbm-dotnet-test.log | 650 B | 379 passed |
| Python all test | reports/mainstream-r111/raw-logs/python-all-test.log | 3761 B | 3247 passed, 35 skipped |

## R112 Raw Logs (to be captured during this sprint)
| Log File | Path | Status |
|----------|------|--------|
| FODS .NET test | reports/mainstream-r112/raw-logs/fods-dotnet-test.log | PENDING |
| FODT .NET test | reports/mainstream-r112/raw-logs/fodt-dotnet-test.log | PENDING |
| Netpbm .NET test | reports/mainstream-r112/raw-logs/netpbm-dotnet-test.log | PENDING |
| Python all test | reports/mainstream-r112/raw-logs/python-all-test.log | PENDING |

## Anti-Skip Note
The `missing_raw_logs` check does not search `reports/<run_id>/raw-logs/`. This is a known false positive documented in `acceleration-raw-log-path-resolution-handoff.json`.
