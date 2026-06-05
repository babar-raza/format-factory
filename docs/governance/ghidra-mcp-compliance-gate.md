# GhidraMCP Compliance Gate

**Added:** 2026-06-04
**Authority:** plans/master-plan.md Section 43 + local-memory-sync sprint 2026-06-04

## Default State

**DISABLED_BY_DEFAULT**

GhidraMCP is not active in any Format Factory stream unless all gate conditions below are met.

## Purpose

GhidraMCP allows AI-assisted binary analysis using Ghidra. This is an optional specialist tool under Acceleration, governed by Supervisor.

## When It May Be Used

GhidraMCP may only be used for:
- Authorized binaries or samples (not proprietary software without authorization)
- Format understanding research (e.g., understanding binary format structures from reference samples)
- Security/reverse engineering research with explicit authorization

## Gate Conditions (ALL must be met)

| Condition | Required Action |
|---|---|
| 1. Ownership/license basis | Document who owns the binary and the license that permits analysis |
| 2. Input hash | Compute and record SHA-256 of the input binary before analysis |
| 3. Compliance note | Write compliance note to `.local/evidences/ghidra/<hash>/compliance.md` |
| 4. Human authorization | Explicit human instruction ("use GhidraMCP on <file>") |
| 5. Supervisor approval | Supervisor must approve the specific use case |
| 6. No proprietary RE | No reverse engineering of proprietary software unless owner explicitly authorizes |

## Hard Prohibitions

- Do not install GhidraMCP via MCP server without human authorization
- Do not modify `.vscode/mcp.json` to add GhidraMCP
- Do not copy decompiled code into product source
- Do not update capability matrix from Ghidra output alone (requires test confirmation)

## Output Labeling

All GhidraMCP output must be labeled:
```yaml
ghidra_ai_draft: true
authority: non-authoritative
source: ghidra_mcp_analysis
requires_human_verification: true
```

## Result Chain

Ghidra analysis → labeled ai_draft → Acceleration-B review → if useful, create code-generation handoff (still ai_draft) → Mainstream reviews and implements → tests confirm → product credit earned

At no point does Ghidra output directly update the capability matrix or close a taskcard.

## Skills Wrapper

If a Skills wrapper for GhidraMCP is created, it must:
1. Have risk_level: HIGH in the registry
2. Have activation_gate requiring Supervisor + human authorization
3. Have explicit compliance_note_path in its allowed_paths
4. Run compliance check before any analysis
