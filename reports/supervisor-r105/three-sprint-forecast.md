# Three-Sprint Forecast (Supervisor R106-R108)

## R106 Supervisor: Per-Stream State Directory and Markdown Regeneration
- Per-stream state directories: reports/supervisor-{stream}/ as primary output
- evidence-review.md and contradictions.md regenerated from JSON (currently missing)
- Package builder reads stream-scoped directory
- Shared reports/supervisor/ becomes last-run copy

## R107 Supervisor: Grade Confidence Scoring and Replay Depth
- Grading confidence score (0-100) based on evidence quality
- Replay with mixed-grade packages to validate grading stability
- Grade explanation field in JSON output
- Regression suite for grade stability

## R108 Supervisor: Self-Assessment and Multi-Stream Dispatch
- Supervisor grades its own output
- Autonomous multi-stream dispatch (one cycle triggers all 4 streams)
- supervisor-worker-contract v3 documentation
- Gate 8/11 handoff preparation
