# Lane B: AI Test Isolation Hardening

## Bug Found and Fixed
Two tests failed in clean-env mode (env vars cleared):
1. `test_model_discovery.py::TestModelDiscovery::test_discover_parses_model_list`
2. `test_phase2_model_registry.py::TestDiscoverModelsPhase2::test_discover_populates_family_and_candidates`

### Root Cause
Both tests patched `tools.ai.control_plane.config.get_api_key` instead of
`tools.ai.control_plane.model_discovery.get_api_key`. Since `model_discovery.py`
imports `get_api_key` directly (`from ... import get_api_key`), the mock must
target the name in the consuming module, not the defining module.

When real env vars were present, the unpatched function still returned a valid key,
masking the bug. When env was cleared, `get_api_key()` returned None and
`discover_models()` returned `[]` early.

### Fix
Changed patch target from `tools.ai.control_plane.config.get_api_key` to
`tools.ai.control_plane.model_discovery.get_api_key` in both test files.

## Clean-env Test Results
- Before fix: 356 passed, 2 failed
- After fix: 358 passed, 0 failed (with env), 358 passed, 0 failed (clean-env)
- After R31 tests added: 449 passed, 0 failed (both modes)

## Regression Tests Added
- `TestCleanEnvRegression::test_discover_models_uses_mocked_api_key`
- `TestCleanEnvRegression::test_discover_returns_empty_when_api_key_missing_and_env_clear`
- `TestCleanEnvRegression::test_gateway_import_requires_litellm`
- `TestCleanEnvRegression::test_no_litellm_import_in_product_source`

## litellm Import Status
- `gateway.py` is the ONLY file importing litellm at top level
- All tests that exercise gateway.py require litellm in the environment
- The venv has litellm installed; system Python does not
- No product source (src/python/, src/net/) imports AI libraries (runtime guard verified)

## Status: HARDENED
