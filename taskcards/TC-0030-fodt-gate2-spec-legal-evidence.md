---
artifact_id: TC-0030-fodt-gate2-spec-legal-evidence
artifact_type: taskcard
path: taskcards/TC-0030-fodt-gate2-spec-legal-evidence.md
format_id: fodt
product_family: words
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude-sonnet-4-6
generated_at: "2026-05-07"
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "FODT Gate 2 spec/legal evidence taskcard. Created run041 (2026-05-07) after Gate 1 approval. Execution blocked until explicit Gate 2 execution prompt is issued. DEC-034 independent verification required before human Gate 2 review."
---

# TC-0030: FODT Gate 2 — Spec/Legal Evidence

**Taskcard ID:** TC-0030
**Phase:** 3 (parallel execution alongside FODS Gate 6)
**Gate:** 2 (Spec/Legal Evidence)
**Status:** not_started — awaiting explicit Gate 2 execution prompt
**Created:** 2026-05-07 (run041)
**Created by:** claude-sonnet-4-6 (run041)
**Gate 1 approved:** YES — Babar Raza, 2026-05-07, run041 (prerequisite met)
**DEC-034 required:** YES — independent verification required before Gate 2 human review

---

## IMPORTANT — Execution Gate

**This taskcard may NOT be executed until an explicit FODT Gate 2 execution prompt is issued.**

The execution prompt must state:
- "Execute TC-0030 FODT Gate 2 spec/legal evidence"
- Authorized format: FODT
- Spec reuse: ODF 1.3 cached (`.local/spec-cache/fods/1.3/`)
- Fast-path basis: OASIS RF Category 1

---

## Objective

Produce the spec/legal evidence for FODT Gate 2. Confirm that ODF 1.3 (already cached from FODS
acquisition) is legally safe and technically sufficient for FODT parser implementation.

---

## Expected Fast-Path

FODT Gate 2 is expected to qualify for the same fast-path as FODS Gate 2 (passed Babar Raza,
2026-05-05, run023). Legal Category 1 (OASIS RF on Limited Terms) applies to all ODF 1.3 formats.

---

## Deliverables

| # | Deliverable | Location | Status |
|---|---|---|---|
| 1 | Updated spec-evidence.md | `acquisition-packs/fodt/spec-evidence.md` | not_started |
| 2 | Updated legal-notes.md | `acquisition-packs/fodt/legal-notes.md` | not_started |
| 3 | Updated pack.yaml (gate_2 section) | `acquisition-packs/fodt/pack.yaml` | not_started |
| 4 | Registry gate_2 status updated | `registry/format-registry.yaml` | not_started |
| 5 | DEC-034 independent verification | Separate execution session | not_started |
| 6 | Gate 2 human review packet | TBD | not_started |

---

## Execution Steps

When the Gate 2 execution prompt is issued:

1. Confirm spec cache SHA-256 MATCH for ODF 1.3 Part 3 PDF at `.local/spec-cache/fods/1.3/`
2. Confirm FODT MIME type and spec coverage in ODF 1.3 (Part 2 §3)
3. Document all fast-path items (min 6/8):
   - OASIS ODF 1.3 legal category: 1 (RF on Limited Terms)
   - Primary source: docs.oasis-open.org (official standards body)
   - Patent search: waivable (same basis as FODS Gate 2 waiver by Babar Raza)
   - Spec cached locally: YES (SHA-256 verified twice)
   - No DRM or access restrictions: YES (plain XML)
   - Open-access publication: YES (OASIS public)
4. Update `spec-evidence.md` status to `SUPPORTED_BY_CACHED_SOURCE`
5. Update `legal-notes.md` with complete fast-path determination
6. Update `pack.yaml` gate_2.status → `evidence_cached_pending_independent_verification`
7. Update registry gate_2.status
8. Run DEC-034 independent verification (separate session)
9. After DEC-034 PASS: update status to `evidence_cached_pending_human_review`
10. Prepare Gate 2 human review packet for Babar Raza

---

## WIP Limit

- FODS: Gates 4-6, using 1/2 slots (Gate 6 blocked)
- FODT: Gates 1-3, using 1/3 slots (Gate 2 in progress)
- Total: 2 active format pipelines — within WIP limits

---

## Acceptance Criteria

- [ ] spec-evidence.md status: `SUPPORTED_BY_CACHED_SOURCE`
- [ ] legal-notes.md: fast-path determination complete with approval date
- [ ] pack.yaml gate_2: status updated from `not_started`
- [ ] Registry gate_2: status updated
- [ ] DEC-034 independent verification: PASS (separate session)
- [ ] Gate 2 human review packet prepared for Babar Raza
- [ ] No FODT samples, parser, neutral model, or product source created

---

## Related Files

| File | Purpose |
|---|---|
| `acquisition-packs/fodt/gate2-planning.md` | Gate 2 execution plan (this sprint) |
| `acquisition-packs/fodt/spec-evidence.md` | Spec evidence (to be updated) |
| `acquisition-packs/fodt/legal-notes.md` | Legal evidence (to be updated) |
| `acquisition-packs/fodt/pack.yaml` | Acquisition pack (gate_2 to be updated) |
| `acquisition-packs/fods/legal-notes.md` | Source legal determination (OASIS RF, PASSED) |
| `acquisition-packs/fods/spec-evidence.md` | Source spec evidence (SUPPORTED_BY_CACHED_SOURCE) |
| `registry/format-registry.yaml` | FODT entry (gate_2 to be updated) |
| `taskcards/TC-0029-fodt-gate1-scoring-preparation.md` | TC-0029 (COMPLETED, Gate 1 approved) |
