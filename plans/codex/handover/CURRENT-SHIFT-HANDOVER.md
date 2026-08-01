---
artifact_id: FF6-CURRENT-SHIFT-HANDOVER-EVENT-39
artifact_type: provider_shift_handover
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-08-01
---

# Outgoing shift: Event 39 production checkpoint

## Goal that remains active

Deliver six independently publishable production-grade Python libraries for
IPYNB, OpenRaster, NRRD, XLIFF, SafeTensors, and OASIS UBL, together with
content-addressed proof machinery, independent repository extraction, complete
verification, and release-ready artifacts. The mission is not complete until
all six are technically certified. Current certification is `0/6`.

## Where this shift started

The accepted controller head was Event 38 at semantic commit `3fc939ad`.
XLIFF had 30/105 source-bound Core obligations and 7/1,130 independently
verified candidate dispositions. The selected work was target `xml:lang`
versus root `trgLang` semantics. A read-only investigation had exposed a
conflict between display prose and executable XLIFF 2.1 Schematron but had not
adjudicated it.

## What was implemented

The shift completed one bounded contract microstep,
`XLF-04-BATCH-005-PARTIAL-002-G`, at semantic commit
`39b2e89fde0f7dd5e1acebc424f4d700dfe74765`.

Implemented evidence and machinery:

- profile-aware target-language semantics for XLIFF 2.0 and 2.1;
- exact XLIFF 2.0 equality versus XLIFF 2.1 exact-or-more-specific behavior;
- explicit normative machine-readable precedence over conflicting 2.1 display
  prose;
- canonical fact `SAL-XLIFF-6F42212680161FF2` / `FACT-XLIFF-33` with ten
  executed assertions and proof SHA-256
  `d34684502ae62f211ca59fba60d947421fac3aa7bf436ae55efd3f209862fe14`;
- decision `XLF-ADJ-CORE-SCHEMATRON-0008`, SHA-256
  `93dd097010ceb3f5c0699336a1089ad7b1013293e524aede4040a3de48e1356e`;
- acceptance of the existing direct owner
  `SAL-XLIFF-CORE-TARGET-LANGUAGE-001`;
- explicit rejection of generic validator, hierarchy, segment, optional-target,
  root-presence, and omitted-inheritance overclaims;
- profile correction of the existing obligation without denominator expansion;
- missing authority source registration `SRC-XLF-001` repaired in the XLIFF
  research contract;
- fresh ProductContract compilation at SHA-256
  `7ef89b038b8b74b59ede6123a7a2ec57fea4730f84fbff3eaf21a43d02a9a2ad`.

The control projection was then sealed as `FF6-EVENT-000039`, event hash
`5f76c75ca4f7bc0845b22dccd38a195e962fb49b5f4161651737ab23d560cd36`,
and pushed at control commit
`c421940ae70a3dc949318eee00cbfc5e3cf8b9a3`.

## Exact verified boundary

- Expected XLIFF Core obligations: 105.
- Source-bound obligations: 30.
- Missing obligations: 75.
- Candidate census: 1,130.
- Independently verified dispositions: 8.
- Unverified dispositions: 1,122.
- XLIFF ProductContract: `DRAFT`, 15 capabilities.
- XLF-04: incomplete.
- UBL-03: incomplete.
- Product source effect: none.
- Gate/promotion/release effect: none.
- All six promotions: `UNASSESSED`.
- Technical certifications: `0/6`.

Twenty-eight unaffected predecessor rows remained semantically exact. One
existing target-language row changed profile semantics. It would be false to
claim that all 30 rows were byte- or semantically unchanged.

## Verification performed

- 77 affected adjudicator/extractor tests passed.
- 191 tests passed across selected seeding, SAL verification, contract, and
  production-program tiers; the exact known stateful CSV test was deselected.
- After contract refresh, 163 contract/production tests passed with the same
  exact deselection.
- All 33 XLIFF SAL facts passed.
- XLIFF authority audit passed 5/5 with zero missing, mismatched, undeclared, or
  legal-blocked records.
- Three exact same-input runs reproduced:
  - denominator
    `86a4f2cdc6e4a341eba2a3cbb6fcc8119883d1cda64d056198c7c34b7fa880b7`;
  - census
    `9f10464e14c55a36ee1e54a5d12d04e8e23f19d2cb94d7c0c732cb40861db4b7`;
  - adjudication
    `d63a31f936262c9952a0f50afd076b8547bc5c26cbdfd5adf04464b5f2c3dcc2`;
  - obligation inventory
    `ea376cbaad5e8559b6789844be2bef06478e5b8ee69f7a3c557cfbc5bd474370`;
  - compiled contract
    `7ef89b038b8b74b59ede6123a7a2ec57fea4730f84fbff3eaf21a43d02a9a2ad`.
- Ruff, strict Mypy with explicit package bases, Pyright 1.1.411, and
  py_compile passed.
- Four semantic skill transcripts and the Event 39 plan-control transcript
  validated with zero warnings.
- Immutable detached replay from `39b2e89f` passed the 77-test slice, SAL,
  contract check, and 5/5 authority closure.

## Critical replay lesson

A detached replay with only the two XLIFF packages is incomplete. It can pass
focused tests and SAL verification while the ProductContract check differs.
The full replay requires:

1. ignored `src-xlf-001.bin`;
2. ignored `src-xlf-002.bin`;
3. ignored `src-xliff-001.bin`;
4. ignored `src-xliff-003.bin`; and
5. the tracked product-requirement authority.

This is an input-closure requirement, not optional setup. A future controller
should materialize these content-addressed inputs automatically rather than
relying on a provider to remember them.

## What remains

The immediate remaining XLIFF work is candidate
`XLF-CAND-CORE-SCHEMATRON-E891C4DEC555F165` in
`XLF-04-BATCH-005-PARTIAL-002-H`. Beyond that bounded candidate, 1,122
candidate dispositions, 75 expected Core obligations, every module inventory,
profile compilation, product architecture, production source, installed-wheel
proof, cross-platform matrices, interoperability, fuzzing, mutation testing,
packaging, repository extraction, and release evidence remain open.

Portfolio truth remains:

- IPYNB: partial source and tests; not production-certified.
- OpenRaster: product source absent.
- NRRD: partial source and tests; not production-certified.
- XLIFF: contract repair in progress; product source not authorized by this
  checkpoint.
- SafeTensors: partial source and tests; not production-certified.
- UBL: contract/schema graph work in progress; 91 roots are counted but the
  complete type graph and product implementation are unfinished.

These statements are boundaries, not estimates of percentage completion.

## Exact next action

Resume from Event 39 and GitLab semantic commit `39b2e89f`. Execute
`XLF-04-BATCH-005-PARTIAL-002-H` exactly as specified in
[NEXT-MICROSTEP.yaml](NEXT-MICROSTEP.yaml). Begin with an independently
constructed failing test. Treat all eight mappings as proposals, preserve all
accepted rows and candidate identities, and append Event 40 only after a
committed immutable replay succeeds.

## Shift-transfer rules

The next provider must create a fresh coordination identity, leases, execution
manifest, and mutation authorization. Nothing provider-local transfers. If
required paths are live-owned, do read-only work or a deterministic disjoint
task; never seize a live lease. Commit explicit file lists to GitLab `main`
only. A clean shift ends with remote validation and owned lease release.
