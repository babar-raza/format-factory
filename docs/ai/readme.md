# Format Factory AI / Agentic Direction — Consolidated Context, Requirements, and Verification Items

## 1. Purpose of this document

This document converts the raw discussion into a reusable project context for the Format Factory project. It is intended to be referenced repeatedly when planning, reviewing evidence, writing agent prompts, validating sprint results, or deciding whether the project is still aligned with the original goal.

The document is not a sprint prompt. It is a consolidated specification and requirements context.

It captures:

* What the project is supposed to become.
* Why AI, embeddings, LLMs, and agentic workflows are needed.
* How AI must be controlled so it accelerates the work without becoming an untrusted authority.
* What evidence is required to prove progress.
* What verification items must exist before the project can claim meaningful product progress.
* How VS Code agents should execute under supervision.
* What “back to the original plan” means for this project.

## 2. Source basis and limitations

This context is based on the raw discussion between the user and the LLM, plus the continuing Format Factory project direction already established in prior project discussions.

Important limitation: the raw discussion mentions an attached source archive, but this document does not claim to inspect that archive unless a specific evidence bundle or source archive is later reviewed. This document captures intent, requirements, governance, and verification expectations.

## 3. Core project understanding

Format Factory is a governed, evidence-driven system for building robust support for file formats, especially formats that are not already fully covered by commercial products or existing high-level libraries.

The goal is not merely to experiment with parsers. The goal is to create a repeatable product pipeline that can move selected formats from discovery to specification understanding, implementation, validation, and eventually product-quality delivery.

The original direction is still valid:

* Start with controlled foundations.
* Use official specifications and verified facts.
* Build deterministic parsing and neutral models.
* Add tests, gates, evidence bundles, and independent verification.
* Use AI only when it can be governed, checked, and constrained.
* Prove the system through real format pilots.

The user accepts that the original plan correctly delayed heavy LLM use until a stronger foundation existed. However, the design for introducing LLMs and embeddings now needs to be refined and made concrete, because without AI acceleration the project will become too slow and tedious to reach tangible product results.

## 4. User’s core requirement

The user wants the project to move to the next level from an AI perspective.

AI, embeddings, LLMs, agentic workflow, skills, and other agentic-app capabilities must be used to reduce tedious manual work while preserving strict control, consistency, repeatability, and production safety.

The user wants the assistant to drive the project at the reasoning and planning level, while weaker VS Code agents execute the work on the assistant’s behalf.

The assistant is expected to:

* Understand the repository and governance deeply.
* Refine designs before execution.
* Write detailed, executable prompts for VS Code agents.
* Require agents to produce evidence bundles.
* Review those evidence bundles before accepting work.
* Plan follow-up sprints based on evidence and logic.
* Keep the project aligned with the original end goal.

## 5. End goal

The immediate strategic end goal is to prove the Format Factory system with three XML-style format pilots.

These pilots should all be XML-style source formats, but they must provide different features and stress different capabilities of the pipeline.

The pilots should demonstrate that the system can:

* Acquire and cache official format knowledge.
* Normalize and index specification content.
* Extract verified facts and implementation requirements.
* Build parsers and neutral models.
* Use AI to accelerate controlled tasks.
* Validate AI outputs against source-grounded evidence.
* Produce repeatable implementations and tests.
* Generate evidence bundles strong enough for independent review.
* Move toward real product delivery rather than endless planning.

A later product-level target is to take at least two products to Python and .NET delivery quality, but the immediate proof target remains the three XML-style pilots.

## 6. What “AI acceleration” means in this project

AI acceleration does not mean letting an LLM freely design, code, or declare success.

AI acceleration means using LLMs, embeddings, retrieval, synthesis, and agentic workflows to reduce tedious work in controlled places where the outputs can be checked.

Examples of appropriate AI acceleration:

* Summarizing specification sections into structured candidate facts.
* Producing draft implementation requirements from verified spec chunks.
* Suggesting parser strategies from source-grounded facts.
* Comparing implementation behavior against requirements.
* Finding inconsistencies between plans, taskcards, evidence, and code.
* Drafting test cases from verified requirements.
* Helping classify format features and risk surfaces.
* Creating initial code scaffolds that are then validated by deterministic tests.
* Assisting in evidence review, not replacing it.

Examples of inappropriate AI use:

* Treating LLM output as authoritative without provenance.
* Allowing uncited claims into verified facts.
* Letting LLMs bypass gates, tests, taskcards, or evidence requirements.
* Using broad live model calls without contracts, schemas, or redaction controls.
* Mixing format vector stores or embeddings across unrelated formats without isolation.
* Claiming product readiness based on static inspection or narrative summaries only.
* Calling a pipeline “AI-powered” when it only runs deterministic fixtures.

## 7. AI must be an accelerator, never the authority

The controlling principle is:

> AI may propose, summarize, classify, draft, compare, and accelerate. It must not be the final authority.

Final authority must come from:

* Official specifications.
* Source-grounded citations.
* Deterministic validators.
* Tests.
* Pipeline execution.
* Evidence bundles.
* Independent verification.
* Human-approved gates where external authority is required.

Every AI-generated artifact that influences implementation must be traceable to source evidence and must pass validation.

## 8. Current state from requirement perspective

From the project direction and evidence history, the project has built meaningful governance foundations, but it has not yet fully reached the user’s desired AI-assisted product velocity.

### 8.1 What appears aligned with the original plan

The project direction remains aligned where it emphasizes:

* Governed acquisition.
* Format-specific pipelines.
* Specification provenance.
* Evidence bundles.
* Gate-based progression.
* Parser and neutral model development.
* Independent verification.
* Avoiding uncontrolled LLM authority.

### 8.2 What remains insufficient

The user’s concern is valid: after many rounds, the results can feel non-tangible if the system is mostly building governance, plans, and deterministic scaffolding without using AI to speed up the hard parts.

The major remaining gaps are:

* AI is not yet deeply integrated into the productive pipeline.
* Embeddings and retrieval are not yet fully established as reusable project-local assets.
* LLM synthesis is not yet consistently source-grounded, schema-constrained, and validator-enforced.
* Agentic workflows are not yet reliably producing end-to-end format delivery results.
* Evidence sometimes proves local progress but not full product readiness.
* Some sprints may overclaim closure without enough actual executable pipeline proof.
* The system must prove itself through real format pilots, not just architecture documents.

### 8.3 What “not yet back to original plan” means

The project is only fully back to the original plan when it can show real, evidence-backed movement from format understanding to implemented product capability.

The project is not fully back to the original plan if it only produces:

* Plans without executable implementation.
* AI architecture without working AI pipeline proof.
* Evidence bundles without clean commits and reproducible tests.
* Static summaries without end-to-end pipeline execution.
* Isolated components that do not integrate into the format delivery flow.

## 9. Required operating model

The user wants the assistant to own the thinking and strategy, while VS Code agents execute detailed instructions.

This means agent prompts must be:

* Governance-first.
* Evidence-first.
* Plan-aware.
* Memory-aware.
* Repository-aware.
* Self-managed but bounded.
* Multi-lane where safe.
* Explicit about stop conditions.
* Explicit about what not to touch.
* Explicit about evidence bundle requirements.

Agents should not be asked to “figure it out” vaguely. They should receive precise instructions, with enough autonomy to make routine execution decisions without blocking the sprint.

## 10. Sprint execution philosophy

The preferred sprint structure is a controlled mega-train sprint with multiple lanes where safe.

Each lane should have:

* A named purpose.
* A lane manager role.
* File ownership boundaries.
* Stop conditions.
* Acceptance criteria.
* Required evidence.
* Integration responsibility.

The coordinator must:

* Run preflight state checks.
* Detect overlapping file ownership.
* Maintain taskcards and status.
* Keep TODOs updated.
* Verify that lane outputs do not conflict.
* Produce a final evidence bundle.
* Report the absolute evidence bundle path.

## 11. Governance requirements

### FF-GOV-001 — Evidence before acceptance

No sprint result may be accepted based only on a final summary. Every important claim must be backed by evidence artifacts.

Verification items:

* Evidence bundle exists.
* Evidence bundle path is absolute.
* Bundle includes manifest/hash records.
* Bundle includes before/after state.
* Bundle includes command logs.
* Bundle includes test outputs.
* Bundle includes final git status.
* Bundle includes final verdict.
* Bundle includes taskcard state.

### FF-GOV-002 — Clean closure requirement

A sprint cannot be treated as cleanly closed if source changes remain dirty, untracked, contradictory, or uncommitted without explicit classification.

Verification items:

* `git status` before and after captured.
* All dirty files classified.
* Owned verified changes committed or intentionally left uncommitted with reason.
* Untracked files are either committed, ignored, archived, or removed.
* Final status is clean unless there is an explicit governed exception.

### FF-GOV-003 — No blind claims

Agents must not claim a pipeline works unless they executed it or clearly identify that the claim is based on static inspection only.

Verification items:

* Real commands captured.
* Real outputs captured.
* Exit codes captured.
* Logs captured.
* Artifacts captured.
* Static-only findings labeled as static-only.

### FF-GOV-004 — Taskcard-driven state

Every actionable item must be represented as a taskcard or equivalent governed state item.

Verification items:

* Taskcard exists for each actionable unit.
* Taskcard has owner/lane.
* Taskcard has status.
* Taskcard has acceptance criteria.
* Taskcard has evidence references.
* Closed taskcards have closeout proof.

### FF-GOV-005 — No evidence contamination

Evidence bundles must not mix unrelated sprint identities or stale reports in a way that makes closure ambiguous.

Verification items:

* Bundle identity matches sprint identity.
* Metadata files agree on run ID and sprint ID.
* Final verdict matches evidence contents.
* No contradictory stale report is included without being explicitly labeled as historical context.

### FF-GOV-006 — Agent actions on human’s behalf

Where governance allows, agents should perform human-review/manual steps themselves using approved local mechanisms. The human should only be treated as a blocker for external credentials, explicit production approval, destructive operations, or decisions outside granted authority.

Verification items:

* Prompt delegates routine decisions to agents.
* Prompt identifies true external blockers only.
* Prompt prevents unnecessary human waiting.
* Prompt requires escalation only for explicit approval gates.

## 12. AI architecture requirements

### FF-AI-001 — Controlled gateway

All LLM calls must go through a governed gateway layer.

Requirements:

* Centralized provider routing.
* Explicit model selection.
* No accidental direct provider fallback.
* Redacted logs.
* Token and call accounting.
* Failure modes classified.
* Deterministic fallback only when clearly labeled as fallback.

Verification items:

* Gateway implementation exists.
* Tests cover allowed provider routes.
* Tests cover missing credential behavior.
* Tests cover blocked provider behavior.
* Logs redact secrets.
* Evidence records model, provider, tokens, and call count without secrets.

### FF-AI-002 — Source-grounded synthesis

LLM synthesis must be grounded in retrieved source chunks and must produce structured output with provenance.

Requirements:

* Inputs must include cited source chunks or verified facts.
* Output must include provenance references.
* Output must conform to schema.
* Unsupported claims must be rejected or labeled as unverified.
* Contradictions must be detected and handled.

Verification items:

* Schema validation tests.
* Citation/provenance validation tests.
* Unsupported-claim rejection tests.
* Contradiction detection tests.
* Live or fixture pipeline proof showing source-grounded synthesis.

### FF-AI-003 — AI cannot directly promote authority

AI-generated output must not automatically become verified facts, requirements, implementation decisions, or product-readiness claims.

Requirements:

* AI output starts as draft authority.
* Promotion requires validators and evidence.
* Promotion events are recorded.
* Rejected AI outputs are retained as evidence only where useful.

Verification items:

* Authority status model exists.
* Tests prove draft outputs cannot bypass validation.
* Evidence shows promotion path from draft to verified.

### FF-AI-004 — Prompt contracts

Every AI task must have a defined prompt contract.

Requirements:

* Task purpose.
* Allowed inputs.
* Required output schema.
* Required citations.
* Forbidden claims.
* Failure behavior.
* Validation rules.

Verification items:

* Prompt contract files exist.
* Prompt contract tests exist.
* Invalid model output fails validation.
* Missing citation fails validation where citations are required.

### FF-AI-005 — Model capability discovery

The system should discover and record available LLM and embedding models, but discovery is not the same as authorization to use every model.

Requirements:

* Capability discovery is recorded.
* Model use is governed by policy.
* Unsupported or unauthorized models are blocked.
* Model selection is justified by task type.

Verification items:

* Discovery artifact exists.
* Policy artifact exists.
* Tests cover unsupported model rejection.
* Evidence records chosen model and reason.

### FF-AI-006 — Isolated and pipeline verification

AI must be verified both in isolation and inside the full pipeline.

Verification items:

* Gateway unit tests pass.
* Retrieval unit tests pass.
* Synthesis unit tests pass.
* Validation unit tests pass.
* End-to-end AI pipeline proof exists.
* Format delivery pipeline proof exists with AI-enabled step.

## 13. Embedding and retrieval requirements

### FF-EMB-001 — Format-segregated stores

Vector stores and embedding indexes must be segregated by format and version.

Requirements:

* No cross-format contamination.
* Format/version identity included in index metadata.
* Rebuilds are reproducible.
* Source hashes are recorded.
* Stale indexes are invalidated.

Verification items:

* Per-format index paths.
* Manifest with format/version/source hashes.
* Tests prevent cross-format retrieval leakage.
* Rebuild verification proof.

### FF-EMB-002 — Project-local permanent stores

Embeddings should be reusable project-local assets, not temporary one-off outputs.

Requirements:

* Stored under governed local/project paths.
* Large binary/vector content excluded from evidence bundles unless explicitly authorized.
* Manifests and hashes included in evidence.
* Rebuild instructions exist.

Verification items:

* Storage policy exists.
* `.gitignore` or equivalent policy exists for bulky local assets.
* Manifest artifact exists.
* Evidence includes metadata, not raw full vector DB dumps.

### FF-EMB-003 — Retrieval quality must be tested

Retrieval must be meaningful, not just matching broad terms like a format name.

Requirements:

* Queries must target specific requirements/features.
* Retrieval must rank relevant chunks above irrelevant chunks.
* Tests must include positive and negative retrieval cases.
* Evidence must show returned and excluded chunks.

Verification items:

* Retrieval fixture corpus exists.
* Retrieval quality tests exist.
* Pipeline report includes query, selected chunks, excluded chunks, and scores.

## 14. Specification management requirements

### FF-SPEC-001 — Local-first immutable spec cache

Official specifications and source references must be cached in an immutable local-first layer.

Requirements:

* Source URL or acquisition method recorded.
* Hash recorded.
* Retrieval date recorded.
* Format/version recorded.
* Normalized text/pages produced.
* Section/page/chunk indexes produced.

Verification items:

* Spec cache manifest exists.
* Hash checks pass.
* Normalized text exists.
* Index exists.
* Tests prove lookup and provenance.

### FF-SPEC-002 — Verified facts layer

The system must maintain verified facts derived from official sources.

Requirements:

* Fact text.
* Source reference.
* Confidence/authority level.
* Format version.
* Related implementation requirement.
* Validation status.

Verification items:

* `verified-facts` artifact exists.
* Each fact cites source location.
* No fact without source can be marked verified.
* Tests enforce source requirement.

### FF-SPEC-003 — Implementation requirements layer

The system must transform verified facts into implementation requirements.

Requirements:

* Requirement ID.
* Requirement statement.
* Source fact references.
* Affected parser/model/exporter/tests.
* Acceptance criteria.
* Test mapping.

Verification items:

* Requirements artifact exists.
* Each requirement maps to verified facts.
* Each requirement maps to at least one test or explicit deferred reason.

## 15. Format pipeline requirements

### FF-FMT-001 — Repeatable acquisition pipeline

Each format must pass through repeatable acquisition, not ad hoc manual research.

Verification items:

* Acquisition pack exists.
* Source manifest exists.
* License/source suitability recorded.
* Gate status recorded.

### FF-FMT-002 — Parser strategy artifact

Each format must have a parser strategy before implementation is considered complete.

Requirements:

* Format structure summary.
* Required parser behaviors.
* Edge cases.
* Security considerations.
* Unsupported/deferred features.

Verification items:

* Parser strategy file exists.
* Strategy maps to requirements.
* Tests cover strategy decisions.

### FF-FMT-003 — Neutral model artifact

Each implemented format must produce or consume a neutral model where appropriate.

Verification items:

* Neutral model schema exists.
* Parser produces neutral model.
* Tests validate neutral model output.
* Round-trip or import/export behavior is defined where applicable.

### FF-FMT-004 — Product-readiness artifact

Each format must eventually have product-readiness status.

Requirements:

* Supported features.
* Unsupported features.
* Security risks.
* Test coverage.
* Known limitations.
* Publication readiness.

Verification items:

* Product-readiness file exists.
* Status is not `ready` without passing gates.
* Evidence links to test results and implementation proof.

## 16. Three-pilot proof requirement

### FF-PILOT-001 — Three XML-style pilots

The project must prove the system using three XML-style format pilots.

Requirements:

* All three formats are XML-style sources.
* Each pilot stresses different features.
* Each pilot has acquisition, spec, requirements, parser/model, tests, and evidence.
* At least one AI-assisted step is proven in each pilot or explicitly justified if deferred.

Verification items:

* Pilot selection rationale.
* Feature differentiation matrix.
* Per-pilot evidence bundle.
* Cross-pilot comparison report.
* End-to-end pipeline proof.

### FF-PILOT-002 — Tangible result definition

A pilot is tangible only if it produces executable results.

A pilot is not tangible if it only produces planning docs.

Verification items:

* Source parser or equivalent implementation exists.
* Tests execute successfully.
* Sample files are processed.
* Output artifacts are validated.
* Requirements are traced to implementation and tests.

## 17. Product delivery requirements

### FF-PROD-001 — Python and .NET delivery path

The project must move toward real product delivery for at least two products across Python and .NET.

Requirements:

* Packaging strategy.
* API surface strategy.
* Tests in both ecosystems.
* Installed-package verification.
* Publication dry-run before live publication.

Verification items:

* Python package dry-run evidence.
* .NET package dry-run evidence.
* Installed package tests.
* API documentation draft.
* Publication gate status.

### FF-PROD-002 — Commercial/product readiness must not be overclaimed

Commercial or product readiness cannot be claimed until all required gates, tests, packaging checks, and evidence reviews pass.

Verification items:

* Product readiness remains false until proven.
* Publication remains blocked unless approval gates pass.
* Evidence explicitly separates local readiness, dry-run readiness, and live publication readiness.

## 18. Agentic workflow requirements

### FF-AGENT-001 — Assistant-owned reasoning, agent-executed work

The assistant owns hard reasoning, strategy, review, and next-step planning. VS Code agents execute detailed prompts.

Requirements:

* Prompts must include context, goals, constraints, files to inspect, gates, evidence, stop conditions, and final reporting requirements.
* Agents must not invent missing context.
* Agents must inspect repo state before modifying files.
* Agents must update TODOs/taskcards continuously.

Verification items:

* Prompt includes preflight section.
* Prompt includes execution lanes.
* Prompt includes evidence requirements.
* Prompt includes final response format.

### FF-AGENT-002 — Multi-lane execution with coordination

Where safe, sprints should use multiple lanes to increase progress without bypassing governance.

Verification items:

* Lane table exists.
* File ownership map exists.
* Overlap checks performed.
* Coordinator integration report exists.
* Lane outputs reconciled before final verdict.

### FF-AGENT-003 — Self-governed lane managers

Lane managers may make routine decisions on the human’s behalf within the defined sprint scope.

Verification items:

* Lane stop conditions distinguish routine decisions from true blockers.
* Human approval required only for credentials, external publication, destructive changes, or explicit approval gates.

## 19. Evidence bundle requirements

Every meaningful sprint must produce an evidence bundle.

Minimum required contents:

* Evidence index.
* Sprint identity metadata.
* Preflight report.
* Git status before.
* Git status after.
* Branch and HEAD proof.
* Commit log proof.
* Taskcard state before and after.
* Implementation summary.
* Test command logs.
* Test outputs.
* Pipeline execution logs.
* AI call ledger if AI was used.
* Token/API call counts if LLMs were used.
* Redaction proof.
* Bundle manifest with hashes.
* Final verdict.
* Known caveats and blockers.
* Absolute bundle path in final agent response.

## 20. Verification matrix

| Area              | Required proof                           | Failure condition                                 |
| ----------------- | ---------------------------------------- | ------------------------------------------------- |
| AI gateway        | Unit tests, config proof, redacted logs  | Direct ungoverned provider call or secret leakage |
| LLM synthesis     | Schema output, citations, validator pass | Unsupported claims marked verified                |
| Embeddings        | Per-format store manifest, leakage tests | Cross-format contamination                        |
| Retrieval         | Positive/negative relevance tests        | Retrieval only matches broad format name          |
| Spec cache        | Hashes, normalized text, index           | Untracked or unverifiable source facts            |
| Verified facts    | Source-linked fact records               | Fact marked verified without source               |
| Requirements      | Trace to facts and tests                 | Requirement without evidence or test/defer reason |
| Parser            | Executable implementation and tests      | Static-only implementation claim                  |
| Pipeline          | End-to-end run logs and artifacts        | Only isolated unit tests for pipeline claim       |
| Product readiness | Package dry-runs and installed tests     | Readiness claimed from planning docs              |
| Evidence          | Complete bundle with clean identity      | Mixed sprint identity or missing core logs        |
| Closure           | Clean or classified git state            | Dirty/untracked files left unexplained            |

## 21. Required status vocabulary

The project should use precise status labels to prevent overclaiming.

Recommended statuses:

* `NOT_STARTED`
* `PLANNED`
* `IN_PROGRESS`
* `STATIC_REVIEWED`
* `IMPLEMENTED_NOT_VALIDATED`
* `ISOLATION_VALIDATED`
* `PIPELINE_VALIDATED`
* `PILOT_VALIDATED`
* `DRY_RUN_READY`
* `PUBLICATION_BLOCKED_PENDING_APPROVAL`
* `PRODUCT_READY`
* `BLOCKED`
* `DEFERRED_WITH_REASON`
* `REJECTED`

Forbidden or risky status behavior:

* Calling something complete when only static inspection passed.
* Calling something product-ready when only local tests passed.
* Calling something AI-integrated when it uses fixture-only deterministic synthesis.
* Calling something closed when evidence bundle identity is contradictory.

## 22. Design refinement requirements for AI implementation

The AI design must include more than tests and evidence. It must include:

* Contracts.
* Schemas.
* Task state.
* Validators.
* Gates.
* Check-and-balance reviews.
* Engineering guardrails.
* Format/version isolation.
* Telemetry.
* Redaction.
* Authority promotion rules.
* Failure classification.
* Reproducible replay.

## 23. Telemetry requirements

The canonical telemetry sink for LLM usage should be the existing Agent Metrics system, not a reinvention.

Local JSONL or OpenTelemetry-style ledgers may exist as local spool/evidence/replay, but they should not replace the established Agent Metrics product.

Verification items:

* Local AI call ledger exists.
* Token counts recorded.
* API call counts recorded.
* Agent Metrics payload schema compatible.
* Production posting controlled by policy.
* No secrets logged.

## 24. Redaction and content minimization requirements

AI artifacts and telemetry must avoid leaking secrets or unnecessary raw source content.

Requirements:

* Secrets redacted.
* Raw full spec chunks excluded from external telemetry.
* Evidence bundles include enough provenance to verify, but not large raw caches unless authorized.
* Source excerpts minimized where possible.

Verification items:

* Redaction tests.
* Evidence bundle scan.
* Telemetry artifact review.
* No secret values in logs.

## 25. What the next AI-focused design should produce

A proper AI design sprint should produce the following artifacts:

* AI architecture overview.
* AI task catalog.
* Prompt contract registry.
* Model/provider policy.
* Gateway schema.
* Retrieval schema.
* Synthesis schema.
* Authority model.
* Validation pipeline.
* Telemetry design.
* Embedding/vector store policy.
* Format-isolation rules.
* Evidence contract updates.
* Test plan.
* Pilot integration plan.

## 26. What the next implementation sprint should prove

The next meaningful implementation sprint should not merely add documents. It should prove at least one AI-assisted flow end-to-end.

Minimum proof:

* Select one XML-style pilot format.
* Retrieve format-specific spec chunks.
* Use governed LLM synthesis to produce draft facts or requirements.
* Validate citations and schema.
* Promote only validated outputs.
* Feed promoted outputs into a parser/test requirement artifact.
* Run isolation tests.
* Run the relevant pipeline step.
* Capture evidence bundle.

## 27. Acceptance criteria for “AI is working as planned”

AI can be considered working as planned only when all of the following are true:

1. AI calls go through the governed gateway.
2. Model/provider choice is explicit and policy-compliant.
3. Retrieval is format-isolated and meaningful.
4. LLM output is schema-constrained.
5. LLM output includes provenance.
6. Unsupported claims are rejected or labeled unverified.
7. Contradictions are detected.
8. Draft AI output cannot become verified authority without validation.
9. The AI flow runs in isolation.
10. The AI flow runs inside the format pipeline.
11. Evidence captures commands, logs, artifacts, token counts, and verdicts.
12. The result advances a real format pilot toward implementation or product delivery.

## 28. Acceptance criteria for “back to the original plan”

The project is back to the original plan when:

* Governance remains intact.
* AI acceleration is controlled and productive.
* Three XML-style pilots are progressing through real executable pipelines.
* Verified facts and requirements drive implementation.
* Parser/model/package work produces tangible outputs.
* Evidence bundles are clean, reproducible, and reviewable.
* Product-readiness claims are conservative and proven.
* Agents execute on the assistant’s detailed direction rather than drifting into shallow closure work.

The project is not yet back to the original plan if:

* The AI system is mostly architecture without pipeline proof.
* Evidence bundles are incomplete or contradictory.
* Sprints close documentation but do not advance pilots.
* Product delivery remains theoretical.
* LLM outputs are not source-grounded and validator-controlled.

## 29. Non-goals and boundaries

The following are not acceptable shortcuts:

* Uncontrolled LLM use.
* Overwriting governance to make tests pass.
* Treating AI output as verified fact.
* Mixing vector stores across formats.
* Ignoring evidence bundle problems.
* Claiming completion from summaries.
* Skipping parser tests.
* Skipping pipeline proof.
* Publishing packages without approval gates.
* Logging secrets or full sensitive source content.

## 30. Reusable instruction to agents

Agents working on this project must operate under the following standing instruction:

> You are executing on behalf of the assistant and the human. The assistant owns the hard reasoning, strategy, and acceptance review. You must inspect the current repository state, governance files, plans, taskcards, evidence rules, and relevant prior artifacts before acting. You may make routine execution decisions within the prompt’s scope, but you must not bypass tests, validators, gates, or evidence requirements. Use AI as an accelerator only where governed by contracts, schemas, validators, provenance, and authority rules. Produce a complete evidence bundle and include its absolute path in your final response.

## 31. Reusable review checklist

When reviewing any future sprint evidence, check:

1. Does the evidence bundle exist and have a clear identity?
2. Does the final summary match the actual evidence?
3. Are commits present and consistent with claimed work?
4. Is final git state clean or fully classified?
5. Were tests actually run?
6. Was the changed component tested in isolation?
7. Was the changed behavior tested in the pipeline?
8. Did AI calls, if any, go through the governed gateway?
9. Were token counts and API call counts recorded?
10. Were outputs source-grounded and schema-validated?
11. Did the work advance a real pilot or only update planning docs?
12. Are product-readiness claims conservative?
13. Are there blockers that must be corrected in the next prompt?
14. Is a next prompt required immediately after review?

## 32. Final project direction statement

Format Factory should become a governed AI-assisted format engineering pipeline.

It should combine deterministic engineering discipline with controlled AI acceleration.

The project should not become a loose LLM experiment, and it should not remain a slow manual pipeline that never reaches tangible product results.

The correct path is:

1. Preserve the strong governance foundation.
2. Introduce AI through controlled gateways, contracts, schemas, validators, and evidence.
3. Build reusable format-specific retrieval and embedding assets.
4. Convert official specs into verified facts and implementation requirements.
5. Drive three XML-style pilots through executable implementation proof.
6. Move selected products toward Python and .NET delivery with conservative readiness claims.
7. Use evidence bundles and independent review to prevent drift and overclaiming.

This is the context future prompts, reviews, and sprint plans should follow.
