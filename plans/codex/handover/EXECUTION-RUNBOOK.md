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

Current state is `CONTRACT`. Authority closure passed at event 16, OpenRaster
profile/surface repair at event 17, and IPYNB profile/surface repair at event
18. NRRD0001-NRRD0005 profile repair passed at event 19. The parent capability
task remains `NEEDS_REPAIR`, so product
implementation is locked. The exact next task is
`TC-FF6-XLIFF-PROFILE-SURFACE-001`.

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
       -> TC-FF6-ORA-PROFILE-SURFACE-001 [PASS]
       -> TC-FF6-IPYNB-PROFILE-SURFACE-001 [PASS]
       -> TC-FF6-NRRD-PROFILE-SURFACE-001 [PASS]
       -> TC-FF6-XLIFF-PROFILE-SURFACE-001 [READY]
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

## Exact XLIFF task algorithm

### Inputs

- remote-verified event 19 and the `PASS` NRRD checkpoint;
- the locked XLIFF 2.1 OASIS Standard package, prose member, and product
  requirements;
- the authority lock, which currently has no separate XLIFF 2.0 Standard
  package and therefore cannot support 2.0 claims yet;
- `shared/format-contracts/authority-lock.yaml`;
- XLIFF research store, SAL facts, SAL evidence, policy, family and
  enrichment inputs;
- current `shared/format-contracts/xliff.yaml`;
- capability universe compiler and all six generated projections;
- taskcard `TC-FF6-XLIFF-PROFILE-SURFACE-001`.

### Steps

1. Revalidate event 19, controller/task/index agreement, the remote source
   commit, coordination ownership, and all 15 predecessor authority matches.
2. Acquire the official XLIFF 2.0 OASIS Standard package only through the
   legal-aware authority pipeline.
3. Independently recompute its digest, inventory normative prose/Core XSD/
   module XSD/Schematron/catalog/example/notice members, add the authority
   record, and prove clean offline reconstruction.
4. Extract a source-located 2.0/2.1 delta matrix. Separate common Core rules,
   2.1 additions/changes, module rules, processing requirements, ITS mappings,
   and uncertainty.
5. Audit every current XLIFF SAL fact against that matrix. Split mixed 2.0/2.1
   claims; ingest missing facts and heal false claims only through registered
   SAL skills.
6. Compile complete Core requirements for hierarchy, languages, identifiers,
   inheritance, ordering/cardinality, source/target structure, notes,
   original data, skeletons, extensions, inline identity/pairing/nesting/
   isolation/order, segmentation/re-segmentation, state/sub-state, and agent
   processing.
7. Replace the generic module bucket with separately owned Translation
   Candidates/Matches, Glossary, Format Style, Metadata, Resource Data, Size
   and Length Restriction, Validation, and ITS capability families.
8. Reconcile all nine module schema vocabularies (`matches`, `glossary`, `fs`,
   `metadata`, `resource_data`, `size_restriction`, `validation`, `its`,
   `itsm`) to the eight owners. Treat `its` and `itsm` as one ITS module.
   Inventory Change Tracking as informative and give it no normative
   conformance credit.
9. For each module, require typed models, parse/write, schema plus processing
   validation, preservation, rejection, diagnostics, positive/negative/
   property/roundtrip/interoperability/security/resource obligations.
10. Repair mixed-profile research or product requirements at their governed
   source, then regenerate and relock; never patch only the projection.
11. Apply explicit-complete fact ownership only after every live fact has one
    exact Core or module owner.
12. Give every stable capability and obligation an exact non-empty subset of
    `xliff_2.0` and `xliff_2.1`; never assign a 2.1-only module to 2.0.
13. Keep XLIFF 2.2 absent or `PREVIEW_ISOLATED`, with no stable obligation
    ownership. Keep XLIFF 1.2 outside the 2.x model.
14. Preserve namespace-aware extensions and deterministic semantic roundtrip,
    but do not treat preservation-only content or XSD validity as semantic
    module/processing support.
15. Compile XLIFF and all six format projections; require zero missing stable
    profile, module-owner, empty-profile, duplicate, foreign, or dangling edge.
16. Run negative controls for malformed IDs, missing module ownership,
    cross-profile contamination, and preview leakage.
17. Replay at least three clean strict runs plus authority, focused regression,
    Ruff, Pyright, and bounded strict Mypy checks.
18. Reconcile gaps, taskcards, controller and journal atomically; retain UBL
    typing as the exact remaining contract repair.

### Failure routing

- Missing authority: repair lock/materialization; do not bypass.
- XLIFF 2.0 package unavailable: record a profile-specific current gap and
  continue independent 2.1 module work; do not infer 2.0 from 2.1.
- Schema/prose/Schematron contradiction: retain every source location, add a
  discriminating test requirement, and create separate named semantics where
  the authority supports them.
- Schema-valid but processing-invalid example: preserve the distinction;
  schema validation cannot override normative agent requirements.
- Module behavior found only in a product implementation: classify it as a
  product requirement or future interoperability expectation, not as a
  normative format fact.
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
