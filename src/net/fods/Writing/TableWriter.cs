// FormatFactory.Fods — Writing.TableWriter
// Serializes canonical Model.Table.* objects back into a LINQ-to-XML XDocument.
// spec_qnames: table:table, table:table-row, table:table-cell
// Authority: plans/.claude/imperative-drifting-conway.md §2, §5
// TC-W1-FODS-NET-005

using System.Collections.Generic;
using System.Xml.Linq;
using FormatFactory.Fods.Model.Table;

namespace FormatFactory.Fods.Writing;

/// <summary>
/// Serializes canonical <see cref="Table"/> model objects into LINQ-to-XML XElements
/// for inclusion in a FODS XDocument.
///
/// This writer is the canonical serializer for the table:* QName group.
/// It is the counterpart to <see cref="FormatFactory.Fods.Parsing.TableParser"/>.
///
/// ODF spec basis:
///   §9.1.2  table:table
///   §9.4.3  table:table-column
///   §9.4.4  table:table-row
///   §9.4.5  table:table-cell
///
/// spec_qname: table:table (primary domain)
/// TC-W1-FODS-NET-005
/// </summary>
internal static class TableWriter
{
    private static readonly XNamespace NsTable =
        "urn:oasis:names:tc:opendocument:xmlns:table:1.0";
    private static readonly XNamespace NsText =
        "urn:oasis:names:tc:opendocument:xmlns:text:1.0";
    private static readonly XNamespace NsOffice =
        "urn:oasis:names:tc:opendocument:xmlns:office:1.0";

    /// <summary>
    /// Serialize a list of canonical <see cref="Table"/> objects into table:table XElements.
    /// Returns one XElement per table.
    /// </summary>
    internal static IEnumerable<XElement> WriteTables(IEnumerable<Table> tables)
    {
        foreach (var table in tables)
            yield return WriteTable(table);
    }

    /// <summary>
    /// Serialize a single canonical <see cref="Table"/> into a table:table XElement.
    /// Writes table:table-column elements followed by table:table-row elements.
    /// </summary>
    internal static XElement WriteTable(Table table)
    {
        var el = new XElement(NsTable + "table",
            new XAttribute(NsTable + "name", table.Name));

        if (!table.Display)
            el.Add(new XAttribute(NsTable + "display", "false"));

        foreach (var col in table.Columns)
            el.Add(WriteColumn(col));

        foreach (var row in table.Rows)
            el.Add(WriteRow(row));

        return el;
    }

    /// <summary>
    /// Serialize a <see cref="TableColumn"/> into a table:table-column XElement.
    /// </summary>
    private static XElement WriteColumn(TableColumn col)
    {
        var el = new XElement(NsTable + "table-column");

        if (!string.IsNullOrEmpty(col.StyleName))
            el.Add(new XAttribute(NsTable + "style-name", col.StyleName));

        if (!string.IsNullOrEmpty(col.DefaultCellStyleName))
            el.Add(new XAttribute(NsTable + "default-cell-style-name", col.DefaultCellStyleName));

        if (col.RepeatCount > 1)
            el.Add(new XAttribute(NsTable + "number-columns-repeated", col.RepeatCount));

        if (col.Visibility != "visible")
            el.Add(new XAttribute(NsTable + "visibility", col.Visibility));

        return el;
    }

    /// <summary>
    /// Serialize a <see cref="TableRow"/> into a table:table-row XElement.
    /// </summary>
    private static XElement WriteRow(TableRow row)
    {
        var el = new XElement(NsTable + "table-row");

        if (!string.IsNullOrEmpty(row.StyleName))
            el.Add(new XAttribute(NsTable + "style-name", row.StyleName));

        if (row.RepeatCount > 1)
            el.Add(new XAttribute(NsTable + "number-rows-repeated", row.RepeatCount));

        foreach (var cell in row.Cells)
            el.Add(WriteCell(cell));

        return el;
    }

    /// <summary>
    /// Serialize a <see cref="TableCell"/> into a table:table-cell or
    /// table:covered-table-cell XElement.
    ///
    /// Writes:
    ///   office:value-type → ValueType
    ///   office:value      → NumericValue
    ///   table:formula     → Formula
    ///   table:style-name  → StyleName
    ///   text:p            → Value (display string)
    ///
    /// ODF 1.3 §9.4.5
    /// </summary>
    private static XElement WriteCell(TableCell cell)
    {
        var localName = cell.IsCovered ? "covered-table-cell" : "table-cell";
        var el = new XElement(NsTable + localName);

        if (!string.IsNullOrEmpty(cell.StyleName))
            el.Add(new XAttribute(NsTable + "style-name", cell.StyleName));

        if (!string.IsNullOrEmpty(cell.ValueType))
            el.Add(new XAttribute(NsOffice + "value-type", cell.ValueType));

        if (cell.NumericValue.HasValue)
            el.Add(new XAttribute(NsOffice + "value",
                cell.NumericValue.Value.ToString(System.Globalization.CultureInfo.InvariantCulture)));

        if (!string.IsNullOrEmpty(cell.Formula))
            el.Add(new XAttribute(NsTable + "formula", cell.Formula));

        if (cell.ColumnSpan > 1)
            el.Add(new XAttribute(NsTable + "number-columns-spanned", cell.ColumnSpan));

        if (cell.RowSpan > 1)
            el.Add(new XAttribute(NsTable + "number-rows-spanned", cell.RowSpan));

        if (cell.Value != null)
            el.Add(new XElement(NsText + "p", cell.Value));

        return el;
    }
}
