// FormatFactory.Fods -- ODF Style Chain Resolver ( 3b)
// Standalone, stateless resolver: navigates office:automatic-styles → style:style parent chain.
// Gate 11 status: commercial_readiness_in_progress (NOT approved)
//
// ODF spec references:
//   §9.4.5  table:table-cell / @table:style-name
//   §16.2   style:style / @style:parent-style-name
//   §15.5   style:table-cell-properties
//   §15.11  style:paragraph-properties
//   §15.4   style:text-properties
//   §9.1.6  table:table-column / @table:style-name
//   §9.1.3  table:table-row / @table:style-name
//   §15.9   style:table-column-properties / style:table-row-properties

using System;
using System.Collections.Generic;
using System.Globalization;
using System.Xml.Linq;

namespace FormatFactory.Fods;

/// <summary>
/// Resolves ODF style chains from an XDocument and extracts typed property bags.
/// All methods are static and stateless — safe for multi-thread use on distinct XDocuments.
/// </summary>
public static class FodsStyleResolver
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
    // Public API
    // -------------------------------------------------------------------------

    /// <summary>
    /// Resolve the full ODF style chain for <paramref name="cell"/> and return
    /// a <see cref="FodsOdfCellStyle"/> with all available properties.
    /// Returns a default-valued instance if no style is applied or found.
    /// </summary>
    public static FodsOdfCellStyle ResolveCellStyle(XDocument doc, XElement cell)
    {
        if (doc is null || cell is null)
            return new FodsOdfCellStyle();

        string? styleName = cell.Attribute(NsTable + "style-name")?.Value;
        if (string.IsNullOrEmpty(styleName))
            return new FodsOdfCellStyle();

        var chain = BuildStyleChain(doc, styleName, "table-cell");
        return ExtractCellStyle(chain, styleName);
    }

    /// <summary>
    /// Resolve the ODF style for a <c>table:table-column</c> element and return
    /// a <see cref="FodsOdfColumnStyle"/>.
    /// </summary>
    public static FodsOdfColumnStyle ResolveColumnStyle(XDocument doc, XElement column)
    {
        if (doc is null || column is null)
            return new FodsOdfColumnStyle();

        string? styleName = column.Attribute(NsTable + "style-name")?.Value
                         ?? column.Attribute(NsTable + "default-cell-style-name")?.Value;
        if (string.IsNullOrEmpty(styleName))
            return new FodsOdfColumnStyle();

        var chain = BuildStyleChain(doc, styleName, "table-column");
        return ExtractColumnStyle(chain);
    }

    /// <summary>
    /// Resolve the ODF style for a <c>table:table-row</c> element and return
    /// a <see cref="FodsOdfRowStyle"/>.
    /// </summary>
    public static FodsOdfRowStyle ResolveRowStyle(XDocument doc, XElement row)
    {
        if (doc is null || row is null)
            return new FodsOdfRowStyle();

        string? styleName = row.Attribute(NsTable + "style-name")?.Value;
        if (string.IsNullOrEmpty(styleName))
            return new FodsOdfRowStyle();

        var chain = BuildStyleChain(doc, styleName, "table-row");
        return ExtractRowStyle(chain);
    }

    // -------------------------------------------------------------------------
    // Style chain builder
    // -------------------------------------------------------------------------

    /// <summary>
    /// Walk the style:style parent chain. Returns styles ordered from most-derived
    /// (index 0) to most-base (last index). Stops at cycle detection or missing parent.
    /// </summary>
    private static List<XElement> BuildStyleChain(XDocument doc, string styleName, string family)
    {
        var autoStyles = doc.Descendants(NsOffice + "automatic-styles").FirstOrDefault();
        var namedStyles = doc.Descendants(NsOffice + "styles").FirstOrDefault();

        var chain = new List<XElement>();
        var seen = new HashSet<string>(StringComparer.Ordinal);
        string? current = styleName;

        while (current is not null && !seen.Contains(current))
        {
            seen.Add(current);
            var el = FindStyle(autoStyles, current, family)
                  ?? FindStyle(namedStyles, current, family);
            if (el is null) break;
            chain.Add(el);
            current = el.Attribute(NsStyle + "parent-style-name")?.Value;
        }

        return chain;
    }

    private static XElement? FindStyle(XElement? container, string name, string family)
    {
        if (container is null) return null;
        foreach (var el in container.Elements(NsStyle + "style"))
        {
            if (el.Attribute(NsStyle + "name")?.Value == name &&
                el.Attribute(NsStyle + "family")?.Value == family)
                return el;
        }
        return null;
    }

    // -------------------------------------------------------------------------
    // Property extractors — walk chain from derived → base, first-wins
    // -------------------------------------------------------------------------

    private static FodsOdfCellStyle ExtractCellStyle(List<XElement> chain, string styleName)
    {
        string? hAlign = null;
        string? vAlign = null;
        string? fontName = null;
        double? fontSize = null;
        string? fontColor = null;
        string? bgColor = null;
        string? borderStyle = null;
        string? underline = null;
        bool? shrinkToFit = null;
        int? indentLevel = null;
        int? rotationAngle = null;
        bool? isProtected = null;
        string? strikethrough = null;

        foreach (var style in chain)
        {
            var cellProps = style.Element(NsStyle + "table-cell-properties");
            var paraProps = style.Element(NsStyle + "paragraph-properties");
            var textProps = style.Element(NsStyle + "text-properties");

            if (cellProps is not null)
            {
                vAlign     ??= cellProps.Attribute(NsStyle + "vertical-align")?.Value;
                bgColor    ??= cellProps.Attribute(NsFo + "background-color")?.Value;
                borderStyle??= cellProps.Attribute(NsFo + "border")?.Value;
                if (shrinkToFit is null)
                {
                    var stf = cellProps.Attribute(NsStyle + "shrink-to-fit")?.Value;
                    if (stf is not null) shrinkToFit = stf.Equals("true", StringComparison.OrdinalIgnoreCase);
                }
                if (rotationAngle is null)
                {
                    var ra = cellProps.Attribute(NsStyle + "rotation-angle")?.Value;
                    if (ra is not null && int.TryParse(ra, out int deg)) rotationAngle = deg;
                }
                if (isProtected is null)
                {
                    var prot = cellProps.Attribute(NsStyle + "cell-protect")?.Value;
                    if (prot is not null) isProtected = prot.Contains("protected", StringComparison.OrdinalIgnoreCase);
                }
            }

            if (paraProps is not null)
            {
                hAlign ??= paraProps.Attribute(NsFo + "text-align")?.Value;
                if (indentLevel is null)
                {
                    var ml = paraProps.Attribute(NsFo + "margin-left")?.Value;
                    if (ml is not null) indentLevel = ParseIndentLevel(ml);
                }
            }

            if (textProps is not null)
            {
                fontName  ??= textProps.Attribute(NsStyle + "font-name")?.Value;
                fontColor ??= textProps.Attribute(NsFo + "color")?.Value;
                underline ??= textProps.Attribute(NsStyle + "text-underline-style")?.Value;
                strikethrough ??= textProps.Attribute(NsStyle + "text-line-through-style")?.Value;
                if (fontSize is null)
                {
                    var fs = textProps.Attribute(NsFo + "font-size")?.Value;
                    if (fs is not null) fontSize = ParsePointValue(fs);
                }
            }
        }

        return new FodsOdfCellStyle
        {
            StyleName           = styleName,
            HorizontalAlignment = hAlign ?? "start",
            VerticalAlignment   = vAlign ?? "bottom",
            FontName            = fontName,
            FontSize            = fontSize ?? 0.0,
            FontColor           = fontColor,
            BackgroundColor     = bgColor,
            BorderStyle         = borderStyle,
            Underline           = underline ?? "none",
            ShrinkToFit         = shrinkToFit ?? false,
            IndentLevel         = indentLevel ?? 0,
            RotationAngle       = rotationAngle ?? 0,
            IsProtected         = isProtected ?? false,
            Strikethrough       = strikethrough ?? "none",
        };
    }

    private static FodsOdfColumnStyle ExtractColumnStyle(List<XElement> chain)
    {
        double? width = null;
        bool? optimal = null;

        foreach (var style in chain)
        {
            var colProps = style.Element(NsStyle + "table-column-properties");
            if (colProps is null) continue;

            if (width is null)
            {
                var w = colProps.Attribute(NsStyle + "column-width")?.Value;
                if (w is not null) width = ParsePointValue(w);
            }
            if (optimal is null)
            {
                var o = colProps.Attribute(NsStyle + "use-optimal-column-width")?.Value;
                if (o is not null) optimal = o.Equals("true", StringComparison.OrdinalIgnoreCase);
            }
        }

        return new FodsOdfColumnStyle
        {
            Width            = width ?? 0.0,
            UseOptimalWidth  = optimal ?? false,
        };
    }

    private static FodsOdfRowStyle ExtractRowStyle(List<XElement> chain)
    {
        double? height = null;
        bool? optimal = null;

        foreach (var style in chain)
        {
            var rowProps = style.Element(NsStyle + "table-row-properties");
            if (rowProps is null) continue;

            if (height is null)
            {
                var h = rowProps.Attribute(NsStyle + "row-height")?.Value;
                if (h is not null) height = ParsePointValue(h);
            }
            if (optimal is null)
            {
                var o = rowProps.Attribute(NsStyle + "use-optimal-row-height")?.Value;
                if (o is not null) optimal = o.Equals("true", StringComparison.OrdinalIgnoreCase);
            }
        }

        return new FodsOdfRowStyle
        {
            Height           = height ?? 0.0,
            UseOptimalHeight = optimal ?? false,
        };
    }

    // -------------------------------------------------------------------------
    // Unit conversion helpers
    // -------------------------------------------------------------------------

    private const double CmToPoints   = 28.3465;
    private const double InchToPoints = 72.0;
    private const double MmToPoints   = 2.83465;

    /// <summary>
    /// Parse an ODF length value (e.g. "14pt", "1.2cm", "0.5in", "3mm") to points.
    /// Returns 0.0 if unparseable.
    /// </summary>
    internal static double ParsePointValue(string value)
    {
        if (string.IsNullOrWhiteSpace(value)) return 0.0;
        value = value.Trim();

        if (value.EndsWith("pt", StringComparison.OrdinalIgnoreCase))
        {
            if (double.TryParse(value[..^2], NumberStyles.Float, CultureInfo.InvariantCulture, out double pt))
                return pt;
        }
        else if (value.EndsWith("cm", StringComparison.OrdinalIgnoreCase))
        {
            if (double.TryParse(value[..^2], NumberStyles.Float, CultureInfo.InvariantCulture, out double cm))
                return cm * CmToPoints;
        }
        else if (value.EndsWith("in", StringComparison.OrdinalIgnoreCase))
        {
            if (double.TryParse(value[..^2], NumberStyles.Float, CultureInfo.InvariantCulture, out double inches))
                return inches * InchToPoints;
        }
        else if (value.EndsWith("mm", StringComparison.OrdinalIgnoreCase))
        {
            if (double.TryParse(value[..^2], NumberStyles.Float, CultureInfo.InvariantCulture, out double mm))
                return mm * MmToPoints;
        }
        else
        {
            // Try bare number as points
            if (double.TryParse(value, NumberStyles.Float, CultureInfo.InvariantCulture, out double bare))
                return bare;
        }

        return 0.0;
    }

    /// <summary>
    /// Convert an ODF margin-left value to an approximate indent level (0-based).
    /// One indent level ≈ 0.5cm ≈ 14.17pt.
    /// </summary>
    private static int ParseIndentLevel(string marginLeft)
    {
        double pt = ParsePointValue(marginLeft);
        if (pt <= 0) return 0;
        return (int)Math.Round(pt / 14.17, MidpointRounding.AwayFromZero);
    }
}
