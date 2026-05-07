---
artifact_id: fodt-gate2-planning-v1
artifact_type: acquisition-pack-planning
path: acquisition-packs/fodt/gate2-planning.md
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
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "FODT Gate 2 planning document — created run041. Gate 2 execution blocked until explicit Gate 2 execution prompt is issued. DEC-034 independent verification required before Gate 2 human review."
---

# FODT Gate 2 Planning — Spec/Legal Evidence

**Format:** FODT — Flat OpenDocument Text
**Gate:** 2 (Spec/Legal Evidence)
**Status:** PLANNING — Gate 2 execution pending explicit prompt
**Expected fast-path basis:** OASIS RF Category 1 (same as FODS Gate 2)

---

## Gate 2 Objective

Confirm that the FODT specification is legally safe to use for parser implementation and that
the spec is available, comprehensive, and authoritative. Gate 2 must produce:

1. `spec-evidence.md` — updated with full spec source/cache/hash confirmation
2. `legal-notes.md` — updated with legal category, patent search / waiver, fast-path basis
3. `pack.yaml` gate_2 section — updated from `not_started` to `evidence_cached_pending_human_review`
4. Registry entry for FODT — gate_2.status updated after human approval

---

## Fast-Path Analysis

FODT Gate 2 is eligible for the same fast-path as FODS Gate 2 (passed Babar Raza, 2026-05-05, run023):

| Fast-path criterion | FODS Gate 2 result | FODT Gate 2 expected |
|---|---|---|
| Legal Category 1 (OASIS RF) | CONFIRMED | EXPECTED (same spec body) |
| Official canonical source | YES (oasis-open.org) | YES (same URL tree) |
| Patent search | WAIVED (Babar Raza, 2026-05-05) | WAIVABLE (same basis) |
| Spec cached locally | YES (run021) | YES (reuses FODS cache) |
| Spec independently verified | YES (run022 DEC-034) | REUSES verification |

**Fast-path item count (estimated):** 6/8 items — same as FODS Gate 2.

---

## Evidence Sources

All FODT Gate 2 evidence can be drawn from existing FODS pipeline artifacts:

| Evidence needed | Source |
|---|---|
| Legal Category 1 basis | `acquisition-packs/fods/legal-notes.md` (Gate 2 PASSED 2026-05-05) |
| OASIS RF IPR policy | https://www.oasis-open.org/policies-guidelines/ipr/ |
| Spec cache confirmation | `.local/spec-cache/fods/1.3/` (SHA-256 already verified twice) |
| Spec normalization | Already complete (782 pages, 884 sections — run025/run026) |
| FODT-specific structure | ODF 1.3 Part 2 §3 (text documents); same spec body |

---

## Gate 2 Execution Checklist

When Gate 2 execution prompt is issued, the agent must:

- [ ] Confirm spec cache SHA-256 MATCH for ODF 1.3 Part 3 PDF
- [ ] Confirm FODT falls under same OASIS RF legal category as FODS
- [ ] Document fast-path items (target: 6/8 minimum)
- [ ] Update `spec-evidence.md` from `NOT_STARTED` to `SUPPORTED_BY_CACHED_SOURCE`
- [ ] Update `legal-notes.md` with final fast-path declaration
- [ ] Update `pack.yaml` gate_2.status → `evidence_cached_pending_independent_verification`
- [ ] Run DEC-034 independent verification in separate session
- [ ] Update status → `evidence_cached_pending_human_review` after DEC-034 PASS
- [ ] Present Gate 2 human review packet for Babar Raza approval

---

## TC Reference

Gate 2 execution will be governed by a new TC-0030 taskcard (to be created in run041 under Section H).

---

## Blocked Actions

Until Gate 2 is approved:

- No FODT samples may be acquired or created
- No FODT parser prototype may be started
- No FODT neutral model work
- No FODT product source

Gate 2 may proceed in parallel with FODS Gate 6 (WIP limit not violated: FODT Gates 1-3 = 1/3 slots).
