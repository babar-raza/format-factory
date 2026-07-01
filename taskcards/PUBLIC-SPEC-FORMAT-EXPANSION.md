---
taskcard_id: PUBLIC-SPEC-FORMAT-EXPANSION
title: "Public-Spec Format Expansion — Planning and Governance"
type: expansion_planning
sprint: FORMAT-FACTORY-ROADMAP-MEMORY-SYNC-001
created_at: "2026-05-14"
status: pending
visibility: internal
publish_allowed: false
authority: plans/master-plan.md Section 38
---

# Taskcard: PUBLIC-SPEC-FORMAT-EXPANSION

## Purpose

This taskcard governs the expansion of Format Factory to formats with publicly available
specifications or sufficient public technical information. It defines the selection criteria,
expansion process, and governance for the first wave of post-FODS/FODT format additions.

---

## Prerequisites

**None of the work below may begin until:**

1. Conway Phase R9 is complete (first new format rollout proven).
2. The XML-based proof system is stable on FODS/FODT.
3. Explicit human authorization for expansion is given in a session prompt.

---

## Format Selection Criteria

Formats selected for public-spec expansion must meet at least one of:

| Criterion | Description |
|-----------|-------------|
| Public specification | Publicly available spec document (no NDA required) |
| Public structural knowledge | Open documentation, community-published format docs |
| Open test material | Open-license sample files freely available |
| Reverse-engineering-safe | Community reverse-engineering documentation exists |
| FOSS reference implementation | Open source parser/writer exists with permissive license |

**Legal requirement:** Every selected format must be legally classifiable before acquisition begins.
Reverse-engineered formats require explicit legal review.

---

## Expansion Process (Per Format)

For each format entering the public-spec expansion:

### Step 1: Support-Matrix Audit
- Check current Aspose support matrices (Words, Cells, Slides, Imaging, etc.)
- Record result: fully_supported / partially_supported / not_supported / unknown
- Result must be committed to `registry/format-registry.yaml` before proceeding

### Step 2: Specification / Source Audit
- Identify public spec, documentation, or open reverse-engineering sources
- Record spec URL, version, license, access method
- Download and cache locally per AGENTS.md Section T

### Step 3: Legal / Provenance Classification
- Confirm sample license: Apache-2.0 / MIT / other open / unknown / blocked
- Confirm spec license: permissive / reference-only / unknown / blocked
- Confirm reverse-engineering status: safe / restricted / unknown

### Step 4: Pilot Scoring and Gate 1
- Score format using scoring model (`registry/scoring/_scoring-model.md`)
- Submit for Gate 1 (Candidate Accepted) — human approval required
- Create acquisition-packs/{format}/ after Gate 1

### Step 5: Full 11-Gate Pipeline
Follow all gates 1-11 per the standard gate model.
Each gate requires human approval. DEC-034 IV required before human review of gates.

---

## Priority Queue (Tier A — Initial Expansion Candidates)

All marked `unsupported_by_aspose: needs_audit`.
Ordered by public-spec quality and system fit:

1. .gnumeric — Gnumeric (full public XML spec, FOSS reference impl)
2. .abw — AbiWord (full public XML spec, FOSS reference impl)
3. .qoi — Quite OK Image (minimal public spec, extremely simple)
4. .ora — OpenRaster (full public XML ZIP spec, LGPL)
5. .osm — OpenStreetMap XML (full public spec, massive community)
6. .zst — Zstandard (RFC standard, reference library)
7. .xcf — GIMP native (documented, FOSS reference impl)
8. .zpaq — ZPAQ (public spec)
9. .hwpx — Hancom Hangul XML/package (partial public — verify spec coverage)
10. .pages / .numbers / .key — Apple iWork (no public spec — community reverse-engineering only)

---

## Expansion Governance Rules

1. **Never expand without Conway R9 proven** — skill system must be functional first.
2. **Never expand without explicit human authorization** — expansion sprint requires human prompt.
3. **Every format uses the skill system** — no manual one-off sprints after R9.
4. **Every format gets its own gate progression** — no shared gates between formats.
5. **AI-generated requirements are mandatory** — no implementation without accepted requirements.
6. **Evidence bundles required at each gate** — BUNDLE_VALIDATION: PASS required.
7. **No commercial readiness claim** until Gate 11 approved by human.
8. **DEC-034 IV required** before human gate review at each gate.

---

## Skill System Integration

After Conway R9, each new format uses:
- `/commercial-sprint {format}` — generates full governed implementation prompt
- `tools/skills/format_context_resolver.py` — determines format readiness state
- `tools/skills/lane_selector.py` — selects appropriate lanes
- `tools/skills/swarm_prompt_generator.py` — generates coordinator prompt
- `tools/skills/prompt_quality_gate.py` — validates generated prompt before use
- `templates/commercial-sprint/lane-library.yaml` — lane definitions

---

## Tracking

| Format | Audit Status | Gate 1 | Active |
|--------|-------------|--------|--------|
| (all candidates) | needs_audit | NOT STARTED | NO |

This table will be updated as audits complete and expansion begins.

---

## Related Files

| File | Purpose |
|------|---------|
| docs/python-foss/format-expansion-roadmap.md | Full expansion roadmap |
| docs/python-foss/format-expansion-roadmap.yaml | Machine-readable roadmap |
| taskcards/FORMAT-EXPANSION-ROADMAP.md | Strategic governance |
| taskcards/NON-ASPOSE-FORMAT-BACKLOG.md | Full candidate backlog |
| reports/planning/conway-rebaseline-roadmap-20260513.md | Conway R1-R9 dependency |
| registry/format-registry.yaml | Format gate status |
| registry/scoring/_scoring-model.md | Scoring model |
