# Three-Sprint Forecast (Supervisor R104-R106)

## R104 Supervisor: Raw Logs and State Isolation
- Capture raw pytest/dotnet logs during autonomous-cycle
- Per-stream state directories: reports/supervisor-{stream}/
- Package builder reads per-stream snapshots
- State isolation test: concurrent stream runs don't overwrite
- Fix stale selected-product-gaps.json (regenerate per cycle)

## R105 Supervisor: Grading Confidence and Replay Depth
- Grading confidence score (0-100) based on evidence completeness
- Replay with intentionally mixed-grade packages (not real accepted sprints)
- Grade explanation field: why ACCEPTED_VERIFIED (not just criteria met)
- Regression suite for grade stability across sprints

## R106 Supervisor: Self-Assessment and Graduation
- Supervisor stream grades its own output (self-referential loop)
- Documentation: supervisor-worker-contract v3
- Candidate for autonomous multi-stream dispatch (one cycle triggers all 4 streams)
- Handoff to human for Gate 8/11 decision
