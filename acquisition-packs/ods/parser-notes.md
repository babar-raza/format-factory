# ODS Parser Notes
# Format: OpenDocument Spreadsheet (.ods)
# Gate: 4 — Parser Planning
# Sprint: FORMAT-FACTORY-R25-AI-PHASE1-GATE4-FORWARD-TRAIN-AND-R24-METADATA-SYNC-001
# Date: 2026-05-18
# Authorization: Gate 4 prototype planning only — no production source authorized

## Container Structure

ODS is a ZIP archive (ODF 1.3):
- `mimetype` — first entry, stored (not compressed), value: `application/vnd.oasis.opendocument.spreadsheet`
- `META-INF/manifest.xml` — file listing
- `content.xml` — main spreadsheet content
- `styles.xml` — cell/page styles
- `meta.xml` — document metadata (optional)
- `settings.xml` — application settings (optional)

## Python stdlib parsing approach

```python
import zipfile
import xml.etree.ElementTree as ET

NS = {
    'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
    'table':  'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
    'text':   'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
}

def parse_ods(path):
    with zipfile.ZipFile(path) as zf:
        root = ET.fromstring(zf.read('content.xml'))
    spreadsheet = root.find('.//office:spreadsheet', NS)
    sheets = []
    for sheet in spreadsheet.findall('table:table', NS):
        name = sheet.get('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}name')
        rows = []
        for row in sheet.findall('table:table-row', NS):
            cells = []
            for cell in row.findall('table:table-cell', NS):
                text = cell.findtext('.//text:p', default='', namespaces=NS)
                cells.append(text)
            rows.append(cells)
        sheets.append({'name': name, 'rows': rows})
    return sheets
```

## Key Limitations for G4 Prototype

1. Repeated cells (`table:number-columns-repeated`) must be expanded
2. Formulas in `office:value-type="formula"` — read display value only
3. Merged cells (`table:table-cell` with `table:number-columns-spanned`) — unmerge
4. Dates stored as ISO 8601 in `office:date-value` attribute
5. Max rows/cols guard: ODS spec allows 1048576 rows × 1024 cols (LibreOffice defaults)

## Gate 4 Prototype Scope

| Feature | Planned |
|---------|---------|
| Multi-sheet read | YES |
| Cell text extraction | YES |
| Sheet names | YES |
| Numeric values | YES |
| Repeated column expansion | YES |
| Formula display values | YES |
| Merged cell handling | NO (phase 2) |
| Styles/formatting | NO (phase 2) |
| Write/save | NO (phase 2) |

## Status
gate_4_parser_notes: ready_for_prototype_planning
production_source_authorized: false
