---
taskcard_id: FUL-001
title: Format Understanding Layer — Schema and Design
status: proposed_pending_human_approval
created: 2026-05-08
sprint: memory-sprint-format-understanding-llm-strategy
visibility: internal
relationship_to_main_sprint: backlog — not a MAIN SPRINT gate; must not start before human approval
relationship_to_product_source: prerequisite — FUL-002/003 must complete before product source begins
---

# FUL-001 — Format Understanding Layer: Schema and Design

## Purpose

Design the Format Understanding Layer schemas and file structure before any per-format compilation
begins. Defines the schema for all six per-format understanding files and establishes the
authority model, update rules, and invalidation conditions.

## Scope

- Define YAML schema for: format-profile.yaml, verified-facts.yaml, implementation-requirements.yaml, parser-strategy.yaml, security-surface.yaml, product-readiness.yaml
- Define field-level rules for each schema (required fields, allowed values, citation requirements)
- Define authority model (how FUL files relate to gate evidence, specs, and human approvals)
- Define update rules (when FUL files must be refreshed after gate changes)
- Define invalidation conditions (what breaks a FUL file's validity)
- Create JSON Schema or YAML schema validation tooling (optional — for later review)

## Out of Scope

- Populating per-format FUL files (FODS or FODT) — that is FUL-002 and FUL-003
- Product source creation
- LLM or embedding integration
- Non-XML format profiles

## Inputs

- docs/format-understanding-layer.md (this sprint)
- plans/master-plan.md
- AGENTS.md and GOVERNANCE.md
- Existing gate evidence as reference for schema design

## Outputs

- schemas/format-understanding/ (new directory)
  - format-profile.schema.yaml
  - verified-facts.schema.yaml
  - implementation-requirements.schema.yaml
  - parser-strategy.schema.yaml
  - security-surface.schema.yaml
  - product-readiness.schema.yaml
- docs/format-understanding-layer.md (updated with schema references)
- evidence bundle

## Exact Allowed Files

- schemas/format-understanding/*.schema.yaml (new)
- docs/format-understanding-layer.md (update only)
- plans/master-plan.md (update only)
- memory/ (update only)
- tools/evidence/contracts/FUL-001-*.yaml (evidence contract)

## Exact Forbidden Files

- src/python/fods/ — product source
- src/net/fods/ — product source
- acquisition-packs/fods/verified-facts.yaml — not yet (FUL-002)
- acquisition-packs/fodt/verified-facts.yaml — not yet (FUL-003)
- Any per-format FUL YAML files — not yet
- .local/embeddings/ — not yet
- .local/vector/ — not yet

## Acceptance Criteria

1. All six schemas defined with required fields, types, and citation rules.
2. Authority model documented and consistent with AGENTS.md and GOVERNANCE.md.
3. DEC-034 independent verification PASS.
4. Human approval recorded.
5. Evidence bundle BUNDLE_VALIDATION: PASS.

## Evidence Requirements

- DEC-034 independent verification in separate session
- Evidence bundle with schema files and design docs

## Future Trigger

Human authorizes FUL-001 execution after reviewing docs/format-understanding-layer.md.

## Status

proposed_pending_human_approval — no execution authorized in this memory sprint.
