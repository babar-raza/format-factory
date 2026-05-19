# Taskcard: AI-GPT-OSS-SYNTHESIS-CONTROLS

## Objective
Implement GPT-OSS synthesis pipeline with citation verification, contradiction detection, evaluator/regression suite, and full artifact authority lifecycle enforcement.

## Status
`implemented_live_verified` — runner.py with citation verification, contradiction detection, and schema validation implemented in R27 (cb7e05c). R31 isolated verification (caed52b): all components verified, 449 AI tests. R32 live citation pipeline (qwen3-next): 2/2 citations verified against source snippets, contradiction check passed, evaluator score 1.0, authority stays ai_draft. 506 AI tests pass.

## Prerequisites
- AI-PLATFORM-FOUNDATION-PLAN Phase 1 control plane operational
- AI-MODEL-DISCOVERY-AND-ROUTING: GPT-OSS discovered and routable
- Normalized spec artifacts available for at least one format (FODS)

## Allowed Scope
- Implement `tools/ai/synthesis/synthesis_runner.py`
- Implement `tools/ai/synthesis/citation_verifier.py`
- Implement `tools/ai/synthesis/contradiction_detector.py`
- Implement `tools/ai/synthesis/evaluator.py`
- Define synthesis task schemas in `tools/ai/schemas/`
- Create golden eval datasets in `tools/ai/evals/`
- Create tests in `tests/ai/test_synthesis.py`

## Forbidden Scope
- No product source changes
- No gate approval
- No authority lifecycle skip
- No synthesis output treated as authoritative without lifecycle completion

## Gates
1. Synthesis runner produces structured output conforming to schema
2. Citation verifier confirms cited chunks support claims
3. Contradiction detector flags conflicts with verified facts
4. Golden eval suite passes for at least one synthesis task type
5. Artifact authority lifecycle enforced (ai_draft → ... → evaluator_passed)
6. Provenance manifest generated for every synthesis run

## Evidence Requirements
- Synthesis output samples with citation verification results
- Contradiction detection examples
- Golden eval baseline and regression results
- Provenance manifests

## Validation Requirements
- `tests/ai/test_synthesis.py` passes
- No unverified synthesis output in authority files

## Closeout Criteria
- At least one synthesis task type (e.g., spec extraction) fully operational
- Citation verification, contradiction detection, and eval passing
- Artifact authority lifecycle enforced end-to-end

## Next Transition
On closeout: AI-TEST-GENERATION-INTEGRATION and AI evidence review become eligible.
