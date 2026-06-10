# External Tool Intelligence Intake
# Sprint: FORMAT-FACTORY-ACCELERATION-PRODUCT-FIRST-AI-LLM-EMBEDDING-EXECUTION-001
# authority_state: ai_draft | non_authoritative: true

## Summary

Three external tools have been evaluated as potential ai_draft accelerators for Format Factory streams.
No tool was installed. No tool was invoked. No binary analysis was performed.

| Tool | Owner Stream | Default Status | Installation Required |
|------|-------------|---------------|----------------------|
| Ruflo | Supervisor/Mainstream | disabled | No (Acceleration must not install) |
| Superpowers Marketplace | Skills | audit_only | No (Skills stream only) |
| GhidraMCP | Acceleration (gated) | disabled_pending_supervisor_approval | No |

## Ruflo

Ruflo (https://github.com/ruvnet/ruflo/) is an LLM-native runtime with memory, RAG, and plugin
orchestration. Acceleration may consume Ruflo telemetry signals if Supervisor approves a mode
above `absent`. Ruflo does not become product authority.

**This sprint status:** absent. No consumption.

## Superpowers Marketplace

Superpowers Marketplace (https://github.com/obra/superpowers-marketplace) provides community
AI agent skills. Acceleration's role is recommendation only. Skills stream owns normalization
and registry entry. Acceleration recommendations are in `superpowers-recommendations-for-skills.json`.

**This sprint status:** audit_only. No plugins installed.

## GhidraMCP

GhidraMCP (https://github.com/LaurieWired/GhidraMCP) is a binary analysis MCP server backed by Ghidra.
DISABLED_BY_DEFAULT. Gate document written. Not installed. Not invoked. No binary analyzed.

**This sprint status:** disabled. Gate document only.

## Verification Proof

- ruflo: ABSENT (python importlib.util.find_spec returns None)
- Superpowers commands: NONE found in .claude/commands/
- GhidraMCP: NO_MCP_CONFIG (no .mcp.json present)
