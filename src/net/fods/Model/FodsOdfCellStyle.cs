// FormatFactory.Fods -- ODF cell style property bag ( 3b)
// Resolved from the ODF style chain via FodsStyleResolver.
// ODF basis: ODF 1.3 §16 (Styles), §15.11 (Paragraph), §15.5 (Table cell)

namespace FormatFactory.Fods;

/// <summary>
/// Immutable bag of ODF cell style properties resolved through the style chain.
/// Populated by <see cref="FodsStyleResolver.ResolveCellStyle"/>.
/// ODF spec: ODF 1.3 §9.4.5 table:table-cell, §16.2 style:style.
/// </summary>
public sealed record FodsOdfCellStyle
{
    /// <summary>style:style/@style:name of the applied style.</summary>
    public string? StyleName { get; init; }

    /// <summary>style:paragraph-properties/@fo:text-align — e.g. "start", "center", "end".</summary>
    public string HorizontalAlignment { get; init; } = "start";

    /// <summary>style:table-cell-properties/@style:vertical-align — e.g. "bottom", "middle", "top".</summary>
    public string VerticalAlignment { get; init; } = "bottom";

    /// <summary>style:text-properties/@style:font-name.</summary>
    public string? FontName { get; init; }

    /// <summary>style:text-properties/@fo:font-size (parsed as double from e.g. "14pt").</summary>
    public double FontSize { get; init; }

    /// <summary>style:text-properties/@fo:color — hex string e.g. "#000000".</summary>
    public string? FontColor { get; init; }

    /// <summary>style:table-cell-properties/@fo:background-color — hex string.</summary>
    public string? BackgroundColor { get; init; }

    /// <summary>style:table-cell-properties/@fo:border — e.g. "0.05pt solid #000000".</summary>
    public string? BorderStyle { get; init; }

    /// <summary>style:text-properties/@style:text-underline-style — e.g. "none", "solid".</summary>
    public string Underline { get; init; } = "none";

    /// <summary>style:table-cell-properties/@style:shrink-to-fit — "true"/"false".</summary>
    public bool ShrinkToFit { get; init; }

    /// <summary>style:paragraph-properties/@fo:margin-left parsed as indent level (0-based).</summary>
    public int IndentLevel { get; init; }

    /// <summary>style:table-cell-properties/@style:rotation-angle in degrees.</summary>
    public int RotationAngle { get; init; }

    /// <summary>style:table-cell-properties/@style:cell-protect — "protected" or empty.</summary>
    public bool IsProtected { get; init; }

    /// <summary>style:text-properties/@style:text-line-through-style — "none" or "solid".</summary>
    public string Strikethrough { get; init; } = "none";

    /// <summary>style:text-properties/@fo:font-style — "normal" or "italic".</summary>
    public string FontStyle { get; init; } = "normal";
}
