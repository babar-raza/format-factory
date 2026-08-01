---
artifact_id: FF6-XLIFF-CLEAN-REPLAY-REPAIR-809CC18
artifact_type: verified_repair_handover
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-08-01
---

# XLIFF clean-replay repair: completed technical checkpoint

## Outcome

Repair commit `809cc18cc6e62ae19f6ea5c11ed41ab9a7ec5956` is on GitLab
`origin/main` and passes clean Windows checkout replay. It makes the reciprocal
skeleton adjudication from non-promoting semantic commit
`2dcb161ed8e53bfc55e5be81374f5f7ddea3bb17` portable without changing its
meaning. No Event 36 was appended, so native authority remains
`FF6-EVENT-000035` and the exact continuation remains
`XLF-04-BATCH-005-PARTIAL-002-D-REPLAY-REPAIR-001`, now in
`VERIFIED_PENDING_CONTROLLER_ACCEPTANCE`.

## Symptom, root cause, and structural weakness

The symptom was five failures among 71 affected XLIFF tests in a clean Windows
checkout, all reporting a stale canonical SAL manifest digest. The shared
worktree passed.

The immediate root cause was raw-byte identity applied to text that Git could
materialize differently under checkout configuration. The XLIFF evidence
manifest also contained mixed line endings (821 CRLF lines and 29 LF lines),
while the clean checkout normalized it to LF. Two proof tools were likewise
CRLF in the shared copy and LF in Git. Receipts therefore captured workstation
materialization, not a stable repository identity.

The structural weakness was broader than a stale receipt:

- no repository-wide checkout policy covered proof-bearing text;
- producers and consumers did not share one materialization invariant;
- mutable shared-worktree success was allowed to precede immutable replay;
- derived receipts could appear current even when their tool/input byte closure
  differed in another supported checkout.

A local receipt refresh would have hidden the symptom and preserved the defect.

## Implemented durable repair

- `.gitattributes` now enforces LF for proof/source text and explicitly leaves
  byte-sensitive samples, fixtures, and extension payloads unconverted.
- `tests/governance/test_proof_checkout_identity.py` adds 44 positive and
  negative controls for supported checkouts, semantic tampering, mixed digest
  models, stale receipts, deleted inputs, and cross-format reuse.
- A registered `proof-checkout-identity-repair` skill and governed transcripts
  make the repair repeatable.
- The XLIFF manifest and verifier closure were rematerialized from immutable LF
  checkout bytes.
- Only current invalidated descendants were regenerated: SAL proof references,
  current receipt, adjudication, and obligation inventory. Historical receipts
  were not rewritten.
- No authority facts, claims, decisions, obligation identities, profile
  semantics, candidate identities, source code, gate, certification, or
  promotion state changed.

## Bound evidence

Final current hashes:

- XLIFF evidence manifest: `e590c75a2fb815873b3260b841084c75ac8b6f2b6de17628bd71557fa88a12db`
- `verify_sal_facts.py`: `1abaab1f52b9ab70f7338bda741881dcb224bbaeec1de8f84c6e131245001aa3`
- `sal_proof.py`: `69ef2ef2fe2e30f428dcefe576284832b0effd9b03bd2af6f0fc80ad4c3ddeb7`
- current SAL store: `a9ba1ddcb109ab17a7f7a954891e929cf8c90db5c21b589b9f846cedd15850e8`
- verification receipt: `9eccaa7f7327fb6f05439a6630986f15e7699739fcc0a08c60cca190219b1b34`
- adjudication: `878c12670c5c19889259d6def1439ab106304084fee95d8257819f58879b22d2`
- obligation inventory: `76f51e51216f1b6b8fb41e24623e806bb63ad9ab15da279f16157ffe7369bf1d`
- `.gitattributes`: `906054a6ac57f272e8ac337338a78dfea905776f6a1d2e8cf714148c99dfc982`
- checkout regression test: `1f3a2c4dc53f9f14d5a071b74560da067383f1d3ba63c773f340931d11ecdc96`

Verification at exact commit `809cc18c`:

- clean Windows/autocrlf replay: 115 tests passed (44 checkout identity, 21
  adjudicator, 50 extractor);
- production program: 69 passed;
- format contract: 94 passed and exactly one known stateful test deselected,
  `test_full_slice_second_run_is_idempotent`;
- three clean generations produced identical adjudication and inventory bytes;
- five XLIFF authority locks matched, with zero missing or mismatched records;
- SAL check/apply produced zero diff;
- Ruff, strict Mypy, Pyright 1.1.411, and `py_compile` passed;
- repair skill transcripts validate with zero warnings.

## What is preserved

- Event 35 and its hash chain;
- accepted implementation `591fcfe18808e5195c33570eaa9d334770e90166`;
- semantic attempt `2dcb161ed8e53bfc55e5be81374f5f7ddea3bb17`;
- all 1,130 candidate identities and 105 obligation identities;
- 28 resolved and 77 missing obligation rows;
- no product source or public API changes.

## What remains

The materialized adjudication contains 5 verified dispositions and 1,125 open,
but Event 35 accepts only 4 and 1,126. This is not a contradiction: native
state deliberately lags verified materialized evidence until `plan-control`
commits Event 36. The next executor must perform only that acceptance
transaction, then derive the next candidate dynamically.

The repair proves checkout identity for the covered proof paths. It does not
prove every future generated artifact portable, and it does not replace
installed-wheel, cross-platform product, corpus, oracle, security, fuzz,
mutation, performance, or release certification.
