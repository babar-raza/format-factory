# Acquisition Pack Standardization Report
Sprint: FORMAT-FACTORY-R12-ACQUISITION-ENGINE-IV-AND-ZST-GOVERNED-READINESS-SWARM-001
Lane: F
Date: 2026-05-14
Status: COMPLETE

> **PLANNING ARTIFACT ONLY** — No new acquisition packs created.
> No specs fetched. No internet access. Simulation only.

---

## Current Acquisition Pack Structure

### Template: acquisition-packs/_template/

```
acquisition-packs/_template/
├── pack.yaml           -- Format metadata, legal, scoring, stage status
├── legal-notes.md      -- Legal classification and provenance notes
├── parser-notes.md     -- Parser approach, complexity, oracle notes
├── sample-sources.md   -- Open-license sample file sources
└── spec-evidence.md    -- Spec evidence: URL, hash, access date
```

### Active Packs:
- `acquisition-packs/fods/` — Complete (Gates 1-10 PASSED)
- `acquisition-packs/fodt/` — Complete (Gates 1-10 PASSED)

### Family Definitions:
- `acquisition-packs/_families/` — Format family groupings

---

## Pack Governance Rules (Established / Confirmed)

### Rule PK-001: Pack Creation Requires Gate 1 Approval
> "Do not create an acquisition pack until Gate 1 has been passed for this format."
— `acquisition-packs/_template/pack.yaml`, line 5

Gate 1 is the scoring/legal classification gate. No pack may be created for ZST or any
other TIER_A candidate until Gate 1 is explicitly approved by a human reviewer.

### Rule PK-002: Pack Completeness Requirements Per Gate

| Pack Component | Required By Gate | Status for Candidates |
|----------------|-----------------|----------------------|
| pack.yaml | Gate 1 | NOT_STARTED for all candidates |
| spec-evidence.md | Gate 2 | NOT_STARTED |
| legal-notes.md | Gate 2 | NOT_STARTED |
| sample-sources.md | Gate 3 | NOT_STARTED |
| parser-notes.md | Gate 4 | NOT_STARTED |
| oracle_tool | Gate 6 | NOT_STARTED |
| tier_map / delivery_plan | Gate 9 | NOT_STARTED |

### Rule PK-003: Pack Visibility is evidence-only
All acquisition packs use `visibility: evidence-only` and `publish_allowed: false`.
Pack contents are internal governance artifacts, not public documentation.

### Rule PK-004: Pack Source Hash Required
Each `pack.yaml` requires `source_hash: sha256:<hash>` for the spec document.
No pack may claim spec evidence without a verifiable hash.

### Rule PK-005: No Commercial Allowed Without Gate 11
`commercial_allowed: false` in pack.yaml is the default and must remain false
until Gate 11 is approved by a human reviewer (Babar Raza or designate).

---

## Pack Readiness Scoring

A pack is considered complete for a gate when all components required by that
gate are in `status: complete`.

### Pack Readiness Score Formula (Simulation)

```
pack_readiness = completed_components / required_components_for_current_gate
```

| Score Range | Status | Implication |
|-------------|--------|-------------|
| 0.0 | PACK_NOT_STARTED | No components created |
| 0.01–0.49 | PACK_IN_PROGRESS | Some components present |
| 0.50–0.99 | PACK_NEARLY_COMPLETE | Most components present |
| 1.00 | PACK_GATE_READY | All required components complete |

**FODS/FODT current score: 1.00 (PACK_GATE_READY through Gate 10)**

### Candidate Pack Readiness (All TIER_A)
All TIER_A candidates: `pack_readiness = 0.0 (PACK_NOT_STARTED)` — no packs exist.
This is correct and expected. No packs should exist before Gate 1.

---

## Future Candidate Pack Template Rules

When ZST (or any future candidate) receives Gate 1 authorization:

### Step 1: Initialize Pack
```
cp -r acquisition-packs/_template/ acquisition-packs/zst/
```
Replace all `<format-id>` placeholders with `zst`.

### Step 2: Populate pack.yaml
Required fields to populate at Gate 1:
- `format_id: zst`
- `display_name: Zstandard Compressed File`
- `family: archive`
- `extensions: [.zst]`
- `mime_type: application/zstd`
- `spec_body: IETF`
- `spec_version: RFC 8878`
- `legal_category: 1` (Open Standard RF)
- `scoring.gate_1_approved_by: <human name>`
- `scoring.gate_1_approved_date: <ISO-8601>`

### Step 3: Populate spec-evidence.md (Gate 2)
- RFC 8878 URL, access date, sha256 hash of downloaded document
- Note: spec must be retrieved and cached locally BEFORE hash can be recorded

### Step 4: legal-notes.md (Gate 2)
- Confirm IETF Trust license for RFC implementation
- Confirm BSD license path for reference implementation (not GPLv2)
- No known patent claims

### Step 5: sample-sources.md (Gate 3)
- Linux kernel source packages (use .zst compressed tarballs)
- npm package tarballs (modern packages use .zst)
- Provenance: confirm open-license, document source URL and access date

---

## Pack Evidence Expectations

Each pack must ultimately contain:

| Artifact | Purpose | Gate |
|----------|---------|------|
| pack.yaml | Master metadata | 1 |
| spec-evidence.md | Spec provenance and hash | 2 |
| legal-notes.md | Legal clearance | 2 |
| sample-sources.md | Sample file provenance | 3 |
| parser-notes.md | Parser design decisions | 4 |
| oracle_tool | Test oracle specification | 6 |

---

## Standardization Gaps Found

### Gap PK-STANDARD-001: No Acquisition Risk Field in pack.yaml Template
The existing `pack.yaml` template does not include `acquisition_risk_classification`.
R12 Lane D added this field to `format-onboarding.schema.yaml`.
**Recommendation:** Add `acquisition_risk_classification: NOT_ASSESSED` to `pack.yaml` template in a future sprint.
**Classification: NON-BLOCKING** — template improvement, not a current defect.

### Gap PK-STANDARD-002: No Oracle Classification Field in pack.yaml Template
The existing template has `oracle_tool.name` and `oracle_tool.version` but not `oracle_classification` (ROUND_TRIP / SCHEMA_VALIDATE etc.).
**Recommendation:** Add `oracle_classification: NOT_ASSESSED` to template.
**Classification: NON-BLOCKING.**

### Gap PK-STANDARD-003: No Spec Normalization Status Field
`pack.yaml` template does not track `spec_normalization_status`.
**Recommendation:** Add `spec_normalization_status: NOT_STARTED` as a trackable field.
**Classification: NON-BLOCKING.**

---

## Summary

The existing acquisition pack structure is sound. FODS and FODT packs demonstrate
the complete lifecycle through Gate 10. The template is sufficient for future formats.
Three standardization gaps were found; all are non-blocking improvements.

No new acquisition packs created (Gate 1 not yet approved for any TIER_A candidate).

**ACQUISITION_PACK_STANDARDIZATION_STATUS: REVIEW_COMPLETE_3_NON_BLOCKING_GAPS_FOUND**
