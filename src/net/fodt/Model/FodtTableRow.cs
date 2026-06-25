// FormatFactory.Fodt -- Commercial .NET FODT Model -- FodtTableRow
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: commercial_readiness_in_progress (NOT approved)
//
// ODF spec basis: ODF 1.3 §9.4.4 table:table-row

using System.Collections.Generic;
using System.Xml.Linq;

namespace FormatFactory.Fodt;

/// <summary>
/// Typed wrapper for the ODF table:table-row element.
/// Provides access to cells within the row.
///
/// ODF spec basis: ODF 1.3 §9.4.4 table:table-row.
/// </summary>
public sealed class FodtTableRow
{
    private static readonly XNamespace NsTable =
        "urn:oasis:names:tc:opendocument:xmlns:table:1.0";

    internal XElement Element { get; }

    internal FodtTableRow(XElement element)
    {
        Element = element;
    }

    /// <summary>
    /// All cells in this row (table:table-cell elements).
    /// Does not include table:covered-table-cell (merged cell placeholders).
    /// ODF spec basis: §9.4.4 table:table-row children.
    /// </summary>
    public IReadOnlyList<FodtTableCell> Cells
    {
        get
        {
            var result = new List<FodtTableCell>();
            foreach (var child in Element.Elements(NsTable + "table-cell"))
                result.Add(new FodtTableCell(child));
            return result;
        }
    }

    /// <summary>Number of cells in this row.</summary>
    public int CellCount => Cells.Count;
}
