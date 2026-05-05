---
artifact_id: TC-0009
artifact_type: taskcard
path: taskcards/TC-0009-fods-phase2-spec-legal-evidence.md
format_id: fods
product_family: cells
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: "2026-05-04"
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "Phase 2 taskcard for FODS spec and legal evidence planning. CLOSED 2026-05-05. Gate 2 passed: approved by Babar Raza (2026-05-05). Patent search waived. Evidence: run019 drafted, run020 verified, run021 spec acquired, run022 DEC-034 verified, run023 Gate 2 approved."
---

# TC-0009: FODS Phase 2 — Spec and Legal Evidence Planning

**Phase:** 2
**Status:** closed — Gate 2 passed 2026-05-05
**Owner:** Closed. Gate 2 approved by Babar Raza (2026-05-05, run023).
**Created:** 2026-05-04 (run017)
**Last updated:** 2026-05-05 (run023: Gate 2 approved; TC-0009 closed)
**Blocking:** none — Gate 2 passed; TC-0010 activated
**Blocked by:** none
**Format:** fods
**Gate:** Gate 2

---

## Objective

Plan and execute Phase 2 Gate 2 evidence for FODS: spec source verification, legal fast-path checklist, and spec cache acquisition planning. Produce Gate 2 evidence artifacts for human review. The output is evidence for human Gate 2 review — NOT a self-approved gate.

**Gate 2 is a human-only approval.** No agent may self-approve Gate 2.

---

## Prerequisites

- [x] Gate 1 passed — Babar Raza (2026-05-04)
- [x] acquisition-packs/fods/ skeleton exists
- [x] Explicit Phase 2 execution prompt issued by human (run019, 2026-05-04)
- [x] Independent agent verification sprint completed before Gate 2 human review (per DEC-034, AGENTS.md Section V) — run022 (2026-05-05): SHA-256 re-verified, tooling smoke-checks pass, evidence claims reviewed, no overclaiming found

---

## Context

FODS is the pilot format (DEC-001). Gate 1 was approved by Babar Raza on 2026-05-04 with score 93/100. Gate 2 requires spec and legal evidence before sample acquisition (Gate 3) may begin.

The ODF 1.3 specification is published by OASIS at https://docs.oasis-open.org/office/OpenDocument/v1.3/. It is Legal Category 1 (royalty-free). Spec acquisition requires authorization per AGENTS.md Section T3 and `docs/specification-cache.md`.

---

## Scope

### In scope (Phase 2 / Gate 2)

- Identify and document canonical OASIS ODF 1.3 spec source URL and version
- Verify legal fast-path eligibility: OASIS Category 1, royalty-free, two+ open-source implementations, no patent litigation
- Complete `acquisition-packs/fods/legal-notes.md` fast-path checklist
- Plan spec cache acquisition: document what would be acquired, from where, under what conditions
- Complete `acquisition-packs/fods/spec-evidence.md` primary source section
- Update `acquisition-packs/fods/pack.yaml` with spec URL and legal category confirmation
- Update master plan and memory with Gate 2 evidence status
- Produce Gate 2 evidence bundle for human review
- Request human Gate 2 approval (after independent verification sprint per DEC-034)

### Out of scope (Phase 2)

- Spec download is NOT authorized in this taskcard skeleton alone. Spec acquisition requires:
  1. A separate explicit execution prompt naming the format, version, canonical URL, and stating that acquisition is permitted
  2. All six conditions in AGENTS.md Section T3 must be satisfied
  3. Storage in `.local/spec-cache/fods/1.3/` (gitignored, never committed)
- samples/by-format/ — FORBIDDEN until Gate 3
- prototypes/by-format/ — FORBIDDEN until Gate 4
- schemas/neutral-model/ — FORBIDDEN until Gate 5
- Product source code — FORBIDDEN until Gate 9 + Phase 4 prompt
- CI workflows — FORBIDDEN
- Commercial source — FORBIDDEN
- Approving Gate 2 — human-only action

---

## Acceptance Criteria

- [x] Canonical spec URL identified and documented in spec-evidence.md (https://docs.oasis-open.org/office/OpenDocument/v1.3/)
- [x] Spec version confirmed: ODF 1.3 [SUPPORTED_BY_RECORDED_URL]
- [x] Legal fast-path checklist 6/8 items confirmed — run021 added cached spec download confirmation
- [x] Legal category confirmed as Category 1 (OASIS ODF 1.3, royalty-free) [SUPPORTED_BY_RECORDED_URL]
- [x] Two independent open-source implementations confirmed: LibreOffice, Apache OpenOffice [CONFIRMED_INDEPENDENTLY]
- [ ] No patent litigation in past five years confirmed — currently PLAUSIBLE_PENDING_VERIFICATION; pending project lead review
- [x] pack.yaml updated with gate_2 evidence_cached status and run021 spec_cache downloaded/validated status
- [x] Gate 2 evidence bundle produced — run019 bundle created; run020 staging bundle created; run021 full-width clean bundle created (Section J)
- [x] Independent agent verification sprint completed (DEC-034) — run022 (2026-05-05) independently verified run021 evidence: SHA-256 MATCH, VALID/CURRENT, no overclaiming found
- [x] Human has reviewed and explicitly set gate_2.status: passed — Babar Raza, 2026-05-05 (via run023 execution prompt)
- [x] plans/master-plan.md updated with Gate 2 evidence status — v2.16 (run020)
- [x] Self-challenge completed (AGENTS.md Section I, all 15 questions) — run020 self-challenge in bundle

---

## Artifacts to Produce

| Artifact | Path | Gate | Status |
|---|---|---|---|
| Spec evidence | `acquisition-packs/fods/spec-evidence.md` | 2 | evidence_cached_pending_human_review (run022 verified) |
| Legal notes | `acquisition-packs/fods/legal-notes.md` | 2 | evidence_cached_pending_human_review (run022 verified) |
| Pack manifest update | `acquisition-packs/fods/pack.yaml` | 2 | evidence_cached_pending_human_review (run022 verified) |
| Gate 2 evidence bundle | `.local/evidence-bundles/` | 2 | run022 canonical bundle created (run022-independent-gate2-verification-20260505-112638.zip) |

---

## Artifacts Consumed (Inputs)

| Artifact | Path | Required? |
|---|---|---|
| Registry FODS entry | `registry/format-registry.yaml` | Required |
| Legal and licensing policy | `docs/legal-and-licensing.md` | Required |
| Gate 2 criteria | `docs/gates.md` | Required |
| Spec-cache policy | `docs/specification-cache.md` | Required |
| AGENTS.md Section T3 | `AGENTS.md` | Required |
| Scoring model (for context) | `registry/scoring/_scoring-model.md` | Optional |

---

## Steps (to be executed when Phase 2 prompt is issued)

1. Read `docs/gates.md` Gate 2 criteria.
2. Read `docs/legal-and-licensing.md` for Category 1 fast-path rules.
3. Read `docs/specification-cache.md` for spec acquisition authorization model.
4. Identify canonical OASIS ODF 1.3 spec URL.
5. Complete legal-notes.md fast-path checklist (no spec download required for legal work).
6. Update spec-evidence.md primary source section with URL, version, and spec summary.
7. If spec download is authorized in the current prompt: proceed per AGENTS.md Section T3.
8. If spec download is NOT authorized: document spec source metadata only; mark spec as not-yet-cached.
9. Update pack.yaml with confirmed spec URL and legal status.
10. Produce Gate 2 evidence bundle.
11. Request independent agent verification sprint (DEC-034).
12. After verification sprint: request human Gate 2 approval.
13. After human Gate 2 approval: update master plan.

---

## Completion Record

**Status:** evidence_cached_pending_human_review
**Created:** 2026-05-04 by claude-sonnet-4-6 (run017).
**Evidence drafted:** 2026-05-04 by claude-sonnet-4-6 (run019 — Phase 2 execution prompt authorized by human).
**Independently verified and strengthened:** 2026-05-04 by claude-sonnet-4-6 (run020 — combined verification and fix sprint).
**Spec acquired and evidence upgraded:** 2026-05-04 by claude-sonnet-4-6 (run021 — combined sprint: hygiene, settings.json fix, spec acquisition, evidence upgrade).
**Spec download status (run021):** SUCCESS. ODF 1.3 Part 3 PDF downloaded from https://docs.oasis-open.org/office/OpenDocument/v1.3/os/part3-schema/OpenDocument-v1.3-os-part3-schema.pdf (24,270,588 bytes, sha256:92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066). spec-index.yaml validates VALID/CURRENT. Primary claims upgraded to SUPPORTED_BY_CACHED_SOURCE.
**run022 independent verification (2026-05-05):** SHA-256 re-verified: MATCH. spec_index.py VALID/CURRENT. refresh_check.py: 0 stale entries. Tooling dry-run mode confirmed. Evidence claims reviewed: primary source SUPPORTED_BY_CACHED_SOURCE confirmed; structural claims PLAUSIBLE_PENDING_VERIFICATION correctly labeled; no overclaiming found. Stale state fixed. Status upgraded to evidence_cached_pending_human_review. DEC-034 independent verification COMPLETE.
**Next actions:**
  1. Human (project lead) reviews legal-notes.md fast-path checklist (2 items pending: patent search waiver + sign-off)
  2. Human Gate 2 sign-off (DEC-034 independent verification complete as of run022)
  3. After human approval: update registry gate_2.status → passed, update master plan v2.19
