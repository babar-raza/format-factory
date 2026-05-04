---
memory_package: format-factory-chat-memory
version: 1.0
created_at: 2026-05-03
intended_location: /memory
source: ChatGPT conversation memory plus inspected Phase 0 evidence bundles through run013
visibility: internal
publish_allowed: false
notes: Place this folder at repo root as /memory. These files are for agent context and must not supersede plans/master-plan.md.
---

# 04 — Phase 0 Evolution and Bundle Reviews

This file explains how the plan evolved through repeated bundle inspections.

## Starting point

The repo began as a greenfield project named `format-factory`, with only a one-line README and no tooling or structure.

Initial architectural planning created a broad foundation:

- governance files
- docs
- registry skeleton
- scoring model
- acquisition pack templates
- taskcards
- local evidence bundle rules
- product track separation

## v1 plan issue

The first architecture plan mixed foundation work and FODS pilot work.

Problem:

- It said not to create format-specific acquisition packs yet.
- It also implied FODS scoring/spec evidence was required before execution.

Fix:

- Split work into Phase 0 foundation, Phase 1 pilot scoring, Phase 2 evidence, Phase 3 prototype, Phase 4 product implementation.

## v2 hardened plan

v2 fixed phase confusion and added:

- Python 3.11+ baseline instead of using installed Python 3.13 as package minimum.
- net8.0/net10.0 strategy instead of net9.0.
- no `src/dotnet/commercial/` in Phase 0.
- no `.github/workflows/` in Phase 0.
- gap/risk/decision registers with owners, severity, triggers.

## v3 architecture additions

The human added new requirements:

- master plan must be living and reproducible.
- Claude in VS Code is primary executor.
- Codex is optional reviewer/executor.
- LLM endpoint communication must support `llm.professionalize.com` and local discoverable models.
- everything useful must persist on disk.
- release control must explicitly decide what becomes open source.

v3 added:

- Agent Operations Layer
- Commands and Skills Governance
- LLM Endpoint and Model Strategy
- Persistent Artifact Model
- Reuse, Cache, and Idempotency Strategy
- Open-Source Release Control Layer
- Artifact Visibility and Release Manifest Schema

## run001 foundation execution

The agent created the initial Phase 0 files and evidence bundle.

External inspection found issues:

- missing audit files
- malformed `ocal/` path in bundle
- visibility classification inconsistency
- `.claude/settings.json` too broad

## run002 healing

run002 fixed:

- missing audit files
- malformed bundle path
- visibility policy via hybrid classification
- conservative Claude settings

Bundle structure became clean.

## run003 master plan canonicalization

The master plan was rewritten to be more complete. However, follow-up review still found it did not contain all project memory and all standing rules.

## run004 governance sync

Governance files were synchronized against the canonical master plan.

External inspection found:

- Phase 1 still had an ambiguity around `acquisition-packs/fods/`.
- The scoring model contained FODS pre-score language.

## run005 final consistency healing

run005 fixed much of this:

- Phase 1 split into 1A/1B.
- scoring model hardened to 7-factor/100-point model.
- FODS pre-scoring removed from scoring files.

External inspection still found missed contradictions in `plans/master-plan.md`.

## run006 contradiction cleanup

run006 fixed:

- `acquisition-packs/fods/` boundary in master plan.
- live numeric FODS pre-score references.

External inspection then found product implementation gate ambiguity.

## run007 product gate semantics

run007 clarified:

- Gate 9 authorizes implementation planning, not product source.
- explicit Phase 4 prompt authorizes OSS source after Gate 9 approval.
- Gate 10 is OSS release readiness.
- commercial source requires Gate 10, DD3, commercial taskcards, and explicit prompt.
- Gate 11 is commercial release readiness.

## run008 specification cache amendment

The human added a major requirement:

- standardized format specs and related official/public materials must be fetched systematically, saved on disk, indexed, and reused locally.

run008 added:

- `docs/specification-cache.md`
- `tools/spec-cache/_readme.md`
- `taskcards/TC-0007-specification-cache.md`
- spec-cache architecture in master plan and docs
- local-only default storage under `.local/spec-cache/`
- no spec downloads in Phase 0

run008 also cleaned residual historical pre-score language and residual commercial-folder gate annotations.

## run009 spec-cache governance cleanup (main execution stream)

run009 is a continuation of the main execution stream. It addressed issues found during human inspection of the run008 bundle.

Fixes applied:

- TC-0007 corrected: spec-cache is generic tooling that applies to all formats, not FODS-specific. TC-0007 title and scope updated accordingly.
- Authorization model added: spec downloads require explicit prompt authorization before any fetch occurs. Agents must never self-authorize a download.
- Stop-log-gap model defined: if a spec is missing or stale, the agent must stop, log a gap in the Gap Register, create a taskcard if needed, and wait for human authorization. No automatic downloads.
- Spec-cache architecture in master plan updated to reflect the authorization model.

run009 is the main execution stream counterpart to run010 (memory integration stream). Both run concurrently and must be reconciled before Phase 1.

## run010 memory integration (memory stream)

run010 is the memory integration stream for Phase 0. It addressed the absence of any `/memory` guidance in `AGENTS.md`.

Changes applied:

- AGENTS.md pre-existing structural bug fixed: duplicate Section Q (Security Rules using P1-P4 IDs, Acquisition Workflow Rules also labeled Q). Security Rules IDs corrected to Q1-Q4. Acquisition Workflow Rules renamed to Section R. What This Document Does Not Cover renamed to Section S. Specification Cache Rules renamed to Section T with all internal IDs updated.
- AGENTS.md Section I (Self-Challenge) extended from 10 to 14 questions. Questions 11-14 cover memory usage, authority, contradiction logging, and maintenance triggers.
- AGENTS.md Section S (What This Document Does Not Cover): memory cross-reference line added.
- AGENTS.md Section U (Memory Usage and Maintenance) added with subsections U1-U9.
- GOVERNANCE.md Section 1.2 extended: memory is not operational authority; contradictions must be logged.
- GOVERNANCE.md Section 1.2a added: memory content restrictions for human contributors.
- plans/master-plan.md updated to v2.7: new decisions DEC-028/DEC-029/DEC-030, gaps G-017/G-018, healing gap G-HEAL-014 resolved, risks R-019/R-020/R-021, Section 35 Memory Layer added.
- TC-0008 (planned /sync-memory command) created as not_started Phase 1+ taskcard.

## run012 memory sync (memory stream)

run012 is a memory stream sync run. It updated `/memory` files to reflect the post-run009/run010 state and captured a new human expectation about product source layout.

Human expectation captured:

- `src/net/{format}` is the intended .NET product workspace (e.g., `src/net/odp/`)
- `src/python/{format}` is the intended Python FOSS product workspace (e.g., `src/python/odp/`)

This expectation is **not yet propagated to `plans/master-plan.md`** (still v2.7, still uses old layout). An agent must not create source folders until the master plan explicitly authorizes the layout.

Additional principles captured in run012:

- Repeatability matters more than rushing. Every format must be processable through the same 11-gate pipeline.
- Agentic workflow routes: Claude Code (primary), Codex (optional), Ollama/local LLMs, `llm.professionalize.com`, keys via system environment.
- run009 and run010 are concurrent but distinct streams that must be reconciled by run011.

## run011 product source layout reconciliation (main execution stream)

run011 propagated the format-first source layout expectation into `plans/master-plan.md` and all canonical governance docs.

Changes applied in run011:

- `plans/master-plan.md` updated to v2.8: product source layout section updated to `src/net/{format}/` and `src/python/{format}/`. Old paths (`src/dotnet/`, `src/python/open-source/`) marked obsolete.
- `docs/architecture.md` updated: source layout section updated.
- `docs/product-tracks.md` updated: track descriptions updated to use format-first layout.
- `AGENTS.md` updated: forbidden path rules reflect format-first layout.
- `GOVERNANCE.md` updated: source layout references updated.
- DEC-033 recorded: .NET FOSS packaging deferred — whether `src/net/{format}/` produces a separate Apache 2.0-licensed NuGet package is not yet decided; must resolve before Gate 10 .NET release.

## run013 source-layout verification and memory reconciliation (main execution stream)

run013 verified that run011's propagation was complete and removed stale "pending propagation" notes from `/memory` files.

Changes applied in run013:

- `plans/master-plan.md` updated to v2.9: run012 (memory stream) and run013 recorded in run history.
- `docs/release-control.md` Last reviewed date updated to 2026-05-04.
- `docs/llm-endpoint-strategy.md` Last reviewed date updated; Repeatable Agentic Workflow section added (5 rules).
- `/memory` files 03, 05, 06, 07, 09, 10, 00-index updated: stale "pending propagation" notes removed; run011 propagation status recorded.

## run014 Phase 0 closure-readiness sprint (main execution stream)

run014 performed a full governance audit of all 45 Phase 0 files and fixed stale references found.

Changes applied in run014:

- `plans/master-plan.md` updated to v2.10: stale "run003 bundle" reference in Section 7 fixed; Section 8 file count corrected (44→45); Section 31 file count corrected (44→45); run014 added to run history; current state updated.
- Memory files updated: 00-index.md (run014 entry added), 04-phase0-evolution-and-bundle-reviews.md (this entry), 09-current-state-before-phase1.md (state and run history updated).
- 28 search/audit patterns verified: 1 FIXED (stale run003 bundle reference), rest PASS.
- No contradictions found beyond the three fixed items above.

## run015/run016/run017 status (Phase 1A complete, Phase 2 started)

- **run015** (2026-05-04): Phase 0 accepted (all 36 checks PASS). Phase 0 baseline commit made (c9d02da). FODS scored 93/100 (Accept band). Registry entry created (gate_1: scored_pending_human_approval). master-plan.md v2.11.
- **run016** (2026-05-04): Independent verification sprint. All run015 claims verified. DEC-034 added (independent verification before human review). AGENTS.md Section V + question 15. GOVERNANCE.md Section 15. master-plan.md v2.12.
- **run017** (2026-05-04): Gate 1 approved by Babar Raza. acquisition-packs/fods/ skeleton created (5 files). TC-0009 created (Phase 2, not_started). run016+run017 changes committed. master-plan.md v2.13.

## run018/run019 combined (Phase 2 Gate 2 evidence draft + TC-0007 tooling)

- **run018** (2026-05-04, committed via run019): State reconciliation. README.md, ROADMAP.md, settings.json Phase 2, master-plan v2.14. G-HEAL-018–025 resolved. No Gate 2 work.
- **run019** (2026-05-04): Combined sprint. run018 committed (0c97256). TC-0007 spec-cache tooling implemented (spec_index.py, acquire_spec.py, refresh_check.py). TC-0009 Gate 2 evidence draft completed (spec-evidence.md, legal-notes.md; OASIS fast-path 4/7 confirmed). Gate 2 status: evidence_draft_pending_independent_verification. master-plan.md v2.15.

## Current status after run019

Phase 0: ACCEPTED. Phase 1A: COMPLETE. Gate 1: PASSED. Gate 2: evidence_draft_pending_independent_verification. TC-0007: completed_pending_independent_verification. TC-0009: evidence_draft_pending_independent_verification.

No spec downloaded. No samples acquired. No prototype or source code created. Spec claims are SUPPORTED_BY_RECORDED_URL or PLAUSIBLE_PENDING_VERIFICATION.

Next: independent verification sprint + project lead Gate 2 sign-off.
