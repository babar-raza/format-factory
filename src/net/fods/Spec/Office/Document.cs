// FormatFactory.Fods — Spec.Office.Document — Canonical spec-shaped model class
// spec_qname: office:document
// spec_fact_ref: FACT-FODS-001
// TC-QHARD-050: converted from architecture_only stub to real model class
namespace FormatFactory.Fods.Spec.Office;

/// <summary>
/// Spec-shaped model class for the ODF office:document element.
///
/// ODF 1.3 §3.1.2 — office:document is the root element of a flat ODF
/// spreadsheet document (single-XML form, .fods).
/// spec_qname: office:document
/// spec_fact_ref: FACT-FODS-001
///
/// This is a canonical class in the Spec/ hierarchy. The facade wrapper is
/// FormatFactory.Fods.FodsDocument (in FodsDocument.cs).
/// </summary>
public sealed class Document
{
    /// <summary>The ODF QName for this element. Grounded in ODF 1.3 §3.1.2.</summary>
    public const string SpecQName = "office:document";

    /// <summary>The SAL fact reference for this element (sal-facts-latest.json).</summary>
    public const string SpecFactRef = "FACT-FODS-001";

    /// <summary>
    /// The office:mimetype attribute value.
    /// For FODS this is "application/vnd.oasis.opendocument.spreadsheet".
    /// </summary>
    public string MimeType { get; init; } =
        "application/vnd.oasis.opendocument.spreadsheet";

    /// <summary>
    /// The office:version attribute value, e.g. "1.3".
    /// </summary>
    public string? Version { get; init; }

    /// <summary>Number of table:table elements (sheets) in this document.</summary>
    public int SheetCount { get; init; }
}
