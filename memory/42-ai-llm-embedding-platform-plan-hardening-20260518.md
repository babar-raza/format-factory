# 42 — AI/LLM/Embedding Platform Plan Hardening (2026-05-18)

**Sprint 1:** FORMAT-FACTORY-AI-LLM-EMBEDDING-PLAN-MEMORY-SYNC-001 (commit 13ba55f)
**Sprint 2:** FORMAT-FACTORY-AI-PLATFORM-FINAL-PLAN-HEALING-AND-IMPLEMENTATION-READINESS-001 (commit fcab643)
**Sprint 3:** FORMAT-FACTORY-AI-PLATFORM-FINAL-DEEP-PLAN-HEALING-001
**Date:** 2026-05-18
**Type:** Plan hardening and memory synchronization only — no implementation performed.

## Summary

Three sprints on 2026-05-18 hardened the AI/LLM/Embedding platform plan from immature to production-ready. Sprint 3 added deep production architecture review: 13 root causes, 17 rerun consistency breakers, preserve/redesign matrix, 17-component production solution architecture, control-plane contract model, model routing stress analysis, retrieval/vector replay design, telemetry/Agent Metrics concrete field mapping, tradeoffs/limits, recovery model, and content-level validation. 11 docs/ai/ files, 17 AI taskcards, 48-risk register, 10-report architecture package, 15 deep review reports, 4 companion analysis reports. LLM-001/EMB-001 frontmatter normalized to superseded. Implementation not yet authorized.

## Corrected AI Platform Direction

### Three AI Usage Types + Control Plane

**Type A — Agentic Reasoning / Task Execution**
- HIGH-RISK: Claude/Codex (outside llm.professionalize.com)
- LOW-RISK: Qwen2 through llm.professionalize.com with strict controls
- Controls: role contract, task contract, path/operation allowlists, state-machine guard, validators, IV, evidence, rollback, no authority

**Type B — LLM Transformation / Synthesis**
- Preferred: GPT-OSS through llm.professionalize.com
- Use cases: spec understanding, requirement extraction, test generation, security analysis, evidence review
- Controls: prompt contract, schema validation, cited source chunks, source-support verifier, contradiction detector, evaluator regression, artifact authority lifecycle

**Type C — Embeddings / Retrieval**
- Source: embedding model through llm.professionalize.com (auto-detected)
- Vector stores: format-segregated, permanent, project-local (`.local/ai/vector-stores/`), hash-invalidated, never authority
- Controls: namespace isolation, versioned manifests, stale detection, retrieval audit logs

**Mandatory Control Plane**
- Model discovery and capability probing
- Role-based model routing (not hardcoded)
- Task contracts, prompt registry, schema registry
- Validators, evaluators, telemetry (Agent Metrics)
- Evidence integration, no-runtime-AI guards

### Key Decisions

1. **Qwen2 controls:** Restricted to `agentic_low_risk` only. Full policy: `docs/ai/agentic-qwen2-control-policy.md`.
2. **GPT-OSS synthesis controls:** Citation-verified, contradiction-checked, eval-gated. Full policy: `docs/ai/gpt-oss-synthesis-control-policy.md`.
3. **Embedding/vector permanence:** Format-segregated LanceDB, hash-invalidated, replayable. Full policy: `docs/ai/embedding-and-vector-store-policy.md`.
4. **Agent Metrics telemetry:** Canonical sink. Local JSONL is spool/replay/evidence only. Full policy: `docs/ai/ai-telemetry-and-agent-metrics-policy.md`.
5. **Spec normalization mandatory:** AI consumes normalized artifacts only. See `docs/ai/ai-assisted-acquisition-pipeline.md`.
6. **Test generation mandatory:** With full artifact lifecycle and reviewer gates. See taskcard AI-TEST-GENERATION-INTEGRATION.
7. **Risk mitigation:** 48-item risk register with controls, validation tests, stop conditions. See `docs/ai/ai-risk-register.md`.
8. **Deferred features:** Formal review of 25 candidates with implement/defer/reject. See `docs/ai/deferred-ai-features-review.md`.
9. **AI artifact authority lifecycle:** `ai_draft` → ... → `authoritative_after_gate`. No skip. See `docs/ai/ai-artifact-authority-lifecycle.md`.
10. **Runtime AI-free guard:** Static analysis prevents AI imports in `src/`. See runtime guard in platform model.

### Technology Stack

| Phase 1 (Foundation) | LiteLLM, Pydantic v2, Agent Metrics local spool, pytest evals |
| Phase 2 (Synthesis) | GPT-OSS pipeline, eval harness, test generation |
| Phase 3 (Retrieval) | LlamaIndex, LanceDB, per-format embeddings |
| Phase 4+ | Qwen2 agentic, cross-format, source generation |
| Rejected | ChromaDB, Qdrant, LangChain, Docker AI, runtime AI, AI gate approval |

### Implementation Not Yet Authorized

Implementation requires:
1. Human review and acceptance of the plan
2. Explicit authorization to begin Phase 1
3. No AI code, endpoints, vector DBs, or runtime changes until authorized

## Files Created

### docs/ai/ (11 files)
- ai-platform-operating-model.md
- model-routing-and-discovery-policy.md
- agentic-qwen2-control-policy.md
- gpt-oss-synthesis-control-policy.md
- embedding-and-vector-store-policy.md
- ai-telemetry-and-agent-metrics-policy.md
- ai-risk-register.md
- ai-artifact-authority-lifecycle.md
- ai-assisted-acquisition-pipeline.md
- ai-technology-decision-record.md
- deferred-ai-features-review.md

### taskcards/ (10 files)
- AI-PLATFORM-FOUNDATION-PLAN.md
- AI-MODEL-DISCOVERY-AND-ROUTING.md
- AI-AGENTIC-QWEN2-CONTROLS.md
- AI-GPT-OSS-SYNTHESIS-CONTROLS.md
- AI-EMBEDDING-VECTOR-STORE-FOUNDATION.md
- AI-TELEMETRY-AGENT-METRICS-INTEGRATION.md
- AI-SPEC-NORMALIZATION-INTEGRATION.md
- AI-TEST-GENERATION-INTEGRATION.md
- AI-RISK-MITIGATION-MATRIX.md
- AI-FOUNDATION-IMPLEMENTATION-NEXT.md

### Updated existing files
- plans/master-plan.md — Section 39 added (v2.57)
- ROADMAP.md — Infrastructure milestones updated; Architecture Backlog LLM section updated
- GOVERNANCE.md — Section 26.14 added
- AGENTS.md — Section AF16 added
- docs/python-foss/specification-normalization.md — AI platform cross-references added
- docs/python-foss/acquisition-workflow.md — AI pipeline cross-references added
- docs/python-foss/format-expansion-roadmap.md — AI platform cross-references added
- docs/governance/current-state-and-evidence-authority.md — Section 8.4 AI artifact authority added

### Reports
- reports/ai/ai-plan-hardening-preflight.md
- reports/ai/ai-plan-gap-analysis.md

## Required Reading for Future AI Implementation Sprints

1. `docs/ai/ai-platform-operating-model.md` — start here
2. `plans/master-plan.md` Section 39
3. `docs/ai/ai-risk-register.md` — 48 risks with controls
4. `docs/ai/deferred-ai-features-review.md` — what to build when
5. `reports/ai/ai-platform-plan-20260518/final-execution-readiness-review.md` — implementation prerequisites
6. `reports/ai/ai-platform-final-deep-plan-healing-20260518/` — deep production review (15 reports)
7. Relevant taskcard for the specific phase being implemented
