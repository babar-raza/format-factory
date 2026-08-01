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
notes: Harden plan version 5 for faster product delivery without weakening proof or release gates.
---

# TC-FF6-PLAN-THROUGHPUT-001: Harden FF6 Production Throughput

**Phase:** CONTRACT
**Status:** complete
**Owner:** GitLab mainline plan-control integrator
**Created:** 2026-08-02
**Last updated:** 2026-08-02
**Blocking:** efficient execution of the four Event-46 product lanes
**Blocked by:** none
**Format:** all six FF6 products
**Gate:** no product, certification, promotion, release, or approval transition

## Objective

Replace the stale Event-40 bootstrap wording and remaining globally serialized
interpretation in the canonical FF6 strategic plan with an Event-46-based,
pull-driven execution contract. Increase delivery throughput through complete
homogeneous batches, pre-staged external evidence, product-first lane
allocation, verification tiers, and serialized commit trains. Preserve every
authority, proof, security, packaging, interoperability, compatibility, and
release threshold.

## Verified starting truth

- GitLab `origin/main` and local `main` both resolved to
  `748013f4eb619a109a609a2664c7750cfa184afd` before mutation.
- Native controller Event 46 selects NRRD R2 as the active task and retains
  XLIFF, UBL, and compact-product readiness as disjoint ready lanes.
- The current canonical denominator is 110 capabilities and 689 obligations:
  IPYNB 68, OpenRaster 134, NRRD 65, XLIFF 142, SafeTensors 86, and UBL 194.
- All six products remain `UNASSESSED`; technical certification remains 0/6.
- The existing version-4 impact selector, semantic-batch transaction,
  deterministic scheduler, generated handover, and single-writer integration
  controls are preserved.

## Exact owned outputs

- `plans/strategic/autonomous-six-python-production-execution-plan.md`
- `taskcards/TC-FF6-PLAN-THROUGHPUT-001.md`
- this task's single entry in `taskcards/index.yaml`
- this task's three skill transcripts under
  `reports/skills-rff6/skill-transcripts/`

Product source, product tests, FF6 controller state/journal, contracts,
obligations, proof, gates, promotion, release metadata, and GitHub are read-only.

## Required changes

1. Advance the strategic plan to version 5 and bind its planning baseline to
   the clean Event-46 checkpoint.
2. Replace stale obligation totals and Event-40 queue instructions with the
   current machine-derived Event-46 denominator and task states.
3. Make the scheduler a pull system: one exclusive writer per path and one
   serialized integrator, with all other disjoint lanes allowed to prepare,
   test, or execute concurrently under separate leases.
4. Require at least three of four scheduled lanes to close product contract,
   implementation, corpus/oracle, package, or certification gaps whenever that
   work is ready. Machinery work may consume a lane only when it blocks safe
   product progress or proof correctness.
5. Define complete homogeneous work packages, pre-staged corpus/oracle/tool
   environments, verification tier triggers, commit-train rules, queue health
   metrics, and automatic anti-churn controls.
6. Preserve NRRD R2 as the exact next controller task; planning changes must not
   fabricate product progress or reorder the native controller without an event.

## Acceptance criteria

- [x] Plan version is 5 and the current Event-46 truth is explicit.
- [x] All six canonical obligation totals equal the current committed files.
- [x] The immediate queue names NRRD R2, XLIFF, UBL, and compact readiness with
      exact current states and no obsolete Event-40 bootstrap instruction.
- [x] Batch sizing, lane pull rules, environment pre-staging, tiered
      verification, integration serialization, and anti-churn rules are
      executable and machine-testable.
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
python tools/supervisor/validate_skill_transcript.py reports/skills-rff6/skill-transcripts/plan-hardening-ff6-plan-throughput-001.json
python tools/supervisor/validate_skill_transcript.py reports/skills-rff6/skill-transcripts/create-taskcard-ff6-plan-throughput-001.json
python tools/supervisor/validate_skill_transcript.py reports/skills-rff6/skill-transcripts/plan-control-ff6-plan-throughput-001.json
python plans/codex/handover/validate_handover.py --self-test
```

Additionally parse the plan front matter, verify the six obligation files sum
to 689, search for stale production exit totals, require `git diff --check`,
and require explicit-path precommit review. A failed check yields
`NEEDS_REPAIR`; it never permits a weaker plan or optimistic status.

## Truth boundary

This task improves execution policy only. It does not implement a format
capability, satisfy an obligation, certify a package, approve a gate, or make a
release claim. Event 46 and `TC-FF6-NRRD-READINESS-001` remain the exact
continuation authority after this plan-only checkpoint.
