// FormatFactory.Fods — Spec.Table.TableRow — Canonical spec-shaped model class
// spec_qname: table:table-row
// spec_fact_ref: FACT-FODS-005
// TC-QHARD-050: converted from architecture_only stub to real model class
namespace FormatFactory.Fods.Spec.Table;

/// <summary>
/// Spec-shaped model class for the ODF table:table-row element.
///
/// ODF 1.3 §9.1.3 — table:table-row is an element representing a single row
/// within a table:table element in an ODF spreadsheet.
/// spec_qname: table:table-row
/// spec_fact_ref: FACT-FODS-005
///
/// This is a canonical class in the Spec/ hierarchy.
/// </summary>
public sealed class TableRow
{
    /// <summary>The ODF QName for this element. Grounded in ODF 1.3 §9.1.3.</summary>
    public const string SpecQName = "table:table-row";

    /// <summary>The SAL fact reference for this element (sal-facts-latest.json).</summary>
    public const string SpecFactRef = "FACT-FODS-005";

    /// <summary>Number of table:table-cell elements in this row.</summary>
    public int CellCount { get; init; }

    /// <summary>
    /// The table:style-name attribute — row style name, if present.
    /// </summary>
    public string? StyleName { get; init; }
}
