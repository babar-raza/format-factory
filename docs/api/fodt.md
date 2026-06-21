# FODT Python API Reference

**Package:** `aspose-format-factory-fodt`
**Version:** 0.1.0
**Format:** Flat OpenDocument Text (FODT)
**Spec:** OASIS ODF 1.3

---

## Installation

```bash
pip install aspose-format-factory-fodt
```

```python
import fodt
```

---

## Core Functions

### `parse_fodt`

```python
def parse_fodt(file_path: str | os.PathLike) -> dict[str, Any]
```

Parse a FODT file and return a document dictionary.

**Parameters:**
- `file_path` — Path to the `.fodt` file

**Returns:** Document dict with keys: `paragraphs` (list), `styles` (dict), `metadata` (dict), `odf_version` (str)

**Raises:** `FodtInputError` if file not found; `FodtParseError` if XML is malformed; `FodtSizeError` if file exceeds `MAX_FILE_BYTES`

**Example:**
```python
doc = fodt.parse_fodt("document.fodt")
print(doc["odf_version"])          # "1.3"
print(len(doc["paragraphs"]))      # number of content paragraphs
```

---

### `parse_fodt_strict`

```python
def parse_fodt_strict(file_path: str | os.PathLike) -> dict[str, Any]
```

Parse with strict validation — raises on structural warnings.

---

### `write_fodt`

```python
def write_fodt(document: dict[str, Any], file_path: str | Path) -> None
```

Write a document dict to a FODT file.

**Example:**
```python
doc = fodt.parse_fodt("input.fodt")
fodt.document_set_paragraph_text(doc, 0, "Updated paragraph")
fodt.write_fodt(doc, "output.fodt")
```

---

### `document_to_xml`

```python
def document_to_xml(document: dict[str, Any]) -> str
```

Serialize document to ODF XML string without writing to disk.

---

## Text Content Access

### `document_text_content`

```python
def document_text_content(document: dict[str, Any]) -> str
```

Return all text content as a single string (paragraphs joined with newlines).

---

### `document_paragraph_count`

```python
def document_paragraph_count(document: dict[str, Any]) -> int
```

Return total number of paragraphs including headings.

---

### `document_word_count`

```python
def document_word_count(document: dict[str, Any]) -> int
```

Return estimated word count across all text paragraphs.

---

### `document_get_paragraph_text`

```python
def document_get_paragraph_text(document: dict[str, Any], index: int) -> str
```

Get text of a paragraph by zero-based index.

---

### `document_set_paragraph_text`

```python
def document_set_paragraph_text(document: dict[str, Any], index: int, text: str) -> tuple[bool, str]
```

Set text of a paragraph. Returns `(success, message)`.

---

### `document_get_paragraph_text_by_index`

```python
def document_get_paragraph_text_by_index(document: dict[str, Any], index: int) -> str
```

Alias for `document_get_paragraph_text`.

---

### `document_get_paragraph_style_name`

```python
def document_get_paragraph_style_name(document: dict[str, Any], index: int) -> str
```

Return the style name of a paragraph at the given index.

---

### `document_get_plain_text_range`

```python
def document_get_plain_text_range(document: dict[str, Any], start: int, end: int) -> str
```

Return concatenated plain text from paragraphs in the range [start, end).

---

### `document_get_text_between_paragraphs`

```python
def document_get_text_between_paragraphs(document: dict[str, Any], start: int, end: int) -> str
```

Return text between two paragraph indices (inclusive).

---

## Paragraph Operations

### `document_append_paragraph`

```python
def document_append_paragraph(document: dict[str, Any], text: str, style: str | None = None) -> tuple[bool, str]
```

Append a new paragraph at the end of the document. Returns `(success, message)`.

---

### `document_remove_paragraph`

```python
def document_remove_paragraph(document: dict[str, Any], index: int) -> tuple[bool, str]
```

Remove a paragraph at the given index. Returns `(success, message)`.

---

### `document_remove_all_paragraphs`

```python
def document_remove_all_paragraphs(document: dict[str, Any]) -> tuple[bool, str]
```

Remove all paragraphs from the document.

---

## Heading Operations

### `document_heading_outline`

```python
def document_heading_outline(document: dict[str, Any]) -> list[dict]
```

Return a list of heading entries with level and text.

---

### `document_get_heading_count`

```python
def document_get_heading_count(document: dict[str, Any]) -> int
```

Return number of heading paragraphs.

---

### `document_get_heading_texts`

```python
def document_get_heading_texts(document: dict[str, Any]) -> list[str]
```

Return list of all heading text strings in document order.

---

### `document_heading_level_distribution`

```python
def document_heading_level_distribution(document: dict[str, Any]) -> dict[int, int]
```

Return dict mapping heading level to count.

---

### `insert_heading`

```python
def insert_heading(document: dict[str, Any], text: str, level: int, index: int | None = None) -> tuple[bool, str]
```

Insert a heading at the specified position.

---

### `remove_heading`

```python
def remove_heading(document: dict[str, Any], index: int) -> tuple[bool, str]
```

Remove a heading paragraph at the given index.

---

## Export

### `document_to_text`

```python
def document_to_text(document: dict[str, Any]) -> str
```

Export document to plain text string.

---

## Statistics

### `document_stats`

```python
def document_stats(document: dict[str, Any]) -> dict[str, Any]
```

Return aggregate statistics: paragraph count, word count, heading count, char count, formula count.

---

### `document_get_document_stats`

```python
def document_get_document_stats(document: dict[str, Any]) -> dict[str, Any]
```

Alias for `document_stats`.

---

### `document_get_char_count`

```python
def document_get_char_count(document: dict[str, Any]) -> int
```

Return total character count across all paragraphs.

---

### `document_get_word_count`

```python
def document_get_word_count(document: dict[str, Any]) -> int
```

Return estimated word count.

---

### `document_get_paragraph_count`

```python
def document_get_paragraph_count(document: dict[str, Any]) -> int
```

Return total paragraph count.

---

### `document_get_heading_count`

```python
def document_get_heading_count(document: dict[str, Any]) -> int
```

Return heading count.

---

### `document_reading_level`

```python
def document_reading_level(document: dict[str, Any]) -> dict[str, Any]
```

Return readability metrics: sentence count, avg words per sentence, Flesch-Kincaid estimate.

---

## Constants

| Name | Value | Description |
|------|-------|-------------|
| `FORMAT_ID` | `"FODT"` | Format identifier |
| `SPEC_VERSION` | `"ODF 1.3"` | ODF spec version |
| `PACKAGE_VERSION` | `"0.1.0"` | Package version |
| `MAX_FILE_BYTES` | `104857600` | File size limit (100 MB) |

---

## Exception Classes

| Class | Description |
|-------|-------------|
| `FodtError` | Base exception |
| `FodtInputError` | File not found or unreadable |
| `FodtSizeError` | File exceeds `MAX_FILE_BYTES` |
| `FodtParseError` | XML parse error or invalid FODT structure |

---

## Quick Start

```python
import fodt

# Load a FODT file
doc = fodt.parse_fodt("report.fodt")

# Inspect
print(fodt.document_paragraph_count(doc))    # total paragraphs
print(fodt.document_word_count(doc))          # word count
print(fodt.document_get_heading_texts(doc))   # list of headings

# Read a paragraph
text = fodt.document_get_paragraph_text(doc, 0)

# Edit
fodt.document_set_paragraph_text(doc, 0, "New first paragraph")
fodt.document_append_paragraph(doc, "New final paragraph")

# Save
fodt.write_fodt(doc, "report_updated.fodt")

# Export to plain text
plain = fodt.document_to_text(doc)
```
