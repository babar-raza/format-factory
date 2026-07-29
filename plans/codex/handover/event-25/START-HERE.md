---
artifact_id: FF6-PROVIDER-NEUTRAL-START-EVENT-25
artifact_type: provider_neutral_handover_entrypoint
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
authoritative_state: false
canonical_state_path: plans/strategic/ff6/controller-state.yaml
---

# Start Here — Six Python Production Libraries, Event 25

This is the current provider-neutral entrypoint for mission
`FF6-PRODUCTION-LIBRARIES-001`.

Absolute Windows path:

```text
C:\Users\prora\OneDrive\Documents\GitHub\format-factory\plans\codex\handover\event-25\START-HERE.md
```

Claude, Codex, or another governed executor must reconstruct state from GitLab
and the canonical machine records. Provider memory and this packet are
navigation aids, never state authorities.

## Why this versioned packet exists

The prior root packet under `plans/codex/handover/` was being refreshed when
its writer process ended. Its long-TTL coordination leases remained active and
correctly prevented another writer from overwriting the partial bytes.

The missing product/control checkpoint was repaired independently:

- implementation commit
  `2522752776f64ab800a2a21c8fa46c1f2a4e361c` is on GitLab `origin/main`;
- event `FF6-EVENT-000025` binds that commit and its evidence;
- controller and XLIFF taskcard projections agree with event 25;
- checkpoint commit
  `220ee7f5b9d39c3684cff6af6331b56a03ae9e75` is on GitLab `origin/main`.

This versioned packet avoids violating active leases. It does not discard the
prior writer's bytes, reuse its identity, or create a second product truth.
After those leases become stale, a later governed refresh may fold this packet
back into the root `START-HERE.md`. Until then, use this file.

## Canonical precedence

If any statement conflicts, trust the first valid source in this order:

1. fetched GitLab `origin/main` tracked bytes;
2. valid `plans/strategic/ff6/events.jsonl`;
3. `plans/strategic/ff6/controller-state.yaml`;
4. current taskcard and `taskcards/index.yaml`;
5. current gap and capability projections;
6. digest-bound authority, contracts, corpus, tests, packages, and proof;
7. this packet;
8. older handover packets, chat, or provider memory.

## Mission contract

Deliver six independently publishable, production-grade Python libraries:

- Jupyter Notebook, nbformat 4.0–4.5;
- OpenRaster, named 0.0.3/0.0.4/0.0.5 interoperability profiles;
- NRRD0001–NRRD0005;
- XLIFF 2.0 and 2.1 Core plus all official 2.1 modules;
- SafeTensors pinned to the official format definition;
- OASIS UBL 2.3 with all 91 document roots and fully typed schema models.

The quality target is not file presence or a broad API. Each supported
capability must be authority-backed, production-grade, behaviorally tested,
independently interoperable, installed-wheel verified, secure under bounded
resources, documented, typed, maintainable, and connected to live proof.

The executor never asks whether to continue. A blocked format does not stop
safe work on another. Gate 10 publication/business authority remains external;
technical release preparation continues without bypassing that gate.

## Clean checkpoint

| Field | Current value |
|---|---|
| Forge | GitLab only |
| Remote/branch | `origin/main` |
| Checkpoint commit | `220ee7f5b9d39c3684cff6af6331b56a03ae9e75` |
| Implementation commit | `2522752776f64ab800a2a21c8fa46c1f2a4e361c` |
| Controller state | `CONTRACT` |
| Journal head | `FF6-EVENT-000025` |
| Event hash | `237f7759e2286cfc08c547c53a0b47d44e1c77307329ec0215c5326e3f811e48` |
| Parent task | `TC-FF6-PROGRAM-CAPABILITIES-001` — `NEEDS_REPAIR` |
| Active task | `TC-FF6-XLIFF-PROFILE-SURFACE-001` — `WORK_IN_PROGRESS` |
| Completed XLIFF steps | `XLF-01`, `XLF-02`, `XLF-03` |
| Completed XLF-04 batches | `001`, `002`, `003` |
| First unmet step | `XLF-04` |
| Exact next microstep | `XLF-04-BATCH-004` |
| Portfolio capability projection | 110 capabilities / 672 obligations |
| XLIFF Core work denominator | 105 expected IDs |
| XLIFF resolved/open | 25 resolved / 80 missing |
| Authority | 17/17 global; 5/5 XLIFF `MATCH` |
| Product certifications | 0/6 |
| Promotion | all six `UNASSESSED` |

## Real product state

The baseline product inventory in
`plans/strategic/ff6/current-state.yaml` predates event 25. Its product source
counts remain useful because event 25 changed contract machinery, not product
source. Its readiness labels do not promote any product.

| Format | Existing depth | Material limits |
|---|---|---|
| IPYNB | 46 Python files, typed notebook/cell/output/attachment/MIME/metadata models, read/write, validation, conversion, cleanup/editing helpers | contract is DRAFT; architecture has oversized public initializers; corpus adequacy unproven; oracle D0; install proof stale; not certified |
| OpenRaster | contract/SAL planning only | no source, product tests, corpus, oracle, install proof, or certification |
| NRRD | 32 Python files, attached/detached lifecycle, payload codecs, header/comments/key-values/preservation, limits and validation | typed dimensional/spatial semantics incomplete; architecture violation; corpus/oracle/install proof non-promoting; not certified |
| XLIFF | 38 product Python files with Core hierarchy, inline editing, segmentation/state helpers, extension preservation and limits; separate authority compiler now has 25 source-bound obligations | all official module models incomplete; 80 expected Core IDs unresolved; every new row unverified against canonical SAL; product source was not changed by XLF-04; not certified |
| SafeTensors | 38 Python files, descriptors/dtypes, layout validation, lazy mmap/regions, deterministic writing, sharded index, NumPy/PyTorch adapters | oracle D0, corpus adequacy and current install proof incomplete; contract DRAFT; not certified |
| UBL | 39 Python files, 91 named root subclasses, generic ordered XML parse/edit/write, extension preservation, limits, signature invalidation | roots mostly wrap a generic document; common components, simple types, attributes, cardinalities and content models are not fully schema-typed; not certified |

These counts are inventory, not quality scores. Existing behaviors must be
characterized and preserved where valid, but the current architecture and
readiness labels are not presumed correct.

## What event 25 actually achieved

XLF-04 batch 003:

- preserved the 19 prior XLIFF Core obligation IDs;
- added six obligations for structural/semantic roundtrip, deterministic
  output, unsafe URI risk, external-resolution policy, and resource limits;
- separated 21 XLIFF specification obligations from four Format Factory
  production-policy obligations;
- added `obligation_basis` and `conformance_effect`, preventing production
  policy from inflating OASIS conformance;
- created a tracked 105-ID expected-obligation denominator;
- bound denominator bytes as a direct compiler input;
- rejects authority-input digest tampering;
- produced deterministic matrix, denominator, and inventory artifacts;
- passed 27 focused tests, 94 affected format-contract tests with one
  baseline-known deselection, 69 production-program tests, Ruff, strict Mypy,
  Pyright 1.1.411, bytecode compilation, artifact check mode, receipt
  validation, and five XLIFF authority matches.

## What event 25 did not achieve

- The 105-ID denominator is `OPEN_AUTHORITY_CENSUS`, not proven exhaustive.
- Eighty expected IDs are unresolved.
- All 12 categories have rows, but all 12 remain incomplete.
- The 25 rows are `SOURCE_BOUND_UNVERIFIED`.
- Core normative prose, XSD, Schematron, and 2.0/2.1 delta surfaces are not
  completely dispositioned.
- XLF-05 module obligations, SAL reconciliation, family/capability repair,
  product implementation, installed-package proof, certification, promotion,
  and release remain open.
- No product source or test was changed in this checkpoint.
- No library is publication-ready.

## Symptoms, root causes, and structural weaknesses

### Symptoms

- status packets can lag behind valid implementation commits;
- different agents can attempt the same projection work;
- category counts can appear complete while most expected obligations remain
  unresolved;
- source/test counts and legacy proof labels look stronger than executed
  evidence warrants;
- a provider crash can leave long-lived leases blocking an immediate shift.

### Root causes

- journal, controller, taskcards, packet prose, historical ledgers, and proof
  stores are only partially unified;
- older evidence hashes do not always bind the complete source/test/fixture/
  authority/environment/package closure;
- mutable shared state can move between discovery and execution;
- historical gaps and current operational gaps are mixed in some consumers;
- hand-maintained capability lists can omit normative surfaces;
- independent evidence is sometimes synthetic or implementation-derived;
- coordination staleness is heartbeat-only and does not safely combine local
  process liveness with lease expiry.

### Structural weaknesses to redesign

- make one content-addressed proof graph the computed promotion authority;
- compile a complete `ProductContract` and mandatory-obligation denominator
  for every format;
- bind every executed result to source, test, corpus, authority, dependency,
  environment, and package digests;
- materialize current gaps from the append-only history rather than scheduling
  directly from the history;
- certify built wheels in isolated, pinned environments;
- make provider shifts a journaled transaction with an immutable
  implementation commit followed by a projection/packet commit;
- repair coordination so dead local processes can become audited takeover
  candidates without waiting for an unrelated long TTL, while never
  authorizing data deletion from process death alone.

## Preserve versus redesign

Preserve:

- valid public behaviors through characterization tests;
- pinned authorities and their content-addressed bytes;
- working proof, manifest, event, taskcard, and coordination primitives;
- explicit GitLab-main and exact-path staging rules;
- format-specific models and safe parsing behavior that pass fresh evidence.

Redesign:

- competing readiness/status authorities;
- presence-based or stale evidence;
- generic module buckets and untyped schema-family facades;
- package/source import ambiguity;
- hand-maintained incomplete obligation denominators;
- provider-local recovery and long-TTL dead-process lease handling.

## Exact continuation

Resume `TC-FF6-XLIFF-PROFILE-SURFACE-001` at
`XLF-04-BATCH-004`. Do not start UBL merely because its taskcard is ready; the
controller still selects XLIFF.

Batch 004 must compile a deterministic Core authority-candidate census across:

1. direct/leaf normative prose requirements, avoiding ancestor/descendant
   double counting;
2. Core XSD elements, types, attributes, cardinalities, and ordering;
3. Core Schematron or equivalent assertions;
4. exact XLIFF 2.0 versus 2.1 additions, changes, removals, and shared rules.

Every candidate must map exactly once to:

- one or more expected obligation IDs; or
- an explicit, reasoned non-obligation disposition.

Fail on unmapped candidates, duplicate mappings, stale authority digests,
ambiguous profile ownership, ancestor/leaf duplication, or preview leakage.
Keep `complete: false` until the candidate census is exhaustive and every
expected ID resolves.

## Read order

1. [`AGENTS.md`](../../../../AGENTS.md)
2. [`skill-only-policy.yaml`](../../../../docs/governance/skill-only-policy.yaml)
3. Codex only: [`codex-adapter.md`](../../../../docs/governance/codex-adapter.md)
4. [`product-goal.yaml`](../../../strategic/ff6/product-goal.yaml)
5. [`autonomous-six-python-production-execution-plan.md`](../../../strategic/autonomous-six-python-production-execution-plan.md)
6. [`controller-state.yaml`](../../../strategic/ff6/controller-state.yaml)
7. complete [`events.jsonl`](../../../strategic/ff6/events.jsonl)
8. [`current-gaps.yaml`](../../../strategic/ff6/current-gaps.yaml)
9. [`capability-coverage.yaml`](../../../strategic/ff6/capability-coverage.yaml)
10. [`TC-FF6-XLIFF-PROFILE-SURFACE-001.md`](../../../../taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md)
11. [`TC-FF6-UBL-TYPING-001.md`](../../../../taskcards/TC-FF6-UBL-TYPING-001.md)
12. [`xliff-normative-delta-matrix.yaml`](../../../../reports/ff6/xliff-normative-delta-matrix.yaml)
13. [`xliff-core-obligation-denominator.yaml`](../../../../reports/ff6/xliff-core-obligation-denominator.yaml)
14. [`xliff-core-obligation-inventory.yaml`](../../../../reports/ff6/xliff-core-obligation-inventory.yaml)
15. [`plan-control event-25 receipt`](../../../../reports/skills-rff6/skill-transcripts/plan-control-xliff-profile-surface-wip-006.json)
16. [`CHECKPOINT.yaml`](CHECKPOINT.yaml)
17. [`RUNBOOK.md`](RUNBOOK.md)
18. [`manifest.yaml`](manifest.yaml)
19. [`receipt.json`](receipt.json)

## Provider-shift invariant

Only one provider owns an active task's write scope. The incoming provider:

1. fetches and validates GitLab;
2. reads canonical state;
3. queries live coordination;
4. registers a new identity;
5. claims exact paths;
6. resolves registered skills and mutation authorization;
7. replays the predecessor evidence;
8. executes one bounded RED→GREEN→regression slice;
9. commits implementation;
10. appends the native event and rebuilds projections;
11. refreshes the handover;
12. commits and pushes the checkpoint;
13. verifies remote state;
14. releases only its own leases and completes its identity.

No token, process, lease, chat, branch, ignored worktree, or unpushed commit is
transferred as durable state.

## Non-negotiable truth boundary

This packet proves a clean, resumable contract-stage checkpoint. It does not
prove complete XLIFF Core support, any production library, certification,
publication readiness, release authority, or 6/6 completion.
