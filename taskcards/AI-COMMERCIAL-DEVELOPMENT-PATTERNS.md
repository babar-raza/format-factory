# Taskcard: AI-COMMERCIAL-DEVELOPMENT-PATTERNS

**Status:** completed
**Created:** 2026-05-13
**Sprint:** AI-USAGE-LOCAL-DOC-SYNC-20260513

## Purpose

Define how AI supports commercial .NET implementation of load-edit-save-convert capability for FODS and FODT formats.

## Scope

- Create `docs/ai-assisted-commercial-development.md` (Patterns A-F)
- Create `docs/ai-assisted-commercial-development.yaml` (machine-readable)
- Define spec-to-requirements, requirements-to-model, model-to-code, test generation, adversarial review, evidence summarization patterns
- Define commercial direction guard checklist

## Non-Goals

- Implementing commercial code
- Defining Gate 11 approval criteria
- Changing existing capability model

## Acceptance Criteria

- [x] docs/ai-assisted-commercial-development.md exists
- [x] docs/ai-assisted-commercial-development.yaml exists
- [x] Pattern A (spec extraction) documented
- [x] Pattern B (object model draft) documented
- [x] Pattern C (code draft) documented
- [x] Pattern D (test generation) documented
- [x] Pattern E (adversarial review) documented
- [x] Pattern F (evidence summarization) documented
- [x] Commercial direction guard checklist documented
- [x] FODS and FODT format-specific notes included

## Evidence Requirements

- Files exist and consistent with capability model (C2->C7 trajectory)
- Patterns reference existing sample files and spec cache

## Files Allowed

- docs/ai-assisted-commercial-development.md (create)
- docs/ai-assisted-commercial-development.yaml (create)

## Prohibited Actions

- No code creation
- No claiming commercial readiness

## Validation Required

- Consistency with docs/commercial-product-capability-model.md
- Consistency with docs/commercial-dotnet-architecture.md

## Next Dependency

- NEXT-COMMERCIAL-IMPLEMENTATION-SWARM (uses these patterns)
