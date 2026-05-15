---
artifact_id: r16-multi-format-intake-and-next-candidates
artifact_type: candidate-shortlist
path: acquisition-packs/_candidate-shortlists/r16-multi-format-intake-and-next-candidates-20260515.md
visibility: internal
publish_allowed: false
generated_by: claude
generated_at: "2026-05-15"
sprint: FORMAT-FACTORY-R16-ZST-GATE3B-CORPUS-ACQUISITION-IV-AND-MULTI-FORMAT-INTAKE-SWARM-001
notes: "CANDIDATE-ONLY — no Gate 1 approval granted. Identity survey only."
---

# R16 Multi-Format Intake and Next Candidates
Sprint: FORMAT-FACTORY-R16-ZST-GATE3B-CORPUS-ACQUISITION-IV-AND-MULTI-FORMAT-INTAKE-SWARM-001
Date: 2026-05-15

**CANDIDATE-ONLY DOCUMENT**
No format in this document has passed Gate 1. No acquisition pack has been started.
No registry entry has been created for any new format. This is a planning survey only.

---

## Purpose

Survey format identities for the candidate pipeline. These formats appear in:
- R11 planning bundle scoring (Gnumeric, ABW, ZPAQ, QOI)
- ODF flat family shortlist (FODP, FODG, FODB)
- Sprint prompt: FODP, FODG, FODB, ORA, Gnumeric, ABW, dnumber identity

---

## ODF Flat Family Candidates

### FODP — Flat OpenDocument Presentation
- **Full name:** Flat OpenDocument Presentation
- **File extension:** `.fodp`
- **MIME type:** `application/vnd.oasis.opendocument.presentation-flat-xml`
- **Spec body:** OASIS ODF 1.3 (same as FODS/FODT)
- **Description:** Single-file XML variant of ODP (OpenDocument Presentation).
  Equivalent to ODP but without the ZIP container. Used for version-control-friendly
  slide deck authoring. Full presentation schema with slides, layouts, animations, styles.
- **Aspose support:** Likely YES — Aspose.Slides handles ODP and flat variants
- **Pipeline reuse from FODS/FODT:** HIGH — same OASIS spec, same legal basis
- **R11 planning bundle score:** Not independently scored (subsumed under ODF family)
- **Gate 1 status:** NOT STARTED — candidate only
- **Recommended next step:** Include in next ODF family batch Gate 1 after FODS/FODT proof stable

### FODG — Flat OpenDocument Drawing/Graphics
- **Full name:** Flat OpenDocument Drawing
- **File extension:** `.fodg`
- **MIME type:** `application/vnd.oasis.opendocument.graphics-flat-xml`
- **Spec body:** OASIS ODF 1.3 (same as FODS/FODT)
- **Description:** Single-file XML variant of ODG (OpenDocument Drawing). Used for
  diagrams and vector graphics. Drawing schema with shapes, connectors, styles, layers.
- **Aspose support:** Likely YES — Aspose.Diagram handles drawing formats
- **Pipeline reuse from FODS/FODT:** HIGH — same spec basis
- **R11 planning bundle score:** Not independently scored
- **Gate 1 status:** NOT STARTED — candidate only
- **Priority:** Lower than FODP; diagramming use case narrower

### FODB — Flat OpenDocument Database
- **Full name:** Flat OpenDocument Database
- **File extension:** `.fodb`
- **MIME type:** `application/vnd.oasis.opendocument.base-flat-xml` (unofficial; rarely used)
- **Spec body:** OASIS ODF 1.3 Extension (database schemas less standardized)
- **Description:** Flat XML variant of ODB (OpenDocument Base/Database). Embeds
  form definitions, data connections, queries, and reports. LibreOffice Base native format.
- **Aspose support:** Unclear — database formats are niche; needs audit
- **Pipeline reuse:** Partial — same ODF spec container but database schema differs significantly
- **R11 planning bundle score:** Not independently scored
- **Gate 1 status:** NOT STARTED — candidate only
- **Priority:** DEFER — limited Aspose support evidence; niche use case

---

## Non-ODF Candidates from R11 Planning Bundle

### Gnumeric — Gnumeric Spreadsheet
- **Full name:** Gnumeric Spreadsheet
- **File extension:** `.gnumeric`
- **MIME type:** `application/x-gnumeric`
- **Spec body:** GNOME/GNUMERIC open spec (public, XML-based)
- **Description:** Gzip-compressed XML spreadsheet from the GNOME Gnumeric application.
  Well-documented XML schema with cells, formulas, styles, charts. Open spec.
  Strongly related to the spreadsheet family; cells/formulas reuse potential from FODS.
- **Aspose support:** Needs audit — Aspose.Cells does not list Gnumeric explicitly
- **R11 planning bundle score:** 8.75 (ACQUISITION_READY band)
- **License:** LGPL-2.1+ (application); XML spec is public
- **Gate 1 status:** NOT STARTED — candidate only
- **Priority:** HIGH after ZST and ODF batch

### ABW — AbiWord Document
- **Full name:** AbiWord Document
- **File extension:** `.abw`
- **MIME type:** `application/x-abiword`
- **Spec body:** AbiWord public XML spec (open source)
- **Description:** XML word processing format from the AbiWord application.
  Compressed or uncompressed XML with paragraphs, styles, revisions, metadata.
  Public schema available.
- **Aspose support:** Aspose.Words may handle ABW — needs audit
- **R11 planning bundle score:** 8.75 (ACQUISITION_READY band, tied with Gnumeric)
- **License:** GPL-2+ (application); XML spec is public
- **Gate 1 status:** NOT STARTED — candidate only
- **Priority:** HIGH — same band as Gnumeric

### ORA — OpenRaster
- **Full name:** OpenRaster Image Format
- **File extension:** `.ora`
- **MIME type:** `image/openraster`
- **Spec body:** freedesktop.org OpenRaster spec (open)
- **Description:** ZIP container holding PNG tiles, an XML stack file, and metadata.
  Used by GIMP, Krita, and other open-source image editors as interchange format.
  Clean spec with small surface area.
- **Aspose support:** Aspose.Imaging may handle ORA — needs audit
- **R13 note:** Mentioned as "Gate 5 fallback ORA" in master-plan (run R13 context)
- **Gate 1 status:** NOT STARTED — candidate only
- **Priority:** Medium — niche imaging use case

### dnumber — Format Identity Unclear
- **Full name:** Unknown — "dnumber" is not a standard format identifier
- **Possible interpretations:**
  - `.d` files (D programming language source) — not a data format
  - `.dng` (Digital Negative — Adobe raw image format) — possible
  - `.d64` (Commodore 64 disk image) — archival niche
  - `dNumber` as a format code in a third-party catalog — needs clarification
- **Status:** IDENTITY UNRESOLVED — cannot proceed to Gate 1 evaluation
- **Action required:** Human clarification needed on what "dnumber" refers to before this
  format can be added to the candidate pipeline

---

## Prioritized Candidate Queue

| Priority | Format | Band | Gate 1 Status | Blocker |
|----------|--------|------|---------------|---------|
| 1 | ZST | ACQUISITION_READY (8.95) | PASSED → Gate 3 PASSED (R16) | None — proceed to R17 |
| 2 | Gnumeric | ACQUISITION_READY (8.75) | NOT STARTED | Conway R9 proof; FODS/FODT stable |
| 3 | ABW | ACQUISITION_READY (8.75) | NOT STARTED | Same |
| 4 | FODP | Accept | NOT STARTED | ODF batch planning |
| 5 | FODG | Accept/Borderline | NOT STARTED | ODF batch planning |
| 6 | ORA | Medium | NOT STARTED | Aspose support audit |
| 7 | FODB | DEFER | NOT STARTED | Aspose support unclear |
| 8 | dnumber | UNKNOWN | BLOCKED | Identity unresolved |

---

## What This Document Does NOT Do

- Does NOT add any format to `registry/format-registry.yaml`
- Does NOT approve Gate 1 for any format
- Does NOT create acquisition packs under `acquisition-packs/{format}/`
- Does NOT download any spec
- Does NOT create any samples or parser code
- Does NOT authorize any Gate 1 execution prompt

## Next Steps

1. **ZST R17:** Gate 4 parser prototype planning (ZST-R17-GATE4-PARSER-PROTOTYPE-PLANNING.md created)
2. **ODF batch:** After FODS/FODT Conway proof stable — FODP + FODG batch Gate 1
3. **Gnumeric/ABW:** Independent Gate 1 scoring (DEC-034 required) — schedule after ZST R17
4. **dnumber:** Request human clarification on format identity before including in pipeline

MULTI_FORMAT_INTAKE_SURVEY: COMPLETE
