# AI Platform Gap Root-Cause Analysis

**Date:** 2026-05-18

## Gap Analysis Summary

12 structural gaps were identified in the prior plan hardening sprint (reports/ai/ai-plan-gap-analysis.md). This analysis traces each gap to its root cause and confirms the correction applied.

## Root Causes

### RC-1: Fragmented Policy Architecture
**Symptom:** GAP-AI-001 (no generic platform boundary)
**Root cause:** AI governance was built incrementally across 5+ sprints (2026-05-08 to 2026-05-13). Each sprint added policies for its specific concern (operating model, RAG, swarm, endpoint strategy) without a unifying platform concept.
**Correction:** `docs/ai/ai-platform-operating-model.md` provides the unified substrate.
**Status:** CORRECTED

### RC-2: Static Model Selection
**Symptom:** GAP-AI-002 (no role-based routing)
**Root cause:** `plans/master-plan.md` Section 14 defined a fixed model-selection table before llm.professionalize.com endpoint behavior was understood. The table assumed stable model names.
**Correction:** `docs/ai/model-routing-and-discovery-policy.md` defines dynamic discovery and role-based routing.
**Status:** CORRECTED

### RC-3: Insufficient Model-Specific Controls
**Symptoms:** GAP-AI-003 (Qwen2 controls), GAP-AI-004 (GPT-OSS controls)
**Root cause:** Model families were named in strategy docs but not given dedicated control policies. Risk profiles differ significantly between agentic (Qwen2) and synthesis (GPT-OSS) work.
**Correction:** Dedicated policies in `docs/ai/agentic-qwen2-control-policy.md` and `docs/ai/gpt-oss-synthesis-control-policy.md`.
**Status:** CORRECTED

### RC-4: Incomplete Retrieval Architecture
**Symptom:** GAP-AI-005 (embedding/vector not fully specified)
**Root cause:** RAG policy blocked Tier 3 for gate evidence but didn't specify the full vector store architecture needed when Tier 3 is eventually enabled.
**Correction:** `docs/ai/embedding-and-vector-store-policy.md` specifies format segregation, lifecycle, and stale detection.
**Status:** CORRECTED

### RC-5: No Telemetry Product Mapping
**Symptom:** GAP-AI-006 (telemetry not mapped to Agent Metrics)
**Root cause:** AGENTS.md H5 defined local JSONL logging but didn't connect it to Agent Metrics as canonical sink.
**Correction:** `docs/ai/ai-telemetry-and-agent-metrics-policy.md` maps all fields and defines spool/post flow.
**Status:** CORRECTED

### RC-6: Shallow Risk Treatment
**Symptom:** GAP-AI-007 (3 risks → 48 needed)
**Root cause:** Risk register covered only obvious risks (leaks, scope creep, secrets). AI-specific risks (hallucination, drift, contamination, prompt injection, eval false confidence) were not systematically cataloged.
**Correction:** `docs/ai/ai-risk-register.md` expanded to 48 risks with full control matrix.
**Status:** CORRECTED (this sprint)

### RC-7: Informal Technology Selection
**Symptom:** GAP-AI-008 (no deferred-feature discipline)
**Root cause:** Technology candidates mentioned informally in memory files without formal implement/defer/reject classification.
**Correction:** `docs/ai/ai-technology-decision-record.md` and `docs/ai/deferred-ai-features-review.md` provide formal decisions.
**Status:** CORRECTED

### RC-8: Missing Normalization Linkage
**Symptom:** GAP-AI-009 (spec normalization not linked to AI)
**Root cause:** `docs/specification-normalization.md` was written before AI platform concept existed.
**Correction:** Cross-references added; `docs/ai/ai-assisted-acquisition-pipeline.md` defines normalization as mandatory AI input.
**Status:** CORRECTED

### RC-9: No Artifact State Machine
**Symptom:** GAP-AI-010 (authority lifecycle missing)
**Root cause:** Operating model defined status values but not transition rules or skip prevention.
**Correction:** `docs/ai/ai-artifact-authority-lifecycle.md` defines 12-state machine with no-skip enforcement.
**Status:** CORRECTED

### RC-10: Optional Test Generation
**Symptom:** GAP-AI-011 (test generation not mandated)
**Root cause:** Pattern D in commercial development doc presented test generation as one of six patterns rather than a mandatory platform capability.
**Correction:** Test generation mandatory in platform model; dedicated taskcard AI-TEST-GENERATION-INTEGRATION.
**Status:** CORRECTED

### RC-11: Informal Runtime Guard
**Symptom:** GAP-AI-012 (runtime AI-free guard not formalized)
**Root cause:** AGENTS.md broadly prohibited AI in products but didn't specify enforcement mechanism.
**Correction:** Runtime guard specified in platform model with static analysis enforcement.
**Status:** CORRECTED

## Assessment

All 12 gaps from the prior analysis have been corrected through documentation. The corrections are structural (new policies, state machines, registries) not superficial (additional paragraphs in existing docs).
