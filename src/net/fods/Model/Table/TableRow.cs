// FormatFactory.Fods — Model.Table.TableRow
// spec_qname: table:table-row
// spec_fact_ref: FACT-FODS-005
// Authority: plans/.claude/imperative-drifting-conway.md §2
// TC-W1-FODS-NET-001

using System.Collections.Generic;

namespace FormatFactory.Fods.Model.Table;

/// <summary>
/// Canonical runtime model for the ODF table:table-row element.
///
/// ODF 1.3 §9.4.4 — table:table-row is a row within a table:table.
/// spec_qname: table:table-row
/// spec_fact_ref: FACT-FODS-005
///
/// Public API wrapper: <see cref="FormatFactory.Fods.FodsRow"/>.
/// </summary>
public sealed class TableRow
{
    /// <summary>The ODF QName for this element.</summary>
    public const string SpecQName = "table:table-row";

    /// <summary>The SAL fact reference (sal-facts-latest.json).</summary>
    public const string SpecFactRef = "FACT-FODS-005";

    /// <summary>
    /// All table:table-cell and table:covered-table-cell elements in document order.
    /// Populated by FodsParser.
    /// </summary>
    public List<TableCell> Cells { get; } = new();

    /// <summary>
    /// table:number-rows-repeated attribute — row repeat count.
    /// Default: 1.
    /// </summary>
    public int RepeatCount { get; set; } = 1;

    /// <summary>
    /// table:style-name attribute — row style reference.
    /// </summary>
    public string? StyleName { get; set; }
}
