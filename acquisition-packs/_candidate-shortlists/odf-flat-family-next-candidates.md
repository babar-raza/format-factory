---
artifact_id: odf-flat-family-next-candidates
artifact_type: candidate-shortlist
path: acquisition-packs/_candidate-shortlists/odf-flat-family-next-candidates.md
visibility: internal
publish_allowed: false
generated_by: claude
generated_at: "2026-05-07"
notes: "CANDIDATE-ONLY — no Gate 1 approval. Created run038. Must be independently verified before any new format Gate 1 scoring begins."
---

# ODF Flat Family Next-Format Candidates

**CANDIDATE-ONLY DOCUMENT**

This document evaluates likely next-format candidates for acquisition after FODS Gate 6 completes. **No format in this document has passed Gate 1. No official registry entry has been created. No acquisition pack has been started.** This is a planning document only.

**Created:** 2026-05-07 (run038)
**Authorized by:** run038 execution prompt (human-authorized candidate shortlist only)

---

## Why Evaluate Now

FODS Gate 6 is blocked on LibreOffice installation. While Gate 6 remains blocked, evaluating potential next formats provides:
1. A clear recommended next candidate when Gate 6 unblocks and completes.
2. Documentation of pipeline reuse potential (reduces future acquisition cost).
3. A shortlist ready for independent verification before any Gate 1 scoring prompt.

---

## Pipeline Reuse from FODS

The FODS acquisition has produced assets that can be reused for ODF flat family formats:

| Asset | Reusable For | Status |
|---|---|---|
| ODF 1.3 spec cache (`.local/spec-cache/fods/1.3/`) | All ODF formats (FODT, FODP, FODG) | YES — same spec |
| Spec normalization (text.txt, pages.jsonl, chunks.jsonl) | All ODF formats | YES — same spec |
| Spec Navigation Layer (sections.jsonl, chunk index) | All ODF formats | YES — same spec |
| Oracle provider (LibreOffice) | All ODF flat variants | YES — same tool |
| Evidence contract templates | All formats | YES — same system |
| Sample/prototype/model pattern | Next format | YES — adapt to new schema |
| Neutral model (Cells family) | Cells family only | PARTIAL — Words/Slides need new model |

---

## Candidate Evaluation Summary

| Candidate | Display Name | Family | Est. Score | Band | Priority |
|---|---|---|---|---|---|
| **FODT** | Flat OpenDocument Text | Words | 87-93/100 | Accept | **HIGH** |
| **FODP** | Flat OpenDocument Presentation | Slides | 82-90/100 | Accept | Medium |
| **FODG** | Flat OpenDocument Drawing | Diagram | 75-86/100 | Accept/Borderline | Low |
| **FODB** | Flat OpenDocument Database | Archive | 62-72/100 | Borderline/Defer | Defer |

Score estimates use existing project evidence (FODS pipeline + public ODF documentation). Confidence is `supported_by_existing_project_evidence` for FODT and `plausible_pending_verification` for others.

---

## Recommended Next Format: FODT

**FODT** is the recommended next acquisition candidate.

### Rationale

1. **Same legal/spec basis as FODS:** OASIS ODF 1.3 Category 1 RF — no new legal review required for spec body.
2. **Same oracle provider:** LibreOffice handles FODT natively — no new provider evaluation needed.
3. **Same spec cache:** The cached ODF 1.3 Part 2 spec covers FODT structure — no new download.
4. **Strong community demand:** FODT is widely used for version-control-friendly document authoring.
5. **Validated acquisition pipeline:** The FODS acquisition has proven all 11 gates work — FODT benefits from this proof.
6. **Estimated score 87-93/100:** Firmly in Accept band.

### New Investment Required

1. **Words-family neutral model:** A new neutral model schema for text/paragraph/style entities (Gate 5).
2. **FODT-specific samples:** 4+ synthetic FODT samples with Apache-2.0 provenance (Gate 3).
3. **FODT parser prototype:** Extend/adapt FODS parser for paragraph/style XML (Gate 4).
4. **Gate 2 spec evidence:** ODF 1.3 Part 2 (Packages) — same spec as FODS but focus on text structures.

---

## Prerequisites Before Any Gate 1 Scoring

1. This shortlist must be **independently verified** in a separate agent session (DEC-034).
2. A human must explicitly authorize Gate 1 scoring for FODT by name.
3. FODS Gate 6 does NOT need to complete before FODT Gate 1 scoring begins (pipeline allows parallel early-gate work).
4. WIP limit check: maximum 2 formats in Gates 4-6 simultaneously — FODS is currently in Gate 6 (blocked), so one slot is available.

---

## What This Document Does NOT Do

- Does NOT add any format to `registry/format-registry.yaml`
- Does NOT approve Gate 1 for any format
- Does NOT create any acquisition pack under `acquisition-packs/{format}/`
- Does NOT download any new spec
- Does NOT create any samples or parser code
- Does NOT authorize any Gate 1 execution prompt

---

## Authoritative Data Source

Full candidate data (scores, pipeline reuse fields, per-candidate notes) is in:
`registry/candidates/odf-flat-family-shortlist.yaml`

This document is a human-readable summary only.
