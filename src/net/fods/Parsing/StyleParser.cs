// FormatFactory.Fods — Parsing.StyleParser
// Parses ODF style:style elements from a loaded XDocument into canonical Model.Style.* types.
// spec_qnames: style:style, style:table-cell-properties, style:text-properties
// Authority: plans/.claude/imperative-drifting-conway.md §2, §5
// TC-W1-FODS-NET-005

using System.Collections.Generic;
using System.Xml.Linq;
using FormatFactory.Fods.Model.Style;

namespace FormatFactory.Fods.Parsing;

/// <summary>
/// Parses ODF style:style and child property elements from an already-loaded XDocument
/// into canonical <see cref="Style"/> model objects.
///
/// This parser handles the office:automatic-styles section of FODS documents.
///
/// ODF spec basis:
///   §16.2   style:style
///   §17.18  style:table-cell-properties
///   §17.19  style:text-properties (subset)
///
/// spec_qname: style:style (primary domain)
/// TC-W1-FODS-NET-005
/// </summary>
internal static class StyleParser
{
    private static readonly XNamespace NsOffice =
        "urn:oasis:names:tc:opendocument:xmlns:office:1.0";
    private static readonly XNamespace NsStyle =
        "urn:oasis:names:tc:opendocument:xmlns:style:1.0";
    private static readonly XNamespace NsFo =
        "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0";

    /// <summary>
    /// Parse all style:style elements from office:automatic-styles in the given XDocument.
    /// Returns a list of canonical <see cref="Style"/> objects, keyed by style:name.
    /// </summary>
    /// <param name="doc">The loaded FODS XDocument.</param>
    /// <returns>List of parsed <see cref="Style"/> objects (may be empty).</returns>
    internal static List<Style> ParseAutomaticStyles(XDocument doc)
    {
        var styles = new List<Style>();
        var root = doc.Root;
        if (root is null) return styles;

        var autoStyles = root.Element(NsOffice + "automatic-styles");
        if (autoStyles is null) return styles;

        foreach (var styleEl in autoStyles.Elements(NsStyle + "style"))
            styles.Add(ParseStyle(styleEl));

        return styles;
    }

    /// <summary>
    /// Parse a single style:style XElement into a <see cref="Style"/> model.
    /// </summary>
    private static Style ParseStyle(XElement styleEl)
    {
        var style = new Style
        {
            Name = styleEl.Attribute(NsStyle + "name")?.Value ?? string.Empty,
            Family = styleEl.Attribute(NsStyle + "family")?.Value ?? string.Empty,
            ParentStyleName = styleEl.Attribute(NsStyle + "parent-style-name")?.Value,
        };

        var cellPropsEl = styleEl.Element(NsStyle + "table-cell-properties");
        if (cellPropsEl != null)
            style.TableCellProperties = ParseTableCellProperties(cellPropsEl);

        var textPropsEl = styleEl.Element(NsStyle + "text-properties");
        if (textPropsEl != null)
            style.TextProperties = ParseTextProperties(textPropsEl);

        return style;
    }

    /// <summary>
    /// Parse style:table-cell-properties into a <see cref="TableCellProperties"/> model.
    /// ODF 1.3 §17.18.
    /// </summary>
    private static TableCellProperties ParseTableCellProperties(XElement el)
    {
        return new TableCellProperties
        {
            BackgroundColor = el.Attribute(NsFo + "background-color")?.Value,
            WrapOption = el.Attribute(NsFo + "wrap-option")?.Value,
            VerticalAlign = el.Attribute(NsStyle + "vertical-align")?.Value,
            TextAlign = el.Attribute(NsFo + "text-align")?.Value,
            Border = el.Attribute(NsFo + "border")?.Value,
        };
    }

    /// <summary>
    /// Parse style:text-properties into a <see cref="TextProperties"/> model.
    /// ODF 1.3 §17.19 (subset of properties most common in FODS).
    /// </summary>
    private static TextProperties ParseTextProperties(XElement el)
    {
        return new TextProperties
        {
            FontName = el.Attribute(NsFo + "font-family")?.Value
                    ?? el.Attribute(NsStyle + "font-name")?.Value,
            FontSize = el.Attribute(NsFo + "font-size")?.Value,
            FontWeight = el.Attribute(NsFo + "font-weight")?.Value,
            FontStyle = el.Attribute(NsFo + "font-style")?.Value,
            Color = el.Attribute(NsFo + "color")?.Value,
        };
    }
}
