---
artifact_id: FF6-ACTIVE-WORK-CHECKPOINT-001
artifact_type: provider_neutral_work_checkpoint
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
authoritative_state: false
canonical_event: FF6-EVENT-000019
---

# Active Work Checkpoint: XLIFF Stable Profiles and Modules

This is the provider-neutral shift boundary after the NRRD contract
repair. Canonical authority remains the controller, event journal, current-gap
projection, and taskcards; this document explains how to resume them.

## Exact checkpoint

| Field | Value |
|---|---|
| Mission | `FF6-PRODUCTION-LIBRARIES-001` |
| Forge and branch | GitLab `origin/main` only |
| Controller state | `CONTRACT` |
| Controller sequence | `19` |
| Event head | `76b580d72f865428e92bc5b6089a89487356c69163aadf6b615b70c6867221f8` |
| Parent task | `TC-FF6-PROGRAM-CAPABILITIES-001` - `NEEDS_REPAIR` |
| Completed task | `TC-FF6-NRRD-PROFILE-SURFACE-001` - `PASS` |
| Exact next task | `TC-FF6-XLIFF-PROFILE-SURFACE-001` - `READY` |
| Selected finding | `FF6-XLIFF-PROFILE-001` |
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
- Notebook execution remains `EXCLUDED_WITH_AUTHORITY`. Event 18 closed only
  the IPYNB contract/profile defect; it does not certify the existing product.
- Event 19 compiles the exact NRRD0001-NRRD0005 delta: key/value metadata
  begins in 0002, kinds in 0003, space/orientation and multi-file behavior in
  0004, and measurement frame in 0005.
- All 25 NRRD SAL facts pass exact evidence. Eighteen scientific-raster
  domains and 41 policy IDs assign every fact exactly once.
- The governed research source was repaired where one requirement mixed
  NRRD0004 coordinate transforms with NRRD0005 measurement-frame semantics.
- NRRD now has 21 capabilities and 65 obligations with exact non-empty
  profile subsets. All five profiles are claimed and the live profile gap is
  resolved.
- Teem's permissive acceptance of later fields under earlier magic remains an
  explicit interoperability peculiarity, not a weakened strict contract.
- Event 19 proves only the NRRD normative denominator and deterministic
  projection. It does not certify the existing product.

## Current compiled planning state

| Measure | Value |
|---|---:|
| Capabilities | 110 |
| IPYNB obligations | 68 |
| OpenRaster obligations | 134 |
| NRRD obligations | 65 |
| XLIFF obligations | 125 |
| SafeTensors obligations | 86 |
| UBL obligations | 194 |
| Total obligations | 672 |
| Aggregate SHA-256 | `4d17d8c8c0ef3de74d59e1d5b16884c0210fd0836e0593591871f10d0af2efd2` |
| Three-run digest | `389be84634941d3f244387bbc488c2303dcdb3add74b7d1edfb5def85710d3fc` |
| Authority matches | 15/15 |
| Product certifications | 0 |

The portfolio remains `NEEDS_PROFILE_OR_SURFACE_REPAIR` because exact XLIFF
2.0/2.1 module applicability and UBL all-root typing remain.

## Verification boundary

- NRRD format-contract tests: 92 passed; one baseline-known stateful CSV
  idempotency test was deselected.
- Affected verifier/compiler/controller tests: 96 passed.
- Authority dependency-closure tests: 119 passed.
- Ruff: pass.
- Strict Mypy for the touched family-pack validator: pass after adding
  `types-PyYAML 6.0.12.20260724` to the ignored environment. No
  repository-wide Mypy result is claimed.
- Pyright 1.1.411: zero diagnostics.
- NRRD family-pack validation: 18 domains, 41 policy IDs,
  explicit-complete fact ownership, valid, idempotent.
- NRRD SAL exact verification: 25/25 pass.
- Three strict six-format compilations: byte-identical.
- Authority audit: 15/15 match.
- Global SAL merge remains non-promoting because of pre-existing ODS/ODT alias
  contradictions. The NRRD cache content was verified and all attempted alias
  side effects were removed.

## Exact resume procedure

1. Read `START-HERE.md`, `CURRENT-MACHINE-STATE.yaml`, `AGENTS.md`, and the
   provider adapter in their declared order.
2. Fetch GitLab `origin/main`; do not use GitHub or create a branch.
3. Require `865558bb88243acda08c2a8d58a0d5ec887dedeb` to be an ancestor of
   fetched `origin/main`.
4. Require a clean or fully classified shared worktree.
5. Register a fresh coordination identity and inspect live leases/conflicts.
6. Validate event 19 natively using `previous_event_hash` and canonical JSON
   with `event_hash` removed.
7. Verify the controller names
   `TC-FF6-XLIFF-PROFILE-SURFACE-001` as `READY`.
8. Read that taskcard, the product goal, current gaps, capability policy,
   XLIFF contract/SAL/evidence/enrichment, the pinned 2.1 package, and the
   authority lock showing that a separate 2.0 package is absent.
9. Claim exact paths, resolve registered skills, and run the mutation guard
   before every write.
10. Execute the atomic steps XLF-01 through XLF-08 in
    `STATE-MACHINE-AND-TASKCARD-PROTOCOL.md`.
11. Acquire, independently digest-check, legally classify, lock, and prove
    offline reconstruction of the official XLIFF 2.0 OASIS Standard package.
12. Produce source-located 2.0/2.1 Core and module delta matrices.
13. Split all eight official 2.1 modules—Translation Candidates/Matches,
    Glossary, Format Style, Metadata, Resource Data, Size and Length
    Restriction, Validation, and ITS—into separately owned capability
    families. Account for all nine module schema vocabularies; `its` and
    `itsm` belong to the single ITS module.
14. Inventory Change Tracking as an informative extension and prohibit it
    from satisfying or inflating normative module coverage.
15. Preserve semantic inline pairing/order, segmentation, state, original
    data, skeleton, extension, ITS, agent-processing, canonical XML, security,
    and downgrade-loss obligations.
16. Recompile all six projections and require three identical runs plus a
    complete authority match after adding the 2.0 record.
17. Reconcile gaps/task/controller/event/handover, commit explicit owned paths,
    and push only GitLab `origin/main`.

If the provider shift ends before XLF-08, only stop after the current atomic
step is integration-safe. Journal the completed steps and first unmet step as
`WORK_IN_PROGRESS`, refresh this packet, commit, push, and verify the remote.
Never leave a required result only in conversation or an uncommitted tree.

## Do not infer

This checkpoint does not mean:

- any of the 672 obligations is implemented merely by this contract work;
- any current source package is production-ready;
- any format has independent interoperability certification;
- the broad cross-platform installed-wheel matrix is current;
- architecture work is unlocked;
- publication is authorized.

Only digest-bound executed behavior can move those states.

## Outgoing self-challenge

The event-19 executor recorded the required governance challenge at the shift
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
