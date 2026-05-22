# R51 LLM Provider Summary

**Sprint:** FORMAT-FACTORY-R51-INSTALLED-ARTIFACT-BASELINE-AND-AI-ACCELERATION-001
**Run:** R51
**Date:** 2026-05-22

---

## Provider Configuration

| Field | Value |
|-------|-------|
| Provider | llm.professionalize.com (GPT-OSS gateway) |
| Endpoint | `$GPT_OSS_ENDPOINT` (SET, 35 chars) |
| Auth | Bearer token via `$GPT_OSS_API_KEY` |
| Model routing | `recommended` alias (resolved via endpoint) |
| Model discovery | `/v1/models` endpoint (note: endpoint var includes `/v1` prefix) |

**Note on endpoint URL**: `GPT_OSS_ENDPOINT` already includes the `/v1` path prefix. Chat completions endpoint is `$GPT_OSS_ENDPOINT/chat/completions` (not `$GPT_OSS_ENDPOINT/v1/chat/completions`).

---

## Model Policy

Per AI usage operating model (`docs/ai-usage-operating-model.md`):
- Model routing: use `recommended` alias — do NOT hardcode specific model IDs
- AI type B (synthesis/analysis): GPT-OSS via llm.professionalize.com
- AI type A (agentic high-risk): NOT used in R51
- AI type C (embeddings): NOT used

---

## Calls Made in R51

| Call # | Purpose | Model | Tokens | Status |
|--------|---------|-------|--------|--------|
| 1 | FODS formula preservation design | recommended | 548 | PASS |

---

## Agent Metrics Sink

| Field | Value |
|-------|-------|
| Endpoint | `$AGENT_METRICS_ENDPOINT` (SET, 112 chars) |
| Auth | Query param `?token=$AGENT_METRICS_TOKEN` |
| R51 post | `{"status": 200, "ok": true, "run_id": "R51"}` |

---

## Usage Governance

- All AI outputs tagged as `ai_draft`
- No AI output consumed as authoritative without human review
- AI is accelerator, NOT authority (AGENTS.md AF12, GOVERNANCE.md 26.10)
