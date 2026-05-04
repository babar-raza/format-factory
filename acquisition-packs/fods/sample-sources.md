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
notes: "Gate 3 planning artifact. Skeleton only — not started. Lists candidate sample sources for future acquisition. Actual provenance records go in samples/_provenance.yaml."
---

# Sample Sources — Flat OpenDocument Spreadsheet (FODS)

**Format ID:** `fods`
**Gate:** 3
**Status:** Not started — skeleton created run017 after Gate 1 approval

**Gate 1 approved by:** Babar Raza (2026-05-04)
**Gate 2 status:** not_started
**Gate 3 status:** not_started

**Important:** No samples have been acquired. `samples/by-format/fods/` does not exist and must not be created until Gate 2 is passed and an explicit Gate 3 / Phase 2 sample acquisition prompt is issued.

---

## Purpose

This document records candidate sample sources for FODS sample acquisition. It is a working document for Gate 3 planning. The authoritative provenance records for acquired samples are in `samples/_provenance.yaml`. This document captures the research process: what sources were found, why some were selected and others rejected.

---

## Sample Requirements

The minimum corpus for Gate 3 must include:

| Sample Type | Description | Status |
|---|---|---|
| Minimal valid | Smallest valid FODS file; ideally hand-crafted | Needed |
| Empty / trivial | Empty spreadsheet (no cells) | Needed |
| Core data | File containing cells, multiple sheets, basic styles | Needed |
| Edge case | File with empty rows, special characters, long strings, merged cells | Needed |

Preference order: (1) Created specifically for this project (owned by project), (2) CC0 / public domain, (3) CC-BY, (4) CC-BY-SA, (5) Apache 2.0 or MIT from open-source projects.

---

## Candidate Sources

*(To be researched and documented in TC-0009 Phase 2 work.)*

### Source 1: LibreOffice Test Suite

| Field | Value |
|---|---|
| URL | (to be identified — LibreOffice source repository) |
| License | MPL 2.0 / LGPL (to be verified) |
| Format variant | FODS |
| File count | (to be determined) |
| Sample types available | (to be determined) |
| Acquisition status | pending |
| Rejection reason | |

### Source 2: Project-created minimal samples

| Field | Value |
|---|---|
| URL | N/A — created by project |
| License | Apache-2.0 (project-owned) |
| Format variant | FODS |
| File count | 4 (minimal, empty, core-data, edge-case) |
| Sample types available | All required types |
| Acquisition status | pending — creation deferred to Gate 3 |
| Rejection reason | |

---

## Final Corpus Plan

*(To be confirmed before Gate 3 is requested.)*

| Sample File | Source | License | Provenance Entry Created? |
|---|---|---|---|
| `samples/by-format/fods/minimal.fods` | TBD | TBD | No |
| `samples/by-format/fods/empty.fods` | TBD | TBD | No |
| `samples/by-format/fods/core-data.fods` | TBD | TBD | No |
| `samples/by-format/fods/edge-case.fods` | TBD | TBD | No |

---

## Gate 3 Sign-off

**Reviewed by:** (to be filled)
**Review date:** (to be filled)
**All provenance entries confirmed:** (yes/no)
**Notes:** (to be filled)
