// FormatFactory.Fods — Model.Table.TableCell
// spec_qname: table:table-cell
// spec_fact_ref: FACT-FODS-006
// Authority: plans/.claude/imperative-drifting-conway.md §2
// TC-W1-FODS-NET-001

namespace FormatFactory.Fods.Model.Table;

/// <summary>
/// Canonical runtime model for the ODF table:table-cell element.
///
/// ODF 1.3 §9.4.5 — table:table-cell represents a single cell in a spreadsheet.
/// spec_qname: table:table-cell
/// spec_fact_ref: FACT-FODS-006
///
/// Public API wrapper: <see cref="FormatFactory.Fods.FodsCell"/>.
/// </summary>
public sealed class TableCell
{
    /// <summary>The ODF QName for this element.</summary>
    public const string SpecQName = "table:table-cell";

    /// <summary>The SAL fact reference (sal-facts-latest.json).</summary>
    public const string SpecFactRef = "FACT-FODS-006";

    /// <summary>
    /// office:value-type attribute — the cell's value type.
    /// Common values: "string", "float", "date", "boolean", "percentage", "currency".
    /// Per ODF 1.3 §9.4.5 and §6.7.1.
    /// </summary>
    public string? ValueType { get; set; }

    /// <summary>
    /// The cell's text/string value — from the first text:p child element.
    /// For numeric cells, this is the formatted display string.
    /// </summary>
    public string? Value { get; set; }

    /// <summary>
    /// office:value attribute — the numeric value for float/currency/percentage cells.
    /// </summary>
    public double? NumericValue { get; set; }

    /// <summary>
    /// table:formula attribute — the cell formula, e.g. "of:=A1+B1".
    /// Null if cell contains no formula.
    /// </summary>
    public string? Formula { get; set; }

    /// <summary>
    /// table:style-name attribute — the cell's style reference.
    /// </summary>
    public string? StyleName { get; set; }

    /// <summary>
    /// table:number-columns-spanned — column span for merged cells.
    /// Default: 1.
    /// </summary>
    public int ColumnSpan { get; set; } = 1;

    /// <summary>
    /// table:number-rows-spanned — row span for merged cells.
    /// Default: 1.
    /// </summary>
    public int RowSpan { get; set; } = 1;

    /// <summary>Whether this cell is a table:covered-table-cell (merged/covered).</summary>
    public bool IsCovered { get; set; }
}
