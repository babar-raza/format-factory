// FormatFactory.Fods — Model.Text.Span
// spec_qname: text:span
// spec_fact_ref: FACT-FODS-021
// Authority: plans/.claude/imperative-drifting-conway.md §2
// TC-W1-FODS-NET-002

namespace FormatFactory.Fods.Model.Text;

/// <summary>
/// Canonical runtime model for the ODF text:span element.
///
/// ODF 1.3 §5.1.5 — text:span is a formatted run of text within a paragraph.
/// spec_qname: text:span
/// spec_fact_ref: FACT-FODS-021
/// </summary>
public sealed class Span
{
    /// <summary>The ODF QName for this element.</summary>
    public const string SpecQName = "text:span";

    /// <summary>The SAL fact reference (sal-facts-latest.json).</summary>
    public const string SpecFactRef = "FACT-FODS-021";

    /// <summary>The text content of this span.</summary>
    public string Text { get; set; } = string.Empty;

    /// <summary>text:style-name attribute — character style reference.</summary>
    public string? StyleName { get; set; }
}
