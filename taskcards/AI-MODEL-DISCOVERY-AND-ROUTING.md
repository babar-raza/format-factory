# Taskcard: AI-MODEL-DISCOVERY-AND-ROUTING

## Objective
Implement and validate dynamic model discovery and role-based routing at llm.professionalize.com. Ensure fail-closed behavior, capability probing, model fingerprinting, and fallback policy.

## Status
`live_verified` — Model discovery, capability probe, and role-based routing implemented in Phase 1. R31 governed live verification (caed52b): 7 models discovered, PROBE_OK on gpt-oss, structured extraction valid. R32 live pipeline (qwen3-next): discovery + probe + citation-verified synthesis. 506 AI tests pass. Router fail-closed behavior verified in R31+R32 failure injection.

## Prerequisites
- AI-PLATFORM-FOUNDATION-PLAN Phase 1 control plane operational
- `GPT_OSS_ENDPOINT` reachable

## Allowed Scope
- Implement model discovery client in `tools/ai/control_plane/model_discovery.py`
- Implement capability probe in `tools/ai/control_plane/capability_probe.py`
- Implement role-based router in `tools/ai/control_plane/model_router.py`
- Define role configurations (minimum capability, preferred model, fallback order)
- Create model benchmark tests
- Store discovery results in `.local/ai/model-registry/`

## Forbidden Scope
- No hardcoded model names in any tool outside configuration
- No product source changes
- No gate approval
- No vector database creation

## Gates
1. Model discovery successfully enumerates models from endpoint
2. Capability probe verifies chat, embedding, and function-calling support
3. Role-based router selects correct model for each defined role
4. Fail-closed behavior verified (role unavailable → pipeline stops)
5. Fallback model selection logged in telemetry
6. Model fingerprint captured in every call record

## Evidence Requirements
- Discovery output samples
- Capability probe results
- Routing decision logs for each role
- Fail-closed test results
- Benchmark comparison (if multiple models discovered)

## Validation Requirements
- Tests in `tests/ai/test_model_discovery.py` pass
- No hardcoded model names in tools/

## Closeout Criteria
- All defined roles have at least one qualified model
- Fail-closed behavior verified for all roles
- Model fingerprinting operational

## Next Transition
On closeout: Routing available for AI-GPT-OSS-SYNTHESIS-CONTROLS and AI-AGENTIC-QWEN2-CONTROLS.
