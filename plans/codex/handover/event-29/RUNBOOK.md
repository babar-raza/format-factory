---
artifact_id: FF6-HANDOVER-EVENT-29-RUNBOOK
artifact_type: execution_runbook
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-30
---

# Event 29 exact resume runbook

## A. Reconstruct the checkpoint

Run from the repository root:

```powershell
git fetch origin main --prune
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor 315efa5f5f4420202b5254c86ccd8863a91c385f origin/main
git merge-base --is-ancestor c1f4be66b97acb9a23faa02764e3d41ec1e4a3b0 origin/main
.venv\Scripts\python.exe plans\codex\handover\validate_handover.py --self-test
python -m tools.supervisor.coordination --json status
```

Read the complete journal and controller. If Event 30 or later exists, validate
the newer chain and follow its projection. Do not run stale task selection.

## B. Establish a new provider session

Register a new Claude/Codex identity; never reuse the outgoing identity,
token, leases, execution manifest, or mutation authorizations. Query skill and
capability routing. Claim the logical XLIFF Batch 005 scope and every exact
path that will be written. Create a fresh execution manifest. Run the
pre-mutation guard, preflight before each write, and record every write.

The committed checkpoint is clean. There is no local recovery dependency and
no uncommitted XLIFF implementation to adopt.

## C. Revalidate XLIFF Event 29

```powershell
.venv\Scripts\python.exe -m pytest -q tests\tools\test_extract_sal_facts.py tests\tools\test_extract_sal_facts_candidate_binding.py
.venv\Scripts\python.exe -m pytest -q tests\format_contract --deselect tests/format_contract/test_consumption_chain.py::test_full_slice_second_run_is_idempotent
.venv\Scripts\python.exe -m pytest -q tests\production_program
.venv\Scripts\python.exe -m ruff check tools\spec\extract_sal_facts.py tools\spec\xliff_core_candidate_binding.py tests\tools\test_extract_sal_facts.py tests\tools\test_extract_sal_facts_candidate_binding.py
.venv\Scripts\python.exe -m mypy --strict tools\spec\extract_sal_facts.py tools\spec\xliff_core_candidate_binding.py
npx --yes pyright@1.1.411 tools\spec\extract_sal_facts.py tools\spec\xliff_core_candidate_binding.py tests\tools\test_extract_sal_facts.py tests\tools\test_extract_sal_facts_candidate_binding.py
.venv\Scripts\python.exe -m py_compile tools\spec\extract_sal_facts.py tools\spec\xliff_core_candidate_binding.py tests\tools\test_extract_sal_facts.py tests\tools\test_extract_sal_facts_candidate_binding.py
```

Run all four artifact check modes exposed by
`tools/spec/extract_sal_facts.py --help`. Generate the census three times in
isolated temporary destinations from the pinned authority packages and compare
LF-canonical bytes. Audit all five XLIFF authority records and validate the
three Batch 005 transcripts.

Expected immutable facts:

- census SHA-256:
  `24c1902b6387cc9fa3402f78392ba91c6e6656407719ec11cfaab1c4f3d22b9e`;
- 1,130 candidates, all authority replay-bound;
- 1,130 unverified dispositions and zero verified dispositions;
- 105 expected IDs, 60 with no candidate mapping;
- 25 source-bound obligation rows and 80 missing rows;
- XLF-04 and Batch 005 incomplete.

Any mismatch is invalidation evidence, not permission to update expected
values.

## D. Execute the next XLIFF increment

Use registered `test-driven-development`, `ingest-spec-sal`, and
`sal-pipeline-heal` skills.

1. Select a deterministic, bounded candidate batch using stable candidate IDs.
2. Independently read the exact pinned authority occurrences. The mapping
   generator and current disposition must not serve as the oracle.
3. Add a failing test or validation case that distinguishes the independently
   justified disposition.
4. Repair the mapping rule or emit a source-bound obligation with stable
   `SAL-XLIFF-*` ownership.
5. If authority exposes a missing normative behavior, expand the denominator
   rather than forcing it into an unrelated ID.
6. For the 60 expected IDs without candidates, locate authority support,
   classify them as explicit production policy, or prove a denominator defect.
7. Preserve the existing 25 obligation IDs and provenance.
8. Recompute counts and keep all completeness flags false until the entire
   denominator and candidate set are independently verified.

Do not “verify” all 1,130 rows by mechanically copying generated labels into
SAL. Verification requires an independent authority reading and discriminating
evidence.

## E. Disjoint UBL fallback

If the exact XLIFF write scope is live-owned, claim only the UBL graph paths
and continue from `f98d220a` with one RED-GREEN cycle for:

- offline import/include closure;
- missing or remote `schemaLocation` policy;
- path escape;
- namespace/import mismatch;
- unresolved or ambiguous global references;
- deterministic closure independent of member discovery order.

Keep `UBL-03` and the complete-graph flag open. Never mutate XLIFF paths while
using this fallback.

## F. Checkpoint and shift

1. Fetch GitLab and prove `origin/main` is an ancestor of `HEAD`.
2. Stage only exact reviewed owned paths.
3. Run coordination `precommit-check`.
4. Commit and push the bounded implementation.
5. Rerun its proof from the immutable commit.
6. Append one native hash-chained event before projections.
7. Update controller and taskcard without changing promotion.
8. Commit and push the plan-control checkpoint.
9. Refresh this provider-neutral packet through its registered skill.
10. Validate hashes, links, YAML/JSON, journal, projections, ancestry, task
    registration, clean workspace, and negative controls twice.
11. Commit and push the handover.
12. Release only the outgoing identity's leases, then complete that session.

Before reporting the shift, answer all 15 AGENTS.md self-challenge questions.
A green test suite, candidate count, or generated classification is not a
production or conformance claim.
