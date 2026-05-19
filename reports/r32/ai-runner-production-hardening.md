# AI Runner Production Hardening (Lane K)
## Sprint: FORMAT-FACTORY-R32-AI-CLEAN-CLOSURE-STATUS-REPAIR-AND-PIPELINE-DEEPENING-MEGA-TRAIN-001

## Purpose
Make `tools/ai/run_ai_checks.py` useful for future agents with comprehensive command modes.

## New Command Modes
| Flag | Purpose |
|------|---------|
| --fixture | Run fixture checks (default) |
| --fixture-pipeline | Run fixture pipeline with lexical retrieval |
| --isolation | Run isolation checks only |
| --live-probe | Run live gateway probes |
| --live-pipeline | Run live pipeline with citations |
| --failure-injection | Run failure injection tests via pytest |
| --all | Run all modes (respects --no-live) |
| --no-live | Skip live probes |
| --json | Output JSON only (suppress stderr) |
| --fail-on-blocked-live | Exit 1 if live is blocked |

## Exit Codes
| Code | Meaning |
|------|---------|
| 0 | All required checks pass |
| 1 | Failure |
| 2 | Live blocked but allowed (no --fail-on-blocked-live) |

## New Functions
- `run_failure_injection_checks()` — runs pytest with failure injection filter
- `run_fixture_pipeline_checks()` — runs e2e pilot with lexical retrieval

## Tests (TestAIRunnerCLI)
1. `test_runner_fixture_mode_returns_results` — fixture returns passed=True
2. `test_runner_isolation_mode_returns_results` — isolation returns passed=True
3. `test_runner_fixture_pipeline_mode` — fixture_pipeline uses lexical retrieval
4. `test_runner_produces_json_output` — CLI output is valid JSON
5. `test_runner_exit_code_0_on_pass` — exit code 0 on success

## Backward Compatibility
- Default behavior unchanged (--fixture + --isolation when no flags)
- All existing CLI patterns still work
