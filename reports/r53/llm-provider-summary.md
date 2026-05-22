# LLM Provider Summary

**Sprint:** FORMAT-FACTORY-R53-SELF-VERIFYING-BASELINE-001
**Date:** 2026-05-22

## Configured Providers

| Provider | Env Var | Status | Role |
|---------|---------|--------|------|
| GPT-OSS (via llm.professionalize.com) | GPT_OSS_ENDPOINT + GPT_OSS_API_KEY | CONFIGURED | Type B synthesis (governed) |
| Anthropic | ANTHROPIC_KEY | CONFIGURED | Type A agentic (restricted) |
| OpenAI | OPENAI_API_KEY | CONFIGURED | Type B synthesis alt |
| Agent Metrics | AGENT_METRICS_ENDPOINT | CONFIGURED | Telemetry sink |

## AI Type Classification (R27 Platform)

| Type | Description | Provider | Status |
|------|-------------|----------|--------|
| A — Agentic | High-risk agentic ops (Claude/Codex) | Anthropic | Restricted to `agentic_low_risk` for Qwen2 only |
| B — Synthesis | Citation-verified content generation | GPT-OSS | Available with citation check |
| C — Embeddings | Vector embeddings (LanceDB) | TBD | NOT IMPLEMENTED (Phase 3) |

## Live Calls in R53

None. All AI operations were fixture mode only.

## Governance

All providers must route through `tools/ai/control_plane/gateway.py`.
No direct provider calls outside the gateway. See ai-gateway-direct-call-audit.md.
