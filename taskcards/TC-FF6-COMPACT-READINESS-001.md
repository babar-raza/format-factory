---
artifact_id: TC-FF6-COMPACT-READINESS-001
artifact_type: taskcard
path: taskcards/TC-FF6-COMPACT-READINESS-001.md
format_id: null
product_family: compact-json-and-binary
visibility: internal
publish_allowed: false
license: null
provenance_required: true
provenance_status: pending-execution
source_hash: null
generated_by: codex
generated_at: 2026-08-01
reusable: false
refresh_policy:
  trigger: source-api-test-package-contract-or-proof-change
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
goal_id: FF6-PRODUCTION-LIBRARIES-001
parent_task_id: TC-FF6-PROGRAM-CAPABILITIES-001
status: SUPERSEDED
lane: HISTORICAL
skill_ids:
  - build-product-context
  - inventory-format-dom
  - package-install-proof
  - validate-product-code-ledger
  - plan-control
release_blockers: []
notes: Superseded without execution by separate IPYNB and SafeTensors readiness cards in plan version 7.
---

# TC-FF6-COMPACT-READINESS-001: IPYNB and SafeTensors Production Readiness Characterization

**Phase:** SNAPSHOT / architecture preparation
**Status:** SUPERSEDED (not executed)
**Owner:** historical version-6 queue record
**Created:** 2026-08-01
**Last updated:** 2026-08-01
**Blocking:** safe residual implementation task compilation for two compact formats
**Blocked by:** none for read-only characterization
**Format:** ipynb, safetensors
**Gate:** no source mutation or promotion

## Supersession record

This combined card is retained for audit history but must not be scheduled.
Plan version 7 separates it into:

- `TC-FF6-IPYNB-READINESS-001`; and
- `TC-FF6-SAFETENSORS-READINESS-001`.

No obligation, evidence, or product progress was credited by this
supersession. The successor cards keep independent baselines, oracles, package
proof, gaps, and controller routes so a failure in one format cannot block or
contaminate the other.

## Objective

Establish an evidence-backed, installed-use truth baseline for the existing
IPYNB and SafeTensors libraries so useful behavior is preserved and weak or
unsafe architecture is not carried forward. Map every source/public symbol,
test, package artifact, oracle result, and documentation example to current
contract obligations, then classify each implementation unit `KEEP`, `REPAIR`,
`REPLACE`, or `REMOVE` with evidence and an exact residual task.

This task is characterization only. It cannot mutate either product source,
change public APIs, count stale wheel evidence, or promote a product.

## Locked baseline

- IPYNB: draft contract, 25 capabilities, 68 obligations; source exists.
- SafeTensors: draft contract, 11 capabilities, 86 obligations; source exists.
- SafeTensors official 0.8.0 interop passed once from source, but broader wheel
  collection exposed a stale installed wheel missing `PayloadAccessMode`.
- Neither package is assessed or certified. Prior reports are hypotheses until
  replayed against the current GitLab commit and rebuilt wheels.

## Exact path allowlist and logical leases

Read-only inputs:

- `src/python/ipynb/**`
- `src/python/safetensors/**`
- `tests/python/ipynb/**`
- `tests/python/safetensors/**`
- `shared/format-contracts/ipynb.yaml`
- `shared/format-contracts/safetensors.yaml`
- `plans/strategic/ff6/capabilities/ipynb.yaml`
- `plans/strategic/ff6/capabilities/safetensors.yaml`
- `plans/strategic/ff6/obligations/ipynb.yaml`
- `plans/strategic/ff6/obligations/safetensors.yaml`
- `packaging/python/package-matrix.yaml`
- `reports/package-install-proof/**`
- `reports/r90/product-code-change-ledger.json`

Writable outputs, under `logical:FF6-COMPACT-READINESS`:

- `reports/ff6/ipynb-production-readiness.yaml`
- `reports/ff6/safetensors-production-readiness.yaml`
- `reports/ff6/compact-readiness-residual-tasks.yaml`
- `reports/skills-rff6/skill-transcripts/build-product-context-compact-readiness-001.json`
- `reports/skills-rff6/skill-transcripts/package-install-proof-compact-readiness-001.json`
- `reports/skills-rff6/skill-transcripts/validate-product-code-ledger-compact-readiness-001.json`

Built wheels, virtual environments, manifests, and proof transactions remain
untracked under `.local/run-records/ff6/TC-FF6-COMPACT-READINESS-001/` and
`.local/proof/ff6/TC-FF6-COMPACT-READINESS-001/`. Product source/tests are
strictly read-only; new characterization tests require a separate taskcard.

## Ordered implementation steps

1. T0-bind GitLab commit/tree, both contract/authority digests, source/test/docs/
   package-lock digests, environment, adapters, existing evidence, and import paths.
2. Inventory modules, LOC/complexity, import graph, public exports/signatures,
   models, readers, writers, validators, security policies, workflows, adapters,
   analytics, CLI, docs, examples, tests, fixtures, and package metadata.
3. Detect stubs, pass-throughs, hard-coded samples, untyped primary models,
   monoliths, layer violations, optional-dependency leaks, source-tree import
   confusion, undocumented exports, and behavior with no executed test.
4. Rebuild sdist/wheel separately for each package in clean locked environments.
   Install with `--no-deps` where appropriate, then locked dependencies. Assert
   every import resolves inside the installed distribution, not the repository.
5. Replay focused and full existing suites against the installed wheel. Preserve
   failures as current gaps; no skip, filename, or source-only pass is evidence.
6. Run official differential checks (`nbformat`, official `safetensors`) in
   isolated environments and record exact versions/digests. Record contradictions.
7. Map every contract capability and obligation to public/source symbols,
   positive/negative/roundtrip/security tests, fixtures, oracles, docs, and live
   proof. Missing or stale edges remain explicit gaps.
8. Classify every implementation unit:
   - `KEEP`: correct structure and current executed proof;
   - `REPAIR`: sound boundary with bounded correctness/quality gaps;
   - `REPLACE`: behavior useful but architecture/security/model is unsalvageable;
   - `REMOVE`: non-format analytics, unsafe alias, dead/stub behavior, or duplicate.
9. Generate residual IPYNB then SafeTensors taskcards ordered by security/data
   loss, mandatory read/write, interop, packaging, API/docs, and utilities.
10. Emit a closure candidate for the controller. Do not edit product/controller state.

## Verification tiers

- **T0:** exact digest and installed-import baseline.
- **T1:** each characterization assertion is reproducible from source, wheel,
  test result, or independent oracle; unsupported judgments fail closed.
- **T2:** complete mapping/reference integrity, rebuilt-wheel tests, official
  differential checks, architecture/static inventory, deterministic reports,
  product-ledger validation, receipt validation.
- **T3:** fresh detached checkout rebuild/install/replay for both products.
- **T4:** full cross-platform, dependency, fuzz, mutation, and performance work
  is scheduled by residual cards and is not claimed here.
- **T5:** not satisfied by characterization.

## Acceptance criteria

- [ ] Every public/source symbol and test is inventoried with stable identity.
- [ ] Every one of 68 IPYNB and 86 SafeTensors obligations has a current mapping or explicit gap.
- [ ] Fresh wheels build/install and import-location assertions are recorded.
- [ ] Stale SafeTensors wheel evidence cannot be reused.
- [ ] Official differential results include versions/digests and contradictions.
- [ ] Every implementation unit has one evidenced KEEP/REPAIR/REPLACE/REMOVE decision.
- [ ] Reports are byte-identical across three same-input runs.
- [ ] Residual taskcards own every mandatory gap with exact paths and proof needs.
- [ ] Product source/tests, APIs, promotion, release, and gates remain unchanged.

## Failure and next-task rules

- A package build/import failure becomes a high-priority current gap and does not
  block characterization of the other package.
- Oracle disagreement creates a discriminating task; never choose the result
  that makes existing code pass.
- Unprovable classification defaults to `REPAIR_PENDING_EVIDENCE`, not `KEEP`.
- Complete IPYNB characterization schedules IPYNB residual batches first;
  SafeTensors follows independently. Source mutation requires those new cards.

## Evidence required

- Exact inventories, import graph/API snapshots, installed-wheel build/install/
  test logs, source-vs-wheel isolation assertion, oracle versions/digests,
  obligation mapping, classification rationales, three-run report digests,
  valid transcripts, exact changed paths, detached replay, and residual cards.
