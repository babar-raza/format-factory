# AI-Assisted Acquisition Pipeline

**Version:** 1.0
**Date:** 2026-05-18
**Status:** PLAN — Implementation not yet authorized
**Authority:** docs/ai/ai-platform-operating-model.md

---

## 1. Purpose

Define how the AI platform integrates with the existing 11-gate format acquisition pipeline. AI assists at specific gates but never approves gates or replaces deterministic validation.

## 2. Gate-by-Gate AI Integration Points

### Gate 1 — Format Candidate Scoring
- **AI role:** Candidate classification, scoring criteria extraction from public information
- **Type:** B (synthesis) or A (low-risk agentic)
- **Input:** Candidate format metadata, public documentation links
- **Output:** Scored candidate YAML (ai_draft)
- **Authority:** Human reviews and approves candidate admission

### Gate 2 — Specification Retrieval
- **AI role:** Spec source identification, retrieval strategy suggestion
- **Type:** B (synthesis)
- **Input:** Format name, known spec sources
- **Output:** Retrieval plan YAML (ai_draft)
- **Authority:** Human approves retrieval; actual retrieval is deterministic

### Gate 3 — Sample Acquisition
- **AI role:** Sample source identification, sample quality assessment
- **Type:** B (synthesis)
- **Input:** Format spec, known sample repositories
- **Output:** Sample acquisition plan YAML (ai_draft)
- **Authority:** Human approves sources; collection is deterministic

### Gate 4 — Prototype Development
- **AI role:** Parser strategy drafting from normalized spec chunks; test idea generation
- **Type:** B (synthesis) + C (retrieval for spec chunks)
- **Input:** Normalized spec artifacts, requirements, samples
- **Output:** Parser strategy YAML (ai_draft), test ideas YAML (ai_draft)
- **Authority:** Human reviews; code is written by human/agent through normal process

### Gate 5 — Neutral Model Design
- **AI role:** Requirement extraction for data model; cross-format pattern analysis
- **Type:** B (synthesis) + C (cross-format retrieval)
- **Input:** Normalized spec, existing format models
- **Output:** Model design suggestions YAML (ai_draft)
- **Authority:** Human designs model; AI suggestions are input only

### Gate 6 — Oracle Comparison
- **AI role:** Diff analysis between Format Factory output and oracle output
- **Type:** B (synthesis)
- **Input:** Comparison results (deterministic), spec references
- **Output:** Diff analysis report (ai_draft)
- **Authority:** Human evaluates; deterministic diff is ground truth

### Gate 7 — Fuzz Testing
- **AI role:** Fuzz strategy suggestion; crash triage assistance
- **Type:** B (synthesis)
- **Input:** Format spec, parser code, known edge cases
- **Output:** Fuzz strategy YAML (ai_draft), crash analysis (ai_draft)
- **Authority:** Human reviews; fuzzing is deterministic

### Gate 8 — Security Review
- **AI role:** Security analysis of parsing code; vulnerability pattern detection
- **Type:** B (synthesis)
- **Input:** Parser code, format spec security sections, known vulnerabilities
- **Output:** Security findings YAML (ai_draft)
- **Authority:** Human security review; AI findings are input

### Gate 9 — Product Mapping
- **AI role:** Feature mapping suggestions; capability gap analysis
- **Type:** B (synthesis)
- **Input:** Requirements, implementation status, capability model
- **Output:** Mapping report (ai_draft)
- **Authority:** Human maps product features

### Gate 10 — Release Candidate
- **AI role:** Release readiness gap analysis
- **Type:** B (synthesis)
- **Input:** All gate evidence, test results, requirements coverage
- **Output:** Readiness assessment (ai_draft)
- **Authority:** Human approves release candidate

### Gate 11 — Commercial Readiness
- **AI role:** Commercial readiness assessment; documentation gap analysis
- **Type:** B (synthesis)
- **Input:** Commercial requirements, implementation evidence
- **Output:** Commercial readiness report (ai_draft)
- **Authority:** Human (Babar Raza) approves commercial release

## 3. Spec Normalization is Mandatory

AI consumption of specifications requires normalization. The spec normalization layer (`docs/specification-normalization.md`) produces:
- Immutable raw spec manifest
- Normalized text
- Page/section maps
- Chunkable markdown/JSONL
- Tables (if extractable)
- References
- Source hashes
- Extraction method and known defects
- Normalization version
- Provenance records

AI and embeddings MUST consume normalized artifacts, not untracked raw PDFs/specs. This ensures provenance, reproducibility, and citation accuracy.

## 4. Test Generation is Mandatory

AI-assisted test generation is part of the generic AI layer, not optional.

Test generation lifecycle:
1. AI generates test ideas citing requirements/spec chunks/samples (ai_draft)
2. Deterministic reviewer/verifier filters for quality and relevance
3. Accepted test ideas converted into normal pytest/.NET xUnit tests
4. Generated tests cannot bypass human/delegated review gates
5. Test idea artifacts retained for replay and audit
6. Generated test quality tracked in telemetry

## 5. Runtime AI-Free Guard

Product runtime code (`src/python/**`, `src/net/**`) MUST NOT import or call AI infrastructure.

Protected imports:
- `tools/ai/**`
- `litellm`, `llama_index`, `lancedb`
- Any `llm.professionalize.com` client
- `GPT_OSS_ENDPOINT`, `GPT_OSS_API_KEY` references
- `openai`, `anthropic`, `ollama` client libraries (in runtime code)

Exception: Repository tools (`tools/**`) and acquisition pipeline scripts may use the AI layer.

Enforcement: Static import analysis via `tools/ai/validators/runtime_guard.py`.

## 6. Cross-References

| Document | Relationship |
|----------|-------------|
| `docs/ai/ai-platform-operating-model.md` | Parent platform model |
| `docs/acquisition-workflow.md` | Existing acquisition pipeline |
| `docs/specification-normalization.md` | Spec normalization requirements |
| `docs/ai/gpt-oss-synthesis-control-policy.md` | Synthesis controls at each gate |
| `docs/ai/embedding-and-vector-store-policy.md` | Retrieval at gates 4-5 |
