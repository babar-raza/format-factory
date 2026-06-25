// FormatFactory.Fodt -- Commercial .NET FODT Model -- FodtTableCell
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: commercial_readiness_in_progress (NOT approved)
//
// ODF spec basis: ODF 1.3 §9.4.5 table:table-cell

using System.Collections.Generic;
using System.Text;
using System.Xml.Linq;

namespace FormatFactory.Fodt;

/// <summary>
/// Typed wrapper for the ODF table:table-cell element.
/// Provides access to cell text content from nested text:p elements.
///
/// ODF spec basis: ODF 1.3 §9.4.5 table:table-cell.
/// </summary>
public sealed class FodtTableCell
{
    private static readonly XNamespace NsText =
        "urn:oasis:names:tc:opendocument:xmlns:text:1.0";

    internal XElement Element { get; }

    internal FodtTableCell(XElement element)
    {
        Element = element;
    }

    /// <summary>
    /// Number of columns this cell spans (from table:number-columns-spanned attribute).
    /// Returns 1 if the attribute is absent (default).
    /// ODF spec basis: §9.4.5 table:table-cell @table:number-columns-spanned.
    /// </summary>
    public int ColumnSpan
    {
        get
        {
            var attr = Element.Attribute(
                XName.Get("number-columns-spanned",
                    "urn:oasis:names:tc:opendocument:xmlns:table:1.0"));
            if (attr is not null && int.TryParse(attr.Value, out int span))
                return span;
            return 1;
        }
    }

    /// <summary>
    /// Plain text extracted from all nested text:p elements, joined with newlines.
    /// Returns an empty string if the cell has no text content.
    /// ODF spec basis: §5.1.3 text:p (paragraph inside table cell).
    /// </summary>
    public string GetPlainText()
    {
        var sb = new StringBuilder();
        bool first = true;
        foreach (var p in Element.Descendants(NsText + "p"))
        {
            if (!first) sb.Append('\n');
            sb.Append(p.Value);
            first = false;
        }
        return sb.ToString();
    }
}
