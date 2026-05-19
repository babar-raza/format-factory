# R32 AI Clean Closure, Status Repair, and Pipeline Deepening

## Sprint
FORMAT-FACTORY-R32-AI-CLEAN-CLOSURE-STATUS-REPAIR-AND-PIPELINE-DEEPENING-MEGA-TRAIN-001

## Key Outcomes
- R31 metadata drift forward-documented (commit SHA, bundle validation, adversarial pending)
- Deterministic lexical retrieval baseline: tools/ai/retrieval/lexical_retriever.py (TF-IDF scored, top-k, namespace-filtered)
- litellm lazy import: gateway.py no longer imports litellm at module level
- Live citation pipeline: qwen3-next, 2/2 citations verified, evaluator score 1.0, ai_draft
- 57 new R32 tests (506 total AI tests)
- 19 new failure injection cases (34 total with R31)
- AI runner hardened: 6 CLI modes, exit codes 0/1/2
- Canonical verification matrix: docs/ai/ai-system-verification-matrix.md
- 5 AI taskcards updated to reflect R31/R32 verified state

## Test Counts
- AI with env: 506 passed
- AI clean-env: 506 passed
- New R32: 57 tests
- Live probes: 1 (citation pipeline)

## Files Created/Modified
- tools/ai/retrieval/lexical_retriever.py (NEW)
- tools/ai/control_plane/gateway.py (lazy import)
- tools/ai/pipeline/e2e_pilot.py (lexical retrieval integration)
- tools/ai/run_ai_checks.py (6 new CLI modes)
- tests/ai/test_r32_ai_deepening.py (57 tests)
- tests/ai/test_r28_e2e_pilot.py (fixture_return_all mode name fix)
- docs/ai/ai-system-verification-matrix.md (NEW)
- 5 taskcards updated
- 15 reports in reports/r32/
