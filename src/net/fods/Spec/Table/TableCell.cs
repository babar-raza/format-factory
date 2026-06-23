// FormatFactory.Fods — Spec.Table.TableCell — Canonical spec-shaped model class
// spec_qname: table:table-cell
// spec_fact_ref: FACT-FODS-006
// TC-QHARD-050: converted from architecture_only stub to real model class
namespace FormatFactory.Fods.Spec.Table;

/// <summary>
/// Spec-shaped model class for the ODF table:table-cell element.
///
/// ODF 1.3 §9.4.5 — table:table-cell is the element representing a single
/// cell within a table:table-row in an ODF spreadsheet.
/// spec_qname: table:table-cell
/// spec_fact_ref: FACT-FODS-006
///
/// This is a canonical class in the Spec/ hierarchy. The facade wrapper is
/// FormatFactory.Fods.FodsCell (in Model/FodsCell.cs).
/// </summary>
public sealed class TableCell
{
    /// <summary>The ODF QName for this element. Grounded in ODF 1.3 §9.4.5.</summary>
    public const string SpecQName = "table:table-cell";

    /// <summary>The SAL fact reference for this element (sal-facts-latest.json).</summary>
    public const string SpecFactRef = "FACT-FODS-006";

    /// <summary>
    /// The office:value-type attribute — the cell's value type.
    /// Common values: "string", "float", "date", "boolean", "percentage", "currency".
    /// Per ODF 1.3 §9.4.5 and §6.7.1.
    /// </summary>
    public string? ValueType { get; init; }

    /// <summary>
    /// The plain-text content of this cell, from the first text:p child element.
    /// </summary>
    public string Content { get; init; } = string.Empty;

    /// <summary>Whether this is a table:covered-table-cell (merged/spanned cell).</summary>
    public bool IsCovered { get; init; }
}
