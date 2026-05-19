# R30 Lane G: Telemetry and Secret Redaction Hardening
# Date: 2026-05-19

## Defect
`tools/ai/validators/secret_redaction.py`: `_SECRET_ENV_VARS` list was missing `AGENT_METRICS_API_KEY` and `AGENT_METRICS_ENDPOINT`. If those env var values appeared in telemetry/logs, they would not be redacted.

## Fix
Added `AGENT_METRICS_API_KEY` and `AGENT_METRICS_ENDPOINT` to `_SECRET_ENV_VARS` list.

## Tests Added (Lane G in test_r30_ai_defect_closure.py)
- `test_agent_metrics_api_key_in_env_vars`
- `test_agent_metrics_endpoint_in_env_vars`
- `test_sk_pattern_redacted`
- `test_bearer_pattern_redacted`
- `test_contains_secret_detects_sk`
- `test_env_var_value_redacted` — mocks AGENT_METRICS_API_KEY env var, verifies redaction
- `test_clean_text_not_flagged`

## Status: CLOSED_VERIFIED
