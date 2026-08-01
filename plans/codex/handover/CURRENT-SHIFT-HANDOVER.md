---
artifact_id: FF6-CURRENT-SHIFT-HANDOVER-EVENT-38
artifact_type: provider_shift_record
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-08-01
---

# Outgoing shift: Event 38 handover hardening checkpoint

## Outcome

The outgoing Codex shift completed and pushed one bounded XLIFF contract slice
and its controller projection. The semantic commit is
`3fc939ad70ec6caac9e0699041076e02de00c5d2`; the controller checkpoint is
`d1f8b3229bf3be32675e047b1469259ad7375500`; native authority is
`FF6-EVENT-000038` / `13db4cceafcefb86d9c964d7c3e20e7d63092977faf50002ef0c88ea4f6b5603`.

GitLab `origin/main` matched each commit after its push. GitHub and non-main
branches were not used.

This later handover-only shift revalidated the same accepted boundary from
clean GitLab `main` at `62f23b30a13d56bc4e1e369390aaf611e75462b4`.
It did not mutate XLIFF source, SAL stores, the obligation denominator,
controller state, gate state, or promotion state.

## Semantic work completed

The shift independently adjudicated
`XLF-CAND-CORE-SCHEMATRON-B0961B8D3678CA73`, the XLIFF 2.1 source-language
compatibility report. It:

- added exact candidate-ID selection to the SAL seeder;
- failed closed on missing and duplicate IDs;
- isolated unrelated invalid queue rows from selected mode;
- prevented QName collision when canonical fact IDs are hashed;
- scoped the merge subprocess to XLIFF;
- restored store, aliases, and cache on merge failure;
- preserved existing store bytes and proved selected-rerun idempotency;
- seeded `SAL-XLIFF-39A807E74F92A266` with exact authority evidence;
- accepted only `SAL-XLIFF-CORE-DOCUMENT-SOURCE-LANGUAGE-001`;
- rejected generic validator behavior, segment and ignorable trigger context,
  source cardinality, and omitted-value inheritance overclaims;
- narrowed the obligation to XLIFF 2.1 because the pinned 2.0 authority lacks
  the compatibility constraint;
- preserved all 29 predecessor obligation rows and all 1,130 candidate IDs.

The accepted projection is 7/1,130 candidate dispositions and 30/105
source-bound obligations. XLF-04 remains incomplete.

## Proof executed

- Seeder tests: 15 passed.
- Adjudicator tests: 23 passed.
- Extractor tests: 52 passed.
- Affected shared-worktree total: 90 passed.
- Affected immutable-detached-checkout replay: 90 passed.
- Production-program regression: 69 passed.
- Format-contract regression: 94 passed with only
  `tests/format_contract/test_consumption_chain.py::test_full_slice_second_run_is_idempotent`
  deliberately deselected as the exact baseline-known stateful test.
- Denominator, census, adjudication, and inventory check modes reproduced
  exact expected digests.
- All 32 XLIFF SAL facts passed; five of five authority locks matched.
- Selected seeding preserved store, aliases, and cache bytes on rerun.
- Ruff, strict Mypy with established import flags, Pyright 1.1.411 with zero
  diagnostics, py_compile, three semantic transcripts, and the 40-test native
  plan-control suite passed.
- The full 38-event native hash chain and controller/taskcard projection passed.

## Evidence identities

- denominator: `86a4f2cdc6e4a341eba2a3cbb6fcc8119883d1cda64d056198c7c34b7fa880b7`
- candidate census: `9f10464e14c55a36ee1e54a5d12d04e8e23f19d2cb94d7c0c732cb40861db4b7`
- adjudication: `61f17b6449ae1ea6b5a95c892afc075b48aa7b9a100be2d6e8168b8794baeb32`
- obligation inventory: `483767b208b75b880804288a6f56ed3758b05d46d4ef872bc0bcb6e4d083e1ba`
- new fact proof: `2db27ac01f5b31faf2041066663ef76826582c0963b29c8388f86a164ecd0d46`
- decision: `636d2524c6b9d7ccd5b71a248924d1a4be2778c4e7cd321ad81caa00f4ee13d0`

## What remains

The immediate successor is `XLF-04-BATCH-005-PARTIAL-002-G`, candidate
`XLF-CAND-CORE-SCHEMATRON-5D563A565DC6DCFE`. The next provider must begin with
a genuine RED test and independently adjudicate target `xml:lang` versus root
`trgLang`. Source-language symmetry is useful context but is not proof.

Read-only inspection narrowed the first RED test without deciding it. The
existing direct-owner hypothesis is `SAL-XLIFF-CORE-TARGET-LANGUAGE-001`.
Pinned XLIFF 2.0 and 2.1 target prose require exact equality, but the XLIFF 2.1
F4T Schematron note and its `lang($trgLang)` expression permit a more-specific
target-language subcategory. Claude must encode equal, more-specific, and
reverse-specific cases before changing the obligation or accepting the
candidate. This contradiction is deliberately unresolved.

Beyond that single candidate, 1,123 candidate dispositions and 75 expected
Core obligation bindings remain open. XLIFF modules, model/API architecture,
product implementation, security, interoperability, packaging, cross-platform
installed-wheel proof, and release evidence all remain. The other five formats
also remain uncertified; ORA product source is still absent.

## Coordination state at handover generation

The handover-refresh identity is
`agent-codex-20260801T122600-c2f6c7`. Its token, manifests, authorizations, and
leases are not transferable.
The coordination plane reported 17 pre-existing open conflicts, none on this
handover packet or the accepted XLIFF semantic paths. They were preserved and
not resolved, taken over, cleaned, or staged.

The incoming provider must requery current coordination state because this
snapshot becomes stale immediately. It registers a new identity, acquires new
leases, and creates new manifests and mutation authorizations. The outgoing
identity is released only after the final handover commit is verified on
GitLab.

## Truth boundary

Nothing in this shift certifies a product. All six products remain
`UNASSESSED`; technical certification is `0/6`; no gate, promotion, release, or
publication state changed.
