# R28 Lane D: AI End-to-End Pilot
# Date: 2026-05-19

## Pipeline Implemented

Complete E2E pilot pipeline in tools/ai/pipeline/e2e_pilot.py:

1. **Stage 1: Load Chunks** — Loads normalized spec chunks for target format (fixture mode generates 3 chunks)
2. **Stage 2: Retrieval** — Retrieves relevant chunks (fixture: returns all)
3. **Stage 3: Synthesis** — Runs synthesis pipeline with citation verification
4. **Stage 4: Evaluation** — Quality gate checking schema validity, citations, contradictions

## Pilot Format: FODS

- Used FODS as pilot target (verified format with existing spec normalization)
- Also tested with FODT format
- All 4 stages pass in fixture mode

## Authority Lifecycle

- All outputs remain at `ai_draft` — never auto-escalated
- Stage 3 synthesis result carries authority_state = ai_draft
- Final pilot result carries final_authority_state = ai_draft

## Test Results

- **New tests:** 8 (test_r28_e2e_pilot.py)
- **All 8/8 PASS**

## Blockers

- Live mode requires:
  - Actual normalized spec chunks in specs/normalization/{format}/
  - GPT_OSS_ENDPOINT configured for real synthesis
  - Verified facts YAML for contradiction checking
- All blockers are EXPECTED for fixture mode pilot
