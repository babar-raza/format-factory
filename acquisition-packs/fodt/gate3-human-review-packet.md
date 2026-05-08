---
artifact_id: fodt-gate3-human-review-packet
artifact_type: gate-review-packet
path: acquisition-packs/fodt/gate3-human-review-packet.md
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
notes: "FODT Gate 3 human review packet. Created run044 (2026-05-08). TC-0032 DEC-034 verified PASS 27/27 checks. Awaiting Babar Raza Gate 3 approval."
---

# FODT Gate 3 Human Review Packet

**Format:** FODT — Flat OpenDocument Text
**Gate:** 3 — Sample Corpus Complete
**Status:** VERIFICATION_PASS — Awaiting human approval
**DEC-034 verification:** TC-0032 — PASS 27/27 checks (run044, 2026-05-08)
**Prepared:** run044 (2026-05-08)

---

## Gate 3 Summary

4 synthetic FODT samples were created run043 (2026-05-08). All samples are Apache-2.0,
project-owned, hand-authored XML, validated against ODF 1.3 namespace and structure
requirements. All 4 SHA-256 hashes confirmed in `samples/_provenance.yaml`.

| Metric | Value |
|---|---|
| Total samples | 4 |
| Validation PASS | 4/4 |
| License | Apache-2.0 (all) |
| Creator | format-factory project (all) |
| SHA-256 verified | MATCH 4/4 |

---

## TC-0032 DEC-034 Verification Summary (run044)

**Verification session:** run044 — separate from run043 (satisfies DEC-034)
**Checks performed:** 27
**Checks PASS:** 27
**Checks FAIL:** 0

### Checks Performed

| # | Check | Result |
|---|---|---|
| 1 | run044 is separate execution session from run043 (corpus creation) | PASS |
| 2 | FODT_SAMPLE_VALIDATION: PASS 4/4 — validate_fodt_samples.py re-run in run044 | PASS |
| 3 | minimal-document.fodt: PASS (XML well-formed, root element, MIME type, version 1.3, body) | PASS |
| 4 | headings-and-paragraphs.fodt: PASS | PASS |
| 5 | list-basic.fodt: PASS | PASS |
| 6 | table-basic.fodt: PASS | PASS |
| 7 | minimal-document.fodt SHA-256: MATCH (ed118bbaacea1779...38) | PASS |
| 8 | headings-and-paragraphs.fodt SHA-256: MATCH (c3c1463327360ca2...39) | PASS |
| 9 | list-basic.fodt SHA-256: MATCH (5a32987e2b7aec4b...a4) | PASS |
| 10 | table-basic.fodt SHA-256: MATCH (0996d75e18cda81a...49) | PASS |
| 11 | _provenance.yaml: fodt-minimal-01 entry — provenance_status: confirmed | PASS |
| 12 | _provenance.yaml: fodt-headings-01 entry — provenance_status: confirmed | PASS |
| 13 | _provenance.yaml: fodt-list-01 entry — provenance_status: confirmed | PASS |
| 14 | _provenance.yaml: fodt-table-01 entry — provenance_status: confirmed | PASS |
| 15 | All 4 FODT provenance entries: license=Apache-2.0 | PASS |
| 16 | All 4 FODT provenance entries: creator=format-factory project | PASS |
| 17 | All 4 FODT provenance entries: visibility=public | PASS |
| 18 | All 4 FODT provenance entries: source_url=null (synthetic, no external source) | PASS |
| 19 | registry FODT gate_3.status: sample_corpus_created_pending_independent_verification | PASS |
| 20 | registry FODT gate_3.sample_count: 4 | PASS |
| 21 | registry FODT gate_3.approved_by: null (not pre-approved) | PASS |
| 22 | Forbidden: prototypes/by-format/fodt/ does NOT exist | PASS |
| 23 | Forbidden: schemas/neutral-model/fodt/ does NOT exist | PASS |
| 24 | Forbidden: src/python/fodt/ does NOT exist | PASS |
| 25 | Forbidden: src/net/fodt/ does NOT exist | PASS |
| 26 | Forbidden: reports/security/ does NOT exist | PASS |
| 27 | No Gate 3 self-approval — gate_3.approved_by: null | PASS |

---

## Sample Corpus Details

| # | Sample | Coverage | SHA-256 (first 16 chars) | Status |
|---|---|---|---|---|
| 1 | `minimal-document.fodt` | Minimal FODT: single paragraph, office:document root (§2, §5.1) | ed118bbaacea1779 | PASS |
| 2 | `headings-and-paragraphs.fodt` | text:h outline-level 1+2, text:p (§3.1, §5.1, §5.3) | c3c1463327360ca2 | PASS |
| 3 | `list-basic.fodt` | text:list bullet + numbered, text:list-item (§5.3) | 5a32987e2b7aec4b | PASS |
| 4 | `table-basic.fodt` | table:table 2×3, table:table-row, table:table-cell in text context (§14) | 0996d75e18cda81a | PASS |

**All samples:** Apache-2.0, project-owned, synthetic (not derived from any copyrighted document).

---

## Evidence References

| Evidence | Location |
|---|---|
| FODT samples | `samples/by-format/fodt/` (4 files) |
| Sample provenance | `samples/_provenance.yaml` (fodt-minimal-01, fodt-headings-01, fodt-list-01, fodt-table-01) |
| Validation script | `tools/samples/validate_fodt_samples.py` |
| FODT acquisition pack | `acquisition-packs/fodt/` |
| FODT sample sources | `acquisition-packs/fodt/sample-sources.md` |

---

## Gate 3 Approval Request

**TC-0032 DEC-034 verification: PASS 27/27 (run044, 2026-05-08)**

Gate 3 may now be submitted for human approval.

**Requesting:** Babar Raza Gate 3 approval for FODT sample corpus.

**If approved, this authorizes:**
- FODT Gate 4 parser prototype planning (TC-0034)
- FODT Gate 4 execution (requires separate explicit prompt)

**This does NOT authorize:**
- FODT Gate 4 self-approval
- FODT neutral model (Gate 5+)
- FODT oracle comparison (Gate 6)
- FODT product source (Gate 10+)
- FODT security report (Gate 8)
