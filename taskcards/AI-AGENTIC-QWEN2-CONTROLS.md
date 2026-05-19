# Taskcard: AI-AGENTIC-QWEN2-CONTROLS

## Objective
Implement Qwen2 agentic controls: role contracts, path/operation allowlists, state-machine guard, scope monitor, output validation, rollback, and DEC-034 integration for authority-affecting outputs.

## Status
`implemented_blocked_no_model` — scoped_runner.py with AgenticTaskContract, FORBIDDEN_OPERATIONS, path/operation allowlists, and model validation implemented in R27 (cb7e05c). Blocked on Qwen2 model availability. 9 tests pass.

## Prerequisites
- AI-MODEL-DISCOVERY-AND-ROUTING operational (Qwen2 discovered and routable)
- AI-PLATFORM-FOUNDATION-PLAN task contracts defined

## Allowed Scope
- Implement `tools/ai/agentic/agent_runner.py` with scope enforcement
- Implement `tools/ai/agentic/task_state_machine.py`
- Implement `tools/ai/agentic/scope_guard.py`
- Implement `tools/ai/agentic/rollback.py`
- Define Qwen2-specific role contracts in `tools/ai/contracts/`
- Create tests in `tests/ai/test_agentic_qwen2.py`

## Forbidden Scope
- No high-risk agentic tasks via Qwen2
- No direct repo mutations from Qwen2
- No product source changes
- No gate approval delegation

## Gates
1. Qwen2 routed only to `agentic_low_risk` role
2. Path allowlist enforcement verified (out-of-scope access blocked)
3. Operation allowlist enforcement verified
4. State machine transitions enforced
5. Scope violation triggers immediate stop
6. Output tagged as `ai_draft` in authority lifecycle
7. DEC-034 IV required for authority-affecting outputs

## Evidence Requirements
- Scope violation test results
- State machine transition logs
- Qwen2 output authority state verification
- Telemetry records with Qwen2-specific fields

## Validation Requirements
- `tests/ai/test_agentic_qwen2.py` passes
- Scope guard rejects out-of-scope access

## Closeout Criteria
- Qwen2 agentic runner operational with all controls
- At least one low-risk task completed through full lifecycle

## Next Transition
On closeout: Qwen2 available for low-risk agentic tasks in acquisition pipeline.
