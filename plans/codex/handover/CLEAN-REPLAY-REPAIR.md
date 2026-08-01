---
artifact_id: FF6-XLIFF-CLEAN-REPLAY-REPAIR-001
artifact_type: provider_neutral_repair_handover
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-08-01
---

# XLIFF clean-replay repair — exact continuation

This file is the executable delta from accepted native Event 35. It does not
replace the journal or promote the attempted microstep.

## Immutable state

- Canonical forge/branch: GitLab `origin/main` only.
- Current remote commit: `2dcb161ed8e53bfc55e5be81374f5f7ddea3bb17`.
- Last accepted native state: `FF6-EVENT-000035` /
  `2866d7e70bd193f8aa7b60ca1f92f4f842d1cd470f97984c07f47d88ed2ea97d`.
- Accepted XLIFF implementation: `591fcfe18808e5195c33570eaa9d334770e90166`.
- Non-promoting reciprocal implementation attempt:
  `2dcb161ed8e53bfc55e5be81374f5f7ddea3bb17`.
- Accepted XLIFF boundary remains 28/105 obligations, 77 missing, 4/1,130
  candidate dispositions accepted, 1,126 open, XLF-04 incomplete.
- Program certification remains 0/6; all promotions remain `UNASSESSED`.

Do not revert or rewrite `2dcb161e`. It contains valid implementation and
test evidence, but clean-checkout replay rejected promotion.

## What the attempted microstep implemented

`XLF-04-BATCH-005-PARTIAL-002-D` independently adjudicated candidate
`XLF-CAND-CORE-SCHEMATRON-8D50B407E90E354E`, the XLIFF 2.1 Schematron report
at `schematron/rule[11]/report[2]` that rejects a `skeleton` containing both
`href` and child content. It:

- mapped the report only to existing direct owner
  `SAL-XLIFF-CORE-REFERENCE-SKELETON-HREF-001`;
- rejected downstream generic-validator ownership;
- rejected broader skeleton-hierarchy ownership as incidental context;
- required both reciprocal skeleton reports before the biconditional
  obligation is considered completely evidenced;
- retained the 28-obligation denominator result and all 1,130 candidate IDs;
- added no product source and no new obligation ID.

Shared-worktree verification passed:

- 71 affected adjudicator/extractor tests;
- 43 production-program tests;
- 94 format-contract tests with only
  `tests/format_contract/test_consumption_chain.py::test_full_slice_second_run_is_idempotent`
  deliberately deselected because it is a known stateful shared-worktree test;
- three byte-identical adjudication and inventory generations;
- 27/28 predecessor rows unchanged and all four predecessor decision objects
  unchanged;
- Ruff, strict Mypy, Pyright 1.1.411, and `py_compile`;
- canonical SAL verification and five matching XLIFF authority records;
- three zero-warning implementation transcripts.

## Promotion-blocking failure

A clean detached Windows worktree at exact commit `2dcb161e` produced 5
failures and 66 passes. Every failure terminated at `canonical SAL manifest
digest is stale`:

1. `test_adjudication_accepts_denominator_owner_omitted_by_generator`
2. `test_subflow_pair_adjudication_requires_both_reciprocal_decisions`
3. `test_skeleton_href_adjudication_records_incidental_unproposed_owner`
4. `test_skeleton_href_obligation_requires_both_reciprocal_reports`
5. `test_cli_batch_five_compiles_only_reciprocally_adjudicated_pairing_obligation`

Observed byte evidence:

| Input | Shared LF worktree SHA-256 | Clean Windows checkout SHA-256 |
|---|---|---|
| `shared/sal-facts/evidence/xliff.yaml` | `3a961199eb156658c978f36361f483498aefcd5e7a1582c14df6577a53410b9a` | `dd5b1b37dbfa8c2f435dbaf4e4c6015842dba3be54fe4f31e9d042ae80d4471b` |
| `reports/sal-verification/xliff.json` | `911ebf4d9701af71d117af2a2347e0b2e102a5b8f5104af9e162355dd095daa2` | `79b4f06919885d999fcbf4f26ffb4aa75d3b946e35b2e984bdc1ce42c3a89f1e` |
| `shared/sal-facts/xliff.yaml` | `1a94baa5f19e4d09f438a6325580e5e9d2969be8529d72103d9d849486061fe7` | `f41de8ac36d15510194f42052f77ffdbe56528210a6ec0d836dde18219185ec4` |
| `reports/ff6/xliff-core-authority-candidate-census.yaml` | `24c1902b6387cc9fa3402f78392ba91c6e6656407719ec11cfaab1c4f3d22b9e` | `c185c46d55e8e7ae7ac250f8455b57055d6461491b5fcedc7f11accc8aee5f76` |
| `reports/ff6/xliff-core-obligation-denominator.yaml` | `264e0092b27789dca60e210233f99088ee90c7e747c0765cf9c99286a5b4783f` | `8b6b00d6296458e4e17ef2f96f10f1eb81f8c53a0c4725d4c24b495f34037898` |

Recompute all hashes before using them as repair inputs; the packet validator
treats live Git objects as authority.

## Root cause and structural weakness

The visible symptom is a stale-manifest exception. The root cause is a split
digest model:

- `.gitattributes` does not declare an EOL policy for proof-bearing YAML and
  JSON;
- Git can materialize the same tracked object as LF or CRLF depending on
  checkout configuration;
- SAL receipts, adjudication, and inventory tooling bind raw worktree bytes;
- the FF6 controller separately claims `CRLF_TO_LF` canonicalization and Git
  object database authority;
- producers and consumers therefore do not share one byte identity.

This is the concrete live manifestation of existing
`FF6-GAP-011/FF6-HO-GAP-003`. It can affect more than XLIFF. A local receipt
refresh would hide the failure in one checkout and make portability worse.

## Exact repair task

Execute `XLF-04-BATCH-005-PARTIAL-002-D-REPLAY-REPAIR-001`.

1. Fetch GitLab and require `HEAD == origin/main == 2dcb161e...`.
2. Run the packet validators. They should pass the handover state while
   retaining the documented product replay failure.
3. Register a fresh provider identity; do not reuse any identity, token,
   lease, authorization, or manifest from this packet.
4. Query skill/capability registries. Existing XLIFF product skills do not
   authorize `.gitattributes` or repository-wide digest-policy changes. Use
   the registered missing-skill workflow and create/repair a narrowly scoped
   machinery skill before mutating those paths.
5. Add a RED regression that creates two clean worktrees from the same commit,
   including a Windows-style `core.autocrlf=true` checkout, and proves the
   current proof replay disagrees.
6. Choose one invariant:
   - preferred: declare stable LF checkout bytes for all tracked proof-bearing
     text through a reviewed `.gitattributes` policy; or
   - if raw checkout bytes cannot be constrained, route every proof producer
     and consumer through one shared canonical-text digest primitive.
7. Do not combine the two models or keep a fallback that accepts either hash.
   That would weaken tamper detection and make evidence ambiguous.
8. Add negative controls for content changes, CRLF-only changes, stale
   receipts, mixed raw/canonical hashes, deleted inputs, and cross-format
   evidence reuse.
9. Rebuild only descendants whose declared digest inputs change. Preserve
   immutable historical receipts and record their invalidation; do not edit
   them into apparent currency.
10. Replay `2dcb161e` plus the repair in a fresh detached Windows worktree.
11. Require all 71 affected tests, 43 production-program tests, 94
    format-contract tests with the exact named deselection, three identical
    generations, tamper tests, static checks, SAL verification, five authority
    matches, and zero-warning skill transcripts.
12. Only after clean replay passes may the next native event accept
    PARTIAL-002-D, move accepted dispositions from 4 to 5, and derive the next
    candidate from the live unverified projection. Do not guess that candidate
    in advance.

## Regression controls that must remain

- Same Git object plus supported checkout configurations yields one canonical
  proof identity.
- A semantic byte change invalidates all correct descendants.
- Line-ending normalization cannot conceal a non-EOL content change.
- A raw digest cannot satisfy a canonical-digest field and vice versa.
- Clean source checkout and shared worktree produce the same result.
- Generated evidence never promotes itself.
- Event 35 remains accepted until an independently replayed successor event is
  committed and validated.

## Tradeoffs and limits

An LF `.gitattributes` policy is small and makes raw-byte hashes reproducible,
but it changes checkout behavior for contributors and must cover every
proof-bearing extension/path. A canonical-text digest primitive is more
portable for text, but requires migrating every producer/consumer and clearly
separating binary raw hashes from normalized text hashes. Either choice needs
a repository-wide inventory; a one-file fix is insufficient.

This repair does not deepen XLIFF capabilities, finish XLF-04, implement any
library, certify a product, authorize release, or change Gate 10.
