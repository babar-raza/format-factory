---
taskcard_id: REP-001
title: Format Representation Profile — Schema and Design
status: proposed_pending_human_approval
created: 2026-05-08
sprint: memory-sprint-format-understanding-llm-strategy
visibility: internal
relationship_to_main_sprint: backlog — not a MAIN SPRINT gate
relationship_to_product_source: prerequisite for non-XML format source; not needed for current XML formats
---

# REP-001 — Format Representation Profile Schema and Design

## Purpose

Define the format representation profile schema that captures each format's physical representation
category. This schema enables future non-XML format acquisition to use a consistent representation
model and avoids XML-only hardcoding in pipeline infrastructure.

## Scope

- Extend FUL-001 format-profile.yaml schema with representation fields (physical_representation, container_model, etc.)
- Define allowed values for physical_representation (text_xml, zip_container, binary_records, etc.)
- Define per-representation parser strategy stubs (for future adaptation)
- Document how each representation category affects: oracle strategy, fuzz surface, sample creation
- Update docs/format-representation-model.md with schema references

## Blocked On

- FUL-001 approved (representation fields are part of format-profile schema)

## Out of Scope

- Implementing non-XML parsers — that is REP-003/4/5
- Embedding or LLM work

## Acceptance Criteria

1. Representation profile schema defined and consistent with FUL-001 format-profile schema.
2. All representation categories documented with per-category pipeline adaptations.
3. FODS and FODT profiles demonstrate text_xml category correctly.
4. DEC-034 PASS.
5. Human approval.

## Future Trigger

Human authorizes REP-001 after FUL-001 design approved.

## Status

proposed_pending_human_approval
