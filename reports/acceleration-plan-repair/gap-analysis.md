# Gap Analysis — External Tool Modeling

**Sprint:** FORMAT-FACTORY-ACCELERATION-PRODUCT-FIRST-AI-LLM-EMBEDDING-EXECUTION-001
**Date:** 2026-06-04
**authority_state:** ai_draft

---

## What v3 Had vs. What v3 Was Missing vs. What Was Added (v4)

| # | Gap Area | v3 Status | Missing Element | v4 Addition |
|---|----------|-----------|----------------|-------------|
| 1 | Ruflo authority boundary | Not defined | Which stream owns Ruflo; what modes are allowed | Lane X TC-EXT-002: 5-mode boundary doc |
| 2 | Ruflo packet context | Not present | How Mainstream packets signal Ruflo availability | TC-EXT-006: ruflo_context field in all packets |
| 3 | Superpowers governance | Not defined | Skills normalization path; who installs what | TC-EXT-003: Skills ownership doc |
| 4 | Superpowers recommendations | Not present | Advisory skill recommendations for Skills stream | superpowers-recommendations-for-skills.json |
| 5 | GhidraMCP gate | Not defined | 9-condition activation gate | TC-EXT-004: ghidra-mcp-gate.md |
| 6 | External tool risk register | Not present | Structured risk assessment per tool | TC-EXT-005: external-tool-risk-register.json + schema |
| 7 | No-installation proof | Not defined | Verification that no tool was installed | TC-EXT-007: mandatory verification at Gate 7 |
| 8 | External tool authority boundary | Not present | May/may-not table; 12-state lifecycle | external-tool-authority-boundary.md |
| 9 | Repaired IV questions | 14 questions | 5 new external-tool-specific IV questions | 19-question IV (this repair) |
| 10 | External tool validation file | Not present | JSON tracking invariants | external-tool-authority-validation.json |
| 11 | Stream ownership clarity | Implicit only | Explicit: Ruflo=Supervisor, Superpowers=Skills, GhidraMCP=Acceleration(gate only) | Authority boundary table |
| 12 | Mainstream packet schema | Basic fields | Missing external_tool_context schema | TC-EXT-006: external_tool_context field |
| 13 | Risk register schema | Not present | JSON Schema for consistent risk register format | tool-risk-register-schema.json |
| 14 | Coordinator taskcard | Implied | TC-EXT-007 as mandatory gate at closeout | Explicit mandatory gate |
| 15 | Repaired execution prompt | Not self-contained | Plan repair docs not self-referential | final-single-go-execution-prompt.md |

---

## Summary

v3 established the owl model (AI as cognitive operating layer) correctly but did not model
the external tools that the broader Format Factory architecture references. This created a gap
where a future sprint might install or activate Ruflo/Superpowers/GhidraMCP without clear
governance.

v4 closes this gap by:
1. Defining ownership (which stream controls each tool)
2. Defining modes (what states each tool can be in)
3. Defining gates (what conditions must be met before activation)
4. Documenting risks (structured risk register)
5. Adding mandatory verification (TC-EXT-007 cannot be skipped)

All v3 AI cognitive layer work (owl model, 8 tools, 4 Mainstream packets) is preserved.
The gap additions are purely additive.

---

*authority_state: ai_draft | non_authoritative: true*
