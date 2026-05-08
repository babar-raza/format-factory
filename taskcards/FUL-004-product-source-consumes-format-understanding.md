---
taskcard_id: FUL-004
title: Product Source Consumption of Compiled Format Understanding
status: proposed_pending_human_approval
created: 2026-05-08
sprint: memory-sprint-format-understanding-llm-strategy
visibility: internal
relationship_to_main_sprint: backlog — requires FUL-002 or FUL-003 and Phase 4 prompt
relationship_to_product_source: directly enables Phase 4 source development
---

# FUL-004 — Product Source Consumption of Compiled Format Understanding

## Purpose

Define and implement the process by which Phase 4 product source development is grounded in
compiled Format Understanding Layer files. Ensures that src/python/{format}/ and src/net/{format}/
are informed by verified-facts.yaml, implementation-requirements.yaml, and product-readiness.yaml
rather than by scattered evidence re-reading.

## Scope

- Define the Phase 4 source development workflow that references FUL files
- Establish which FUL files are required before each Phase 4 gate
- Create tooling or checklists for developers to verify FUL file coverage
- Document how LLM-assisted code generation (future) should be grounded in FUL files
- Create example: mapping FUL-002 FODS implementation-requirements.yaml to Python test stubs

## Blocked On

- FUL-001 approved (schemas)
- FUL-002 complete for FODS OR FUL-003 complete for FODT
- Phase 4 explicit implementation prompt authorized

## Out of Scope

- Actual product source creation (requires Phase 4 explicit prompt)
- LLM integration (requires LLM-001 authorization)
- Commercial source (requires DD3 resolution)

## Acceptance Criteria

1. Phase 4 workflow documented with FUL file checkpoints.
2. Mapping from implementation-requirements.yaml to test stubs demonstrated.
3. DEC-034 PASS.
4. Human approval.

## Future Trigger

Human authorizes Phase 4 Python implementation prompt after FUL-002 complete.

## Status

proposed_pending_human_approval
