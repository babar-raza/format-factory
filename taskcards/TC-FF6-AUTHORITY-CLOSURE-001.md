---
artifact_id: TC-FF6-AUTHORITY-CLOSURE-001
artifact_type: taskcard
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
goal_id: FF6-PRODUCTION-LIBRARIES-001
parent_task_id: TC-FF6-PROGRAM-CAPABILITIES-001
status: WORK_IN_PROGRESS
skill_ids:
  - sal-pipeline-heal
  - ingest-spec-sal
  - compile-format-contract
  - compile-production-capability-universe
  - create-taskcard
  - plan-control
---

# Close the Six-Format Authority-Artifact Dependency Closure

## State

- Status: `WORK_IN_PROGRESS`
- Parent: `TC-FF6-PROGRAM-CAPABILITIES-001` (`NEEDS_REPAIR`)
- Predecessor: `TC-FF6-CAPABILITY-COMPILER-001` (`PASS`)
- Source gap: `FF6-GAP-014`
- Controller predecessor event: `FF6-EVENT-000013`
- Product source mutation: prohibited
- Product promotion effect: none

## Durable provider-shift checkpoint

Controller event `FF6-EVENT-000014` records a bounded, non-promoting
implementation checkpoint. The task is not complete and none of the 15
authority records is yet promotably closed.

Completed and independently rerunnable:

- `tools/format_contract/authority_lock.py` implements schema-backed lock
  loading, repository-path containment, semantic validation, deterministic
  source projection, and deterministic internal-requirement generation.
- `tools/format_contract/authority_runtime.py` implements content-addressed
  caching, digest-before-placement, online/offline URL materialization,
  bounded ZIP-member extraction, and live authority/contract audit results.
- `tools/format_contract/authority_materializer.py` exposes deterministic
  `materialize`, `audit`, and `sync-product-requirements` commands.
- `schemas/format-contracts/authority-lock.schema.json` defines the shared
  source, legal, limit, and fetch record vocabulary.
- Four tracked `PRODUCT_REQUIREMENT` artifacts were generated for IPYNB,
  NRRD, XLIFF, and UBL and remain explicitly non-spec authority.
- Six focused tests pass; Ruff and mypy pass for the new machinery.

Not completed and not implied by that evidence:

- the canonical 15-source `authority-lock.yaml`;
- the immutable NRRD locator decision and its primary-source/legal evidence;
- registered `research-format-contract-sources` skill/command integration;
- redirect-count enforcement and same-process concurrency testing;
- ProductContract, input-closure, and capability-compiler integration;
- real online materialization, offline replay, six strict contract compiles,
  three clean capability compiles, or parent-task closure.

The exact next step is Step 3 below: finish the source-by-source immutable
authority and legal matrix, beginning with NRRD, then create the 15-source
lock. Do not rewrite the completed modules merely because the executor changed.

## Objective

Make every authority dependency used by the six canonical format contracts
reproducible, legally classified, digest-verified, and available to a clean
compiler run. Eliminate false `ACQUIRED` labels whose bytes cannot be
reconstructed, while preserving all valid contract, SAL, and proof work.

This task closes authority-artifact mechanics only. It does not certify the
authority depth or format surface, and it does not close the remaining
OpenRaster profile/surface gap.

## Verified starting inventory

`plans/strategic/ff6/capability-manifest.json` at source checkpoint
`916dec86e05e304c49ba04a01692bd9f726b8f85` records 15 authority dependencies:

- 0 `MATCH`;
- 11 `MISSING` at declared repository-relative cache paths;
- 4 `UNDECLARED` internal product-requirement sources without reproducible
  local path and content digest;
- all six formats `BLOCKED`.

The exact expected paths, source IDs, and SHA-256 values in that manifest are
the starting inventory. Recompute them before mutation.

## Root cause

The contracts store `acquisition_status: ACQUIRED`, but acquisition state is
not part of a clean reproducible dependency closure:

- external bytes live only under ignored `.local` paths;
- no single lock manifest explains fetch URL, immutable version, digest,
  license, redistribution decision, and cache materialization;
- internal product requirements have authority IDs but no tracked canonical
  artifact or digest;
- contract compilation checks the current filesystem, while historic status
  labels survive after bytes disappear;
- clean-checkout replay and installed-package proof therefore cannot trust
  authority readiness.

## Required design

Create one authority-lock and materialization contract reused by all six
formats:

1. Each authority source has a stable source ID, authority class, immutable
   locator/version, expected SHA-256, media type, license/terms reference,
   redistribution classification, cache policy, and verification command.
2. Redistributable sources may be stored in a tracked content-addressed
   authority root only after license evidence allows it.
3. Non-redistributable sources remain outside Git, but an exact lock record and
   deterministic fetch/materialization command must recreate them into the
   declared cache path.
4. Internal `PRODUCT_REQUIREMENT` sources become tracked, reviewable canonical
   documents with their own stable paths and digests. They must not masquerade
   as external specification authority.
5. Fetching writes a temporary file, verifies the expected digest before
   atomic placement, and never replaces a valid cached artifact with mismatched
   bytes.
6. Offline mode either verifies a matching cache or fails with a named missing
   dependency. It never silently substitutes secondary or generated text.
7. Compilation consumes the lock/materialized closure and reports
   `MATCH`, `MISSING`, `MISMATCH`, `UNDECLARED`, or `LEGAL_BLOCKED` per source.
8. Every authority input and tool is included in the capability manifest
   invalidation closure.

## Exact execution steps

1. Revalidate GitLab `origin/main`, controller event 13, task state, worktree,
   coordination ownership, and the 15-source manifest inventory.
2. Query `.local/artifact-index.yaml`, current acquisition tools, SAL evidence,
   contract registry, spec cache, and prior receipts before creating anything.
3. For each source, inspect the primary official endpoint and immutable version.
   Do not trust contract labels without checking the actual bytes and endpoint.
4. Build a source-by-source legal/redistribution matrix. Preserve quotations
   as evidence-only; do not commit copyrighted standards unless redistribution
   is affirmatively supported.
5. Select or repair one registered authority acquisition/materialization
   pipeline. If the current skills cannot express the shared lock/cache
   contract, run `validate-missing-skill-workflow` and create the smallest
   reusable skill before mutation.
6. Write the shared authority lock schema, lock records, materializer,
   negative tests, and cache verification tests. Avoid one-off per-format
   download scripts.
7. Convert the four internal product-requirement sources into tracked canonical
   requirement artifacts with clear non-spec authority classification.
8. Materialize all legally retrievable external sources and verify their
   SHA-256 values. A mismatch is a contradiction to investigate, not a reason
   to edit the expected digest to whatever downloaded.
9. Recompile all six ProductContracts without
   `--allow-blocked-authority`. Repair only evidence-backed contract source
   declarations or expected digests.
10. Recompile the capability universe three times, in clean isolated
    environments, without `--allow-blocked-authority`.
11. Prove offline cached replay and clean online materialization separately.
12. Run authority, SAL, contract, capability, event-chain, concurrency, static,
    security, and affected regression suites.
13. Update current gaps, parent task, task index, controller, and append-only
    event journal atomically. Do not close the parent while `FF6-GAP-013`
    remains.
14. Create and validate a complete transcript and evidence bundle; commit and
    push only explicit owned files to GitLab `main`.

## Allowed tracked outputs

- shared authority lock/schema/manifests and internal product-requirement
  artifacts selected by the governed skill;
- authority acquisition/materialization tools and their focused tests;
- evidence-backed changes to the six format contracts, SAL evidence, contract
  registry, and verification reports;
- regenerated FF6 capability universe and manifest;
- `plans/strategic/ff6/current-gaps.yaml`;
- `plans/strategic/ff6/controller-state.yaml`;
- `plans/strategic/ff6/events.jsonl`;
- this taskcard, parent taskcard, successor taskcard, and task index;
- governed receipts, transcripts, and evidence.

Every exact path must be claimed and approved by the selected registered skill
before writing.

## Forbidden outputs

- `src/**` and product tests;
- package or release metadata;
- certifications, promotions, gate approvals, or publication records;
- unlicensed external specification bytes;
- secrets, credentials, cookies, or bearer URLs;
- new branches or GitHub remotes;
- mutable `latest` URLs without an immutable version and digest;
- synthetic replacements for unavailable authority.

## Acceptance criteria

- [ ] All 15 source records have nonempty path/locator, expected digest,
      authority class, legal status, redistribution policy, and cache policy.
- [ ] All four internal product-requirement sources resolve to tracked
      canonical artifacts and remain explicitly non-spec authority.
- [ ] Every legally retrievable external source is `MATCH`.
- [ ] No source remains falsely labeled `ACQUIRED`.
- [ ] No source is `MISSING`, `MISMATCH`, or `UNDECLARED` in the promoting run.
- [ ] Any true legal/access block is `LEGAL_BLOCKED` with primary evidence and
      does not get hidden by `--allow-blocked-authority`.
- [ ] The materializer is path-safe, size-bounded, redirect-bounded,
      timeout-bounded, digest-before-placement, and concurrency-safe.
- [ ] Clean online materialization and offline matching-cache replay pass.
- [ ] ProductContract compilation passes all six without authority override.
- [ ] Three capability compiles are byte-identical and all authority artifacts
      are `MATCH`.
- [ ] Every changed authority input invalidates the correct manifest
      descendants.
- [ ] Existing working contract/SAL behavior and all compiler regressions pass.
- [ ] Parent remains `NEEDS_REPAIR` and unpromoted for OpenRaster gap 13.

## Failure policy

- Retry transient official-endpoint failures with bounded backoff and approved
  alternate official mirrors.
- Never change an expected digest solely to make a mismatch pass.
- Never commit external bytes until legal/redistribution evidence allows it.
- After three materially different failed repairs for one source, mark that
  source technically or legally blocked with evidence and continue the other
  sources.
- Missing credentials for public standards are not assumed; inspect official
  anonymous access and repository mirrors first.

## Required verification

```text
authority lock/schema validation
materializer unit, security, concurrency, online, and offline tests
SAL fact/evidence verification
six strict ProductContract compiles
canonical capability compiler --check --verify-idempotency without override
focused plus affected format-contract and production-program regressions
Ruff, mypy, pyright for new machinery
event-chain and controller projection verification
coordination precommit check
validated transcript and evidence bundle
GitLab remote commit verification
```

## Exit

- `PASS`: all authority sources are reproducible and strict compilation passes;
  register and select the OpenRaster profile/surface repair task.
- `NEEDS_REPAIR`: a concrete source/tool/contract defect remains.
- `TECHNICALLY_BLOCKED`: only for a source after three materially different
  repair attempts, while other sources continue.

No exit state from this task certifies or promotes a format.
