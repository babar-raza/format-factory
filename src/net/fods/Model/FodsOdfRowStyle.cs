// FormatFactory.Fods -- ODF row style property bag (GI-FODS-NET-001 Phase 3b)
// ODF basis: ODF 1.3 §9.1.3 table:table-row, §15.9.3 style:row-height

namespace FormatFactory.Fods;

/// <summary>
/// Immutable bag of ODF row style properties resolved through the style chain.
/// Populated by <see cref="FodsStyleResolver.ResolveRowStyle"/>.
/// ODF spec: ODF 1.3 §15.9.3 style:table-row-properties.
/// </summary>
public sealed record FodsOdfRowStyle
{
    /// <summary>
    /// Row height in points, parsed from style:table-row-properties/@style:row-height.
    /// Common ODF values are in "cm". Returns 0.0 if no explicit height is defined.
    /// </summary>
    public double Height { get; init; }

    /// <summary>style:table-row-properties/@style:use-optimal-row-height.</summary>
    public bool UseOptimalHeight { get; init; }
}
