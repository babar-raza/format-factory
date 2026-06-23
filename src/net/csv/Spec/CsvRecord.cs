// FormatFactory.Csv — Spec.CsvRecord — Canonical spec-shaped model class
// spec_qname: csv:record
// TC-QHARD-052: new canonical spec authority class for CSV format
namespace FormatFactory.Csv.Spec;

/// <summary>
/// Canonical spec-shaped model class for a CSV record (data row).
///
/// A CSV record is a sequence of fields separated by a delimiter character
/// (RFC 4180 §2). Each record corresponds to a row in the CSV document.
/// spec_qname: csv:record
///
/// This is a canonical class in the Spec/ hierarchy. The facade wrapper is
/// FormatFactory.Csv.CsvDocument (rows are exposed as string[]).
/// </summary>
public sealed class CsvRecord
{
    /// <summary>The spec QName for a CSV record element.</summary>
    public const string SpecQName = "csv:record";

    /// <summary>The field values in this record.</summary>
    public IReadOnlyList<string> Fields { get; init; } = [];

    /// <summary>Number of fields in this record.</summary>
    public int FieldCount => Fields.Count;
}
