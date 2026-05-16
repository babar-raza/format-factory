# R17 Gate 1 Candidate Packets
Sprint: FORMAT-FACTORY-R17-R16-CLOSURE-VERIFY-ZST-GATE4-PLANNING-AND-MULTI-FORMAT-GATE1-SWARM-001
Date: 2026-05-16
Gate: 6 — Multi-format Gate 1 intake

## Status: PLANNING ONLY — No Gate 1 approvals granted here

DEC-034 IV required before any Gate 1 passes. This document is Gate 1 audit packet evidence.

---

## FODP — Flat OpenDocument Presentation

| Field | Value |
|-------|-------|
| format_id | fodp |
| display_name | Flat OpenDocument Presentation |
| extensions | .fodp |
| mime_type | application/vnd.oasis.opendocument.presentation-flat-xml |
| spec_body | OASIS |
| spec_version | ODF 1.3 |
| legal_category | 1 (OASIS RF) |
| fast_path_eligible | true |
| aspose_support | NEEDS_AUDIT (likely Aspose.Slides) |
| pipeline_reuse | HIGH — same spec as FODS/FODT |
| estimated_score | 8.5-8.8 |
| gate_1_status | NOT_STARTED |
| recommended_batch | FODP + FODG together |
| prerequisites | Aspose audit; DEC-034 IV of scoring; Conway R9 stable |

---

## FODG — Flat OpenDocument Drawing

| Field | Value |
|-------|-------|
| format_id | fodg |
| display_name | Flat OpenDocument Drawing |
| extensions | .fodg |
| mime_type | application/vnd.oasis.opendocument.graphics-flat-xml |
| spec_body | OASIS |
| spec_version | ODF 1.3 |
| legal_category | 1 (OASIS RF) |
| fast_path_eligible | true |
| aspose_support | NEEDS_AUDIT (likely Aspose.Diagram) |
| pipeline_reuse | HIGH — same spec as FODS/FODT |
| estimated_score | 8.2-8.5 |
| gate_1_status | NOT_STARTED |
| recommended_batch | FODG + FODP together |
| prerequisites | Aspose audit; DEC-034 IV of scoring; Conway R9 stable |

---

## ORA — OpenRaster

| Field | Value |
|-------|-------|
| format_id | ora |
| display_name | OpenRaster |
| extensions | .ora |
| mime_type | image/openraster |
| spec_body | freedesktop.org (community) |
| spec_version | OpenRaster 0.0.3 (informal) |
| legal_category | 2 (permissive community spec) |
| fast_path_eligible | false |
| aspose_support | NEEDS_AUDIT |
| pipeline_reuse | MEDIUM (ZIP handling; PNG; XML) |
| estimated_score | 6.5-7.0 |
| gate_1_status | NOT_STARTED |
| prerequisites | Aspose audit; confirm spec completeness |

---

## Gnumeric — Gnumeric Spreadsheet

| Field | Value |
|-------|-------|
| format_id | gnumeric |
| display_name | Gnumeric Spreadsheet |
| extensions | .gnumeric, .gnm |
| mime_type | application/x-gnumeric |
| spec_body | GNOME Project (open source) |
| spec_version | Gnumeric XML format (GNOME documentation) |
| legal_category | 2 (permissive OSS — GPL application, open format) |
| fast_path_eligible | false |
| aspose_support | NEEDS_AUDIT |
| pipeline_reuse | MEDIUM (gzip + XML) |
| r11_score | 8.75 (ACQUISITION_READY) |
| estimated_score | 8.0-8.5 |
| gate_1_status | NOT_STARTED |
| prerequisites | DEC-034 IV of Gate 1 scoring; Aspose audit |

---

## ABW — AbiWord Document

| Field | Value |
|-------|-------|
| format_id | abw |
| display_name | AbiWord Word Processing Document |
| extensions | .abw, .abw.gz, .zabw |
| mime_type | application/x-abiword |
| spec_body | AbiSource Project (open source) |
| spec_version | AWML 1.0 (outdated DTD) |
| legal_category | 2 (permissive OSS) |
| fast_path_eligible | false |
| aspose_support | NEEDS_AUDIT |
| pipeline_reuse | MEDIUM (XML patterns from FODT) |
| r11_score | 8.75 (ACQUISITION_READY) |
| estimated_score | 7.5-8.0 |
| gate_1_status | NOT_STARTED |
| constraints | Outdated DTD; reference implementation may be needed |
| prerequisites | DEC-034 IV of Gate 1 scoring; Aspose audit |

---

## dnumber / .numbers — Identity Note and Rejection

| Field | Value |
|-------|-------|
| original_identifier | dnumber |
| resolved_identity | Apple Numbers (.numbers) — high confidence |
| extensions | .numbers |
| mime_type | application/x-iwork-numbers-sffnumbers |
| spec_body | Apple Inc. (no public spec) |
| legal_category | 5 (proprietary, reverse-engineered binary, no public spec) |
| gate_1_result | AUTOMATIC_REJECT |

### Identity Resolution Evidence

- Web searches for ".dnumber file format extension" return only Apple Numbers (.numbers) results
- No file format database contains a ".dnumber" extension
- Sprint prompt explicitly pairs "dnumber / .numbers" — indicates same candidate
- Format uses IWA (iWork Archive) files: Protocol Buffers + ZIP container
- Apple has never published an official format specification
- Available documentation is from reverse engineering only (no permission granted)

### Rejection Basis

Per _scoring-model.md:
> "Legal Category 5 (reverse-engineered binary): reject regardless of other scores."
> "Score 0 on the legal safety dimension: automatic reject."

Apple Numbers falls squarely in Category 5: proprietary binary, no public spec,
no implementation permission from rights holder.

**Status: AUTOMATIC_REJECT — no Gate 1 evaluation proceeds**

If "dnumber" does NOT mean Apple Numbers, human must provide the correct identity.

---

## Batch Recommendations

| Batch | Formats | Trigger |
|-------|---------|---------|
| Batch A | FODP + FODG | After Conway R9 stable; Aspose audit |
| Batch B | Gnumeric + ABW | DEC-034 IV of scoring; Aspose audit; can parallel ZST Gate 5 |
| Single | ORA | After Aspose audit; lower priority |
| Rejected | dnumber/.numbers | Automatic reject — no batch needed |
