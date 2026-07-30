---
artifact_id: TC-FF6-XLIFF-PROFILE-SURFACE-001
artifact_type: taskcard
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
goal_id: FF6-PRODUCTION-LIBRARIES-001
parent_task_id: TC-FF6-PROGRAM-CAPABILITIES-001
status: WORK_IN_PROGRESS
format_id: xliff
skill_ids:
  - research-format-contract-sources
  - ingest-spec-sal
  - sal-pipeline-heal
  - create-format-family-pack
  - compile-format-contract
  - compile-production-capability-universe
  - create-taskcard
  - plan-control
---

# Compile the Complete XLIFF 2.0/2.1 Profile and Module Surface

## Boundary

Contract, authority, obligation, capability-policy, and deterministic
projection work only. Product source, product tests, packages, certification,
promotion, release, and gates remain prohibited.

This task does not claim that the current 15 broad XLIFF capabilities or 125
compiled obligations are complete. Their present single-profile assignment to
`xliff_2.1` is the defect under repair.

## Objective

Compile an exact, authority-located capability and obligation universe for
stable XLIFF 2.0 and XLIFF 2.1, including Core and every module shipped in the
official XLIFF 2.1 schema bundle. Model XLIFF 2.2 only as an isolated preview
profile, and do not mix XLIFF 1.2 into the XLIFF 2.x object model.

The result must be complete enough to drive a future production library:
typed Core and module models, inline-code and state semantics, processing
requirements, extension preservation, schema validation, deterministic
serialization, and developer-facing editing workflows must each have explicit
owners and exact profile applicability.

## Historical starting state

The bullets below describe the defect when this task was created. They are not
the resume state; event 21 and the checkpoint sections below supersede them.

- The authority lock contains the XLIFF 2.1 OASIS Standard package and its
  prose member, but no separately pinned XLIFF 2.0 Standard package.
- The SAL store contains 31 manually seeded facts with mixed 2.0/2.1 wording
  and shallow module coverage.
- The compiled projection contains 15 broad capabilities and 125 obligations;
  every record claims only `xliff_2.1`.
- `xliff_2.0` is therefore missing, while `xliff_2.2_preview` is named in
  policy but has no isolated compiled capability surface.
- Product source observations and existing tests are non-promoting inputs and
  cannot fill missing normative authority.

## Current checkpoint — event 20

`XLF-01` and `XLF-02` are complete and integration-safe. The task remains
`WORK_IN_PROGRESS`; the first unmet step is `XLF-03`.

- The official XLIFF 2.0 OASIS Standard ZIP is enrolled as `SRC-XLF-001` at
  SHA-256
  `aaefef5797c2387cfaaa2ca69bfeabe59fa5248535d45d3056b7fad024916055`.
- Its published SHA-1
  `4a23114abdca2585a7b2840dae179242aca8eada` matched an independent,
  bounded, non-persisting probe.
- The embedded 2.0 HTML specification is enrolled as `SRC-XLIFF-003` at
  SHA-256
  `4b19c8d7c878c34b5422310f340abf099dedccf968c0a3c145548d3a691da7c2`.
- The tracked member inventory at
  `reports/ff6/xliff-authority-member-inventory.yaml` binds all 15 members of
  the 2.0 package and all 27 members of the 2.1 package.
- Global authority audit is 17/17 `MATCH`; XLIFF is 5/5 `MATCH`; a clean
  offline XLIFF reconstruction from the content-addressed cache is 5/5
  `MATCH`.
- The capability projection remains 110 capabilities and 672 obligations.
  No XLIFF profile gap, capability, obligation, product implementation,
  certification, promotion, release, or gate is closed by this checkpoint.

Resume at `XLF-03`. Recompute `XLF-01` or `XLF-02` only if event-20 input
digests or authority bytes were invalidated.

## Current implementation checkpoint — event 21

XLF-03 is still the first unmet task step. Event 21 binds an
integration-safe `GREEN_VERIFIED_CHECKPOINTED` microstep at source commit
`a1316b4fae21c20c71ccb6d60e4b9fe634dca573`.

Completed inside XLF-03:

- the previously registered but missing
  `tools/spec/extract_sal_facts.py` implementation path now exists;
- pinned archive SHA-256, ZIP path/duplicate/size/compression limits, XML
  entity rejection, and fail-closed parsing are implemented;
- XLIFF 2.0 and 2.1 Core/module structural inventories are compiled from
  exact authority members;
- XLIFF 2.0 Change Tracking is classified as a normative module while XLIFF
  2.1 Change Tracking is classified as informative;
- XLIFF 2.1 ITS owns both `its` and `itsm`;
- DocBook section delta, curated source-row validation, canonical YAML bytes,
  atomic write, and drift check primitives are implemented;
- 3 focused tests, Ruff, strict Mypy, and bytecode compilation pass;
- Pyright was unavailable in the checkpoint shell and is not claimed.

Exact committed digests:

- source:
  `16466e1e7778259cd284fcf89af61ca902c1b2aac609ccf6b6ebce388590388c`;
- tests:
  `93a4e5ce49cc8e2dcd2a513d6a6e598fd966849cfe63a58b7e84d2fcd4fc0c84`;
- ingest transcript:
  `d1e283235efc0ee3af5a36a7257e6bf0ed93162ea7bc394c9eab5a4331f819ef`.

Still required before XLF-03 can pass:

1. add `test_cli_writes_and_checks_default_xliff_matrix` as the next RED test;
2. add default curated Core/module/validation requirement seeds and the
   deterministic CLI/check-mode contract;
3. add digest, duplicate/path, entity, missing-member, malformed-row, duplicate
   ID, and preview-contamination negative controls;
4. generate the real matrix from both pinned packages, prove three identical
   outputs, and validate exact 293/420 section and 8/8 module inventories;
5. write the final XLF-03 receipt and only then mark XLF-03 complete.

Do not reinterpret the existence of the compiler or its three tests as a
completed normative matrix, SAL repair, capability repair, product
implementation, or certification.

## Current execution checkpoint — event 22

Event 22 supersedes the event-21 resume instruction. `XLF-03` is complete at
the source-surface boundary; `XLF-04` is the first unmet step. The task remains
`WORK_IN_PROGRESS`, the parent remains `NEEDS_REPAIR`, and product source,
architecture, certification, promotion, release, and gates remain locked.

Immutable implementation commit:
`6622aa1fef947530128b5b49de67afba3cc10088`.

Completed and verified in XLF-03:

- the registered extractor now has a deterministic command-line/check-mode
  contract and 36 unique default source-surface anchors;
- the real pinned XLIFF 2.0 and 2.1 packages compile to
  `reports/ff6/xliff-normative-delta-matrix.yaml` at SHA-256
  `9f4ea4b8b71378217af26c0fb2b97a759817a0aca6c64255b8cd55170c60a090`;
- the matrix accounts for 293/420 DocBook sections, 8/8 normative modules,
  and 8/9 module schema vocabularies for XLIFF 2.0/2.1 respectively;
- XLIFF 2.2 is `AUTHORITY_ABSENT_NOT_COMPILED`; XLIFF 1.2 is
  `EXCLUDED_SEPARATE_COMPATIBILITY_MODEL`;
- digest, duplicate/casefold/path, decompression, document-type/entity,
  missing-member, malformed-row, duplicate-ID, owner, and preview leakage
  controls fail closed;
- three clean real-authority generations are byte-identical at the matrix
  digest above;
- 18 focused tests, Ruff, strict Mypy, Pyright 1.1.411, and bytecode
  compilation pass;
- both final XLF-03 skill transcripts validate with zero warnings.

Exact committed digests:

- source:
  `f7e59ae41ac3e0a82c8e0b2523711e3f7569c33b0cfa58d32f2ef9ee14096dbb`;
- tests:
  `4a9e5f6aa1cf68a80dcd4c93f135b80c84ff18ff0bbccc5d81e87677ddae2e58`;
- matrix:
  `9f4ea4b8b71378217af26c0fb2b97a759817a0aca6c64255b8cd55170c60a090`;
- TDD transcript:
  `ff3c01917056f02a85cb552e0f6459b1c4f5531f33e8fd0c8d083645e44079df`;
- ingestion transcript:
  `18497bd7b49eb50f20b9476610754b62935aa8cf993a2b85a82aefd2232a7859`.

Truth boundary: the 36 rows are intentionally coarse source-surface anchors.
They establish authority, profile, Core/module, schema, and validation
ownership for the next extraction steps. They are not the complete
fine-grained Core or module semantic obligation inventory and cannot satisfy
XLF-04, XLF-05, SAL closure, capability closure, product implementation, or
certification.

## Current XLF-04 microstep checkpoint — event 23

Event 23 supersedes the event-22 resume paragraph. `XLF-04-BATCH-001` is
integration-safe at implementation commit
`4f0e8793d7aa694ccb45a57e9d3abc8f8cce92f7`, but XLF-04 remains the first
unmet task step and the task remains `WORK_IN_PROGRESS`.

The bounded batch adds:

- a separate fine-grained Core obligation compiler and deterministic
  `--artifact core-obligations` command;
- seven stable source-bound IDs covering document structure, hierarchy
  cardinality, spanning inline semantics, segmentation, state, extension
  preservation, and agent processing;
- exact authority package, member, section, paragraph, anchor, and normalized
  paragraph digests for both stable profiles;
- mandatory positive and rejection evidence declarations;
- seed-schema rejection of self-declared verification;
- safe DocBook public/internal entity handling through the existing bounded
  parser path;
- an explicit completeness rule: category presence cannot close XLF-04.

Tracked evidence:

- `reports/ff6/xliff-core-obligation-inventory.yaml` — seven obligations,
  SHA-256
  `d9c3fc4b9dd7002cc86ef0852864fb03acdc3be5fa4aead05efc15d39dfd11ff`;
- source SHA-256
  `e44a70d39d0415190854a3dc048da8f7927d3ce6fb22cbe93875121c648df685`;
- test SHA-256
  `627949766f2a5acffb8c0c1176cb03438a8c1fd9126cc51524870ed61be8fb43`;
- 23 focused tests, Ruff, strict Mypy, Pyright 1.1.411, and bytecode
  compilation pass;
- three real-authority generations are byte-identical at the inventory digest;
- the XLF-03 matrix remains unchanged at
  `9f4ea4b8b71378217af26c0fb2b97a759817a0aca6c64255b8cd55170c60a090`;
- both batch receipts validate with zero warnings; XLIFF authority remains
  5/5 `MATCH`.

Truth boundary: the inventory is `SOURCE_LOCATED_PARTIAL` and every obligation
is `SOURCE_BOUND_UNVERIFIED`. Five top-level categories remain absent:
identifiers/references/inheritance, language/direction/whitespace,
source-target correspondence, XML security/resource limits, and semantic
roundtrip/canonical output. Even after those categories have rows, XLF-04
cannot become complete until an explicit expected-obligation ID denominator
exists and every expected ID resolves. Canonical SAL reconciliation,
capability repair, product source, certification, and promotion remain
untouched.

Resume at `XLF-04-BATCH-002`. Revalidate event 23, implementation commit,
23 tests, both report digests, three-run replay, receipts, and authority audit.
Then add the next RED test for source-located identifier/reference/inheritance,
language/direction/whitespace, and source-target correspondence rules. Preserve
the seven batch-001 IDs and do not treat category coverage as completeness.

## Current XLF-04 microstep checkpoint — event 24

Event 24 supersedes the event-23 resume paragraph. `XLF-04-BATCH-002` is
integration-safe at implementation commit
`78660ae1a310ab06cf00d977bbc26fb65914f1c9`, but XLF-04 remains the first
unmet task step and the task remains `WORK_IN_PROGRESS`.

The cumulative inventory now contains 19 stable, source-bound obligations.
Batch 002 adds 12 obligations for:

- file-ID uniqueness, same-unit `dataRef` resolution, relative-fragment
  inheritance, and inherited `translate`;
- source/target language defaults, source/target direction inheritance, and
  `xml:space` inheritance;
- segment source/optional-target cardinality, target-language correspondence,
  and implicit target order.

Every row records `introduced_in_batch`. The compiler rejects a row introduced
after the requested batch, preventing a later inventory from being
misrepresented as an earlier checkpoint. The generated artifact identity is
also derived from the requested batch.

Tracked evidence:

- implementation commit:
  `78660ae1a310ab06cf00d977bbc26fb65914f1c9`;
- Core inventory SHA-256:
  `5930f1e28d21e277325c9a88ad8486ce9076ff1aa680ae21979440fd85d3244b`;
- source SHA-256:
  `ac44f43456f5c1ac02f9c157ae6bb653be6f9eacbdd2eca55e40e8447f74b5ce`;
- test SHA-256:
  `5f0554a03eb3ac9f220e8f4a5b3ee58d4764b488a78db661dc649b8a55ee2070`;
- 24 focused tests, Ruff, strict Mypy, Pyright 1.1.411, and bytecode
  compilation pass;
- three real-authority generations are byte-identical at the inventory digest;
- the XLF-03 matrix remains unchanged at
  `9f4ea4b8b71378217af26c0fb2b97a759817a0aca6c64255b8cd55170c60a090`;
- both batch-002 receipts validate with zero warnings; XLIFF authority remains
  5/5 `MATCH`.

Truth boundary: the inventory remains `SOURCE_LOCATED_PARTIAL`; every row
remains `SOURCE_BOUND_UNVERIFIED`. The two uncovered top-level categories are
semantic roundtrip/canonical output and XML security/resource limits. Covering
them still cannot close XLF-04 without an explicit expected Core obligation-ID
denominator and resolution of every expected ID. Canonical SAL reconciliation,
capability repair, product source, certification, promotion, and release remain
untouched. Portfolio certification is still 0/6.

Resume at `XLF-04-BATCH-003`. Revalidate event 24, the immutable implementation
commit, 24 tests, both report digests, three-run replay, zero-warning receipts,
and authority audit. Then add RED tests for the two remaining categories and a
separate fail-closed denominator contract. Preserve all 19 existing IDs and
retain `complete: false` until every expected Core obligation ID resolves.

## Current XLF-04 microstep checkpoint — event 25

Event 25 supersedes the event-24 resume paragraph.
`XLF-04-BATCH-003` is integration-safe at implementation commit
`2522752776f64ab800a2a21c8fa46c1f2a4e361c`, which is present on GitLab
`origin/main`. XLF-04 remains the first unmet task step and the task remains
`WORK_IN_PROGRESS`.

Batch 003 adds six obligations while preserving the prior 19 IDs:

- two XLIFF-specification obligations for structural roundtrip and unsafe URI
  risk;
- four separately classified Format Factory production-policy obligations for
  semantic roundtrip, deterministic writing, external-resolution policy, and
  resource limits;
- explicit `obligation_basis` and `conformance_effect` fields so production
  hardening cannot be misreported as OASIS conformance;
- a tracked, direct-input denominator containing 105 expected obligation IDs;
- fail-closed validation of the denominator's authority input closure;
- an explicit open-census boundary rather than a percentage or category-count
  completion claim.

Tracked evidence:

- source SHA-256:
  `a5c67f56378e586bf46ddb8c39881ab9ea81e42e76539bac942c5220c45f0190`;
- test SHA-256:
  `bf7fa725496979e3f5a50125319f9974c6205803c8358adbfb0ba8677c52bc32`;
- Core inventory SHA-256:
  `ae4d00af06fffc1eaf7741cd131d8ed7e7fc8a89b2a195acf4f649b5f44b6bbb`;
- Core denominator SHA-256:
  `c1a326e42bd1b47ec792088258f81fc4eac0b02543c57beedb48242181d008da`;
- XLF-03 matrix unchanged at
  `9f4ea4b8b71378217af26c0fb2b97a759817a0aca6c64255b8cd55170c60a090`;
- 27 focused tests, 94 format-contract tests with the one baseline-known
  stateful CSV case deselected, and 69 production-program tests pass;
- Ruff, strict Mypy, Pyright 1.1.411, and bytecode compilation pass;
- all three generated artifacts pass check mode, both batch-003 receipts
  validate without warnings, and XLIFF authority remains 5/5 `MATCH`;
- three denominator and three inventory runs were recorded byte-identical by
  the batch receipts.

Truth boundary: 25 of 105 explicit expected IDs are resolved and 80 remain.
All 12 top-level categories have at least one row, but every category remains
incomplete and the denominator is `OPEN_AUTHORITY_CENSUS`. The 105-ID set is
itself not yet proven exhaustive because the complete Core normative prose,
XSD, Schematron, and 2.0/2.1 delta surfaces have not been dispositioned.
Every row remains `SOURCE_BOUND_UNVERIFIED`. Canonical SAL reconciliation,
module obligations, capability repair, product source, certification,
promotion, release, and gate state remain unchanged. Portfolio certification
is still 0/6.

Resume at `XLF-04-BATCH-004`. Revalidate event 25, commit `25227527`, the exact
digests above, 27 tests, affected regressions, static checks, artifact check
mode, deterministic receipts, and authority audit. Then compile a deterministic
Core authority-candidate census covering direct/leaf normative prose, Core XSD
element/type/attribute/cardinality/order constraints, Core Schematron
assertions, and exact XLIFF 2.0/2.1 deltas. Map each candidate exactly once to
one or more expected obligation IDs or to an explicit non-obligation
disposition with reason. Reject unmapped candidates, duplicate mappings, stale
authority digests, ancestor/leaf double counting, and profile leakage. Retain
`complete: false` until the authority census is exhaustive and every expected
ID resolves.

## Current XLF-04 microstep checkpoint — event 26

Event 26 supersedes the event-25 resume paragraph.
`XLF-04-BATCH-004` is integration-safe at implementation commit
`1fef79b9d6c1ee1f6667e0c5c70435562c97544c`, which is present on GitLab
`origin/main`. XLF-04 remains the first unmet task step and the task remains
`WORK_IN_PROGRESS`.

Batch 004 adds a separate, deterministic authority-candidate census and
fail-closed validator:

- 542 grouped candidates: 182 selected Core prose candidates, 264 Core XSD
  component/constraint candidates, and 96 Core Schematron assertions/reports;
- exact stable-profile relations: 411 common-identical, 19 common-changed,
  four removed in 2.1, and 108 added in 2.1;
- exact authority source, package, member, semantic location, normalized
  requirement, and digest bindings for every occurrence;
- zero unmapped and zero multiply dispositioned selected candidates;
- independent rejection of missing disposition, duplicate obligation mapping,
  multiply dispositioned input, and preview-profile leakage;
- a regression control preventing short inline names such as `sc` and `em`
  from matching substrings such as `schema`;
- explicit disposition precision: 464 lexical/context plus structural
  mappings and 78 coarse structural fallbacks;
- an exact candidate-selector definition and explicit scope limitations;
- deterministic CLI/check mode and three byte-identical real-authority
  generations.

Tracked evidence:

- source SHA-256:
  `138385387e78e567782df467829a468707b4edaeb32e458d7092c11f0f0270fa`;
- test SHA-256:
  `f0dc5db56d19f9669d9875e7f11303c87d2a4ee49a2d0619710ccb45b21eef72`;
- census SHA-256:
  `7227f43bb8d5ad93d0770df60f061d24cdd0ac5f521bd2ae5af2a6712407c69a`;
- 34 focused tests, 94 format-contract tests with the one baseline-known
  stateful CSV case deselected, and 69 production-program tests pass;
- Ruff, strict Mypy, Pyright 1.1.411, and bytecode compilation pass;
- matrix, denominator, Core inventory, and candidate census check modes pass;
- all three batch-004 skill transcripts validate with zero warnings;
- XLIFF authority remains 5/5 `MATCH`.

Truth boundary: `candidate_scope_complete: true` applies only to the declared
selector: direct/leaf prose carrying an RFC-style modal, every configured Core
XSD semantic node, and every Core Schematron assert/report. Non-modal
declarative prose is explicitly not classified yet. Seventy-eight dispositions
remain coarse and every disposition remains
`SOURCE_LOCATED_RULE_DISPOSITION_UNVERIFIED`. Candidate routing touches 45 of
the 105 expected IDs and leaves 60 without a selected authority candidate, but
this is not obligation resolution: the cumulative obligation inventory still
contains 25 source-bound rows, leaving 80 expected obligation IDs missing.
The denominator remains `OPEN_AUTHORITY_CENSUS`; XLF-04 is not complete.
Canonical SAL reconciliation, module obligations, capability repair, product
source, certification, promotion, release, and gate state remain unchanged.
Portfolio certification is still 0/6.

Resume at `XLF-04-BATCH-005`. Revalidate event 26, implementation commit
`1fef79b9`, the exact digests and counts above, the three real-authority
replays, zero-warning receipts, and authority audit. Then:

1. census and classify every non-modal Core prose paragraph excluded by batch
   004;
2. replace each of the 78 coarse structural fallbacks with an exact semantic
   mapping or an explicit, reasoned non-obligation disposition;
3. expand the expected-ID denominator where the newly classified authority
   surface exposes a real missing normative behavior;
4. compile source-bound obligation rows for remaining expected IDs without
   altering the 25 existing stable IDs;
5. retain `complete: false` until the authority surface is exhaustive, every
   expected ID has a source-bound obligation, and canonical SAL verification
   succeeds.

## Current XLF-04 microstep checkpoint — event 29

Event 29 supersedes the event-26 resume paragraph. The first bounded part of
`XLF-04-BATCH-005` is integration-safe at GitLab implementation commit
`315efa5f5f4420202b5254c86ccd8863a91c385f`, but it is not a completed batch.
The task remains `WORK_IN_PROGRESS`; `XLF-04` remains the first unmet task
step; portfolio certification remains 0/6.

What this checkpoint proves:

- the deterministic Core census now covers 1,130 candidates:
  182 modal normative-prose candidates, 588 non-modal prose candidates,
  264 Core XSD candidates, and 96 Core Schematron candidates;
- every candidate carries content-bound occurrence and member digests;
- a full validator replay against the pinned XLIFF 2.0 and 2.1 authority
  packages rejects internally rehashed but authority-forged content;
- generated dispositions are recomputed from candidate content and cannot be
  forged by editing mapping IDs, labels, precision, or rationale;
- all generated precision labels honestly end in `_UNVERIFIED`; no
  implementation-derived mapping is called exact or independently proven;
- three clean processes generated the identical LF-canonical census SHA-256
  `24c1902b6387cc9fa3402f78392ba91c6e6656407719ec11cfaab1c4f3d22b9e`;
- 64 focused tests pass, including negative controls for forged dispositions
  and rehashed forged authority content;
- Ruff, strict Mypy, Pyright 1.1.411, bytecode compilation, 94 affected
  format-contract tests with one baseline-known stateful CSV test deselected,
  69 production-program tests, all three batch-005 skill transcripts, and the
  five-record XLIFF authority audit pass.

What this checkpoint does not prove:

- zero of the 1,130 generated dispositions has independent SAL verification;
- 60 of the 105 expected obligation IDs still have no candidate mapping;
- only 25 expected IDs have source-bound obligation inventory rows, so 80
  source-bound rows remain missing;
- the expected-ID denominator is still `OPEN_AUTHORITY_CENSUS`;
- the 588 non-modal candidates have a deterministic disposition, not a
  verified semantic classification;
- no XLIFF module obligation family, ProductContract, product source,
  certification, promotion, release, or gate changed.

Resume at
`XLF-04-BATCH-005-PARTIAL-002_DISPOSITION_VERIFICATION_AND_OBLIGATION_COMPILATION`:

1. Revalidate event 29, GitLab commit `315efa5f`, the report digest and counts,
   64 focused tests, all four existing artifact check modes, three batch-005
   receipts, three clean census generations, and all five XLIFF authority
   matches.
2. Independently verify candidate dispositions through canonical SAL in
   deterministic, source-located batches. A generated mapping cannot verify
   itself.
3. When an independent reading contradicts a generated disposition, add a
   discriminating negative test and repair the mapping rule; never choose the
   result that merely reduces the open count.
4. Expand the 105-ID denominator when the authority exposes a normative
   behavior that it does not contain.
5. Compile source-bound obligation rows for the 80 missing expected IDs while
   preserving the 25 existing stable IDs and provenance.
6. Investigate the 60 expected IDs with no candidate mapping. Bind them to
   exact authority occurrences, identify them as production policy where
   appropriate, or repair the denominator. Do not silently delete them.
7. Keep `complete: false` until all 1,130 candidate dispositions are
   independently verified, every expected ID resolves to a verified
   source-bound obligation, and canonical SAL reconciliation succeeds.

If the XLIFF exact paths are live-owned when a future provider starts, the
only allowed fallback is the already-journaled UBL lane at
`UBL-03`: exact import/include closure and reference resolution from commit
`f98d220a`. That fallback must not mutate XLIFF paths or claim UBL-03 complete.

## Current XLF-04 microstep checkpoint — event 30

Native `FF6-EVENT-000030` supersedes the event-29 resume instructions.
Partial-002-A is
integration-safe on GitLab `main` at implementation commit
`e13e103de0bb789ff51a8e931af0fb649474be20`. It proves exactly one independent
candidate adjudication and one additional source-bound obligation row:

- `1/1,130` candidate dispositions independently verified;
- `26/105` expected Core obligations source-bound;
- `1,129` dispositions and `79` expected rows remain open;
- XLF-04 and XLF-04-BATCH-005 remain incomplete;
- product source, certification, promotion, release, and gate state remain
  unchanged.

The exact next microstep is `XLF-04-BATCH-005-PARTIAL-002-B` for
`XLF-CAND-CORE-SCHEMATRON-00C4A041AF12C8A1`, content digest
`0a37761215603eb4db3f9602f6e979869b4f1f44c124c1f5ca2183cba1d7578a`.
The authority is XLIFF 2.1 Core Schematron
`schemas/xliff_core_2.1.sch`, rule 47/assert 2. It states that
`subFlowsStart` and `subFlowsEnd` on `pc` must occur as a pair.

Execute the next microstep as a new RED-GREEN-refactor cycle:

1. Replay Event 30 and both committed artifact check modes from GitLab `main`.
2. Add a failing decision test before extending the adjudication artifact.
3. Independently decide whether the assertion directly owns an inline `pc`
   pairing obligation. Do not accept the generated generic-validator,
   `segment`, or `ignorable` mappings merely because those tokens occur in the
   rule context.
4. Bind accepted and rejected mappings to the exact candidate, occurrence,
   member, denominator, SAL store, SAL manifest, SAL receipt, and adjudicator
   digests.
5. Add negative controls proving that incidental ancestor names do not create
   hierarchy obligations and that one-sided subflow attributes are rejected.
6. Regenerate the adjudication projection and obligation inventory. Preserve
   all 26 current stable rows and IDs.
7. Run focused tests, all dependency-drift controls, static checks, affected
   regressions, authority audit, SAL verification, three clean deterministic
   generations, and installed proof only when product source is eventually
   in scope.
8. Commit the bounded implementation first, replay from that immutable commit,
   then append the next native event and rebuild provider-neutral handover
   projections.

No future executor may promote this task from counts alone. Completion still
requires every mandatory Core and module obligation, independent evidence,
and the downstream product/certification gates.

## Semantic contradiction checkpoint — event 31

Native `FF6-EVENT-000031` supersedes the Event 30 execution instructions
without closing Partial-002-B. Commit
`d99fc6bf3679cd39396afbf5621847e3009ddf31` is preserved on GitLab `main` as
an auditable, mechanically green implementation attempt, not as an accepted
contract increment.

The attempt passed its own focused and regression checks and generated:

- two decision records and a deterministic adjudication digest
  `3d9c81773ceaddaae97a55fc804bd35efaf6501fe24c9fae8bf941fe338ceb01`;
- 27 mechanically source-bound rows and 78 mechanically missing rows at
  inventory digest
  `d5f77d95c703f62766e4ef4178ee3d811147df06844f0eacdec372bbd51cb351`;
- 62 affected tool tests, 94 format-contract tests with the exact
  baseline-known stateful CSV test deselected, 69 production-program tests,
  strict static checks, three-run generation, canonical SAL verification, and
  five matching XLIFF authority records.

Those results do not satisfy the hardened semantic acceptance contract:

1. The decision accepts `SAL-XLIFF-CORE-INLINE-PC-001`, but the direct
   semantic owner of mutual subflow presence is the existing denominator ID
   `SAL-XLIFF-CORE-INLINE-PAIRING-001`.
2. Only candidate `XLF-CAND-CORE-SCHEMATRON-00C4A041AF12C8A1` has a decision.
   Reciprocal candidate `XLF-CAND-CORE-SCHEMATRON-4BE479DD3F5875EF` remains
   unverified, so a bidirectional obligation cannot be compiled.
3. The generated row claims both stable profiles even though the exact
   mutual-presence assertions were located only in the pinned XLIFF 2.1
   Schematron. No separate XLIFF 2.0 normative rule was proven.
4. The adjudicator currently requires accepted and rejected IDs to equal the
   generated proposal set. That makes it impossible for an independent review
   to repair a valid denominator owner omitted by generation.
5. `SAL-XLIFF-00005` does not yet bind both reciprocal Schematron occurrences
   as exact, separate assertions.
6. The in-flight implementation manifest did not include the
   provider-neutral plan digest. The concurrently hardened execution contract
   therefore did not automatically invalidate the older active plan.

Production acceptance remains at the Event 30 boundary:

- `1/1,130` candidate dispositions accepted;
- `26/105` obligation rows accepted;
- `1,129` dispositions and `79` rows remain open;
- XLF-04, product source, certification, promotion, release, and every gate
  remain incomplete.

Resume exactly at `XLF-04-BATCH-005-PARTIAL-002-B-REPAIR-001`:

1. Start from GitLab commit `d99fc6bf` and validate Event 31 plus
   `plans/codex/handover/NEXT-MICROSTEP.yaml` at SHA-256
   `5fe34f5a0b5f269123c094cad4ecf88acf581fe8703fef5c084973aba555137f`.
2. Add RED controls permitting an independently accepted current denominator
   ID that the generator omitted, while still requiring every generated
   proposal to be accepted or explicitly rejected.
3. Repair the adjudicator and expose unproposed accepted IDs explicitly in the
   normalized projection.
4. Add exact SAL assertions for both reciprocal Schematron occurrences and
   regenerate the canonical SAL receipt through registered SAL skills.
5. Create one independently reasoned decision per reciprocal candidate.
   Reject generic validator and incidental hierarchy mappings. Accept only
   `SAL-XLIFF-CORE-INLINE-PAIRING-001`.
6. Require both decisions before compiling at most one pairing obligation.
   A one-sided decision must fail closed.
7. Narrow the pairing obligation to `xliff_2.1` unless a separately pinned
   XLIFF 2.0 normative rule is located and proven. Attribute presence in the
   2.0 XSD is not mutual-presence authority.
8. Preserve all 26 Event 30 accepted rows and all 1,130 candidate identities.
   Replace or quarantine the rejected 27th row; do not count it as closure.
9. Rerun all candidate, occurrence, member, denominator, decision, SAL, tool,
   profile, and reciprocal-proof drift controls; then run deterministic,
   static, authority, SAL, format-contract, and production-program gates.
10. Bind every future implementation manifest to the exact active
    provider-neutral plan digest so a concurrent contract change invalidates
    the in-flight run before commit.

Do not advance to another candidate and do not report 27 accepted obligations
or two accepted dispositions until every item above passes.

## Required execution

### XLF-01 — Revalidate the clean predecessor

1. Start from the fetched GitLab `origin/main` checkpoint containing
   `FF6-EVENT-000019`.
2. Verify event-chain integrity, controller/task/index agreement, the current
   capability aggregate, and all 15 predecessor authority matches.
3. Register a fresh provider identity, claim exact paths, and use registered
   skills with mutation guards and write receipts.
4. Confirm no product, certification, promotion, gate, GitHub, or branch
   mutation is in scope.

### XLF-02 — Close the authority prerequisite

1. Acquire and hash-pin the official XLIFF 2.0 OASIS Standard release package
   through `research-format-contract-sources` and its canonical authority
   materializer; do not use the current 2.1 prose as a proxy for 2.0. There is
   no registered `acquire-format-authority` skill, so an executor must not
   invent or bypass the registered acquisition path.
2. Inventory every relevant member of the pinned 2.0 and 2.1 packages:
   normative prose, Core XSD, module XSDs, Schematron or other normative
   validation artifacts, catalog/import files, examples, and notices.
3. Record legal and redistribution status and keep external bytes in the
   content-addressed local authority store.
4. Add a lock record only after independently recomputing the byte digest and
   proving clean offline reconstruction.
5. Treat unavailable or contradictory artifacts as named per-profile gaps;
   never infer normative behavior from implementation convenience.

### XLF-03 — Build the normative delta and module matrix

Produce a source-located matrix that distinguishes:

1. XLIFF 2.0 Core requirements.
2. XLIFF 2.1 Core additions and changed processing requirements.
3. Every official 2.1 module:
   - Translation Candidates / Matches;
   - Glossary;
   - Format Style;
   - Metadata;
   - Resource Data;
   - Size and Length Restriction;
   - Validation;
   - ITS.
4. The nine module schema vocabularies shipped by the pinned 2.1 bundle:
   `matches`, `glossary`, `fs`, `metadata`, `resource_data`,
   `size_restriction`, `validation`, `its`, and `itsm`. ITS is one official
   module with two schema vocabularies; vocabulary count must not be reported
   as module count.
5. ITS mappings and any normative constraints defined outside a module XSD.
6. The informative Change Tracking extension as explicitly
   `INFORMATIVE_EXTENSION`, never as a ninth official module or stable
   conformance owner.
7. XLIFF 2.2 preview-only behavior, if an exact authority can be pinned.
8. Rules common to both stable versions versus rules introduced, tightened,
   relaxed, or removed in 2.1.

Every matrix row must contain an authority source ID, source digest, exact
member/section or schema location, normalized requirement, affected profile,
module/Core ownership, requirement class, confidence, and contradiction or
interpretation note.

### XLF-04 — Compile complete Core obligations

Audit and, through registered SAL skills, repair facts for at least:

- document root, version, source/target language, namespace, and file
  cardinality;
- files, groups, units, segments, ignorable content, notes, original data,
  skeleton references, and extension points;
- ordering, cardinality, identifiers, reference scope, inheritance, language,
  directionality, whitespace, state, and sub-state semantics;
- segmentation, re-segmentation, canResegment, translate, preserveSpace, and
  copyOf/dataRef/startRef constraints;
- inline `ph`, `pc`, `sc`, `ec`, `mrk`, `sm`, and `em` identity, pairing,
  nesting, isolation, ordering, and original-data resolution;
- source/target structural correspondence and target-presence rules;
- processing requirements for modifiers, writers, extractors, mergers, and
  validators;
- namespace-aware preservation and loss reporting for foreign extensions;
- XML parsing security, external-resource policy, and resource limits;
- semantic roundtrip and canonical deterministic XML output.

Do not flatten inline codes into text or collapse processing requirements into
schema-validity claims.

### XLF-05 — Compile each module as a first-class capability family

Replace the single broad `XLIFF-MODULE-001` bucket with separately owned
capabilities where module requirements, models, validation, or profile
applicability differ. For every module:

1. Inventory all elements, attributes, types, references, cardinalities,
   ordering constraints, processing requirements, and cross-Core edges.
2. Define typed model, parser, writer, validation, preservation, diagnostics,
   positive, negative, property, roundtrip, interoperability, security, and
   resource-limit obligations.
3. Assign exact stable profile applicability.
4. Preserve unknown module or extension content only where the standard
   permits it; preservation is not semantic support.
5. Require a machine-readable module coverage declaration. `modeled`,
   `preservation_only`, `preview`, and `unsupported` are distinct and cannot
   satisfy one another.

### XLF-06 — Repair the product-requirement and family layers

1. Split any research/product requirement that mixes 2.0, 2.1, module, or 2.2
   preview semantics.
2. Reconcile the XML-localization family pack using
   `fact_ownership: explicit_complete` only after every live XLIFF fact has
   exactly one owner.
3. Preserve existing strong requirements for typed hierarchy, lossless inline
   token editing, segment mapping, full validation matrices, and explicit
   downgrade-loss reporting.
4. Split broad capabilities when their normative rules have different
   profiles or proof strategies. Do not use keyword duplication to create
   apparent depth.
5. Keep optional ecosystem adapters separate from stable Core/module
   conformance.

### XLF-07 — Compile exact stable and preview profiles

1. Every stable capability and obligation must declare a non-empty subset of
   `xliff_2.0` and `xliff_2.1`.
2. A 2.1-only module or rule must not claim 2.0.
3. Common Core rules may claim both versions only when both pinned authorities
   prove them.
4. XLIFF 2.2 records, if authority-ready, must be
   `PREVIEW_ISOLATED`, use preview-only public/proof namespaces, and own no
   stable obligation.
5. XLIFF 1.2 must remain an explicit future compatibility model, not an alias
   or tolerant mode of the XLIFF 2.x model.
6. Reject duplicate, unassigned, foreign, ambiguous, and dangling fact,
   profile, module, capability, or obligation edges.

### XLF-08 — Verify and checkpoint

1. Verify every XLIFF SAL fact against exact pinned authority bytes.
2. Compile the ProductContract and six-format universe in check mode and prove
   at least three byte-identical clean runs.
3. Prove the exact profile/module denominator, zero missing stable profiles,
   zero known XLIFF surface gaps, zero empty-profile obligations, and exact
   single ownership.
4. Retain live matches for every authority record after the 2.0 lock addition.
5. Run focused and affected regression tests, Ruff, Pyright 1.1.411, and
   strict Mypy on the touched typed machinery; state exact boundaries and
   baseline-known failures.
6. Run negative controls proving malformed IDs, missing module ownership,
   cross-profile contamination, and preview-to-stable leakage fail closed.
7. Append the next native FF6 event before derived projections, update the
   controller/current gaps/task index, refresh the provider-neutral handover,
   commit explicit files, push to GitLab `main`, and verify the remote.
8. Select `TC-FF6-UBL-TYPING-001` as the exact successor unless fresh
   higher-severity evidence creates a deterministic prerequisite task.

## Acceptance criteria

- Official XLIFF 2.0 and 2.1 authority packages are hash-pinned, legally
  classified, independently digest-verified, and clean-offline reconstructible.
- The delta matrix locates every claimed requirement in exact authority bytes.
- XLIFF 2.0 and 2.1 stable profiles are both fully claimed without assigning
  2.1-only rules or modules to 2.0.
- Core and all eight official XLIFF 2.1 modules have explicit,
  non-overlapping production capability owners and complete normative
  obligation inventories. The bundle's nine module schema vocabularies are
  all accounted for, with `its` and `itsm` assigned to the single ITS module.
- The informative Change Tracking extension is inventoried and classified but
  does not satisfy, own, or inflate normative module coverage.
- Inline pairing, ordering, segmentation, state, original-data, extension,
  skeleton, ITS, and processing requirements are modeled semantically rather
  than reduced to XSD validation.
- XLIFF 2.2 is absent or isolated preview-only; XLIFF 1.2 remains outside the
  stable 2.x model.
- Every mandatory fact and obligation has one canonical owner and an exact
  non-empty profile subset; referential-integrity errors fail closed.
- Three identical strict six-format compilations, complete authority matches,
  focused/affected tests, Ruff, Pyright, and bounded strict Mypy pass.
- No source-file presence, product test, synthetic fixture, or current
  implementation behavior is treated as contract completion evidence.
- No product source, certification, promotion, release, or gate state changes.

## Required checkpoint evidence

- XLIFF 2.0/2.1/2.2 authority and profile delta matrix.
- Core and per-module element/attribute/type/processing-requirement coverage.
- SAL exact-verification receipt and explicit ownership report.
- ProductContract and capability-universe digests plus three-run digest.
- Authority-lock audit and offline reconstruction receipt.
- Negative-control results and focused/affected test/static-analysis results.
- Skill transcripts for every mutation pipeline.
- Native FF6 event hash, controller projection, exact successor, commit hashes,
  GitLab remote verification, and refreshed handover manifest.

## Truth boundary

Passing this task proves the normative contract and deterministic work
denominator, not that an XLIFF library is implemented or production-ready.
Product implementation remains locked behind closure of the parent capability
universe and its successor architecture task.
