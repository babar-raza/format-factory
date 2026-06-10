# Three-Sprint Forecast (Supervisor R107-R109)

## R107 Supervisor: Raw Log Capture and Subprocess Integration
- Capture pytest stdout/stderr during autonomous-cycle into raw-test-logs/
- Package raw logs alongside source-change-diffs.patch
- ACCEPTED_VERIFIED optionally cites log location
- Grade explanation field

## R108 Supervisor: Per-Stream State Directories
- reports/supervisor-{stream}/ as primary output per stream
- Autonomous-cycle writes to stream-scoped directory
- Package builder reads from stream directory (not shared)
- Shared reports/supervisor/ becomes last-run copy

## R109 Supervisor: Self-Assessment and Graduation
- Supervisor grades its own output (self-referential loop)
- Grade confidence scoring (0-100)
- Autonomous multi-stream dispatch
- Gate 8/11 handoff preparation
