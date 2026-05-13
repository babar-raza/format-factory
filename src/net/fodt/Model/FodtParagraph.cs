// FormatFactory.Fodt -- Commercial .NET FODT Model -- FodtParagraph
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: commercial_readiness_in_progress (NOT approved)

using System;
using System.Xml.Linq;

namespace FormatFactory.Fodt;

/// <summary>
/// Typed wrapper for an ODF text:p (paragraph) or text:h (heading) element.
/// Backed by the live XElement in the DOM — mutations write through to the document.
///
/// ODF spec basis:
///   ODF 1.3 §5.1.3  text:p — paragraph
///   ODF 1.3 §5.1.2  text:h — heading (exposed as paragraph with IsHeading=true)
///   ODF 1.3 §6.1.1  text:p text content rules
///
/// Local fact source: format_understanding/fodt/ (FUL-003 verified fact set)
///
/// Security: no deserialization; reads/writes through trusted XDocument loaded securely.
/// </summary>
public sealed class FodtParagraph
{
    private static readonly XNamespace NsText =
        "urn:oasis:names:tc:opendocument:xmlns:text:1.0";

    internal XElement Element { get; }

    internal FodtParagraph(XElement element)
    {
        Element = element;
    }

    /// <summary>
    /// Gets the plain-text content of this paragraph (all character data concatenated).
    /// Returns empty string if the paragraph is empty.
    ///
    /// Note: This reads the direct text content of the text:p / text:h element.
    /// Inline elements (text:span, text:a, etc.) contribute their character data as well
    /// through XElement.Value, which concatenates all descendant text nodes.
    /// </summary>
    public string Text => Element.Value;

    /// <summary>
    /// Sets the paragraph text by replacing all child content with a single text node.
    /// Inline formatting (spans, links, etc.) is intentionally removed on edit — this is
    /// a vertical slice implementation. Full inline formatting preservation is a future
    /// capability (roadmap).
    ///
    /// ODF citation: §5.1.3 — text:p may contain character data directly.
    /// Local fact source: format_understanding/fodt/
    /// </summary>
    /// <param name="value">The new plain-text content. Must not be null.</param>
    public void SetText(string value)
    {
        ArgumentNullException.ThrowIfNull(value);

        // Remove all children and replace with plain text node
        // XElement.Value setter replaces all child content with a text node
        Element.Value = value;
    }

    /// <summary>Whether this is a heading element (text:h) rather than a paragraph (text:p).</summary>
    public bool IsHeading => Element.Name.LocalName == "h";

    /// <summary>
    /// Heading outline level from text:outline-level attribute, or 0 if not a heading or
    /// the attribute is absent.
    /// </summary>
    public int OutlineLevel
    {
        get
        {
            if (!IsHeading) return 0;
            var attr = Element.Attribute(NsText + "outline-level");
            return int.TryParse(attr?.Value, out var level) ? level : 0;
        }
    }
}
