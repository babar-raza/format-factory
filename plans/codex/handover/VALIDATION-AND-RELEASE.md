---
artifact_id: FF6-VALIDATION-RELEASE-HANDOVER-001
artifact_type: verification_and_release_contract
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
authoritative_state: false
---

# Validation, Regression, and Release Contract

## Capability completion

A capability is complete only when its public API, behavior, preservation,
errors, security, resources, scale behavior, deterministic contract, tests,
external interoperability, installed-wheel examples, compatibility, and full
proof-input closure pass.

Planning records, files, methods, generated classes, test names, and synthetic
fixtures cannot satisfy this rule.

## Current checkpoint boundary

The capability compiler checkpoint proves deterministic planning structure,
not format behavior:

- 89 capabilities and 636 obligations reconcile with exact ownership;
- 14 compiler, 43 production-program, and 76 unaffected format-contract tests
  pass;
- one CSV gap-ledger idempotency test fails identically at the pre-change
  commit and remains a separate baseline defect;
- all 636 obligations remain `UNVERIFIED`;
- all six product promotions remain `UNASSESSED`;
- 15 authority sources remain unresolved: 11 missing and 4 undeclared.

Event 14 additionally proves only a bounded authority WIP tier:

- the shared schema/runtime/CLI and four internal requirement artifacts exist
  with recorded digests;
- six focused tests pass;
- Ruff and mypy pass;
- Pyright was not available in the current interpreter;
- the canonical lock, real-network audit, strict compiles, and replay remain
  absent.

The active task must make strict authority compilation pass without an override.
Even that result would establish `CONTRACT_READY` prerequisites only; it would
not make product implementation or certification claims.

## Provider-shift checkpoint gate

A provider shift is acceptable only when:

- the checkpoint is committed to and verified on GitLab `origin/main`;
- controller, journal, taskcard, task index, and handover agree;
- every changed tracked path has a recorded digest;
- completed substeps have passing focused verification;
- missing gates and known defects are named, not omitted;
- the next substep is deterministic;
- no result required for continuation exists only in chat or ignored storage;
- the outgoing coordination session is completed, or the incoming provider
  uses governed takeover;
- promotion state is no stronger than before the partial checkpoint.

This gate allows a valid, explicitly non-promoting `WORK_IN_PROGRESS` commit.
It does not allow a failing, contradictory, or unclassified change set to be
normalized as a checkpoint.

## Required evidence per mandatory obligation

- Positive behavior proof.
- Negative proof for rejection and security obligations.
- Preservation proof when unknown or extension data can survive.
- Resource-limit boundary and beyond-boundary proof.
- Roundtrip or semantic metamorphic proof where applicable.
- Official or genuinely independent interoperability proof when available.
- Exact authority, source, test, fixture, corpus, lock, tool, environment,
  package, and oracle digests.

## Pull request or bounded task tier

- contract and graph integrity;
- changed-format unit, behavior, rejection, and roundtrip tests;
- Ruff, mypy, pyright, architecture, API compatibility, and security checks;
- generator reproducibility for generated outputs;
- wheel build and installed-wheel smoke tests.

For machinery-only contract tasks that prohibit product/package mutation, the
wheel check is deferred by the taskcard, but the deferral does not satisfy any
product obligation. The focused machinery test, static, security, idempotency,
and affected regression gates still apply.

## Merge and nightly tier

- full official and independent corpora;
- property, metamorphic, fuzz, mutation, and differential tests;
- dependency minimum/latest matrices;
- performance and memory regression budgets;
- cross-platform Python 3.11 through 3.14;
- replay, invalidation, concurrency, and source-versus-wheel isolation.

## Release tier

- fresh checkout and hash-locked environment;
- complete proof graph rebuild;
- two identical package builds;
- six-package namespace co-installation;
- upstream `safetensors` co-installation;
- documentation examples against installed wheels;
- SBOM, provenance, signatures, licenses, and vulnerability scans;
- standalone repository extraction and full recertification.

## Mandatory regression controls

1. Three equivalent runs yield identical canonical outputs.
2. Each input category invalidates its descendants.
3. Deleted or renamed tests revoke evidence.
4. Modified fixtures cannot reuse results.
5. Stale authority digests stop compilation.
6. Missing, duplicate, foreign, or broken facts fail closed.
7. Prose deferrals cannot satisfy mandatory work.
8. Concurrent runs cannot share mutable state.
9. Installed-wheel and source-tree imports cannot be confused.
10. Manual status changes cannot promote a product.
11. Historical evidence cannot become current without replay.
12. Repository extraction preserves canonical source and package digests.
13. CRLF/LF checkout differences do not create false proof invalidation.
14. Global task selection cannot bypass FF6 program dependencies.

## Promotion states

```text
UNASSESSED
-> CONTRACT_READY
-> IMPLEMENTATION_IN_PROGRESS
-> IMPLEMENTATION_VERIFIED
-> RELEASE_CANDIDATE
-> RELEASED
```

Any changed proof dependency yields `INVALIDATED`. Recovery rebuilds proof; it
does not edit the status.

## External release boundary

Technical source, packages, docs, SBOMs, provenance, signatures, and repository
exports must be completed without asking for continuation. Missing credentials
or mandatory business authorization records `EXTERNAL_RELEASE_BLOCKED`.

Do not bypass Gate 10, Gate 11 business authority, legal approval, credentials,
or publication policy. Do not impersonate an approver.

## Task close self-challenge

Before any close event, record answers to at least:

1. Is the claim executed behavior rather than presence?
2. Does every public symbol map to a classified capability and authority?
3. Are positive, negative, preservation, and resource cases current?
4. Can valid input lose information silently?
5. Was the installed wheel tested?
6. Is the oracle independent and digest-bound?
7. Are dependency direction and package boundaries intact?
8. Are optional dependencies isolated?
9. Are API, typing, docs, examples, and compatibility complete?
10. Do input changes invalidate the right descendants?
11. Are performance and memory bounded?
12. Are contradictions and gaps retained?
13. Did writes and staging stay inside the allowlist?
14. Were controller, taskcard, index, proof, and artifacts updated?
15. Were governance and release boundaries preserved?
16. Were hidden manual substitutes and unapproved LLM calls avoided?
17. Is the final state no stronger than live proof?
