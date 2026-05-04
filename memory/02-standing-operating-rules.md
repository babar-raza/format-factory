---
memory_package: format-factory-chat-memory
version: 1.0
created_at: 2026-05-03
intended_location: /memory
source: ChatGPT conversation memory plus inspected Phase 0 evidence bundles through run014
visibility: internal
publish_allowed: false
notes: Place this folder at repo root as /memory. These files are for agent context and must not supersede plans/master-plan.md.
---

# 02 — Standing Operating Rules

These rules were explicitly established during the conversation and should guide future agent work.

## Prompt rules

1. Do not provide prompts unless the human explicitly asks for one.
2. Every prompt must be labeled as either **PLAN MODE** or **EXECUTION MODE**.
3. Plan prompts must include detailed “fix this plan” instructions.
4. Execution prompts must include allowed files, forbidden files, validation checks, bundle requirements, and stop conditions.
5. Do not auto-continue from a plan-mode result. The human will ask separately for execution handoff.

## Human comments and summaries

1. Every human comment must be addressed.
2. Every pasted agent summary must be challenged.
3. Every problem mentioned by the human must be logged or resolved.
4. No gap is acceptable to ignore.
5. Agent summaries are not trusted until evidence/source bundles are inspected.

## Evidence bundle rule

Before moving forward or providing the next prompt:

1. The latest evidence/source bundle must be uploaded.
2. It must be extracted.
3. Its contents must be inspected.
4. The inspection must challenge the agent’s summary.
5. The next prompt must be based on what is actually inside the bundle.

Every execution prompt must require:

```text
EVIDENCE_BUNDLE: <absolute Windows path to zip>
```

as the final line of the agent response.

## Commit rule

No commit is allowed unless the human explicitly asks for a commit handoff.

Even if a run appears successful, the default is:

```text
NO COMMIT MADE
```

## Gate rule

Agents may prepare evidence, but agents may not approve gates.

All gates require human approval.

## Phase rule

Agents must obey phase boundaries.

No Phase 1 work is allowed before Phase 0 is accepted.

No product code is allowed before the proper implementation authorization model is satisfied.

## Product source authorization model

Open-source source can be created only after:

1. Gates 1-9 are complete.
2. Gate 9 human approval is recorded.
3. implementation taskcards exist.
4. an explicit Phase 4 OSS implementation execution prompt authorizes source creation.

Gate 10 is **OSS release readiness**, not permission to start writing source.

Commercial source can be created only after:

1. Gate 10 has passed.
2. DD3/commercial isolation is resolved.
3. commercial taskcards exist.
4. an explicit commercial implementation execution prompt authorizes source creation.

Gate 11 is **commercial release readiness**, not permission to start writing source.

## Current standing blocker

As of the latest memory package, Phase 0 has not yet been accepted. The run008 bundle must be inspected and accepted before Phase 1 can begin.
