---
artifact_id: fodt-spec-evidence
artifact_type: acquisition-pack-evidence
path: acquisition-packs/fodt/spec-evidence.md
format_id: fodt
product_family: words
visibility: evidence-only
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: sha256:92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066
generated_by: claude-sonnet-4-6
generated_at: "2026-05-07"
reusable: true
refresh_policy:
  trigger: spec-version-changed
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "Gate 2 spec evidence — SUPPORTED_BY_CACHED_SOURCE. SHA-256 verified run042 (2026-05-08): MATCH. Status: evidence_cached_pending_independent_verification. Fast-path declared: OASIS RF Category 1, 8/8 fast-path items met. DEC-034 independent verification required before human Gate 2 review."
---

# FODT Spec Evidence — Gate 2

**Format:** FODT — Flat OpenDocument Text
**Gate:** 2 (Spec/Legal Evidence)
**Status:** SUPPORTED_BY_CACHED_SOURCE — evidence_cached_pending_independent_verification
**Spec:** ODF 1.3 (same as FODS)
**Spec status:** REUSES_FODS_SPEC_CACHE — spec already cached, normalized, and indexed
**SHA-256 verified:** 2026-05-08 (run042) — MATCH confirmed (3rd verification)

---

## Specification Source

| Item | Value |
|---|---|
| Specification body | OASIS ODF TC |
| Specification | ODF 1.3 (OpenDocument Format v1.3) |
| Specification URL | https://docs.oasis-open.org/office/OpenDocument/v1.3/ |
| Part(s) relevant to FODT | Part 1 (Schema), Part 2 (Packages and processing model), Part 3 (Extended Schema) |
| Spec version | 1.3 (current/stable, published 2021) |
| Spec license | OASIS RF on Limited Terms (royalty-free for implementors) |

---

## Cached Specification

| Item | Value |
|---|---|
| Cache location | `.local/spec-cache/fods/1.3/` (shared with FODS — gitignored) |
| Filename | `OpenDocument-v1.3-os-part3-schema.pdf` |
| Size | 24,270,588 bytes (24.27 MB) |
| SHA-256 | `92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066` |
| Downloaded | run021 (2026-05-04) |
| SHA-256 verified | run022 (2026-05-05) — MATCH confirmed |
| Normalized | run025 — `text.txt` (2,160,370 chars), `pages.jsonl` (782 pages) |
| Section index | run026 — `sections.jsonl` (884 sections), `chunks.jsonl` (940 chunks) |
| Spec reuse basis | Same OASIS ODF 1.3 body covers both FODS (spreadsheet) and FODT (text documents) |

---

## FODT-Specific Spec Coverage

The ODF 1.3 specification covers FODT through the following sections:

| Section | Coverage |
|---|---|
| §2 (Document Structure) | Office document types including flat XML variant |
| §3 (Text Documents) | `office:text` content model, paragraphs, headings, sections |
| §4 (Spreadsheet Documents) | (FODS only — not relevant to FODT) |
| §5 (Text Content) | `text:p`, `text:h`, `text:span`, `text:list` elements |
| §14 (Tables) | Table structures within text documents |
| §15 (Drawing Shapes) | Frames, images embedded in text |
| §17 (Text Fields) | Page numbers, dates, cross-references |
| §18 (Number Styles) | Number, date, time styles |
| §19 (Automatic Styles) | Automatic-styles section and named-styles interaction |

**Note:** Detailed section mapping will be produced as part of Gate 2 evidence execution.

---

## Gate 2 Status

**Status: SUPPORTED_BY_CACHED_SOURCE — evidence_cached_pending_independent_verification**

Gate 2 spec evidence executed (run042, 2026-05-08):
- SHA-256 verified MATCH (3rd verification — run021 download, run022 verify, run042 verify)
- FODT MIME type confirmed: `application/vnd.oasis.opendocument.text-flat-xml`
- ODF 1.3 spec coverage for FODT confirmed (§2, §3, §5, §14, §15, §17, §18, §19)
- Fast-path declared: 8/8 fast-path items met (see legal-notes.md)

**Next step:** DEC-034 independent verification (TC-0031, separate execution session).
After DEC-034 PASS: status updates to `evidence_cached_pending_human_review`.

See `legal-notes.md` for legal evidence. See `gate2-planning.md` for the Gate 2 execution plan.

---

## Reuse from FODS Pipeline

The FODS Gate 2 evidence at `acquisition-packs/fods/spec-evidence.md` directly supports FODT Gate 2:
- Legal review confirmed OASIS RF for all ODF 1.3 formats (not FODS-specific)
- Spec cache is shared (no re-download needed)
- Normalization artifacts are shared (same PDF, same sections.jsonl)

Gate 2 was executed in run042 (2026-05-08). This file has been updated to `SUPPORTED_BY_CACHED_SOURCE`. DEC-034 independent verification remains pending (TC-0031).
