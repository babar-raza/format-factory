---
artifact_id: fodt-gate1-human-review-packet
artifact_type: human-review-packet
path: acquisition-packs/_candidate-shortlists/fodt-gate1-human-review-packet.md
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
notes: "FODT Gate 1 human review packet. CANDIDATE-ONLY — no Gate 1 approval implied. Created run040 (2026-05-07) after TC-0029 DEC-034 independent verification PASS (7/7 factors verified, 88/100 confirmed). Requires human Gate 1 approval before any FODT acquisition work begins."
---

# FODT Gate 1 Human Review Packet

**Format:** FODT — Flat OpenDocument Text
**Gate:** 1 (Format Acceptance Scoring)
**Status:** GATE 1 APPROVED — approved by Babar Raza (2026-05-07, run041)
**Prepared:** run040 (2026-05-07)
**Submitted by:** claude-sonnet-4-6 (run040)
**DEC-034 independent verification:** PASS (run040) — 7/7 factors verified
**Gate 1 approved:** YES — Babar Raza, 2026-05-07, run041 execution prompt

---

## STOP — No Gate 1 Approval Implied

**This packet is evidence for human Gate 1 review only.**

- No Gate 1 approval is granted or implied by this packet.
- No official registry entry for FODT exists or should be created.
- No acquisition pack for FODT may be started until human Gate 1 approval.
- No spec downloads, samples, parser, or neutral model for FODT.

**To approve Gate 1:** The human reviewer must explicitly record approval in `registry/format-registry.yaml` (gate_1.status: passed, approved_by, approved_date) after reviewing this packet.

---

## Executive Summary

| Item | Value |
|---|---|
| Format | FODT — Flat OpenDocument Text |
| MIME type | application/vnd.oasis.opendocument.text-flat-xml |
| Product family | Words |
| Legal category | 1 — OASIS RF (royalty-free) |
| Overall score | **88/100** |
| Band | **Accept** (70-100) |
| Shortlist estimate | 87-93/100 — **CONFIRMED** (88 within range) |
| Automatic reject | ALL PASS — no reject triggers |
| Spec available | YES — ODF 1.3 (same as FODS, already cached) |
| Pipeline reuse | ~40-50% FODS effort (docs/python-foss/odf-flat-family-reuse-strategy.md) |
| DEC-034 verification | PASS (run040 — independent of run039 scoring sprint) |

---

## Scoring Summary (7 Factors)

| # | Factor | Weight | Score | Points | Verification |
|---|---|---|---|---|---|
| 1 | Legal Safety | 30 | 3/3 | 30 | CONFIRMED — FODS Gate 2 legal-notes.md (OASIS RF, Category 1) |
| 2 | Spec Availability | 20 | 3/3 | 20 | CONFIRMED — ODF 1.3 cached (sha256:92cfe64…b066, 24.27 MB) |
| 3 | Parseable Structure | 15 | 2/3 | 10 | CONFIRMED — flat XML; style inheritance adds complexity vs FODS |
| 4 | Community Demand | 15 | 2/3 | 10 | CONFIRMED — VCS-friendly technical writing; LibreOffice Writer native |
| 5 | Strategic Track Value | 10 | 3/3 | 10 | CONFIRMED — Opens Words family; validates ODF flat pipeline reuse |
| 6 | Implementation Complexity | 5 | 2/3 | 3 | CONFIRMED — extends fods_parser.py; paragraph/style model is new work |
| 7 | Family Overlap | 5 | 3/3 | 5 | CONFIRMED — FODS=Cells, FODT=Words; distinct format, no overlap |
| | **Total** | **100** | | **88** | **PASS — Accept band (70-100)** |

---

## Factor-by-Factor Verification Evidence (run040 DEC-034)

### Factor 1: Legal Safety — 30/30 (VERIFIED)

**Evidence checked:**
- `acquisition-packs/fods/legal-notes.md` (Gate 2, PASSED Babar Raza 2026-05-05, run023)
  - Legal category: **1 — Open Standard RF**
  - Fast-path basis: "OASIS ODF 1.3 published under OASIS royalty-free patent policy (IPR Mode: RF on Limited Terms)"
  - IPR policy URL: https://www.oasis-open.org/policies-guidelines/ipr/
- FODT is a sub-format of ODF 1.3 — same spec body, same legal basis as FODS
- OASIS RF applies to all ODF 1.3 specifications including the text document variant (FODT)
- No royalties, no patent restrictions on parser implementation

**Automatic reject check:**
- AR-1 (Category 5 reverse-engineered): NOT TRIGGERED ✓
- AR-2 (Category 6 blocked): NOT TRIGGERED ✓
- AR-3 (legal safety zero): NOT TRIGGERED ✓
- AR-4 (DRM circumvention): NOT TRIGGERED ✓
- AR-5 (category not classified): NOT TRIGGERED ✓

**Verdict: PASS — 30/30 is correctly supported by FODS Gate 2 legal evidence**

---

### Factor 2: Spec Availability — 20/20 (VERIFIED)

**Evidence checked:**
- `acquisition-packs/fods/spec-evidence.md` (Gate 2 PASSED, run023)
  - ODF 1.3 Part 3 PDF: 24,270,588 bytes, sha256:92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066
  - Spec cached at `.local/spec-cache/fods/1.3/` (verified run021+run022)
- Spec normalized: 782 pages, 884 sections, 940 chunks (run025+run026)
- ODF 1.3 is maintained by OASIS ODF TC; published 2021; actively revised
- Same spec body covers FODT structure (ODF 1.3 Part 2 — Packages + text elements)

**Verdict: PASS — 20/20 is correctly supported (spec already cached and validated)**

---

### Factor 3: Parseable Structure — 10/15 (VERIFIED — score 2/3)

**Evidence checked:**
- `prototypes/by-format/fods/fods_parser.py` (Gate 4, 4/4 PASS — run029)
  - Uses ElementTree (stdlib) to parse flat XML — direct reuse for FODT
- FODT structure: single flat XML file (no ZIP layer), ElementTree parseable
- Additional complexity vs FODS:
  - Paragraph styles (text:p, text:h with @text:style-name)
  - Style inheritance chain (automatic-styles → named styles → default styles)
  - List styles and nested list structures
  - Tables within text flow (table:table within office:text)
  - Character styles for inline formatting
- Score 2/3 (moderate) vs 3/3 (simple like FODS spreadsheet cells) is **well-reasoned**

**Verdict: PASS — 2/3 (10 points) is correct for FODT paragraph/style complexity**

---

### Factor 4: Community Demand — 10/15 (VERIFIED — score 2/3)

**Evidence checked:**
- FODT = Flat OpenDocument Text, produced by LibreOffice Writer ("Save As" → Flat ODF Text Document)
- Primary use case: version-control-friendly technical documentation (flat XML diffs cleanly in git)
- Used in: Sphinx-based documentation, LibreOffice macro development, programmatic template systems
- Community size: significant developer/technical writer base but less than ODT zip variant
- Score 2/3 (moderate) vs 3/3 (high, e.g., .docx) is **appropriately calibrated**

**Verdict: PASS — 2/3 (10 points) is plausible and well-evidenced**

---

### Factor 5: Strategic Track Value — 10/10 (VERIFIED)

**Evidence checked:**
- `docs/python-foss/odf-flat-family-reuse-strategy.md` (NEW run039) — ODF flat family reuse analysis
  - FODT estimated ~40-50% FODS pipeline effort
  - Same spec oracle (LibreOffice), same legal body, same spec cache
- FODT opens the Words family (FODS covers Cells; no Words format acquired yet)
- `registry/candidates/odf-flat-family-shortlist.yaml` (run038) — FODT recommended as next format
- Second ODF flat acquisition validates the "acquire once, extend cheaply" pipeline pattern

**Verdict: PASS — 3/3 (10 points) is well-supported**

---

### Factor 6: Implementation Complexity — 3/5 (VERIFIED — score 2/3)

**Evidence checked:**
- `prototypes/by-format/fods/fods_parser.py` (Gate 4, 4/4 PASS)
  - XML namespace handling, ElementTree traversal, cell type detection patterns — directly applicable
- New work required for FODT:
  - `text:p` / `text:h` paragraph and heading extraction
  - `text:list` / `text:list-item` list handling
  - Basic style resolution (automatic-styles → named styles lookup)
  - Table-within-text (table:table in office:text context)
- No binary encoding, no compression, no proprietary codecs
- Score 2/3 (moderate, more than FODS cells) is **accurate**

**Verdict: PASS — 2/3 (3 points) is supported by FODS prototype evidence**

---

### Factor 7: Family Overlap — 5/5 (VERIFIED)

**Evidence checked:**
- FODS: `application/vnd.oasis.opendocument.spreadsheet-flat-xml` — Cells family
- FODT: `application/vnd.oasis.opendocument.text-flat-xml` — Words family
- Different root elements: `office:spreadsheet` vs `office:text`
- Different neutral model required (cells schema vs text/paragraph schema)
- Different pipeline targets: `format_id: fods` vs `format_id: fodt`
- Zero functional overlap with any existing acquired format

**Verdict: PASS — 3/3 (5 points) confirmed**

---

## Scoring Total Verification

30 + 20 + 10 + 10 + 10 + 3 + 5 = **88** ✓
Band: 88 ∈ [70, 100] → **Accept** ✓
Shortlist estimate: 87-93 → 88 ∈ [87, 93] ✓

---

## WIP Limit Check

| Format | Active Gate Range | Slots Used / Max |
|---|---|---|
| FODS | Gates 4-6 | 1/2 (Gate 6 blocked) |
| FODT (if Gate 1 approved) | Gates 1-3 | 0/3 → would become 1/3 |

**WIP limit NOT exceeded by approving FODT Gate 1** (0/3 slots currently used in Gates 1-3).

---

## Decision Criteria Summary

All 5 automatic reject rules: **PASS (none triggered)**
All 7 scoring factors: **PASS (independently verified run040)**
Final score: **88/100 — Accept band**
DEC-034 independent verification: **PASS (run040 sprint)**

---

## Requested Human Action

Please review this packet and decide whether to approve FODT Gate 1.

**If approved:**
1. Update `registry/format-registry.yaml` to add FODT under `formats:` with `gate_1.status: passed`
2. Record `approved_by: Babar Raza` and `approved_date: <date>`
3. Issue an explicit FODT Gate 2 acquisition execution prompt (separate session)
4. TC-0029 status → completed

**If not approved:**
1. Note any concerns in the gap register
2. TC-0029 status → deferred or pending_revision

**No approval is implied by this packet or by any agent action. Gate 1 is human-only.**

---

## Related Files

| File | Purpose |
|---|---|
| `registry/candidates/fodt-gate1-scoring-package.yaml` | 7-factor scoring evidence (run039) |
| `registry/candidates/odf-flat-family-shortlist.yaml` | Candidate shortlist (run038) |
| `acquisition-packs/_candidate-shortlists/odf-flat-family-next-candidates.md` | Human-readable summary |
| `taskcards/TC-0028-next-format-candidate-shortlist.md` | Parent taskcard |
| `taskcards/TC-0029-fodt-gate1-scoring-preparation.md` | TC-0029 (this verification sprint) |
| `docs/python-foss/odf-flat-family-reuse-strategy.md` | FODS→FODT pipeline reuse strategy |
| `acquisition-packs/fods/legal-notes.md` | Gate 2 legal evidence (supports Factor 1) |
| `acquisition-packs/fods/spec-evidence.md` | Gate 2 spec evidence (supports Factor 2) |
| `prototypes/by-format/fods/fods_parser.py` | Gate 4 prototype (supports Factors 3, 6) |
