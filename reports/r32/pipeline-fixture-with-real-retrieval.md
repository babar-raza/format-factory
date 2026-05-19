# Pipeline Fixture with Real Retrieval (Lane F)
## Sprint: FORMAT-FACTORY-R32-AI-CLEAN-CLOSURE-STATUS-REPAIR-AND-PIPELINE-DEEPENING-MEGA-TRAIN-001

## Purpose
Re-run the fixture pipeline using the improved deterministic retrieval baseline instead of return-all.

## Pipeline Stages
1. **Load chunks** — 3 fixture FODS chunks (fixture mode)
2. **Retrieval** — lexical retrieval with TF-IDF scoring, top-k selection
3. **Synthesis** — run_synthesis with citation requirement
4. **Citation verification** — verify_all_citations against source snippets
5. **Contradiction check** — check_output_contradictions (fixture facts if provided)
6. **Evaluator** — evaluate_synthesis with quality criteria
7. **Requirements generation** — extract requirements from synthesis output
8. **Authority lifecycle** — remains ai_draft throughout

## Key Changes from R31
- stage_2_retrieval now accepts `use_lexical=True` to activate ranked retrieval
- PilotConfig has new fields: `use_lexical_retrieval`, `retrieval_query`, `retrieval_top_k`
- Legacy mode (`use_lexical=False`) returns all chunks as before (backward compatible)

## Evidence
- Fixture pipeline runner output: reports/r32/pipeline-fixture-run/ai-pipeline-runner-output.json
- CLI: `tools/ai/run_ai_checks.py --fixture-pipeline --sprint-id R32`
- Tests: test_r32_ai_deepening.py::TestPipelineFixtureWithRetrieval (5 tests)

## Test Results
1. `test_pilot_with_lexical_retrieval` — PASS (all stages, lexical mode)
2. `test_pilot_retrieval_selects_top_k` — PASS (top_k=2 enforced)
3. `test_stage_2_lexical_returns_scored_metadata` — PASS (mode=lexical)
4. `test_stage_2_fallback_returns_all` — PASS (backward compat)
5. `test_pilot_deterministic_replay` — PASS (two runs produce same structure)
