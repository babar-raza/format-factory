---
taskcard_id: FORMAT-EXPANSION-ROADMAP
title: "Format Expansion Roadmap — Governance and Tracking"
type: governance_roadmap
sprint: FORMAT-FACTORY-ROADMAP-MEMORY-SYNC-001
created_at: "2026-05-14"
status: active
visibility: internal
publish_allowed: false
authority: plans/master-plan.md Section 38
---

# Taskcard: FORMAT-EXPANSION-ROADMAP

## Purpose

This taskcard governs the format expansion roadmap for Format Factory.
It tracks the strategic direction, milestone status, and governance of format expansion beyond FODS/FODT.

---

## Strategic Phases

### Phase 1 — XML-Based Proof (CURRENT)
**Status:** IN PROGRESS

Complete the XML-based proof system on FODS/FODT.
Complete Conway orchestration infrastructure (R1–R9).
Do NOT add new formats until Conway R9 is proven.

**Blockers:**
- Conway R1 (schemas) → R2 (context resolver) → R3 (lane library) → R4 (prompt generator + quality gate) → R5 (evidence contract template) → R6 (commands) → R7 (dry-runs) → R8 (IV) → R9 (first new format)
- Gate 11 for FODS and FODT (both NOT APPROVED, C4-C6-vertical-slice)

### Phase 2 — Public-Spec XML/Package Expansion (SHORT-TERM)
**Status:** PENDING — blocked on Conway R9

Add Tier A candidates from `docs/python-foss/format-expansion-roadmap.md`.
Prefer formats with public specifications and open test material.
Every format must pass all 11 gates with human approval.

### Phase 3 — Beyond-Aspose Format Universe (LONG-TERM)
**Status:** BACKLOG

Expand to any format family with sufficient public technical information.
Not limited to Aspose-supported formats.

---

## Governance Checkpoints

| Checkpoint | Requirement | Status |
|-----------|-------------|--------|
| Roadmap synced to repo | docs/python-foss/format-expansion-roadmap.md created | DONE |
| Memory file created | memory/26-... created | DONE |
| Master plan Section 38 | plans/master-plan.md Section 38 | DONE |
| Bootstrap updated | docs/automation/fresh-chat-project-bootstrap.md/.yaml | DONE |
| Conway R9 complete | First new format rollout proven | NOT STARTED |
| Tier A support-matrix audit | All Tier A candidates audited against Aspose | NOT STARTED |
| First new format Gates 1-11 | Human-approved gate progression | NOT STARTED |

---

## Related Taskcards

| Taskcard | Topic |
|----------|-------|
| NON-ASPOSE-FORMAT-BACKLOG.md | Full candidate backlog governance |
| PUBLIC-SPEC-FORMAT-EXPANSION.md | Public-spec format expansion |
| NAC-001-non-aspose-format-candidate-registry.md | Registry plan (existing) |
| REP-003-non-xml-adaptability-backlog.md | Non-XML adaptability (existing) |

---

## Key Files

| File | Purpose |
|------|---------|
| docs/python-foss/format-expansion-roadmap.md | Full human-readable roadmap |
| docs/python-foss/format-expansion-roadmap.yaml | Machine-readable roadmap |
| memory/26-format-expansion-roadmap-and-non-aspose-backlog-20260514.md | Memory file |
| plans/master-plan.md Section 38 | Authority section |

---

## Non-Negotiable Rules

1. No new format before Conway R9 complete.
2. No gate self-approval — all 11 gates require human approval.
3. Support-matrix audit before any acquisition planning.
4. Public-spec availability recorded before implementation.
5. Legal classification required for proprietary/reverse-engineered formats.
6. AI assists, not decides.
7. Speed required, but not at the expense of governance.
