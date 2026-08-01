---
artifact_id: TC-FF6-ACCEL-CONTROL-001
artifact_type: taskcard
path: taskcards/TC-FF6-ACCEL-CONTROL-001.md
format_id: null
product_family: six-python-production
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
  trigger: input-digest-change
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
goal_id: FF6-PRODUCTION-LIBRARIES-001
parent_task_id: TC-FF6-PROGRAM-CAPABILITIES-001
status: READY
lane: A
skill_ids:
  - product-contract-runtime-repair
  - production-program-controller-repair
  - test-driven-development
  - plan-control
release_blockers: []
notes: Plan-v4 control-plane acceleration; no product or promotion effect.
---

# TC-FF6-ACCEL-CONTROL-001: Fail-Closed and Impact-Aware Control Acceleration

**Phase:** CONTRACT / shared machinery
**Status:** READY
**Owner:** deterministic FF6 Lane A scheduler
**Created:** 2026-08-01
**Last updated:** 2026-08-01
**Blocking:** selective verification and accelerated portfolio scheduling
**Blocked by:** none for the first fail-closed slice
**Format:** portfolio
**Gate:** no gate transition; product certification remains 0/6

## Objective

Remove the machinery defects that make acceleration unsafe. Required authorities
must fail before a contract digest, emitted contract, or proof node can exist;
verification selection must be derived from proof dependencies and checked by a
full-suite sentinel; semantic batches, generated handovers, per-product queues,
and GitLab-main integration must be deterministic and isolated.

This card owns control mechanics only. It cannot adjudicate format semantics,
modify product source, promote a product, or approve a gate.

## Locked baseline and invariants

- Baseline is GitLab `origin/main` commit
  `00357eb2aac2e657ef087a9ea1ca8433f1d06322` plus native Event 40.
- Event 40 remains valid until the bootstrap scheduling event is accepted.
- XLIFF candidate `XLF-CAND-CORE-SCHEMATRON-60B596A00F7FA06A` is not complete.
- All six products remain `UNASSESSED`; technical certification remains `0/6`.
- The impact selector is an optimization only. Any false negative disables
  selective promotion for the affected component.
- Only the controller identity may hold `logical:FF6-CONTROLLER-WRITE`; only the
  integration identity may hold `logical:FF6-MAINLINE-INTEGRATION`.

## Exact execution slices and path allowlists

Each slice requires its own live execution manifest and exact leases. Paths not
listed below require a generated follow-on taskcard before mutation.

### A1 - missing-authority fail-closed repair (execute first)

- `tools/format_contract/product_contract.py`
- `tests/production_program/test_production_program.py`
- `reports/skills-rff6/skill-transcripts/product-contract-runtime-repair-ff6-missing-authority-001.json`

### A2 - proof-impact selector and sentinel comparison

- `tools/requirements_authority/production_graph.py`
- `tools/supervisor/production_program.py`
- `tests/production_program/test_production_program.py`
- `reports/ff6/impact-selector-sentinel.json`
- `reports/skills-rff6/skill-transcripts/production-program-controller-repair-ff6-impact-selector-001.json`

### A3 - batch manifests, product scheduler, generated handovers, integration lock

- `tools/supervisor/production_program.py`
- `tests/production_program/test_production_program.py`
- `plans/strategic/ff6/controller-state.yaml`
- `plans/strategic/ff6/events.jsonl`
- `plans/codex/handover/START-HERE.md`
- `plans/codex/handover/checkpoint.yaml`
- `plans/codex/handover/CURRENT-MACHINE-STATE.yaml`
- `plans/codex/handover/CURRENT-SHIFT-HANDOVER.md`
- `plans/codex/handover/validate_handover.py`
- `reports/skills-rff6/skill-transcripts/production-program-controller-repair-ff6-acceleration-001.json`
- `reports/skills-rff6/skill-transcripts/plan-control-ff6-acceleration-001.json`

Runtime outputs are isolated under
`.local/run-records/ff6/TC-FF6-ACCEL-CONTROL-001/`,
`.local/proof/ff6/TC-FF6-ACCEL-CONTROL-001/`, and
`.local/evidence-contracts/ff6/TC-FF6-ACCEL-CONTROL-001.yaml`.

## Out of scope

- `src/**`, format-specific semantic decisions, package APIs, fixtures, release
  manifests, promotion records, Gate 10, and publication.
- Rewriting or deleting historical ledgers, handovers, events, stale leases, or
  open conflicts.
- Branch creation, GitHub, non-fast-forward integration, broad staging, stash,
  reset, clean, or restore.

## Ordered implementation steps

1. Capture T0 revision/tree, authority lock, six contract digests, tool/test
   digests, event head, target baselines, live leases, and expected descendants.
2. Add a RED test in A1 proving a missing required local authority raises a
   typed fail-closed error before digest finalization. Assert no compiled output
   and no proof node is created. Cover missing path, non-file, unsafe path, and
   digest mismatch separately.
3. Repair compilation as a two-phase operation: validate complete authority
   closure first; only then canonicalize, digest, emit, or construct proof.
   Preserve diagnostic detail and existing valid-authority behavior.
4. Add a content-addressed impact selector in A2. Model source, tests, fixtures,
   authorities, contracts, generators, locks, tools, environment, public API,
   package, and proof nodes. Return stable ordered descendants and reasons.
5. Seed one mutation per input category. Compare T2 selection with a scheduled
   T4 full sentinel. Persist prediction, observed affected set, false positives,
   and false negatives. Fail closed on any false negative.
6. Define canonical semantic-batch manifest and rollback transaction fields:
   group ID, member IDs/decisions, exception queue, predecessor digests,
   invalidation set, tests, artifacts, and acceptance state.
7. Implement deterministic per-product scheduling with severity, downstream
   unlock count, then oldest task ID. One blocked lane releases its slot.
8. Generate the four operational handover projections from controller/proof
   inputs. Three identical runs must be byte-identical; a stale manual value
   must fail validation.
9. Enforce single controller writer and single GitLab-main integration writer.
   Test four disjoint simulated lanes, explicit staging, fast-forward-only
   integration, and absence of retained branch/worktree state.
10. Append controller events only after closure-candidate validation. A failed
    product lane never writes controller or promotion state.

## Verification tiers

- **T0:** every write - lease, manifest, path baseline, authority/contract
  identity, invalidation prediction.
- **T1:** each mutation case, authority rejection case, batch member, lease
  conflict, and scheduler decision.
- **T2:** affected format-contract and production-program suites, Ruff, strict
  Mypy, Pyright, deterministic replay, predecessor equality, receipt validation.
- **T3:** controller transition, generator/handover change, or provider shift -
  detached replay, event chain, current-state consistency, handover validation.
- **T4:** full sentinel for selector calibration; zero false negatives.
- **T5:** not satisfied by this taskcard and never claimed.

## Acceptance criteria

- [ ] Missing required authority fails before digest, output, or proof creation.
- [ ] Existing valid-authority and declared diagnostic behavior is preserved.
- [ ] Three selector runs and three batch-manifest runs are byte-identical.
- [ ] Seeded mutations in every input category select every affected descendant.
- [ ] Full sentinel reports zero selector false negatives.
- [ ] Failed batch member leaves predecessor decisions/counts/identities intact.
- [ ] Four disjoint lanes cannot share mutable artifacts or write authorities.
- [ ] Three handover generations are byte-identical; stale values fail closed.
- [ ] Main integration is single-writer, explicit-path, fast-forward-only.
- [ ] Focused, regression, static, receipt, event-chain, and detached checks pass.
- [ ] No product, certification, release, or gate state changes.

## Failure, rollback, and next-task rules

- Any A1 failure blocks contract/proof emission but not read-only investigation.
- Any selector false negative disables selective promotion for the component and
  restores the conservative full affected-suite path.
- A failed batch is unaccepted as a whole; split heterogeneous members into a
  new stable group with a new taskcard.
- After three materially different repairs of the same root cause, record only
  the affected mechanism as technically blocked and release Lane A.
- Successful A1 automatically selects A2. Successful A2 selects A3. A3 closure
  transfers Lane A to NRRD readiness without promoting any product.

## Evidence required

- RED and GREEN outputs for every fail-closed case.
- Canonical manifests and three-run digests.
- Impact prediction/full-sentinel comparison with zero false negatives.
- Four-lane isolation and integration-lock test output.
- Valid skill transcripts, exact changed-file list, detached replay, native
  event ID/hash, and remote GitLab commit verification.
