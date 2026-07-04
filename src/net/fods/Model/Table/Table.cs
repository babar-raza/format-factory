// FormatFactory.Fods — Model.Table.Table
// spec_qname: table:table
// spec_fact_ref: FACT-FODS-004
// Authority: plans/.claude/imperative-drifting-conway.md §2
// TC-W1-FODS-NET-001

using System.Collections.Generic;

namespace FormatFactory.Fods.Model.Table;

/// <summary>
/// Canonical runtime model for the ODF table:table element (a spreadsheet sheet/tab).
///
/// ODF 1.3 §9.1.2 — table:table is a single spreadsheet sheet.
/// spec_qname: table:table
/// spec_fact_ref: FACT-FODS-004
///
/// This class is the parser-populated runtime model. Public API wrapper:
/// <see cref="FormatFactory.Fods.FodsWorksheet"/>.
/// </summary>
public sealed class Table
{
    /// <summary>The ODF QName for this element.</summary>
    public const string SpecQName = "table:table";

    /// <summary>The SAL fact reference (sal-facts-latest.json).</summary>
    public const string SpecFactRef = "FACT-FODS-004";

    /// <summary>
    /// The table:name attribute — the user-visible sheet name.
    /// Required per ODF 1.3 §9.1.2.
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// All table:table-row elements in document order.
    /// Populated by FodsParser.
    /// </summary>
    public List<TableRow> Rows { get; } = new();

    /// <summary>
    /// All table:table-column elements in document order.
    /// Populated by FodsParser.
    /// </summary>
    public List<TableColumn> Columns { get; } = new();

    /// <summary>
    /// table:print attribute — whether this sheet is included in print range.
    /// </summary>
    public bool Print { get; set; } = true;

    /// <summary>
    /// table:display attribute — visible/hidden state of the sheet.
    /// </summary>
    public bool Display { get; set; } = true;
}
