# QName Translation Standard

**Sprint/Run ID:** ff-archaeology-20260625

This document defines the required standard for translating spec QNames into
Format Factory source code, with examples drawn directly from the existing codebase.

---

## Core Translation Rule

**A spec QName `ns:localName` MUST map to:**

1. **Spec class:** `Ns.LocalName` → `src/python/{format}/spec/{ns}/{local_name}.py:class LocalName`
2. **Compat facade (Python):** `FormatLocalName` → `src/python/{format}/Compat/{format}_{local_name}.py`
3. **Compat facade (.NET):** `FormatLocalName` → `src/net/{format}/Compat/{FormatLocalName}.cs`
4. **Registry entry:** `shared/qname-registry/{format}.yaml` with all required fields
5. **spec_qname ClassVar:** On every authority class in production code

**What is NEVER acceptable as primary class name:**
- `FodsTableCell` as primary implementation (only as Compat facade)
- `GenericCell`, `Node`, `Item`, `Element` without spec traceability
- Any format-prefixed name in `spec/` hierarchy (only in `Compat/`)

---

## ODF Formats (FODS, FODT, ODS, ODT)

### Rule: XML Namespace → Python Module → Folder

| Spec QName | Canonical Class | Python Path | .NET Path |
|-----------|----------------|-------------|-----------|
| `office:document` | `Office.Document` | `spec/office/document.py:Document` | `Spec/Office/Document.cs` |
| `table:table` | `Table.Table` | `spec/table/table.py:Table` | `Spec/Table/Table.cs` |
| `table:table-cell` | `Table.TableCell` | `spec/table/table_cell.py:TableCell` | `Spec/Table/TableCell.cs` |
| `text:paragraph` | `Text.Paragraph` | `spec/text/paragraph.py:Paragraph` | `Spec/Text/Paragraph.cs` |
| `office:body` | `Office.Body` | `spec/office/body.py:Body` | `Spec/Office/Body.cs` |

### Compat Facade Names (CORRECT)

| Spec QName | Format | Compat Facade | Compat Path |
|-----------|--------|--------------|-------------|
| `office:document` | FODS | `FodsDocument` | `Compat/fods_document.py` |
| `table:table-cell` | FODS | `FodsCell` | `Compat/fods_cell.py` |
| `table:table` | FODS | `FodsSpreadsheet` | `Compat/fods_spreadsheet.py` |
| `text:paragraph` | FODT | `FodtParagraph` | `Compat/fodt_paragraph.py` |

### Actual Code Example (FODS — CORRECT)

```python
# src/python/fods/spec/table/table_cell.py
from typing import ClassVar

class TableCell:
    """Spec-literal class for table:table-cell."""
    spec_qname: ClassVar[str] = "table:table-cell"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    local_name: ClassVar[str] = "table-cell"
    spec_fact_ref: ClassVar[str] = "FACT-FODS-089"
    authority_only: ClassVar[bool] = True
    # No behavioral implementation — spec identity marker only
```

```python
# src/python/fods/Compat/fods_cell.py
from ..spec.table.table_cell import TableCell as SpecTableCell

class FodsCell(SpecTableCell):
    """Compat facade for FODS table cell operations."""
    spec_qname = "table:table-cell"  # Inherited, re-declared for clarity
    # May add FODS-specific behavioral methods here
```

---

## Binary / Image Formats (PBM, PGM, PPM, QOI, XCF)

### Rule: Format-Specific Prefix → Named Namespace

Since binary formats don't have XML namespaces, Format Factory creates governed canonical
names. The format name becomes the namespace prefix.

| Spec Concept | Canonical QName | Python Class | Path |
|-------------|----------------|-------------|------|
| XCF image root | `xcf:image` | `XcfImage` | `xcf_parser.py:XcfImage` |
| XCF layer | `xcf:layer` | `Layer` | `spec/layer/layer.py:Layer` |
| XCF channel | `xcf:channel` | `Channel` | `spec/layer/channel.py:Channel` |
| PBM raster | `pbm:bitmap` | `Bitmap` | `spec/bitmap/bitmap.py:Bitmap` |
| QOI image | `qoi:chunk` | `Chunk` | `spec/chunk/chunk.py:Chunk` |

### Actual Code Example (XCF — CORRECT)

```python
# src/python/xcf/xcf_parser.py
from typing import ClassVar

class XcfImage:
    """Primary domain class for XCF images."""
    spec_qname: ClassVar[str] = "xcf:image"
    spec_fact_ref: ClassVar[str] = "FACT-XCF-001"

    def __init__(self):
        self.layer_names: list[str] = []
        self.layer_count: int = 0
        self.width: int = 0
        self.height: int = 0
```

**Note:** For binary formats, the primary codec/parser class IS the domain class.
Spec hierarchy exists in `spec/layer/layer.py` etc. but the primary entry point is
the codec class itself.

---

## Text / Table Formats (CSV, DIF, NDJSON, SYLK, TOML, TSV)

### Rule: Grammar/Record Concepts → Named Namespace

| Spec Concept | Canonical QName | Python Class | Path |
|-------------|----------------|-------------|------|
| NDJSON record | `ndjson:record` | `NdjsonRecord` | `ndjson_codec.py:NdjsonRecord` (authority-only) |
| NDJSON field | `ndjson:field` | `Field` | `spec/record/field.py:Field` |
| CSV record | `csv:record` | `Record` | `spec/record/record.py:Record` |
| TSV row | `tsv:row` | `Row` | `spec/record/row.py:Row` |
| DIF data block | `dif:data` | `Data` | `spec/table/data.py:Data` |
| TOML table | `toml:table` | `Table` | `spec/table/table.py:Table` |

### Authority-Only Marker Pattern (NDJSON — CORRECT)

```python
# src/python/ndjson/ndjson_codec.py
from typing import ClassVar

class NdjsonRecord:
    """Authority-only marker for ndjson:record spec identity."""
    spec_qname: ClassVar[str] = "ndjson:record"
    spec_fact_ref: ClassVar[str] = "FACT-NDJSON-001"
    namespace_uri: ClassVar[str] = "https://ndjson.org/spec#record"
    authority_only: ClassVar[bool] = True
    # No instance behavior — identity marker only
```

### Domain Model Wrapper Pattern (CORRECT)

```python
# src/python/ndjson/models.py
from typing import ClassVar

class NdjsonDocument:
    """Domain model wrapper for NDJSON documents."""
    spec_qname: ClassVar[str] = "ndjson:record"

    def __init__(self, records: list[dict]):
        self._records = records

    @classmethod
    def from_file(cls, path: str) -> "NdjsonDocument":
        from .ndjson_codec import load_ndjson
        return cls(load_ndjson(path))

    @property
    def record_count(self) -> int:
        return len(self._records)

    @property
    def records(self) -> list[dict]:
        return self._records

    def get_record(self, index: int) -> dict:
        return self._records[index]

    def to_list(self) -> list[dict]:
        return list(self._records)
```

---

## Compression Formats (ZST)

### Rule: Frame/Block Concepts

| Spec Concept | Canonical QName | Python Class | Path |
|-------------|----------------|-------------|------|
| ZST frame | `zst:frame` | `ZstDocument` | `models.py:ZstDocument` |
| ZST magic | `zst:magic-number` | `MagicNumber` | `spec/frame/magic_number.py` |

### Domain Model Pattern (ZST — CORRECT)

```python
# src/python/zst/models.py
from typing import ClassVar

class ZstDocument:
    spec_qname: ClassVar[str] = "zst:frame"
    spec_fact_ref: ClassVar[str] = "FACT-ZST-001"

    def __init__(self, ...):
        self.compressed_size: int = ...
        self.decompressed_size: int = ...
        self.frame_count: int = ...

    @classmethod
    def from_file(cls, path: str) -> "ZstDocument": ...
```

---

## Anti-Patterns (FORBIDDEN)

### Anti-Pattern 1: Format-Prefixed Primary Class in spec/
```python
# WRONG — format prefix in spec/ hierarchy
class FodsTableCell:  # Should be TableCell
    pass
```

### Anti-Pattern 2: Generic Names Without Spec Traceability
```python
# WRONG — generic name, no spec_qname
class GenericCell:  # What spec element is this?
    pass
```

### Anti-Pattern 3: Instance Field Instead of ClassVar
```python
# WRONG — instance field, not class-level attribute
class OdsRow:
    spec_qname: str = "table:table-row"  # Must be ClassVar[str]
```

### Anti-Pattern 4: Wrong Namespace Prefix
```python
# WRONG — using abw: instead of abiword:
class AbwDocument:
    spec_qname: ClassVar[str] = "abw:document"  # Should be "abiword:document"
```

### Anti-Pattern 5: No spec_qname at All
```python
# WRONG — missing spec_qname entirely
class DifData:  # No spec identity
    def __init__(self):
        self.vectors = []
```

---

## Summary: Translation Checklist

For every new class that represents a spec concept:

- [ ] Is the class name derived from the spec element local name?
- [ ] Is `spec_qname: ClassVar[str] = "ns:element"` present?
- [ ] Is `spec_fact_ref: ClassVar[str] = "FACT-FORMAT-NNN"` present?
- [ ] Is `namespace_uri: ClassVar[str] = "..."` present?
- [ ] Is there a corresponding entry in `shared/qname-registry/{format}.yaml`?
- [ ] Is the class in the correct location (`spec/{ns}/` for primary, `Compat/` for facade)?
- [ ] Are format-prefixed names ONLY in `Compat/`?
- [ ] Does V53 pass on this class?
