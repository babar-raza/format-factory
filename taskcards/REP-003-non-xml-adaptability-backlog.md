---
taskcard_id: REP-003
title: Non-XML Adaptability Architecture
status: proposed_pending_human_approval
created: 2026-05-08
sprint: memory-sprint-format-understanding-llm-strategy
visibility: internal
relationship_to_main_sprint: deferred — do not execute before completing FODS/FODT product source
relationship_to_product_source: prerequisite for any non-XML format source
---

# REP-003 — Non-XML Adaptability Architecture

## Purpose

Design the architectural adaptations needed to support non-XML formats (ZIP containers, binary
records, compound documents) through the existing 11-gate pipeline. The current pipeline was
validated on XML-type formats. This taskcard identifies what changes are needed for other
representation categories.

## Scope

- Audit pipeline gates 1-11 for XML-only assumptions
- Define adaptation points for each representation category
- Define which infrastructure can be reused vs. what needs new work
- Create adaptation guide: docs/non-xml-pipeline-adaptation.md
- Update evidence contracts to support non-XML bundles (if changes needed)
- Define ZIP extraction layer design (for zip_container)
- Define binary reader layer design (for binary_records and compound_document)

## Blocked On

- REP-001 approved (representation schema must exist)
- At least one non-XML format identified as acquisition candidate (NAC-002)

## Out of Scope

- Implementing any non-XML parsers — that is REP-004 (ZIP) and REP-005 (binary)
- Any src/ product source

## Acceptance Criteria

1. All pipeline gates audited for XML assumptions.
2. Adaptation guide written for each representation category.
3. Infrastructure reuse vs. new work classified.
4. DEC-034 PASS.
5. Human approval.

## Future Trigger

Human authorizes REP-003 when a non-XML format is ready for pipeline entry.

## Status

proposed_pending_human_approval — deferred until XML pipeline is further validated.
