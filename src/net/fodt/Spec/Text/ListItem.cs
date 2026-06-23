// FormatFactory.Fodt — Spec.Text.ListItem — Canonical spec-shaped model class
// spec_qname: text:list-item
// spec_fact_ref: FACT-FODT-005
namespace FormatFactory.Fodt.Spec.Text;

/// <summary>
/// Spec-shaped model class for the ODF text:list-item element.
///
/// ODF 1.3 §5.3.2 — text:list-item is a single item within a text:list.
/// It typically contains one or more text:p children for the item text.
/// spec_qname: text:list-item
/// spec_fact_ref: FACT-FODT-005
/// </summary>
public sealed class ListItem
{
    /// <summary>The ODF QName for this element. Grounded in ODF 1.3 §5.3.2.</summary>
    public const string SpecQName = "text:list-item";

    /// <summary>The SAL fact reference for this element (sal-facts-latest.json).</summary>
    public const string SpecFactRef = "FACT-FODT-005";

    /// <summary>The plain-text content of this list item (from its text:p children).</summary>
    public string Content { get; init; } = string.Empty;
}
