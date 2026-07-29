---
artifact_id: FF6-EXECUTION-RUNBOOK-001
artifact_type: autonomous_execution_runbook
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
authoritative_state: false
---

# FF6 Execution Runbook

## Mission state machine

```text
DISCOVER -> SNAPSHOT -> CONTRACT -> IMPLEMENT -> VERIFY
         -> REPAIR -> CERTIFY -> EXTRACT -> RELEASE_PREP -> COMPLETE
```

Current state is `CONTRACT`. Authority closure passed at event 17. The parent
capability task remains `NEEDS_REPAIR`, so product implementation is locked.
The exact next task is `TC-FF6-IPYNB-PROFILE-SURFACE-001`.

## Canonical state precedence

When records disagree, use this order:

1. GitLab `origin/main` commit and tracked bytes.
2. `plans/strategic/ff6/events.jsonl`, validated as a native hash chain.
3. `plans/strategic/ff6/controller-state.yaml`.
4. Current taskcard and `taskcards/index.yaml`.
5. `plans/strategic/ff6/current-gaps.yaml`.
6. Digest-bound generated contracts and capability manifest.
7. This derived packet.
8. Chat history and provider memory, which never authorize work.

Generic Plan Control is not the FF6 journal validator until `FF6-GAP-011` is
repaired.

## Task lifecycle

```text
READY -> CLAIMED -> WORK_IN_PROGRESS -> VERIFYING
      -> PASS | NEEDS_REPAIR | TECHNICALLY_BLOCKED
      -> CLOSE_INTENT -> COMPLETE
```

- `READY` means dependencies, owner skill, and allowlist are known.
- `CLAIMED` is off-repo coordination state.
- `PASS` means task acceptance passed, not product certification.
- `NEEDS_REPAIR` records a reproducible technical gap and successor.
- `TECHNICALLY_BLOCKED` requires three materially different failed repair
  attempts for the same true external root cause.
- Close intent is write-ahead state; verified close follows independent replay.
- A provider or token change never alters acceptance criteria.

## Current DAG

```text
TC-FF6-PROGRAM-TRUTH-001 [COMPLETE]
  -> TC-FF6-PROGRAM-CAPABILITIES-001 [NEEDS_REPAIR]
       -> TC-FF6-CAPABILITY-COMPILER-001 [PASS]
       -> TC-FF6-AUTHORITY-CLOSURE-001 [PASS]
       -> TC-FF6-IPYNB-PROFILE-SURFACE-001 [READY]
       -> remaining compiler-derived contract repairs
  -> TC-FF6-PROGRAM-ARCHITECTURE-001
  -> TC-FF6-PROGRAM-TASKCARDS-001
  -> TC-FF6-PROGRAM-QUALITY-GATES-001
  -> TC-FF6-PROGRAM-REPLAY-001
  -> per-format implement/verify/certify/extract chains
```

No product wave may bypass the program dependencies.

## Start-of-task algorithm

1. Fetch `origin/main`; verify ancestry and clean worktree.
2. Read `AGENTS.md`, Codex or Claude adapter, master plan, FF6 goal, controller,
   journal, current gaps, task index, and current taskcard.
3. Validate the native FF6 chain and controller projection.
4. Query coordination; register a provider-specific identity.
5. Claim logical task scope and exact paths.
6. Resolve every operation through the capability/skill registries.
7. Run pre-mutation guard and path preflight.
8. Capture Git, authority, contract, generator, tool, lock, corpus, dependency,
   and environment digests relevant to the task.
9. Execute one bounded change set.
10. Record every write and heartbeat during long work.

## Exact OpenRaster task algorithm

### Inputs

- locked sources `SRC-ORA-001`, `SRC-ORA-002`, `SRC-ORA-003`;
- `shared/format-contracts/authority-lock.yaml`;
- OpenRaster research store, SAL facts, SAL evidence, policy, family and
  enrichment inputs;
- current `shared/format-contracts/ora.yaml`;
- capability universe compiler and all six generated projections;
- taskcard `TC-FF6-IPYNB-PROFILE-SURFACE-001`.

### Steps

1. Revalidate event 17 and three OpenRaster authority matches.
2. Materialize sources only through the canonical authority machinery.
3. Extract the nbformat 4.0-4.5 delta matrix with exact source fragments.
4. Classify each item as draft-normative, interoperability, product
   requirement, optional, preview, unsupported, or uncertain.
5. Compare every current OpenRaster SAL fact to the matrix.
6. Ingest missing facts through `ingest-spec-sal`; heal through
   `sal-pipeline-heal`.
7. Compile explicit capabilities for:
   - document identity and canvas geometry;
   - ZIP/mimetype/container reading and deterministic writing;
   - stack XML and namespace handling;
   - stack, nested group, layer, and mask models;
   - asset paths and PNG validation;
   - names, offsets, opacity, visibility, isolation and compositing;
   - editable baseline, merged image and thumbnail;
   - extension and unknown-data preservation;
   - rendering adapter and pinned operation semantics;
   - traversal, duplicates, bombs, resource limits, recursion, XML and entity
     security;
   - semantic roundtrip, deterministic output and external application
     interoperability.
8. Give every capability and obligation exact profile applicability.
9. Preserve stable IDs only when semantics are unchanged.
10. Compile OpenRaster, then all six format projections.
11. Require removal by evidence of both OpenRaster compiler findings.
12. Replay three clean strict runs and all affected validation.
13. Reconcile gaps, taskcards, controller and journal atomically.
14. Select the next mandatory repair without entering product source.

### Failure routing

- Missing authority: repair lock/materialization; do not bypass.
- Draft contradiction: split named profiles and preserve uncertainty.
- Application behavior absent from drafts: classify as interoperability or
  product requirement, not normative fact.
- Compiler finding remains: task is `NEEDS_REPAIR`, not pass.
- Nondeterministic output: block closure, isolate input, repair, rerun.
- Same true external cause after three distinct repairs: record
  `TECHNICALLY_BLOCKED` and continue other formats.

## Verification tiers

### Bounded contract task

- authority and referential integrity;
- schema validation;
- SAL positive and negative validation;
- deterministic generation;
- affected unit and regression tests;
- Ruff, mypy, pyright;
- native event-chain validation;
- no unexpected source/product/package changes.

### Implementation task

Add behavior, rejection, preservation, roundtrip, resource, property,
metamorphic, fuzz, differential, architecture, API, typing, documentation, and
installed-wheel proof.

### Certification task

Add complete official/independent corpora, mutation testing, performance,
cross-platform Python matrix, minimum/latest dependencies, reproducible builds,
SBOM, provenance, signatures, vulnerabilities, namespace co-installation, and
standalone repository replay.

## Close algorithm

1. Run the task's focused and regression suites.
2. Record self-challenge answers and unresolved limitations.
3. Write close-intent event.
4. Compute LF-normalized output and evidence digests.
5. Independently replay/validate.
6. Write verified close event.
7. Update controller, taskcard, task index, gaps, handover, and receipt.
8. Validate journal from event 1.
9. Stage explicit reviewed files only.
10. Run coordination precommit check.
11. Fetch and classify any remote movement.
12. Commit with a precise Conventional Commit message.
13. Push only to GitLab `origin/main`.
14. Verify remote main equals the pushed commit.
15. Complete only the outgoing agent's coordination session.

## Program waves after contract readiness

1. Package chassis and common lifecycle.
2. SafeTensors and IPYNB.
3. NRRD and OpenRaster.
4. XLIFF 2.0/2.1 core and all 2.1 modules.
5. UBL 2.3 generator, all components, and all 91 roots.
6. Independent repository extraction and release preparation.

Formats may certify independently. Mission completion requires all six or only
true, adjudicated external blocks after all technical work.
