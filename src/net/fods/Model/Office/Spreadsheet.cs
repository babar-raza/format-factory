// FormatFactory.Fods — Model.Office.Spreadsheet
// spec_qname: office:spreadsheet
// spec_fact_ref: FACT-FODS-003
// Authority: plans/.claude/imperative-drifting-conway.md §2
// TC-W1-FODS-NET-001

using System.Collections.Generic;
using TableModel = FormatFactory.Fods.Model.Table.Table;

namespace FormatFactory.Fods.Model.Office;

/// <summary>
/// Canonical runtime model for the ODF office:spreadsheet body element.
///
/// ODF 1.3 §3.7 — office:spreadsheet is the body element of a spreadsheet document.
/// spec_qname: office:spreadsheet
/// spec_fact_ref: FACT-FODS-003
///
/// This class is the parser-populated runtime model.
/// </summary>
public sealed class Spreadsheet
{
    /// <summary>The ODF QName for this element.</summary>
    public const string SpecQName = "office:spreadsheet";

    /// <summary>The SAL fact reference (sal-facts-latest.json).</summary>
    public const string SpecFactRef = "FACT-FODS-003";

    /// <summary>
    /// All table:table (sheet) elements in document order.
    /// Populated by FodsParser from the XML DOM.
    /// </summary>
    public List<TableModel> Tables { get; } = new();
}
