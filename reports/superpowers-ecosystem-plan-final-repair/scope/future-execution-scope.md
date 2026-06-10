# Future Execution Sprint Scope
Sprint: FORMAT-FACTORY-SUPERPOWERS-AGENTIC-AUTONOMY-EXECUTION-001 (to be executed after this plan sprint)

## Backend Architecture to Build
- tools/supervisor/next_action_schema.py
- tools/supervisor/next_action_runner.py
- tools/supervisor/execution_backend.py (base class)
- tools/supervisor/backend_selector.py
- tools/supervisor/backends/__init__.py
- tools/supervisor/backends/mcp_superpowers_backend.py
- tools/supervisor/backends/llm_api_backend.py
- tools/supervisor/backends/local_deterministic_backend.py
- tools/supervisor/backends/session_skill_tool_backend.py
- tools/supervisor/backends/claude_agent_subagent_backend.py
- tools/supervisor/autonomous_host_daemon.py
- scripts/format_factory_autonomous_host.sh (or .ps1)

## Proofs Required
- H3: runner executed one action (minimum required)
- H4: two sequential runner cycles
- H5: agentic backend via runner (SESSION_SKILL_TOOL or CLAUDE_AGENT_SUBAGENT)
- H6: external host continuation (only if CLAUDECODE=0)

## Tools to Install (each with governance gate)
- cognee (pip install cognee) — SETUP_REQUIRED_BUT_NOT_THIS_SPRINT
- openspec (npm install -g openspec) — SETUP_REQUIRED_BUT_NOT_THIS_SPRINT
- skill_seekers — SETUP_REQUIRED_BUT_NOT_THIS_SPRINT
- Superpowers plugin — AGENT_CAN_PREPARE_ONLY (governance intake required before install)

## Tests to Create
- tests/supervisor/test_execution_backends.py
- tests/supervisor/test_backend_selector.py
- tests/supervisor/test_two_cycle_proof.py
