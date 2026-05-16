# Gnumeric Gate 2 Spec Evidence
Sprint: FORMAT-FACTORY-R19-HIGH-THROUGHPUT-ACQUISITION-TRAIN-001
Date: 2026-05-16
Gate: 2 — Spec Retrieval

## Spec Retrieval Summary

Gnumeric uses a project-maintained XSD schema as its primary spec. No formal OASIS/ISO spec exists.

## Primary Spec: Gnumeric XSD Schema

| Field | Value |
|-------|-------|
| Spec name | Gnumeric XML Spreadsheet Format v10 (XSD Schema) |
| Publisher | GNOME Project |
| Version | v10 (namespace: http://www.gnumeric.org/v10.dtd) |
| Source URL | https://gitlab.gnome.org/GNOME/gnumeric/-/raw/master/gnumeric.xsd |
| Access date | 2026-05-16 |
| Retrieval status | RETRIEVED_VIA_WEBFETCH |
| Cache path | .local/spec-cache/gnumeric/v10/spec-index.yaml |

## Key XSD Facts Retrieved

- Namespace: `http://www.gnumeric.org/v10.dtd`
- Root element: `<Workbook>`
- Key elements: Version, Sheets/Sheet, Cells, Styles/StyleRegion, PrintInformation, Objects, Filters, Scenarios
- Cell value types: empty, boolean, integer, float, error, string, cellrange, array
- Schema created for: Gnumeric 1.2.2; last updated: 1.12.21 (February 2015)

## Secondary Documentation Sources

| Source | URL | Type |
|--------|-----|------|
| GNOME manual | https://gnome.pages.gitlab.gnome.org/gnumeric/manual/sect-file-formats.html | Official manual |
| GNOME source doc | https://github.com/GNOME/gnumeric/blob/master/doc/C/files-formats.xml | Source documentation |

## Format Technical Summary

- File structure: XML + gzip compression
- MIME type: application/x-gnumeric
- Extensions: .gnumeric, .gnm
- Gzip format: standard gzip (decompress to get XML)
- XML parsing: namespace-aware (gnm: prefix for Gnumeric-specific elements)
- Version field: `<Version Epoch="..." Major="..." Minor="..."/>` inside Workbook

## Spec Quality Assessment

| Criterion | Status |
|-----------|--------|
| Schema exists | YES (XSD) |
| Schema is current | PARTIALLY (last updated 2015, Gnumeric still active) |
| Format is stable | YES (format has been stable since v10) |
| Documentation quality | ADEQUATE for parsing purposes |
| Legal openness | YES (no restrictions on format parsing) |

## Gate 2 Outcome

Spec retrieval: **PASSED** — XSD schema identified and key structure retrieved.
Note: Full XSD not stored locally; spec-index.yaml captures key metadata.
The Gnumeric format is sufficiently documented for prototype development (Gate 4).

GATE_2_SPEC_EVIDENCE: PASSED (XSD schema retrieved, key structure documented)
