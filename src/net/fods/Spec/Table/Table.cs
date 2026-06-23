// FormatFactory.Fods — Spec.Table.Table — Canonical spec-shaped model class
// spec_qname: table:table
// spec_fact_ref: FACT-FODS-004
// TC-QHARD-050: converted from architecture_only stub to real model class
namespace FormatFactory.Fods.Spec.Table;

/// <summary>
/// Spec-shaped model class for the ODF table:table element.
///
/// ODF 1.3 §9.1.2 — table:table is the element representing a single
/// spreadsheet sheet within an ODF spreadsheet document.
/// spec_qname: table:table
/// spec_fact_ref: FACT-FODS-004
///
/// This is a canonical class in the Spec/ hierarchy. The facade wrapper is
/// FormatFactory.Fods.FodsSheet (in Model/FodsSheet.cs).
/// </summary>
public sealed class Table
{
    /// <summary>The ODF QName for this element. Grounded in ODF 1.3 §9.1.2.</summary>
    public const string SpecQName = "table:table";

    /// <summary>The SAL fact reference for this element (sal-facts-latest.json).</summary>
    public const string SpecFactRef = "FACT-FODS-004";

    /// <summary>
    /// The table:name attribute — the user-visible sheet name.
    /// Required per ODF 1.3 §9.1.2.
    /// </summary>
    public string Name { get; init; } = string.Empty;

    /// <summary>Number of table:table-row elements in this table.</summary>
    public int RowCount { get; init; }
}
