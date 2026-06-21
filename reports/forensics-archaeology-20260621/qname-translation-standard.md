# QName Translation Standard

**Sprint:** forensics-archaeology-20260621
**Status:** BINDING for all future product code

---

## Standard for XML-Namespace Formats (ODF: FODS, FODT, ODS, ODT, FODG, FODP)

### Namespace → Module Mapping

| Spec Namespace | Python Module | Python Folder | .NET Namespace | .NET Folder |
|---------------|--------------|--------------|----------------|------------|
| urn:...office:1.0 | src.python.{format}.spec.office | spec/office/ | FormatFactory.{Format}.Spec.Office | Spec/Office/ |
| urn:...table:1.0 | src.python.{format}.spec.table | spec/table/ | FormatFactory.{Format}.Spec.Table | Spec/Table/ |
| urn:...text:1.0 | src.python.{format}.spec.text | spec/text/ | FormatFactory.{Format}.Spec.Text | Spec/Text/ |
| urn:...style:1.0 | src.python.{format}.spec.style | spec/style/ | FormatFactory.{Format}.Spec.Style | Spec/Style/ |
| urn:...number:1.0 | src.python.{format}.spec.number | spec/number/ | FormatFactory.{Format}.Spec.Number | Spec/Number/ |

### Element Local Name → Class Name Mapping

| Spec QName | Canonical Python Class | Canonical .NET Class | Compat Facade |
|-----------|----------------------|--------------------|--------------|
| office:document | Office.Document | Office.Document | FodsDocument / FodtDocument |
| office:body | Office.Body | Office.Body | (internal only) |
| office:spreadsheet | Office.Spreadsheet | Office.Spreadsheet | (internal only) |
| table:table | Table.Table | Table.Table | FodsSheet |
| table:table-row | Table.TableRow | Table.TableRow | (no public facade needed) |
| table:table-cell | Table.TableCell | Table.TableCell | FodsCell |
| text:p | Text.Paragraph | Text.Paragraph | FodtParagraph |
| text:h | Text.Heading | Text.Heading | FodtHeading |
| text:span | Text.Span | Text.Span | (internal) |
| text:list | Text.List | Text.List | FodtList |
| text:list-item | Text.ListItem | Text.ListItem | (internal) |
| style:style | Style.Style | Style.Style | (internal) |
| number:date-style | Number.DateStyle | Number.DateStyle | (internal) |

### Rules

1. **QName → Class name:** Replace `-` with title-case. `table-cell` → `TableCell`. `table-row` → `TableRow`. `date-style` → `DateStyle`.

2. **Namespace prefix → folder:** Use the prefix word only. `table:` → `table/`. `text:` → `text/`. `office:` → `office/`.

3. **Canonical class first, facade second:**
   - ALWAYS create the canonical class in `spec/{namespace}/{element}.py` FIRST
   - THEN create the Compat/ facade that optionally inherits from it
   - NEVER create only the facade without the canonical class

4. **Facade naming rule:**
   - Use format-prefixed facade ONLY in `Compat/` directory
   - `FodsDocument`, `FodsSheet`, `FodsCell` are facades over `office:document`, `table:table`, `table:table-cell`
   - Facade class MUST have `spec_qname`, `spec_fact_ref`, `namespace_uri` attributes

5. **Repeated children → typed collection:**
   - `table:table-row` children → `FodsSheet.rows: list[FodsRow]`
   - NOT `FodsSheet.row_list` or `FodsSheet.data`

6. **Mixed content is explicit:**
   - `text:p` containing `text:span` → `Paragraph.spans: list[Span]` not `Paragraph.text_content: str`

---

## Standard for Binary/Text Formats (DIF, SYLK, CSV, ZST, XCF, Netpbm, QOI, TOML, NDJSON, TSV, ABW, Gnumeric)

These formats have no formal XML namespace. Use governed canonical names:

### Canonical Naming Pattern

```
{Format}.{RecordType}  — based on spec terminology

Examples:
  DIF → DIF.TableHeader, DIF.DataRecord, DIF.VectorsRecord
  SYLK → SYLK.DocumentHeader, SYLK.Cell, SYLK.Format, SYLK.Row
  CSV → CSV.Row, CSV.Field, CSV.Header
  ZST → ZST.Frame, ZST.Block, ZST.FrameHeader
  XCF → XCF.Image, XCF.Layer, XCF.Channel, XCF.Property
  PBM → Netpbm.BitmapImage, Netpbm.Header
  PGM → Netpbm.GrayscaleImage, Netpbm.Header
  PPM → Netpbm.PixmapImage, Netpbm.Header
  QOI → QOI.Header, QOI.Pixel, QOI.Chunk
  TOML → TOML.Document, TOML.Table, TOML.Value
```

### Registration Requirement

ALL governed canonical names MUST be registered in `registry/format-canonical-names.yaml`:

```yaml
- format_id: dif
  governed_names:
    - class_name: DIF.TableHeader
      spec_ref: "DIF spec §2.1"
      fact_ref: FACT-DIF-001  # or "pending" if SAL facts not yet created
      qname_equivalent: "dif:table-header"  # governed equivalent
```

---

## Anti-Patterns (NEVER DO)

| Anti-Pattern | Example | Why Wrong |
|-------------|---------|-----------|
| Format-prefixed primary class | `FodsDocument` as primary | Should be facade over `Office.Document` |
| Invented names without registry | `GenericCell`, `Node`, `Item` | No spec traceability |
| No spec_qname on domain class | `class DifDocument: pass` | Cannot participate in spec pipeline |
| Duplicate canonical definitions | `fods/spec/` AND `fods/fods/spec/` | Causes confusion |
| Wrong canonical name | `FodsTableCell` instead of `FodsCell` | Facade must be shorter/user-facing |

---

## Verification Command

```bash
# Check QName compliance for all Python packages
python tools/validators/qname_structure_validator.py src/python/

# Check specific format
python tools/validators/qname_structure_validator.py src/python/ --format fods
```

Expected output for compliant format: `status: COMPLIANT`
Expected output for format in progress: `status: PARTIALLY_COMPLIANT`
Blocking status: `status: NON_COMPLIANT` (new spec/ classes without spec_qname)
