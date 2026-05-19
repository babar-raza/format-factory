# AI Wiring Reality and Decision Report

**Sprint:** R32
**Date:** 2026-05-19
**Lane:** H

---

## AI System Inventory

| Component | Location | LOC | Tests | Status |
|-----------|----------|-----|-------|--------|
| Control plane | tools/ai/control_plane/ | ~400 | ~50 | Implemented |
| Model discovery | tools/ai/control_plane/ | ~200 | ~30 | Implemented |
| Synthesis | tools/ai/synthesis/ | ~300 | ~40 | Framework (fixture mode) |
| Retrieval | tools/ai/retrieval/ | ~300 | ~30 | Framework (fixture mode) |
| Normalization | tools/ai/normalization/ | ~200 | ~30 | Implemented |
| Pipeline | tools/ai/pipeline/ | ~300 | ~40 | Framework |
| Agentic | tools/ai/agentic/ | ~200 | ~30 | Policy only |
| Requirements | tools/ai/requirements/ | ~300 | ~40 | Framework |
| Test generation | tools/ai/test_generation/ | ~200 | ~30 | Framework |
| Telemetry | tools/ai/telemetry/ | ~300 | ~40 | Mapped (not posting) |
| Schemas | tools/ai/schemas/ | ~200 | ~30 | Implemented |
| Validators | tools/ai/validators/ | ~200 | ~40 | Implemented |
| Contracts | tools/ai/contracts/ | ~100 | ~20 | Implemented |
| Prompts | tools/ai/prompts/ | ~200 | ~10 | Templates |
| **Total** | | **~3478** | **461** | |

## Integration Analysis

### Is AI imported by acquisition/productization workflow?
**NO.** Verified by searching for imports of `tools.ai` in `src/python/`:
- Zero imports found
- AI code is entirely self-contained in `tools/ai/`
- No format parser, writer, or test imports any AI module

### Does AI generate requirements today?
**Framework exists, not producing.** `tools/ai/requirements/` and `generated-requirements/fods/` + `generated-requirements/fodt/` contain schema-validated YAML. But these were generated in early sprints and have not been updated or expanded to new formats.

### Does AI generate tests today?
**No.** `tools/ai/test_generation/` has framework code, but all 774 Python tests were hand-written by agents.

### Does AI enforce anything?
**Yes, in isolation.** `run_ai_checks.py` validates:
- Schema compliance
- Direct endpoint bypass detection
- Telemetry mapping
- Model routing rules
But these checks run standalone, not as part of format acquisition gates.

### Is Agent Metrics posting real?
**Mapped, not posting.** Field mapping exists. No evidence of live telemetry being sent.

### Are embeddings/vector stores implemented?
**No.** LanceDB planned, not implemented. Policy documents exist.

### Is GPT-OSS synthesis implemented?
**Framework only, fixture mode.** Env vars GPT_OSS_ENDPOINT/GPT_OSS_API_KEY not set. Tests use fixtures.

### Is Qwen2 agentic work implemented?
**Policy only.** Restricted to `agentic_low_risk`. No evidence of live usage.

## Classification

**AI State: control_plane_only**

The AI platform is a well-architected, well-tested control plane. It validates rules in isolation. It does not yet:
- Generate requirements for new formats
- Generate tests
- Improve source quality
- Post telemetry
- Use embeddings
- Run live synthesis
- Perform agentic tasks

## Decision

### Recommendation: AI must stay out of main productization until gate quality / matrix recovery is complete.

**Rationale:**
1. The project's primary problem is source quality, not AI capability.
2. Investing more in AI scaffolding without pipeline integration increases drift.
3. AI investment should only resume when there is a concrete contract: "AI generates X requirement for format Y, validated by Z test."
4. The 461 AI tests should be maintained (they test valid control plane logic) but not expanded until wiring is planned.

### When AI should be wired in
After Phase 2 (source layout normalization) of the recovery roadmap:
1. Pick 1 format (e.g., ODS) as AI pilot
2. Define contract: AI generates neutral model requirements from spec
3. Validate: generated requirements match human-written ones for FODS/FODT
4. If validated: expand to other formats
5. If not: pause AI investment

### What NOT to do
- Do not add more AI policy documents
- Do not add more AI test files that test scaffolding
- Do not implement embeddings/vector DB until a format-specific use case is proven
- Do not run live AI endpoints without a measurable quality improvement target
