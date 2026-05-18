# Model Routing and Agentic Control Review

**Sprint:** FORMAT-FACTORY-AI-PLATFORM-FINAL-DEEP-PLAN-HEALING-001
**Date:** 2026-05-18
**Gate:** 5
**Lane:** L5

---

## 1. Model Discovery Design Review

### 1.1 Discovery Flow

```
1. Read GPT_OSS_ENDPOINT from os.environ (fail if unset)
2. Read GPT_OSS_API_KEY from os.environ (fail if unset)
3. Call GET {endpoint}/v1/models with auth header
4. Parse response → list of DiscoveredModel
5. For each model: probe capabilities (chat, embedding, structured_output, json_mode)
6. Compare against previous discovery cache
7. Log diff if model set changed
8. Store in .local/ai/model-registry/models-{timestamp}.json
9. Return ModelRegistry
```

### 1.2 Failure Modes

| Failure | Detection | Response | Recovery |
|---------|-----------|----------|----------|
| GPT_OSS_ENDPOINT unset | os.environ check | Fail immediately with clear error | Set env var |
| GPT_OSS_API_KEY unset | os.environ check | Fail immediately with clear error | Set env var |
| Endpoint unreachable | HTTP timeout/error | Use cached registry if < 24h old | Wait and retry manually |
| Cache expired + endpoint down | Cache timestamp check | Fail closed — no AI operations | Fix connectivity |
| API returns unexpected shape | JSON schema validation | Log error, fail closed | Investigate endpoint |
| Model removed | Diff against previous | Log ROLE_UNAVAILABLE for affected roles | Update role contracts |
| New model added | Diff against previous | Log discovery, do NOT auto-route | Human review new model |

### 1.3 Discovery Cache Schema

```
ModelRegistry:
  discovered_at: datetime
  endpoint_url: str              # URL without auth
  models: list[DiscoveredModel]

DiscoveredModel:
  model_id: str
  capabilities: list[str]        # ["chat", "embedding", "structured_output", "json_mode", "function_calling"]
  context_window: Optional[int]
  max_tokens: Optional[int]
  embedding_dimensions: Optional[int]
  model_family: str              # Inferred: "gpt-oss", "qwen2", "embedding", "unknown"
  fingerprint: Optional[str]
  discovery_probe_results: dict  # Raw capability probe outcomes
```

## 2. Role-Based Routing Stress Analysis

### 2.1 Selection Algorithm (Concrete)

```python
def select_model(role: ModelRole, registry: ModelRegistry) -> SelectedModel:
    requirement = ROLE_REQUIREMENTS[role]

    # Step 1: Filter by minimum capabilities
    candidates = [m for m in registry.models
                  if all(cap in m.capabilities for cap in requirement.required_capabilities)
                  and (m.context_window or 0) >= requirement.min_context_window]

    if not candidates:
        raise RoleUnavailableError(role)

    # Step 2: Prefer model family
    preferred = [m for m in candidates if m.model_family == requirement.preferred_model_family]

    if preferred:
        return SelectedModel(model_id=preferred[0].model_id, was_fallback=False)

    # Step 3: Fallback order
    for fallback_family in requirement.fallback_order:
        fallback = [m for m in candidates if m.model_family == fallback_family]
        if fallback:
            return SelectedModel(model_id=fallback[0].model_id, was_fallback=True)

    # Step 4: No acceptable model
    raise RoleUnavailableError(role)
```

### 2.2 Stress Scenarios

| Scenario | Expected Behavior | Test |
|----------|------------------|------|
| Only GPT-OSS available | All GPT-OSS roles succeed; Qwen2 roles get GPT-OSS as fallback | Mock registry with one model |
| Only Qwen2 available | agentic_low_risk succeeds; structured_extraction fails (no fallback) | Mock registry with Qwen2 only |
| No models available | All roles fail with ROLE_UNAVAILABLE | Empty registry |
| Model has wrong context window | Role requiring 16K rejects model with 4K | Mock undersized model |
| New unknown model appears | Not auto-routed; logged for human review | Mock new model family |
| Model disappears between calls | Mid-task failure → task stops, telemetry recorded | Mock model removal |

## 3. Qwen2 Agentic Control Review

### 3.1 Scope Guard Design

The scope guard enforces boundaries at runtime:

```
ScopeGuardConfig:
  path_allowlist: list[str]      # Glob patterns of readable paths
  path_denylist: list[str]       # Explicit deny (overrides allow)
  op_allowlist: list[str]        # Allowed operations: read, classify, sort, extract
  op_denylist: list[str]         # Forbidden: write, delete, execute, modify
  max_output_tokens: int
  timeout_seconds: int
  state_machine_def: str         # Reference to task state machine
```

### 3.2 What Qwen2 CAN Do

- Read files within path_allowlist
- Classify format candidates
- Sort/rank items by criteria
- Extract structured facts from text
- Return structured JSON output
- Log all actions to telemetry

### 3.3 What Qwen2 CANNOT Do

- Write or modify any file
- Access src/python/ or src/net/
- Access .env or any secret file
- Make network calls beyond the LLM endpoint
- Approve gates or authority transitions
- Generate code for implementation
- Modify taskcards, evidence, or governance docs
- Override scope guard restrictions
- Retry after scope violation (immediate stop)

### 3.4 Qwen2 Failure Handling

| Failure | Response | Rollback |
|---------|----------|----------|
| Scope violation (path access) | Immediate stop; discard ALL output; log violation | No partial output accepted |
| Scope violation (operation) | Immediate stop; discard ALL output; log violation | No partial output accepted |
| Timeout | Stop; discard output | Task can be retried with same contract |
| Schema validation failure | Reject output; log | Retry once; if fails again, escalate to GPT-OSS |
| Semantic accuracy below threshold | Reject output; log | Escalate to GPT-OSS or human |

## 4. GPT-OSS Synthesis Control Review

### 4.1 Citation Verification Design

For every factual claim in synthesis output:

```
1. Extract claim text and cited chunk_id
2. Load cited chunk from normalized spec cache
3. Check: does chunk text contain supporting evidence for claim?
4. Scoring: full_support (1.0), partial_support (0.5), no_support (0.0)
5. Aggregate: if any claim scores 0.0, reject output
6. If average support score < 0.7, flag for review
```

### 4.2 Contradiction Detection Design

```
1. Load verified-facts.yaml for target format
2. For each claim in synthesis output:
   a. Compare against all verified facts
   b. Check for direct contradiction (opposite assertion)
   c. Check for scope contradiction (claim about wrong spec version)
   d. Check for magnitude contradiction (numeric values differ significantly)
3. If any contradiction found: reject output, log contradiction details
4. If no verified-facts.yaml exists for format: skip (flag in evidence)
```

### 4.3 Evaluator/Regression Design

```
1. Load golden eval fixtures for task type from tools/ai/evals/fixtures/{task_type}/
2. Run synthesis on golden input
3. Compare output against golden expected output
4. Score: structural match, factual accuracy, citation quality
5. If score < role quality_threshold: reject
6. Log eval results in telemetry
```

## 5. What Breaks If Controls Are Weak

| Missing Control | Consequence |
|----------------|-------------|
| No scope guard | Qwen2 reads secrets or modifies files |
| No citation verifier | Hallucinated requirements enter pipeline |
| No contradiction detector | AI output contradicts verified facts |
| No eval regression | Model update silently degrades quality |
| No fail-closed routing | Bad model serves critical role |
| No discovery diff | Model removal goes unnoticed |
