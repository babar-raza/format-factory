// FormatFactory.Fods -- Commercial .NET FODS Model -- FodsSheet
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: commercial_readiness_in_progress (NOT approved)

using System.Collections.Generic;
using System.Xml.Linq;

namespace FormatFactory.Fods;

/// <summary>
/// Typed wrapper for a single ODF table:table element (a spreadsheet sheet/tab).
/// Backed by the live XElement in the DOM — mutations write through to the document.
///
/// ODF spec basis: ODF 1.3 §9.4.2 table:table.
/// </summary>
public sealed class FodsSheet
{
    private static readonly XNamespace NsTable =
        "urn:oasis:names:tc:opendocument:xmlns:table:1.0";

    internal XElement Element { get; }

    internal FodsSheet(XElement element)
    {
        Element = element;
    }

    /// <summary>
    /// Gets or sets the sheet name (table:name attribute).
    /// Setting to null removes the attribute; ODF requires a name so prefer non-null values.
    /// </summary>
    public string Name
    {
        get => Element.Attribute(NsTable + "name")?.Value ?? string.Empty;
        set => Element.SetAttributeValue(NsTable + "name", value);
    }

    /// <summary>All rows in this sheet (table:table-row elements), in document order.</summary>
    public IReadOnlyList<FodsRow> Rows
    {
        get
        {
            var result = new List<FodsRow>();
            foreach (var child in Element.Elements(NsTable + "table-row"))
                result.Add(new FodsRow(child));
            return result;
        }
    }
}
