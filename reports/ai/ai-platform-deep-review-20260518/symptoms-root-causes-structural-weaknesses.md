# Symptoms, Root Causes, and Structural Weaknesses

**Sprint:** FORMAT-FACTORY-AI-PLATFORM-DEEP-PRODUCTION-ARCHITECTURE-REVIEW-001
**Date:** 2026-05-18

---

## 1. Symptoms

### S-01: Docs exist but enforcement does not
11 policy documents in `docs/ai/` define contracts, schemas, lifecycle states, routing rules, and controls. Zero lines of enforcement code exist. No `tools/ai/` directory. No validators. No runtime guard. No model discovery. The policy-code gap is total.

### S-02: Taskcards exist but implementation readiness is unproven
16 AI-* taskcards have status `plan_hardened`. But several lack prerequisite specificity. AI-PLATFORM-FOUNDATION-PLAN lists `.venv` with LiteLLM as prerequisite but doesn't specify version pinning, lock file, or what happens if LiteLLM drops a breaking release between planning and execution.

### S-03: Future phases are not contract-bound
Phase 1 has a taskcard. Phases 2-7 are described only in prose in the operating model. No per-phase contract exists defining entry criteria, exit criteria, validation commands, evidence requirements, or rollback rules. An implementation sprint could drift from the plan with no structural guard.

### S-04: Model routing is disconnected from gate/task authority
The model routing policy defines roles (agentic_low_risk, structured_extraction, etc.) but doesn't connect to the existing gate authority model. Which model role is required at which gate? What happens if gate 4 needs structured_extraction but only agentic_low_risk is available? The policy doesn't say.

### S-05: Telemetry binding to Agent Metrics is aspirational
The telemetry policy defines 30+ fields per call and a Google Sheet posting flow. But the Agent Metrics Google Sheet has 17 specific fields (timestamp, agent_name, agent_owner, job_type, run_id, status, product, platform, website, website_section, item_name, items_discovered, items_succeeded, items_failed, run_duration_ms, token_usage, api_calls_count). The mapping between 30 local fields and 17 Google Sheet fields is described as "mapping rules" (Section 4.2) without concrete specification. The aggregation logic (per-call -> per-run summary) is not defined.

### S-06: Embedding replay/refresh is under-specified for real use
The embedding policy says "refresh when source hash changes" but doesn't address: What if only 3 of 940 chunks change? Full rebuild or incremental? What if embedding model changes but old model is gone? What if LanceDB schema changes between versions? The policy assumes steady-state operations but doesn't handle transitions.

### S-07: Risk register lists risks without engineering depth
40 risks exist. Each has one-line prevention/mitigation. Example: RISK-AI-020 "AI output becomes authority" — Prevention: "All AI output starts as ai_draft; no skip in lifecycle." But there is no enforcement mechanism, no state machine code, no database of artifact states. The prevention is a re-statement of the policy, not an engineering control.

### S-08: Validation list tests file existence, not behavior
The current plan's validation checks are: file count, grep for imports, evidence contract existence. These prove the plan sprint didn't create implementation code. They don't prove the plan is complete, consistent, or implementable. No content validation exists.

### S-09: Parallel sprint safety is path-based only
The plan defines owned/forbidden paths for AI vs non-AI sprints. But path-based isolation doesn't prevent: (a) a non-AI sprint adding an `import litellm` somewhere unexpected, (b) a shared file (plans/master-plan.md) getting conflicting edits, (c) evidence bundles from parallel sprints referencing stale AI plan state. State-based isolation is needed.

### S-10: Findings are inventory, not architecture analysis
The original plan audit classifies every AI reference as "active runtime / config only / docs only" etc. This is useful but it's a census, not an analysis. It doesn't answer: Why can't we build this today? What would break if we built it naively? What must the architecture guarantee that simple coding cannot?

---

## 2. Root Causes

### RC-01: No AI platform boundary exists
There is no enforced boundary between "AI platform" and "everything else." Nothing prevents a future sprint from importing `litellm` in `tools/evidence/`, calling GPT-OSS from `tools/spec-normalize/`, or embedding vectors in `tools/oracle/`. The AI platform is a concept in docs, not a boundary in code.

**Why this matters:** Without a boundary, every component could independently acquire AI capabilities, creating ungovernability. The policy says "all AI calls through tools/ai/ only" but there is nothing structural enforcing this.

### RC-02: No executable contract model
The plan defines contracts (role contracts, task contracts, prompt contracts, output schemas) but only as prose descriptions. No Pydantic models exist. No JSON Schema files exist. No validation code exists. The only executable schema validation in the project is `tools/requirements/validate_generated_requirements.py` for AI-generated requirements — and that was built separately, not as part of a platform.

**Why this matters:** Contracts that exist only as documentation get violated silently. The first implementation sprint will have to design schemas from scratch because the plan doesn't provide them.

### RC-03: No state machine connecting AI artifacts to gates
The artifact authority lifecycle defines 12 states (ai_draft through authoritative_after_gate). But this lifecycle is entirely disconnected from the format-registry gate model. When does an AI artifact's lifecycle state need to advance for a gate to proceed? Which gate requires which artifact state? The two authority models don't reference each other's states.

**Why this matters:** The project already has a proven gate model (11 gates, human approval, registry entries). The AI artifact lifecycle is a second, parallel authority model with no integration. This will cause confusion about which model governs what.

### RC-04: No model capability contract
The plan says "model discovery probes capabilities" but doesn't define what capabilities are required for each role. What context window is needed for structured_extraction? What embedding dimensions are acceptable? What structured output format must be supported? Without a capability contract, model routing is guesswork.

**Why this matters:** If llm.professionalize.com adds a new model tomorrow, the routing system has no basis for deciding whether it's suitable for any role.

### RC-05: No per-format retrieval authority model
Embeddings are "retrieval aids, never authority." But the plan doesn't specify how retrieval results connect to the fact verification chain. When a synthesis model uses retrieved chunks to generate requirements, how does the system know whether the retrieved chunks are from verified-facts.yaml (authoritative) or raw spec text (non-authoritative)? The provenance chain is described but the authority classification of retrieved content is missing.

### RC-06: No replay model for AI-assisted decisions
The plan mentions "replay manifests" and "replayability" but doesn't define a replay format, a replay runner, or how to verify that a replay produces the same results. Replayability is stated as a goal but not designed as a system.

### RC-07: No canonical telemetry posting lifecycle
The Agent Metrics flow is: call -> local JSONL -> post to Google Sheet. But: When does posting happen? Per-call? Per-sprint? At evidence bundle build time? The policy says "async" but doesn't define the trigger. It says "retry on next pipeline invocation" but there is no pipeline invocation mechanism yet. The posting lifecycle is circular — it depends on infrastructure that doesn't exist.

### RC-08: No distinction between local spool purposes
`.local/ai/llm-logs/` serves as: offline buffer, replay ledger, evidence artifact, debug trace, and posting retry source (per telemetry policy Section 2.2). These five purposes have different retention, privacy, and integrity requirements. A single JSONL file cannot serve all five well. Replay needs immutability; posting retry needs mutation (marking posted records); evidence needs summaries; debug needs verbosity.

### RC-09: No drift detector design
The plan mentions "model fingerprint tracking" and "stale index detection" but doesn't design an actual drift detection system. How frequently does drift detection run? Is it per-call or per-sprint? What is the detection threshold? How are drift alerts routed? What happens between detection and human response?

### RC-10: No proof that runtime packages cannot import AI tooling
The risk register mentions a "runtime guard" (RISK-AI-019) with validation test "Add AI import to src/ file; verify guard catches it." But the guard doesn't exist. More importantly, there's no CI check, no pre-commit hook, and no `.importlinter` config. The proof is entirely aspirational.

### RC-11: No rollback/recovery model
What happens when: model discovery fails mid-sprint? A synthesis run produces garbage? An embedding index gets corrupted? A telemetry spool file is malformed? The plan has no error recovery design. Every component is described in its success path only.

### RC-12: No Qwen2 scope contract is machine-verifiable
The Qwen2 policy says "path allowlist" and "operation allowlist" but doesn't define the enforcement mechanism. Is it a Python decorator? A filesystem permission? A process sandbox? An API-level filter? Without a mechanism, the allowlist is advisory.

### RC-13: No source-support verification is deep enough
The GPT-OSS synthesis policy says "source-support verifier confirms cited chunks support the claims." But what does "support" mean algorithmically? String matching? Semantic similarity? Human judgment? If it's LLM-based verification, it's circular (LLM verifying LLM output). If it's keyword matching, it's brittle. The verification depth is unspecified.

---

## 3. Structural Weaknesses

### SW-01: Policy-code gap
**Description:** 11 policy documents, 0 enforcement modules. Every enforcement claim is aspirational.
**Consequence:** The first implementation sprint will discover that policies conflict with practical implementation constraints, requiring redesign under pressure.
**Fix direction:** Write executable schemas (Pydantic models) as the first implementation deliverable, before any endpoint calls.

### SW-02: Config-discovery gap
**Description:** `tools/llm/endpoints.yaml` exists with static endpoint configs. The model discovery policy says "probe /v1/models dynamically." These two mechanisms aren't connected. Which one is authoritative? What if they disagree?
**Fix direction:** Define endpoints.yaml as the static fallback and discovery as the live override, with reconciliation rules.

### SW-03: Telemetry gap
**Description:** Three telemetry designs coexist: (1) existing AI usage ledger (reports/ai/*.jsonl), (2) planned local JSONL spool (.local/ai/llm-logs/), (3) Agent Metrics Google Sheet. No unified lifecycle connects them.
**Fix direction:** Define one telemetry lifecycle: local record -> aggregate -> post to Agent Metrics -> mark as posted. Existing ledger format becomes input to the new system, not a separate product.

### SW-04: Retrieval/index lifecycle gap
**Description:** Index creation, refresh, stale detection are described. Index migration, corruption recovery, partial rebuild, and cross-version compatibility are not.
**Fix direction:** Add failure modes to the index lifecycle. Define what "rebuild" means when the embedding model is no longer available.

### SW-05: Artifact authority gap
**Description:** AI artifact lifecycle (12 states) and project gate lifecycle (11 gates) are separate authority models with no integration spec.
**Fix direction:** Define a mapping: which artifact states are required/forbidden at each gate transition. Make the artifact lifecycle a sub-model of the gate lifecycle, not a parallel one.

### SW-06: Prompt/task contract gap
**Description:** Contracts are described as "Pydantic models" but no model definitions exist. No field names, types, validation rules, or default values are specified. Implementation will require design decisions not captured in the plan.
**Fix direction:** Publish at minimum the Pydantic model field lists as YAML schemas in the plan, even if the Python code doesn't exist yet.

### SW-07: Evaluation gap
**Description:** Golden evals are mentioned but no golden dataset exists. No eval methodology is defined. No pass/fail thresholds are specified. No baseline measurements exist.
**Fix direction:** Define what "golden eval" means for each synthesis task type. Create at least one golden eval fixture from existing verified facts before implementation.

### SW-08: Parallel sprint state drift gap
**Description:** Path-based isolation doesn't prevent state drift. If an AI sprint and a non-AI sprint both modify plans/master-plan.md, the merge order determines which state is authoritative. No merge conflict resolution protocol exists.
**Fix direction:** Define which sections of shared files are owned by which sprint type. Use section-level ownership, not file-level.

### SW-09: Dependency/version governance gap
**Description:** LiteLLM, Pydantic v2, LlamaIndex, LanceDB are recommended but no version pins exist. No requirements.txt with pinned versions. No lock file strategy. No upgrade/compatibility testing plan.
**Fix direction:** Pin exact versions in the plan. Define an upgrade verification protocol.

### SW-10: Evidence bundle integration gap
**Description:** Evidence bundles forbid `embeddings/**` and `*.faiss` (base-run.yaml). But the AI platform will produce artifacts that should be in bundles (telemetry summaries, model discovery results, eval reports). No evidence contract template for AI sprints exists.
**Fix direction:** Create an AI sprint evidence contract template that includes AI-specific required metadata files.
