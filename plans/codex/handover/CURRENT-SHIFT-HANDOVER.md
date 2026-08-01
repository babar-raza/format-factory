---
artifact_id: FF6-SHIFT-HANDOVER-EVENT-37
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-08-01
---

# Outgoing Codex shift: Event 37 checkpoint for Claude

## What this shift actually completed

The shift resumed from native Event 36. It independently adjudicated the next
exact XLIFF 2.1 Core Schematron candidate rather than trusting generated
proposal mappings.

It independently revalidated:

- candidate `XLF-CAND-CORE-SCHEMATRON-100732DB0BBED389` and decision
  `XLF-ADJ-CORE-SCHEMATRON-0006`;
- direct owner `SAL-XLIFF-CORE-HIERARCHY-UNIT-CHILDREN-001`, with generic
  validator and segment-child surface proposals explicitly rejected;
- semantic commit `1b758c2e05856552169de098d8719a82f425a1c2`;
- 6 current adjudications, 29/105 obligations, and 76 missing obligations;
- 73 affected adjudicator/extractor tests, an independent 117-test immutable
  checkout replay, 69 production-program tests, 94 format-contract tests
  with one exact documented deselection, deterministic outputs, SAL proof, and
  five authority matches.

It then appended the hash-chained `FF6-EVENT-000037`, updated the controller
and XLIFF taskcard, validated the complete 37-event chain, and pushed GitLab
commit `6fca743ca55a8c221e63954b4c8a371b73e2246d`.

The normal Git commit hook initially could not resolve `python3` on this
Windows host. A temporary external `python3.exe` compatibility shim was added
to `PATH`; the normal hook then ran and passed. No hook bypass was used.

The pushed semantic commit was replayed from a clean detached checkout after
hydrating four exact, digest-verified XLIFF authority cache files. The complete
checkout-identity and affected XLIFF suite passed: 117/117. No tracked file in
the replay worktree changed, and that temporary worktree was safely removed.

The required artifact-index refresh was also attempted. The canonical updater
failed before writing because `.local/artifact-index.yaml` is pre-existing
invalid YAML. Nothing was overwritten; this remains an explicit non-promoting
machinery gap.

## Exact accepted state

- native head: `FF6-EVENT-000037` /
  `09a3ae3d4521afc5c6c6c937d667c2246a8ad1fbae6ffb8af04a5b32e0e2b2b6`;
- controller checkpoint: `6fca743ca55a8c221e63954b4c8a371b73e2246d`;
- state: `CONTRACT`;
- task: `TC-FF6-XLIFF-PROFILE-SURFACE-001`, first unmet step XLF-04;
- candidate dispositions: 6 verified, 1,124 unverified, 1,130 total;
- obligations: 29 resolved, 76 missing, 105 expected;
- XLF-04 incomplete; UBL-03 incomplete;
- product source effect: none; promotions: all `UNASSESSED`;
- production certifications: 0/6.

## Exact next work

Claude must start from `XLF-04-BATCH-005-PARTIAL-002-F` and candidate
`XLF-CAND-CORE-SCHEMATRON-B0961B8D3678CA73`. The exact XLIFF 2.1 Schematron
occurrence compares source `xml:lang` with root `srcLang`. Generated proposals
name generic validator, document source language, source-required, segment,
and ignorable contexts; none is accepted until independently adjudicated.

The next shift must start RED, decide the direct semantic owner or record a
gap, preserve all predecessor rows and candidate identities, run the full
proof ladder, commit and replay one bounded result, append the next native
event only after proof, then refresh this packet again.

## Six-product truth

- 0/6 products are technically certified.
- OpenRaster product source is absent.
- IPYNB, NRRD, XLIFF, SafeTensors, and UBL have useful but incomplete
  pre-production code.
- XLIFF is still compiling its Core obligation denominator; module contracts
  and product work remain locked.
- UBL has partial schema-graph machinery through derivation edges; attributes,
  facets, groups/wildcards, substitutions, documentation, and a complete
  checked-in graph remain open.
- None has the complete independent corpus/oracle, security/resource, fuzz,
  mutation, installed-wheel OS/Python matrix, reproducible package, SBOM,
  provenance, signature, and release proof required by the mission.

## Cross-provider safety

GitLab, the native journal/controller, taskcards, and content-addressed evidence
are authority. Chat memory, provider identity, tokens, leases, mutation
authorizations, and temporary worktrees are never transferable. Each provider
must reconstruct state, obtain fresh leases, and leave one immutable pushed
checkpoint plus a self-tested handover. No provider may approve its own product
certification or weaken proof to finish a shift.

## Known limits

- Event 37 accepts only one additional obligation and candidate disposition.
- Checkout identity is proven for this declared proof closure; future
  generators and byte-sensitive formats still need explicit classification.
- The handover commit will descend from `6fca743c` and cannot embed its own final
  hash; the packet-base rule and Git ancestry check address that recursion.
- Gate 10 and actual publication remain external business-authority boundaries
  even after technical certification.
