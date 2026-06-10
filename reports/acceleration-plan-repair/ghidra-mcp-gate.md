# GhidraMCP Activation Gate

**Sprint:** FORMAT-FACTORY-ACCELERATION-PRODUCT-FIRST-AI-LLM-EMBEDDING-EXECUTION-001
**Date:** 2026-06-04
**authority_state:** ai_draft
**Status this sprint:** DISABLED — DO NOT RUN

---

## What GhidraMCP Is

GhidraMCP (https://github.com/LaurieWired/GhidraMCP) is an MCP server backed by Ghidra,
the NSA reverse engineering tool. It exposes Ghidra's decompilation, symbol analysis, and
binary inspection capabilities over the MCP protocol.

Capabilities include:
- Binary function listing and decompilation
- Symbol and cross-reference analysis
- Data type and structure extraction
- Assembly-level code inspection

**Default Status:** `disabled_pending_supervisor_approval`

---

## For This Sprint

**DO NOT:**
- Install Ghidra
- Install GhidraMCP
- Run Ghidra
- Analyze any binary file
- Add GhidraMCP to `.mcp.json`
- Produce any output from binary analysis

This sprint only writes this gate document and a risk register entry.
GhidraMCP activation requires Supervisor approval first.

---

## 9-Condition Activation Gate

GhidraMCP may ONLY be activated when ALL of the following conditions are met:

| # | Condition | Verification |
|---|-----------|-------------|
| 1 | Supervisor writes approval in `.supervisor/policies.yaml` | Check file for explicit GhidraMCP approval entry |
| 2 | Input binary is owned, open-source, test-fixture, or explicitly authorized in writing | Authorization record in `ghidra-mcp-authorization-record.json` |
| 3 | License/ownership basis is recorded before analysis begins | File exists with legal basis |
| 4 | Input SHA-256 is recorded before analysis | Hash in `ghidra-mcp-input-hashes.json` before any run |
| 5 | No proprietary third-party binary analyzed without explicit authorization | Checked per-binary, not per-sprint |
| 6 | All output is labeled `authority_state: ai_draft` | Enforced in analysis output schema |
| 7 | No capability matrix update made from reverse-engineering output alone | Test evidence required for any matrix change |
| 8 | No generated code copied from decompiled proprietary code | Human reviewer checks before any code inclusion |
| 9 | Results used only for understanding format behavior or fixture structure | Scope limited to format reverse engineering |

**All 9 must be true.** Partial compliance does not permit activation.

---

## Required Outputs IF GhidraMCP Is Ever Activated

These files must be created before analysis begins:
```
reports/acceleration-product-first/ghidra-mcp-authorization-record.json
reports/acceleration-product-first/ghidra-mcp-input-hashes.json
```

These files are created after analysis:
```
reports/acceleration-product-first/ghidra-mcp-analysis-summary.md
reports/acceleration-product-first/ghidra-mcp-risk-review.md
```

---

## Risk Summary

| Risk | Level | Mitigation |
|------|-------|-----------|
| Proprietary binary analysis without authorization | Critical | Condition 2+3 in gate |
| Decompiled code copied to product source | Critical | Condition 8 in gate |
| RE output treated as authoritative format spec | High | Condition 7 in gate |
| Capability matrix updated from RE alone | High | Test evidence required |
| License contamination | High | Legal review per binary |

---

## Rollback

If GhidraMCP is accidentally activated:
1. Remove GhidraMCP entry from `.mcp.json`
2. Delete any ghidra-mcp-analysis-summary.md and related outputs
3. Verify no capability matrix was updated from RE output
4. Verify no decompiled code was added to src/
5. Report incident to Supervisor for policies.yaml review

---

*authority_state: ai_draft | non_authoritative: true*
