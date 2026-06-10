# Acceleration System Gap Analysis -- R100

## R99 State Assessment

| Tool | Has Tests | Has CLI | Runs | Gap |
|------|-----------|---------|------|-----|
| select_poc_gaps.py | 12 | YES | YES | Stale sprint ID in per-stream output |
| choose_skill_or_handoff.py | 10 | YES | YES | Doesn't cover test-only/docs/package proof |
| record_lane_execution.py | 10 | YES | YES | No dependency graph, no subagent ID |
| generate_sprint_learning.py | 7 | YES | YES | No parallelization/shallow warnings |
| package_install_proof.py | 5 | YES | YES | No .NET, no wheel smoke |
| detect_product_progress.py | 0 | YES | YES | No per-category breakdown |
| generate_execution_handoff (tool) | 0 | NO | N/A | Does not exist as standalone tool |
| materialization wrapper | 0 | NO | N/A | Multi-step manual process |
| next-prompt helper | 0 | NO | N/A | Does not exist |

## Priority Map

1. **HIGH**: Execution handoff generator -- needed by every non-skill gap
2. **HIGH**: Router work-type expansion -- blocks correct routing
3. **HIGH**: Progress detector tests + per-category breakdown
4. **MEDIUM**: Lane recorder dependency graph + bottleneck tags
5. **MEDIUM**: Sprint learning parallelization suggestions
6. **MEDIUM**: Package proof .NET + wheel support
7. **MEDIUM**: Materialization one-command wrapper
8. **LOW**: Stream gap stale sprint detection
9. **LOW**: Next-prompt helper (mostly done by supervisor)
