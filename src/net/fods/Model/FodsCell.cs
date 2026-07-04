// FormatFactory.Fods -- Commercial .NET FODS Model -- FodsCell
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: commercial_readiness_in_progress (NOT approved)
// TC-W1-FODS-NET-003: Added Value setter, ValueType, Formula properties.
// Canonical model type: FormatFactory.Fods.Model.Table.TableCell (spec_qname: table:table-cell)

using System.Xml.Linq;

namespace FormatFactory.Fods;

/// <summary>
/// Typed wrapper for a single ODF table:table-cell element.
/// Backed by the live XElement in the DOM — mutations write through to the document.
///
/// Public API facade for canonical type <see cref="FormatFactory.Fods.Model.Table.TableCell"/>
/// (spec_qname: table:table-cell, ODF 1.3 §9.4.5).
///
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

    // -------------------------------------------------------------------------
    // Value (text display content) — read/write
    // ODF 1.3 §9.4.5: string value is carried in text:p child element.
    // -------------------------------------------------------------------------

    /// <summary>
    /// Gets or sets the cell's text/string display value.
    ///
    /// Get: reads from the first text:p child element; returns null if absent.
    /// Set: writes (or creates) the text:p child and sets office:value-type="string".
    ///
    /// ODF 1.3 §9.4.5 — string cells use office:value-type="string" and text:p children.
    /// spec_qname: table:table-cell
    /// </summary>
    public string? Value
    {
        get
        {
            var textP = Element.Element(NsText + "p");
            return textP?.Value;
        }
        set
        {
            if (value is null)
            {
                // Remove text:p if setting to null
                Element.Element(NsText + "p")?.Remove();
                return;
            }

            var textP = Element.Element(NsText + "p");
            if (textP is null)
            {
                textP = new XElement(NsText + "p");
                Element.Add(textP);
            }
            textP.Value = value;
            Element.SetAttributeValue(NsOffice + "value-type", "string");
        }
    }

    // -------------------------------------------------------------------------
    // ValueType — read/write
    // ODF 1.3 §9.4.5: office:value-type attribute
    // -------------------------------------------------------------------------

    /// <summary>
    /// Gets or sets the cell's value type from the office:value-type attribute.
    ///
    /// Common values: "string", "float", "date", "boolean", "percentage", "currency".
    /// Returns null if the attribute is absent (empty cell).
    ///
    /// ODF 1.3 §9.4.5 + §6.7.1
    /// spec_qname: table:table-cell
    /// </summary>
    public string? ValueType
    {
        get => Element.Attribute(NsOffice + "value-type")?.Value;
        set => Element.SetAttributeValue(NsOffice + "value-type", value);
    }

    // -------------------------------------------------------------------------
    // Formula — read/write
    // ODF 1.3 §9.4.5: table:formula attribute
    // -------------------------------------------------------------------------

    /// <summary>
    /// Gets or sets the cell formula from the table:formula attribute.
    ///
    /// Formula syntax: "of:=&lt;expression&gt;" per ODF 1.3 §9.4.5.
    /// Returns null if no formula is present.
    ///
    /// spec_qname: table:table-cell
    /// </summary>
    public string? Formula
    {
        get => Element.Attribute(NsTable + "formula")?.Value;
        set => Element.SetAttributeValue(NsTable + "formula", value);
    }

    // -------------------------------------------------------------------------
    // NumericValue — read
    // ODF 1.3 §9.4.5: office:value attribute (numeric backing value)
    // -------------------------------------------------------------------------

    /// <summary>
    /// Gets the cell's numeric backing value from the office:value attribute.
    /// Used for float, percentage, and currency cells.
    /// Returns null if the attribute is absent or not a valid double.
    ///
    /// ODF 1.3 §9.4.5
    /// spec_qname: table:table-cell
    /// </summary>
    public double? NumericValue
    {
        get
        {
            var attr = Element.Attribute(NsOffice + "value")?.Value;
            if (attr == null) return null;
            return double.TryParse(attr,
                System.Globalization.NumberStyles.Any,
                System.Globalization.CultureInfo.InvariantCulture, out var d) ? d : null;
        }
    }

    // -------------------------------------------------------------------------
    // IsCovered
    // -------------------------------------------------------------------------

    /// <summary>Whether this cell element is table:covered-table-cell (merged/covered).</summary>
    public bool IsCovered => Element.Name.LocalName == "covered-table-cell";

    // -------------------------------------------------------------------------
    // SetText — kept for backward compatibility; prefer Value setter instead
    // -------------------------------------------------------------------------

    /// <summary>
    /// Sets the cell's text content (backward-compatible method).
    /// Prefer the <see cref="Value"/> setter for new code.
    /// </summary>
    /// <param name="value">The text value to write. Must not be null.</param>
    public void SetText(string value)
    {
        ArgumentNullException.ThrowIfNull(value);
        Value = value;
    }
}
