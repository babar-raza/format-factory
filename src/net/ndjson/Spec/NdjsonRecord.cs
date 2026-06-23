// FormatFactory.Ndjson — Spec.NdjsonRecord — Canonical spec-shaped model class
// spec_qname: ndjson:record
// TC-QHARD-052: new canonical spec authority class for NDJSON format
namespace FormatFactory.Ndjson.Spec;

/// <summary>
/// Canonical spec-shaped model class for an NDJSON record (a single JSON object line).
///
/// NDJSON (Newline-Delimited JSON) stores one JSON object per line.
/// Each line is an independent JSON record (ndjson.org spec).
/// spec_qname: ndjson:record
///
/// This is a canonical class in the Spec/ hierarchy. The facade wrapper is
/// FormatFactory.Ndjson.NdjsonDocument.
/// </summary>
public sealed class NdjsonRecord
{
    /// <summary>The spec QName for an NDJSON record element.</summary>
    public const string SpecQName = "ndjson:record";

    /// <summary>The raw JSON text of this record line (a single JSON object).</summary>
    public string RawJson { get; init; } = string.Empty;

    /// <summary>The zero-based line index of this record in the NDJSON stream.</summary>
    public int LineIndex { get; init; }
}
