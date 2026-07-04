// FormatFactory.Fods — Writing.StyleWriter
// Serializes canonical Model.Style.* objects into LINQ-to-XML XElements.
// spec_qnames: style:style, style:table-cell-properties, style:text-properties
// Authority: plans/.claude/imperative-drifting-conway.md §2, §5
// TC-W1-FODS-NET-005

using System.Collections.Generic;
using System.Xml.Linq;
using FormatFactory.Fods.Model.Style;

namespace FormatFactory.Fods.Writing;

/// <summary>
/// Serializes canonical <see cref="Style"/> model objects into LINQ-to-XML XElements
/// for inclusion in the office:automatic-styles section of a FODS XDocument.
///
/// This writer is the canonical serializer for the style:* QName group.
/// It is the counterpart to <see cref="FormatFactory.Fods.Parsing.StyleParser"/>.
///
/// ODF spec basis:
///   §16.2   style:style
///   §17.18  style:table-cell-properties
///   §17.19  style:text-properties
///
/// spec_qname: style:style (primary domain)
/// TC-W1-FODS-NET-005
/// </summary>
internal static class StyleWriter
{
    private static readonly XNamespace NsStyle =
        "urn:oasis:names:tc:opendocument:xmlns:style:1.0";
    private static readonly XNamespace NsFo =
        "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0";

    /// <summary>
    /// Serialize a list of <see cref="Style"/> objects into style:style XElements.
    /// </summary>
    internal static IEnumerable<XElement> WriteStyles(IEnumerable<Style> styles)
    {
        foreach (var style in styles)
            yield return WriteStyle(style);
    }

    /// <summary>
    /// Serialize a single <see cref="Style"/> into a style:style XElement.
    /// </summary>
    internal static XElement WriteStyle(Style style)
    {
        var el = new XElement(NsStyle + "style",
            new XAttribute(NsStyle + "name", style.Name),
            new XAttribute(NsStyle + "family", style.Family));

        if (!string.IsNullOrEmpty(style.ParentStyleName))
            el.Add(new XAttribute(NsStyle + "parent-style-name", style.ParentStyleName));

        if (style.TableCellProperties is not null)
            el.Add(WriteTableCellProperties(style.TableCellProperties));

        if (style.TextProperties is not null)
            el.Add(WriteTextProperties(style.TextProperties));

        return el;
    }

    private static XElement WriteTableCellProperties(TableCellProperties props)
    {
        var el = new XElement(NsStyle + "table-cell-properties");

        if (!string.IsNullOrEmpty(props.BackgroundColor))
            el.Add(new XAttribute(NsFo + "background-color", props.BackgroundColor));

        if (!string.IsNullOrEmpty(props.WrapOption))
            el.Add(new XAttribute(NsFo + "wrap-option", props.WrapOption));

        if (!string.IsNullOrEmpty(props.VerticalAlign))
            el.Add(new XAttribute(NsStyle + "vertical-align", props.VerticalAlign));

        if (!string.IsNullOrEmpty(props.TextAlign))
            el.Add(new XAttribute(NsFo + "text-align", props.TextAlign));

        if (!string.IsNullOrEmpty(props.Border))
            el.Add(new XAttribute(NsFo + "border", props.Border));

        return el;
    }

    private static XElement WriteTextProperties(TextProperties props)
    {
        var el = new XElement(NsStyle + "text-properties");

        if (!string.IsNullOrEmpty(props.FontName))
            el.Add(new XAttribute(NsFo + "font-family", props.FontName));

        if (!string.IsNullOrEmpty(props.FontSize))
            el.Add(new XAttribute(NsFo + "font-size", props.FontSize));

        if (!string.IsNullOrEmpty(props.FontWeight))
            el.Add(new XAttribute(NsFo + "font-weight", props.FontWeight));

        if (!string.IsNullOrEmpty(props.FontStyle))
            el.Add(new XAttribute(NsFo + "font-style", props.FontStyle));

        if (!string.IsNullOrEmpty(props.Color))
            el.Add(new XAttribute(NsFo + "color", props.Color));

        return el;
    }
}
