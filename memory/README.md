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

# format-factory Memory Package

This folder preserves the working memory from the ChatGPT conversation that shaped the `format-factory` project before Phase 1 began.

It is intended for agents working in the local repo. It explains what was discussed, why the plan evolved, what decisions were made, which mistakes were found in evidence bundles, and what the current standing rules are.

## Important authority rule

These memory files are **context**, not the operational authority.

The operational authority remains:

```text
plans/master-plan.md
```

Agents must read the master plan first. These memory files help explain the history behind it.

## Recommended reading order

1. `00-index.md`
2. `01-project-origin-and-intent.md`
3. `02-standing-operating-rules.md`
4. `03-architecture-and-product-tracks.md`
5. `04-phase0-evolution-and-bundle-reviews.md`
6. `05-decision-register-expanded.md`
7. `06-gap-risk-and-healing-history.md`
8. `07-agent-governance-model.md`
9. `08-specification-cache-amendment.md`
10. `09-current-state-before-phase1.md`
11. `10-memory-maintenance-protocol.md`
12. `11-prompting-and-agent-style-rules.md`
13. `12-glossary.md`

## Maintenance

When the project evolves, update these memory files or generate a new memory package from ChatGPT. Every memory update should preserve chronology and explicitly state what changed.

Do not let memory drift away from `plans/master-plan.md`. If a contradiction is found, log a gap and treat `plans/master-plan.md` as operational authority until corrected.
