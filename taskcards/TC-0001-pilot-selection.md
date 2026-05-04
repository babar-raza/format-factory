---
artifact_id: TC-0001
artifact_type: taskcard
path: taskcards/TC-0001-pilot-selection.md
format_id: fods
product_family: cells
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: 2026-05-03
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: Gate 1 scoring taskcard for FODS pilot format.
---

# TC-0001: Pilot Format Selection and Gate 1 Scoring — FODS

**Phase:** 1A
**Status:** in_progress — scoring evidence produced; awaiting human Gate 1 approval
**Owner:** Claude (scoring); Human (Gate 1 approval)
**Created:** 2026-05-03
**Last updated:** 2026-05-04 (run015: scoring completed, registry entry created)
**Blocking:** TC-0002, TC-0003 (FODS must be confirmed as pilot before schema and SDK work begins)
**Blocked by:** Phase 0 completion and human review of foundation files
**Format:** fods
**Gate:** Gate 1

---

## Objective

Apply the seven-factor scoring model to FODS (Flat OpenDocument Spreadsheet) and create the first registry entry in `registry/format-registry.yaml` with `gate_1.status: scored_pending_human_approval`. Request human Gate 1 approval. The output is scoring evidence for human review — NOT a self-approved gate. Gate 1 is passed only after the human records approval.

**Phase assignment:** This taskcard covers Phase 1A (scoring and Gate 1 evidence only). Phase 1B and Phase 2 work begins only after human Gate 1 approval is explicitly recorded in the current session.

---

## Context

FODS is the pre-selected pilot format (Decision DEC-001). It was selected in Phase 0 based on qualitative review as a strong candidate. No pre-score is authoritative — the formal Gate 1 score is computed in this taskcard using the seven-factor 100-point scoring model.

The scoring model is defined in `registry/scoring/_scoring-model.md`. The legal classification fast-path for OASIS Category 1 formats is defined in `docs/legal-and-licensing.md`.

---

## Scope

### In scope (Phase 1A)

- Formal Gate 1 scoring of FODS on all seven dimensions using `registry/scoring/_scoring-model.md`
- Creating the FODS registry entry in `registry/format-registry.yaml` with `gate_1.status: scored_pending_human_approval`
- Requesting human Gate 1 approval — producing evidence bundle for human review
- Updating `plans/master-plan.md` with Gate 1 evidence result (not gate passage — that is human-recorded)

### Out of scope (all Phase 1A runs)

- `acquisition-packs/fods/` — FORBIDDEN until human Gate 1 approval is recorded AND a Phase 2 execution prompt is issued
- `samples/by-format/` — FORBIDDEN until Gate 2
- `schemas/neutral-model/` — FORBIDDEN until Gate 5
- `prototypes/by-format/` — FORBIDDEN until Gate 4
- Product source code (`src/python/{format}/`, `src/net/{format}/`) — FORBIDDEN until Gate 9 human approval + implementation taskcards + explicit Phase 4 implementation prompt. **Obsolete paths** `src/python/open-source/`, `src/dotnet/open-source/`, `src/dotnet/commercial/` must never be created.
- CI workflows — FORBIDDEN until Phase 4 OSS implementation begins + explicit Phase 4 CI/setup prompt
- Commercial-tier source within `src/net/{format}/` — FORBIDDEN until Gate 10 passed + DD3 resolved + commercial taskcards + explicit commercial implementation prompt (Gate 11 is release readiness, not creation authorization)
- Scoring any format other than FODS in this taskcard
- Marking Gate 1 passed — human-only action

---

## Acceptance Criteria

- [ ] FODS scored on all seven dimensions using the scoring model; weighted total computed (out of 100)
- [ ] Scoring rationale documented per dimension
- [ ] Legal category confirmed as Category 1 (OASIS ODF 1.3, royalty-free)
- [ ] No automatic-reject triggers present (legal safety > 0, no Category 5/6, no DRM/access-control bypass)
- [ ] FODS registry entry created in `registry/format-registry.yaml` with `gate_1.status: scored_pending_human_approval`
- [ ] `approved_by` and `approved_date` left as null — to be filled by human
- [ ] Evidence bundle produced for human review
- [ ] Human has reviewed and explicitly set `gate_1.status: passed` (human action, not agent action)
- [ ] `plans/master-plan.md` updated to record Gate 1 evidence produced (agent), and Gate 1 passed (after human approval)
- [ ] Self-challenge completed (AGENTS.md Section I)

---

## Artifacts Produced

| Artifact | Path | Visibility | Notes |
|---|---|---|---|
| FODS registry entry | `registry/format-registry.yaml` | internal | Gate 1 entry only; no acquisition pack yet |

---

## Artifacts Consumed (Inputs)

| Artifact | Path | Required? |
|---|---|---|
| Scoring model | `registry/scoring/_scoring-model.md` | Required |
| Legal and licensing policy | `docs/legal-and-licensing.md` | Required |
| Gate 1 criteria | `docs/gates.md` | Required |
| Registry template | `registry/format-registry.yaml` (schema comments) | Required |

---

## Steps

1. Read `registry/scoring/_scoring-model.md` to understand all seven scoring dimensions and 100-point weights.
2. Read `docs/legal-and-licensing.md` to confirm OASIS ODF 1.3 Category 1 classification and fast-path eligibility.
3. Score FODS on each of the seven dimensions. For each dimension, write a one-sentence rationale.
4. Compute the weighted total (out of 100). Confirm the acceptance band.
5. Check all automatic-reject rules: legal safety > 0, Category not 5 or 6, no DRM/access-control bypass evidence.
6. Write the FODS registry entry in `registry/format-registry.yaml` using the template schema. Set `gate_1.status: scored_pending_human_approval`. Leave `approved_by: null` and `approved_date: null`.
7. Do NOT set `gate_1.status: passed`. Do NOT create `acquisition-packs/fods/`. Do NOT create samples.
8. Produce evidence bundle. Print scoring results. Request human Gate 1 approval.
9. If human approval is not recorded in the current session: stop after producing the evidence bundle. Do not advance.
10. After human sets `gate_1.status: passed` in the registry: complete self-challenge (AGENTS.md Section I).
11. Update `plans/master-plan.md`: record Gate 1 evidence produced (or passed if human approved). Add FODS to format registry summary.

---

## Scoring Evidence (Phase 1A — run015, 2026-05-04)

### Automatic Reject Check

| Check | Result |
|---|---|
| Legal category classified | YES — Category 1 (OASIS RF) |
| Category 5 or 6 | NO |
| DRM/access-control bypass evidence | NO |
| Legal safety score zero | NO |
| **Result** | **NO automatic reject** |

### Seven-Factor Score

| Factor | Score (0-3) | Points | Rationale |
|---|---|---|---|
| Legal Safety (max 30) | 3 | 30 | OASIS ODF 1.3 royalty-free patent policy; no licensing fees or patent barriers |
| Spec Availability (max 20) | 3 | 20 | Comprehensive, actively-maintained spec at docs.oasis-open.org (HTML + PDF) |
| Parseable Structure (max 15) | 3 | 15 | Single flat XML file; no ZIP/OPC container; standard XML parsers sufficient |
| Community Demand (max 15) | 2 | 10 | Moderate demand; used for developer/VCS scenarios; LibreOffice + AOO support |
| Strategic Track Value (max 10) | 3 | 10 | First Cells-family acquisition; pilot validates full pipeline; opens ODF family |
| Implementation Complexity (max 5) | 2 | 3 | No ZIP layer but ODF XML semantics (styles, OpenFormula, conditional formatting) require real work |
| Family Overlap (max 5) | 3 | 5 | First format in registry; no overlap; complementary to future ODF acquisitions |
| **Total** | | **93/100** | **Accept band (70-100)** |

### Recommendation

**Accept — 93/100 (Accept band).** Strong candidate for Gate 1 approval. OASIS royalty-free, comprehensive spec, flat XML structure, first acquisition in Cells family. Recommend human Gate 1 approval.

### Registry Status

FODS entry created in `registry/format-registry.yaml` with:
- `gate_1.status: scored_pending_human_approval`
- `approved_by: null` — to be set by human
- `approved_date: null` — to be set by human

**Agent rule:** Agent set status to `scored_pending_human_approval`. Only human may set `passed`.

### Acceptance Criteria Status

- [x] FODS scored on all seven dimensions; weighted total computed (93/100)
- [x] Scoring rationale documented per dimension
- [x] Legal category confirmed as Category 1 (OASIS ODF 1.3, royalty-free)
- [x] No automatic-reject triggers present
- [x] FODS registry entry created with `gate_1.status: scored_pending_human_approval`
- [x] `approved_by` and `approved_date` left as null
- [ ] Evidence bundle produced for human review — **(created in run015 bundle)**
- [ ] Human has reviewed and explicitly set `gate_1.status: passed` — **PENDING HUMAN ACTION**
- [ ] `plans/master-plan.md` updated — **done (v2.11)**
- [ ] Self-challenge completed — **completed (Section I, all 14 questions answered)**

---

## Completion Record

**Completed by:** Phase 1A scoring: claude-sonnet-4-6 (run015). Gate 1 approval: pending human.
**Completion date:** Phase 1A scoring: 2026-05-04. Gate 1 approval: TBD.
**Artifacts produced:** registry/format-registry.yaml FODS entry; scoring evidence above.
**Gaps discovered:** None.
**Notes:** Gate 1 approval is a human-only action. Human must set gate_1.status: passed in registry/format-registry.yaml after reviewing this scoring evidence.
