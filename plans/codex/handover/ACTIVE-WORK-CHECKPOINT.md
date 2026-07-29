---
artifact_id: FF6-ACTIVE-WORK-CHECKPOINT-001
artifact_type: provider_neutral_work_checkpoint
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
authoritative_state: false
canonical_event: FF6-EVENT-000018
---

# Active Work Checkpoint: NRRD Profile Applicability

This is the provider-neutral shift boundary after the IPYNB contract
repair. Canonical authority remains the controller, event journal, current-gap
projection, and taskcards; this document explains how to resume them.

## Exact checkpoint

| Field | Value |
|---|---|
| Mission | `FF6-PRODUCTION-LIBRARIES-001` |
| Forge and branch | GitLab `origin/main` only |
| Controller state | `CONTRACT` |
| Controller sequence | `18` |
| Event head | `73b0f6074d13cae4c519176bf34908d2906653e831adc7d6dc1934310ec38362` |
| Parent task | `TC-FF6-PROGRAM-CAPABILITIES-001` - `NEEDS_REPAIR` |
| Completed task | `TC-FF6-IPYNB-PROFILE-SURFACE-001` - `PASS` |
| Exact next task | `TC-FF6-NRRD-PROFILE-SURFACE-001` - `READY` |
| Selected finding | `FF6-NRRD-PROFILE-001` |
| Product source mutation | Prohibited |
| Promotion effect | None |
| Certified libraries | 0 of 6 |

## What was proved

- All 15 authority artifacts remain live `MATCH`.
- All 20 OpenRaster SAL facts now pass exact assertions against the current
  commit-pinned RST authorities. Obsolete HTML proof hashes are gone.
- The previous `SAL-ORA-00014` claim was absent from current authority. The
  correction and reason are retained in fact provenance.
- OpenRaster now uses the dedicated `layered_raster_archive` family with 17
  format-family domains plus three shared lifecycle/preservation/security
  capabilities.
- ORA has 20 explicit developer capabilities and 134 canonical obligations.
- Every ORA capability and obligation declares exact applicability across
  0.0.3/0.0.4/0.0.5. Isolation applies only to 0.0.4/0.0.5.
- Masks are explicitly a safe product extension surface, not claimed as an
  OpenRaster baseline construct.
- `FF6-ORA-SURFACE-001` and `FF6-ORA-PROFILE-001` are absent from live
  compiler output. `FF6-GAP-013` is resolved.
- No product behavior, package, certification, promotion, release, or gate was
  changed or proved.
- The pinned nbformat 4.0-4.5 schemas were compared recursively. The retained
  matrix records 62 source-located leaf changes and all six exact member
  hashes.
- IPYNB now has 25/25 exact SAL facts, 25 profile-homogeneous capabilities,
  and 68 canonical obligations. Every capability and obligation has a
  non-empty exact profile subset.
- Explicit complete fact ownership rejects unknown, duplicate, and unassigned
  IPYNB facts. Cell names cover 4.0-4.5; notebook title/authors and name
  uniqueness begin in 4.2; hidden metadata begins in 4.3; execution timing in
  4.4; cell IDs in 4.5.
- Notebook execution remains `EXCLUDED_WITH_AUTHORITY`. Event 18 closes only
  the IPYNB contract/profile defect; it does not certify the existing product.

## Current compiled planning state

| Measure | Value |
|---|---:|
| Capabilities | 104 |
| IPYNB obligations | 68 |
| OpenRaster obligations | 134 |
| NRRD obligations | 94 |
| XLIFF obligations | 125 |
| SafeTensors obligations | 86 |
| UBL obligations | 194 |
| Total obligations | 701 |
| Aggregate SHA-256 | `e0747efbf376f081fd6550afed48100c7e1872a055bf6155332ed9358ac05b5f` |
| Three-run digest | `dc33648ffa8f8b676de98f7b145dc2180630d5c470148ca0f46b13ec1492b554` |
| Authority matches | 15/15 |
| Product certifications | 0 |

The portfolio remains `NEEDS_PROFILE_OR_SURFACE_REPAIR` because
NRRD0001-NRRD0004, XLIFF 2.0, and UBL full-typing gaps remain.

## Verification boundary

- `tests/format_contract`, the capability compiler tests, and the SAL verifier:
  126 passed; the baseline-known CSV idempotency test was deselected because it
  mutates three unrelated tracked reports before exposing its pre-existing
  gap-ledger mismatch.
- Ruff: pass.
- Strict mypy for the new family-pack validator: pass. The legacy contract
  compiler import graph is not strict-mypy-clean and is not claimed as passed.
- Pyright 1.1.411 on all three affected compiler modules: zero errors.
- Family-pack validation: 22 domains, explicit-complete fact ownership,
  valid, idempotent.
- IPYNB SAL exact verification: 25/25 pass.
- Three strict six-format compilations: byte-identical.
- Authority audit: 15/15 match.

## Exact resume procedure

1. Read `START-HERE.md`, `CURRENT-MACHINE-STATE.yaml`, `AGENTS.md`, and the
   provider adapter in their declared order.
2. Fetch GitLab `origin/main`; do not use GitHub or create a branch.
3. Require `50c2fd0610a1028ee08e2fdb0ef91494159af559` to be an ancestor of
   fetched `origin/main`.
4. Require a clean or fully classified shared worktree.
5. Register a fresh coordination identity and inspect live leases/conflicts.
6. Validate event 18 natively using `previous_event_hash` and canonical JSON
   with `event_hash` removed.
7. Verify the controller names
   `TC-FF6-NRRD-PROFILE-SURFACE-001` as `READY`.
8. Read that taskcard, the product goal, current gaps, capability policy, NRRD
   contract/SAL/evidence/enrichment, and both pinned NRRD authorities.
9. Claim exact paths, resolve registered skills, and run the mutation guard
   before every write.
10. Execute the atomic steps NRD-01 through NRD-08 in
    `STATE-MACHINE-AND-TASKCARD-PROTOCOL.md`.
11. Produce a source-located NRRD0001-NRRD0005 delta matrix.
12. Split capabilities where rules have different minor-version
    applicability; never assign all rules to 4.5 merely because the newest
    schema contains them.
13. Preserve attached/detached payloads, data types/endian/dimensions,
    spatial and axis metadata, all required encodings, data-file lists and
    patterns, streaming/memory mapping conditions, high-fidelity headers,
    deterministic writing, and resource/path protections.
14. Recompile all six projections and require three identical runs plus 15/15
    authority matches.
15. Reconcile gaps/task/controller/event/handover, commit explicit owned paths,
    and push only GitLab `origin/main`.

If the provider shift ends before NRD-08, only stop after the current atomic
step is integration-safe. Journal the completed steps and first unmet step as
`WORK_IN_PROGRESS`, refresh this packet, commit, push, and verify the remote.
Never leave a required result only in conversation or an uncommitted tree.

## Do not infer

This checkpoint does not mean:

- any of the 701 obligations is implemented merely by this contract work;
- any current source package is production-ready;
- any format has independent interoperability certification;
- the broad cross-platform installed-wheel matrix is current;
- architecture work is unlocked;
- publication is authorized.

Only digest-bound executed behavior can move those states.

## Outgoing self-challenge

The event-18 executor recorded the required governance challenge at the shift
boundary:

1. Required contract-task steps performed: yes.
2. Required task evidence present; none missing: yes.
3. Evidence sufficient for the contract-only acceptance boundary: yes.
4. Secondary source substituted where primary authority was required: no.
5. Phase-forbidden file created: no.
6. Product gate self-approved: no.
7. Later product phase entered: no.
8. Commit/push performed without the approved autonomous GitLab-main policy:
   no.
9. Checkpoint inspection preserved before successor execution: yes.
10. Discovered gap left unlogged: no.
11. Relevant memory read: yes.
12. Memory treated only as context: yes.
13. Memory checked against canonical repository state; no contradiction needed
    a gap: yes.
14. Memory update: not applicable; no update was requested.
15. Human review: not applicable; none requested.
