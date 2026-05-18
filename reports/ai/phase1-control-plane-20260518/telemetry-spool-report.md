# Telemetry and Spool Report

**Sprint:** FORMAT-FACTORY-AI-PLATFORM-PHASE1-CONTROL-PLANE-FOUNDATION-001
**Date:** 2026-05-18
**Gate:** GATE 5

## Implementation

- **Call logger:** tools/ai/telemetry/call_logger.py — writes AIUsageRecords to JSONL spool
- **Spool manager:** tools/ai/telemetry/spool_manager.py — lifecycle management, rotation
- **Spool path:** .local/ai/spool/ai-telemetry.jsonl

## Schema Alignment

All 24 telemetry fields from the telemetry-schema.yaml contract are implemented in AIUsageRecord:
timestamp, run_id, sprint_id, taskcard_id, gate_id, provider, endpoint_identity, model, role, operation, input_tokens, output_tokens, total_tokens, api_calls_count, status, error_class_redacted, prompt_hash, input_artifact_hashes, output_artifact_hashes, model_fingerprint, fallback_used, evidence_path, posted_to_agent_metrics

## Phase 1 Constraints

- `posted_to_agent_metrics` = false always (no external posting in Phase 1)
- No raw prompts or responses logged by default (hashes only)
- Secret redaction applied during serialization
- Spool replay is a Phase 2+ placeholder

## Tests

6/6 PASS (test_telemetry.py)

## GATE 5: PASS
