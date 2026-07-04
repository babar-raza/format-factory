// FormatFactory.Fods — Model.Style.TableCellProperties
// spec_qname: style:table-cell-properties
// spec_fact_ref: FACT-FODS-011
// Authority: plans/.claude/imperative-drifting-conway.md §2
// TC-W1-FODS-NET-002

namespace FormatFactory.Fods.Model.Style;

/// <summary>
/// Canonical runtime model for the ODF style:table-cell-properties element.
///
/// ODF 1.3 §17.18 — style:table-cell-properties defines cell-level formatting.
/// spec_qname: style:table-cell-properties
/// spec_fact_ref: FACT-FODS-011
/// </summary>
public sealed class TableCellProperties
{
    /// <summary>The ODF QName for this element.</summary>
    public const string SpecQName = "style:table-cell-properties";

    /// <summary>The SAL fact reference (sal-facts-latest.json).</summary>
    public const string SpecFactRef = "FACT-FODS-011";

    /// <summary>fo:background-color attribute — cell background color (e.g. "#FFFFFF").</summary>
    public string? BackgroundColor { get; set; }

    /// <summary>fo:wrap-option attribute — "wrap" or "no-wrap".</summary>
    public string? WrapOption { get; set; }

    /// <summary>style:vertical-align attribute — "top", "middle", "bottom".</summary>
    public string? VerticalAlign { get; set; }

    /// <summary>fo:text-align attribute — "start", "center", "end".</summary>
    public string? TextAlign { get; set; }

    /// <summary>fo:border attribute — shorthand border spec (e.g. "0.06pt solid #000000").</summary>
    public string? Border { get; set; }
}
