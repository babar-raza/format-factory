# ODT Parser Notes
# Format: OpenDocument Text (.odt)
# Gate: 4 — Parser Planning
# Sprint: FORMAT-FACTORY-R25-AI-PHASE1-GATE4-FORWARD-TRAIN-AND-R24-METADATA-SYNC-001
# Date: 2026-05-18
# Authorization: Gate 4 prototype planning only — no production source authorized

## Container Structure

ODT is a ZIP archive (ODF 1.3):
- `mimetype` — first entry, stored (not compressed), value: `application/vnd.oasis.opendocument.text`
- `META-INF/manifest.xml` — file listing
- `content.xml` — main document content
- `styles.xml` — paragraph/character styles
- `meta.xml` — document metadata (optional)

## Python stdlib parsing approach

```python
import zipfile
import xml.etree.ElementTree as ET

NS = {
    'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
    'text':   'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
}

def parse_odt(path):
    with zipfile.ZipFile(path) as zf:
        root = ET.fromstring(zf.read('content.xml'))
    body = root.find('.//office:body/office:text', NS)
    paragraphs = []
    for elem in body:
        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
        if tag == 'p':
            text = ''.join(elem.itertext())
            paragraphs.append({'type': 'paragraph', 'text': text})
        elif tag == 'h':
            level = elem.get('{urn:oasis:names:tc:opendocument:xmlns:text:1.0}outline-level', '1')
            text = ''.join(elem.itertext())
            paragraphs.append({'type': 'heading', 'level': int(level), 'text': text})
        elif tag == 'list':
            items = [i.findtext('.//text:p', namespaces=NS) or ''
                     for i in elem.findall('.//text:list-item', NS)]
            paragraphs.append({'type': 'list', 'items': items})
    return paragraphs
```

## Key Limitations for G4 Prototype

1. Embedded images/objects — extract text only; skip draw: elements
2. Tables in text (`table:table` within office:text) — flatten to text
3. Footnotes/endnotes (`text:note`) — optionally include or skip
4. Change tracking (`text:tracked-changes`) — use display text, ignore markup
5. Unicode: UTF-8 throughout; no special handling needed

## Gate 4 Prototype Scope

| Feature | Planned |
|---------|---------|
| Paragraph text extraction | YES |
| Heading detection + level | YES |
| List item extraction | YES |
| UTF-8/Unicode text | YES |
| Table content (flattened) | YES |
| Embedded images | NO (skip) |
| Footnotes | NO (skip in prototype) |
| Styles/formatting | NO (phase 2) |
| Write/save | NO (phase 2) |

## Status
gate_4_parser_notes: ready_for_prototype_planning
production_source_authorized: false
