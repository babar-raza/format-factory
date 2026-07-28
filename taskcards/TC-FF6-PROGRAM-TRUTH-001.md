---
artifact_id: TC-FF6-PROGRAM-TRUTH-001
artifact_type: taskcard
path: taskcards/TC-FF6-PROGRAM-TRUTH-001.md
format_id: null
product_family: python_format_libraries
visibility: internal
publish_allowed: false
license: null
provenance_required: true
provenance_status: captured
source_hash: null
generated_by: codex
generated_at: 2026-07-28
reusable: false
refresh_policy:
  trigger: any tracked input digest change
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
skill_ids:
  - build-context-pack
  - create-taskcard
  - plan-control
---

# TC-FF6-PROGRAM-TRUTH-001: Establish the six-library production truth baseline

**Goal:** `FF6-PRODUCTION-LIBRARIES-001`
**Phase:** Wave 0 — evidence quarantine and baseline
**Status:** complete
**Owner:** autonomous FF6 controller
**Created:** 2026-07-28
**Last updated:** 2026-07-28
**Blocking:** capability compilation and all product mutation
**Blocked by:** none
**Format:** portfolio (`ipynb`, `ora`, `nrrd`, `xliff`, `safetensors`, `ubl`)
**Controller transition:** `DISCOVER -> SNAPSHOT`

---

## Objective

Replace historical readiness narratives with a digest-bound snapshot of the
actual source, packages, tests, contracts, SAL facts, corpora, oracle results,
install proof, architecture status, and controller state for all six products.
The snapshot must identify evidence strength and gaps without promoting any
library.

## Exact scope

### In scope

- Read all six format contracts, SAL facts, SAL verification reports, source
  and test trees, sample roots, oracle packages/summaries, package matrix, and
  package proof manifest.
- Refresh the advisory repository context pack from the pinned clean commit.
- Materialize the immutable FF6 product goal, append-only controller event
  chain, current-state snapshot, controller checkpoint, taskcard, and index.
- Run clean-checkout inventory, package-proof freshness, architecture, and test
  bootstrap diagnostics.

### Out of scope

- Product source or product test mutation.
- Capability or obligation completion claims.
- Contract promotion, gate approval, package release, or publication.
- Repairing stale package proof, shallow oracles, architecture violations, or
  missing OpenRaster source in this taskcard.

## Allowed paths

- `.supervisor/context-pack.yaml`
- `plans/strategic/ff6/**`
- `taskcards/TC-FF6-PROGRAM-TRUTH-001.md`
- `taskcards/index.yaml`
- `.local/ff6-truth-001-context/**`
- `.local/transcripts/ff6-program-truth-001.json`

All other tracked paths are read-only.

## Acceptance criteria

- [x] GitLab `origin/main` is pinned to an exact commit and tree.
- [x] Every selected contract, SAL source, source tree, test tree, corpus,
  oracle, and install-proof state is classified with exact evidence.
- [x] Contract-compilation, SAL, test-count, oracle, and install-smoke evidence
  are explicitly prevented from over-promoting products.
- [x] Missing OpenRaster product artifacts are represented as gaps, not zeros
  interpreted as completion.
- [x] Existing five-package source and test depth is recorded without treating
  public-symbol or test counts as production capability.
- [x] Controller projection and event-chain hashes validate.
- [x] Focused plan-control, YAML/JSON, taskcard, and consistency checks pass.
- [x] Skill transcript validates and the exact GitLab main commit is recorded.

## Evidence required

- `plans/strategic/ff6/product-goal.yaml`
- `plans/strategic/ff6/current-state.yaml`
- `plans/strategic/ff6/controller-state.yaml`
- `plans/strategic/ff6/events.jsonl`
- `.supervisor/context-pack.yaml`
- validated skill transcript and exact changed-file list
- command results for source architecture, V226 freshness, clean-checkout test
  bootstrap, plan-control tests, and current-state consistency

## Failure and repair policy

Any missing, contradictory, or stale evidence remains a named gap in
`current-state.yaml`. A failed diagnostic cannot be rewritten as passing and
does not prevent independent inventory work. This task closes only when the
snapshot and controller event chain validate; it never closes a product gap.

## Deterministic next task

`TC-FF6-PROGRAM-CAPABILITIES-001` compiles the complete classified capability
and normative obligation universe from this snapshot and current authorities.

## Closure

Result: `PASS`. This closes only the truth-recovery task. All six products
remain `UNASSESSED`; no format implementation or certification gap is closed.
