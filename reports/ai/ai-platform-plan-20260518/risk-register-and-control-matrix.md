# Risk Register and Control Matrix Report

**Date:** 2026-05-18

## Summary

The AI risk register (`docs/ai/ai-risk-register.md`) contains 48 unique risks (RISK-AI-001 through RISK-AI-048) covering all identified failure modes for the AI platform.

## Severity Distribution

| Severity | Count | IDs |
|----------|-------|-----|
| CRITICAL | 5 | 006, 018, 020, 029, 030 |
| HIGH | 12 | 001, 002, 003, 007, 011, 019, 021, 022, 035, 038, 042, 048 |
| MEDIUM | 22 | 004, 005, 008, 009, 010, 012-017, 023-028, 037, 039, 041, 043, 044, 045, 046, 047 |
| LOW | 9 | 032, 033, 034, 036, 040 |
| **Total** | **48** | |

## Category Coverage

| Category | Count | Risk IDs |
|----------|-------|----------|
| Model availability/behavior | 5 | 001-005 |
| Hallucination/citation | 2 | 006-007 |
| Retrieval quality | 5 | 008-012 |
| Configuration drift | 3 | 013-015 |
| Telemetry | 3 | 016-017, 023 |
| Security | 2 | 018, 036 |
| Authority/governance | 4 | 019-022 |
| Quality control | 4 | 024-025, 028, 040 |
| Evidence/state | 2 | 026-027 |
| Source/release safety | 2 | 029-030 |
| Technology/dependency | 4 | 031-035 |
| Adversarial input | 2 | 038-039 |
| Context management | 1 | 037 |
| New risks (041-048) | 8 | 041-048 |

## New Risks Added (This Sprint)

| Risk ID | Description | Severity |
|---------|-------------|----------|
| RISK-AI-041 | Qwen2 agentic task produces structurally valid but semantically wrong output | MEDIUM |
| RISK-AI-042 | GPT-OSS synthesis produces plausible but factually wrong requirements | HIGH |
| RISK-AI-043 | Schema-valid output contains unsupported claims | MEDIUM |
| RISK-AI-044 | Contradiction with existing verified facts not detected | MEDIUM |
| RISK-AI-045 | Global vector cache pollution from shared .local directory | MEDIUM |
| RISK-AI-046 | Local telemetry/spool file corruption | MEDIUM |
| RISK-AI-047 | Deferred feature forgotten after classification | MEDIUM |
| RISK-AI-048 | Non-AI sprint accidentally depends on AI layer | HIGH |

## Field Completeness

All 48 risks have: risk ID, description, affected layer, severity, likelihood, detection mechanism, prevention control, mitigation action, validation test, evidence artifact, owner/taskcard, stop condition.

## Implementation Priority

CRITICAL risks (006, 018, 020, 029, 030) require validation tests in Phase 1. HIGH risks require tests by Phase 2. MEDIUM/LOW risks require tests by Phase 6.
