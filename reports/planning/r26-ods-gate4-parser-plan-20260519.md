# ODS Gate 4 Parser Plan
# Format: OpenDocument Spreadsheet (.ods)
# Sprint: R26
# Date: 2026-05-19
# Status: parser_plan_complete
# Authorization: PLANNING ONLY — no production source authorized

## Parser API

**Class:** `OdsParser`
**Method:** `parse(path: str) -> OdsDocument`

### OdsDocument Structure

```
OdsDocument
  sheets: list[OdsSheet]

OdsSheet
  name: str
  rows: list[OdsRow]

OdsRow
  cells: list[OdsCell]

OdsCell
  value: str | float | None
  value_type: str  # "string", "float", "date", "percentage", "currency", "boolean"
  text: str        # display text from text:p
```

## Technology

- **ZIP extraction:** Python `zipfile` (stdlib) — read `content.xml` from ODS ZIP archive
- **XML parsing:** `xml.etree.ElementTree` (stdlib) — XXE-safe by default (no external entity resolution)
- **No third-party dependencies** for core parsing

## ODS Container Structure

ODS is a ZIP archive conforming to ODF 1.3 (ISO/IEC 26300-3:2021):

| Entry | Purpose | Required |
|-------|---------|----------|
| `mimetype` | First entry, stored uncompressed: `application/vnd.oasis.opendocument.spreadsheet` | YES |
| `META-INF/manifest.xml` | File listing | YES |
| `content.xml` | Main spreadsheet content | YES |
| `styles.xml` | Cell/page styles | YES |
| `meta.xml` | Document metadata | NO |
| `settings.xml` | Application settings | NO |

## XML Element Mapping

Content XML structure for spreadsheet data:

```
office:document-content
  office:body
    office:spreadsheet
      table:table (@table:name)
        table:table-row
          table:table-cell (@office:value-type, @office:value, @office:date-value)
            text:p  (display text)
```

## ODF Namespaces

| Prefix | URI |
|--------|-----|
| `office` | `urn:oasis:names:tc:opendocument:xmlns:office:1.0` |
| `table` | `urn:oasis:names:tc:opendocument:xmlns:table:1.0` |
| `text` | `urn:oasis:names:tc:opendocument:xmlns:text:1.0` |

## Security Guards

| Guard | Limit | Rationale |
|-------|-------|-----------|
| Max ZIP archive size | 64 MiB | Prevent memory exhaustion from large files |
| Max decompressed size | 64 MiB | Zip bomb detection — reject if total decompressed exceeds limit |
| No external entity resolution | N/A | `xml.etree.ElementTree` does not resolve external entities by default |
| Max entry count | 1000 | Prevent zip bomb with many small entries |
| Mimetype validation | exact match | Reject if `mimetype` entry is absent or incorrect |

## Cell Type Handling

| `office:value-type` | Attribute | Python Type |
|---------------------|-----------|-------------|
| `string` | (text in `text:p`) | `str` |
| `float` | `office:value` | `float` |
| `date` | `office:date-value` (ISO 8601) | `str` (ISO format) |
| `percentage` | `office:value` | `float` |
| `currency` | `office:value` | `float` |
| `boolean` | `office:boolean-value` | `str` ("true"/"false") |

## Repeated Column/Row Expansion

- `table:number-columns-repeated` on `table:table-cell` — duplicate cell N times
- `table:number-rows-repeated` on `table:table-row` — duplicate row N times
- Guard: cap expansion at 1024 columns and 1048576 rows (LibreOffice ODS limits)

## Test Cases (Gate 4 Plan)

| Test Case | Sample | Expected Result |
|-----------|--------|-----------------|
| Valid single-sheet parse | `valid/minimal-spreadsheet.ods` | 1 sheet, 2 rows, mixed string+float cells |
| Valid single-cell | `valid/single-cell.ods` | 1 sheet, 1 row, 1 cell with text "A1" |
| Valid numeric row | `valid/numeric-row.ods` | 1 sheet, 1 row, 3 float cells (1.0, 2.0, 3.0) |
| Invalid truncated ZIP | `invalid/truncated.ods` | Raise `BadZipFile` or equivalent error |
| Cell type: string | synthetic | `value_type="string"`, text extracted from `text:p` |
| Cell type: float | synthetic | `value_type="float"`, numeric value from `office:value` |
| Cell type: date | synthetic | `value_type="date"`, ISO 8601 from `office:date-value` |
| Multi-sheet document | synthetic | Multiple `OdsSheet` objects, correct sheet names |
| Repeated columns | synthetic | `table:number-columns-repeated` expanded correctly |
| ZIP size guard | synthetic >64MiB | Reject before parsing |
| Missing content.xml | synthetic | Raise descriptive error |

## Prototype Scope (Gate 4)

| Feature | Included | Notes |
|---------|----------|-------|
| Multi-sheet read | YES | |
| Cell text extraction | YES | |
| Sheet names | YES | |
| Numeric values (`office:value`) | YES | |
| Date values (`office:date-value`) | YES | ISO 8601 string |
| Repeated column expansion | YES | Capped at 1024 |
| Formula display values | YES | Read `text:p`, ignore formula |
| Merged cell handling | NO | Phase 2 |
| Styles/formatting | NO | Phase 2 |
| Write/save | NO | Phase 2 |

## Gate 4 Status

```
gate_4_status: parser_plan_complete
production_source_authorized: false
commercial_product_ready: false
implementation_authorized: false
```

## References

- ODF 1.3 Part 3 (ISO/IEC 26300-3:2021) — content schema
- ODF 1.3 Part 2 (ISO/IEC 26300-2:2021) — ZIP package format
- Parser notes: `acquisition-packs/ods/parser-notes.md`
- Sample corpus: `samples/by-format/ods/_corpus-manifest.yaml`
- Gate 3 IV report: `reports/planning/r25-ods-iv-gate4-readiness-report-20260518.md`
