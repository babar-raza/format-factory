---
taskcard_id: LLM-001
title: LLM Model Discovery and Endpoint Preflight for llm.professionalize.com
status: proposed_pending_human_approval
created: 2026-05-08
sprint: memory-sprint-format-understanding-llm-strategy
visibility: internal
relationship_to_main_sprint: backlog — not a MAIN SPRINT gate
relationship_to_product_source: not a product source task
---

# LLM-001 — LLM Model Discovery and Endpoint Preflight

## Purpose

Perform safe model discovery and endpoint preflight for llm.professionalize.com.
Enumerate available models (GPT OSS, Qwen Next, embedding models) and verify that the
endpoint is reachable, credential policy is correct, and no secrets are exposed.

## Scope

- Set up environment variable policy for LLM_ENDPOINT, LLM_API_KEY (names TBD)
- Implement a safe preflight script (tools/llm/llm_preflight.py or equivalent)
- Enumerate available models via endpoint metadata (no production calls)
- Record: model names, families, context lengths, embedding dimensions
- Verify redaction policy (no secrets in logs, no tokens in evidence)
- Create model-selection.yaml with discovered model families and capabilities

## Allowed Files

- tools/llm/llm_preflight.py (new)
- tools/llm/model-selection.yaml (existing — update)
- tools/llm/endpoints.yaml (existing — add llm.professionalize.com entry without secrets)
- .env.example (update with new env var names — no actual values)
- plans/master-plan.md (update)
- evidence bundle

## Forbidden Files

- .env (never — secrets)
- Any file containing actual API keys or tokens
- src/python/fods/ or src/net/fods/
- .local/embeddings/

## Secret Policy

- LLM_ENDPOINT: environment variable only
- LLM_API_KEY: environment variable only, NEVER committed
- Preflight script reads from os.environ, does NOT hardcode
- All log output must be redacted before evidence bundle inclusion
- model-selection.yaml must NOT contain API keys

## Acceptance Criteria

1. Preflight script runs without secrets in code.
2. Model enumeration output recorded in model-selection.yaml (names only, no keys).
3. DEC-034 PASS.
4. Human approval.
5. Evidence bundle PASS with no secrets.

## Future Trigger

Human explicitly authorizes LLM-001 execution with LLM endpoint access confirmed.

## Status

proposed_pending_human_approval — no LLM calls made in this memory sprint.
