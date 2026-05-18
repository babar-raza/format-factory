# Taskcard: AI-PLATFORM-FOUNDATION-PLAN

## Objective
Implement the Phase 1 AI platform control plane foundation: model discovery, role-based routing, task contracts, prompt registry, schema registry, telemetry (local JSONL spool), and runtime guard.

## Status
`plan_hardened` — Implementation not yet authorized. Plan must be reviewed and accepted first.

## Prerequisites
- AI platform plan reviewed and accepted by human authority
- `GPT_OSS_API_KEY` and `GPT_OSS_ENDPOINT` environment variables available
- `.venv` with LiteLLM and Pydantic v2 installed

## Allowed Scope
- Create `tools/ai/control_plane/` modules (model_discovery.py, model_router.py, capability_probe.py, task_contract.py, prompt_registry.py, schema_registry.py)
- Create `tools/ai/telemetry/` modules (call_logger.py, spool_manager.py)
- Create `tools/ai/validators/` modules (schema_validator.py, authority_lifecycle.py, runtime_guard.py)
- Create `tools/ai/contracts/`, `tools/ai/prompts/`, `tools/ai/schemas/`
- Create `.local/ai/` directory structure
- Add LiteLLM, Pydantic v2 to AI requirements file
- Create pytest tests in `tests/ai/`

## Forbidden Scope
- No product source code changes (`src/python/`, `src/net/`)
- No endpoint calls until control plane scaffolding passes tests
- No vector database creation
- No gate approval
- No publication or release changes

## Gates
1. LiteLLM installed and importable in .venv
2. Model discovery returns model list from endpoint
3. Role-based router selects correct model for each role
4. Task contract schemas defined for at least 3 roles
5. Prompt registry operational with hash tracking
6. Telemetry JSONL written for every AI call
7. Runtime guard detects forbidden imports in `src/`
8. All tests pass

## Evidence Requirements
- Evidence bundle with all created files
- Model discovery test output
- Runtime guard scan results
- Telemetry sample records
- Test results summary

## Validation Requirements
- `python -m pytest tests/ai/ -q` passes
- Runtime guard scan on `src/` returns clean
- No secrets in any committed file

## Closeout Criteria
- Phase 1 control plane operational
- At least one model discovered and routed
- Telemetry logging verified
- Runtime guard enforced

## Next Transition
On closeout: AI-GPT-OSS-SYNTHESIS-CONTROLS and AI-MODEL-DISCOVERY-AND-ROUTING become eligible for Phase 2 implementation.
