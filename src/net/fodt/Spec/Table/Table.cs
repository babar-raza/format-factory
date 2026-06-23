// FormatFactory.Fodt — Spec.Table.Table — Canonical spec-shaped model class
// spec_qname: table:table
// spec_fact_ref: FACT-FODT-007
// TC-QHARD-051: converted from architecture_only stub to real model class
namespace FormatFactory.Fodt.Spec.Table;

/// <summary>
/// Spec-shaped model class for the ODF table:table element as it appears in
/// an ODF text document (FODT context).
///
/// ODF 1.3 §9.1.2 — table:table represents a table embedded in a text document.
/// spec_qname: table:table
/// spec_fact_ref: FACT-FODT-007
/// </summary>
public sealed class Table
{
    /// <summary>The ODF QName for this element. Grounded in ODF 1.3 §9.1.2.</summary>
    public const string SpecQName = "table:table";

    /// <summary>The SAL fact reference for this element (sal-facts-latest.json).</summary>
    public const string SpecFactRef = "FACT-FODT-007";

    /// <summary>The table:name attribute — the table name. May be null.</summary>
    public string? Name { get; init; }

    /// <summary>Number of table:table-row elements in this table.</summary>
    public int RowCount { get; init; }
}
