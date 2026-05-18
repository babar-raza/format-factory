# Recovery and Failure Handling Plan

**Sprint:** FORMAT-FACTORY-AI-PLATFORM-FINAL-PLAN-HEALING-AND-IMPLEMENTATION-READINESS-001
**Date:** 2026-05-18
**Gate:** GATE 7

## 1. Model Unavailability

| Scenario | Detection | Recovery | Escalation |
|----------|-----------|----------|------------|
| llm.professionalize.com unreachable | Connection timeout (configurable) | Fail-closed: no AI output produced | Log telemetry, alert operator |
| Model removed from endpoint | Discovery returns empty/missing model | Fail-closed: role has no available model | Log, block affected task type |
| API key expired/invalid | 401/403 response | Fail-closed: no retry with bad credentials | Alert operator for credential rotation |

## 2. Output Validation Failures

| Scenario | Detection | Recovery | Escalation |
|----------|-----------|----------|------------|
| Schema validation failure | Pydantic raises ValidationError | Reject output, retry once with same prompt | If retry fails: fail task, log |
| Citation verification failure | Source chunk not found or unsupporting | Reject output, flag as hallucination | Human review queue |
| Contradiction detected | Conflict with verified fact | Reject output, flag for human review | Human resolves contradiction |
| Golden eval regression >threshold | Eval score below configured floor | Pause affected task type | Investigate model/prompt change |

## 3. Vector Store Failures

| Scenario | Detection | Recovery | Escalation |
|----------|-----------|----------|------------|
| Corrupt LanceDB index | Read error or hash mismatch | Delete and rebuild from source | Log, verify rebuild |
| Stale index (source hash changed) | Hash comparison on access | Auto-rebuild triggered | Log rebuild |
| Embedding model unavailable | Discovery failure | Fail-closed: no retrieval | Alert operator |
| Cross-format namespace leak | Namespace audit check | Quarantine affected namespace | Investigate root cause |

## 4. Telemetry Failures

| Scenario | Detection | Recovery | Escalation |
|----------|-----------|----------|------------|
| Agent Metrics endpoint down | POST failure | Spool to local JSONL | Replay spool when endpoint recovers |
| Local spool corruption | Read/parse error | Rotate spool file, start fresh | Log lost records count |
| Spool replay failure | Replay POST returns error | Exponential backoff retry | Alert after N failures |

## 5. Artifact Authority Failures

| Scenario | Detection | Recovery | Escalation |
|----------|-----------|----------|------------|
| State skip attempted | State machine guard rejects | Block transition, log violation | Alert, investigate caller |
| Invalid backward transition | State machine guard rejects | Block, maintain current state | Log |
| Missing validation for transition | Transition prerequisite check | Block until validation passes | Queue for required validation |

## 6. Runtime Guard Failures

| Scenario | Detection | Recovery | Escalation |
|----------|-----------|----------|------------|
| AI import in src/ detected | Static analysis (CI + pre-commit) | Block commit/merge | Developer must remove import |
| Guard bypass attempted | CI check always runs | Merge blocked | Review for policy violation |

## 7. Cross-Sprint Safety

| Scenario | Detection | Recovery | Escalation |
|----------|-----------|----------|------------|
| AI sprint modifies non-AI file | Path allowlist check in contract | Reject change, revert file | Sprint scope violation |
| Non-AI sprint depends on AI layer | Import analysis + dependency check | Block until AI layer is stable | Architectural review |

## Stop Conditions

The following conditions trigger immediate halt of AI operations:
1. Any CRITICAL-severity risk control test fails
2. Model fingerprint changes without eval pass
3. Hallucination rate exceeds configured threshold
4. Runtime guard detects AI import in product source
5. Artifact authority state machine is bypassed

## GATE 7 (Part 2): PASS
