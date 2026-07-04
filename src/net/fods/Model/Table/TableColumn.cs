// FormatFactory.Fods — Model.Table.TableColumn
// spec_qname: table:table-column
// spec_fact_ref: FACT-FODS-008
// Authority: plans/.claude/imperative-drifting-conway.md §2
// TC-W1-FODS-NET-001

namespace FormatFactory.Fods.Model.Table;

/// <summary>
/// Canonical runtime model for the ODF table:table-column element.
///
/// ODF 1.3 §9.4.3 — table:table-column defines column-level properties.
/// spec_qname: table:table-column
/// spec_fact_ref: FACT-FODS-008
/// </summary>
public sealed class TableColumn
{
    /// <summary>The ODF QName for this element.</summary>
    public const string SpecQName = "table:table-column";

    /// <summary>The SAL fact reference (sal-facts-latest.json).</summary>
    public const string SpecFactRef = "FACT-FODS-008";

    /// <summary>table:style-name — the column style reference.</summary>
    public string? StyleName { get; set; }

    /// <summary>
    /// table:number-columns-repeated — how many columns this element represents.
    /// Default: 1.
    /// </summary>
    public int RepeatCount { get; set; } = 1;

    /// <summary>table:visibility — "visible" (default), "collapse", or "filter".</summary>
    public string Visibility { get; set; } = "visible";

    /// <summary>table:default-cell-style-name — default cell style for this column.</summary>
    public string? DefaultCellStyleName { get; set; }
}
