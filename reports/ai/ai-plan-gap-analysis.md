# AI Plan Gap Analysis

**Sprint:** FORMAT-FACTORY-AI-LLM-EMBEDDING-PLAN-MEMORY-SYNC-001
**Date:** 2026-05-18
**Gate:** GATE 1 — Current Plan Gap Analysis

## Existing AI Planning Infrastructure

The project has substantial AI governance and strategy documentation from prior sprints (2026-05-08 through 2026-05-13). This is NOT a greenfield AI plan — it is a hardening and correction of existing design.

### Preserved Strengths

| Area | Status | Authority File |
|------|--------|---------------|
| AI-is-accelerator philosophy | ESTABLISHED | docs/ai-usage-operating-model.md |
| Gate approval prohibition | ESTABLISHED | GOVERNANCE.md 26.10, AGENTS.md AF12 |
| Secret management policy | ESTABLISHED | AGENTS.md H2-H3, docs/llm-endpoint-strategy.md |
| Three-tier retrieval hierarchy | ESTABLISHED | docs/spec-retrieval-and-rag-policy.md |
| AI usage ledger format | ESTABLISHED | docs/ai-usage-operating-model.md |
| Generated requirements discipline | ESTABLISHED | AGENTS.md AF13, GOVERNANCE.md 26.11 |
| DEC-034 independent verification | ESTABLISHED | AGENTS.md V, GOVERNANCE.md 26.6 |
| Commercial development patterns | DESIGNED | docs/ai-assisted-commercial-development.md |
| Swarm lane governance | DESIGNED | docs/agent-swarm-ai-orchestration.md |
| LLM module architecture direction | DESIGNED | memory/15, docs/llm-and-embedding-strategy.md |

### Identified Gaps and Weaknesses

#### GAP-AI-001: No Generic Platform Boundary
**Severity:** HIGH
**Description:** Current docs treat AI as a collection of individual tools and policies. There is no unified "AI platform layer" concept that governs all AI usage through a single substrate with contracts, schemas, model discovery, role routing, validators, telemetry, task state, evidence, replay, and regression controls.
**Impact:** Without a platform boundary, AI integration risks becoming ad hoc — each new use case wires directly to endpoints without consistent governance infrastructure.
**Correction:** Create `docs/ai/ai-platform-operating-model.md` defining the generic platform.

#### GAP-AI-002: No Role-Based Model Routing
**Severity:** HIGH
**Description:** `plans/master-plan.md` Section 14 defines a static model-selection table, but there is no dynamic role-based routing policy. Model selection is hardcoded by task type, not discoverable by role. No capability probing, no fail-closed behavior, no model fingerprint capture.
**Impact:** When llm.professionalize.com adds/removes/renames models, the current static table breaks silently.
**Correction:** Create `docs/ai/model-routing-and-discovery-policy.md`.

#### GAP-AI-003: Qwen2 Controls Insufficient
**Severity:** HIGH
**Description:** Qwen2 is mentioned in `docs/llm-and-embedding-strategy.md` as a model family ("Qwen Next") but has no specific control policy. No agentic scope limits, no task contracts, no state-machine guards, no rollback rules, no IV requirements for Qwen2-driven work.
**Impact:** Qwen2 used for agentic work without firm controls could exceed task scope, produce unvalidated mutations, or silently degrade output quality vs. Claude/Codex.
**Correction:** Create `docs/ai/agentic-qwen2-control-policy.md`.

#### GAP-AI-004: GPT-OSS Synthesis Controls Missing
**Severity:** HIGH
**Description:** GPT-OSS is listed as a model family but has no synthesis-specific control policy. No prompt/task contracts, no source-citation requirements, no contradiction detectors, no evaluator/regression suites, no artifact authority state tracking for GPT-OSS outputs.
**Impact:** GPT-OSS synthesis output could become implicitly authoritative without passing through validation gates.
**Correction:** Create `docs/ai/gpt-oss-synthesis-control-policy.md`.

#### GAP-AI-005: Embedding/Vector Store Not Fully Specified
**Severity:** MEDIUM-HIGH
**Description:** `docs/spec-retrieval-and-rag-policy.md` defines Tier 3 as "not yet authorized for gate evidence" and mentions local embedding models. But there is no policy for: format-segregated namespaces, versioned chunk manifests, embedding model fingerprints, index versioning, rebuild/refresh rules, stale-index detection, retrieval audit logs, permanent project-local vector stores.
**Impact:** When embeddings are eventually implemented, without these specifications they risk cross-format contamination, stale retrieval, and non-reproducible indexes.
**Correction:** Create `docs/ai/embedding-and-vector-store-policy.md`.

#### GAP-AI-006: Telemetry Not Mapped to Agent Metrics
**Severity:** MEDIUM-HIGH
**Description:** Current docs specify JSONL run logs in `.local/llm-logs/` (AGENTS.md H5, Section L). But there is no mapping to Agent Metrics as canonical telemetry sink. No schema alignment, no post-to-metrics workflow, no offline spool-to-metrics pipeline, no telemetry field coverage analysis.
**Impact:** Telemetry remains local-only with no aggregation, analytics, or canonical reporting product.
**Correction:** Create `docs/ai/ai-telemetry-and-agent-metrics-policy.md`.

#### GAP-AI-007: Risk Register Shallow
**Severity:** HIGH
**Description:** `plans/master-plan.md` lists risks R-007 (LLM prompt leaks), R-013 (LLM scope creep), R-021 (secrets in memory). But there is no comprehensive AI risk register covering model drift, hallucination, prompt injection, vector contamination, framework lock-in, evaluation false confidence, and 30+ other AI-specific risks.
**Impact:** Risk management is reactive rather than systematic. New risks discovered during implementation will not have pre-established controls.
**Correction:** Create `docs/ai/ai-risk-register.md` with 40-item control matrix.

#### GAP-AI-008: Deferred-Feature Discipline Absent
**Severity:** MEDIUM
**Description:** Several technology candidates are mentioned informally (LangGraph, Prefect, Temporal, Dagster in memory/15; ChromaDB implied by embedding design). No formal review of each candidate with implement/defer/reject classification, risk assessment, and review gate.
**Impact:** Technology decisions are implicit, not governed. Future sprints may adopt components without prerequisite validation.
**Correction:** Create `docs/ai/deferred-ai-features-review.md` and `docs/ai/ai-technology-decision-record.md`.

#### GAP-AI-009: Spec Normalization Not Linked to AI Platform
**Severity:** MEDIUM
**Description:** `docs/specification-normalization.md` defines normalization artifacts but contains zero AI/LLM references. The AI platform must consume normalized artifacts, not raw specs. This linkage is not documented.
**Impact:** AI consumers might bypass normalization and process raw PDFs/specs directly, losing provenance and reproducibility.
**Correction:** Create `docs/ai/ai-assisted-acquisition-pipeline.md` and update `docs/specification-normalization.md` to reference the AI platform.

#### GAP-AI-010: AI Artifact Authority Lifecycle Missing
**Severity:** HIGH
**Description:** `docs/ai-usage-operating-model.md` defines 8 AI output status values, but there is no formal artifact authority lifecycle with defined state transitions (ai_draft → schema_validated → source_cited → ... → authoritative_after_gate → rejected/superseded). No state machine, no transition rules, no skip-prevention.
**Impact:** AI artifacts can jump from draft to authoritative without passing through required validation steps.
**Correction:** Create `docs/ai/ai-artifact-authority-lifecycle.md`.

#### GAP-AI-011: Test Generation Not Mandated
**Severity:** MEDIUM
**Description:** `docs/ai-assisted-commercial-development.md` Pattern D describes AI test generation, but it is presented as optional. No mandate that AI-assisted test generation must be part of the platform with its own artifact lifecycle, reviewer gates, and regression controls.
**Impact:** Test generation may be skipped or done ad hoc without quality controls.
**Correction:** Address in `docs/ai/ai-platform-operating-model.md` and create taskcard.

#### GAP-AI-012: Runtime AI-Free Guard Not Formalized
**Severity:** MEDIUM
**Description:** AGENTS.md broadly prohibits AI in product runtimes, but there is no formal guard specification defining which imports/calls are blocked, which paths are protected, and how static analysis enforces the boundary.
**Impact:** Runtime packages could accidentally import AI infrastructure without detection.
**Correction:** Address in `docs/ai/ai-platform-operating-model.md` Section on runtime isolation.

## Summary

| Gap ID | Severity | Existing Coverage | Correction Required |
|--------|----------|-------------------|---------------------|
| GAP-AI-001 | HIGH | Fragmented policies | Unified platform model |
| GAP-AI-002 | HIGH | Static table only | Dynamic role-based routing |
| GAP-AI-003 | HIGH | Generic mention only | Qwen2 control policy |
| GAP-AI-004 | HIGH | Generic mention only | GPT-OSS synthesis controls |
| GAP-AI-005 | MEDIUM-HIGH | Tier 3 blocked | Full vector store specification |
| GAP-AI-006 | MEDIUM-HIGH | JSONL only | Agent Metrics mapping |
| GAP-AI-007 | HIGH | 3 risks only | 40-item risk register |
| GAP-AI-008 | MEDIUM | Informal mentions | Formal technology review |
| GAP-AI-009 | MEDIUM | Zero AI linkage | Normalization-to-AI pipeline |
| GAP-AI-010 | HIGH | 8 status values | Full lifecycle state machine |
| GAP-AI-011 | MEDIUM | Optional pattern | Mandatory with lifecycle |
| GAP-AI-012 | MEDIUM | Broad prohibition | Formal guard specification |

## Gate 1 Verdict

**GATE 1: PASS** — 12 gaps identified. All correctable through documentation. No implementation blockers.
