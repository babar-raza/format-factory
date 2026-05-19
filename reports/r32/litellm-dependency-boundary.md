# litellm Dependency Boundary (Lane H)
## Sprint: FORMAT-FACTORY-R32-AI-CLEAN-CLOSURE-STATUS-REPAIR-AND-PIPELINE-DEEPENING-MEGA-TRAIN-001

## Purpose
R31 noted litellm is imported at top level in gateway.py, causing all AI tests to require litellm even for fixture/offline work.

## Decision
**Lazy import** — litellm is now imported only when `_get_litellm()` is called inside `gateway_chat()`, which only happens when config is configured AND api_key is present AND a live call is actually attempted.

## Implementation
- **File changed:** tools/ai/control_plane/gateway.py
- **Change:** Removed `import litellm` at top level, added `_get_litellm()` function
- **_get_litellm():** Raises `ImportError` with clear message if litellm is not installed
- **Error message:** "litellm is required for live AI gateway calls. Install it with: pip install litellm. Non-live AI tests and fixture pipelines do not require litellm."

## Behavior Matrix
| Scenario | litellm installed | litellm missing |
|----------|------------------|-----------------|
| Fixture pipeline | Works (never calls gateway) | Works (never calls gateway) |
| Offline AI tests | Works (mock patches) | Works (mock patches, gateway not called) |
| Live probe | Works (litellm loaded lazily) | ImportError with clear message |
| gateway_chat unconfigured | Returns blocked_missing_env | Returns blocked_missing_env (never reaches litellm) |

## Tests
1. `test_gateway_module_imports_without_litellm_at_top_level` — no bare `import litellm` in gateway.py
2. `test_fixture_pipeline_works_without_litellm_call` — fixture pipeline passes without gateway
3. `test_gateway_lazy_import_produces_clear_error` — `_get_litellm()` returns module when available
4. `test_blocked_config_does_not_call_litellm` — unconfigured config returns blocked without litellm

## Impact
- All 506 AI tests pass (with env and clean-env)
- No breaking changes to existing test patterns
- Existing mock patches work unchanged
