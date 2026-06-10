# Plan Review Response — PLAN_NEEDS_REPAIR Verdict

**Sprint:** FORMAT-FACTORY-ACCELERATION-PRODUCT-FIRST-AI-LLM-EMBEDDING-EXECUTION-001
**Repair Verdict Target:** ACCELERATION_PLAN_REPAIRED_EXTERNAL_TOOL_READY
**Date:** 2026-06-04

---

## What the Reviewer Found

The v3 plan (owl model / cognitive operating layer) was structurally sound but lacked explicit
modeling of three external tools that were referenced in the broader Format Factory architecture:

1. **Ruflo** — LLM-native orchestration with memory, RAG, and plugin runtime
2. **Superpowers Marketplace** — community AI agent skill/plugin marketplace
3. **GhidraMCP** — binary analysis MCP server backed by NSA Ghidra tool

The v3 plan did not:
- Define how these tools relate to the Format Factory authority model
- Establish governance gates before any activation
- Specify which stream owns each tool
- Document what happens if a tool produces output that conflicts with poc-targets.yaml

**Reviewer verdict:** PLAN_NEEDS_REPAIR — add external tool intelligence lane before execution

---

## What Was Added (Repair Scope)

### Lane X — External Tool Intelligence Intake (Gate 5.5)

7 new taskcards: TC-EXT-001 through TC-EXT-007

| Taskcard | Deliverable |
|----------|-------------|
| TC-EXT-001 | External tool intake model + plan repair docs |
| TC-EXT-002 | Ruflo 5-mode consumption boundary |
| TC-EXT-003 | Superpowers Skills normalization path |
| TC-EXT-004 | GhidraMCP 9-condition activation gate |
| TC-EXT-005 | Risk register (3 entries, JSON Schema validated) |
| TC-EXT-006 | Mainstream packet external_tool_context field |
| TC-EXT-007 | No-installation verification (MANDATORY at Gate 7) |

### New Report Files (9 plan repair docs)

1. `00-review-response.md` (this file)
2. `gap-analysis.md`
3. `external-tool-intake-model.md`
4. `ghidra-mcp-gate.md`
5. `ruflo-consumption-boundary.md`
6. `superpowers-consumption-boundary.md`
7. `tool-risk-register-schema.json`
8. `final-single-go-execution-prompt.md`
9. `final-adversarial-independent-verification.md`

### No Changes to Authority Files

- `poc-targets.yaml`: NOT modified
- `src/net/`, `src/python/`: NOT modified
- `skill-registry.yaml`: NOT modified
- `plans/master-plan.md`: NOT modified

---

## Repair Verdict Assessment

All conditions for ACCELERATION_PLAN_REPAIRED_EXTERNAL_TOOL_READY:
- [x] External tool intake model present (TC-EXT-001)
- [x] All 3 tool boundary documents present (TC-EXT-002..004)
- [x] Risk register with 3 entries present (TC-EXT-005)
- [ ] All 4 Mainstream packets have external_tool_context (TC-EXT-006 — Gate 7)
- [ ] Authority validation confirms no tool installed (TC-EXT-007 — Gate 7)

The plan repair is structurally complete. Final verdict is confirmed at Gate 7 closeout
when TC-EXT-007 marks all invariants VERIFIED.

---

*authority_state: ai_draft | non_authoritative: true*
