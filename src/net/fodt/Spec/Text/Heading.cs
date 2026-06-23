// FormatFactory.Fodt — Spec.Text.Heading — Canonical spec-shaped model class
// spec_qname: text:h
// spec_fact_ref: FACT-FODT-004
// TC-QHARD-051: converted from architecture_only stub to real model class
namespace FormatFactory.Fodt.Spec.Text;

/// <summary>
/// Spec-shaped model class for the ODF text:h (heading) element.
///
/// ODF 1.3 §5.1.2 — text:h is the canonical heading element in ODF text
/// documents. The text:outline-level attribute specifies the heading depth (1–10).
/// spec_qname: text:h
/// spec_fact_ref: FACT-FODT-004
/// </summary>
public sealed class Heading
{
    /// <summary>The ODF QName for this element. Grounded in ODF 1.3 §5.1.2.</summary>
    public const string SpecQName = "text:h";

    /// <summary>The SAL fact reference for this element (sal-facts-latest.json).</summary>
    public const string SpecFactRef = "FACT-FODT-004";

    /// <summary>
    /// The text:outline-level attribute — heading depth, 1–10.
    /// Per ODF 1.3 §5.1.2.
    /// </summary>
    public int OutlineLevel { get; init; } = 1;

    /// <summary>The plain-text content of this heading element.</summary>
    public string Content { get; init; } = string.Empty;

    /// <summary>The text:style-name attribute value, if present. May be null.</summary>
    public string? StyleName { get; init; }
}
