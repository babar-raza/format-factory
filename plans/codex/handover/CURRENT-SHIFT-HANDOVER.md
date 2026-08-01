---
artifact_id: FF6-SHIFT-HANDOVER-EVENT-37
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-08-01
---

# Outgoing Codex shift: clean Event 37 plus quarantined Partial-002-F RED

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

## What was investigated after Event 37, but not accepted

The outgoing shift began `XLF-04-BATCH-005-PARTIAL-002-F` and independently
read the pinned XLIFF 2.1 Core Schematron authority. The exact report has
context `xlf:source[@xml:lang][parent::xlf:segment |
parent::xlf:ignorable]`, binds root `srcLang`, and reports on
`not(lang($srcLang))`. Nearby normative prose constrains the explicit or
inherited source language by the enclosing document language, while the
Schematron explanatory material permits exact and more-specific sublanguage
matches in XLIFF 2.1.

The evidence-backed working adjudication is:

- direct owner: `SAL-XLIFF-CORE-DOCUMENT-SOURCE-LANGUAGE-001`;
- reject `SAL-XLIFF-CORE-AGENT-VALIDATOR-001` as downstream enforcement;
- reject `SAL-XLIFF-CORE-HIERARCHY-IGNORABLE-001` and
  `SAL-XLIFF-CORE-HIERARCHY-SEGMENT-001` as applicability context;
- reject `SAL-XLIFF-CORE-SOURCE-REQUIRED-001` because the report does not
  establish source presence or cardinality;
- explicitly reject the unproposed but nearby
  `SAL-XLIFF-CORE-LANGUAGE-SOURCE-001`, because omitted-value inheritance is
  not the same obligation as explicit language compatibility.

This conclusion is not accepted state. The next provider must independently
reproduce it and close the full content-addressed proof chain.

Two tests were added first and run genuinely RED:

- `test_source_language_adjudicates_only_document_compatibility_owner`;
- `test_batch_five_source_language_seed_requires_exact_candidate_proof`.

The focused command produced exactly two failures for the intended reasons:
the decision was absent and the extractor did not yet require the exact
candidate proof. The intended decision ID is
`XLF-ADJ-CORE-SCHEMATRON-0007`; the deterministic proposed SAL fact ID is
`SAL-XLIFF-39A807E74F92A266`.

The provisional candidate was then passed to the registered SAL seeder. The
seeder failed before canonical writes with:

```text
[sal-seed] ERROR new SAL candidate has no acquired source_ids
```

The selected row itself had pinned `SRC-XLF-002` provenance. The failure came
from a different historical queue row whose claim no longer exactly matches
the canonical store and which lacks source provenance. This exposes a
structural flaw: a bounded ingestion cannot currently select one candidate,
so unrelated stale queue content controls whether the run succeeds.

The durable repair is to add a fail-closed `--candidate-id` selector to
`tools/spec/seed_sal_candidates.py`, with tests for exact-one selection,
missing and duplicate IDs, deterministic union semantics, unchanged unrelated
rows, and retained authority validation. The new queue row must carry
`candidate_id: XLF-SAL-CAND-CORE-SOURCE-LANGUAGE-COMPATIBILITY-001`. Do not
weaken provenance checks or blanket-edit legacy candidates.

Before this handover, both tracked RED edits and the provisional ignored queue
row were reverted through owned, preflighted writes to the exact Event 37
bytes. The failed seeder changed no canonical SAL store or cache. The old
provider leases were released and its identity completed. This gives Claude a
clean reconstructible checkpoint while preserving every conclusion and exact
next assertion in tracked handover data.

## Exact next work

Claude must start from `XLF-04-BATCH-005-PARTIAL-002-F` and candidate
`XLF-CAND-CORE-SCHEMATRON-B0961B8D3678CA73`. The exact XLIFF 2.1 Schematron
occurrence compares source `xml:lang` with root `srcLang`. Generated proposals
name generic validator, document source language, source-required, segment,
and ignorable contexts; none is accepted until independently adjudicated.

The next shift must start RED, decide the direct semantic owner or record a
gap, repair exact candidate selection without weakening SAL authority checks,
preserve all predecessor rows and candidate identities, run the full
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
