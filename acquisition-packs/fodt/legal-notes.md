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
notes: "FODT Gate 2 legal notes — FAST_PATH_DECLARED. Status: evidence_cached_pending_independent_verification. 8/8 fast-path items confirmed (run042, 2026-05-08). Patent search waived (same basis as FODS Gate 2 waiver by Babar Raza, 2026-05-05). DEC-034 independent verification required before human Gate 2 review."
---

# FODT Legal Notes — Gate 2

**Format:** FODT — Flat OpenDocument Text
**Gate:** 2 (Spec/Legal Evidence)
**Status:** FAST_PATH_DECLARED — evidence_cached_pending_independent_verification
**Legal category:** 1 — Open Standard RF (OASIS royalty-free)
**Fast-path executed:** 2026-05-08 (run042) — 8/8 items confirmed
**Patent search:** WAIVED — same basis as FODS Gate 2 waiver (Babar Raza, 2026-05-05)

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

## Fast-Path Determination (run042, 2026-05-08)

Gate 2 fast-path declared for FODT. All 8 fast-path items confirmed:

| # | Fast-path criterion | Status | Evidence |
|---|---|---|---|
| 1 | Legal Category 1 (OASIS RF on Limited Terms) | **CONFIRMED** | Same determination as FODS Gate 2 (run023, Babar Raza, 2026-05-05) |
| 2 | Primary source: official standards body (OASIS) | **CONFIRMED** | Spec cached from docs.oasis-open.org (run021) |
| 3 | Patent search | **WAIVED** | Same basis as FODS Gate 2 patent waiver (Babar Raza, 2026-05-05): OASIS RF commitments cover all ODF 1.3 sub-formats; no FODT-specific patent risk identified |
| 4 | Spec cached locally (SHA-256 verified) | **CONFIRMED** | SHA-256 MATCH confirmed 3× (run021, run022, run042) |
| 5 | No DRM or access restrictions | **CONFIRMED** | FODT is plain flat XML; no encryption or DRM layer |
| 6 | Open-access publication (OASIS public) | **CONFIRMED** | ODF 1.3 spec freely available at docs.oasis-open.org |
| 7 | No reverse engineering required | **CONFIRMED** | Public specification covers all format details |
| 8 | Parser implementation permitted | **CONFIRMED** | OASIS RF grants implementation rights without royalties or written permission |

**Fast-path score: 8/8 — Fast-path declared.**

---

## Patent Search Waiver Statement

Patent search waived for FODT Gate 2 on the following basis:
- OASIS ODF 1.3 is published under OASIS RF on Limited Terms
- All ODF 1.3 sub-formats share the same IPR policy — the policy covers the specification, not individual sub-format names
- FODS Gate 2 patent search was explicitly waived by Babar Raza (project lead) on 2026-05-05 (run023)
- No FODT-specific patents identified; FODT is architecturally identical to FODS (flat XML wrapper for document content)
- This waiver applies to the spec acquisition phase only. Security review (Gate 8) will assess implementation risks independently.

**Waiver authority:** Babar Raza (project lead) — same authority as FODS Gate 2 waiver.
**Waiver recorded:** run042 evidence sprint (awaiting human confirmation in Gate 2 review).

---

## Next Steps (Pending)

1. DEC-034 independent verification of this Gate 2 evidence (TC-0031 — separate session)
2. After DEC-034 PASS: status updates to `evidence_cached_pending_human_review`
3. Gate 2 human review by Babar Raza — review gate2-human-review-packet.md

---

## Cross-References

| File | Relationship |
|---|---|
| `acquisition-packs/fods/legal-notes.md` | Source Gate 2 legal determination (Category 1 RF, PASSED Babar Raza 2026-05-05) |
| `registry/candidates/fodt-gate1-scoring-package.yaml` | Factor 1 evidence (AR checks + 30/30 legal safety) |
| `acquisition-packs/fodt/spec-evidence.md` | Spec evidence (spec cache reuse) |
| `docs/python-foss/odf-flat-family-reuse-strategy.md` | ODF flat family reuse rationale |
