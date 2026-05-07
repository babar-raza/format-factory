---
artifact_id: TC-0028-next-format-candidate-shortlist
artifact_type: taskcard
path: taskcards/TC-0028-next-format-candidate-shortlist.md
format_id: null
product_family: null
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: "2026-05-07"
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "Next-format candidate shortlist taskcard. Created run038 (2026-05-07). CANDIDATE-ONLY — no Gate 1 approval. No official registry entry."
---

# TC-0028: Next-Format Candidate Shortlist — ODF Flat Family

**Taskcard ID:** TC-0028
**Phase:** 3 (parallel planning — does not require Gate 6 completion)
**Gate:** Pre-Gate 1 (candidate evaluation only)
**Status:** in_progress — shortlist independently verified run039; FODT scoring package created run039 (TC-0029)
**Created:** 2026-05-07 (run038)
**Created by:** claude-sonnet-4-6 (run038)
**Updated:** 2026-05-07 (run039)

---

## IMPORTANT — Candidate-Only Status

**This taskcard governs candidate evaluation and shortlist preparation only.**

- **No Gate 1 approval is granted or implied.**
- **No official registry entry may be created until human Gate 1 approval.**
- **No acquisition pack may be started until Gate 1 scoring is complete.**
- **No spec downloads for new formats.**
- **No samples, parser, or neutral model for new formats.**

---

## Objective

Independently verify the ODF flat family candidate shortlist created in run038, then present the recommended next-format candidate (FODT) for human Gate 1 approval decision.

---

## Deliverables

### Already Created (run038)

1. `registry/candidates/odf-flat-family-shortlist.yaml` — full candidate data (4 candidates: FODT, FODP, FODG, FODB)
2. `acquisition-packs/_candidate-shortlists/odf-flat-family-next-candidates.md` — human-readable summary
3. This taskcard (TC-0028)

### Still Required (Next Sprint)

4. Independent verification of the run038 candidate shortlist (DEC-034 requirement)
   - Verify FODT estimated score claims against ODF 1.3 spec evidence
   - Verify pipeline reuse claims against actual FODS artifacts
   - Verify legal category claim (Category 1 RF)
5. Present verified shortlist for human Gate 1 approval decision

---

## Preconditions

- [x] FODS Gate 1-5 PASSED
- [x] FODS oracle pipeline in place (harness, provider registry, operator handoff)
- [x] TC-0028 independent verification sprint (DEC-034) — PASS run039 (10/10 checks)
- [x] FODT Gate 1 scoring package created — 88/100, Accept band (TC-0029, run039)
- [ ] Independent verification of FODT scoring package (DEC-034 — TC-0029 sprint required)
- [ ] Human Gate 1 approval for chosen format (FODT recommended)

---

## WIP Limit Check

Current format pipeline:
- FODS: Gate 6 blocked (Oracle comparison pending)

WIP limit for Gates 4-6: maximum 2 formats. FODS occupies one slot. One slot available for a new format once FODT Gate 1 is approved.

WIP limit for Gates 1-3: maximum 3 formats. Currently 0 in Gates 1-3. Three slots available.

**Gate 1 scoring for FODT can begin without waiting for FODS Gate 6 to complete.**

---

## Out of Scope

- Approving Gate 1 for any new format (human-only)
- Creating official registry entries for FODT/FODP/FODG/FODB
- Downloading ODF specs for new formats
- Creating samples, parsers, schemas, or product source for new formats
- CI workflows
- Reports/security or reports/legal

---

## Related Files

- `registry/candidates/odf-flat-family-shortlist.yaml`
- `acquisition-packs/_candidate-shortlists/odf-flat-family-next-candidates.md`
- `registry/format-registry.yaml` — authoritative (FODT not yet in registry)
- `registry/scoring/_scoring-model.md` — scoring model for Gate 1
- `docs/acquisition-workflow.md` — Stage 1: Candidate Identification

---

## Next Action

Issue a TC-0028 independent verification sprint prompt to verify the candidate shortlist claims, then present the verified shortlist to the human for Gate 1 approval decision.
