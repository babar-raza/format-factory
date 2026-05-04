---
artifact_id: <format-id>-sample-sources-v1
artifact_type: acquisition-pack
path: acquisition-packs/<format-id>/sample-sources.md
format_id: <format-id>
product_family: <cells|words|slides|imaging|diagram|archive>
visibility: evidence-only
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: <human|claude>
generated_at: <ISO-8601>
reusable: true
refresh_policy:
  trigger: manual
  max_age_days: 180
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: Gate 3 planning artifact. Lists candidate sample sources before acquisition. Actual provenance records go in samples/_provenance.yaml.
---

# Sample Sources — [Format Name]

**Format ID:** `<format-id>`
**Gate:** 3
**Status:** Not started

---

## Purpose

This document records the candidate sample sources evaluated during sample acquisition. It is a working document for Gate 3 planning. The authoritative provenance records for acquired samples are in `samples/_provenance.yaml`. This document captures the research process: what sources were found, why some were selected and others rejected.

---

## Sample Requirements

The minimum corpus for Gate 3 must include:

| Sample Type | Description | Status |
|---|---|---|
| Minimal valid | Smallest valid file for this format; ideally hand-crafted | Needed |
| Empty / trivial | Empty document, empty spreadsheet, or similarly trivial file | Needed |
| Core data | File containing all major data structures (cells + styles, text + paragraphs, etc.) | Needed |
| Edge case | File that exercises a known edge case: empty rows, special characters, null values, very long strings | Needed |

Preference order for sample licensing: (1) Created specifically for this project (owned by project), (2) CC0 / public domain, (3) CC-BY, (4) CC-BY-SA, (5) Apache 2.0 or MIT from open-source projects.

---

## Candidate Sources

### Source 1: [Source Name]

| Field | Value |
|---|---|
| URL | |
| License | |
| Format variant | |
| File count | |
| Sample types available | |
| Acquisition status | [selected | rejected | pending] |
| Rejection reason (if rejected) | |

### Source 2: [Source Name]

(repeat as needed)

---

## Created Samples

If no adequate open-licensed samples are available, samples may be created specifically for this project.

| Sample File | Description | Created By | License |
|---|---|---|---|
| | | | Internal / Apache 2.0 |

---

## Rejected Sources

| Source URL | License | Rejection Reason |
|---|---|---|
| | CC-BY-ND | No-derivatives license; incompatible |
| | Unknown | License unconfirmed; blocked until confirmed |

---

## Final Corpus Plan

Before Gate 3 is requested, confirm the corpus plan:

| Sample File | Source | License | Provenance Entry Created? |
|---|---|---|---|
| `samples/by-format/<format-id>/minimal.ext` | | | No |
| `samples/by-format/<format-id>/empty.ext` | | | No |
| `samples/by-format/<format-id>/core-data.ext` | | | No |
| `samples/by-format/<format-id>/edge-case.ext` | | | No |

---

## Gate 3 Sign-off

**Reviewed by:** (to be filled)
**Review date:** (to be filled)
**All provenance entries confirmed:** (yes/no)
**Notes:** (to be filled)
