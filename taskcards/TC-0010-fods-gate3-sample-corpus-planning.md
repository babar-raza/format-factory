---
artifact_id: TC-0010
artifact_type: taskcard
path: taskcards/TC-0010-fods-gate3-sample-corpus-planning.md
format_id: fods
product_family: cells
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: "2026-05-05"
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: [gate_2_not_yet_passed]
notes: "FUTURE PLANNING ONLY. Created run022 as a forward-planning taskcard. DO NOT START until Gate 2 is approved by human. Gate 3 sample corpus planning for FODS."
---

# TC-0010: FODS Gate 3 — Sample Corpus Planning

**Phase:** 2 (planning only) / 3 (execution — after Gate 2 passes)
**Status:** not_started
**Owner:** Pending — assigned after Gate 2 passes
**Created:** 2026-05-05 (run022 — forward planning only)
**Last updated:** 2026-05-05 (run022)
**Blocking:** Gate 3 execution (Gate 3 is Sample Corpus Ready)
**Blocked by:** Gate 2 approval (human sign-off required first)
**Format:** fods
**Gate:** Gate 3

---

## IMPORTANT: DO NOT START

This taskcard was created as forward planning only. No work in this taskcard may begin until Gate 2 has been approved by the human project lead and recorded in `registry/format-registry.yaml` with `gate_2.status: passed`, `gate_2.approved_by`, and `gate_2.approved_date`.

**Gate 2 is not yet approved.** Creating this taskcard does NOT authorize any sample acquisition, sample directory creation, or corpus work.

---

## Objective

After Gate 2 is approved: plan the Gate 3 sample corpus for FODS. Define allowed sample types, provenance requirements, synthetic sample strategy, and real-world sample sources. Produce a corpus plan for human review before any sample is acquired.

**Gate 3 is a human-only approval.** No agent may self-approve Gate 3.

---

## Prerequisites

- [ ] Gate 2 passed — human sign-off in `registry/format-registry.yaml` (gate_2.status: passed)
- [ ] Explicit Gate 3 / Phase 3 execution prompt issued by human after Gate 2 passes
- [ ] Independent agent verification sprint before Gate 3 human review (DEC-034)

---

## Context

FODS is the pilot format. Gate 3 requires a minimum sample corpus covering:
- Minimal valid file
- Empty/trivial file
- File with all core data structures present
- At least one edge-case file

Every sample needs a `_provenance.yaml` entry with `provenance_status: confirmed`. All sample licenses must be on the acceptable licenses list in `docs/legal-and-licensing.md`.

See `docs/gates.md` Gate 3 for full pass criteria.
See `samples/_policy.md` for the sample acquisition policy.

---

## Scope (after Gate 2 passes — planning only until then)

### In scope

- Define the minimum sample corpus structure for FODS
- Define synthetic sample creation plan (samples owned by this project)
- Define real-world sample sources and license verification approach
- Define blocked sample rules (CC-BY-ND, NC, unknown license)
- Define sample provenance tracking procedure
- Define corpus acceptance criteria for Gate 3

### Out of scope — FORBIDDEN until Gate 2 passes AND explicit Gate 3 execution prompt issued

- `samples/by-format/` directory creation — FORBIDDEN
- Any sample file acquisition — FORBIDDEN
- Parser development — FORBIDDEN (Gate 4)
- Neutral model — FORBIDDEN (Gate 5)
- Product source — FORBIDDEN (Gate 9+)
- Prototype — FORBIDDEN (Gate 4)
- Gate 3 self-approval — FORBIDDEN (human-only)

---

## Acceptance Criteria (planning phase — to be defined after Gate 2)

- [ ] Gate 2 passed (prerequisite)
- [ ] Synthetic sample strategy defined
- [ ] Real-world sample source candidates identified with license review
- [ ] Blocked sample rules documented
- [ ] Minimum corpus size and content requirements specified
- [ ] `_provenance.yaml` template/procedure defined for FODS samples
- [ ] Corpus plan reviewed and approved as Gate 3 execution input

---

## Steps (to be executed after Gate 2 passes and Gate 3 execution prompt is issued)

1. Review `docs/gates.md` Gate 3 criteria.
2. Review `docs/legal-and-licensing.md` sample license requirements.
3. Review `samples/_policy.md`.
4. Define synthetic sample plan.
5. Identify real-world sample sources.
6. Classify each source by license.
7. Define edge-case sample requirements.
8. Produce Gate 3 corpus plan.
9. Request independent agent verification sprint (DEC-034).
10. After verification: request human Gate 3 approval.

---

## Completion Record

**Status:** not_started
**Created:** 2026-05-05 by claude-sonnet-4-6 (run022 — forward planning only; Gate 2 not yet passed).

**Next action:** Wait for human Gate 2 sign-off. Then issue explicit Gate 3 execution prompt.
