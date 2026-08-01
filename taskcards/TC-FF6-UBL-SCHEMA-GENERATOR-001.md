---
artifact_id: TC-FF6-UBL-SCHEMA-GENERATOR-001
artifact_type: taskcard
path: taskcards/TC-FF6-UBL-SCHEMA-GENERATOR-001.md
format_id: ubl
product_family: large-schema-generated
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
  trigger: ubl-authority-schema-generator-or-config-change
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
goal_id: FF6-PRODUCTION-LIBRARIES-001
parent_task_id: TC-FF6-UBL-TYPING-001
status: READY
lane: C
skill_ids:
  - spec-parity-source-regeneration-and-migration
  - test-driven-development
  - compile-format-contract
  - plan-control
release_blockers: []
notes: UBL-03 schema-graph closure; no claim of generated product types yet.
---

# TC-FF6-UBL-SCHEMA-GENERATOR-001: Complete the UBL 2.3 Schema Graph and Generator Contract

**Phase:** CONTRACT / generator foundation
**Status:** READY
**Owner:** deterministic FF6 Lane C scheduler
**Created:** 2026-08-01
**Last updated:** 2026-08-01
**Blocking:** UBL-03 and all 91-root typed-source generation
**Blocked by:** none for attributes and attribute groups
**Format:** ubl
**Gate:** no product certification or promotion

## Objective

Complete the authority-derived UBL 2.3 schema graph required to generate
professional, reproducible Python types for all 91 document roots. Continue the
verified partial UBL-03 graph with attributes and attribute groups, then complete
group references, wildcards, substitutions, facets, namespace/form rules, and
documentation. Generated product source begins only after the complete graph and
generator contract pass; no checked-in type surface is inferred from partial data.

## Locked baseline

- 106 XSD documents, 91 document roots, 297 schema dependencies.
- 3,788 global components, 8,926 global reference uses.
- 6,001 local particle nodes across 468 named owners.
- 1,178 derivation edges.
- UBL-01 and UBL-02 are complete; UBL-03 is incomplete.
- Next microstep is attributes and attribute groups. Prior component, reference,
  particle, anonymous-type, and derivation identities are immutable inputs.

## Exact path allowlist and logical leases

Required logical lease: `logical:FF6-UBL-GENERATOR`. Product output files are
not allowed until a later generated-output manifest taskcard exists.

- `tools/spec/compile_ubl_schema_graph.py`
- `tools/spec/ubl_schema_graph.py`
- `tools/spec/ubl_schema_common.py`
- `tools/spec/ubl_schema_dependencies.py`
- `tools/spec/ubl_schema_references.py`
- `tools/spec/ubl_schema_particles.py`
- `tools/spec/ubl_schema_anonymous_types.py`
- `tools/spec/ubl_schema_derivations.py`
- `tools/spec/ubl_schema_attributes.py`
- `tools/spec/ubl_schema_groups.py`
- `tools/spec/ubl_schema_wildcards.py`
- `tools/spec/ubl_schema_substitutions.py`
- `tools/spec/ubl_schema_facets.py`
- `tests/tools/test_compile_ubl_schema_graph.py`
- `tests/tools/test_ubl_schema_graph.py`
- `reports/ff6/ubl-schema-graph.yaml`
- `reports/skills-rff6/skill-transcripts/spec-parity-source-regeneration-ubl-schema-generator-001.json`
- `reports/skills-rff6/skill-transcripts/test-driven-development-ubl-schema-generator-001.json`

Any actual path name differing from a not-yet-existing module above must be
resolved by amending this taskcard through `create-taskcard`/`plan-control`
before mutation; nearby conventions are not authority. Runtime records live
under `.local/run-records/ff6/TC-FF6-UBL-SCHEMA-GENERATOR-001/` and
`.local/proof/ff6/TC-FF6-UBL-SCHEMA-GENERATOR-001/`.

## Ordered implementation steps

1. T0-bind the UBL 2.3 authority package/member digests, all 106 schema bytes,
   existing graph/tool/test digests, Event-40 UBL counts, leases, and expected
   descendants. Revalidate all baseline identities before mutation.
2. RED attributes: cover global/local attributes, `ref`, `type`, inline simple
   types, `use`, `default`, `fixed`, `form`, qualification, and namespace.
3. RED attribute groups: definition, nested references, deterministic expansion,
   cycle detection, duplicate/conflicting declarations, and inherited use.
4. GREEN one schema layer at a time. Preserve raw declaration identity and a
   normalized resolved view; never erase schema location or ownership.
5. Complete model/attribute groups and element groups, `any`/`anyAttribute`
   namespace and processContents semantics, substitution heads/members, simple
   and complex-content derivation composition, and all XSD facets used by UBL.
6. Add stable naming/collision rules for QName, document root, common component,
   anonymous type, attribute, group, and Python reserved-word collisions.
7. Bind documentation/appinfo text as provenance metadata without using it to
   override normative XSD structure.
8. Validate order/cardinality, namespace/form, reference resolution, derivation,
   substitutions, wildcards, facets, and all 91 roots with a second schema engine.
9. Run three clean graph generations and require byte-identical output and
   identical IDs/counts. Seed input/tool/config mutations and verify invalidation.
10. Emit the complete graph manifest and a follow-on type-generation taskcard.
    Do not generate or edit `src/python/ubl/` under this card.

## Verification tiers

- **T0:** authority closure, graph baseline, lease/manifest, invalidation set.
- **T1:** RED/GREEN per schema construct plus adversarial synthetic XSDs for
  cycles, ambiguity, namespace, cardinality, and collisions.
- **T2:** full UBL graph tests, all 106 schemas/91 roots, predecessor equality,
  three-run determinism, independent schema-engine comparison, Ruff, strict
  Mypy, Pyright, py_compile, receipt validation.
- **T3:** detached generation replay after generator/config/output changes.
- **T4:** generated-source mutation/performance/platform matrix is deferred.
- **T5:** not satisfied by schema-graph closure.

## Acceptance criteria

- [ ] Every attribute and attribute group has stable identity and resolved semantics.
- [ ] Groups, wildcards, substitutions, facets, derivations, namespace/form, and documentation are complete for all 106 schemas.
- [ ] All 91 roots are reachable with correct ordered/cardinality-aware graphs.
- [ ] No unresolved QName, group, type, attribute, substitution, or namespace edge remains.
- [ ] Existing identities and verified counts remain unchanged unless exact authority proves a correction.
- [ ] Three clean graph generations are byte-identical.
- [ ] Independent schema engine agrees on official and generated minimal instances.
- [ ] Generated-output manifest and naming/collision contract are complete.
- [ ] No product source, certification, promotion, release, or gate state changes.

## Failure and next-task rules

- A schema contradiction is recorded with exact members and profiles; do not
  silently choose one resolution.
- Nondeterminism blocks graph acceptance and type generation.
- After three distinct repairs of one construct root cause, block that construct
  and continue independent graph work only if no dependent output is accepted.
- Passing graph closure creates the bounded all-roots type-generation card;
  it does not itself make UBL-03 or the product production-ready.

## Evidence required

- Per-construct RED/GREEN outputs, complete graph manifest and counts, identity
  preservation report, three-run digests, second-engine results, mutation
  invalidation report, static checks, valid transcripts, exact changed paths,
  detached replay, and follow-on generated-output taskcard.
