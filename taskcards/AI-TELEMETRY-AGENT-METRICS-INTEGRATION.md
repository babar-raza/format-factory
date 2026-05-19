# Taskcard: AI-TELEMETRY-AGENT-METRICS-INTEGRATION

## Objective
Implement AI telemetry: local JSONL spool with Agent Metrics-aligned schema (Phase 1), and Agent Metrics poster integration (Phase 5).

## Status
`phase1_spool_live_verified` — Local JSONL spool with Agent Metrics-aligned schema implemented. R31 (caed52b): spool validation, secret redaction, Agent Metrics mapping all verified. R32: live telemetry evidence hardened — prompt/response hashes logged, no raw content, env var values redacted. No external posting (no AGENT_METRICS_API_KEY). dry_run drain validated. 506 AI tests pass.

## Prerequisites
- AI-PLATFORM-FOUNDATION-PLAN Phase 1 control plane operational

## Allowed Scope
- Implement `tools/ai/telemetry/call_logger.py` (JSONL writer)
- Implement `tools/ai/telemetry/spool_manager.py` (offline spool management)
- Implement `tools/ai/telemetry/agent_metrics_poster.py` (Phase 5)
- Define telemetry schema as Pydantic model in `tools/ai/schemas/`
- Create `.local/ai/llm-logs/` structure
- Create `.local/ai/spool/` structure
- Create tests in `tests/ai/test_telemetry.py`

## Forbidden Scope
- No secrets in telemetry records
- No raw prompt/response content in telemetry (hashes only)
- No product source changes

## Gates
1. JSONL telemetry record written for every AI call
2. All required fields present per telemetry schema
3. No secrets in any telemetry record
4. Spool accumulates when Agent Metrics unreachable
5. (Phase 5) Spool drains successfully to Agent Metrics
6. Evidence bundle includes telemetry summary

## Evidence Requirements
- Sample telemetry records
- Schema validation results
- Secret absence verification
- Spool accumulation/drain test results

## Validation Requirements
- `tests/ai/test_telemetry.py` passes
- No secrets detected in telemetry output

## Closeout Criteria
- Phase 1: Local JSONL spool operational with Agent Metrics-aligned schema
- Phase 5: Agent Metrics posting verified

## Next Transition
Phase 1 closeout enables telemetry for all other AI tasks. Phase 5 closeout completes full telemetry integration.
