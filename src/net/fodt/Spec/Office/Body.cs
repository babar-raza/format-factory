// FormatFactory.Fodt — Spec.Office.Body — Canonical spec-shaped model class
// spec_qname: office:body
// spec_fact_ref: FACT-FODT-002
// TC-QHARD-051: converted from architecture_only stub to real model class
namespace FormatFactory.Fodt.Spec.Office;

/// <summary>
/// Spec-shaped model class for the ODF office:body element.
///
/// ODF 1.3 §3.3 — office:body is the container element holding the document
/// content within an office:document root. In an ODF text document it wraps
/// the office:text element.
/// spec_qname: office:body
/// spec_fact_ref: FACT-FODT-002
/// </summary>
public sealed class Body
{
    /// <summary>The ODF QName for this element. Grounded in ODF 1.3 §3.3.</summary>
    public const string SpecQName = "office:body";

    /// <summary>The SAL fact reference for this element (sal-facts-latest.json).</summary>
    public const string SpecFactRef = "FACT-FODT-002";

    /// <summary>Number of direct content children (paragraphs, headings, lists, tables).</summary>
    public int ChildCount { get; init; }
}
