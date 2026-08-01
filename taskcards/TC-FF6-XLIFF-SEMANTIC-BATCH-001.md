---
artifact_id: TC-FF6-XLIFF-SEMANTIC-BATCH-001
artifact_type: taskcard
path: taskcards/TC-FF6-XLIFF-SEMANTIC-BATCH-001.md
format_id: xliff
product_family: xml-vocabulary
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
  trigger: authority-contract-or-candidate-digest-change
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
goal_id: FF6-PRODUCTION-LIBRARIES-001
parent_task_id: TC-FF6-XLIFF-PROFILE-SURFACE-001
status: READY
lane: B
skill_ids:
  - ingest-spec-sal
  - sal-pipeline-heal
  - compile-format-contract
  - test-driven-development
  - plan-control
release_blockers: []
notes: Semantic-batch pilot; candidate I remains unaccepted until independent proof passes.
---

# TC-FF6-XLIFF-SEMANTIC-BATCH-001: XLIFF Semantic-Batch Pilot and Compiler

**Phase:** CONTRACT
**Status:** READY
**Owner:** deterministic FF6 Lane B scheduler
**Created:** 2026-08-01
**Last updated:** 2026-08-01
**Blocking:** completion of XLF-04 authority-to-obligation compilation
**Blocked by:** none; Event 40 is the prerequisite checkpoint
**Format:** xliff
**Gate:** no product-source or promotion gate

## Objective

Replace one-candidate-per-checkpoint throughput with evidence-bound semantic
batches while preserving an explicit, independently reproducible decision for
every authority occurrence. Use Event-40 candidate
`XLF-CAND-CORE-SCHEMATRON-60B596A00F7FA06A` as the first regression case. No
generated mapping is evidence and no member is accepted merely because it is
grouped with an accepted member.

## Locked baseline

- Event 40; XLIFF ProductContract `DRAFT`, 15 capabilities.
- 31/105 source-bound Core obligations; 74 missing.
- 9/1,130 independently verified candidate dispositions; 1,121 unverified.
- Candidate I is the XLIFF 2.1 target-side isolated start-code report.
- All 31 predecessor rows, nine decisions, and 1,130 candidate identities must
  remain unchanged unless the batch manifest names and proves the change.

## Exact path allowlist and logical leases

Required logical lease: `logical:FF6-XLIFF-CONTRACT`. The product source tree is
forbidden. Initial pilot paths are:

- `tools/spec/xliff_core_candidate_adjudication.py`
- `tools/spec/xliff_core_candidate_binding.py`
- `tools/spec/extract_sal_facts.py`
- `tools/spec/seed_sal_candidates.py`
- `tests/tools/test_xliff_core_candidate_adjudication.py`
- `tests/tools/test_extract_sal_facts_candidate_binding.py`
- `tests/tools/test_extract_sal_facts.py`
- `tests/tools/test_seed_sal_candidates.py`
- `reports/ff6/xliff-core-authority-candidate-census.yaml`
- `reports/ff6/xliff-core-obligation-denominator.yaml`
- `reports/ff6/xliff-core-obligation-inventory.yaml`
- `reports/sal-verification/xliff-core-candidate-adjudications.yaml`
- `reports/sal-verification/xliff.json`
- `shared/format-contracts/research/xliff.yaml`
- `shared/format-contracts/xliff.yaml`
- `shared/sal-facts/xliff.yaml`
- `shared/sal-facts/evidence/xliff.yaml`
- `shared/sal-facts/evidence/xliff-core-candidate-decisions.yaml`
- `shared/sal-fact-id-aliases.json`
- `registry/format-contract-registry.yaml`
- `reports/skills-rff6/skill-transcripts/ingest-spec-sal-xliff-semantic-batch-001.json`
- `reports/skills-rff6/skill-transcripts/sal-pipeline-heal-xliff-semantic-batch-001.json`
- `reports/skills-rff6/skill-transcripts/compile-format-contract-xliff-semantic-batch-001.json`
- `reports/skills-rff6/skill-transcripts/test-driven-development-xliff-semantic-batch-001.json`

Controller/event/taskcard paths are excluded from the product lane and are
written later by the separately leased controller owner. Runtime proof lives
under `.local/run-records/ff6/TC-FF6-XLIFF-SEMANTIC-BATCH-001/` and
`.local/proof/ff6/TC-FF6-XLIFF-SEMANTIC-BATCH-001/`.

## Ordered implementation steps

1. T0-bind the Event-40 head, five XLIFF authority records and artifact bytes,
   contract/census/denominator/adjudication digests, candidate I occurrence and
   content digests, all predecessor semantic digests, tools, tests, and leases.
2. Add the candidate-I RED test. Independently decide whether its exact
   target-side Schematron report reciprocally proves the existing
   `SAL-XLIFF-CORE-INLINE-ISOLATION-001` rule. Test all eight generated mappings
   as unverified proposals and explicitly reject incidental/downstream owners.
3. Compile semantic fingerprints from normalized authority semantics, profile,
   direct owner, invariant, invalidation closure, and rollback boundary. Never
   use text similarity alone.
4. Form only homogeneous equivalence groups. Emit a stable exception queue for
   profile differences, ambiguous owners, conflicting prose/schema rules,
   contextual-only occurrences, and missing reciprocal evidence.
5. Preserve one signed/content-addressed decision per occurrence. An independent
   validator reconstructs each authority-to-obligation mapping without reading
   generated proposals as proof.
6. Run three clean group compilations and require identical group IDs, member
   IDs, exception ordering, and canonical bytes.
7. Inject a failing heterogeneous member. Prove the unaccepted transaction
   changes no predecessor decision, count, candidate identity, contract, or SAL
   fact. Split it into a new stable group rather than partially accepting it.
8. Accept candidate I only if its direct and reciprocal proof closes. Rebuild
   the XLIFF contract and affected projections, keeping XLF-04 incomplete.
9. Produce a digest-bound closure candidate for the controller owner. The lane
   itself does not append an event or edit promotion state.

## Verification tiers

- **T0:** exact checkpoint and authority closure before every write.
- **T1:** RED/GREEN for candidate I and every grouped member, group invariant,
  proposal rejection, exception classification, reciprocal proof.
- **T2:** all affected XLIFF tests, exact SAL verification, denominator/census
  stability, predecessor equality, three-run determinism, strict contract,
  Ruff, Mypy, Pyright, py_compile, independent validator, receipts.
- **T3:** controller owner performs detached replay and native-event validation
  for an accepted closure candidate.
- **T4:** full XLIFF corpus/oracle/fuzz/mutation work is deferred and unclaimed.
- **T5:** not satisfied by this contract task.

## Acceptance criteria

- [ ] Candidate I has one independent explicit decision bound to exact bytes.
- [ ] All eight generated mappings remain proposals until independently proven.
- [ ] Semantic grouping never crosses profile, owner, invariant, or rollback boundary.
- [ ] Three group compilations produce identical canonical bytes and IDs.
- [ ] Exception queue is deterministic and complete for excluded members.
- [ ] Failed member rollback preserves 31 rows, nine decisions, and 1,130 IDs.
- [ ] Accepted members retain per-occurrence decisions and proof edges.
- [ ] All affected tests/static/contract/SAL/receipt checks pass.
- [ ] XLF-04, source implementation, certification, promotion, and gates remain incomplete.

## Failure and next-task rules

- Authority contradiction creates separate named profiles or an explicit
  contradiction record; never choose the convenient oracle.
- Ambiguous/heterogeneous members remain in the exception queue and do not
  block homogeneous groups.
- After three distinct repairs of one root cause, block only that semantic rule
  and schedule the next highest-priority unblocked XLIFF group.
- A passing pilot selects the largest safe equivalence group by severity and
  downstream unlock count, not raw candidate order.

## Evidence required

- RED/GREEN output, authority excerpts identified by digest/location (not copied
  spec prose), per-member decisions, group/exception manifests, predecessor
  equality, three-run digests, strict contract/SAL reports, valid transcripts,
  exact changed paths, detached replay, and controller closure-candidate digest.
