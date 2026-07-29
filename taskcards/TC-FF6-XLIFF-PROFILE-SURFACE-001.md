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

## Known starting state

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
