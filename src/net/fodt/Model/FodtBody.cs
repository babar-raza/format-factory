// FormatFactory.Fodt -- Commercial .NET FODT Model -- FodtBody
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: commercial_readiness_in_progress (NOT approved)

using System.Collections.Generic;
using System.Xml.Linq;

namespace FormatFactory.Fodt;

/// <summary>
/// Typed wrapper for the ODF office:body/office:text element.
/// Provides access to top-level paragraphs, headings, and tables.
///
/// ODF spec basis: ODF 1.3 §3.3 office:body, §3.4 office:text.
/// </summary>
public sealed class FodtBody
{
    private static readonly XNamespace NsText =
        "urn:oasis:names:tc:opendocument:xmlns:text:1.0";
    private static readonly XNamespace NsTable =
        "urn:oasis:names:tc:opendocument:xmlns:table:1.0";

    internal XElement Element { get; }

    internal FodtBody(XElement element)
    {
        Element = element;
    }

    /// <summary>
    /// All top-level paragraphs and headings (text:p and text:h elements) in document order.
    /// Does not recurse into tables or lists — top-level only for this vertical slice.
    ///
    /// ODF spec basis: §5.1.3 text:p, §5.1.2 text:h.
    /// </summary>
    public IReadOnlyList<FodtParagraph> Paragraphs
    {
        get
        {
            var result = new List<FodtParagraph>();
            foreach (var child in Element.Elements())
            {
                if (child.Name.NamespaceName == NsText.NamespaceName &&
                    (child.Name.LocalName == "p" || child.Name.LocalName == "h"))
                {
                    result.Add(new FodtParagraph(child));
                }
            }
            return result;
        }
    }

    /// <summary>
    /// All top-level tables (table:table elements) in document order.
    /// Provides structured access to rows and cells within each table.
    ///
    /// ODF spec basis: ODF 1.3 §9.4.2 table:table.
    /// </summary>
    public IReadOnlyList<FodtTable> Tables
    {
        get
        {
            var result = new List<FodtTable>();
            foreach (var child in Element.Elements(NsTable + "table"))
                result.Add(new FodtTable(child));
            return result;
        }
    }
}
