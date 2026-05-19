# R32 Lane Ownership and Overlap Matrix
## Sprint: FORMAT-FACTORY-R32-AI-CLEAN-CLOSURE-STATUS-REPAIR-AND-PIPELINE-DEEPENING-MEGA-TRAIN-001

| Lane | Owner | Scope | Overlaps |
|------|-------|-------|----------|
| 0 | Coordinator | Sprint state, contract, bundle, verdict | All lanes |
| A | R31 metadata repair | R31 forward-documentation | Lane B (validator), Lane L (docs) |
| B | Evidence validator hardening | Closure metadata tests | Lane A (repair target) |
| C | AI verification matrix | Canonical docs/ai/ doc | Lane L (docs sync) |
| D | AI taskcard truth repair | taskcards/AI-*.md | Lane L (docs sync) |
| E | Deterministic retrieval | tools/ai/retrieval/ | Lane F (pipeline uses it) |
| F | Pipeline fixture w/ retrieval | Pipeline + retrieval integration | Lane E (retrieval), Lane K (runner) |
| G | Live pipeline w/ citations | Live gateway + synthesis + citation | Lane I (telemetry) |
| H | litellm dependency boundary | gateway.py lazy import | Lane G (live needs litellm) |
| I | Telemetry evidence | Redacted telemetry records | Lane G (live generates telemetry) |
| J | Failure injection expansion | 20 new test cases | Lane E (retrieval), Lane B (validation) |
| K | AI runner hardening | run_ai_checks.py CLI | Lane F (fixture-pipeline mode) |
| L | AI docs/governance sync | docs/ai/, memory/ | Lanes A, C, D |
| M | Full validation | All test suites | All implementation lanes |
| N | Independent verification | IV report | All lanes |
| O | Adversarial review | 30 questions + evidence bundle | All lanes |

## Anti-Shrink Rule
No lane blocker stops other lanes. If live probe fails, Lane G documents "blocked-live" and all other lanes continue.
