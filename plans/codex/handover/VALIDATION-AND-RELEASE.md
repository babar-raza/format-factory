---
artifact_id: FF6-VALIDATION-RELEASE-HANDOVER-001
artifact_type: verification_and_release_contract
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-30
authoritative_state: false
historical_projection: true
---

> **Historical design reference.** Event/status overlays below are retained for
> audit only. Use generated [START-HERE.md](START-HERE.md) and
> [checkpoint.yaml](checkpoint.yaml) for the current controller head and task.

# Validation, Regression, and Release Contract

> **Current authority overlay: Event 40.** Native head
> `FF6-EVENT-000040`; current checkpoint facts and
> commands are in [START-HERE.md](START-HERE.md),
> [CURRENT-MACHINE-STATE.yaml](CURRENT-MACHINE-STATE.yaml), and
> [NEXT-MICROSTEP.yaml](NEXT-MICROSTEP.yaml). The accepted boundary is
> 31/105 obligations and 9/1,130 dispositions after semantic commit `d95af5ae`
> with historical repair `809cc18c` and
> controller acceptance `de569544`; UBL separately retains 6,001 local
> particle nodes.
> No release state is implied here. Event 31 remains historical
> negative-control evidence, not current routing.

The pre-repair state of commit `2dcb161e` is an additional mandatory negative
control: shared-worktree success is insufficient when a clean Windows checkout
fails because raw proof hashes depend on line-ending conversion. The accepted
repair route is `XLF-04-BATCH-005-PARTIAL-002-D-REPLAY-REPAIR-001`; see
[CLEAN-REPLAY-REPAIR.md](CLEAN-REPLAY-REPAIR.md).

Event 31 is a mandatory machinery negative control: deterministic output,
passing tests, clean static analysis, and count growth did not override a
wrong semantic owner, missing reciprocal proof, or unsupported profile claim.
Future promotion logic must retain this discriminating failure.

## Completion semantics

A capability is complete only when public API, behavior, rejection,
preservation, errors, security, resource limits, scale, determinism, typing,
documentation, external interoperability, installed-wheel use, compatibility,
and full proof-input closure pass.

Planning records, files, symbols, test names, generated classes, and synthetic
fixtures are never sufficient evidence.

## Current evidence boundary

Events 16 through 22 prove:

- 17 of 17 locked authorities live-match;
- strict six-format ProductContract compilation;
- deterministic 110-capability/672-obligation planning projections;
- clean offline and clean online authority replay;
- three identical strict generation runs;
- authority-closure affected pytest `250 passed, 1 known baseline test
  deselected`;
- OpenRaster affected pytest `166 passed, 1 known baseline test deselected`;
- Event-18 affected pytest `126 passed, 1 known baseline test deselected`;
- Event-19 NRRD verification: 92 format-contract tests passed with 1
  baseline-known stateful CSV idempotency test deselected, 96 affected tests
  passed, and 119 authority dependency-closure tests passed;
- Ruff passed; strict mypy passed on the new family-pack validator; the legacy
  compiler graph is not claimed strict-clean; Pyright 1.1.411 passed on all
  three affected compiler modules;
- OpenRaster exact SAL verification `20/20`;
- IPYNB exact SAL verification `25/25`;
- NRRD exact SAL verification `25/25`, 18-domain/41-policy explicit-complete
  family ownership, and all five profiles claimed;
- native FF6 event chain passes through `FF6-EVENT-000031`;
- the official XLIFF 2.0 package and prose are independently pinned, legally
  classified, and reconstructed offline with all five XLIFF authorities
  matching;
- the 15-member XLIFF 2.0 and 27-member XLIFF 2.1 packages have a tracked,
  replay-checked exact member inventory;
- authority bootstrap focused tests `12 passed`, format-contract regression
  `94 passed, 1 baseline-known test deselected`, Ruff passed, Pyright 1.1.411
  passed, and bounded Mypy passed on the touched source modules.
- the historical event-24 batch-002 slice is bound to commit
  `78660ae1a310ab06cf00d977bbc26fb65914f1c9`, exact
  source/test/matrix/Core-inventory/receipt digests and zero-warning receipts;
- the extractor passes 24 focused tests, Ruff, strict Mypy, Pyright 1.1.411,
  and bytecode compilation;
- matrix check mode and three real-authority runs produce identical bytes at
  SHA-256
  `9f4ea4b8b71378217af26c0fb2b97a759817a0aca6c64255b8cd55170c60a090`;
- three Core-inventory runs produce identical bytes at SHA-256
  `5930f1e28d21e277325c9a88ad8486ce9076ff1aa680ae21979440fd85d3244b`;
- the 19 Core obligations are source-bound but unverified, two categories
  remain, and completeness is false because the expected-ID denominator is
  absent;
- the historical event-25 batch-003 slice is bound to commit `25227527`, 27
  focused tests, 25 cumulative source-bound obligations, and a 105-ID open
  denominator with 80 unresolved IDs;
- XLF-03 proves 36 coarse source-surface anchors, 293/420 sections, 8/8
  modules, and 8/9 schema vocabularies, but not complete fine-grained Core or
  module semantic obligations.
- GitLab implementation commit
  `2522752776f64ab800a2a21c8fa46c1f2a4e361c` adds batch 003 and is bound by
  event 25 and checkpoint commit `220ee7f5`;
- the handover refresh independently replayed 27 focused tests and validated
  both batch-003 transcripts;
- those transcripts report 94 format-contract tests with one baseline-known
  deselection, 69 production-program tests, Ruff, strict Mypy, Pyright 1.1.411,
  bytecode compilation, three identical outputs, and 5/5 XLIFF authority
  matches; the incoming provider must independently replay those broader
  claims before starting batch 004;
- batch 003 produces 25 source-bound obligations against a 105-ID open
  denominator, leaving 80 IDs unresolved. All 12 categories are represented,
  but the authority census and XLF-04 remain incomplete.
- Event 30 binds implementation commit
  `e13e103de0bb789ff51a8e931af0fb649474be20`, with 1,130
  source-authentic candidates: 182 normative prose, 588 non-modal prose, 264
  Core XSD, and 96 Core Schematron;
- all candidate content, occurrences, members, profiles, and authority inputs
  replay against pinned XLIFF 2.0/2.1 bytes;
- 64 focused tests, 94 affected format-contract tests with one named
  baseline-known deselection, 69 production-program tests, Ruff, strict
  Mypy, Pyright 1.1.411, bytecode compilation, 5/5 XLIFF authority matches,
  and three identical census generations pass;
- one of 1,130 semantic dispositions is independently verified; 1,129 remain
  open and 79 expected IDs lack source-bound rows;
- the current token router can over-map incidental XPath context names, so
  proposal replay is not accepted as independent semantic verification.
- the separate adjudication compiler rejects overmapped proposals and binds
  the accepted decision to candidate, occurrence, authority, denominator,
  canonical SAL, decision, tool, and dependency digests;
- the Event 30 inventory is reproducible at 26/105 source-bound rows, while
  XLF-04 remains explicitly incomplete.

It does not prove:

- implementation of any of the 672 obligations merely from contract proof;
- production readiness of any library;
- independent application interoperability;
- installed-wheel platform/dependency matrices;
- certification, extraction, or release readiness.

No product obligation is certified and all promotion states remain
`UNASSESSED`. Contract-source binding and candidate adjudication are
prerequisites, not product behavior proof.

## Completed OpenRaster contract-task gate

`TC-FF6-ORA-PROFILE-SURFACE-001` passed at event 17 with:

- source-located 0.0.3/0.0.4/0.0.5 profile deltas;
- valid SAL authority edges;
- explicit developer capabilities for full editable/viewing baseline,
  compositing/rendering, preservation, security, deterministic output, and
  application interoperability;
- exact profile applicability for every capability and obligation;
- no `FF6-ORA-SURFACE-001` or `FF6-ORA-PROFILE-001` finding;
- three identical strict runs with the then-current 15/15 authority set;
- affected contract, SAL, program, event, and static gates;
- no product source or promotion changes.

Because the specification is an early draft, later product certification is a
named interoperability certification, not universal conformance.

## Completed IPYNB contract-task gate

`TC-FF6-IPYNB-PROFILE-SURFACE-001` passed at event 18 with:

- source-located nbformat 4.0–4.5 deltas;
- exact fact/evidence edges and explicit uncertainty;
- profile-homogeneous capabilities, splitting mixed-version rules;
- every capability and obligation assigned a non-empty profile subset;
- all six target profiles claimed;
- no `FF6-IPYNB-PROFILE-001` finding;
- retained no-execution exclusion;
- three identical strict runs with the then-current 15/15 authority set;
- affected contract, SAL, capability, event and static gates;
- no product source, product test, certification, gate, or promotion change.

## Completed NRRD contract-task gate

`TC-FF6-NRRD-PROFILE-SURFACE-001` passed at event 19 with:

- source-located NRRD0001-NRRD0005 deltas from both pinned Teem authorities;
- exact fact/evidence edges, explicit uncertainty, and complete ownership;
- profile-homogeneous capabilities, splitting mixed-version rules;
- coverage of attached/detached payloads, types/endian/dimensions, spatial and
  axis metadata, all required encodings, data-file lists and patterns,
  streaming/mmap conditions, preservation, deterministic output and resource
  protections;
- every capability and obligation assigned a non-empty exact profile subset;
- all five target profiles claimed and no `FF6-NRRD-PROFILE-001` finding;
- three identical strict runs with the then-current 15/15 authority set;
- a governed source repair separating NRRD0004 coordinate transforms from
  NRRD0005 measurement-frame semantics;
- an explicit record that Teem's permissive later-field parsing under earlier
  magic is interoperability behavior, not strict conformance;
- no product source, product test, certification, gate, or promotion change.

## Current XLIFF contract-task gate

`TC-FF6-XLIFF-PROFILE-SURFACE-001` requires:

- event-20 XLF-01/XLF-02 evidence retained: independent acquisition, digest
  verification, legal classification, lock, exact package inventory, and
  clean offline reconstruction of the official XLIFF 2.0 Standard package;
- event-25 evidence retained and replayed: exact
  source/test/matrix/denominator/Core-inventory/receipt digests, 27 focused
  tests, Ruff,
  strict Mypy, Pyright 1.1.411, bytecode compilation, check mode, and three
  identical outputs for both reports;
- Event-30 evidence is also required: exact implementation/census/decision/
  adjudication/denominator/SAL/inventory/tool/test/receipt digests, both
  artifact check modes, focused and affected regressions, static checks, five
  authority matches, and three identical authority-bound generations;
- XLF-04 continues at
  `XLF-04-BATCH-005-PARTIAL-002-B-REPAIR-001` until every
  Core obligation, not merely
  every category, has exact stable
  profile, owner, authority/member/location, requirement class, and processing
  semantics;
- the first bounded cycle is exactly the candidate and four RED controls in
  `NEXT-MICROSTEP.yaml`; generated proposals and independent adjudications
  must remain separate;
- source-located XLIFF 2.0/2.1 Core and module deltas;
- complete semantic obligations for hierarchy, inline pairing/order,
  segmentation, state, original data, skeletons, extensions, ITS mappings,
  validation, canonical XML, security, and normative agent processing;
- separate production capability ownership for all eight official modules:
  Translation Candidates/Matches, Glossary, Format Style, Metadata, Resource
  Data, Size and Length Restriction, Validation, and ITS;
- complete accounting for nine module schema vocabularies, with `its` and
  `itsm` mapped to the one ITS module and the informative Change Tracking
  extension receiving no normative conformance credit;
- exact profile subsets on every capability and obligation, with 2.1-only
  rules excluded from 2.0;
- XLIFF 2.2 absent or isolated preview-only, and XLIFF 1.2 outside the 2.x
  model;
- negative controls for missing module ownership, cross-profile
  contamination, malformed identity, and preview leakage;
- three identical strict runs and complete 17/17 authority matches;
- no product source, product test, certification, gate, or promotion change.

## Required proof for each mandatory obligation

- Executed positive behavior.
- Executed negative behavior for rejection/security.
- Preservation behavior for safe unknown/extensions.
- Boundary and beyond-boundary resource tests.
- Semantic roundtrip or metamorphic proof where meaningful.
- Official and genuinely independent interoperability evidence.
- Exact authority, source, test, fixture, corpus, dependency lock, tool,
  environment, built package, import location, and oracle digests.

## Pull-request or bounded-task tier

- contract and proof referential integrity;
- changed-format unit, behavior, rejection and roundtrip tests;
- Ruff, mypy, pyright, architecture, API and security checks;
- reproducible generation where outputs are generated;
- built-wheel and installed-wheel smoke for product changes.

Contract-only tasks defer product wheel proof without satisfying any product
obligation.

## Merge/nightly tier

- full official and independent corpora;
- property, metamorphic, coverage-guided fuzz, mutation and differential tests;
- minimum/latest supported dependency versions;
- performance and memory budgets;
- Linux, Windows, macOS and Python 3.11-3.14;
- replay, invalidation, concurrency and source-versus-wheel isolation.

## Release tier

- fresh checkout and hash-locked environment;
- complete live proof graph rebuild;
- two identical sdist/wheel builds;
- namespace and six-package co-installation;
- official `safetensors` co-installation;
- documentation examples against installed wheels;
- SBOM, provenance, signatures, license and vulnerability evidence;
- standalone repository extraction with full recertification.

## Machinery regression controls

1. Three equivalent reruns produce identical canonical output.
2. Every input category invalidates its correct descendants.
3. Deleted/renamed tests revoke evidence.
4. Modified fixtures cannot reuse results.
5. Stale authority digests stop strict compilation.
6. Missing, duplicate, foreign or broken facts fail closed.
7. Written deferrals cannot satisfy mandatory work.
8. Concurrent runs cannot consume shared mutable state.
9. Source-tree and installed-wheel imports cannot be confused.
10. Manual status edits cannot promote.
11. Historical evidence cannot become current without replay.
12. Repository extraction preserves canonical source/package digests.
13. CRLF/LF checkout differences do not create false invalidation.
14. Global task selection cannot bypass FF6 dependencies.
15. Diagnostic authority overrides remain non-promoting.
16. A lock, schema, runtime, materializer, compiler, store, research input, or
    authority-byte change invalidates affected descendants.

## Promotion

```text
UNASSESSED
-> CONTRACT_READY
-> IMPLEMENTATION_IN_PROGRESS
-> IMPLEMENTATION_VERIFIED
-> RELEASE_CANDIDATE
-> RELEASED
```

Any changed dependency produces `INVALIDATED`. Recovery rebuilds affected
proof; it never edits a status.

## Release boundary

Technical source, packages, docs, SBOMs, provenance, signatures, and repository
exports continue autonomously. Missing credentials or required business/legal
authority records `EXTERNAL_RELEASE_BLOCKED`.

Do not bypass human-only Gate 10, commercial Gate 11, legal approval,
credentials, or publication policy. Do not impersonate an approver.

## Close self-challenge

Before every close:

1. Is the claim executed behavior rather than presence?
2. Does each public symbol map to classified capability and authority?
3. Are positive, negative, preservation, and resource cases current?
4. Can valid input lose information silently?
5. Was the built wheel tested when product behavior changed?
6. Is the oracle independent and digest-bound?
7. Are package boundaries and dependency direction intact?
8. Are optional dependencies isolated?
9. Are API, typing, docs, examples and compatibility complete at this tier?
10. Do changed inputs revoke the right descendants?
11. Are performance and memory bounded at the required tier?
12. Are contradictions and gaps retained?
13. Did writes and staging stay in the allowlist?
14. Do controller, taskcard, index, gaps, proof and packet agree?
15. Were governance and release boundaries preserved?
16. Is the final state no stronger than live evidence?
17. Is every byte required to resume committed on GitLab main or identified as
    an immutable content-addressed external input?
18. Has the outgoing provider released only its own leases and avoided
    transferring provider credentials or execution manifests?
19. Did the shift avoid stash, reset, restore, checkout-discard, clean, broad
    staging, and unscoped generators?
20. Does the handover validator reject predecessor event instructions as well
    as wrong hashes, counts, completion, certification, and recovery state?

## Current authority overlay: Event 40

`FF6-EVENT-000040` is the current native head. The selected task remains
XLIFF, with exact microstep `XLF-04-BATCH-005-PARTIAL-002-I`, 31/105 accepted
obligations, and 9/1,130 verified dispositions. UBL retains 6,001 particle
nodes, stable anonymous-type identities, and 1,178 derivation edges, but
UBL-03 is incomplete. Certification remains 0/6.
