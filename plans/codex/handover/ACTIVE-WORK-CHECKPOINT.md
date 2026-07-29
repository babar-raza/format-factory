---
artifact_id: FF6-ACTIVE-WORK-CHECKPOINT-001
artifact_type: provider_neutral_work_checkpoint
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
authoritative_state: false
canonical_event: FF6-EVENT-000025
---

# Active Work Checkpoint: XLIFF Stable Profiles and Modules

This is the provider-neutral shift boundary after XLIFF authority acquisition,
package inventory, completion of the deterministic XLF-03 source-surface
matrix, and 25 journaled source-bound XLF-04 obligations through batch 003.
Fine-grained Core
semantics remain incomplete. Canonical authority
remains the controller, event journal, current-gap projection, and taskcards;
this document explains how to resume them.

## Exact checkpoint

| Field | Value |
|---|---|
| Mission | `FF6-PRODUCTION-LIBRARIES-001` |
| Forge and branch | GitLab `origin/main` only |
| Controller state | `CONTRACT` |
| Controller sequence | `25` |
| Event head | `237f7759e2286cfc08c547c53a0b47d44e1c77307329ec0215c5326e3f811e48` |
| GitLab handover checkpoint | `d02a00fedf669c6e2b2dd58e480715550fb2afe8` |
| Event/controller checkpoint | `220ee7f5b9d39c3684cff6af6331b56a03ae9e75` |
| Last journaled implementation | `2522752776f64ab800a2a21c8fa46c1f2a4e361c` |
| Parent task | `TC-FF6-PROGRAM-CAPABILITIES-001` - `NEEDS_REPAIR` |
| Last completed task | `TC-FF6-NRRD-PROFILE-SURFACE-001` - `PASS` |
| Active task | `TC-FF6-XLIFF-PROFILE-SURFACE-001` - `WORK_IN_PROGRESS` |
| Completed steps | `XLF-01`, `XLF-02`, `XLF-03`, `XLF-04-BATCH-001`, `XLF-04-BATCH-002` |
| First unmet step | `XLF-04` |
| Shift microstate | `RESUMABLE` |
| Exact next action | Execute `XLF-04-BATCH-004` deterministic authority-candidate census |
| Selected finding | `FF6-XLIFF-PROFILE-001` |
| Product source mutation | Prohibited |
| Promotion effect | None |
| Certified libraries | 0 of 6 |

## What was proved

- All 17 authority artifacts remain live `MATCH`.
- All 20 OpenRaster SAL facts now pass exact assertions against the current
  commit-pinned RST authorities. Obsolete HTML proof hashes are gone.
- The previous `SAL-ORA-00014` claim was absent from current authority. The
  correction and reason are retained in fact provenance.
- OpenRaster now uses the dedicated `layered_raster_archive` family with 17
  format-family domains plus three shared lifecycle/preservation/security
  capabilities.
- ORA has 20 explicit developer capabilities and 134 canonical obligations.
- Every ORA capability and obligation declares exact applicability across
  0.0.3/0.0.4/0.0.5. Isolation applies only to 0.0.4/0.0.5.
- Masks are explicitly a safe product extension surface, not claimed as an
  OpenRaster baseline construct.
- `FF6-ORA-SURFACE-001` and `FF6-ORA-PROFILE-001` are absent from live
  compiler output. `FF6-GAP-013` is resolved.
- No product behavior, package, certification, promotion, release, or gate was
  changed or proved.
- The pinned nbformat 4.0-4.5 schemas were compared recursively. The retained
  matrix records 62 source-located leaf changes and all six exact member
  hashes.
- IPYNB now has 25/25 exact SAL facts, 25 profile-homogeneous capabilities,
  and 68 canonical obligations. Every capability and obligation has a
  non-empty exact profile subset.
- Explicit complete fact ownership rejects unknown, duplicate, and unassigned
  IPYNB facts. Cell names cover 4.0-4.5; notebook title/authors and name
  uniqueness begin in 4.2; hidden metadata begins in 4.3; execution timing in
  4.4; cell IDs in 4.5.
- Notebook execution remains `EXCLUDED_WITH_AUTHORITY`. Event 18 closed only
  the IPYNB contract/profile defect; it does not certify the existing product.
- Event 19 compiles the exact NRRD0001-NRRD0005 delta: key/value metadata
  begins in 0002, kinds in 0003, space/orientation and multi-file behavior in
  0004, and measurement frame in 0005.
- All 25 NRRD SAL facts pass exact evidence. Eighteen scientific-raster
  domains and 41 policy IDs assign every fact exactly once.
- The governed research source was repaired where one requirement mixed
  NRRD0004 coordinate transforms with NRRD0005 measurement-frame semantics.
- NRRD now has 21 capabilities and 65 obligations with exact non-empty
  profile subsets. All five profiles are claimed and the live profile gap is
  resolved.
- Teem's permissive acceptance of later fields under earlier magic remains an
  explicit interoperability peculiarity, not a weakened strict contract.
- Event 19 proves only the NRRD normative denominator and deterministic
  projection. It does not certify the existing product.
- Event 20 records an integration-safe XLIFF WIP boundary. The official
  XLIFF 2.0 OASIS Standard ZIP is pinned as `SRC-XLF-001` at SHA-256
  `aaefef5797c2387cfaaa2ca69bfeabe59fa5248535d45d3056b7fad024916055`;
  its published SHA-1 matched the bounded bootstrap probe.
- The embedded XLIFF 2.0 prose is pinned as `SRC-XLIFF-003` at SHA-256
  `4b19c8d7c878c34b5422310f340abf099dedccf968c0a3c145548d3a691da7c2`.
- The tracked authority inventory binds 15 XLIFF 2.0 and 27 XLIFF 2.1
  members (42 total), including schemas, Schematron, NVDL, catalogs,
  normative prose variants, notices, and the informative Change Tracking
  copy.
- Global authority audit is 17/17, XLIFF is 5/5, and clean offline XLIFF
  reconstruction from CAS/repository inputs is 5/5. This closes only XLF-02.
- The safe authority bootstrap command hashes unenrolled bytes under the same
  HTTPS, host, redirect, timeout, and size constraints as materialization,
  persists no bytes, and requires the normal locked re-download before
  acceptance.
- Event 21 bound the first XLF-03 implementation slice to source commit
  `a1316b4fae21c20c71ccb6d60e4b9fe634dca573` without marking XLF-03
  complete.
- `tools/spec/extract_sal_facts.py` now implements exact package digest checks,
  bounded ZIP safety, safe XML parsing, XLIFF 2.0/2.1 Core and module
  inventories, section deltas, source-row validation, canonical YAML bytes,
  atomic output replacement, and drift check mode.
- The compiler distinguishes normative XLIFF 2.0 Change Tracking from the
  informative XLIFF 2.1 copy and assigns both `its` and `itsm` to the single
  XLIFF 2.1 ITS module.
- The committed slice passes 3 focused tests, Ruff, strict Mypy, and bytecode
  compilation. Pyright was unavailable in this shell and is not claimed.
- Event 24 binds the current implementation at immutable commit
  `78660ae1a310ab06cf00d977bbc26fb65914f1c9`.
- The extractor now has deterministic default seeds and CLI/check mode, bounded
  real-authority-safe XML handling, and fail-closed archive/XML/matrix negative
  controls.
- The tracked matrix contains 36 unique source-surface anchors, 293/420
  DocBook sections, 8/8 normative modules, and 8/9 module schema vocabularies
  across XLIFF 2.0/2.1. Three generations are byte-identical at SHA-256
  `9f4ea4b8b71378217af26c0fb2b97a759817a0aca6c64255b8cd55170c60a090`.
- The current XLF-04 suite passes 24 tests, Ruff, strict Mypy, Pyright 1.1.411,
  bytecode compilation, and zero-warning transcript validation.
- Batches 001-002 add 19 cumulative source-bound obligations across ten
  categories, including identifier/reference/inheritance,
  language/direction/whitespace, and source-target correspondence. Their status is
  `SOURCE_BOUND_UNVERIFIED`, the expected-obligation denominator is absent,
  and XLF-04 remains incomplete.
- GitLab commit `25227527`, bound by event 25, adds batch 003. It contains
  25 cumulative obligations and an explicit 105-ID denominator with 80 IDs
  still unresolved. The denominator is deliberately
  `OPEN_AUTHORITY_CENSUS`; all 12 categories having at least one row does not
  close XLF-04.
- The commit separates 21 XLIFF-specification obligations from four Format
  Factory production-policy obligations, binds denominator bytes as a direct
  input, and rejects authority-digest tampering.
- The handover refresh independently replayed 27 focused tests and validated
  both batch-003 transcripts. The broader 94/69 regression and static results
  are transcript-reported until the incoming provider independently replays
  them.

## Current compiled planning state

| Measure | Value |
|---|---:|
| Capabilities | 110 |
| IPYNB obligations | 68 |
| OpenRaster obligations | 134 |
| NRRD obligations | 65 |
| XLIFF obligations | 125 |
| SafeTensors obligations | 86 |
| UBL obligations | 194 |
| Total obligations | 672 |
| Aggregate SHA-256 | `4d17d8c8c0ef3de74d59e1d5b16884c0210fd0836e0593591871f10d0af2efd2` |
| Three-run digest | `389be84634941d3f244387bbc488c2303dcdb3add74b7d1edfb5def85710d3fc` |
| Authority matches | 17/17 global; 5/5 XLIFF |
| Product certifications | 0 |

The portfolio remains `NEEDS_PROFILE_OR_SURFACE_REPAIR` because exact XLIFF
2.0/2.1 module applicability and UBL all-root typing remain.

## Verification boundary

- NRRD format-contract tests: 92 passed; one baseline-known stateful CSV
  idempotency test was deselected.
- Affected verifier/compiler/controller tests: 96 passed.
- Authority dependency-closure tests: 119 passed.
- Ruff: pass.
- Strict Mypy for the touched family-pack validator: pass after adding
  `types-PyYAML 6.0.12.20260724` to the ignored environment. No
  repository-wide Mypy result is claimed.
- Pyright 1.1.411: zero diagnostics.
- NRRD family-pack validation: 18 domains, 41 policy IDs,
  explicit-complete fact ownership, valid, idempotent.
- NRRD SAL exact verification: 25/25 pass.
- Three strict six-format compilations: byte-identical.
- Event-20 focused materializer tests: 12 passed.
- Event-20 format-contract regression: 94 passed; one baseline-known stateful
  CSV idempotency test was deselected.
- XLIFF authority inventory replay: 42/42 exact member size/digest pairs.
- Authority audit: 17/17 match; XLIFF offline reconstruction: 5/5 match.
- Event-20 Ruff, Pyright 1.1.411, and bounded Mypy checks: pass.
- Event-23 extractor checkpoint: 23 tests passed; Ruff, strict Mypy, Pyright
  1.1.411, and bytecode compilation passed; both final XLF-03 skill transcripts
  validate with zero warnings.
- Event-23 real matrix: check mode passed and three identical outputs matched
  SHA-256
  `9f4ea4b8b71378217af26c0fb2b97a759817a0aca6c64255b8cd55170c60a090`.
- Global SAL merge remains non-promoting because of pre-existing ODS/ODT alias
  contradictions. The NRRD cache content was verified and all attempted alias
  side effects were removed.

## Exact resume procedure

1. Read `START-HERE.md`, `CURRENT-MACHINE-STATE.yaml`, `AGENTS.md`, and the
   provider adapter in their declared order.
2. Fetch GitLab `origin/main`; do not use GitHub or create a branch.
3. Require `d02a00fedf669c6e2b2dd58e480715550fb2afe8` to be an ancestor of
   fetched `origin/main`.
4. Verify commits `25227527` and `220ee7f5` are both on `origin/main`.
5. Register a fresh coordination identity and inspect live leases/conflicts.
6. Validate event 25 natively using `previous_event_hash` and canonical JSON
   with `event_hash` removed.
7. Verify the controller names
   `TC-FF6-XLIFF-PROFILE-SURFACE-001` as `WORK_IN_PROGRESS`, with `XLF-04`
   first unmet.
8. Read that taskcard, the product goal, current gaps, capability policy,
   XLIFF contract/SAL/evidence/enrichment, both pinned packages, the tracked
   42-member inventory, the five XLIFF authority records, the committed
   extractor/test/matrix files, and both final XLF-03 skill receipts.
9. Claim exact paths, resolve registered skills, and run the mutation guard
   before every write.
10. Replay event-25 evidence plus the exact six implementation-commit digests,
    27 tests,
    both transcripts, static checks, deterministic reports, and authorities.
11. Obtain governed ownership for the exact batch-004 paths; never reuse or
    release the prior provider identity.
12. Compile the authority-candidate census and reconcile every candidate to
    exactly one expected ID or a reasoned non-obligation disposition.
13. Keep completeness false with 25/105 resolved and 80 expected IDs open.
14. Continue in source-located batches; full expected-ID enumeration and
    canonical SAL verification remain explicit after category coverage.
15. Resume the remaining XLF-04 through XLF-08 work in
    `STATE-MACHINE-AND-TASKCARD-PROTOCOL.md`.
16. Re-run XLF-01 or XLF-02 only if event-20 authority inputs were invalidated.
17. Produce source-located 2.0/2.1 Core and module delta matrices.
18. Split all eight official 2.1 modules—Translation Candidates/Matches,
    Glossary, Format Style, Metadata, Resource Data, Size and Length
    Restriction, Validation, and ITS—into separately owned capability
    families. Account for all nine module schema vocabularies; `its` and
    `itsm` belong to the single ITS module.
19. Inventory Change Tracking as an informative extension and prohibit it
    from satisfying or inflating normative module coverage.
20. Preserve semantic inline pairing/order, segmentation, state, original
    data, skeleton, extension, ITS, agent-processing, canonical XML, security,
    and downgrade-loss obligations.
21. Recompile all six projections and require three identical runs plus a
    complete authority match after adding the 2.0 record.
22. Reconcile gaps/task/controller/event/handover, commit explicit owned paths,
    and push only GitLab `origin/main`.

If the provider shift ends before XLF-08, only stop after the current atomic
step is integration-safe. Journal the completed steps and first unmet step as
`WORK_IN_PROGRESS`, refresh this packet, commit, push, and verify the remote.
Never leave a required result only in conversation or an uncommitted tree.

## Do not infer

This checkpoint does not mean:

- XLF-04 is complete because XLF-03 emitted 36 source-surface anchors or
  batch 001 covered seven categories;
- any of the 672 obligations is implemented merely by this contract work;
- any current source package is production-ready;
- any format has independent interoperability certification;
- the broad cross-platform installed-wheel matrix is current;
- architecture work is unlocked;
- publication is authorized.

Only digest-bound executed behavior can move those states.

## Outgoing self-challenge

The event-25 executor recorded the required governance challenge at the shift
boundary:

1. Required XLF-01 through XLF-03 and XLF-04-BATCH-001/BATCH-002 steps
   performed;
   remaining XLF-04 through XLF-08 work explicit and unclaimed: yes.
2. Required evidence for the event-25 batch boundary present: yes.
3. Evidence sufficient for the source-surface matrix, without claiming
   fine-grained semantic obligations, XLIFF contract closure, or product
   completion: yes.
4. Secondary source substituted where primary authority was required: no.
5. Phase-forbidden file created: no.
6. Product gate self-approved: no.
7. Later product phase entered: no.
8. Commit/push performed without the approved autonomous GitLab-main policy:
   no.
9. Checkpoint inspection preserved before successor execution: yes.
10. Discovered gap left unlogged: no.
11. Relevant memory read: yes.
12. Memory treated only as context: yes.
13. Memory checked against canonical repository state; no contradiction needed
    a gap: yes.
14. Memory update: not applicable; no update was requested.
15. Human review: not applicable; none requested.
