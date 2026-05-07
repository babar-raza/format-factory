---
artifact_id: TC-0029-fodt-gate1-scoring-preparation
artifact_type: taskcard
path: taskcards/TC-0029-fodt-gate1-scoring-preparation.md
format_id: fodt
product_family: words
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
notes: "FODT Gate 1 scoring preparation taskcard. CANDIDATE-ONLY — no Gate 1 approval. Created run039 (2026-05-07). Scoring package (registry/candidates/fodt-gate1-scoring-package.yaml) created but not yet independently verified."
---

# TC-0029: FODT Gate 1 Scoring Preparation

**Taskcard ID:** TC-0029
**Phase:** Pre-Gate 1 (candidate evaluation — CANDIDATE-ONLY)
**Gate:** Pre-Gate 1 (scoring preparation only)
**Status:** verification_passed_pending_human_review
**Created:** 2026-05-07 (run039)
**Created by:** claude-sonnet-4-6 (run039)
**Verified:** 2026-05-07 (run040) — DEC-034 PASS (7/7 factors verified, 88/100 confirmed)
**Review packet:** acquisition-packs/_candidate-shortlists/fodt-gate1-human-review-packet.md

---

## IMPORTANT — Candidate-Only Status

**This taskcard governs scoring preparation only.**

- **No Gate 1 approval is granted or implied.**
- **No official registry entry may be created until human Gate 1 approval.**
- **No acquisition pack may be started until Gate 1 scoring is complete and human-approved.**
- **No spec downloads for FODT.**
- **No FODT-specific samples, parser, or neutral model.**

---

## Objective

Prepare and independently verify the FODT Gate 1 scoring evidence, then present the scoring package for human Gate 1 approval decision.

---

## Deliverables

### Already Created (run039)

1. `registry/candidates/fodt-gate1-scoring-package.yaml` — 7-factor scoring package (score: 88/100, Accept band)
2. `registry/candidates/odf-flat-family-shortlist.yaml` — candidate shortlist (independently verified run039)
3. This taskcard (TC-0029)

### Still Required (Next Sprint)

4. Independent verification of the run039 scoring package (DEC-034 requirement):
   - Verify each scoring factor claim against ODF 1.3 spec evidence
   - Verify FODS Gate 2 legal evidence supports Factor 1 (legal safety)
   - Verify spec cache existence for Factor 2 (spec availability)
   - Verify FODS prototype patterns support Factor 6 estimate (implementation complexity)
5. Present verified scoring package for human Gate 1 approval

---

## Scoring Package Summary

| Factor | Weight | Score | Points | Evidence Quality |
|---|---|---|---|---|
| 1. Legal Safety | 30 | 3/3 | 30 | Supported by FODS Gate 2 evidence |
| 2. Spec Availability | 20 | 3/3 | 20 | Supported by cached ODF 1.3 spec |
| 3. Parseable Structure | 15 | 2/3 | 10 | Supported by FODS prototype patterns |
| 4. Community Demand | 15 | 2/3 | 10 | Plausible (market knowledge) |
| 5. Strategic Track Value | 10 | 3/3 | 10 | Supported by pipeline evidence |
| 6. Implementation Complexity | 5 | 2/3 | 3 | Supported by FODS prototype evidence |
| 7. Family Overlap | 5 | 3/3 | 5 | Supported (different family from FODS) |
| **Total** | **100** | | **88** | **Accept band (70-100)** |

**Band:** Accept (88/100)
**Shortlist estimate:** 87-93/100 — score 88 is within range (CONFIRMED)

---

## Preconditions

- [x] TC-0028 candidate shortlist independently verified (run039)
- [x] FODS Gate 1–5 PASSED (pipeline proven)
- [x] Scoring package created: registry/candidates/fodt-gate1-scoring-package.yaml
- [x] Scoring package independently verified (DEC-034 PASS — run040, 7/7 factors)
- [x] Human-review packet created: acquisition-packs/_candidate-shortlists/fodt-gate1-human-review-packet.md
- [ ] Human Gate 1 approval for FODT (human-only gate)

---

## WIP Limit Check

Current pipeline:
- FODS: Gate 6 blocked (1/2 slots, Gates 4-6)
- FODT: Pre-Gate 1 candidate-only (0/3 slots, Gates 1-3)

**FODT Gate 1 scoring can begin immediately after human Gate 1 approval.**
**WIP limit will NOT be exceeded (0/3 Gates 1-3 slots currently used).**

---

## Out of Scope

- Approving Gate 1 (human-only)
- Creating official registry entries for FODT
- Downloading ODF specs specifically for FODT (same spec as FODS, already cached)
- Creating FODT-specific samples, parsers, schemas, or product source
- CI workflows or security/legal reports

---

## Related Files

- `registry/candidates/fodt-gate1-scoring-package.yaml` — 7-factor scoring evidence
- `registry/candidates/odf-flat-family-shortlist.yaml` — candidate shortlist (run038)
- `acquisition-packs/_candidate-shortlists/odf-flat-family-next-candidates.md` — summary
- `registry/scoring/_scoring-model.md` — scoring model definition
- `taskcards/TC-0028-next-format-candidate-shortlist.md` — parent taskcard

---

## Next Action

Issue a TC-0029 independent verification sprint prompt to verify the 7-factor scoring claims, then present the verified scoring package to the human for Gate 1 approval decision.
