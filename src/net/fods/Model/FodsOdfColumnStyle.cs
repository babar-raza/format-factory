// FormatFactory.Fods -- ODF column style property bag ( 3b)
// ODF basis: ODF 1.3 §9.1.6 table:table-column, §15.9.1 style:column-width

namespace FormatFactory.Fods;

/// <summary>
/// Immutable bag of ODF column style properties resolved through the style chain.
/// Populated by <see cref="FodsStyleResolver.ResolveColumnStyle"/>.
/// ODF spec: ODF 1.3 §15.9.1 style:table-column-properties.
/// </summary>
public sealed record FodsOdfColumnStyle
{
    /// <summary>
    /// Column width in points, parsed from style:table-column-properties/@style:column-width.
    /// Common ODF values are in "cm" (converted to pt: 1cm ≈ 28.3465pt) or "in".
    /// Returns 0.0 if no explicit width is defined.
    /// </summary>
    public double Width { get; init; }

    /// <summary>style:table-column-properties/@style:use-optimal-column-width.</summary>
    public bool UseOptimalWidth { get; init; }
}
