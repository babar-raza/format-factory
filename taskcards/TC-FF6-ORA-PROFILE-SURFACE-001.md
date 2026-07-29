---
artifact_id: TC-FF6-ORA-PROFILE-SURFACE-001
artifact_type: taskcard
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
goal_id: FF6-PRODUCTION-LIBRARIES-001
parent_task_id: TC-FF6-PROGRAM-CAPABILITIES-001
status: READY
format_id: ora
skill_ids:
  - ingest-spec-sal
  - sal-pipeline-heal
  - build-obligation-register
  - compile-format-contract
  - compile-production-capability-universe
  - plan-control
---

# Repair the OpenRaster Profile and Format-Specific Capability Surface

## State and boundary

- Status: `READY`
- Parent: `TC-FF6-PROGRAM-CAPABILITIES-001` (`NEEDS_REPAIR`)
- Source gap: `FF6-GAP-013`
- Controller predecessor: `FF6-EVENT-000016`
- Product source, product tests, package metadata, certification, promotion,
  and gate mutation: prohibited
- Promotion effect: none

Authority availability is no longer the defect: `SRC-ORA-001`,
`SRC-ORA-002`, and `SRC-ORA-003` are locked and live `MATCH` results. The
remaining defect is semantic depth. The current archive-family contract
describes only ten generic capabilities, claims only the 0.0.3 profile, and
does not express the format-specific editable image/layer/compositing surface
required by the mission.

## Objective

Produce an authority-backed, version-applicable OpenRaster contract and
capability universe for named interoperability profiles 0.0.3, 0.0.4, and
0.0.5. Account explicitly for the complete editable and viewing baselines
without pretending that the early drafts provide a universal conformance
standard.

This task defines what the future library must implement and prove. It does
not create OpenRaster product source.

## Required execution

1. Revalidate controller event 16, the three locked OpenRaster sources, their
   legal dispositions, and exact bytes. Use only the canonical authority
   materializer; do not introduce another download/cache path.
2. Extract a source-located profile delta matrix for 0.0.3, 0.0.4, and 0.0.5.
   Every row must name:
   - concept or rule;
   - first applicable version;
   - later-version change or removal;
   - normative/interop strength;
   - source ID and exact section/fragment;
   - required positive, rejection, preservation, or interoperability proof.
3. Audit the current 20 OpenRaster SAL facts and evidence targets against that
   matrix. Ingest missing specification facts through `ingest-spec-sal`;
   never write SAL facts ad hoc or infer rules solely from existing code.
4. Replace generic archive-only modeling with explicit contract capabilities
   for at least:
   - image/document identity and canvas geometry;
   - ZIP/mimetype/container validation and deterministic archive writing;
   - `stack.xml` parsing, serialization, ordering, and namespace handling;
   - stack, nested group, layer, and mask models;
   - layer name, source, offsets, opacity, visibility, isolation, and
     compositing operation;
   - editable baseline assets and viewing baseline `mergedimage.png`;
   - thumbnail behavior;
   - PNG media validation and dimension consistency;
   - extension/unknown-data preservation;
   - rendering/compositing adapter boundary and pinned operation semantics;
   - path traversal, duplicate entry, decompression, size, count, recursion,
     malformed XML, and external-entity defenses;
   - semantic roundtrip, deterministic output, and application
     interoperability expectations.
5. Express applicability for each capability and obligation across all three
   named profiles. A common rule may reference multiple profiles; a version
   delta must remain separately testable.
6. Reconcile the explicit capabilities with policy and enrichment records.
   Preserve existing correct stable IDs when their semantics are unchanged;
   introduce stable new IDs for genuinely distinct developer capabilities.
   Never overload one ID with a materially different meaning.
7. Recompile the OpenRaster contract through `/compile-format-contract`, then
   recompile all six capability/obligation projections through
   `/compile-production-capability-universe`.
8. Require no missing OpenRaster target profile and no
   `FF6-ORA-SURFACE-001` or `FF6-ORA-PROFILE-001` compiler finding. Do not
   suppress the findings in policy; remove them only when compiled evidence
   proves the surface.
9. Reconcile parent gaps and register the next highest-severity repair. Do not
   unlock architecture while any mandatory capability/profile obligation is
   incomplete.

## Required tracked outputs

- evidence-backed OpenRaster SAL facts and evidence updates;
- `shared/format-contracts/ora.yaml` via the registered compiler;
- OpenRaster policy/family/enrichment inputs required by that compiler;
- regenerated six-format capability, obligation, coverage, and manifest
  projections;
- this taskcard, parent taskcard, current gaps, controller state, event
  journal, task index, handover, transcripts, and evidence.

No external specification bytes may be added to Git unless redistribution is
affirmatively allowed by the lock’s legal evidence.

## Acceptance criteria

- [ ] The 0.0.3/0.0.4/0.0.5 profile delta matrix has source-located evidence
      and explicit uncertainty for every weak or contradictory draft rule.
- [ ] All current and newly required OpenRaster SAL facts resolve with no
      foreign, dangling, duplicate, or unsupported authority edge.
- [ ] Image, stack, group, layer, mask, merged image, thumbnail, PNG,
      compositing/rendering, extension preservation, container security,
      lifecycle, validation, and deterministic writing are represented by
      explicit developer capabilities.
- [ ] Every mandatory rule compiles to a canonical
      `SAL-ORA-OBL-*` obligation owned by exactly one capability.
- [ ] Every capability and obligation declares exact profile applicability.
- [ ] Capability coverage reports all three target profiles claimed and no
      OpenRaster known surface/profile gap.
- [ ] Three clean strict compilations are byte-identical and all 15 authority
      artifacts remain `MATCH`.
- [ ] Contract, SAL, production-program, event-chain, static, and affected
      regressions pass.
- [ ] No product source, certification, promotion, or gate state changes.

## Failure and honesty policy

- The OpenRaster drafts are weak authority. Preserve uncertainty and certify
  this future library on named interoperability profiles, not exaggerated
  universal conformance.
- If versions contradict, define separate profile behavior; never select the
  version that makes an existing implementation pass.
- If a feature is common application practice but absent from the draft,
  classify it as interoperability evidence or product requirement, not a
  normative specification fact.
- A capability description, file, symbol, or synthetic fixture is not
  implementation or interoperability proof.
- Other formats continue independently; this task blocks only the parent
  capability/architecture transition.

## Exit

- `PASS`: OpenRaster profile and surface coverage compile completely; select
  the next current mandatory gap.
- `NEEDS_REPAIR`: a named authority, fact, profile, or surface obligation
  remains incomplete.
- `TECHNICALLY_BLOCKED`: only after three materially different failed repairs
  to the same external contradiction, with evidence and no suppression.
