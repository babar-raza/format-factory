// FormatFactory.Fods — Parsing.TableParser
// Parses ODF table:* elements from a loaded XDocument into canonical Model.* types.
// spec_qnames: table:table, table:table-row, table:table-cell, table:table-column
// Authority: plans/.claude/imperative-drifting-conway.md §2, §5
// TC-W1-FODS-NET-005

using System.Xml.Linq;
using FormatFactory.Fods.Model.Office;
using FormatFactory.Fods.Model.Table;

namespace FormatFactory.Fods.Parsing;

/// <summary>
/// Parses ODF table:table, table:table-row, table:table-cell, and table:table-column
/// elements from an already-loaded XDocument into canonical Model.* runtime objects.
///
/// This parser operates on the in-memory XDocument DOM (LINQ-to-XML).
/// It is the canonical parser for the table:* QName group.
///
/// ODF spec basis:
///   §9.1.2  table:table
///   §9.4.3  table:table-column
///   §9.4.4  table:table-row
///   §9.4.5  table:table-cell
///   §9.4.6  table:covered-table-cell
///
/// spec_qname: table:table (primary domain)
/// TC-W1-FODS-NET-005
/// </summary>
internal static class TableParser
{
    private static readonly XNamespace NsOffice =
        "urn:oasis:names:tc:opendocument:xmlns:office:1.0";
    private static readonly XNamespace NsTable =
        "urn:oasis:names:tc:opendocument:xmlns:table:1.0";
    private static readonly XNamespace NsText =
        "urn:oasis:names:tc:opendocument:xmlns:text:1.0";

    /// <summary>
    /// Parse the loaded XDocument into a canonical <see cref="Document"/> model.
    ///
    /// The Document model is populated from the office:document root, navigating
    /// to office:body/office:spreadsheet and parsing each table:table child.
    ///
    /// Returns an empty Document (no tables) if the spreadsheet body is absent.
    /// </summary>
    /// <param name="doc">The XDocument loaded from a .fods file.</param>
    /// <returns>Populated <see cref="Document"/> canonical model.</returns>
    internal static Document ParseDocument(XDocument doc)
    {
        var model = new Document();

        var root = doc.Root;
        if (root is null) return model;

        model.Version = root.Attribute(NsOffice + "version")?.Value ?? "1.3";
        model.MimeType = root.Attribute(NsOffice + "mimetype")?.Value
            ?? "application/vnd.oasis.opendocument.spreadsheet-flat-xml";

        var body = root.Element(NsOffice + "body");
        if (body is null) return model;

        var spreadsheet = body.Element(NsOffice + "spreadsheet");
        if (spreadsheet is null) return model;

        foreach (var tableEl in spreadsheet.Elements(NsTable + "table"))
            model.Spreadsheet.Tables.Add(ParseTable(tableEl));

        return model;
    }

    /// <summary>
    /// Parse a single table:table XElement into a <see cref="Table"/> model.
    /// Populates Rows (with Cells) and Columns.
    /// </summary>
    internal static Table ParseTable(XElement tableEl)
    {
        var table = new Table
        {
            Name = tableEl.Attribute(NsTable + "name")?.Value ?? string.Empty,
        };

        var displayAttr = tableEl.Attribute(NsTable + "display")?.Value;
        if (displayAttr != null)
            table.Display = !string.Equals(displayAttr, "false",
                System.StringComparison.OrdinalIgnoreCase);

        foreach (var child in tableEl.Elements())
        {
            if (child.Name.Namespace == NsTable)
            {
                if (child.Name.LocalName == "table-column")
                    table.Columns.Add(ParseColumn(child));
                else if (child.Name.LocalName == "table-row")
                    table.Rows.Add(ParseRow(child));
            }
        }

        return table;
    }

    /// <summary>
    /// Parse a table:table-column XElement into a <see cref="TableColumn"/> model.
    /// </summary>
    private static TableColumn ParseColumn(XElement colEl)
    {
        var col = new TableColumn
        {
            StyleName = colEl.Attribute(NsTable + "style-name")?.Value,
            DefaultCellStyleName = colEl.Attribute(NsTable + "default-cell-style-name")?.Value,
        };

        var repeatAttr = colEl.Attribute(NsTable + "number-columns-repeated")?.Value;
        if (int.TryParse(repeatAttr, out var repeatCount))
            col.RepeatCount = repeatCount;

        var visAttr = colEl.Attribute(NsTable + "visibility")?.Value;
        if (visAttr != null)
            col.Visibility = visAttr;

        return col;
    }

    /// <summary>
    /// Parse a table:table-row XElement into a <see cref="TableRow"/> model.
    /// Populates Cells list from table:table-cell and table:covered-table-cell children.
    /// </summary>
    private static TableRow ParseRow(XElement rowEl)
    {
        var row = new TableRow
        {
            StyleName = rowEl.Attribute(NsTable + "style-name")?.Value,
        };

        var repeatAttr = rowEl.Attribute(NsTable + "number-rows-repeated")?.Value;
        if (int.TryParse(repeatAttr, out var repeatCount))
            row.RepeatCount = repeatCount;

        foreach (var child in rowEl.Elements())
        {
            if (child.Name.Namespace != NsTable) continue;

            if (child.Name.LocalName == "table-cell")
                row.Cells.Add(ParseCell(child, isCovered: false));
            else if (child.Name.LocalName == "covered-table-cell")
                row.Cells.Add(ParseCell(child, isCovered: true));
        }

        return row;
    }

    /// <summary>
    /// Parse a table:table-cell or table:covered-table-cell into a <see cref="TableCell"/> model.
    ///
    /// Reads:
    ///   office:value-type → ValueType
    ///   office:value      → NumericValue
    ///   table:formula     → Formula
    ///   table:style-name  → StyleName
    ///   text:p/text()     → Value (display string)
    ///
    /// ODF 1.3 §9.4.5
    /// </summary>
    private static TableCell ParseCell(XElement cellEl, bool isCovered)
    {
        var nsOffice = "urn:oasis:names:tc:opendocument:xmlns:office:1.0";

        var cell = new TableCell
        {
            IsCovered = isCovered,
            ValueType = cellEl.Attribute(XName.Get("value-type", nsOffice))?.Value,
            Formula = cellEl.Attribute(NsTable + "formula")?.Value,
            StyleName = cellEl.Attribute(NsTable + "style-name")?.Value,
        };

        var numericStr = cellEl.Attribute(XName.Get("value", nsOffice))?.Value;
        if (numericStr != null && double.TryParse(numericStr,
            System.Globalization.NumberStyles.Any,
            System.Globalization.CultureInfo.InvariantCulture, out var num))
            cell.NumericValue = num;

        var colSpanAttr = cellEl.Attribute(NsTable + "number-columns-spanned")?.Value;
        if (int.TryParse(colSpanAttr, out var colSpan))
            cell.ColumnSpan = colSpan;

        var rowSpanAttr = cellEl.Attribute(NsTable + "number-rows-spanned")?.Value;
        if (int.TryParse(rowSpanAttr, out var rowSpan))
            cell.RowSpan = rowSpan;

        // Extract text:p content as the display value
        var textP = cellEl.Element(NsText + "p");
        if (textP != null)
            cell.Value = textP.Value;

        return cell;
    }
}
