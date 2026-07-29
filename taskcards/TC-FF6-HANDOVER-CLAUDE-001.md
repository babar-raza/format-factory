---
artifact_id: TC-FF6-HANDOVER-CLAUDE-001
artifact_type: taskcard
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
goal_id: FF6-PRODUCTION-LIBRARIES-001
status: COMPLETE
skill_ids:
  - refresh-provider-neutral-handover
  - create-taskcard
  - plan-control
---

# Publish a Provider-Neutral Claude/Codex Shift Handover

Status: `COMPLETE`

## Objective

Create a single-entry, evidence-backed, machine-readable handover that lets
Claude and Codex resume the FF6 mission from GitLab main without conversation
memory, provider-local state, lost work, duplicate execution, or false product
promotion.

## Allowed paths

- `plans/codex/handover/**`
- `plans/strategic/ff6/controller-state.yaml`
- `plans/strategic/ff6/events.jsonl`
- `taskcards/TC-FF6-PROGRAM-CAPABILITIES-001.md`
- `taskcards/TC-FF6-AUTHORITY-CLOSURE-001.md`
- this taskcard
- `taskcards/index.yaml`
- local task transcript and evidence metadata

## Acceptance

- One start file links every handover artifact and canonical authority.
- Exact commit, tree, controller event, next task, and evidence limits are
  recorded.
- Symptoms, root causes, structural weaknesses, preservation requirements,
  redesign direction, risks, and uncertainty are separated.
- Start, execution, checkpoint, takeover, validation, integration, and release
  procedures are provider-neutral and executable.
- The absent next taskcard is materialized as `READY`.
- Known global plan-control and line-ending digest contradictions are explicit.
- All internal links, YAML, normalized hashes, event chain, task index, and
  focused regression checks pass.
- Files are committed and pushed to GitLab main with remote verification.
- No product implementation or promotion occurs.

## Initial closure

The packet was integrated and remote-verified at
`1f215cc7ba0ce36225ae8bbc49678b3ca0d5d8fd`. The closing controller event
records the final packet and task-index digests. This task changes no product
promotion state.

## Refresh checkpoint

The packet was refreshed after `TC-FF6-AUTHORITY-CLOSURE-001` passed.
Controller event 16 records 15 of 15 live authority matches, strict
six-contract compilation, clean online and offline replay, deterministic
six-format projections, and no product promotion. The exact successor is
`TC-FF6-ORA-PROFILE-SURFACE-001` in `READY`.

The packet remains a derived navigation and shift artifact. The fetched
GitLab `origin/main` commit, native FF6 journal, controller, task index,
current gaps, and taskcard supersede every earlier packet revision and the
initial integration commit above.

## Event-19 refresh checkpoint

The packet was rebuilt from the remote-verified NRRD source checkpoint
`865558bb88243acda08c2a8d58a0d5ec887dedeb`.

- Native journal head:
  `FF6-EVENT-000019` /
  `76b580d72f865428e92bc5b6089a89487356c69163aadf6b615b70c6867221f8`.
- `TC-FF6-NRRD-PROFILE-SURFACE-001` is `PASS`.
- The current planning denominator is 110 capabilities and 672 obligations;
  NRRD owns 21 capabilities and 65 exact-profile obligations.
- All 15 predecessor authority records match.
- No product, package, certification, promotion, release, or gate changed.
- The exact successor is `TC-FF6-XLIFF-PROFILE-SURFACE-001` in `READY`.
- The successor must first acquire a separately pinned official XLIFF 2.0
  Standard package; the existing XLIFF 2.1 authority cannot stand in for it.
- Core and all six XLIFF 2.1 modules must receive separate, exact normative
  capability ownership. XLIFF 2.2 is preview-only and XLIFF 1.2 is outside the
  2.x model.

This refresh replaces every event-18/NRRD-as-next statement in the packet,
recomputes normalized hashes, and preserves the same provider-neutral,
GitLab-main-only, atomic-shift contract.
