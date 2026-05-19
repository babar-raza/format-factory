# ODT Gate 4 Parser Plan
# Format: OpenDocument Text (.odt)
# Sprint: R26
# Date: 2026-05-19
# Status: parser_plan_complete
# Authorization: PLANNING ONLY — no production source authorized

## Parser API

**Class:** `OdtParser`
**Method:** `parse(path: str) -> OdtDocument`

### OdtDocument Structure

```
OdtDocument
  elements: list[OdtElement]

OdtElement (union type)
  OdtParagraph
    text: str
    style_name: str | None

  OdtHeading
    text: str
    outline_level: int  # 1-6, from text:outline-level attribute
    style_name: str | None

  OdtList
    items: list[str]
```

## Technology

- **ZIP extraction:** Python `zipfile` (stdlib) — read `content.xml` from ODT ZIP archive
- **XML parsing:** `xml.etree.ElementTree` (stdlib) — XXE-safe by default (no external entity resolution)
- **No third-party dependencies** for core parsing

## ODT Container Structure

ODT is a ZIP archive conforming to ODF 1.3 (ISO/IEC 26300-3:2021):

| Entry | Purpose | Required |
|-------|---------|----------|
| `mimetype` | First entry, stored uncompressed: `application/vnd.oasis.opendocument.text` | YES |
| `META-INF/manifest.xml` | File listing | YES |
| `content.xml` | Main document content | YES |
| `styles.xml` | Paragraph/character styles | YES |
| `meta.xml` | Document metadata | NO |

## XML Element Mapping

Content XML structure for text documents:

```
office:document-content
  office:body
    office:text
      text:p (@text:style-name)         -> OdtParagraph
      text:h (@text:outline-level, @text:style-name) -> OdtHeading
      text:list                          -> OdtList
        text:list-item
          text:p                         -> list item text
```

### Element Details

- **`text:p`** — Paragraph. Text content gathered via `itertext()` to capture inline spans.
- **`text:h`** — Heading. `text:outline-level` attribute (integer 1-6) maps to heading level. Defaults to 1 if absent.
- **`text:list`** — List. Items extracted from `text:list-item/text:p`. Nested lists flattened in prototype.

## ODF Namespaces

| Prefix | URI |
|--------|-----|
| `office` | `urn:oasis:names:tc:opendocument:xmlns:office:1.0` |
| `text` | `urn:oasis:names:tc:opendocument:xmlns:text:1.0` |

## Security Guards

| Guard | Limit | Rationale |
|-------|-------|-----------|
| Max ZIP archive size | 64 MiB | Prevent memory exhaustion from large files |
| Max decompressed size | 64 MiB | Zip bomb detection — reject if total decompressed exceeds limit |
| No external entity resolution | N/A | `xml.etree.ElementTree` does not resolve external entities by default |
| Max entry count | 1000 | Prevent zip bomb with many small entries |
| Mimetype validation | exact match | Reject if `mimetype` entry is absent or incorrect |

## Test Cases (Gate 4 Plan)

| Test Case | Sample | Expected Result |
|-----------|--------|-----------------|
| Valid minimal document | `valid/minimal-document.odt` | 1 paragraph: "Hello, world." |
| Valid two paragraphs | `valid/two-paragraphs.odt` | 2 paragraphs: "First paragraph.", "Second paragraph." |
| Valid Unicode text | `valid/unicode-text.odt` | 1 paragraph with Unicode characters preserved |
| Invalid truncated ZIP | `invalid/truncated.odt` | Raise `BadZipFile` or equivalent error |
| Headings with levels | synthetic | `OdtHeading` with correct `outline_level` (1-6) |
| List extraction | synthetic | `OdtList` with correct item texts |
| Mixed content | synthetic | Paragraphs + headings + lists in correct order |
| ZIP size guard | synthetic >64MiB | Reject before parsing |
| Missing content.xml | synthetic | Raise descriptive error |
| Inline spans | synthetic | `text:span` within `text:p` merged into paragraph text |

## Prototype Scope (Gate 4)

| Feature | Included | Notes |
|---------|----------|-------|
| Paragraph text extraction | YES | Via `itertext()` |
| Heading detection + level | YES | `text:outline-level` attribute |
| List item extraction | YES | Flattened in prototype |
| UTF-8/Unicode text | YES | Native support |
| Table content (flattened) | YES | `table:table` within `office:text` — extract cell text |
| Embedded images | NO | Skip `draw:` elements |
| Footnotes | NO | Skip `text:note` in prototype |
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
- Parser notes: `acquisition-packs/odt/parser-notes.md`
- Sample corpus: `samples/by-format/odt/_corpus-manifest.yaml`
- Gate 3 IV report: `reports/planning/r25-odt-iv-gate4-readiness-report-20260518.md`
