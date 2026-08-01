---
artifact_id: FF6-CURRENT-SHIFT-HANDOVER-EVENT-40
artifact_type: provider_shift_handover
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-08-01
---

# Outgoing shift: Event 40 production checkpoint

## Goal that remains active

Deliver six independently publishable, production-grade Python libraries for
IPYNB, OpenRaster, NRRD, XLIFF, SafeTensors, and OASIS UBL, together with
content-addressed proof machinery, independent repository extraction, complete
verification, and release-ready artifacts. The mission is not complete until
all six are technically certified. Current certification is `0/6`.

## Where this shift started

The accepted controller head was Event 39 at semantic commit `39b2e89f`.
XLIFF had 30/105 source-bound Core obligations and 8/1,130 independently
verified candidate dispositions. The exact candidate was the XLIFF 2.1 F5S
source-side `sc isolated=yes` report.

## What was implemented

The shift completed bounded contract microstep
`XLF-04-BATCH-005-PARTIAL-002-H` at semantic commit
`d95af5aeb248907b4d23457ecd288723fc9c2050`.

Implemented evidence and machinery:

- exact SAL fact `SAL-XLIFF-D5C1325C047A7CB0` / `FACT-XLIFF-34` with six
  executed assertions and proof SHA-256
  `c584c795046953ff73f4de7db941bdbae9abd35fc0d838bf9cc297b9790a3085`;
- decision `XLF-ADJ-CORE-SCHEMATRON-0009`, SHA-256
  `48ca690f9a75720e407b485666b0c87b1d09d6deeba06ad3fc6f38f272c20ba9`;
- acceptance of direct owner `SAL-XLIFF-CORE-INLINE-ISOLATION-001`;
- exact stable-profile prose binding plus XLIFF 2.1 F5S executable rejection
  evidence;
- explicit rejection of generic validator, incidental hierarchy, complete
  element-surface, `startRef`, and source-cardinality overclaims;
- exact candidate-proof enforcement in the obligation compiler;
- one new authority-bound obligation with all predecessors preserved; and
- fresh ProductContract compilation at SHA-256
  `d584e217f5f2d06bcd71723d5d89e60c24a39f3273e8967fe920d4b03bacfc69`.

The control projection was sealed as `FF6-EVENT-000040`, event hash
`c9c7167d447fbe0945c7a65c288f3cece78c64090e09c1ce2d674fdbf9bf2d63`,
and pushed at control commit `de569544eebc1fff011901e61d3574dcc48e5e08`.

## Exact verified boundary

- Expected XLIFF Core obligations: 105.
- Source-bound obligations: 31.
- Missing obligations: 74.
- Candidate census: 1,130.
- Independently verified dispositions: 9.
- Unverified dispositions: 1,121.
- XLIFF ProductContract: `DRAFT`, 15 capabilities.
- XLF-04 and UBL-03: incomplete.
- Product source, gate, promotion, and release effect: none.
- All six promotions: `UNASSESSED`.
- Technical certifications: `0/6`.

All 30 predecessor obligations and 8 predecessor decisions remain semantically
identical. Exactly one obligation and one decision were appended.

## Verification performed

- 113 affected tool tests passed.
- 94 format-contract tests passed with only the named stateful CSV test
  deselected; 69 production-program tests passed.
- All 34 XLIFF SAL facts passed.
- Three exact same-input runs reproduced adjudication digest
  `51ac3adc6fa530246ff25b70e179d040d68eeb65dc8a744794e0d4fbe7738e42`
  and obligation inventory digest
  `7bb46e814b5be12ad313ba0ec77c0585a279f8f85f6cb974481414368c5e713b`.
- Ruff, strict Mypy, Pyright 1.1.411, and py_compile passed.
- Four semantic transcripts and the Event 40 plan-control transcript validate
  with zero warnings.
- Detached replay from `d95af5ae` passed the focused tests and every changed
  descendant check with all five authority records materialized.

## Incidents and structural lesson

The candidate queue was initially written before immediate coordination
`record-write`, creating an own-session conflict. It was journaled, resolved
with same-session evidence, and rebaselined. The first SAL verifier evidence
string missed an authority-rendering space before a comma; the exact pinned
text was restored without weakening the requirement. A post-apply shell parser
then raised `KeyError` even though the verifier had already applied valid
files; read-only verification confirmed the result.

The first detached replay collected no tests because of an incorrect working
directory and selector. The next replay omitted `src-xliff-003.bin`, so the
contract check failed. Both attempts are non-promoting. The accepted replay
recreated the worktree and included all four cached binary authorities plus the
tracked product-requirement authority.

This revealed a machinery weakness: the contract compiler currently hashes a
missing local authority as empty bytes instead of failing closed. It did expose
drift, so no false acceptance occurred, but the compiler should eventually
reject the missing input before compilation.

## What remains

The immediate work is candidate
`XLF-CAND-CORE-SCHEMATRON-60B596A00F7FA06A` in
`XLF-04-BATCH-005-PARTIAL-002-I`. Beyond it, 1,121 candidate dispositions, 74
expected Core obligations, every module inventory, profile compilation,
product architecture, production source, installed-wheel proof, cross-platform
matrices, interoperability, fuzzing, mutation testing, packaging, repository
extraction, and release evidence remain open.

Portfolio truth:

- IPYNB, NRRD, SafeTensors: partial source/tests; not certified.
- OpenRaster: product source absent.
- XLIFF: contract repair in progress; source is not authorized by this checkpoint.
- UBL: contract/schema graph work in progress; all 91 roots are not yet a
  production typed library.

## Exact next action

Resume from Event 40 and GitLab semantic commit `d95af5ae`. Execute
`XLF-04-BATCH-005-PARTIAL-002-I` exactly as specified in
[NEXT-MICROSTEP.yaml](NEXT-MICROSTEP.yaml). Begin with an independently
constructed failing test. Determine whether the target-side report completes
reciprocal evidence for the existing isolation obligation; do not duplicate
the obligation. Append Event 41 only after committed immutable replay succeeds.

The incoming provider must create a fresh coordination identity, leases,
execution manifest, and mutation authorization. Nothing provider-local
transfers. Commit explicit files to GitLab `main` only.
