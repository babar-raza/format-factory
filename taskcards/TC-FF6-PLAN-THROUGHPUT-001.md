---
artifact_id: TC-FF6-PLAN-THROUGHPUT-001
artifact_type: taskcard
path: taskcards/TC-FF6-PLAN-THROUGHPUT-001.md
format_id: null
product_family: six-python-production
visibility: internal
publish_allowed: false
license: null
provenance_required: true
provenance_status: complete
source_hash: null
generated_by: codex
generated_at: 2026-08-02
reusable: false
refresh_policy:
  trigger: controller-or-plan-throughput-contract-change
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
goal_id: FF6-PRODUCTION-LIBRARIES-001
status: complete
skill_ids:
  - plan-hardening
  - create-taskcard
  - plan-control
release_blockers: []
notes: Harden plan version 6 for faster product delivery without weakening proof or release gates.
---

# TC-FF6-PLAN-THROUGHPUT-001: Harden FF6 Production Throughput

**Phase:** CONTRACT
**Status:** complete
**Owner:** GitLab mainline plan-control integrator
**Created:** 2026-08-02
**Last updated:** 2026-08-02
**Blocking:** efficient execution of the six Event-47 product queues
**Blocked by:** none
**Format:** all six FF6 products
**Gate:** no product, certification, promotion, release, or approval transition

## Objective

Maintain the Event-47-based pull-driven execution contract and remove the
remaining fixed-lane, single-buffer, static-batch bottlenecks. Increase delivery
throughput through six persistent product queues, a four-write WIP cap,
double-buffered successors, vertical capability slices, adaptive homogeneous
batches, pre-staged external evidence, verification tiers, and serialized commit
trains. Preserve every authority, proof, security, packaging, interoperability,
compatibility, and release threshold.

## Verified starting truth

- GitLab `origin/main` and local `main` both resolved to
  `2ec206edc0104e5f64441c6d043f8d9cd5186fd8` before the version-6 mutation.
- Native controller Event 47 selects NRRD R3 as the active task and retains
  XLIFF, UBL, and compact-product readiness as disjoint ready work; OpenRaster
  non-source preparation is also schedulable.
- The current canonical denominator is 110 capabilities and 689 obligations:
  IPYNB 68, OpenRaster 134, NRRD 65, XLIFF 142, SafeTensors 86, and UBL 194.
- All six products remain `UNASSESSED`; technical certification remains 0/6.
- The existing version-4 impact selector, semantic-batch transaction,
  deterministic scheduler, generated handover, and single-writer integration
  controls are preserved.
- NRRD R2 is accepted: 17 implemented, 39 partial, 6 missing, and 3
  preservation-only classifications; 48 unresolved obligations remain.

## Exact owned outputs

- `plans/strategic/autonomous-six-python-production-execution-plan.md`
- `taskcards/TC-FF6-PLAN-THROUGHPUT-001.md`
- this task's single entry in `taskcards/index.yaml`
- this task's three skill transcripts under
  `reports/skills-rff6/skill-transcripts/`

Product source, product tests, FF6 controller state/journal, contracts,
obligations, proof, gates, promotion, release metadata, and GitHub are read-only.

## Required changes

1. Advance the strategic plan to version 6 and bind its planning baseline to
   the clean Event-47 checkpoint.
2. Replace the fixed four-role lane model with six persistent product queues and
   a maximum of four simultaneous canonical mutation packages.
3. Require one READY and at most one PREPARED successor for every active
   unblocked product; refresh successor baselines after integration.
4. Prefer coherent vertical capability slices and apply deterministic adaptive
   batch risk bands rather than a universal 5-15-obligation size.
5. Require five of every rolling six accepted batches to close product evidence
   unless a current critical/high control defect blocks safe progress.
6. Pre-stage and content-address authority, corpus, oracle, dependency, platform,
   and package kits while preserving executed-result invalidation.
7. Preserve NRRD R3 as the exact next controller task; planning changes must not
   fabricate product progress or reorder the native controller without an event.

## Acceptance criteria

- [x] Plan version is 6 and the current Event-47 truth is explicit.
- [x] All six canonical obligation totals equal the current committed files.
- [x] The immediate queue names NRRD R3 and persistent XLIFF, UBL, IPYNB,
      SafeTensors, and OpenRaster queues with no obsolete Event-40/Event-46
      scheduling authority.
- [x] Adaptive batch sizing, queue/WIP and double-buffer rules, environment
      pre-staging, tiered verification, integration serialization, and
      anti-churn rules are executable and machine-testable.
- [x] No quality, proof, security, corpus, oracle, platform, packaging,
      extraction, or release threshold is reduced.
- [x] Plan hardening remains 22/22 at the design level.
- [x] No product, controller, certification, promotion, release, gate, or
      publication state changes.

## Validation

Run and require all of the following:

```powershell
python tools/evidence/check_current_state_consistency.py
python tools/governance/validate_plan_skill_routes.py plans/strategic/autonomous-six-python-production-execution-plan.md
python tools/supervisor/validate_skill_transcript.py reports/skills-rff6/skill-transcripts/plan-hardening-ff6-plan-throughput-v6-001.json
python tools/supervisor/validate_skill_transcript.py reports/skills-rff6/skill-transcripts/create-taskcard-ff6-plan-throughput-v6-001.json
python tools/supervisor/validate_skill_transcript.py reports/skills-rff6/skill-transcripts/plan-control-ff6-plan-throughput-v6-001.json
python plans/codex/handover/validate_handover.py --self-test
```

Additionally parse the plan front matter, verify the six obligation files sum
to 689, search for stale production exit totals, require `git diff --check`,
and require explicit-path precommit review. A failed check yields
`NEEDS_REPAIR`; it never permits a weaker plan or optimistic status.

## Truth boundary

This task improves execution policy only. It does not implement a format
capability, satisfy an obligation, certify a package, approve a gate, or make a
release claim. Event 47 and `TC-FF6-NRRD-READINESS-001` R3 remain the exact
continuation authority after this plan-only checkpoint.

## Version-6 closure evidence

- The v5 plan was preserved as the historical base; v6 changes only scheduling,
  batching, successor preparation, and verification-kit reuse policy.
- Six logical product queues are explicit; simultaneous canonical writes remain
  capped at four and GitLab-main integration remains single-writer.
- Product-work ratio is five of six accepted batches; planning/control work
  remains exceptional and cannot waive a product gate.
- Current NRRD truth is Event 47 and semantic commit `ea118ba3`; no product,
  promotion, certification, release, publication, or gate state changed.
