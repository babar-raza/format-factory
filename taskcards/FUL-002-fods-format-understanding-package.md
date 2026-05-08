---
taskcard_id: FUL-002
title: FODS Compiled Format Understanding Package
status: COMPLETED
created: 2026-05-08
sprint: memory-sprint-format-understanding-llm-strategy
visibility: internal
relationship_to_main_sprint: backlog — blocked on FUL-001 design approval
relationship_to_product_source: prerequisite — must complete before FODS Phase 4 source begins (or explicitly waived)
---

# FUL-002 — FODS Compiled Format Understanding Package

## Purpose

Compile all FODS gate evidence into the six Format Understanding Layer files for FODS.
This makes format knowledge product-source-ready and reduces the reading burden for Phase 4 developers.

## Scope

- Compile acquisition-packs/fods/format-profile.yaml from Gate 1 scoring and Gate 2 legal evidence
- Compile acquisition-packs/fods/verified-facts.yaml from spec workbench, Gate 2, Gate 3, Gate 4 prototype notes
- Compile acquisition-packs/fods/implementation-requirements.yaml from Gate 4 parser requirements, Gate 5 neutral model, Gate 6 oracle
- Compile acquisition-packs/fods/parser-strategy.yaml from Gate 4 prototype, Gate 6 oracle, Gate 7 fuzz findings
- Compile acquisition-packs/fods/security-surface.yaml from Gate 7 fuzz report and Gate 8 security report
- Compile acquisition-packs/fods/product-readiness.yaml from Gate 9 tier map and Gate 10 product planning

## Blocked On

- FUL-001 approved (schemas must exist before population)
- FODS Gate 9 PASSED (already PASSED — run047)
- FODS Gate 10 PASSED (already PASSED — run048)

## Out of Scope

- Product source creation
- FODT FUL files — that is FUL-003
- LLM-assisted compilation (may be added later under LLM-001 authorization)
- Any embedding or vector DB work

## Inputs

- All acquisition-packs/fods/ files (gates 1–10)
- schemas/neutral-model/fods/
- reports/security/fods.md
- prototypes/by-format/fods/
- acquisition-packs/fods/tier-map.yaml
- .local/spec-cache/fods/ (for verified-facts citations)

## Outputs

- acquisition-packs/fods/format-profile.yaml
- acquisition-packs/fods/verified-facts.yaml
- acquisition-packs/fods/implementation-requirements.yaml
- acquisition-packs/fods/parser-strategy.yaml
- acquisition-packs/fods/security-surface.yaml
- acquisition-packs/fods/product-readiness.yaml
- Evidence bundle

## Exact Forbidden Files

- src/python/fods/ — product source, not authorized here
- src/net/fods/ — product source, not authorized here
- schemas/format-understanding/ (must already exist from FUL-001)
- .local/embeddings/
- .local/vector/

## Acceptance Criteria

1. All six FODS FUL files populated and valid against FUL-001 schemas.
2. Every verified-facts.yaml entry has a spec_citation.
3. Every implementation-requirements.yaml entry has a source_gate reference.
4. DEC-034 independent verification PASS.
5. Human approval recorded.
6. Evidence bundle BUNDLE_VALIDATION: PASS.

## Future Trigger

Human authorizes FUL-002 execution after FUL-001 design is approved.

## Status

COMPLETED — run049 (2026-05-08). 6 FUL files compiled in acquisition-packs/fods/. FUL-001 schemas used.
