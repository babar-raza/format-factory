# AI-Generated Format Requirements Pipeline — Design Report
**Lane R1**
**Date:** 2026-05-13

## Summary

Designed and documented the AI-Generated Format Requirements Pipeline (v1.0). This pipeline produces per-format commercial requirements from local evidence sources, replacing manually-authored static requirement assumptions.

## Key Design Decisions

1. **Local evidence only** — Pipeline consumes only files present in the repo. No spec downloads, no external URLs during generation.
2. **Source priority ladder** — EXISTING_SOURCE > TEST_EVIDENCE > VERIFIED_FACT > SPEC > PRODUCT_DECISION > AI_PROPOSAL
3. **AI_PROPOSAL gate** — AI_PROPOSAL requirements cannot be ACCEPTED without independent verifier approval (Lane R5)
4. **Vertical slice scoping** — ACCEPTED_FOR_VERTICAL_SLICE requires test_requirements; conversion always future-scoped
5. **Repeatability** — Same input sources should produce equivalent requirements on re-run

## Pipeline Stages

1. Gather local evidence (existing source, tests, facts, neutral model, tier map, spec cache)
2. Extract structural facts (entities, namespaces, XML paths)
3. Map to product goals (PG-001 through PG-005)
4. Generate load requirements (C0-C2)
5. Generate object model requirements (C4-C5)
6. Generate edit requirements (C6)
7. Generate save requirements (C7)
8. Mark conversion requirements future-scoped (C9+)
9. Build traceability map
10. Run validator + Lane R5 verifier challenge

## Artifacts

- `docs/ai-generated-format-requirements-pipeline.md`
- `docs/ai-generated-format-requirements-pipeline.yaml`
