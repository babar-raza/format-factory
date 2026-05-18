# Model Discovery and Routing Report

**Sprint:** FORMAT-FACTORY-AI-PLATFORM-PHASE1-CONTROL-PLANE-FOUNDATION-001
**Date:** 2026-05-18
**Gate:** GATE 4

## Live Endpoint Status

- **Endpoint identity:** llm.professionalize.com
- **Status:** AVAILABLE
- **API key:** configured (not logged)

## Models Discovered (7)

| Model ID | Chat | Embedding | Context |
|----------|------|-----------|---------|
| qwen3-next | yes | no | - |
| experimental | yes | no | - |
| gpt-oss | yes | no | - |
| recommended | yes | no | - |
| qwen3-embedding-8b | yes | yes | - |
| Qwen2.5-VL-7B | yes | no | - |
| stable-diffusion-3.5-large | yes | no | - |

## Capability Probe

- **Model probed:** gpt-oss
- **Probe template:** capability_probe_v1
- **Response:** PROBE_OK
- **Status:** success
- **Tokens:** input=72, output=54

## Routing Implementation

- Role-based routing implemented via ModelRouter
- Fail-closed when no model satisfies a role
- Fallback to any chat-capable model with logging
- Preferred model selection supported
- No hardcoded model names

## Secrets

- No API key logged, printed, or included in telemetry records
- Endpoint identity shows hostname only (llm.professionalize.com)

## GATE 4: PASS
