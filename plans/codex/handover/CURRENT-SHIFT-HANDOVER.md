---
artifact_id: FF6-SHIFT-HANDOVER-41BFAEF
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-08-01
---

# Outgoing Codex shift: Event 36 checkpoint for Claude

## What this shift actually completed

The shift began at GitLab handover commit `01c469f9`, where Event 35 still
accepted four XLIFF candidate dispositions while verified repaired evidence at
`809cc18c` contained five. It did not repeat the semantic implementation.

It independently revalidated:

- semantic commit `2dcb161ed8e53bfc55e5be81374f5f7ddea3bb17`;
- checkout-identity repair `809cc18cc6e62ae19f6ea5c11ed41ab9a7ec5956`;
- candidate `XLF-CAND-CORE-SCHEMATRON-8D50B407E90E354E` and decision
  `XLF-ADJ-CORE-SCHEMATRON-0005`;
- 5 current adjudications, 28/105 obligations, and 77 missing obligations;
- 115 affected tests, 69 production-program tests, 94 format-contract tests
  with one exact documented deselection, deterministic outputs, SAL proof, and
  five authority matches.

It then appended the hash-chained `FF6-EVENT-000036`, updated the controller
and XLIFF taskcard, validated the complete 36-event chain, and pushed GitLab
commit `41bfaef73992f69313226543dff81d3a11e232bb`.

The normal Git commit hook initially failed before validation because its
`#!/usr/bin/env python3` interpreter is unavailable on this Windows host. The
same hook program was executed explicitly with the active `python` interpreter
and passed; only then was the already-validated commit created with
`--no-verify`. This was an interpreter-resolution workaround, not a skipped
governance check.

The pushed commit was replayed from a detached `core.autocrlf=true` checkout.
The first run failed closed only because ignored authority CAS bytes were not
present (114 tests passed, one missing-authority failure). After hydrating
exactly `src-xlf-001.bin` and `src-xlf-002.bin` and verifying both committed
SHA-256 locks, the complete affected suite passed: 115/115. No tracked file in
the replay worktree changed, and that worktree alone was removed.

## Exact accepted state

- native head: `FF6-EVENT-000036` /
  `d4a05e36bbae4d3ab5f05a4968045552f79ae45dd7b38f6ba3bc39840f684924`;
- controller checkpoint: `41bfaef73992f69313226543dff81d3a11e232bb`;
- state: `CONTRACT`;
- task: `TC-FF6-XLIFF-PROFILE-SURFACE-001`, first unmet step XLF-04;
- candidate dispositions: 5 verified, 1,125 unverified, 1,130 total;
- obligations: 28 resolved, 77 missing, 105 expected;
- XLF-04 incomplete; UBL-03 incomplete;
- product source effect: none; promotions: all `UNASSESSED`;
- production certifications: 0/6.

## Exact next work

Claude must start from `XLF-04-BATCH-005-PARTIAL-002-E` and candidate
`XLF-CAND-CORE-SCHEMATRON-100732DB0BBED389`. The exact XLIFF 2.1 Schematron
occurrence reports a unit with no segment child as incomplete. Generated
proposals name generic validator, segment hierarchy, and unit-children
obligations; none is accepted until independently adjudicated.

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

- Event 36 closes the accepted/materialized split but only for one candidate.
- Checkout identity is proven for this declared proof closure; future
  generators and byte-sensitive formats still need explicit classification.
- The handover commit will descend from `41bfaef7` and cannot embed its own final
  hash; the packet-base rule and Git ancestry check address that recursion.
- Gate 10 and actual publication remain external business-authority boundaries
  even after technical certification.
