# External Tool Architecture

**Added:** 2026-06-04
**Authority:** plans/master-plan.md Section 100 + local-memory-sync sprint 2026-06-04

## Overview

Three external tools are relevant to Format Factory: Ruflo, Superpowers Marketplace, and GhidraMCP. Each has a defined placement, role, and governance constraint. None is authority.

---

## Tool 1: Ruflo

**Placement:** Primary: Supervisor + Mainstream. Secondary: Acceleration (learning/telemetry only, if Supervisor-approved).

**Role:**
- Runtime orchestration
- Swarm coordination
- Lane worker management
- Continuation loop helper
- Memory/learning helper (if approved)

**NOT authority:**
- Cannot close taskcards
- Cannot approve readiness
- Cannot override Supervisor
- Cannot bypass evidence
- Cannot push/commit/publish

**Modes:**

| Mode | Meaning |
|---|---|
| ABSENT | Ruflo not installed or not detected |
| AUDIT_ONLY | Ruflo present, read-only observation |
| PLUGIN_LITE | Ruflo present with limited plugin access |
| FULL_LOOP_PENDING_APPROVAL | Full loop capable but awaiting Supervisor approval |
| FULL_LOOP_APPROVED | Full loop authorized by Supervisor |
| DISABLED_DUE_RISK | Disabled by Supervisor due to risk detection |

**Full loop approval requirement:**
Full loop requires Supervisor approval because it may involve hooks, daemon, MCP server, memory paths, and workspace mutation. Supervisor must explicitly set `ruflo_mode: FULL_LOOP_APPROVED` in runtime governance.

**Fallback:**
If Ruflo is absent or unapproved, Mainstream must use local coordinator (sequential lane execution). Do not stop for Ruflo absence.

---

## Tool 2: Superpowers Marketplace

**Placement:** Primary: Skills / Governed Execution.

**Role:**
- External skill-pattern library (brainstorming/planning/execution patterns)
- Claude Code workflow examples
- Possible local skill wrappers after normalization

**NOT authority:**
- No blind plugin install
- No direct registry import
- No SessionStart or context injection until reviewed
- No skill usage without local normalization

**Required normalization steps before any Superpowers skill is used:**
1. Review skill for scope and risk
2. Define allowed files / forbidden files
3. Define validation command
4. Define transcript schema
5. Define rollback plan
6. Define evidence rules
7. Define activation gate
8. Register in `.supervisor/skill-registry.yaml` with `superpowers_origin: true`
9. Supervisor must approve activation gate before first use

**Hard prohibition:**
Do not install Superpowers plugins into Claude Code without explicit Supervisor approval and human authorization.

---

## Tool 3: GhidraMCP

**Placement:** Optional specialist tool under Acceleration. Governed by Supervisor. Skills may define a gated wrapper only if approved.

**Default:** DISABLED_BY_DEFAULT

**Allowed only for:**
- Authorized binaries/samples with documented ownership/license basis
- Input hash declared before analysis
- Compliance note attached (who authorized, why)
- No proprietary reverse engineering unless explicitly authorized by owner
- No decompiled code copied into product source
- All output remains ai_draft
- No capability matrix update from Ghidra output alone — requires test confirmation

**Activation gate:**
GhidraMCP is DISABLED_BY_DEFAULT. To enable:
1. Human authorization required (explicit, not inferred)
2. Supervisor must approve the specific binary/use case
3. Compliance note must be written to `.local/evidences/ghidra/` before analysis
4. Output must be labeled `ghidra_ai_draft: true`

**Hard prohibition:**
Do not install GhidraMCP via MCP server without human authorization. Do not modify `.vscode/mcp.json` to add GhidraMCP without explicit user instruction.

---

## Risk Register

| Tool | Risk Level | Default Mode | Approval Required |
|---|---|---|---|
| Ruflo ABSENT | LOW | n/a — fallback to local coordinator | None |
| Ruflo AUDIT_ONLY | LOW | acceptable default | None |
| Ruflo PLUGIN_LITE | MEDIUM | requires Supervisor review | Supervisor |
| Ruflo FULL_LOOP | HIGH | PENDING_APPROVAL | Supervisor + human |
| Superpowers (read/brainstorm) | LOW | acceptable for ideation | None |
| Superpowers (plugin install) | HIGH | DISABLED | Supervisor + human |
| GhidraMCP (any use) | HIGH | DISABLED_BY_DEFAULT | Human + Supervisor |

---

## Detection and Reporting

The Supervisor must detect and report external tool mode at sprint start:
- Ruflo: detect from `.supervisor/` runtime state or absence
- Superpowers: detect from skill-registry entries with `superpowers_origin: true`
- GhidraMCP: detect from `.vscode/mcp.json` or `.local/evidences/ghidra/` presence

Mode is reported in `reports/supervisor/session-resume.md` under `external_tool_modes`.
