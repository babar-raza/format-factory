# QName Translation Standard — ff-arch-20260621-001
# Required standard for Format Factory source organization

## Principle

Specifications are the source of truth.
Every source class, module, folder, and namespace MUST trace to a spec element or governed canonical name.

## Standard for ODF / XML Formats (FODS, FODT, FODG, FODP, ODS, ODT)

### Namespace Mapping

| ODF Namespace URI | Namespace Prefix | .NET Namespace/Folder | Python Module Folder |
|---|---|---|---|
| urn:oasis:names:tc:opendocument:xmlns:office:1.0 | office | Office/ | office/ |
| urn:oasis:names:tc:opendocument:xmlns:table:1.0 | table | Table/ | table/ |
| urn:oasis:names:tc:opendocument:xmlns:text:1.0 | text | Text/ | text/ |
| urn:oasis:names:tc:opendocument:xmlns:style:1.0 | style | Style/ | style/ |
| urn:oasis:names:tc:opendocument:xmlns:draw:1.0 | draw | Draw/ | draw/ |
| urn:oasis:names:tc:opendocument:xmlns:number:1.0 | number | Number/ | number/ |

### Element Naming Rule

```
spec QName (prefix:local-name) -> CamelCase (prefix:local-name -> Prefix.LocalName)

Examples:
  table:table-cell    -> Table.TableCell      (C#: class TableCell in namespace Table)
  text:p              -> Text.Paragraph        (C#: class Paragraph in namespace Text)
  text:h              -> Text.Heading
  office:document     -> Office.Document
  office:body         -> Office.Body
  style:style         -> Style.Style
  draw:frame          -> Draw.Frame
```

### Hyphens in local-name

Hyphens → PascalCase word boundary:
```
table-cell -> TableCell
table-row  -> TableRow
list-item  -> ListItem
value-type -> ValueType (attribute → property)
```

### Attribute Naming Rule

Attributes map to properties on the parent element class:
```
office:value-type   -> TableCell.ValueType (property on Table.TableCell)
table:style-name    -> TableRow.StyleName (property on Table.TableRow)
text:outline-level  -> Heading.OutlineLevel (property on Text.Heading)
```

### .NET Source Layout (Canonical)

```
src/net/
  fods/                       # format-specific workspace
    Compat/                   # Compatibility facades (wraps canonical)
      Fods/
        FodsDocument.cs       # facade for Office.Document
        FodsCell.cs           # facade for Table.TableCell
        FodsSheet.cs          # facade for Table.Table
        FodsRow.cs            # facade for Table.TableRow
    Spec/                     # Canonical spec classes (may be shared)
      Office/
        Document.cs           # -> Office.Document
        Body.cs
        Spreadsheet.cs
      Table/
        Table.cs              # -> Table.Table (table:table)
        TableRow.cs
        TableCell.cs
        CoveredTableCell.cs
      Text/
        Paragraph.cs
        Heading.cs
        Span.cs
      Style/
        Style.cs

src/FormatFactory/            # Shared canonical implementation (cross-format)
  Office/Document.cs          # Single canonical Office.Document
  Table/TableCell.cs          # Single canonical Table.TableCell
  Text/Paragraph.cs           # Single canonical Text.Paragraph
```

### Python Source Layout (Canonical)

```
src/python/
  fods/
    fods/                     # package root (flat, no nesting)
      __init__.py
      parser.py               # streaming parser — returns neutral model dict
      writer.py
      neutral_model.py
      constants.py
      exceptions.py
      office/
        document.py           # Office.Document Python equivalent
      table/
        table.py              # Table.Table
        table_row.py          # Table.TableRow
        table_cell.py         # Table.TableCell
      compat/
        fods_document.py      # FodsDocument facade
        fods_cell.py          # FodsCell facade
```

### Acceptable Exceptions

Format-prefixed names are acceptable ONLY in:
1. `Compat/{Format}/` directory (.NET) or `compat/` module (Python)
2. These are transitional facades that delegate to canonical classes
3. Must have explicit `delegates_to:` reference in qname registry

### NEVER Acceptable

- `FodsDocument` as the PRIMARY implementation (only as facade)
- `GenericCell`, `Node`, `Item` as names for spec elements
- Arbitrary LLM-invented names without a registry entry
- Classes without a `spec_qname` attribute or equivalent metadata

---

## Standard for Non-XML Formats (ZST, XCF, ABW, CSV, TSV, etc.)

For binary/text/compression formats without formal XML QNames:

1. Create a governed canonical name registry entry in `registry/format-specific/`
2. Canonical names derive from format spec concept names:
   - ZST: `Frame`, `Block`, `MagicNumber`, `CompressionLevel`
   - CSV: `Row`, `Field`, `Header`, `Delimiter`
   - Not: `CsvRow`, `CsvField`, `ZstFrame` (no format prefix in canonical names)
3. Format-prefixed names allowed only in user-facing API (compat layer)
4. Every canonical name requires a spec fact reference or evidence comment
