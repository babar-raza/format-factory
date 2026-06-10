# Next Action Generation Policy
Sprint: FORMAT-FACTORY-AUTONOMOUS-ORCHESTRATOR-PERSISTENT-CONTINUATION-001

## Policy

next_action_generator.py generates the next safe executable action for the autonomy loop.

Rules:
1. Never generate GIT_PUSH, GIT_COMMIT, GATE_8/11_APPROVAL, PACKAGE_PUBLISH, MCP_ACTIVATE
2. Never generate product work unless stream explicitly switches
3. Never convert advisory Markdown to executable action
4. Always set preferred_backend=LOCAL_DETERMINISTIC unless backend override specified
5. Always set external_gate=false on generated actions
6. Rotate action types deterministically: RUN_JSON_VALIDATION → RUN_YAML_VALIDATION → RUN_COMMAND_DISCOVERY → GENERATE_EVIDENCE_STUB → RUN_MD_NONEMPTY_CHECK

## Stop Condition

Generator returns None when:
- action_type would be forbidden
- No valid target file exists for the action type
- cycle_index overflow (never occurs in practice; rotation wraps)
