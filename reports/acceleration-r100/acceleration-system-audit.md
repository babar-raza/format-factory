# Acceleration System Audit -- Train A

## Tool Inventory (7 tools + 13 skills)

### Acceleration Tools (tools/supervisor/)

| Tool | Created | Tests | Last Enhanced | Gaps |
|------|---------|-------|---------------|------|
| select_poc_gaps.py | pre-R90 | 12 (R99) | R99 v3 | Stale sprint in stream output, no sprint_id embed |
| choose_skill_or_handoff.py | pre-R90 | 10 (R99) | R99 v2 | 8 work types needed, only 4 covered |
| record_lane_execution.py | R99 | 10 | R99 v1 | No dep graph, no subagent_id, no bottleneck_tags |
| generate_sprint_learning.py | R99 | 7 | R99 v1 | No parallelization suggestions, no shallow warnings |
| package_install_proof.py | R99 | 5 | R99 v1 | No .NET, no wheel install, no blocker report |
| detect_product_progress.py | pre-R90 | 0 | pre-R90 | No tests, no per-category breakdown |
| materialize_declared_evidence.py | R92 | 0 (via supervisor) | R94 | Works, but multi-step |
| build_declaration_review_package.py | R92 | 0 (via supervisor) | R94 | Works, but manual sequence |

### Stale Behaviors Found

1. `select_poc_gaps.py`: Per-stream files lack `sprint_id`; no stale-detection
2. `choose_skill_or_handoff.py`: Work types test-only, docs, package-proof, supervisor-tooling not recognized
3. `detect_product_progress.py`: Zero unit tests; only fingerprint comparison

### Manual Steps Still Repeated

1. Writing evidence-declaration.yaml (YAML by hand)
2. Running materializer + review package (2 separate commands)
3. Writing preflight/scoreboard/lane-ownership reports (copy-paste pattern)
4. Composing next-agent briefing (manual markdown)

### Priority Actions for R100

1. Add work-type rules to router (Train C)
2. Create execution handoff generator tool (Train D)
3. Add dependency graph + bottleneck tags to lane recorder (Train E)
4. Add parallelization + shallow warnings to sprint learning (Train F)
5. Add .NET + wheel support to package proof (Train G)
6. Add tests + per-category detection to progress detector (Train H)
7. Create one-command materialization wrapper (Train I)
