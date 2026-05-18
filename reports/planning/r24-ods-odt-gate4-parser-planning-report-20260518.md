# R24 ODS/ODT Gate 4 Parser Planning Report
# Sprint: FORMAT-FACTORY-R24-PARALLEL-CLOSURE-REPAIR-FORWARD-TRAIN-AND-AI-PLATFORM-PLAN-001
# Date: 2026-05-18
# Gate: 4 Planning — Minimal Parser Design
# Lane: D (ODF Container Formats)

---

## Scope

This report covers Gate 4 parser planning for both ODS (OpenDocument Spreadsheet) and ODT
(OpenDocument Text). Both formats are ZIP containers sharing the ODF 1.3 spec and identical
container structure. The parser architecture is unified at the container layer.

---

## Gate 3 Baseline

Both ODS and ODT Gate 3 sample corpora were completed in R24:
- ODS: 3 valid + 1 invalid samples — see `samples/by-format/ods/`
- ODT: 3 valid + 1 invalid samples — see `samples/by-format/odt/`
- Both: Gate 3 PASS (delegated_agent_r24), awaiting_human_iv: true

---

## Container Architecture (Shared)

ODS and ODT share the same ZIP container layout (ODF Part 2):

```
<document>.ods or .odt
  mimetype              (first entry, ZIP_STORED, not deflated)
  META-INF/
    manifest.xml        (lists all component files with media types)
  content.xml           (document body)
  styles.xml            (style definitions)
  meta.xml              (document metadata: title, author, dates)
  [settings.xml]        (optional)
  [Pictures/]           (optional embedded images)
```

The `mimetype` entry MUST be the first entry in the ZIP and MUST NOT be compressed (ZIP_STORED).
This enables sniffing the format by reading bytes 38-80 of the file without a ZIP parser.

---

## Unified Container Parser Design

### Step 1: Container validation
```python
import zipfile

def open_odf_container(path, expected_mime):
    zf = zipfile.ZipFile(path)
    names = zf.namelist()
    assert names[0] == 'mimetype', "mimetype must be first entry"
    mime = zf.read('mimetype').decode('ascii').strip()
    assert mime == expected_mime, f"wrong mime: {mime}"
    assert 'META-INF/manifest.xml' in names
    assert 'content.xml' in names
    return zf
```

### Step 2: content.xml parsing
```python
import xml.etree.ElementTree as ET

NS_OFFICE = 'urn:oasis:names:tc:opendocument:xmlns:office:1.0'
NS_TABLE  = 'urn:oasis:names:tc:opendocument:xmlns:table:1.0'
NS_TEXT   = 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'

def parse_content(zf):
    data = zf.read('content.xml')
    return ET.fromstring(data)
```

### ODS-specific: cell extraction
```python
def extract_cells(root):
    body = root.find(f'.//{{{NS_OFFICE}}}spreadsheet')
    for table in body.findall(f'{{{NS_TABLE}}}table'):
        for row in table.findall(f'{{{NS_TABLE}}}table-row'):
            for cell in row.findall(f'{{{NS_TABLE}}}table-cell'):
                vtype = cell.get(f'{{{NS_OFFICE}}}value-type')
                value = cell.get(f'{{{NS_OFFICE}}}value')
                text  = ''.join(p.text or '' for p in cell.findall(f'{{{NS_TEXT}}}p'))
                yield vtype, value, text
```

### ODT-specific: paragraph extraction
```python
def extract_paragraphs(root):
    body = root.find(f'.//{{{NS_OFFICE}}}text')
    for p in body.findall(f'{{{NS_TEXT}}}p'):
        yield p.text or ''
```

---

## Security Controls

| Risk | Control | Precedent |
|------|---------|-----------|
| XML External Entity (XXE) | ElementTree does not expand external entities | All ODF parsers |
| ZIP bomb (decompression amplification) | Check ZipInfo.file_size before extraction; 64 MiB guard | gnumeric_codec.py |
| Path traversal in manifest | Assert all paths are relative; reject any containing `..` | Standard practice |
| Malformed XML | Wrap ET.fromstring in try/except ET.ParseError | Standard practice |
| Huge pixel/cell counts | Limit iteration depth; abort at 100k cells or paragraphs | New policy |

---

## Oracle Strategy

### ODS oracle
1. Create known test data (cell values and types)
2. Encode as ODS using corpus generation method (`make_ods()`)
3. Parse with Gate 4 parser
4. Assert cell values and types match expected

Round-trip test cells:
- `("string", None, "Alpha")` — string cell
- `("float", "42", "42")` — float cell
- `("float", "1", "1")` — integer-as-float

### ODT oracle
1. Create known paragraph texts (ASCII + Unicode)
2. Encode as ODT using corpus generation method (`make_odt()`)
3. Parse with Gate 4 parser
4. Assert paragraph list matches expected

Round-trip test paragraphs:
- `"Hello, world."` — ASCII
- `"Café 中文 élève"` — Unicode (Latin-1 supplement + CJK)

---

## Implementation Plan

### Files to create (Gate 4 — NOT in this sprint)
```
src/python/ods/ods_codec.py     — container parser + cell extractor
src/python/odt/odt_codec.py     — container parser + paragraph extractor
tests/python/test_ods_codec.py  — round-trip + structural tests
tests/python/test_odt_codec.py  — round-trip + structural tests
```

### Dependency policy
- Python stdlib only: `zipfile`, `xml.etree.ElementTree`, `io`
- No `odfpy`, no `lxml`, no third-party XML libraries for Gate 4 baseline
- Optional: `defusedxml` for defence-in-depth (evaluate in Gate 4 sprint)

### Reuse from existing parsers
- Size guard pattern from `src/python/gnumeric/gnumeric_codec.py` (64 MiB)
- XXE-safe pattern from `src/python/abw/abw_codec.py` (ElementTree)
- probe() function signature from ZST/FODP/FODG/Gnumeric/ABW codecs

---

## Gate 4 Prerequisites

Before Gate 4 implementation sprint:
1. Human IV of ODS Gate 1-2 (DEC-034) — `awaiting_human_iv: true`
2. Human IV of ODT Gate 1-2 (DEC-034) — `awaiting_human_iv: true`
3. Human IV of ODS Gate 3 corpus — `awaiting_human_iv: true`
4. Human IV of ODT Gate 3 corpus — `awaiting_human_iv: true`
5. Gate 4 authorized by human approver (NO GATE SELF-APPROVAL)

commercial_product_ready: false
