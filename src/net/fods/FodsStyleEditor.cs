// FormatFactory.Fods -- ODF Style Editor ( 3e)
// Implements the setter path: writes cell style properties to ODF XML
// by creating or updating auto-style entries in office:automatic-styles.
//
// ODF spec references:
//   §16.2   style:style — style definition and parent chain
//   §15.5   style:table-cell-properties — background, border, alignment
//   §15.11  style:paragraph-properties — text-align, margin-left
//   §15.4   style:text-properties — font, color, underline, strikethrough
//   §9.4.5  table:table-cell/@table:style-name — cell → style reference

using System;
using System.Globalization;
using System.Linq;
using System.Xml.Linq;

namespace FormatFactory.Fods;

/// <summary>
/// Writes ODF cell style properties to XML by creating or updating
/// <c>style:style</c> entries in <c>office:automatic-styles</c>.
/// All methods are static and operate on a caller-supplied XDocument.
/// </summary>
public static class FodsStyleEditor
{
    // ODF namespace constants
    private static readonly XNamespace NsStyle =
        "urn:oasis:names:tc:opendocument:xmlns:style:1.0";
    private static readonly XNamespace NsTable =
        "urn:oasis:names:tc:opendocument:xmlns:table:1.0";
    private static readonly XNamespace NsFo =
        "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0";
    private static readonly XNamespace NsOffice =
        "urn:oasis:names:tc:opendocument:xmlns:office:1.0";

    // -------------------------------------------------------------------------
    // Cell property setters — write to ODF XML
    // -------------------------------------------------------------------------

    /// <summary>
    /// Set the horizontal alignment (<c>fo:text-align</c>) for the cell.
    /// Creates or updates the cell's automatic style entry.
    /// ODF: style:paragraph-properties/@fo:text-align.
    /// </summary>
    public static void SetCellHorizontalAlignment(
        XDocument doc, XElement cell, string alignment)
    {
        var para = GetOrCreateCellStyleProperty(doc, cell, NsStyle + "paragraph-properties");
        para.SetAttributeValue(NsFo + "text-align", alignment);
    }

    /// <summary>
    /// Set the vertical alignment (<c>style:vertical-align</c>) for the cell.
    /// ODF: style:table-cell-properties/@style:vertical-align.
    /// </summary>
    public static void SetCellVerticalAlignment(
        XDocument doc, XElement cell, string alignment)
    {
        var cellProps = GetOrCreateCellStyleProperty(doc, cell, NsStyle + "table-cell-properties");
        cellProps.SetAttributeValue(NsStyle + "vertical-align", alignment);
    }

    /// <summary>
    /// Set the font color (<c>fo:color</c>) for the cell.
    /// ODF: style:text-properties/@fo:color.
    /// </summary>
    public static void SetCellFontColor(
        XDocument doc, XElement cell, string color)
    {
        var text = GetOrCreateCellStyleProperty(doc, cell, NsStyle + "text-properties");
        text.SetAttributeValue(NsFo + "color", color);
    }

    /// <summary>
    /// Set the background color (<c>fo:background-color</c>) for the cell.
    /// ODF: style:table-cell-properties/@fo:background-color.
    /// </summary>
    public static void SetCellBackgroundColor(
        XDocument doc, XElement cell, string color)
    {
        var cellProps = GetOrCreateCellStyleProperty(doc, cell, NsStyle + "table-cell-properties");
        cellProps.SetAttributeValue(NsFo + "background-color", color);
    }

    /// <summary>
    /// Set the border style (<c>fo:border</c>) for the cell.
    /// ODF: style:table-cell-properties/@fo:border.
    /// </summary>
    public static void SetCellBorderStyle(
        XDocument doc, XElement cell, string borderStyle)
    {
        var cellProps = GetOrCreateCellStyleProperty(doc, cell, NsStyle + "table-cell-properties");
        cellProps.SetAttributeValue(NsFo + "border", borderStyle);
    }

    /// <summary>
    /// Set the underline style (<c>style:text-underline-style</c>) for the cell.
    /// ODF: style:text-properties/@style:text-underline-style.
    /// </summary>
    public static void SetCellUnderline(
        XDocument doc, XElement cell, string underlineStyle)
    {
        var text = GetOrCreateCellStyleProperty(doc, cell, NsStyle + "text-properties");
        text.SetAttributeValue(NsStyle + "text-underline-style", underlineStyle);
    }

    /// <summary>
    /// Set the strikethrough style (<c>style:text-line-through-style</c>) for the cell.
    /// ODF: style:text-properties/@style:text-line-through-style.
    /// </summary>
    public static void SetCellStrikethrough(
        XDocument doc, XElement cell, bool strikethrough)
    {
        var text = GetOrCreateCellStyleProperty(doc, cell, NsStyle + "text-properties");
        text.SetAttributeValue(NsStyle + "text-line-through-style",
            strikethrough ? "solid" : "none");
    }

    /// <summary>
    /// Set the shrink-to-fit property for the cell.
    /// ODF: style:table-cell-properties/@style:shrink-to-fit.
    /// </summary>
    public static void SetCellShrinkToFit(
        XDocument doc, XElement cell, bool shrink)
    {
        var cellProps = GetOrCreateCellStyleProperty(doc, cell, NsStyle + "table-cell-properties");
        cellProps.SetAttributeValue(NsStyle + "shrink-to-fit", shrink ? "true" : "false");
    }

    /// <summary>
    /// Set the text rotation angle for the cell (degrees).
    /// ODF: style:table-cell-properties/@style:rotation-angle.
    /// </summary>
    public static void SetCellRotationAngle(
        XDocument doc, XElement cell, int degrees)
    {
        var cellProps = GetOrCreateCellStyleProperty(doc, cell, NsStyle + "table-cell-properties");
        cellProps.SetAttributeValue(NsStyle + "rotation-angle",
            degrees.ToString(CultureInfo.InvariantCulture));
    }

    /// <summary>
    /// Set the indent level for the cell via left margin.
    /// ODF: style:paragraph-properties/@fo:margin-left (1 level ≈ 0.5cm).
    /// </summary>
    public static void SetCellIndentLevel(
        XDocument doc, XElement cell, int level)
    {
        var para = GetOrCreateCellStyleProperty(doc, cell, NsStyle + "paragraph-properties");
        // 1 indent level ≈ 0.5cm
        var marginCm = (level * 0.5).ToString("0.00", CultureInfo.InvariantCulture) + "cm";
        para.SetAttributeValue(NsFo + "margin-left", marginCm);
    }

    /// <summary>
    /// Set the cell protection flag.
    /// ODF: style:table-cell-properties/@style:cell-protect.
    /// </summary>
    public static void SetCellProtection(
        XDocument doc, XElement cell, bool protect)
    {
        var cellProps = GetOrCreateCellStyleProperty(doc, cell, NsStyle + "table-cell-properties");
        cellProps.SetAttributeValue(NsStyle + "cell-protect",
            protect ? "protected" : "none");
    }

    /// <summary>
    /// Set the font style (<c>fo:font-style</c>) for the cell — "normal" or "italic".
    /// ODF: style:text-properties/@fo:font-style.
    /// </summary>
    public static void SetCellFontStyle(
        XDocument doc, XElement cell, string style)
    {
        var text = GetOrCreateCellStyleProperty(doc, cell, NsStyle + "text-properties");
        text.SetAttributeValue(NsFo + "font-style", style);
    }

    // -------------------------------------------------------------------------
    // Internal style management
    // -------------------------------------------------------------------------

    /// <summary>
    /// Get or create the named property element (<paramref name="propertyElementName"/>)
    /// inside the auto-style for <paramref name="cell"/>.
    /// The method:
    /// 1. Reads the cell's <c>table:style-name</c>.
    /// 2. Finds or creates an auto-style with that name in <c>office:automatic-styles</c>.
    ///    If no style name is set, generates a new unique name and sets it on the cell.
    /// 3. Finds or creates the requested property element inside the auto-style.
    /// </summary>
    private static XElement GetOrCreateCellStyleProperty(
        XDocument doc, XElement cell, XName propertyElementName)
    {
        ArgumentNullException.ThrowIfNull(doc);
        ArgumentNullException.ThrowIfNull(cell);

        // Step 1: ensure office:automatic-styles exists
        var autoStyles = doc.Root!.Element(NsOffice + "automatic-styles");
        if (autoStyles is null)
        {
            autoStyles = new XElement(NsOffice + "automatic-styles");
            // Insert before office:body
            var body = doc.Root.Element(NsOffice + "body");
            if (body is not null)
                body.AddBeforeSelf(autoStyles);
            else
                doc.Root.AddFirst(autoStyles);
        }

        // Step 2: get or create the auto-style for this cell
        string? styleName = cell.Attribute(NsTable + "style-name")?.Value;
        XElement? styleEl = null;

        if (!string.IsNullOrEmpty(styleName))
        {
            styleEl = autoStyles.Elements(NsStyle + "style")
                .FirstOrDefault(s =>
                    s.Attribute(NsStyle + "name")?.Value == styleName &&
                    s.Attribute(NsStyle + "family")?.Value == "table-cell");
        }

        if (styleEl is null)
        {
            // Generate new style name if none set or no matching style found
            if (string.IsNullOrEmpty(styleName))
            {
                styleName = GenerateStyleName(autoStyles, "ce");
                cell.SetAttributeValue(NsTable + "style-name", styleName);
            }
            styleEl = new XElement(NsStyle + "style",
                new XAttribute(NsStyle + "name", styleName),
                new XAttribute(NsStyle + "family", "table-cell"));
            autoStyles.Add(styleEl);
        }

        // Step 3: find or create the property element inside the style
        var propEl = styleEl.Element(propertyElementName);
        if (propEl is null)
        {
            propEl = new XElement(propertyElementName);
            styleEl.Add(propEl);
        }

        return propEl;
    }

    /// <summary>
    /// Generate a unique style name with the given <paramref name="prefix"/>
    /// that does not already exist in <paramref name="autoStyles"/>.
    /// </summary>
    private static string GenerateStyleName(XElement autoStyles, string prefix)
    {
        var existing = autoStyles
            .Elements(NsStyle + "style")
            .Select(s => s.Attribute(NsStyle + "name")?.Value)
            .Where(n => n is not null && n.StartsWith(prefix, StringComparison.Ordinal))
            .ToHashSet(StringComparer.Ordinal);

        for (int i = 1; ; i++)
        {
            var candidate = prefix + i.ToString(CultureInfo.InvariantCulture);
            if (!existing.Contains(candidate))
                return candidate;
        }
    }
}
