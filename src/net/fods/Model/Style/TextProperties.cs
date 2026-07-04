// FormatFactory.Fods — Model.Style.TextProperties
// spec_qname: style:text-properties
// spec_fact_ref: FACT-FODS-012
// Authority: plans/.claude/imperative-drifting-conway.md §2
// TC-W1-FODS-NET-002

namespace FormatFactory.Fods.Model.Style;

/// <summary>
/// Canonical runtime model for the ODF style:text-properties element.
///
/// ODF 1.3 §17.19 — style:text-properties defines text-level formatting.
/// spec_qname: style:text-properties
/// spec_fact_ref: FACT-FODS-012
/// </summary>
public sealed class TextProperties
{
    /// <summary>The ODF QName for this element.</summary>
    public const string SpecQName = "style:text-properties";

    /// <summary>The SAL fact reference (sal-facts-latest.json).</summary>
    public const string SpecFactRef = "FACT-FODS-012";

    /// <summary>fo:font-family attribute — the font name.</summary>
    public string? FontName { get; set; }

    /// <summary>fo:font-size attribute — font size with unit (e.g. "12pt").</summary>
    public string? FontSize { get; set; }

    /// <summary>fo:font-weight attribute — "bold" or "normal".</summary>
    public string? FontWeight { get; set; }

    /// <summary>fo:font-style attribute — "italic" or "normal".</summary>
    public string? FontStyle { get; set; }

    /// <summary>fo:color attribute — text color (e.g. "#000000").</summary>
    public string? Color { get; set; }
}
