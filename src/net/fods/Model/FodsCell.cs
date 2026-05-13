// FormatFactory.Fods -- Commercial .NET FODS Model -- FodsCell
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: commercial_readiness_in_progress (NOT approved)

using System.Xml.Linq;

namespace FormatFactory.Fods;

/// <summary>
/// Typed wrapper for a single ODF table:table-cell element.
/// Backed by the live XElement in the DOM — mutations write through to the document.
///
/// ODF spec basis: ODF 1.3 §9.4.5 table:table-cell, §6.1.1 text:p.
/// Security: no deserialization; reads/writes through trusted XDocument loaded securely.
/// </summary>
public sealed class FodsCell
{
    private static readonly XNamespace NsTable =
        "urn:oasis:names:tc:opendocument:xmlns:table:1.0";
    private static readonly XNamespace NsText =
        "urn:oasis:names:tc:opendocument:xmlns:text:1.0";
    private static readonly XNamespace NsOffice =
        "urn:oasis:names:tc:opendocument:xmlns:office:1.0";

    internal XElement Element { get; }

    internal FodsCell(XElement element)
    {
        Element = element;
    }

    /// <summary>
    /// Gets the cell's text value from the first text:p child element, or null if absent.
    /// This reflects the display/string value; numeric values may have office:value attributes too.
    /// </summary>
    public string? Value
    {
        get
        {
            var textP = Element.Element(NsText + "p");
            return textP?.Value;
        }
    }

    /// <summary>
    /// Sets the cell's text content by updating (or creating) the first text:p child element.
    /// Also sets office:value-type="string" on the cell element per ODF 1.3 §9.4.5.
    ///
    /// ODF citation: §9.4.5 — string cells use office:value-type="string" and
    /// contain text:p elements for their text representation.
    ///
    /// Local fact source: format_understanding/fods/ (FUL-002 fact set)
    /// </summary>
    /// <param name="value">The text value to write. Must not be null.</param>
    public void SetText(string value)
    {
        ArgumentNullException.ThrowIfNull(value);

        // Update or create text:p child
        var textP = Element.Element(NsText + "p");
        if (textP is null)
        {
            textP = new XElement(NsText + "p");
            Element.Add(textP);
        }
        textP.Value = value;

        // Set office:value-type="string" per ODF spec for string cells
        Element.SetAttributeValue(NsOffice + "value-type", "string");
    }

    /// <summary>Whether this cell element is table:covered-table-cell (merged/covered).</summary>
    public bool IsCovered => Element.Name.LocalName == "covered-table-cell";
}
