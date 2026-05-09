---
memory_package: format-factory-chat-memory
created_at: 2026-05-09
source: ChatGPT AI-direction conversation and evidence-bundle review
visibility: internal
publish_allowed: false
authority: context_only
supersedes: none
must_cross_check:
  - plans/master-plan.md
  - registry/format-registry.yaml
  - evidence bundles
---

# 14 -- AI Supervision and Three-Pilot Direction, 2026-05-09

## Purpose

This file captures the current project direction agreed in the 2026-05-09 ChatGPT supervision
conversation. It complements `memory/13-chatgpt-initial-project-analysis-20260509.md`.

## User confirmation

The user confirmed that ChatGPT's project understanding was almost entirely correct.

The user agreed that the original plan was right to introduce LLMs at later stages after the
foundation was laid correctly. However, the design for how LLMs are implemented needs refinement.

The user wants ChatGPT to help drive the project by refining designs, instructing agents in the
VS Code environment, reviewing evidence bundles, and planning ahead toward end goals.

## End goal

The near-term proof target is:

Prove the system with 3 format pilots, all from XML-style sources, but with different feature
profiles.

The three-pilot target should be treated as the production-readiness proof path for the governed
AI-assisted factory.

The system should not merely create more plans. It must move toward tangible outputs while
preserving governance.

## AI direction

AI, embeddings, LLMs, agentic workflows, skills, and playbooks should be used to reduce tedious
work and accelerate progress.

However, AI must be controlled strictly.

The desired model is:

- deterministic first
- evidence-backed
- locally cached where appropriate
- schema-validated
- replayable
- auditable
- citation/provenance-preserving
- consistent across reruns
- able to produce near-identical results from the same inputs

AI is a governed worker, not the source of truth.

## What AI may do

AI may be used to:

- summarize normalized specifications
- propose candidate verified facts
- draft implementation requirements
- suggest parser strategies
- generate or improve tests
- propose edge cases
- analyze failures
- suggest repair plans
- draft source code from approved FUL artifacts
- help build review queues
- help agents compare evidence against claims
- help agents produce consistent planning and execution handoffs

## What AI must not do

AI must not:

- replace evidence
- approve gates
- create facts without provenance
- embed or store raw copyrighted spec text in evidence bundles
- commit raw LLM prompts or responses
- bypass deterministic checks
- weaken validators
- silently change scope
- generate product source from imagination
- promote prototypes directly into product code
- treat embeddings as authority
- use secrets from committed files

## ChatGPT supervisory role

ChatGPT will drive the project through detailed agent prompts.

For every sprint, ChatGPT should:

1. Inspect the provided evidence bundle first.
2. Challenge the prior agent summary.
3. Reconstruct actual state from files and reports.
4. Identify contradictions, stale state, and missing proof.
5. Decide whether the sprint needs closure, repair, verification, or next-scope execution.
6. Produce a detailed, comprehensive, exact prompt for the VS Code agent.
7. Require the agent to produce a new evidence bundle.
8. Use that evidence bundle to plan the next step.

Prompts must be specific and strict. They must tell agents exactly what to inspect, what to verify,
what to fix, what not to touch, what evidence to produce, and how to report completion.

## Parallel sprint handling

The user may run multiple sprints in parallel when they are independent and do not touch the same
authority files.

Parallel sprint streams must be treated separately unless evidence shows they conflict.

For each active stream, agents must classify:

- original scope
- actual completed work
- claimed work not proven
- failed or incomplete work
- conflict risk with other streams
- whether the stream is safe to continue
- whether it should be closed, repaired, verified, or escalated

If multiple streams touch shared authority files such as `plans/master-plan.md`,
`registry/format-registry.yaml`, `memory/`, `AGENTS.md`, `GOVERNANCE.md`, evidence contracts, or
taskcards, a reconciliation sprint is required before major new work.

## Current active stream notes from this chat

### Main stream: run050

The human provided the run050 evidence bundle and summary.

ChatGPT inspection found that the final validator proof says `BUNDLE_VALIDATION: PASS`, and local
checks against the extracted repo snapshot passed:

- FUL validator tests passed.
- Evidence tests passed.
- FODS FUL validation passed.
- FODT FUL validation passed.
- Current-state consistency passed.
- Bundle validation against the run050 contract passed.

However, the run050 bundle also contained stale contradictory closure metadata:

- `bundle-metadata/verdict.md` said `SPRINT_VERDICT: FAIL`.
- `bundle-metadata/final-state-summary.yaml` said `result: FAIL`.
- `bundle-metadata/phase4-readiness-matrix.yaml` said FUL validator `FAIL`.
- `check-N06`, `check-N07`, `check-N08`, and `check-N09` still said `FAIL`.
- FUL validation report bodies were mostly empty.
- `format-understanding-validator-test-report.md` said exit code 1 while repo tests passed.

ChatGPT's recommendation: do not start Phase 4 source yet. First run a focused run050 closure
hygiene and evidence reconciliation sprint.

Expected next state after repair:

- FODS Gate 11: planning_ready, not passed.
- FODT Gate 10: planning_ready, not passed.
- FODS Python Phase 4: not_started, explicit prompt required.
- FODT Python Phase 4: not_started, explicit prompt required.
- DEC-033 remains unresolved for .NET.
- Product source must not be created until explicit Phase 4 authorization.

### Secondary playbook stream: S-F2F-02B

The human provided the S-F2F-02B evidence bundle and summary.

ChatGPT inspection found the bundle validates and the implementation is real:

- `not_for_execution` exists in the playbook schema.
- `additionalProperties: false` is preserved.
- `validate_playbook.py` supports `--engine auto|jsonschema|fallback_structural`.
- Documentation example passes both jsonschema and fallback structural engines.
- Validator remains read-only.
- No replay engine or apply mode was created.
- No acquisition-pack playbook was created.
- No product source, embeddings, LLM calls, or main sprint mutation were created.

However, documentation drift remained:

- `docs/playbook-layer.md` still had stale S-F2F-02 pending/future/30-test references.
- `plans/master-plan.md` had an outdated 30/30 test count in one row.
- `plans/secondary/full2foss-inspired-system-strengthening-plan-v2.md` had a stale future heading.
- `taskcards/S-F2F-03-dry-run-replay-and-review-queue.md` had outdated validator command examples.

ChatGPT's recommendation: do not start S-F2F-03 yet. First run S-F2F-02C closure normalization
and S-F2F-03 readiness cleanup.

Expected next state after repair:

- S-F2F-02: CLOSED_VERIFIED.
- S-F2F-03: proposed_pending_human_approval.
- No replay engine yet.
- S-F2F-03 may be authorized later through a separate explicit prompt.

Note: As of MEMORY.md (run050), both S-F2F-02C and run050 closure hygiene appear to have been
executed (commits 4ce9191 and the run050 closure commits). Agents must verify actual repo file
state before acting on this note; do not trust only this memory file.

### Memory stream

This memory sprint exists because the user wants the current ChatGPT analysis and supervisory rules
stored locally so future agents can follow them without relying on chat history.

The memory stream must not claim that run050 closure hygiene or S-F2F-02C has already been executed
unless actual local evidence proves it.

## Required future behavior for agents

Agents must treat ChatGPT-provided sprint prompts as authoritative execution instructions for that
sprint, subject to repo governance and actual file evidence.

Agents must not shorten, reinterpret, or skip prompt requirements.

Agents must not convert execution prompts into informal plans unless the prompt says PLAN MODE.

Agents must not move to the next sprint just because a previous agent summary says complete.
Evidence bundles must be inspected.

Agents must produce a final evidence bundle path for every execution sprint.

## Three-pilot proof path (strategic direction)

The production-readiness proof path for the governed AI-assisted factory is to complete three
XML-style format pilots with different feature profiles.

FODS and FODT are already in progress. A third format should be selected when the first two pilots
reach product source or near product-ready state.

The three pilots should demonstrate:

1. The full acquisition pipeline from Gate 1 to Gate 11.
2. AI-assisted FUL compilation (facts, requirements, strategies).
3. Governed source scaffolding from approved FUL artifacts.
4. Test generation and oracle validation.
5. Packaging and release readiness.

Until the three pilots are complete, the project should not expand to new format families or new
feature areas beyond what is required for the pilots.

## LLM design refinement required

The LLM implementation design needs refinement before operational rollout. The key decisions are:

1. How are LLM calls governed (budget, authorization, caching)?
2. How are LLM outputs converted to schema-validated artifacts?
3. How are LLM calls audited (run IDs, prompt hashes, model versions)?
4. How do LLM proposals get reviewed, cited, and promoted to facts?
5. How are failed or low-confidence LLM outputs handled?

These decisions must be captured in LLM-001 and related taskcards before LLM client code is created.
The code must not precede the design.

## Detailed AI module and state-management design

See `memory/15-ai-modules-and-state-management-architecture-20260509.md` for the detailed design
direction covering governed LLM modules, embedding retrieval, controlled agent roles, FUL-based
source generation, the Format Factory State Manager, state categories, transition transactions,
community components, and practical sequencing.

This file records supervisory direction and three-pilot strategy. `memory/15` contains the detailed
AI module and state-management architecture. Do not duplicate the full design here. Cross-check both
files against `plans/master-plan.md`, `registry/format-registry.yaml`, taskcards, and evidence
bundles before acting.

## Summary of what is NOT yet authorized

The following are explicitly NOT authorized as of this memory sprint:

- Phase 4 product source in src/python/ or src/net/ (requires explicit Phase 4 prompt)
- LLM endpoint client implementation (requires LLM design refinement and explicit authorization)
- Embedding or vector DB creation (requires EMB-001 design completion and explicit authorization)
- S-F2F-03 playbook replay execution (requires explicit human authorization)
- Playbook replay engine code (not authorized; replay_acquisition_playbook.py exists as untracked
  but must not be committed without explicit S-F2F-03 authorization)
- New format pilots beyond FODS and FODT (deferred until first two pilots mature)
