---
artifact_id: fodt-legal-notes-v1
artifact_type: acquisition-pack
path: acquisition-packs/fodt/legal-notes.md
format_id: fodt
product_family: words
visibility: evidence-only
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude-sonnet-4-6
generated_at: "2026-05-07"
reusable: true
refresh_policy:
  trigger: manual
  max_age_days: 730
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "FODT Gate 2 legal notes skeleton. Status: DRAFT_PENDING — fast-path expected (inherits FODS Gate 2 OASIS RF determination). Requires Gate 2 execution prompt to finalize."
---

# FODT Legal Notes — Gate 2

**Format:** FODT — Flat OpenDocument Text
**Gate:** 2 (Spec/Legal Evidence)
**Status:** DRAFT_PENDING — Gate 2 evidence pending explicit execution prompt
**Legal category:** 1 — Open Standard RF (OASIS royalty-free)

---

## Legal Classification

| Item | Value |
|---|---|
| Legal category | **1 — Open Standard RF** |
| Standard body | OASIS ODF TC |
| IPR policy | OASIS RF on Limited Terms |
| IPR policy URL | https://www.oasis-open.org/policies-guidelines/ipr/ |
| Patent risk | None — OASIS RF commitments apply to all ODF 1.3 sub-formats |
| Copyright risk | None — open standard, parser implementation is permitted |
| DRM/access control | None — plain XML, no encryption or DRM layer |
| Automatic reject check | ALL PASS — see fodt-gate1-scoring-package.yaml |

---

## Legal Basis

FODT is a sub-format of ODF 1.3 (OpenDocument Format version 1.3). The same OASIS RF on Limited Terms
patent policy that governs FODS (Flat OpenDocument Spreadsheet) also governs FODT.

**Inherited from FODS Gate 2 legal review (passed Babar Raza, 2026-05-05, run023):**
- OASIS ODF 1.3 is published under OASIS RF on Limited Terms
- All ODF 1.3 sub-formats (FODS, FODT, FODP, FODB, ODS, ODT, ODP, ODB) share the same legal basis
- The IPR policy covers the entire ODF 1.3 specification, not individual sub-formats
- Parser implementation does not require royalty payments, patent licenses, or written permission

---

## Fast-Path Basis

Gate 2 fast-path is expected for FODT for the same reasons as FODS:

| Fast-path criterion | Status |
|---|---|
| Legal Category 1 (OASIS RF) | CONFIRMED (same as FODS) |
| Official OASIS source | CONFIRMED (spec cached from OASIS site, run021) |
| Patent search | WAIVABLE — same basis as FODS Gate 2 patent search waiver |
| No DRM or access control | CONFIRMED (flat XML, no encryption) |
| No reverse engineering required | CONFIRMED (public specification) |

**Formal Gate 2 fast-path declaration and patent search waiver must be recorded in pack.yaml
by the human reviewer when Gate 2 is executed.**

---

## What Is NOT Covered Here

This legal notes skeleton covers the classification basis only. Full Gate 2 legal notes should include:

1. Formal patent search or waiver statement
2. Human reviewer sign-off (Babar Raza)
3. Any FODT-specific legal concerns (e.g., trademark, specific patent claims)
4. Final fast-path declaration with approval date

These items are deferred to the Gate 2 execution prompt.

---

## Cross-References

| File | Relationship |
|---|---|
| `acquisition-packs/fods/legal-notes.md` | Source Gate 2 legal determination (Category 1 RF, PASSED Babar Raza 2026-05-05) |
| `registry/candidates/fodt-gate1-scoring-package.yaml` | Factor 1 evidence (AR checks + 30/30 legal safety) |
| `acquisition-packs/fodt/spec-evidence.md` | Spec evidence (spec cache reuse) |
| `docs/odf-flat-family-reuse-strategy.md` | ODF flat family reuse rationale |
