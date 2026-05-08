---
taskcard_id: FUL-003
title: FODT Compiled Format Understanding Package
status: proposed_pending_human_approval
created: 2026-05-08
sprint: memory-sprint-format-understanding-llm-strategy
visibility: internal
relationship_to_main_sprint: backlog — blocked on FUL-001 and FODT Gate 9
relationship_to_product_source: prerequisite — must complete before FODT Phase 4 source begins (or explicitly waived)
---

# FUL-003 — FODT Compiled Format Understanding Package

## Purpose

Compile all FODT gate evidence into the six Format Understanding Layer files for FODT.

## Scope

- Compile acquisition-packs/fodt/format-profile.yaml
- Compile acquisition-packs/fodt/verified-facts.yaml
- Compile acquisition-packs/fodt/implementation-requirements.yaml
- Compile acquisition-packs/fodt/parser-strategy.yaml
- Compile acquisition-packs/fodt/security-surface.yaml (from Gate 8 PASSED run048)
- Compile acquisition-packs/fodt/product-readiness.yaml (after Gate 9 passes)

## Blocked On

- FUL-001 approved
- FODT Gate 9 PASSED (TC-0048 not yet started)

## Out of Scope

- FODS FUL files — that is FUL-002
- Product source creation
- Any embedding or vector DB work

## Inputs

- All acquisition-packs/fodt/ files (gates 1–8 PASSED + gate 9 TBD)
- schemas/neutral-model/fodt/
- reports/security/fodt.md (Gate 8 PASSED run048)
- prototypes/by-format/fodt/

## Acceptance Criteria

1. All six FODT FUL files populated and valid against FUL-001 schemas.
2. Every verified-facts.yaml entry has a spec_citation.
3. DEC-034 independent verification PASS.
4. Human approval recorded.
5. Evidence bundle BUNDLE_VALIDATION: PASS.

## Future Trigger

Human authorizes FUL-003 after FUL-001 approved AND FODT Gate 9 PASSED.

## Status

proposed_pending_human_approval — blocked on FUL-001 and FODT Gate 9; no execution in this sprint.
