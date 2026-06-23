// FormatFactory.Fodt — Spec.Table.TableCell — Canonical spec-shaped model class
// spec_qname: table:table-cell
// spec_fact_ref: FACT-FODT-007
// TC-QHARD-051: converted from architecture_only stub to real model class
namespace FormatFactory.Fodt.Spec.Table;

/// <summary>
/// Spec-shaped model class for the ODF table:table-cell element as it appears
/// in an ODF text document (FODT context).
///
/// ODF 1.3 §9.4.5 — table:table-cell is a single cell within a table:table-row.
/// spec_qname: table:table-cell
/// spec_fact_ref: FACT-FODT-007
/// </summary>
public sealed class TableCell
{
    /// <summary>The ODF QName for this element. Grounded in ODF 1.3 §9.4.5.</summary>
    public const string SpecQName = "table:table-cell";

    /// <summary>The SAL fact reference for this element (sal-facts-latest.json).</summary>
    public const string SpecFactRef = "FACT-FODT-007";

    /// <summary>The plain-text content of this cell (from its text:p children).</summary>
    public string Content { get; init; } = string.Empty;

    /// <summary>Whether this cell element is table:covered-table-cell (merged/spanned).</summary>
    public bool IsCovered { get; init; }
}
