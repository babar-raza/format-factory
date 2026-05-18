# Validation and Regression Strategy

**Date:** 2026-05-18

## 1. Validation Layers

### Layer 1 — Schema Validation
- All AI inputs validated against Pydantic models before calls
- All AI outputs validated against Pydantic models before acceptance
- Schema violations immediately reject the output
- Schema registry tracks versions and breaking changes

### Layer 2 — Citation Verification
- Every factual claim in synthesis output must cite a source chunk ID
- Source-support verifier confirms the cited chunk contains supporting text
- Citation failures trigger output rejection and hallucination flagging

### Layer 3 — Contradiction Detection
- Synthesis output compared against existing verified facts
- Contradictions flagged for human review before resolution
- Contradiction rate tracked in telemetry

### Layer 4 — Golden Evaluations
- Per-task-type golden eval datasets
- Known-good input/output pairs
- Regression detection on model change, prompt change, or schema change
- Eval score threshold per task type (configurable)

### Layer 5 — Artifact Authority Lifecycle
- 12-state machine enforced programmatically
- No skip from ai_draft to authoritative
- Each transition requires specific validation pass
- State transition audit log

### Layer 6 — Runtime Guard
- Static import analysis on src/python/ and src/net/
- Blocks imports of tools/ai, LiteLLM, LlamaIndex, LanceDB, endpoint clients
- Runs in CI and as pre-commit check

### Layer 7 — Risk Register Validation
- Each of 48 risks has at least one automated test
- CRITICAL risks have multiple tests
- Stop conditions enforced programmatically where possible

## 2. Regression Controls

### Model Regression
- Trigger: model fingerprint change detected by discovery
- Action: run full golden eval suite; compare against baseline
- Threshold: >20% degradation triggers pause and investigation

### Prompt Regression
- Trigger: prompt version hash change
- Action: run golden evals for affected task types
- Threshold: >15% degradation triggers revert

### Schema Regression
- Trigger: schema version change
- Action: run downstream consumer compatibility tests
- Threshold: breaking change requires migration plan

### Index Regression
- Trigger: source hash change, embedding model change
- Action: re-index affected format; run retrieval eval
- Threshold: recall <60% triggers investigation

## 3. No-Runtime-AI Import Guard

Protected paths: `src/python/**`, `src/net/**`
Blocked imports: `tools/ai`, `litellm`, `llama_index`, `lancedb`, `openai`, `anthropic`, `ollama`
Blocked env refs: `GPT_OSS_ENDPOINT`, `GPT_OSS_API_KEY`
Exception: `tools/**` may import AI infrastructure

## 4. Evidence Bundle Integration

Every sprint that uses AI must include:
- Telemetry summary
- Eval results
- Citation verification stats
- Contradiction detection stats
- Artifact authority state summary
- Risk control test results
