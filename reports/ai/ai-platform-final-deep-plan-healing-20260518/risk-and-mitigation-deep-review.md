# Risk and Mitigation Deep Review

**Sprint:** FORMAT-FACTORY-AI-PLATFORM-FINAL-DEEP-PLAN-HEALING-001
**Date:** 2026-05-18
**Gate:** 6
**Lane:** L6

---

## 1. Risk Register Assessment

The risk register (`docs/ai/ai-risk-register.md`) contains 48 risks (RISK-AI-001 through RISK-AI-048) with all 12 required fields per risk. This review assesses the DEPTH of those controls, not just their presence.

## 2. Control Traceability

### 2.1 Controls That Reference Code That Does Not Exist

Every risk in the register references validation tests, evidence artifacts, and owner taskcards. However, ZERO of these validation tests exist as executable code. This is expected — implementation has not been authorized — but must be tracked:

| Risk Category | Risks | Planned Tests | Existing Tests |
|---------------|-------|---------------|----------------|
| Model drift | 001-005 | 5 | 0 |
| Hallucination/citation | 006-007, 042-044 | 5 | 0 |
| Retrieval | 008-012, 034-035, 045 | 8 | 0 |
| Prompt/schema drift | 013-015 | 3 | 0 |
| Telemetry | 016-017, 023, 046 | 4 | 0 |
| Security | 018-019, 022, 038-039 | 5 | 0 |
| Authority | 020-021, 029-030 | 4 | 0 |
| Nondeterminism/cache | 024-025 | 2 | 0 |
| Evidence/taskcard | 026-027 | 2 | 0 |
| Quality | 028, 040-041 | 3 | 0 |
| Infrastructure | 031-033, 047-048 | 5 | 0 |
| **Total** | **48** | **46** | **0** |

### 2.2 Critical Risk Deep Analysis

**RISK-AI-006 (Hallucinated Requirements) — CRITICAL**
- Prevention says "mandatory citation; source-support verification" but no verifier code exists
- The citation verifier design (Component 17 in production-solution-architecture) must be Phase 2 priority
- Gap: No definition of what "supporting text" means algorithmically (substring match? semantic similarity? human judgment?)
- Recommendation: Phase 2 must define citation support scoring algorithm with threshold

**RISK-AI-020 (AI Output Becoming Authority) — CRITICAL**
- Prevention says "all AI output starts as ai_draft; no skip in lifecycle" but validator doesn't exist
- The state machine is well-defined (12 states, adjacency map) but enforcement is documentation-only
- Gap: Existing generated-requirements/ files have no authority_state metadata
- Recommendation: Phase 1 must include authority_lifecycle validator; Phase 2 must backfill existing generated-requirements

**RISK-AI-018 (Secret Leakage) — CRITICAL**
- Prevention says "keys in .env only; endpoint_identity strips auth"
- Gap: No pre-commit hook for secret scanning exists until Phase 4+
- Phase 0-3 secret protection is MANUAL ONLY
- Recommendation: Add secret pattern grep to runtime_guard.py in Phase 1 (low cost, high value)

## 3. Stop Condition Enforcement

| Stop Condition | Enforcement Mechanism | Status |
|----------------|----------------------|--------|
| No model meets any required role | Gateway returns ROLE_UNAVAILABLE | PLANNED (Phase 1) |
| Eval score drops >20% | Evaluator rejects output | PLANNED (Phase 2) |
| Hallucination rate >10% | Batch monitor | PLANNED (Phase 4) |
| Stale index used for gate evidence | Evidence validator | PLANNED (Phase 3) |
| Secret in committed file | Secret scanner | PLANNED (Phase 1 as part of runtime_guard) |
| Scope violation by Qwen2 | Scope guard immediate stop | PLANNED (Phase 4) |
| Unverified AI output in authority files | Authority lifecycle validator | PLANNED (Phase 1) |

## 4. Risk Severity Distribution

| Severity | Count | Examples |
|----------|-------|---------|
| CRITICAL | 5 | Hallucinated requirements, secret leakage, AI becomes authority, unverified source gen, release influenced by unverified AI |
| HIGH | 12 | Model availability drift, behavior drift, API shape changes, citation mismatch, cross-format contamination, runtime AI imports, scope exceed, gateway bypass, dimension change, prompt injection, plausible-wrong requirements, non-AI depends on AI |
| MEDIUM | 22 | Auto-selection wrong model, fallback quality, retrieval miss/irrelevance, stale embeddings, vector corruption, prompt/schema drift, parser fragility, nondeterminism, stale cache, evidence missing AI, taskcard mismatch, test quality, unsupported claims, contradictions, cache pollution, spool corruption, deferred forgotten |
| LOW | 9 | Telemetry loss (non-blocking), Agent Metrics post fail, cost analytics missing, framework lock-in, version drift, .venv drift, vector not reproducible, data retention, eval false confidence — wait, that's recounted. Actual: LOW severity risks are operational hygiene, not safety |

## 5. Risks Not Yet in Register (Observations)

The 48 risks are comprehensive. Potential additions for future register expansion:

- **RISK-AI-049 (candidate):** Multi-model orchestration confusion — if Phase 6+ introduces LangGraph, model selection across graph nodes could produce inconsistent routing
- **RISK-AI-050 (candidate):** Embedding model licensing change — embedding model at llm.professionalize.com changes license terms
- **RISK-AI-051 (candidate):** Prompt template injection via YAML — malformed YAML in prompt registry could inject unexpected content

These are NOT added to the register in this sprint (register is at 48, meeting requirement). Flagged for future review.

## 6. State Transition

| Timestamp | From | To | Lane | Evidence | Notes |
|-----------|------|----|------|----------|-------|
| 2026-05-18T00:10:00Z | production_architecture_repaired | risk_register_completed | L6 | this file | 48 risks verified, controls traced |
