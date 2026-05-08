---
artifact_id: TC-0035-fodt-gate4-dec034-verification
artifact_type: taskcard
path: taskcards/TC-0035-fodt-gate4-dec034-verification.md
format_id: fodt
product_family: words
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude-sonnet-4-6
generated_at: "2026-05-08"
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "FODT Gate 4 DEC-034 independent verification taskcard. Created run044 (2026-05-08). Blocked until TC-0034 execution complete + explicit verification prompt. Must run in separate session from TC-0034."
---

# TC-0035: FODT Gate 4 — DEC-034 Independent Verification

**Taskcard ID:** TC-0035
**Phase:** 3 (Gate 4 verification)
**Gate:** Gate 4 (Parser Prototype — independent verification)
**Status:** not_started — blocked until TC-0034 execution complete + explicit verification prompt
**Created:** 2026-05-08 (run044)
**Created by:** claude-sonnet-4-6 (run044)
**Blocked by:** TC-0034 execution + explicit TC-0035 verification prompt
**DEC-034 rule:** Must run in a separate execution session from TC-0034

---

## STOP — Authorization Required

**This taskcard must not be executed until:**
1. TC-0034 (Gate 4 parser prototype) is complete
2. A human issues an explicit TC-0035 verification prompt

Per DEC-034 and AGENTS.md Section V: independent agent verification must be performed in a
separate execution session before Gate 4 is submitted for human approval.

---

## Objective

Perform an independent DEC-034 verification sprint on the FODT Gate 4 parser prototype.
Verify all TC-0034 claims before requesting Gate 4 human approval.

---

## Verification Checklist (minimum 20 checks)

| # | Check |
|---|---|
| 1 | Session is separate from TC-0034 execution session |
| 2 | prototype/by-format/fodt/fodt_parser.py exists |
| 3 | validate_against_samples.py exists |
| 4 | prototype-notes.md exists |
| 5 | Re-run validate_against_samples.py — 4/4 PASS confirmed |
| 6 | minimal-document.fodt: PASS |
| 7 | headings-and-paragraphs.fodt: PASS |
| 8 | list-basic.fodt: PASS |
| 9 | table-basic.fodt: PASS |
| 10 | fodt_parser.py uses ElementTree (stdlib only) |
| 11 | fodt_parser.py has no product-source imports |
| 12 | FR-001 (root element + MIME type verification) implemented |
| 13 | FR-002 (text:p extraction) implemented and tested |
| 14 | FR-003 (text:h extraction with outline-level) implemented and tested |
| 15 | FR-004 (text:list extraction) implemented and tested |
| 16 | FR-005 (table:table extraction) implemented and tested |
| 17 | Forbidden: src/python/fodt/ does NOT exist |
| 18 | Forbidden: src/net/fodt/ does NOT exist |
| 19 | Forbidden: schemas/neutral-model/fodt/ does NOT exist |
| 20 | No Gate 4 self-approval |

---

## Deliverables

- TC-0035 completion evidence (verification summary in bundle-metadata)
- `acquisition-packs/fodt/gate4-human-review-packet.md`
- TC-0034 status updated to: verification_passed_pending_human_review
- Registry FODT gate_4 status updated: prototype_verified_pending_human_review
