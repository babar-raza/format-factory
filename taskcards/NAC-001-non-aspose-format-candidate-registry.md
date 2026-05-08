---
taskcard_id: NAC-001
title: Non-Aspose Format Candidate Registry — Schema and Design
status: proposed_pending_human_approval
created: 2026-05-08
sprint: memory-sprint-format-understanding-llm-strategy
visibility: internal
relationship_to_main_sprint: backlog — independent of current FODS/FODT pipeline
relationship_to_product_source: enables future acquisition candidate selection
---

# NAC-001 — Non-Aspose Format Candidate Registry Schema and Design

## Purpose

Design the schema and discovery process for `registry/non-aspose-format-candidates.yaml` —
a visible registry of file formats not common to Aspose products or underserved by current
Aspose tooling.

## Scope

- Design YAML schema for non-aspose-format-candidates.yaml (see docs/non-aspose-format-candidate-registry-plan.md)
- Define verification workflow (how to confirm Aspose overlap status)
- Define candidate evaluation criteria (complexity, product potential, spec availability)
- Create empty template registry file with 2-3 example entries clearly marked as unverified
- Write registry-level documentation (_readme.md in registry/)

## Out of Scope

- Actually populating the registry with verified candidates — that is NAC-002
- Gate 1 scoring for any candidate — requires separate scoring sprint
- LLM-assisted candidate discovery (future — requires LLM-001)

## Allowed Files

- registry/non-aspose-format-candidates.yaml (new — template only, entries marked unverified)
- registry/_readme.md (update to reference new file)
- docs/non-aspose-format-candidate-registry-plan.md (update with schema reference)

## Forbidden Files

- registry/format-registry.yaml — no gate status changes
- src/python/, src/net/

## Claim Policy

Every entry in the registry must have `verification_status` set. Unverified entries must be
clearly marked `verification_status: unverified`. Do not claim a format is not supported by
Aspose without verification evidence recorded in the entry.

## Acceptance Criteria

1. Schema defined with all required fields.
2. Verification workflow documented.
3. Template registry file created (entries marked unverified).
4. DEC-034 PASS.
5. Human approval.

## Future Trigger

Human authorizes NAC-001 when ready to begin candidate discovery program.

## Status

proposed_pending_human_approval
