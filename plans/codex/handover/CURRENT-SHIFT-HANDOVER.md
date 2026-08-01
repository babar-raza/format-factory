---
artifact_id: FF6-SHIFT-HANDOVER-809CC18
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-08-01
---

# Outgoing Codex shift: verified checkpoint for Claude

## Work completed this shift

The shift began from semantic attempt `2dcb161e`, which passed in the shared
worktree but failed five affected tests in a clean Windows checkout. The work
did not accept the stale local proof or weaken hashes. It traced the failure
through the complete proof input closure, established a checkout-byte policy,
added adversarial regression controls, regenerated only invalidated current
descendants, and independently replayed the actual commit.

The durable repair is GitLab main commit
`809cc18cc6e62ae19f6ea5c11ed41ab9a7ec5956`. It contains:

- explicit LF policy for proof/source text and binary treatment for
  byte-sensitive samples/fixtures;
- a registered `proof-checkout-identity-repair` production skill;
- 44 checkout-identity tests;
- corrected LF identity for the XLIFF evidence manifest and verifier closure;
- refreshed current SAL proof, receipt, adjudication, and inventory;
- zero-warning governance/skill transcripts.

No XLIFF product source, authority fact, semantic adjudication, obligation ID,
gate, promotion, certification, or release state was changed by the repair.

## Evidence actually observed

At exact commit `809cc18c` in a clean Windows/autocrlf worktree:

- 115 repair/affected tests passed;
- 69 production-program tests passed;
- 94 format-contract tests passed with exactly the known stateful
  `test_full_slice_second_run_is_idempotent` deselected;
- three clean regenerations were byte-identical;
- five XLIFF authority records matched;
- SAL apply/check produced no diff;
- Ruff, strict Mypy, Pyright 1.1.411, and bytecode compilation passed;
- GitLab `HEAD == origin/main == 809cc18c` after push.

This is strong proof for the bounded repair. It is not product certification.

## Exact state left for the next provider

Native controller head remains `FF6-EVENT-000035` /
`2866d7e70bd193f8aa7b60ca1f92f4f842d1cd470f97984c07f47d88ed2ea97d`.
No Event 36 was appended because implementation/repair proof and controller
acceptance are separate transactions.

Accepted Event 35 state is 4 verified and 1,126 open candidate dispositions.
Materialized files at `809cc18c` contain 5 verified and 1,125 open. Both retain
105 expected obligations, 28 resolved, 77 missing, and `complete=false`.

Therefore the exact next task is
`XLF-04-BATCH-005-PARTIAL-002-D-REPLAY-REPAIR-001` in state
`VERIFIED_PENDING_CONTROLLER_ACCEPTANCE`. Claude must use `plan-control` to
append one Event 36, update accepted projections, derive the next candidate
from live data, refresh this handover, and stop at another clean checkpoint.
Claude must not redo the semantic or checkout repair.

## Six-product truth

- 0/6 products are technically certified and all promotions are `UNASSESSED`.
- OpenRaster product source is absent.
- IPYNB, NRRD, XLIFF, SafeTensors, and UBL contain useful but incomplete
  pre-production code.
- XLIFF contract work is incomplete at XLF-04.
- UBL schema graph work is partial through derivation edges; UBL-03 remains
  incomplete.
- No package has the full independent corpus/oracle, security/resource,
  fuzz/mutation, installed-wheel OS/Python matrix, reproducible package,
  SBOM/provenance/signature, and release proof required by the mission.

## Shift interchange protocol

The next agent reconstructs only from GitLab, the native journal/controller,
taskcards, proof artifacts, and this content-addressed packet. Provider-local
identity, leases, manifests, authorizations, temp worktrees, and chat memory
are intentionally non-transferable. A provider ending a shift must leave one
immutable pushed commit, one validated packet, no unexplained local overlay,
and only an evidence-derived exact next task.

The outgoing identity is not authority and must not be reused. Freshly query
coordination because other stale/live records are machine-local and may change
after this packet is committed.

## Risks and limits

- A handover packet is a derived projection; the native journal and current
  repository evidence win if they advance.
- The LF policy protects declared text classes, but new generators or unusual
  byte-sensitive formats require explicit classification and regression tests.
- The accepted/materialized split is safe only because validation checks both;
  leaving it unresolved across later unrelated controller events would create
  ambiguity. Event 36 is therefore the highest-priority next transaction.
- Publication remains far away: the repair closes proof portability, not
  format capability or release readiness.
