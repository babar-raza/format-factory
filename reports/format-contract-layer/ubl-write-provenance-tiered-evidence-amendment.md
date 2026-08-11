# Governance amendment: tiered evidence policy for `SAL-UBL-OBL-A480CAD1CFEA58AD`

**Status: ACCEPTED_WITH_CHANGES (2026-08-11).** Independent review (a fresh
Explore agent, given the amendment, `POL-XBZ-WRITE-01`, `RF-UBL-00008`, the
OASIS publication inventory, and an independently-recomputed 91-type
matrix — not this document's own §3 table) confirmed all 6 evaluated
points: the authority tracing is accurate, the 91-type matrix (55/54/1/36/
37/0) is independently correct, the tiered policy resolves the stated
problem without inventing or dropping requirements, the Schematron
disclosure is honest (verified against commit `60ed1839e`'s own text), and
OpenPeppol-as-optional does not under-deliver anything `RF-UBL-00008`
actually requires. Two hygiene/traceability fixes were required and are
applied in this same commit: (1) the refreshed
`_official-corpus-manifest.yaml` is committed with its own header fields'
apparent inconsistency explicitly explained rather than left ambiguous;
(2) `RF-UBL-00008` itself now cross-references this amendment
(`shared/format-contracts/research/ubl.yaml`), so a future reader of the
L30 finding alone is not left unaware of the downstream tiering.

## 1. What this amends

`SAL-UBL-OBL-A480CAD1CFEA58AD` (UBL-WRITE-001's official-sample provenance
obligation, split out from `SAL-UBL-OBL-F9D5251F2302AE3A` in commit
`821d43e70`). Current canonical text
(`plans/strategic/ff6/obligations/ubl.yaml`):

> rule_text: "Round-trip every official OASIS-published sample of each
> supported maindoc type, comparing canonicalized XML plus typed
> semantics."
> release_gates: "Every supported maindoc type has an official
> OASIS-published sample that round-trips."

## 2. Answering the 5 reconstruction questions directly

1. **Does an authorized policy require one official OASIS sample for every
   type?** Yes, literally, per the text above. Traced to its exact source:
   `RF-UBL-00008` (`shared/format-contracts/research/ubl.yaml:122-136`),
   `authority_class: PRODUCT_REQUIREMENT`, reviewed 2026-07-16, verdict
   ACCEPTED, `source_ids: [SRC-UBL-002]` (the real pinned OASIS package).
   This is an authorized project policy, not spec-normative (confirmed
   twice now — this session's own prior turn, and an independent
   adversarial reviewer this same session) — but it *is* real, reviewed,
   binding text, not something to quarantine as baseless.

2. **Does it say what happens when OASIS published no sample?** No. Neither
   `RF-UBL-00008`'s own text nor `POL-XBZ-WRITE-01`'s (the other cited
   reference, which doesn't even mention sample provenance at all) names a
   fallback for this case. The policy is silent, not permissive or
   prohibitive — this amendment fills that silence rather than overriding
   an explicit rule.

3. **Is OpenPeppol material required, or merely desirable supplementary
   evidence?** Merely desirable. `RF-UBL-00008`'s own text says "official
   OASIS-published sample" — OpenPeppol is not OASIS. Nothing in this
   obligation's own cited authority ever required OpenPeppol material
   specifically; the licensing-inquiry letter was drafted as an
   opportunistic *improvement* path, not because the policy demanded those
   exact 2 documents.

4. **Can the drafted letter resolve only 2 of ~36 types?** Yes, confirmed
   by direct count (§3 below): 36 types have no official OASIS sample;
   OpenPeppol has real-world examples for exactly 2 of them
   (`ApplicationResponse`, `Catalogue`).

5. **Would sending the letter make the obligation completable, under the
   CURRENT (untiered) policy?** No. Even if granted, OpenPeppol material is
   not an "official OASIS-published sample" — the obligation's own literal
   text would remain unmet for those 2 types regardless, and the other ~34
   types have no lead of any kind after exhaustive research
   (`ubl-sample-coverage-research-memo.md`). **Under the current policy,
   this obligation is unsatisfiable in principle**, independent of any
   future human action — not merely difficult, genuinely impossible to
   ever mark `implemented` as literally worded, since OASIS itself has
   never published examples for these types in any UBL release and shows
   no sign of doing so. This is the precise finding that justifies an
   amendment rather than indefinite `partial` status.

## 3. Full per-type evidence matrix (computed fresh, not carried forward)

91 supported types, cross-referenced against
`samples/by-format/ubl/official/_official-corpus-manifest.yaml` (refreshed
2026-08-11 — its own `roundtrip_capable` per-sample data was found stale,
predating `migrate_document()`'s migration paths, and was corrected; see
commit for this segment) and
`samples/by-format/ubl/synthetic/_synthetic-corpus-manifest.yaml`:

| Category | Count | Types |
|---|---|---|
| Official OASIS sample exists AND round-trips (direct or via migration) | 54 | — |
| Official OASIS sample exists but does NOT round-trip | 1 | `CommonTransportationReport` (structurally incompatible with 2.3, confirmed a migration-path limitation of that one legacy document, not a writer defect — see `SAL-UBL-OBL-F9D5251F2302AE3A`'s own evidence) |
| No official OASIS sample published, in any UBL version | 36 | See `ubl-sample-coverage-research-memo.md` for the full list |
| **Tier-3 (`SYNTHETIC_SCHEMA_DERIVED`) fallback exists** | **37** | The 36 above, plus a supplementary fixture for `CommonTransportationReport` |
| **Types with NO applicable-tier evidence at all** | **0** | — |

Every one of the 91 types currently has either a fully-satisfying Tier 1
artifact or a working Tier 3 fallback. **Zero gaps**, computed directly
against real files, not asserted.

## 4. Proposed tiered evidence policy

```
Tier 1 — Official OASIS example (from the pinned release package),
         when OASIS has published one, AND it round-trips (directly
         or via a proven version migration).
Tier 2 — Independently produced, LAWFULLY REDISTRIBUTABLE public example
         (e.g., OpenPeppol, once and only once explicit permission is
         confirmed), when Tier 1 is unavailable or does not clear its
         own round-trip requirement.
Tier 3 — Deterministic SYNTHETIC_SCHEMA_DERIVED instance, generated from
         the pinned official OASIS XSD (tools/ubl/generate_synthetic_
         document_samples.py), when no Tier 1 or Tier 2 artifact is
         lawfully available.
Tier 4 — Supporting proof for whichever artifact is used: schema
         validation, round-trip (or, where genuinely structurally
         incompatible, a documented correct-refusal proof), and
         deterministic serialization (two round trips byte-identical).
```

**Completion rule:** a document type satisfies this obligation when it has
evidence at the *strongest lawfully available* tier, with Tier 4 support.
This obligation must NEVER require a Tier 1 artifact for a type OASIS has
never published — that is not a gap this project can close by any action,
lawful or otherwise, and treating it as an open failure indefinitely
misrepresents a closed question as an active one.

### Honest disclosure: Tier 4's own "Schematron" component

Tier 4 as specified names 4 components: schema, Schematron, round-trip,
deterministic serialization. **Schematron validation is not implemented
anywhere in this package for any UBL type** — a pre-existing, disclosed
gap (see `SAL-UBL-OBL-788B2748204338B8`'s own commit history: "Deliberately
did NOT bundle the distribution's own per-module ISO Schematron (.sch)
files... not required by any of these obligations' own rule_text").
Neither this obligation's own cited authority (`RF-UBL-00008`) nor
`POL-XBZ-WRITE-01` ever names Schematron. This amendment does NOT invent a
Schematron requirement neither cited authority makes, and does NOT let its
absence block completion — but it is named here explicitly, not silently
dropped from Tier 4's own definition, so a future obligation targeting
Schematron specifically (if one is ever authorized) inherits an accurate
starting point rather than a papered-over one.

## 5. What this amendment does NOT do

- Does not relabel any synthetic fixture as an official example. Every
  Tier 3 artifact stays labeled `SYNTHETIC_SCHEMA_DERIVED` in its own
  manifest, unconditionally.
- Does not make the OpenPeppol letter mandatory. It remains a Tier 2
  evidence-*improvement* action for exactly 2 types (would let those 2
  upgrade from Tier 3 to Tier 2 if granted) — never a release blocker,
  since neither cited authority ever required those specific documents.
- Does not touch `promotion.*` or any format's certification status.
- Does not modify `SAL-UBL-OBL-F9D5251F2302AE3A` (writer functionality),
  already `implemented` and out of this amendment's own scope.

## 6. Independent review

Submitted for independent review with exactly these inputs, no prior
reviewer conclusion: this amendment document, `POL-XBZ-WRITE-01`'s own
text, `RF-UBL-00008`'s own text, the OASIS publication inventory
(`ubl-sample-coverage-research-memo.md`), and the 91-type evidence matrix
in §3. See the accompanying review record for the verdict.
