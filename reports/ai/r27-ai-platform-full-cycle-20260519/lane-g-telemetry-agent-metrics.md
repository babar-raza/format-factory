# Lane G: AI Telemetry and Agent Metrics Integration

## Implementation
Created `tools/ai/telemetry/drain.py` with:
1. `map_spool_to_agent_metrics()` — maps local spool records to Agent Metrics payload format
2. `validate_drain_payload()` — validates all required fields and checks for secret leaks
3. `drain_spool()` — drains spool with dry_run=True by default
4. `is_agent_metrics_configured()` — checks AGENT_METRICS_ENDPOINT + AGENT_METRICS_API_KEY env vars
5. Required Agent Metrics fields: timestamp, agent_name, product, platform, website, website_section, job_type, run_id, sprint_id, taskcard_id, model, endpoint_identity, token_usage, api_calls_count, run_duration_ms, status, posted_to_agent_metrics

## Tests (6)
- test_valid_mapping, test_missing_fields_get_defaults
- test_valid_payload, test_secret_in_payload, test_bearer_token_detected
- test_dry_run_empty_spool, test_dry_run_with_records

## Agent Metrics Status: BLOCKED_MISSING_ENV
- AGENT_METRICS_ENDPOINT and AGENT_METRICS_API_KEY not set
- Dry-run validation passes
- No external posting attempted

## .env.example Entries
- AGENT_METRICS_ENDPOINT=
- AGENT_METRICS_API_KEY=

## Lane G Status: CLOSED_VERIFIED (dry-run mode, BLOCKED_MISSING_ENV for live posting)
