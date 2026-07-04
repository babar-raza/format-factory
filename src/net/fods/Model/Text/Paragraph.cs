// FormatFactory.Fods — Model.Text.Paragraph
// spec_qname: text:p
// spec_fact_ref: FACT-FODS-020
// Authority: plans/.claude/imperative-drifting-conway.md §2
// TC-W1-FODS-NET-002

using System.Collections.Generic;

namespace FormatFactory.Fods.Model.Text;

/// <summary>
/// Canonical runtime model for the ODF text:p (paragraph) element.
///
/// ODF 1.3 §5.1.3 — text:p is a text paragraph, used within cell content.
/// spec_qname: text:p
/// spec_fact_ref: FACT-FODS-020
/// </summary>
public sealed class Paragraph
{
    /// <summary>The ODF QName for this element.</summary>
    public const string SpecQName = "text:p";

    /// <summary>The SAL fact reference (sal-facts-latest.json).</summary>
    public const string SpecFactRef = "FACT-FODS-020";

    /// <summary>
    /// The plain text content of this paragraph.
    /// For cells with only text (no spans), this is the cell's display value.
    /// </summary>
    public string Text { get; set; } = string.Empty;

    /// <summary>text:style-name attribute — paragraph style reference.</summary>
    public string? StyleName { get; set; }

    /// <summary>text:span children — formatted runs within this paragraph.</summary>
    public List<Span> Spans { get; } = new();
}
