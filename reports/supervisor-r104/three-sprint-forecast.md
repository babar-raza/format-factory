# Three-Sprint Forecast (Supervisor R105-R107)

## R105 Supervisor: Per-Stream State Directories
- Full per-stream state isolation: reports/supervisor-{stream}/ as primary
- Autonomous-cycle writes stream-scoped outputs
- Package builder reads from stream-scoped directory, not shared
- Shared reports/supervisor/ becomes symlink or copy of last-run stream

## R106 Supervisor: Raw Log Capture and Replay Depth
- Capture raw pytest/dotnet stdout/stderr during autonomous-cycle
- Replay with intentionally mixed-grade packages
- Grade explanation field: why grade was assigned
- Regression suite for grade stability across sprints

## R107 Supervisor: Self-Assessment and Graduation
- Supervisor stream grades its own output (self-referential loop)
- Documentation: supervisor-worker-contract v3
- Candidate for autonomous multi-stream dispatch
- Handoff to human for Gate 8/11 decision
