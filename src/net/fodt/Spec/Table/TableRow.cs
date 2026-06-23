// FormatFactory.Fodt — Spec.Table.TableRow — Canonical spec-shaped model class
// spec_qname: table:table-row
// spec_fact_ref: FACT-FODT-007
namespace FormatFactory.Fodt.Spec.Table;

/// <summary>
/// Spec-shaped model class for the ODF table:table-row element.
///
/// ODF 1.3 §9.1.3 — table:table-row represents a single row within a table:table
/// element in an ODF text document.
/// spec_qname: table:table-row
/// spec_fact_ref: FACT-FODT-007
/// </summary>
public sealed class TableRow
{
    /// <summary>The ODF QName for this element. Grounded in ODF 1.3 §9.1.3.</summary>
    public const string SpecQName = "table:table-row";

    /// <summary>The SAL fact reference for this element (sal-facts-latest.json).</summary>
    public const string SpecFactRef = "FACT-FODT-007";

    /// <summary>Number of table:table-cell elements in this row.</summary>
    public int CellCount { get; init; }

    /// <summary>The table:style-name attribute — row style. May be null.</summary>
    public string? StyleName { get; init; }
}
