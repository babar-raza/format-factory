# Tradeoffs and Limits

**Sprint:** FORMAT-FACTORY-AI-PLATFORM-FINAL-DEEP-PLAN-HEALING-001
**Date:** 2026-05-18
**Gate:** 6
**Lane:** L6

---

## 1. What the AI Platform CAN Do

1. Discover and probe models at llm.professionalize.com
2. Route tasks to appropriate models based on role requirements
3. Validate AI outputs against Pydantic schemas
4. Track AI artifact authority through 12-state lifecycle
5. Record every AI call in local telemetry with 30 fields
6. Post aggregated telemetry to Agent Metrics (17 fields)
7. Create per-format vector stores from normalized spec chunks
8. Detect stale indexes and flag retrieval results
9. Verify citations in synthesis output
10. Detect contradictions with verified facts
11. Run golden evaluations for regression detection
12. Enforce scope boundaries for agentic tasks
13. Block AI imports from runtime product code

## 2. What the AI Platform CANNOT Do

1. **Approve gates.** Gate approval is human-only (GOVERNANCE.md 2.1). No AI output may influence a gate decision without completing the full authority lifecycle including human review.

2. **Replace human verification.** DEC-034 requires independent verification by a separate agent session before human review. AI output is input to this process, not a substitute.

3. **Guarantee correctness.** LLM outputs are probabilistic. Citation verification, contradiction detection, and golden evals reduce — but do not eliminate — the risk of incorrect output.

4. **Operate without the endpoint.** If llm.professionalize.com is unreachable and the discovery cache is expired, ALL AI operations stop. There is no local LLM fallback in the current design.

5. **Provide real-time monitoring.** The telemetry system is batch-oriented (per-call JSONL, per-sprint aggregation). It is not a real-time monitoring or alerting system.

6. **Cross-format reasoning.** Vector stores are format-segregated. The platform does not support cross-format analysis unless explicitly flagged.

7. **Self-heal.** If a component fails (spool corruption, index corruption, model removal), the platform fails closed and requires human intervention.

8. **Run without .venv.** AI dependencies (LiteLLM, Pydantic v2, LanceDB, LlamaIndex) are separate from project dependencies. If .venv is not configured, AI tools do not function.

## 3. Key Tradeoffs

### 3.1 Fail-Closed vs Graceful Degradation

**Decision:** Fail-closed for model routing (ROLE_UNAVAILABLE stops the task). Graceful degradation for telemetry (spool accumulates, pipeline continues).

**Tradeoff:** Fail-closed means some sprints cannot complete AI tasks if the endpoint is down. This is intentional — partial AI output from an unqualified model is worse than no output.

### 3.2 Local Vector Store vs Cloud

**Decision:** Local LanceDB in `.local/ai/vector-stores/` (gitignored, project-local).

**Tradeoff:** No shared access across machines. Each developer must build their own indexes. Acceptable because format-factory is a single-developer project with one workstation.

### 3.3 LiteLLM Abstraction vs Direct SDK

**Decision:** LiteLLM wraps all LLM calls. No direct OpenAI/Anthropic SDK usage.

**Tradeoff:** Framework dependency. If LiteLLM breaks or is abandoned, replacement needed. Mitigated by wrapping LiteLLM behind project abstractions (gateway module).

### 3.4 Per-Format Isolation vs Global Index

**Decision:** Separate vector stores per format. No global index.

**Tradeoff:** Cannot compare across formats without explicit cross-format query. Benefit: no contamination risk, clean namespace, independent lifecycle.

### 3.5 Agent Metrics as Canonical vs Local-Only

**Decision:** Agent Metrics (Google Sheet) is canonical telemetry sink. Local JSONL is spool/replay/evidence only.

**Tradeoff:** Dependency on Google Sheet endpoint availability. Mitigated by offline spool with 7-day retry.

### 3.6 Citation Required vs Optional

**Decision:** Citation is MANDATORY for extraction and test_generation tasks. Optional for evidence_review and security_analysis (where the entire context is the citation).

**Tradeoff:** Mandatory citation increases rejection rate but prevents hallucinated requirements entering the pipeline.

### 3.7 Temperature 0.0 vs Nonzero

**Decision:** Temperature 0.0 for extraction and classification. Nonzero allowed for creative tasks (test idea generation).

**Tradeoff:** Temperature 0.0 reduces diversity but improves reproducibility. For spec extraction, reproducibility matters more.

## 4. Explicit Limits

| Limit | Rationale |
|-------|-----------|
| No autonomous code generation in Phase 1-3 | Source generation requires verified requirements (RISK-AI-029) |
| No multi-agent workflows until Phase 6+ | LangGraph deferred; complexity not justified yet |
| No cross-project vector stores | Contamination risk (RISK-AI-045) |
| No real-time alerting | Batch telemetry is sufficient for current scale |
| No automatic model selection for new models | Human review required before routing to unknown model |
| Maximum 7-day spool retention | Prevents unbounded spool growth |
| No embedding of raw PDFs | Only normalized chunks with provenance |
| No AI operation without sprint context | sprint_id and taskcard_id are mandatory |
