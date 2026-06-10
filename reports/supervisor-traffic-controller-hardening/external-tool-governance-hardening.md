# External Tool Governance Hardening — Lane F

## Sprint
`FORMAT-FACTORY-SUPERVISOR-TRAFFIC-CONTROLLER-HARDENING-IV-001`

## Purpose
Verify external tool governance: read-only detection, no invocations, correct routing verdicts,
AI output authority limits, and deterministic supervisor retains authority in all scenarios.

## Confirmed External Tool State

| Tool | Status | MCP Registered | State Dir | Invoked | Verdict |
|------|--------|---------------|-----------|---------|---------|
| claude-flow (Ruflo) | DETECTED_NOT_CONFIGURED | YES | NO | NO | APPROVAL_REQUIRED |
| task-master-ai | DETECTED_NOT_CONFIGURED | YES | NO | NO | APPROVAL_REQUIRED |
| Superpowers | ABSENT | NO | NO | NO | EVALUATE_ONLY |
| GhidraMCP | ABSENT | NO | NO | NO | DISABLED_DEFAULT |

## Read-Only Detection Proof

The `detect_external_tools()` function performs read-only operations only:
1. Reads `.vscode/mcp.json` — file read, no mutations
2. Checks `.claude-flow/` directory existence — filesystem check, no mutations
3. Checks `.claude-plugin/` directory existence — filesystem check, no mutations
4. No npm/npx commands executed
5. No daemon processes started
6. No MCP servers activated

**Files read during detection:** `.vscode/mcp.json` only
**Files mutated:** NONE
**Processes started:** NONE

Verdict: **READ_ONLY_DETECTION_CONFIRMED**

## npx -y Auto-Install Risk

`claude-flow` is registered as:
```json
{"type":"stdio","command":"npx","args":["-y","claude-flow@3.10.14","mcp","start"]}
```

The `-y` flag auto-installs the package if not present. This is an **activation risk** because:
- Invocation would install `claude-flow@3.10.14` to the npm cache
- The MCP server would start and could access workspace files
- `.claude-flow/` state directory would be created

**Mitigation:** Supervisor governance rule prevents invocation without explicit approval.
**Status in this sprint:** Not invoked. Auto-install risk documented, not triggered.

## AI Output Authority Boundaries

### Rule
`validate_external_tool_output_authority(output: dict) -> bool`
- Returns `False` if `output.get("closes_taskcard")` is True
- Returns `False` if `output.get("approves_continuation")` is True
- Returns `True` only if output makes no authority claims

### Fixtures verified
1. `{"closes_taskcard": True}` → `False` (BLOCKED)
2. `{"closes_taskcard": False}` → `True` (allowed)
3. `{"approves_continuation": True}` → `False` (BLOCKED)
4. No output from absent tool → no authority, `LOCAL_COORDINATOR_ACTIVE`

## Routing Impact of External Tool Absence

When all external tools are absent or inactive:
- Routing is handled by local coordinator (deterministic Python tools)
- No routing gaps — all 13 blocker routes remain accessible
- `overall_verdict: EXTERNAL_TOOLS_GOVERNED_LOCAL_COORDINATOR_ACTIVE`
- `continuation_impact: none`

**Verified:** Routing determinism test ran with no external tools active.
Same input → same output. `routing_deterministic: true`

## Superpowers Governance

Status: ABSENT
`.claude-plugin/` directory: NOT FOUND
`SessionStart` injection: NOT DETECTED
Skill-registry conflicts: NOT POSSIBLE (plugin not installed)

Verdict: `SUPERPOWERS_NOT_INSTALLED_EVALUATE_ONLY`

If Superpowers were to be installed in future:
- Require path impact analysis before activation
- Confirm no `SessionStart` injection conflicts with supervisor hooks
- Verify no skill-registry.yaml conflicts
- Human approval required

## GhidraMCP Governance

Status: ABSENT / DISABLED_DEFAULT
Not referenced in `.vscode/mcp.json`
No Ghidra-related processes or files detected

Verdict: `GHIDRA_MCP_DISABLED_DEFAULT`

If GhidraMCP were to be enabled in future:
- Authorized binary required with SHA verification
- All decompiled code must be kept out of source tree
- No capability matrix updates from reverse engineering alone
- Human approval required

## Deterministic Supervisor Authority

In all 7 fixture scenarios:
- `deterministic_supervisor_retains_authority: true`
- No external tool output used as authoritative decision
- All continuation decisions made by deterministic Python tools
- AI advisory outputs marked `non_authoritative: true, authority_state: ai_draft`

**Lane F Verdict: EXTERNAL_TOOL_GOVERNANCE_HARDENED — LOCAL_COORDINATOR_ACTIVE**
