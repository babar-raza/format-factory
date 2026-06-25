// FormatFactory.Fodt -- Commercial .NET FODT Model -- FodtTable
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: commercial_readiness_in_progress (NOT approved)
//
// ODF spec basis: ODF 1.3 §9.4.2 table:table

using System.Collections.Generic;
using System.Xml.Linq;

namespace FormatFactory.Fodt;

/// <summary>
/// Typed wrapper for the ODF table:table element inside an FODT document.
/// Provides access to the table name and its rows.
///
/// ODF spec basis: ODF 1.3 §9.4.2 table:table.
/// </summary>
public sealed class FodtTable
{
    private static readonly XNamespace NsTable =
        "urn:oasis:names:tc:opendocument:xmlns:table:1.0";

    internal XElement Element { get; }

    internal FodtTable(XElement element)
    {
        Element = element;
    }

    /// <summary>
    /// Table name from the table:name attribute, or empty string if absent.
    /// ODF spec basis: §9.4.2 table:table @table:name.
    /// </summary>
    public string Name =>
        Element.Attribute(NsTable + "name")?.Value ?? string.Empty;

    /// <summary>
    /// All rows in this table (table:table-row elements).
    /// ODF spec basis: §9.4.2 table:table children.
    /// </summary>
    public IReadOnlyList<FodtTableRow> Rows
    {
        get
        {
            var result = new List<FodtTableRow>();
            foreach (var child in Element.Elements(NsTable + "table-row"))
                result.Add(new FodtTableRow(child));
            return result;
        }
    }

    /// <summary>Number of rows in this table.</summary>
    public int RowCount => Rows.Count;

    /// <summary>
    /// Get the text content of a specific cell by zero-based row and column index.
    /// Returns null if the row or column index is out of range.
    /// </summary>
    public string? GetCellText(int rowIndex, int colIndex)
    {
        var rows = Rows;
        if (rowIndex < 0 || rowIndex >= rows.Count) return null;
        var cells = rows[rowIndex].Cells;
        if (colIndex < 0 || colIndex >= cells.Count) return null;
        return cells[colIndex].GetPlainText();
    }
}
