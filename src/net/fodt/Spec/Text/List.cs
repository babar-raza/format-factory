// FormatFactory.Fodt — Spec.Text.List — Canonical spec-shaped model class
// spec_qname: text:list
// spec_fact_ref: FACT-FODT-005
// TC-QHARD-051: converted from architecture_only stub to real model class
namespace FormatFactory.Fodt.Spec.Text;

/// <summary>
/// Spec-shaped model class for the ODF text:list element.
///
/// ODF 1.3 §5.3.1 — text:list is the container element for list items in an
/// ODF text document. It contains text:list-item children.
/// spec_qname: text:list
/// spec_fact_ref: FACT-FODT-005
/// </summary>
public sealed class List
{
    /// <summary>The ODF QName for this element. Grounded in ODF 1.3 §5.3.1.</summary>
    public const string SpecQName = "text:list";

    /// <summary>The SAL fact reference for this element (sal-facts-latest.json).</summary>
    public const string SpecFactRef = "FACT-FODT-005";

    /// <summary>Number of text:list-item children.</summary>
    public int ItemCount { get; init; }

    /// <summary>The text:style-name attribute — list style applied. May be null.</summary>
    public string? StyleName { get; init; }
}
