# FODG Gate 2 Spec Evidence
Sprint: FORMAT-FACTORY-R19-HIGH-THROUGHPUT-ACQUISITION-TRAIN-001
Date: 2026-05-16
Gate: 2 — Spec Retrieval (Fast-Path)

## Fast-Path Basis

FODG uses the same governing specification as FODS, FODT, and FODP:
**ODF 1.3 Part 3: Open Document Schema (OASIS)**

The spec is already cached from FODS/FODT Gate 2 at:
`.local/spec-cache/fods/1.3/OpenDocument-v1.3-os-part3-schema.pdf`

No new spec download is required. The FODG flat-XML format is defined within the
same ODF 1.3 schema; FODG files are drawing documents conforming to the
`application/vnd.oasis.opendocument.graphics-flat-xml` MIME type.

## Spec Record

| Field | Value |
|-------|-------|
| Spec name | Open Document Format v1.3 — Part 3: Open Document Schema |
| Publisher | OASIS |
| Version | ODF 1.3 |
| Status | OASIS Standard (os) |
| Cache path | `.local/spec-cache/fods/1.3/` |
| SHA-256 | sha256:92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066 |
| Download date | 2026-05-04 |
| Source URL | https://docs.oasis-open.org/office/OpenDocument/v1.3/os/part3-schema/OpenDocument-v1.3-os-part3-schema.pdf |
| MIME type | application/pdf |

## FODG-Specific Relevance

- FODG is a flat-XML encoding of ODG (OpenDocument Drawing/Graphics)
- File structure: single XML file, no ZIP container
- Root element: `<office:document>` with `office:mimetype="application/vnd.oasis.opendocument.graphics-flat-xml"`
- Governed by ODF 1.3 schema — same schema governs FODS (spreadsheet), FODT (text), FODP (presentation)
- No separate spec exists; ODF 1.3 covers all flat-XML variants
- Drawing semantics: `<draw:page>` elements for slides/pages; `<draw:*>` shape elements

## Fast-Path Justification

1. Same spec body (OASIS), same version (1.3), same legal category (1)
2. Spec already locally cached with verified SHA-256
3. No new internet retrieval needed
4. FODS Gate 2 cache is authoritative for FODG Gate 2

GATE_2_SPEC_EVIDENCE: FAST_PATH_COMPLETE (shared ODF 1.3 cache)
