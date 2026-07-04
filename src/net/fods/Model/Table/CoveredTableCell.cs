// FormatFactory.Fods — Model.Table.CoveredTableCell
// spec_qname: table:covered-table-cell
// spec_fact_ref: FACT-FODS-007
// Authority: plans/.claude/imperative-drifting-conway.md §2
// TC-W1-FODS-NET-001

namespace FormatFactory.Fods.Model.Table;

/// <summary>
/// Canonical runtime model for the ODF table:covered-table-cell element.
///
/// ODF 1.3 §9.4.6 — table:covered-table-cell represents a cell that is covered
/// by a spanning cell in a merged range.
/// spec_qname: table:covered-table-cell
/// spec_fact_ref: FACT-FODS-007
/// </summary>
public sealed class CoveredTableCell
{
    /// <summary>The ODF QName for this element.</summary>
    public const string SpecQName = "table:covered-table-cell";

    /// <summary>The SAL fact reference (sal-facts-latest.json).</summary>
    public const string SpecFactRef = "FACT-FODS-007";

    /// <summary>table:style-name attribute — the covered cell's style.</summary>
    public string? StyleName { get; set; }

    /// <summary>
    /// table:number-columns-repeated — repeat count for empty covered cells.
    /// Default: 1.
    /// </summary>
    public int RepeatCount { get; set; } = 1;
}
