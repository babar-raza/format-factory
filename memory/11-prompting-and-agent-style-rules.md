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

# 11 — Prompting and Agent Style Rules

## User preferences for prompts

The user prefers prompts to be:

- direct
- LLM-consumable
- systematic
- drift-resistant
- explicit about mode
- gated
- evidence-driven
- self-challenging
- ready to paste

## Prompt labels

Every prompt must start with one of:

```text
MODE:
PLAN MODE ONLY.
```

or

```text
MODE:
EXECUTION MODE.
```

## Plan mode requirements

Plan mode must:

- not create repo files
- not create bundles
- not execute work
- provide absolute plan path if applicable
- include “Fix This Plan Before Execution” instructions
- challenge assumptions
- include gaps and risks
- include evidence/source bundle expectation for later execution

## Execution mode requirements

Execution mode must:

- define exact allowed files
- define exact forbidden files
- define validation checks
- define evidence/source bundle structure
- require final absolute zip path
- require self-challenge
- require no commit unless explicitly asked
- stop after requested scope

## Bundle inspection before next prompt

If the user provides an agent summary and a bundle, inspect the bundle first.

Do not provide the next prompt from the summary alone.

## Prompt evolution pattern used in Phase 0

The project followed this pattern:

1. Plan prompt for architecture.
2. Harden plan prompt when contradictions found.
3. Execution prompt for Phase 0 foundation.
4. Bundle inspection.
5. Healing prompt.
6. Bundle inspection.
7. Canonicalization prompt.
8. Bundle inspection.
9. Governance sync prompt.
10. Bundle inspection.
11. Final consistency healing prompt.
12. Bundle inspection.
13. Product gate semantics prompt.
14. Bundle inspection.
15. Specification cache amendment prompt.
16. Bundle inspection pending.

This pattern should continue.

## No em dash preference

The user has a broader style preference to avoid em dashes. Agents should avoid em dashes in user-facing prompts and docs unless preserving quoted content.
