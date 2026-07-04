// FormatFactory.Fods — Model.Style.Style
// spec_qname: style:style
// spec_fact_ref: FACT-FODS-010
// Authority: plans/.claude/imperative-drifting-conway.md §2
// TC-W1-FODS-NET-002

namespace FormatFactory.Fods.Model.Style;

/// <summary>
/// Canonical runtime model for the ODF style:style element.
///
/// ODF 1.3 §16.2 — style:style defines a reusable named style.
/// spec_qname: style:style
/// spec_fact_ref: FACT-FODS-010
/// </summary>
public sealed class Style
{
    /// <summary>The ODF QName for this element.</summary>
    public const string SpecQName = "style:style";

    /// <summary>The SAL fact reference (sal-facts-latest.json).</summary>
    public const string SpecFactRef = "FACT-FODS-010";

    /// <summary>style:name attribute — unique identifier for this style.</summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// style:family attribute — the style family (e.g. "table-cell", "table", "table-row").
    /// </summary>
    public string Family { get; set; } = string.Empty;

    /// <summary>
    /// style:parent-style-name attribute — the parent style this inherits from.
    /// </summary>
    public string? ParentStyleName { get; set; }

    /// <summary>
    /// style:table-cell-properties child element properties.
    /// Null if not present.
    /// </summary>
    public TableCellProperties? TableCellProperties { get; set; }

    /// <summary>
    /// style:text-properties child element properties.
    /// Null if not present.
    /// </summary>
    public TextProperties? TextProperties { get; set; }
}
