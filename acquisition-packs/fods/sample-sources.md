---
artifact_id: fods-sample-sources-v1
artifact_type: acquisition-pack
path: acquisition-packs/fods/sample-sources.md
format_id: fods
product_family: cells
visibility: evidence-only
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: "2026-05-04"
reusable: true
refresh_policy:
  trigger: manual
  max_age_days: 180
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "Gate 3 planning artifact. Corpus plan drafted run024. Full normalization completed run025: text.txt 2,160,370 chars, pages.jsonl 782 pages, citations.yaml 194 section refs, 35 external refs. Spec section references verified against normalized text. No samples acquired."
---

# Sample Sources — Flat OpenDocument Spreadsheet (FODS)

**Format ID:** `fods`
**Gate:** 3
**Status:** planning_in_progress — corpus plan drafted run024; awaiting explicit Gate 3 execution prompt for acquisition

**Gate 1 approved by:** Babar Raza (2026-05-04)
**Gate 2 status:** PASSED — Babar Raza (2026-05-05, run023)
**Gate 3 status:** planning_ready (TC-0010); planning in progress (run024); awaiting explicit Gate 3 execution prompt for acquisition

**Normalization status:** Full extraction completed run025 (G-NORM-001 resolved). pdfminer.six 20260107 installed. Extracted: text.txt (2,160,370 chars), pages.jsonl (782 pages), citations.yaml (194 section refs, 35 external refs). SHA-256 MATCH: `sha256:92cfe64...b066`. Validation: 7 PASS, 1 WARN (parser-requirements.yaml pending), 0 FAIL.

**Important:** No samples have been acquired. `samples/by-format/fods/` does not exist and must not be created until Gate 3 is explicitly authorized by a human execution prompt.

---

## Purpose

This document records candidate sample sources for FODS sample acquisition. It is a working document for Gate 3 planning. The authoritative provenance records for acquired samples are in `samples/_provenance.yaml`. This document captures the research process: what sources were found, why some were selected and others rejected, and what the final corpus plan is.

---

## Sample Requirements

The minimum corpus for Gate 3 must include:

| Sample Type | Description | Spec reference | Status |
|---|---|---|---|
| Minimal valid | Smallest valid FODS file with one sheet, one cell | ODF 1.3 Part 3 §3.1.2 (`<office:document>` root), §3.7 (`<office:spreadsheet>`) | Needed |
| Empty / trivial | Empty spreadsheet (no cells, no data) | ODF 1.3 Part 3 §2.2.4 (Spreadsheet document conformance), §3.7 | Needed |
| Core data | Multiple sheets, cells with text/numbers/formulas, basic styles | ODF 1.3 Part 3 §9.4 (Spreadsheet Document Content) | Needed |
| Edge case | Empty rows, special characters (Unicode), long strings, merged cells | ODF 1.3 Part 3 §9.1.5, §20.8.3 (most-cited section in spec) | Needed |

Preference order: (1) Created specifically for this project (owned by project — Apache-2.0), (2) CC0 / public domain, (3) CC-BY (with attribution preserved), (4) CC-BY-SA, (5) Apache 2.0 or MIT from open-source projects.

**Spec section references verified run025** against normalized text.txt (2,160,370 chars, 782 pages). Key sections confirmed present:
- §2.2.4: OpenDocument Spreadsheet Document conformance rules
- §3.1.2: `<office:document>` element (single XML file root for FODS)
- §3.7: `<office:spreadsheet>` element (spreadsheet content container)
- §9.4: Spreadsheet Document Content
- §20.8.3: Most frequently cross-referenced section (44 references in spec)

---

## Blocked Sample Rules

The following sample types must NOT be acquired:

| Condition | Rule |
|---|---|
| License CC-BY-ND | BLOCKED — no-derivatives prevents format conversion testing |
| License CC-NC (any variant) | BLOCKED — non-commercial limits our use |
| License: unknown or "all rights reserved" | BLOCKED — must not acquire without explicit license confirmation |
| Origin: proprietary corporate documents | BLOCKED — may contain confidential data or embedded PII |
| Origin: user-uploaded without explicit license grant | BLOCKED — unknown provenance |

---

## Synthetic Sample Strategy

For Gate 3, the preferred approach is project-owned synthetic samples:

**Strategy:** Create minimal, well-defined FODS files by hand (or via LibreOffice automation) that:
- Cover all required sample types
- Contain no third-party content
- Are explicitly licensed Apache-2.0 by this project
- Are reproducible from a defined schema (documented in the provenance record)

**Rationale:** For a pilot format, synthetic samples eliminate all provenance and license risk. Real-world samples may be added in subsequent gate cycles when sources with confirmed clean licenses are identified.

**Generation approach (to be executed when Gate 3 is authorized):**
1. Create FODS files using a Python script (`tools/samples/create_fods_samples.py`) — script to be created in Gate 3 execution.
2. Verify output is valid FODS using LibreOffice or a FODS parser.
3. Record provenance in `samples/_provenance.yaml` with: origin, generator script hash, creation date, spec version targeted.

---

## Candidate Sources

### Source A: Project-created synthetic samples (PREFERRED)

| Field | Value |
|---|---|
| URL | N/A — created by project |
| License | Apache-2.0 (project-owned) |
| Format variant | FODS (Flat OpenDocument Spreadsheet, XML) |
| File count | 4–6 minimum (minimal, empty, core-data, edge-case, formula-test, style-test) |
| Sample types available | All required types |
| Acquisition status | PENDING — deferred to Gate 3 execution prompt |
| Notes | Requires `tools/samples/create_fods_samples.py` (to be created Gate 3) |

### Source B: LibreOffice Test Suite (CANDIDATE — license review required)

| Field | Value |
|---|---|
| URL | https://github.com/LibreOffice/core/tree/master/sc/qa/unit/data (indicative — verify at Gate 3) |
| License | MPL 2.0 (LibreOffice source) — to be verified for test data files specifically |
| Format variant | ODS and FODS mixed — must filter to .fods |
| File count | To be determined at Gate 3 |
| Sample types available | Core data, edge cases likely present |
| Acquisition status | PENDING — license and content review required at Gate 3 |
| Notes | MPL 2.0 is compatible with Apache-2.0 for most uses. Verify no NC/ND constraints on test data. |

### Source C: OASIS ODF Interoperability Test Suite (CANDIDATE — check availability)

| Field | Value |
|---|---|
| URL | To be identified — OASIS ODF Interoperability TC may publish test suites |
| License | To be verified |
| Format variant | ODF (may include FODS) |
| File count | Unknown |
| Acquisition status | PENDING — research required at Gate 3 |
| Notes | If available and licensed for use, may provide spec-conformance edge cases |

---

## Provenance Tracking Procedure

For each sample acquired at Gate 3:

```yaml
# Template for samples/_provenance.yaml entry
- sample_id: fods-minimal-v1
  format_id: fods
  filename: minimal.fods
  path: samples/by-format/fods/minimal.fods
  source: project-synthetic
  source_url: null
  license: Apache-2.0
  license_url: https://www.apache.org/licenses/LICENSE-2.0
  provenance_status: confirmed
  created_by: tools/samples/create_fods_samples.py
  created_at: (to be filled)
  spec_version: ODF 1.3
  sample_type: minimal_valid
  notes: Hand-crafted minimal FODS file for Gate 3 corpus
```

---

## Final Corpus Plan

*(Status: planned — to be confirmed before Gate 3 acquisition is requested.)*

| Sample File | Source | License | Sample Type | Provenance Entry Created? |
|---|---|---|---|---|
| `samples/by-format/fods/minimal.fods` | Project synthetic | Apache-2.0 | minimal_valid | No — Gate 3 execution required |
| `samples/by-format/fods/empty.fods` | Project synthetic | Apache-2.0 | empty_trivial | No — Gate 3 execution required |
| `samples/by-format/fods/core-data.fods` | Project synthetic | Apache-2.0 | core_data | No — Gate 3 execution required |
| `samples/by-format/fods/edge-case.fods` | Project synthetic | Apache-2.0 | edge_case | No — Gate 3 execution required |

---

## Gate 3 Planning Checklist

- [x] Gate 2 passed — Babar Raza (2026-05-05, run023)
- [x] Sample requirement types defined (4 required)
- [x] Blocked sample rules documented
- [x] Synthetic sample strategy defined
- [x] Source candidates identified (A, B, C above)
- [x] Provenance tracking procedure documented
- [x] Corpus plan drafted
- [x] Normalization layer dependency noted (TC-0012)
- [x] Full normalization completed (run025): text.txt, pages.jsonl, citations.yaml, G-NORM-001 resolved
- [x] Spec section references verified against normalized text (run025)
- [ ] Gate 3 execution prompt issued by human
- [ ] Samples created/acquired
- [ ] Provenance entries confirmed
- [ ] Independent agent verification sprint (DEC-034)
- [ ] Gate 3 human approval

---

## Gate 3 Sign-off

**Reviewed by:** (to be filled at Gate 3)
**Review date:** (to be filled)
**All provenance entries confirmed:** (yes/no)
**Notes:** (to be filled)

---

## Planning History

- **run017 (2026-05-04):** Skeleton created after Gate 1 approval.
- **run023 (2026-05-05):** Gate 2 status updated to PASSED.
- **run024 (2026-05-05):** Corpus plan drafted. Sample requirement types defined, blocked rules, synthetic strategy, candidate sources, provenance procedure. Normalization layer dependency noted. No samples acquired.
- **run025 (2026-05-05):** Full normalization completed (pdfminer.six 20260107). Extracted text.txt (2,160,370 chars), pages.jsonl (782 pages), citations.yaml (194 section refs, 35 external refs). Spec section references updated with verified sections from normalized text. G-NORM-001 resolved.
