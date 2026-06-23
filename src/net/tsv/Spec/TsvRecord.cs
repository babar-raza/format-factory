// FormatFactory.Tsv — Spec.TsvRecord — Canonical spec-shaped model class
// spec_qname: tsv:record
// TC-QHARD-052: new canonical spec authority class for TSV format
namespace FormatFactory.Tsv.Spec;

/// <summary>
/// Canonical spec-shaped model class for a TSV record (data row).
///
/// A TSV record is a sequence of tab-separated fields (IANA text/tab-separated-values).
/// Each record corresponds to a row in the TSV document.
/// spec_qname: tsv:record
///
/// This is a canonical class in the Spec/ hierarchy. The facade wrapper is
/// FormatFactory.Tsv.TsvDocument (rows are exposed as string[]).
/// </summary>
public sealed class TsvRecord
{
    /// <summary>The spec QName for a TSV record element.</summary>
    public const string SpecQName = "tsv:record";

    /// <summary>The field values in this record (tab-separated).</summary>
    public IReadOnlyList<string> Fields { get; init; } = [];

    /// <summary>Number of fields in this record.</summary>
    public int FieldCount => Fields.Count;
}
