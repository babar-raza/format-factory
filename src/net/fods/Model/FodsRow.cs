// FormatFactory.Fods -- Commercial .NET FODS Model -- FodsRow
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: commercial_readiness_in_progress (NOT approved)

using System.Collections.Generic;
using System.Xml.Linq;

namespace FormatFactory.Fods;

/// <summary>
/// Typed wrapper for a single ODF table:table-row element.
/// Backed by the live XElement in the DOM.
///
/// ODF spec basis: ODF 1.3 §9.4.4 table:table-row.
/// </summary>
public sealed class FodsRow
{
    private static readonly XNamespace NsTable =
        "urn:oasis:names:tc:opendocument:xmlns:table:1.0";

    internal XElement Element { get; }

    internal FodsRow(XElement element)
    {
        Element = element;
    }

    /// <summary>
    /// All cells in this row (table:table-cell and table:covered-table-cell), in document order.
    /// </summary>
    public IReadOnlyList<FodsCell> Cells
    {
        get
        {
            var result = new List<FodsCell>();
            foreach (var child in Element.Elements())
            {
                if (child.Name.NamespaceName == NsTable.NamespaceName &&
                    (child.Name.LocalName == "table-cell" ||
                     child.Name.LocalName == "covered-table-cell"))
                {
                    result.Add(new FodsCell(child));
                }
            }
            return result;
        }
    }
}
