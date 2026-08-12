# Policy determination — POL-LRA-RENDER-01 Tier C exception for svg:plus

Directive Section 11. **Status: ACCEPTED**, after two rounds of
independent review.

## Determination

`svg:plus` (Porter-Duff Lighter/additive) is classified
**Tier C — MATHEMATICALLY_VERIFIED_ECOSYSTEM_UNSUPPORTED**:

- Zero conforming external OpenRaster producers or consumers found
  after an exhausted, documented search (jsora, ora.js, GIMP 3.0.4,
  Krita, PyShop, PhotoDemon, pyora — each individually rejected or
  confirmed-mismatched, with primary-source evidence for every
  rejection; see `CANDIDATE-LEDGER-2026-08-12b.md` and the per-candidate
  audit docs in this directory).
- The operation's own formula is unambiguous: Porter & Duff (1984),
  and the W3C Compositing and Blending Level 1 spec's own normative
  text (fetched directly from `w3.org`, not from memory).
- format-factory's own output is independently verified against BOTH
  the standard's own text directly AND **two** independently-authored,
  differently-lineaged reference-oracle implementations of the
  underlying compositing formula: GEGL's own `operations/generated/
  plus.c` (GNOME) and Cairo's own `CAIRO_OPERATOR_ADD` (freedesktop.org)
  — both real, unmodified, pip/apt-installed, executed via their own
  real APIs, both producing `(158,96,139,255)` for the established
  discriminating fixture, an EXACT match with format-factory and this
  project's own independent `composite_oracle.py`.
- `svg:plus` remains in the supported registry
  (`registry/format-contract-registry.yaml` /
  `COMPOSITE_OP_REGISTRY`) with full STRICT read/write/round-trip
  coverage, unchanged.
- Any public-facing capability/certification surface citing this
  operation's own ecosystem status must use the label
  `MATHEMATICALLY_VERIFIED_ECOSYSTEM_UNSUPPORTED`, distinct from
  "interoperable" — not yet propagated to those surfaces (see "Pending
  mechanical steps" below).
- Re-evaluation is tracked, not merely promised in prose:
  `.local/taskcards/ORA-COMPOSITE-001-TIER-C-REEVAL-20260812.yaml`
  (gitignored per this repo's own established taskcard convention,
  consistent with every other taskcard in that directory).

## Review history (both rounds, verdicts only — full transcripts were
not persisted as files; this document is the durable record)

1. **Round 1**: ACCEPTED_WITH_CHANGES. Found the search record
   incomplete (Krita's own already-established result was missing from
   the packet's own summary, though not from the underlying
   investigation) and the proposed Tier C text internally inconsistent
   (claimed "two implementations... where possible" while citing only
   one, GEGL, without having tried an identified, obtainable second
   candidate — Cairo). Required 5 changes.
2. **Round 2** (after obtaining Cairo's own real confirmation and
   correcting the Krita omission): ACCEPTED_WITH_CHANGES, narrowed to
   one remaining item — convert the re-evaluation cadence from prose
   into a tracked mechanism. Independently re-verified the Cairo
   evidence file's own actual contents (not just the packet's prose
   claim) before ruling.
3. **This determination**: the taskcard above satisfies round 2's own
   final required change. No further review round was run; if a fresh
   reviewer would want a third pass on the taskcard specifically, that
   is a reasonable ask not yet performed — disclosed, not hidden.

## Explicitly NOT covered by this determination

- `svg:dst-in`/`svg:dst-out`/`svg:src-atop`/`svg:dst-atop`: NOT given a
  Tier C exception. Each still has exactly 1 actual producer/consumer
  (unchanged from before this cycle), which is sufficient for their own
  existing `COVERED_SINGLE_PRODUCER` status under the CURRENT policy
  without needing any amendment. Their new 2x reference-oracle
  corroboration (GEGL + blendmodes) strengthens confidence but was not
  the subject of any policy exception request.
- `svg:hue`/`svg:saturation`/`svg:color`/`svg:luminosity`: NOT
  evaluated for any policy exception. Search is explicitly incomplete
  (PhotoDemon is a real, unpursued second-producer candidate). No
  determination should be made for these until that lead is either
  pursued or explicitly abandoned with reasoning.
- `svg:overlay`/`svg:soft-light`: unchanged, no new evidence gained
  (GEGL found defective for this family), no exception requested.

## Pending mechanical steps (explicitly disclosed, not silently dropped)

1. **Formal adoption into `shared/format-contracts/policy/family-packs/
   layered_raster_archive.yaml`**: this document is the accepted
   determination; the machine-readable policy YAML itself has NOT been
   edited. That file feeds `tools/format_contract/stores.py` and is
   checked against `schemas/format-contracts/format-contract.schema.json`
   — a schema this session did not fully audit for whether it permits
   new fields (e.g. a `tier_exceptions` list) without breaking
   validation. Editing it blind, under time pressure, at the end of an
   already-long session, was judged a worse risk than leaving the
   accepted determination recorded here and flagging the YAML edit as
   the next concrete action. Added to the re-eval taskcard's own
   `required_work` is NOT yet done — this is a separate, smaller
   follow-up: audit the schema, then make a minimal, schema-conformant
   edit adding the Tier C exception for `svg:plus` only.
2. Propagate the `MATHEMATICALLY_VERIFIED_ECOSYSTEM_UNSUPPORTED` label
   to `reports/certification/` and `reports/capability-layer/` surfaces
   once the policy YAML itself is amended — depends on step 1.
