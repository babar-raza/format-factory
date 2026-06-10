# External Tool Architecture Sync Report
# Sprint: FORMAT-FACTORY-LOCAL-MEMORY-PRODUCT-FIRST-AI-EXTERNAL-TOOLS-SYNC-001
# Date: 2026-06-04

## Status: CLOSED_VERIFIED

## Files Created
- docs/governance/external-tool-architecture.md (NEW)
- docs/governance/ruflo-runtime-governance.md (NEW)
- docs/governance/superpowers-skill-intake.md (NEW)
- docs/governance/ghidra-mcp-compliance-gate.md (NEW)

## Summary

### Ruflo
- Placement: Supervisor + Mainstream (primary), Acceleration (secondary, if approved)
- Modes: ABSENT | AUDIT_ONLY | PLUGIN_LITE | FULL_LOOP_PENDING_APPROVAL | FULL_LOOP_APPROVED | DISABLED_DUE_RISK
- Full loop requires Supervisor + human approval (hooks, daemon, MCP server risk)
- Current mode: ABSENT (not installed)
- Fallback: local sequential coordinator when absent

### Superpowers
- Placement: Skills / Governed Execution stream
- No blind install; normalization required before any skill use
- 5-step intake: review → risk classify → local wrapper → registry entry → activation gate
- Risk LOW→MEDIUM: Supervisor approval; HIGH: Supervisor + human; CRITICAL: not permitted

### GhidraMCP
- Default: DISABLED_BY_DEFAULT
- Requires: ownership basis, input hash, compliance note, human authorization, Supervisor approval
- No decompiled code in product source; all output ai_draft
- No capability matrix update from Ghidra output alone

## Current External Tool Modes (2026-06-04)
| Tool | Mode |
|---|---|
| Ruflo | ABSENT |
| Superpowers | NORMALIZED_SKILLS_ONLY (see skill-registry.yaml) |
| GhidraMCP | DISABLED_BY_DEFAULT |
