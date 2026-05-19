# Lane G: Agentic/Qwen2 Isolated Verification

## Component Verified
- **ScopedRunner** (`scoped_runner.py`): AgenticTaskContract, run(), max_files, path_allowlist, operation_allowlist, model restriction

## Test Results (5)
| Test | Status |
|------|--------|
| Forbidden path rejected | PASS |
| Forbidden operation rejected | PASS |
| Non-Qwen model rejected | PASS |
| Path prefix bypass blocked | PASS |
| Output discard on violation | PASS |

## Qwen2 Model Status
- Qwen2.5-VL-7B is available at the gateway
- qwen3-next is available (newer version)
- No live agentic tasks performed (not authorized for this sprint)
- Model restriction test confirms only Qwen family models are allowed for agentic tasks

## Status: VERIFIED (isolation)
