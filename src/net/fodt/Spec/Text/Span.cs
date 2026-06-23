// FormatFactory.Fodt — Spec.Text.Span — Canonical spec-shaped model class
// spec_qname: text:span
// spec_fact_ref: FACT-FODT-006
namespace FormatFactory.Fodt.Spec.Text;

/// <summary>
/// Spec-shaped model class for the ODF text:span element.
///
/// ODF 1.3 §5.1.5 — text:span is an inline character-style element used to
/// apply character formatting to a run of text within a text:p or text:h element.
/// spec_qname: text:span
/// spec_fact_ref: FACT-FODT-006
/// </summary>
public sealed class Span
{
    /// <summary>The ODF QName for this element. Grounded in ODF 1.3 §5.1.5.</summary>
    public const string SpecQName = "text:span";

    /// <summary>The SAL fact reference for this element (sal-facts-latest.json).</summary>
    public const string SpecFactRef = "FACT-FODT-006";

    /// <summary>The text:style-name attribute value — the character style applied. May be null.</summary>
    public string? StyleName { get; init; }

    /// <summary>The plain-text content of this span element.</summary>
    public string Content { get; init; } = string.Empty;
}
