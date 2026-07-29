---
artifact_id: FF6-VALIDATION-RELEASE-HANDOVER-001
artifact_type: verification_and_release_contract
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
authoritative_state: false
---

# Validation, Regression, and Release Contract

## Completion semantics

A capability is complete only when public API, behavior, rejection,
preservation, errors, security, resource limits, scale, determinism, typing,
documentation, external interoperability, installed-wheel use, compatibility,
and full proof-input closure pass.

Planning records, files, symbols, test names, generated classes, and synthetic
fixtures are never sufficient evidence.

## Current evidence boundary

Events 16 through 19 prove:

- 15 of 15 locked authorities live-match;
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
- native FF6 event chain passes through event 19.

It does not prove:

- implementation of any of the 672 obligations merely from contract proof;
- production readiness of any library;
- independent application interoperability;
- installed-wheel platform/dependency matrices;
- certification, extraction, or release readiness.

All obligations remain unverified and all promotion states remain
`UNASSESSED`.

## Completed OpenRaster contract-task gate

`TC-FF6-ORA-PROFILE-SURFACE-001` passed at event 17 with:

- source-located 0.0.3/0.0.4/0.0.5 profile deltas;
- valid SAL authority edges;
- explicit developer capabilities for full editable/viewing baseline,
  compositing/rendering, preservation, security, deterministic output, and
  application interoperability;
- exact profile applicability for every capability and obligation;
- no `FF6-ORA-SURFACE-001` or `FF6-ORA-PROFILE-001` finding;
- three identical strict runs with authority still 15/15 match;
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
- three identical strict runs with 15/15 authorities still matching;
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
- three identical strict runs with 15/15 authorities still matching;
- a governed source repair separating NRRD0004 coordinate transforms from
  NRRD0005 measurement-frame semantics;
- an explicit record that Teem's permissive later-field parsing under earlier
  magic is interoperability behavior, not strict conformance;
- no product source, product test, certification, gate, or promotion change.

## Current XLIFF contract-task gate

`TC-FF6-XLIFF-PROFILE-SURFACE-001` requires:

- independent acquisition, digest verification, legal classification, lock,
  and clean offline reconstruction of the official XLIFF 2.0 Standard package;
- source-located XLIFF 2.0/2.1 Core and module deltas;
- complete semantic obligations for hierarchy, inline pairing/order,
  segmentation, state, original data, skeletons, extensions, ITS mappings,
  validation, canonical XML, security, and normative agent processing;
- separate production capability ownership for Matches, Glossary, Metadata,
  Resource Data, Size and Length Restriction, and Validation modules;
- exact profile subsets on every capability and obligation, with 2.1-only
  rules excluded from 2.0;
- XLIFF 2.2 absent or isolated preview-only, and XLIFF 1.2 outside the 2.x
  model;
- negative controls for missing module ownership, cross-profile
  contamination, malformed identity, and preview leakage;
- three identical strict runs and complete authority matches after the 2.0
  authority record is added;
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
