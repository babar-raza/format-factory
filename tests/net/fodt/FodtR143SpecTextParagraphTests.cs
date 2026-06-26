// Tests for FormatFactory.Fodt.Spec.Text.Paragraph, Heading, and Span model classes.
// Sprint: FORMAT-FACTORY-FODT-R143-20260627
// Ledger: R143-GOVERNED-DOTNET-FODT-SPEC-TEXT-PARAGRAPH-001

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R143: Tests for the canonical spec-shaped model classes in FormatFactory.Fodt.Spec.Text:
/// Paragraph (text:p, FACT-FODT-003),
/// Heading (text:h, FACT-FODT-004),
/// Span (text:span, FACT-FODT-006).
/// Covers: SpecQName constants; SpecFactRef constants; init-only property assignment;
/// Content; StyleName; OutlineLevel; Spans; IReadOnlyList assignment;
/// dogfood paragraph-spans composition pipeline.
/// ODF 1.3 basis: §5.1.2 (text:h), §5.1.3 (text:p), §5.1.5 (text:span).
/// </summary>
public class FodtR143SpecTextParagraphTests
{
    // -------------------------------------------------------------------------
    // Paragraph constants and properties
    // -------------------------------------------------------------------------

    [Fact]
    public void Paragraph_SpecQName_IsCorrect()
    {
        Assert.Equal("text:p", Spec.Text.Paragraph.SpecQName);
    }

    [Fact]
    public void Paragraph_SpecFactRef_IsCorrect()
    {
        Assert.Equal("FACT-FODT-003", Spec.Text.Paragraph.SpecFactRef);
    }

    [Fact]
    public void Paragraph_Content_IsAssignable()
    {
        var p = new Spec.Text.Paragraph { Content = "Hello, world." };
        Assert.Equal("Hello, world.", p.Content);
    }

    [Fact]
    public void Paragraph_Content_DefaultIsEmpty()
    {
        var p = new Spec.Text.Paragraph();
        Assert.Equal(string.Empty, p.Content);
    }

    [Fact]
    public void Paragraph_StyleName_NullByDefault()
    {
        var p = new Spec.Text.Paragraph();
        Assert.Null(p.StyleName);
    }

    [Fact]
    public void Paragraph_Spans_DefaultIsEmpty()
    {
        var p = new Spec.Text.Paragraph();
        Assert.Empty(p.Spans);
    }

    // -------------------------------------------------------------------------
    // Heading constants and properties
    // -------------------------------------------------------------------------

    [Fact]
    public void Heading_SpecQName_IsCorrect()
    {
        Assert.Equal("text:h", Spec.Text.Heading.SpecQName);
    }

    [Fact]
    public void Heading_SpecFactRef_IsCorrect()
    {
        Assert.Equal("FACT-FODT-004", Spec.Text.Heading.SpecFactRef);
    }

    [Fact]
    public void Heading_OutlineLevel_DefaultIsOne()
    {
        var h = new Spec.Text.Heading();
        Assert.Equal(1, h.OutlineLevel);
    }

    [Fact]
    public void Heading_OutlineLevel_IsAssignable()
    {
        var h = new Spec.Text.Heading { OutlineLevel = 3 };
        Assert.Equal(3, h.OutlineLevel);
    }

    // -------------------------------------------------------------------------
    // Span constants and properties
    // -------------------------------------------------------------------------

    [Fact]
    public void Span_SpecQName_IsCorrect()
    {
        Assert.Equal("text:span", Spec.Text.Span.SpecQName);
    }

    // -------------------------------------------------------------------------
    // Dogfood: paragraph → spans composition pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ParagraphWithSpans_HeadingAndParagraph()
    {
        var spans = new List<string> { "bold text", " normal text" };
        var para = new Spec.Text.Paragraph
        {
            Content = "bold text normal text",
            StyleName = "Default Paragraph Style",
            Spans = spans
        };
        var heading = new Spec.Text.Heading
        {
            Content = "Introduction",
            OutlineLevel = 1,
            StyleName = "Heading 1"
        };
        var inlineSpan = new Spec.Text.Span
        {
            Content = "bold text",
            StyleName = "Bold"
        };

        Assert.Equal(2, para.Spans.Count);
        Assert.Equal("Introduction", heading.Content);
        Assert.Equal(1, heading.OutlineLevel);
        Assert.Equal("Bold", inlineSpan.StyleName);
        Assert.Equal("text:span", Spec.Text.Span.SpecQName);
    }
}
