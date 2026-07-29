---
artifact_id: FF6-ACTIVE-WORK-CHECKPOINT-001
artifact_type: provider_neutral_work_checkpoint
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
authoritative_state: false
canonical_event: FF6-EVENT-000017
---

# Active Work Checkpoint: IPYNB Profile Applicability

This is the provider-neutral shift boundary after the OpenRaster contract
repair. Canonical authority remains the controller, event journal, current-gap
projection, and taskcards; this document explains how to resume them.

## Exact checkpoint

| Field | Value |
|---|---|
| Mission | `FF6-PRODUCTION-LIBRARIES-001` |
| Forge and branch | GitLab `origin/main` only |
| Controller state | `CONTRACT` |
| Controller sequence | `17` |
| Event head | `44cb90a67aec8fff244de05d84c047f1d31077d694eda1ff1e27ee0aaa0f3015` |
| Parent task | `TC-FF6-PROGRAM-CAPABILITIES-001` - `NEEDS_REPAIR` |
| Completed task | `TC-FF6-ORA-PROFILE-SURFACE-001` - `PASS` |
| Exact next task | `TC-FF6-IPYNB-PROFILE-SURFACE-001` - `READY` |
| Selected finding | `FF6-IPYNB-PROFILE-001` |
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

## Current compiled planning state

| Measure | Value |
|---|---:|
| Capabilities | 99 |
| IPYNB obligations | 105 |
| OpenRaster obligations | 134 |
| NRRD obligations | 94 |
| XLIFF obligations | 125 |
| SafeTensors obligations | 86 |
| UBL obligations | 194 |
| Total obligations | 738 |
| Aggregate SHA-256 | `de6a38a86aa7a82cc50dc7dc6ebfa0066c811d8de782a37684fd26d20a89272a` |
| Three-run digest | `2c998635a64f36c2b93c397ab0a5c834379ad5d74fd0544c6017a65337d907fc` |
| Authority matches | 15/15 |
| Product certifications | 0 |

The portfolio remains `NEEDS_PROFILE_OR_SURFACE_REPAIR` because IPYNB 4.0-4.4,
NRRD0001-0004, XLIFF 2.0, and UBL full-typing gaps remain.

## Verification boundary

- `tests/format_contract`, `tests/production_program`, and the SAL verifier:
  166 passed; the baseline-known CSV idempotency test was deselected because it
  mutates three unrelated tracked reports before exposing its pre-existing
  gap-ledger mismatch.
- Ruff: pass.
- Mypy for the three affected compiler modules: pass.
- Pyright was unavailable in the current shell; do not convert that absence
  into a pass.
- Family-pack validation: 17 domains, valid, idempotent.
- ORA SAL exact verification: 20/20 pass.
- Three strict six-format compilations: byte-identical.
- Authority audit: 15/15 match.

## Exact resume procedure

1. Read `START-HERE.md`, `CURRENT-MACHINE-STATE.yaml`, `AGENTS.md`, and the
   provider adapter in their declared order.
2. Fetch GitLab `origin/main`; do not use GitHub or create a branch.
3. Require `17aece4e5301af958b21e4ffc9db878494f3b89c` to be an ancestor of
   fetched `origin/main`.
4. Require a clean or fully classified shared worktree.
5. Register a fresh coordination identity and inspect live leases/conflicts.
6. Validate event 17 natively using `previous_event_hash` and canonical JSON
   with `event_hash` removed.
7. Verify the controller names
   `TC-FF6-IPYNB-PROFILE-SURFACE-001` as `READY`.
8. Read that taskcard, the product goal, current gaps, capability policy, IPYNB
   contract/SAL/evidence/enrichment, and pinned authorities.
9. Claim exact paths, resolve registered skills, and run the mutation guard
   before every write.
10. Execute the atomic steps IPY-01 through IPY-08 in
    `STATE-MACHINE-AND-TASKCARD-PROTOCOL.md`.
11. Produce a source-located nbformat 4.0-4.5 delta matrix.
12. Split capabilities where rules have different minor-version
    applicability; never assign all rules to 4.5 merely because the newest
    schema contains them.
13. Preserve typed notebook/cell/output/attachment/MIME/metadata behavior,
    schema validation/conversion, deterministic serialization, unknown
    metadata preservation, safe clearing/filtering/ID handling, and the
    absolute no-execution boundary.
14. Recompile all six projections and require three identical runs plus 15/15
    authority matches.
15. Reconcile gaps/task/controller/event/handover, commit explicit owned paths,
    and push only GitLab `origin/main`.

If the provider shift ends before IPY-08, only stop after the current atomic
step is integration-safe. Journal the completed steps and first unmet step as
`WORK_IN_PROGRESS`, refresh this packet, commit, push, and verify the remote.
Never leave a required result only in conversation or an uncommitted tree.

## Do not infer

This checkpoint does not mean:

- any of the 738 obligations is implemented;
- any current source package is production-ready;
- any format has independent interoperability certification;
- the broad cross-platform installed-wheel matrix is current;
- architecture work is unlocked;
- publication is authorized.

Only digest-bound executed behavior can move those states.
