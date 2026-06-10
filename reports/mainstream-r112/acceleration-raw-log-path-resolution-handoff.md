# Acceleration Raw-Log Path Resolution Handoff

## From: Mainstream R112
## To: Acceleration Stream

## Defect: D112-ASLP-01 — missing_raw_logs false positive due to path resolution

### Description
The `missing_raw_logs` anti-skip check reports 0 logs found despite 4 raw log files existing at `reports/mainstream-r111/raw-logs/`.

### Root Cause
The check searches under `evidence_root` (`.local/evidences/<run_id>/`) but Mainstream sprints store raw logs under `reports/<run_id>/raw-logs/`. The check also does not scan `evidence_paths` declared in work items for `*.log` files.

### Fix Location
`tools/supervisor/inspect_declared_evidence.py` — the `missing_raw_logs` check implementation.

### Recommended Fix
Search for raw logs in this priority order:
1. `evidence_root` + `raw-logs/` subdirectory
2. `reports/<run_id>/raw-logs/` directory
3. `evidence_paths` entries matching `*.log` glob
4. `evidence_artifacts` entries with `type: raw_log`

Any match should satisfy the check.

### Failing Example
```json
{
  "check": "missing_raw_logs",
  "is_violation": true,
  "logs_found": [],
  "actual_logs_on_disk": [
    "reports/mainstream-r111/raw-logs/fods-dotnet-test.log",
    "reports/mainstream-r111/raw-logs/fodt-dotnet-test.log",
    "reports/mainstream-r111/raw-logs/netpbm-dotnet-test.log",
    "reports/mainstream-r111/raw-logs/python-all-test.log"
  ]
}
```
