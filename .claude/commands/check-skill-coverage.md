---
version: "1.0"
last-updated: "2026-06-21"
phase-available: "all"
gate-required: null
created-by: skill-governance-sync-sprint
---

# /check-skill-coverage

Check whether a planned work type is covered by a registered skill before executing
product source changes. This command is the MANDATORY pre-gate for any product work.

If no skill covers the planned work type, this command produces a skill-gap taskcard
and BLOCKS product work until the skill is designed, registered, and verified.

## Purpose

Enforce the master plan rule: "Claude may only perform a type of work if a matching
skill exists and is invoked." (plans/master-plan.md Section 9)

## When to Run

Run this command BEFORE any sprint step that involves:
- Writing or modifying files under `src/python/` or `src/net/`
- Creating or modifying test files that prove new product capability
- Creating dogfood export paths
- Modifying packaging or public API

This command is OPTIONAL for non-product work (reports, docs, tools, governance files).

## Required Inputs

- `work_type` — one of: python_api, dotnet_api, python_object_model, dotnet_object_model,
  dogfood_export, writer_feature, roundtrip_test, installed_example, analytics_function,
  spec_literal_migration, sal_pipeline_heal, capability_compiler, other
- `format_id` — the format being worked on
- `planned_paths` — list of src/ paths that would be modified

## Steps

1. Read `.supervisor/skill-registry.yaml` and extract all active skills.
2. Map the `work_type` to the expected skill(s) using the mapping table below.
3. Verify the mapped skill(s) are `status: active` in the registry.
4. If a matching active skill exists:
   a. Report: `SKILL_COVERAGE_CONFIRMED: skill_id=<id>, work_type=<type>`
   b. Name the skill that MUST be invoked for this work.
   c. Confirm the product-code ledger exists (for source-editing skills).
   d. Return `PROCEED_WITH_SKILL: <skill_id>`
5. If NO matching active skill exists for the work type:
   a. Report: `SKILL_GAP_DETECTED: work_type=<type>, format=<format>`
   b. Create a skill-gap taskcard at `.local/taskcards/SKILL-GAP-<timestamp>.yaml`
      using the schema below.
   c. Return `BLOCKED_SKILL_GAP: <taskcard_path>` — do NOT proceed with product work.
   d. The next action must be to design and register the missing skill.

## Work-Type to Skill Mapping

| work_type | required_skill_id |
|-----------|------------------|
| python_api | add-python-api |
| dotnet_api | add-dotnet-api |
| python_object_model | add-python-object-model-feature |
| dotnet_object_model | add-dotnet-object-model-feature |
| dogfood_export | add-dogfood-export |
| writer_feature | add-same-format-writer-feature |
| roundtrip_test | add-roundtrip-test (tests only) |
| installed_example | add-installed-package-example |
| analytics_function | add-analytics-function |
| spec_literal_migration | spec-parity-source-regeneration-and-migration |
| python_reduced_parity | python-reduced-spec-parity-model |
| qname_mapping | spec-literal-qname-to-code-mapping |
| architecture_blueprint | spec-shaped-product-architecture-blueprint |
| sal_pipeline_heal | sal-pipeline-heal |
| capability_compiler | SKILL_GAP (no skill registered — creates taskcard) |
| other | SKILL_GAP if involves src/ changes — creates taskcard |

## Skill-Gap Taskcard Schema

When a SKILL_GAP is detected, create:

```yaml
taskcard_id: "SKILL-GAP-<YYYYMMDD-HHMMSS>"
title: "Missing skill for work_type: <work_type>"
status: "gap_confirmed"
priority: HIGH
source_finding: "check-skill-coverage detected no active skill for this work type"
master_plan_clause: "plans/master-plan.md Section 9"
format_id: "<format>"
work_type: "<work_type>"
planned_paths: <list>
required_work:
  - "Design skill spec (purpose, required_handoff_fields, mandatory_validations)"
  - "Create command file in .claude/commands/<skill-id>.md"
  - "Register in .supervisor/skill-registry.yaml"
  - "Verify skill with test invocation"
  - "Use skill to perform the original blocked work"
blocked_product_work: "<description of what was blocked>"
created_at: "<ISO timestamp>"
created_by: "check-skill-coverage"
```

## Output Format

```
SKILL_COVERAGE_CHECK RESULT
---------------------------
work_type: <type>
format_id: <format>
planned_paths: <list>
matched_skill: <skill_id | NONE>
skill_status: <active | deferred | MISSING>
verdict: PROCEED_WITH_SKILL | BLOCKED_SKILL_GAP
taskcard_created: <path | null>
next_action: <invoke skill_id | design skill for skill_gap>
```

## Allowed Paths (this command only reads)

- `.supervisor/skill-registry.yaml`
- `.local/taskcards/` (writes skill-gap taskcards only)

## Forbidden Actions

- Do NOT modify `src/` during this check.
- Do NOT invoke any product skill — only verify coverage.
- Do NOT approve gates or change gate state.

## Validation

Command is complete when:
- Coverage verdict is emitted (PROCEED_WITH_SKILL or BLOCKED_SKILL_GAP)
- If BLOCKED: taskcard exists at the reported path
- If PROCEED: skill_id is named and can be invoked in the next step

## Changelog

- 1.0 (2026-06-21): Initial version — skill-governance-sync-sprint (SKILL-GAP-010)

## Forbidden Paths

- `src/net/**` — no .NET product source mutation
- `src/python/**` — no Python product source mutation
- `plans/strategic/**` — strategic plans are read-only

## Stop Conditions

- Stop if the skill's mandatory validations cannot be completed
- Stop if any required input field is missing or invalid
