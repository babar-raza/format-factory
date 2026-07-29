---
artifact_id: FF6-ACTIVE-WORK-CHECKPOINT-001
artifact_type: provider_neutral_work_checkpoint
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
authoritative_state: false
canonical_event: FF6-EVENT-000016
---

# Active Work Checkpoint: OpenRaster Contract Repair

This is the provider-neutral shift boundary after authority closure and before
OpenRaster profile/surface repair. It explains the canonical controller,
journal, taskcard, and proof state; it does not replace them.

## Exact checkpoint

| Field | Value |
|---|---|
| Mission | `FF6-PRODUCTION-LIBRARIES-001` |
| Forge and branch | GitLab `origin/main` only |
| Controller state | `CONTRACT` |
| Controller sequence | `16` |
| Event head | `2ea206536ff0ccecaa0a4e93df32ada3e7575018f4cdcafb7525c59d51dd50ba` |
| Parent task | `TC-FF6-PROGRAM-CAPABILITIES-001` - `NEEDS_REPAIR` |
| Completed task | `TC-FF6-AUTHORITY-CLOSURE-001` - `PASS` |
| Exact next task | `TC-FF6-ORA-PROFILE-SURFACE-001` - `READY` |
| Selected gap | `FF6-GAP-013` |
| Product source mutation | Prohibited in the next task |
| Promotion effect | None |
| Certified libraries | 0 of 6 |

Resume from the fetched `origin/main` descendant that contains this packet and
event 16. The packet cannot embed the hash of its own containing commit; use
the ancestry rule in `checkpoint.yaml`.

## What the completed authority task proved

The authority dependency plane is now replayable rather than status-shaped:

- `shared/format-contracts/authority-lock.yaml` contains 15 pinned sources.
- Its LF-normalized SHA-256 is
  `8eefb28e3ef24b5b533496b54860daee981853d9c872fddc1ba5de4ff150f249`.
- All 15 sources produce live `MATCH`; none are missing, mismatched,
  undeclared, or legally blocked.
- Four internal product-requirement sources are tracked canonical documents.
- External specification bytes remain content-addressed local inputs and were
  not added to Git without redistribution permission.
- ProductContract compilation is strict and consumes the same live authority
  audit as capability compilation.
- The capability manifest binds the authority lock, schemas, runtime,
  materializer, compilers, stores, research inputs, product requirements, and
  materialized authority bytes.
- A clean offline root rebuilt 15 of 15 sources from CAS.
- A clean online root rebuilt 15 of 15 sources from official endpoints with
  an initially empty CAS; the resulting CAS contained 73,206,772 bytes.
- Three equivalent strict compilations were byte-identical.
- A diagnostic authority override is explicitly non-promoting.

This proves authority closure only. It does not prove any format implementation
or interoperability behavior.

## Current compiled planning state

| Measure | Current value |
|---|---:|
| Capabilities | 89 |
| IPYNB obligations | 105 |
| OpenRaster obligations | 32 |
| NRRD obligations | 94 |
| XLIFF obligations | 125 |
| SafeTensors obligations | 86 |
| UBL obligations | 194 |
| Total obligations | 636 |
| Manifest aggregate SHA-256 | `667cd4cb69773e6746ad46173b53de39c18ef44d39ef7db91c6337d8a3761a73` |
| Manifest LF SHA-256 | `ef9f7e685f1012b32cfa73238ebe0b035dda660c33fc4316ee09b42fd82ee773` |
| Three-run digest | `04114c84221edcdb00dae1097d75e55a7c1a6be75a074c9c0b8b07f0de5533a8` |

Assessment is `NEEDS_PROFILE_OR_SURFACE_REPAIR`. All obligations remain
unverified as product behavior, and every product promotion remains
`UNASSESSED`.

## Verification at this boundary

- Affected pytest: `250 passed, 1 deselected`.
- The deselected test is
  `tests/format_contract/test_consumption_chain.py::test_full_slice_second_run_is_idempotent`.
- That CSV test is a pre-existing unrelated defect and mutates three tracked
  reports before failing. Its side effects were restored to exact HEAD bytes
  through the governed rollback skill.
- Ruff passed.
- Mypy passed for the affected modules.
- Pyright 1.1.411 passed with zero errors and warnings.
- Plan-control tests passed: 40.
- Native FF6 chain validation passed through event 16.
- Skill/capability sync passed: 198 active capabilities, all full parity, no
  drift.

Do not convert the deselected CSV failure into FF6 evidence or silently repair
it inside the OpenRaster task.

## Why the next task is OpenRaster

Authority is no longer the limiting defect. The OpenRaster contract still:

- models mostly generic archive behavior rather than editable layered images;
- claims only profile 0.0.3, while the mission names 0.0.3, 0.0.4, and 0.0.5;
- lacks explicit, separately testable stack, group, layer, mask, asset,
  compositing, rendering, preservation, and application-interoperability
  capabilities;
- cannot distinguish draft-normative rules from application practice;
- has no product package, tests, corpus, oracle, or installed-wheel proof.

The compiler reports `FF6-ORA-SURFACE-001` and `FF6-ORA-PROFILE-001`. The next
task must remove those findings by evidence-backed contract depth, never by
policy suppression.

## Symptoms, root causes, and structural weaknesses

### Symptoms

1. Archive-generic capabilities make the contract appear mechanically complete
   while developer-visible image behavior is absent.
2. Profile applicability omits 0.0.4 and 0.0.5.
3. A small obligation count can conceal whole missing model and codec surfaces.
4. OpenRaster has no implementation foothold while the other five formats do.
5. Generic Plan Control rejects the FF6 journal even though its native chain
   validates.

### Root causes

1. The earlier compiler could only validate what hand-maintained contracts
   named; it could not discover omitted format concepts.
2. Format-family templates overgeneralized ZIP/container behavior.
3. The early OpenRaster drafts do not provide one mature universal
   conformance standard, so version and interoperability evidence must be
   modeled explicitly.
4. Capability breadth was not compiled from a source-located profile delta
   matrix before product planning.
5. FF6 and generic Plan Control use different journal schemas:
   `previous_event_hash` versus `previous_hash`.

### Structural weaknesses to redesign

- Replace archive-generic coverage with format-specific capabilities.
- Bind every capability and obligation to exact profile applicability.
- Separate normative draft facts, interoperability facts, and product
  requirements.
- Preserve uncertainty and contradictions as named profile differences.
- Keep the FF6 native controller authoritative until `FF6-GAP-011` repairs
  generic Plan Control integration.

## Preserve versus redesign

Preserve:

- the 15-source authority lock and one materialization path;
- current correct SAL facts and stable IDs whose semantics do not change;
- strict fail-closed compilation and non-promoting diagnostic mode;
- the append-only event and gap history;
- all existing product source and tests;
- GitLab-main-only integration and coordination rules.

Redesign:

- the OpenRaster contract's generic capability surface;
- profile applicability and source-location evidence;
- the format-specific obligation ownership graph;
- future architecture and implementation only after the contract task passes.

Do not preserve old readiness labels, counts, or generic capability IDs when
their meaning is materially inadequate.

## Exact next execution

Execute `taskcards/TC-FF6-ORA-PROFILE-SURFACE-001.md` without expanding into
product source.

1. Fetch and verify the event-16 checkpoint.
2. Register a new coordination identity and claim the task plus exact paths.
3. Revalidate event 16 and `SRC-ORA-001`, `SRC-ORA-002`, and `SRC-ORA-003`
   through the canonical materializer.
4. Build a source-located delta matrix for 0.0.3, 0.0.4, and 0.0.5.
5. For every delta, record concept, first version, change/removal, strength,
   source fragment, uncertainty, and required proof kind.
6. Audit all existing OpenRaster SAL facts against the matrix.
7. Ingest missing facts only through registered SAL skills.
8. Expand explicit developer capabilities for document/canvas, ZIP and
   mimetype rules, stack XML, stack/group/layer/mask models, asset handling,
   opacity/visibility/offset/isolation/compositing, merged image, thumbnail,
   PNG validation, extension preservation, deterministic output, rendering
   adapter, security limits, semantic roundtrip, and application
   interoperability.
9. Assign every capability and obligation to exact profile applicability.
10. Reconcile policy, family, and enrichment inputs without weakening gates.
11. Compile the OpenRaster contract, then regenerate all six projections.
12. Require no missing OpenRaster target profile and neither OpenRaster
    compiler finding.
13. Run three clean strict compilations, authority audit, SAL/contract/program
    tests, native event-chain validation, and static checks.
14. Reconcile the parent task and gaps, journal the result, and select the next
    highest-severity mandatory repair.

## OpenRaster task acceptance

The task passes only when:

- the three-profile delta matrix is source-located and uncertainty-aware;
- all OpenRaster facts have valid authority edges;
- explicit developer capabilities cover the complete editable and viewing
  baselines plus security and deterministic behavior;
- every mandatory rule maps to exactly one canonical obligation owner;
- all applicability is explicit;
- the compiler reports no OpenRaster profile or surface finding;
- three strict reruns are identical and authority remains 15 of 15 `MATCH`;
- no product source, certification, promotion, or gate state changes.

## Provider shift safety

The next executor must not trust this prose alone. It must verify:

1. `origin/main` contains event 16.
2. Controller head and journal hash agree.
3. The completed authority task is `PASS`.
4. The successor task is `READY`.
5. The working tree is clean before mutation.
6. No live coordination owner holds the target paths.

The incoming provider registers its own identity. It never reuses this
executor's token, releases another agent's lease, or deletes unexplained state.

## Known limits and preserved local evidence

Two ignored replay roots were retained because recursive cleanup was blocked
by the execution safety policy:

- `.local/tmp/ff6-authority-offline-replay`
- `.local/tmp/ff6-authority-online-rebuild`

They are not canonical inputs and are not present in Git status. Their
existence must not replace a clean replay. Preserve them unless an exact,
governed cleanup task authorizes removal.

## Forbidden claims

Do not claim:

- any library is production-ready or certified;
- 636 obligations are implemented;
- OpenRaster universally conforms to every producer;
- a capability description is executable behavior;
- diagnostic compilation is promotion evidence;
- generic Plan Control failure proves FF6 chain corruption;
- the mission is complete.
