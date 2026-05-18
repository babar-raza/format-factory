# Rerun Consistency Failure Analysis

**Sprint:** FORMAT-FACTORY-AI-PLATFORM-DEEP-PRODUCTION-ARCHITECTURE-REVIEW-001
**Date:** 2026-05-18

---

## Purpose

Define what breaks consistency across reruns of AI-assisted pipelines, with detection, prevention, evidence, and regression controls for each.

---

## Consistency Breakers

### CB-01: Model Availability Changes
**What breaks:** llm.professionalize.com removes, renames, or replaces a model between runs.
**Detection:** Model discovery returns different model list; model_id not found in previous run's fingerprint.
**Prevention:** Role-based routing (never hardcode model names); discovery on every invocation; cache previous model list for diff.
**Evidence:** Model discovery diff report in telemetry; ROLE_UNAVAILABLE log entry.
**Regression test:** Mock model removal from /v1/models; verify pipeline halts cleanly and logs reason.

### CB-02: Model Behavior Changes
**What breaks:** Same model_id produces different quality output due to provider-side update.
**Detection:** Golden eval score drop >20% from baseline; output hash differs for identical input/prompt.
**Prevention:** Model fingerprint tracking; mandatory eval after fingerprint change; baseline eval scores stored.
**Evidence:** Eval regression report; before/after score comparison.
**Regression test:** Swap model response mock to degrade quality; verify eval catches degradation.

### CB-03: Role-to-Model Routing Drift
**What breaks:** Routing logic selects a different model for same role due to discovery order, capability score changes, or config update.
**Detection:** Telemetry shows different model_id for same model_role across runs.
**Prevention:** Deterministic routing (stable sort by priority + capability score); routing decision logged.
**Evidence:** Routing selection log with full decision trace.
**Regression test:** Run routing with same discovery results twice; verify identical model selection.

### CB-04: Prompt Changes
**What breaks:** Prompt template modified between runs without version bump.
**Detection:** Prompt version hash differs from previous run; prompt registry detects unversioned change.
**Prevention:** All prompts in registry with content hash; prompt changes require version increment; hash recorded in telemetry.
**Evidence:** Prompt version diff; prompt registry audit.
**Regression test:** Modify prompt without version bump; verify registry rejects it.

### CB-05: Retrieved Chunk Differences
**What breaks:** Different chunks retrieved for same query due to index rebuild, new chunks added, or relevance score changes.
**Detection:** Retrieval audit log shows different chunk_ids for same query_text_hash.
**Prevention:** Pin index version for a pipeline run; replay manifest records exact retrieval results.
**Evidence:** Retrieval replay manifest comparison.
**Regression test:** Run same query against same index version; verify identical chunk_ids returned.

### CB-06: Stale Vector Indexes
**What breaks:** Index was built from spec version X but source now at version X+1; retrieved chunks may be missing new content.
**Detection:** Source hash comparison on every retrieval (stale detector); manifest hash mismatch.
**Prevention:** Mandatory stale check before retrieval; stale flag in telemetry; rebuild trigger on source change.
**Evidence:** Stale index warning in telemetry; source hash diff.
**Regression test:** Update source file; verify stale detector flags index; verify rebuild regenerates fresh index.

### CB-07: Changed Normalized Specs
**What breaks:** Normalization pipeline produces different chunks from same source (e.g., chunking strategy change, page extraction improvement).
**Detection:** Chunk manifest hash changes; chunk count differs.
**Prevention:** Normalization version tracking; chunk manifest committed with hash; normalization changes require taskcard.
**Evidence:** Normalization version log; chunk manifest diff.
**Regression test:** Re-run normalization on same source; verify chunk manifest hash unchanged.

### CB-08: Changed Source/Sample Corpus
**What breaks:** New samples added or existing samples modified; AI pipeline produces different results on different corpus.
**Detection:** Sample manifest hash differs; acquisition pack version changed.
**Prevention:** Sample corpus versioned in acquisition pack; corpus hash recorded in pipeline run.
**Evidence:** Corpus manifest in evidence bundle.
**Regression test:** Add sample; verify pipeline detects corpus change and logs it.

### CB-09: Missing Telemetry Rows
**What breaks:** JSONL spool file truncated, permission error, disk full; some AI calls unrecorded.
**Detection:** Expected call count vs actual spool row count; gap detection in timestamps.
**Prevention:** Spool write as first operation after AI call returns; spool write failure = call failure.
**Evidence:** Spool integrity check in evidence bundle.
**Regression test:** Simulate spool write failure; verify AI call reports as failed.

### CB-10: Fallback Model Differences
**What breaks:** Primary model unavailable; fallback used; output quality/format differs subtly.
**Detection:** telemetry.fallback_model_used == true; output compared against primary model baseline.
**Prevention:** Fallback models must pass same golden evals as primary; eval scores compared.
**Evidence:** Fallback usage log with eval comparison.
**Regression test:** Force fallback; run eval; verify pass/fail threshold maintained.

### CB-11: Taskcard State Mismatch
**What breaks:** AI task completes but taskcard not updated; next run sees stale taskcard state.
**Detection:** Consistency check: completed AI artifacts vs taskcard status.
**Prevention:** Task state machine updates taskcard as part of completion; completion without taskcard update = failure.
**Evidence:** Taskcard state transition log.
**Regression test:** Complete task; verify taskcard status reflects completion.

### CB-12: Evidence Bundle Omissions
**What breaks:** Evidence bundle built without AI telemetry summary, model discovery snapshot, or eval results.
**Detection:** Evidence contract lists required AI metadata files; bundle validator checks.
**Prevention:** AI sprint evidence contract template with mandatory AI metadata files.
**Evidence:** Bundle validation report.
**Regression test:** Build bundle without AI artifacts; verify validation fails.

### CB-13: Untracked Local Caches
**What breaks:** `.local/ai/` contains cached model lists, embedding indexes, spool files from previous runs that influence current run behavior.
**Detection:** Cache age check; cache key validation against current inputs.
**Prevention:** Cache keyed on input hash + model fingerprint + prompt version; TTL enforcement.
**Evidence:** Cache hit/miss statistics in telemetry.
**Regression test:** Change input; verify cache miss; verify fresh computation.

### CB-14: Framework Dependency Version Drift
**What breaks:** LiteLLM 1.40 behavior differs from 1.42; LanceDB schema migration needed.
**Detection:** requirements.txt hash comparison; package version recorded in telemetry.
**Prevention:** Exact version pins in requirements.txt; .venv rebuilt from pins; version logged.
**Evidence:** Package version manifest in evidence bundle.
**Regression test:** Compare golden eval results across two dependency versions.

### CB-15: Environment Drift in .venv
**What breaks:** .venv has extra/missing packages; Python version differs; PATH differences.
**Detection:** `pip freeze` hash comparison; Python version check.
**Prevention:** .venv built from exact requirements.txt; Python version pinned.
**Evidence:** pip freeze snapshot in evidence bundle.
**Regression test:** Build .venv from requirements.txt; verify pip freeze hash matches expected.

### CB-16: External Endpoint Response Variation
**What breaks:** llm.professionalize.com returns different response format, additional fields, changed error codes.
**Detection:** Response schema validation; unexpected field detection; HTTP status code changes.
**Prevention:** Response validated against expected schema; unexpected shapes logged and rejected.
**Evidence:** Response schema validation log.
**Regression test:** Mock unexpected response shape; verify graceful failure.

### CB-17: AI Artifact State Transitions Not Enforced
**What breaks:** Artifact moves from ai_draft directly to accepted_for_tests, skipping verification steps.
**Detection:** State transition validator rejects invalid transitions.
**Prevention:** State machine with explicit valid transitions; transition requires evidence of previous state completion.
**Evidence:** State transition log with timestamps and evidence paths.
**Regression test:** Attempt invalid state transition; verify rejection.
