# Lane M: AI Docs/Taskcards Status Repair

## Reconciliation Findings (from Lane A)

### Stale Claims Fixed
1. **Model discovery "live" claim**: R30 taskcards implied models were "discovered live" when env vars were incidentally present during test execution. R31 is the first sprint to perform governed live probes with evidence.

2. **Endpoint "not configured" claim**: AI-GPT-OSS-SYNTHESIS-CONTROLS.md was stale from Phase 1. The endpoint has been configured since at least R30.

3. **"No live probes"**: R30 correctly reported no intentional governed live probes. R31 establishes the live probe baseline.

## AI System Verification Matrix

| Component | Fixture Verified | Isolated Verified | Pipeline Fixture | Pipeline Live | Blocked |
|-----------|-----------------|-------------------|------------------|---------------|---------|
| Config | yes | yes | yes | yes | - |
| Model Discovery | yes | yes | yes | yes (7 models) | - |
| Model Router | yes | yes | yes | - | - |
| Capability Probe | yes | yes | - | yes (PROBE_OK) | - |
| Gateway | yes | yes | yes | yes | - |
| Synthesis Runner | yes | yes | yes | yes | - |
| Evaluator | yes | yes | yes | yes | - |
| Citation Verifier | yes | yes | yes | - | - |
| Contradiction Detector | yes | yes | yes | yes | - |
| Requirements Generator | yes | yes | yes | - | - |
| Authority Lifecycle | yes | yes | yes | - | - |
| Scoped Runner | yes | yes | - | - | No live agentic |
| Namespace Manager | yes | yes | - | - | No vector store |
| Telemetry/Spool | yes | yes | - | - | No Agent Metrics post |
| Secret Redaction | yes | yes | yes | yes | - |
| Runtime Guard | yes | yes | - | - | - |

## Status: REPAIRED
