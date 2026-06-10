# External Tool Intelligence Intake Model

**Sprint:** FORMAT-FACTORY-ACCELERATION-PRODUCT-FIRST-AI-LLM-EMBEDDING-EXECUTION-001
**Date:** 2026-06-04
**authority_state:** ai_draft

---

## Purpose

This document defines the complete model for how Format Factory evaluates, governs, and
optionally activates external AI tools. It covers three tools evaluated in R93+:

- **Ruflo** — LLM-native orchestration runtime
- **Superpowers Marketplace** — community AI skill registry
- **GhidraMCP** — Ghidra-backed binary analysis MCP server

No external tool was installed during this sprint. This model governs future activation.

---

## Core Principle

**External tools are cognitive accelerators, never authorities.**

They may:
- Provide advisory signals
- Recommend patterns
- Offer analysis

They may never:
- Modify poc-targets.yaml, skill-registry.yaml, or plans/master-plan.md
- Produce evidence that advances an artifact past ai_draft without test validation
- Be installed or activated without the owning stream's governance gate

---

## Tool Summaries

### Ruflo

| Property | Value |
|----------|-------|
| Purpose | LLM-native orchestration with memory, RAG, plugin runtime |
| Owning stream | Supervisor / Mainstream |
| Default mode | absent |
| Activation gate | Supervisor written approval in policies.yaml |
| Acceleration role | Advisory input only (if mode >= audit_only) |

**5 modes:** absent → audit_only → plugin_lite → full_loop_pending_approval → full_loop_approved

Acceleration may NOT install or activate Ruflo. Ruflo memory/RAG outputs are runtime_advisory,
never authoritative. poc-targets.yaml is NEVER replaced by Ruflo signal.

### Superpowers Marketplace

| Property | Value |
|----------|-------|
| Purpose | Community AI agent skill/plugin marketplace |
| Owning stream | Skills |
| Default mode | audit_only (catalog read only) |
| Activation gate | Skills normalization: wrapper → allowed/forbidden files → validation → registry |
| Acceleration role | Recommendation only — Skills stream owns all normalization and installation |

Acceleration may read the marketplace catalog and recommend skills. All skill activation
goes through the Skills normalization pipeline. Acceleration never writes to skill-registry.yaml.

### GhidraMCP

| Property | Value |
|----------|-------|
| Purpose | Binary analysis MCP server (Ghidra-backed reverse engineering) |
| Owning stream | Acceleration (specialist gate only) |
| Default mode | disabled_pending_supervisor_approval |
| Activation gate | 9-condition gate — see ghidra-mcp-gate.md |
| Acceleration role | Binary format analysis for undocumented formats (disabled this sprint) |

GhidraMCP is not installed, not activated, and not used this sprint. The gate document
(ghidra-mcp-gate.md) defines the 9 conditions that must be met before any activation.

---

## Intake Process Flow

```
External Tool Identified
        ↓
Owning Stream Identified (Supervisor / Skills / Acceleration)
        ↓
Mode Assessment (What state is it in? absent/audit_only/...)
        ↓
Risk Register Entry Created (workspace_mutation_risk, secret_risk, etc.)
        ↓
Boundary Document Written (what it may/may not do)
        ↓
Activation Gate Defined (conditions for mode elevation)
        ↓
Recommendations Written (advisory, authority_state: ai_draft)
        ↓
No-Installation Verification (TC-EXT-007)
        ↓
Ready for Future Supervisor Approval Decision
```

---

## Authority Invariants (all must hold at sprint closeout)

1. No external tool output has `authority_state` other than `ai_draft` or `runtime_advisory`
2. `poc-targets.yaml` SHA-256 unchanged from `poc_targets_checksum_before`
3. No file created under `src/net/` or `src/python/`
4. No external tool installed, activated, or added to `.mcp.json`
5. All Mainstream packets have `external_tool_activation_required_for_packet: false`
6. `external-tool-risk-register.json` has exactly 3 entries
7. `external-tool-authority-validation.json` has all invariants VERIFIED at Gate 7

---

*authority_state: ai_draft | non_authoritative: true*
