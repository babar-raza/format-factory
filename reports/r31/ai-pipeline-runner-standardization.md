# Lane L: AI Pipeline Runner Standardization

## CLI Created
`tools/ai/run_ai_checks.py` — single entry point for all AI checks.

## Supported Modes
| Flag | Description | Tested |
|------|-------------|--------|
| `--fixture` | Deterministic fixture pipeline (default) | PASS |
| `--live-probe` | Live gateway probes | PASS |
| `--no-live` | Skip live probes | PASS |
| `--format` | Target format ID (default: fods) | PASS |
| `--report-dir` | Output directory for JSON report | PASS |
| `--sprint-id` | Sprint identifier for telemetry | PASS |
| `--clean-env` | Clear AI env vars (isolation mode) | PASS |

## Fail-Closed Behavior
- Default mode: fixture only (no live calls)
- `--clean-env` clears all AI env vars before running
- Unconfigured endpoint returns `blocked_no_env`
- No secrets printed to stdout/stderr

## CLI Test Results
| Test | Result |
|------|--------|
| `--fixture --sprint-id R31` | overall_passed: true |
| `--clean-env --fixture` | overall_passed: true |
| `--live-probe --sprint-id R31` | overall_passed: true |

## Status: STANDARDIZED
