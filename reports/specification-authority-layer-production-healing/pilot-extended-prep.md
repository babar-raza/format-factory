# Extended Pilot Preparation — Gnumeric and FODS/FODT
Sprint ID: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-BLOCKER-PLAN-HEALING-001

## Scope

Extended prep = source registration + fetch-plan only.
Full lifecycle pilots (parse, normalize, extract, verify, context pack) run during MWP execution.

---

## Gnumeric

### Source Registration

```json
{
  "source_id": "src-gnumeric-001",
  "url": "https://gnumeric.org/",
  "format_id": "gnumeric",
  "license": "OPEN_SOURCE",
  "license_confirmed": true,
  "registration_date": "2026-06-04",
  "approved_by": "FORMAT_FACTORY_SAL_HEALING_SPRINT",
  "status": "registered_source",
  "notes": "Gnumeric is GNU GPL v2. Format documentation available via project."
}
```

**License assessment:**
- Gnumeric is GNU GPL v2 (open source)
- Format specification available via Gnumeric project documentation
- **LICENSE_CONFIRMED: YES — OPEN_SOURCE**
- Format is XML-based (.gnumeric = gzip-compressed XML)

### Fetch Plan

**Primary spec source:**
- Gnumeric XML format documentation: https://gitlab.gnome.org/GNOME/gnumeric/-/tree/master/doc
- Or: Gnumeric source code XML schema files (definitive format definition)

**Fetch steps:**
1. Clone/download Gnumeric source or documentation
2. Locate XML schema files (doc/ directory or .xsd files in source)
3. Ingest schema + format description as raw_snapshot in SpecVault
4. Parse as project_docs format

**Expected parser output sections:**
- Workbook structure (wb:Workbook element)
- Sheet model (gnm:Sheet element)
- Cell model (gnm:Cell element with ValueType)
- Style model (gnm:Style)

**License caveat:** GPL v2 source code; format documentation and spec are freely usable.
Format itself (the .gnumeric XML structure) is not licensed — it is a data format.

---

## FODS/FODT (ODF Flat Format)

### Source Registration

```json
{
  "source_id": "src-odf-001",
  "url": "https://docs.oasis-open.org/office/OpenDocument/v1.3/os/",
  "format_id": "odf",
  "license": "PUBLIC_SPEC",
  "license_confirmed": true,
  "registration_date": "2026-06-04",
  "approved_by": "FORMAT_FACTORY_SAL_HEALING_SPRINT",
  "status": "registered_source",
  "notes": "OASIS OpenDocument Format (ODF) v1.3 — public specification. FODS (Flat ODF Spreadsheet) and FODT (Flat ODF Text Document) are single-file XML variants of ODF."
}
```

**License assessment:**
- OASIS ODF standard is a public specification (OASIS Open)
- Available at no cost; freely implementable
- **LICENSE_CONFIRMED: YES — PUBLIC_SPEC**
- No quarantine needed

### Fetch Plan

**Primary spec sources:**
1. ODF 1.3 Part 1 (Introduction): https://docs.oasis-open.org/office/OpenDocument/v1.3/os/part1-introduction/
2. ODF 1.3 Part 2 (Packages): https://docs.oasis-open.org/office/OpenDocument/v1.3/os/part2-packages/
3. ODF 1.3 Part 3 (Schema): https://docs.oasis-open.org/office/OpenDocument/v1.3/os/part3-schema/
4. ODF 1.3 Part 4 (Recalculated Formula): https://docs.oasis-open.org/office/OpenDocument/v1.3/os/part4-formula/

**FODS/FODT specific:**
- FODS = Flat ODF Spreadsheet = ODF spreadsheet content as single XML file (no zip)
- FODT = Flat ODF Text = ODF text document content as single XML file (no zip)
- Root element for FODS: `<office:document>` with `office:mimetype="application/vnd.oasis.opendocument.spreadsheet"`
- Root element for FODT: `<office:document>` with `office:mimetype="application/vnd.oasis.opendocument.text"`

**Fetch steps:**
1. Download ODF 1.3 Part 3 (Schema) — most relevant for FODS/FODT structure
2. Download FODS/FODT specific schema sections (table:, text:, draw: namespaces)
3. Ingest as raw_snapshot in SpecVault
4. Parse as odf_spec format

**Expected parser output sections:**
- Spreadsheet content model (table:table, table:table-row, table:table-cell)
- Text content model (text:p, text:h, text:body)
- Cell value types (office:value-type: float, string, date, boolean, time)
- Style model (style:style, style:paragraph-properties)

---

## Fetch-Plan Status

| Format | Source ID | License | Fetch Steps | Ready for MWP? |
|--------|-----------|---------|------------|----------------|
| Gnumeric | src-gnumeric-001 | OPEN_SOURCE | 4 steps | YES — register + fetch during MWP |
| FODS/FODT | src-odf-001 | PUBLIC_SPEC | 4 steps | YES — register + fetch during MWP |
