# Taskcard: AI-Generated Format Requirements Pipeline
**ID:** AI-GENERATED-FORMAT-REQUIREMENTS-PIPELINE
**Lane:** R1
**Status:** completed
**Completed:** 2026-05-13

## Objective
Design and document the AI-generated format requirements pipeline for producing per-format commercial requirements from local evidence sources.

## Deliverables
- [x] `docs/ai-generated-format-requirements-pipeline.md` — Pipeline design (10 stages, input sources, validation rules)
- [x] `docs/ai-generated-format-requirements-pipeline.yaml` — Machine-readable pipeline spec

## Key Decisions
- Pipeline consumes ONLY local evidence (no spec downloads, no external URLs)
- Priority order: EXISTING_SOURCE > TEST_EVIDENCE > VERIFIED_FACT > SPEC > PRODUCT_DECISION > AI_PROPOSAL
- AI_PROPOSAL cannot be ACCEPTED without verifier approval
- Conversion requirements always future-scoped in initial sprint
- ACCEPTED_FOR_VERTICAL_SLICE requires test_requirements field

## Governance
- DEC-034 compliant (local evidence only, no spec downloads)
- No Gate 11 approval implied
- AI is accelerator not authority (AGENTS.md AF12)
