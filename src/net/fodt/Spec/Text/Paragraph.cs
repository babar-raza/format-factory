// FormatFactory.Fodt — Spec.Text.Paragraph — Canonical spec-shaped model class (pilot)
// spec_qname: text:p
// spec_fact_ref: FACT-FODT-003 (ODF 1.3 §5.1.3)
namespace FormatFactory.Fodt.Spec.Text;

/// <summary>
/// Spec-shaped model class for the ODF text:p (paragraph) element.
///
/// ODF 1.3 §5.1.3 — text:p is the canonical paragraph element in ODF text documents.
/// spec_qname: text:p
/// spec_fact_ref: FACT-FODT-003
///
/// This is a canonical class in the Spec/ hierarchy. The facade wrapper is
/// FormatFactory.Fodt.FodtParagraph (in Model/).
/// </summary>
public sealed class Paragraph
{
    /// <summary>The ODF QName for this element. Grounded in ODF 1.3 §5.1.3.</summary>
    public const string SpecQName = "text:p";

    /// <summary>The SAL fact reference for this element (sal-facts-latest.json).</summary>
    public const string SpecFactRef = "FACT-FODT-003";

    /// <summary>The text:style-name attribute value, if present. May be null.</summary>
    public string? StyleName { get; init; }

    /// <summary>The plain-text content of this paragraph element.</summary>
    public string Content { get; init; } = string.Empty;

    /// <summary>Inline spans contained in this paragraph (text:span elements).</summary>
    public IReadOnlyList<string> Spans { get; init; } = [];
}
