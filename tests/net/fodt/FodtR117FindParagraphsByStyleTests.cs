// Tests for FodtDocument.FindParagraphsByStyle
// Sprint: FORMAT-FACTORY-FODT-FIND-BY-STYLE-20260626
// Ledger: R117-GOVERNED-DOTNET-FODT-FIND-BY-STYLE-001

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R117 Train A: FindParagraphsByStyle — returns indices of paragraphs whose
/// effective style name contains the given pattern (case-insensitive).
/// Heading elements (text:h) use synthetic style "Heading" when no explicit
/// style-name attribute is set.
/// </summary>
public class FodtR117FindParagraphsByStyleTests
{
    // ---- Basic matching ----

    [Fact]
    public void FindByStyle_EmptyDoc_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        var result = doc.FindParagraphsByStyle("Heading");
        Assert.Empty(result);
    }

    [Fact]
    public void FindByStyle_HeadingPattern_ReturnsHeadingIndices()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Chapter One", 1);
        doc.AppendParagraph("Body text here.");
        doc.InsertHeading(2, "Chapter Two", 1);

        var result = doc.FindParagraphsByStyle("Heading");

        Assert.Equal(2, result.Count);
        Assert.Contains(0, result);
        Assert.Contains(2, result);
    }

    [Fact]
    public void FindByStyle_HeadingPattern_DoesNotReturnBodyParagraphs()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("body paragraph");
        doc.InsertHeading(1, "A Heading", 1);

        var result = doc.FindParagraphsByStyle("Heading");

        Assert.DoesNotContain(0, result);
    }

    // ---- Case-insensitive matching ----

    [Fact]
    public void FindByStyle_CaseInsensitive_UppercasePattern()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Introduction", 1);
        doc.AppendParagraph("Body text.");

        var upper = doc.FindParagraphsByStyle("HEADING");
        var lower = doc.FindParagraphsByStyle("heading");
        var mixed = doc.FindParagraphsByStyle("Heading");

        Assert.Equal(upper, lower);
        Assert.Equal(upper, mixed);
    }

    // ---- Index correctness ----

    [Fact]
    public void FindByStyle_ReturnsCorrectIndices_MixedContent()
    {
        var doc = FodtDocument.CreateEmpty();
        // 0: heading
        doc.InsertHeading(0, "Title", 1);
        // 1: body
        doc.AppendParagraph("Paragraph one.");
        // 2: heading
        doc.InsertHeading(2, "Section 2", 2);
        // 3: body
        doc.AppendParagraph("Paragraph two.");
        // 4: heading
        doc.InsertHeading(4, "Section 3", 2);

        var result = doc.FindParagraphsByStyle("Heading");

        Assert.Equal(new[] { 0, 2, 4 }, result);
    }

    [Fact]
    public void FindByStyle_NonMatchingPattern_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some text.");
        doc.InsertHeading(1, "A Heading", 1);

        var result = doc.FindParagraphsByStyle("FooterStyle");

        Assert.Empty(result);
    }

    // ---- Paragraph count consistency ----

    [Fact]
    public void FindByStyle_AllHeadings_CountMatchesGetHeadingCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "H1", 1);
        doc.AppendParagraph("Body.");
        doc.InsertHeading(2, "H2", 2);
        doc.AppendParagraph("More body.");
        doc.InsertHeading(4, "H3", 3);

        var styleResult = doc.FindParagraphsByStyle("Heading");
        int headingCount = doc.GetHeadingCount();

        Assert.Equal(headingCount, styleResult.Count);
    }

    // ---- Null guard ----

    [Fact]
    public void FindByStyle_NullPattern_Throws()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Throws<ArgumentNullException>(() => doc.FindParagraphsByStyle(null!));
    }

    // ---- Dogfood pipeline ----

    [Fact]
    public void DogfoodPipeline_BuildOutline_FindByHeading_ExportSection()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Introduction", 1);
        doc.AppendParagraph("This section covers the basics.");
        doc.InsertHeading(2, "Core Concepts", 1);
        doc.AppendParagraph("Here we explain key ideas.");
        doc.InsertHeading(4, "Advanced Topics", 1);
        doc.AppendParagraph("For power users.");

        // Find all heading indices
        var headingIndices = doc.FindParagraphsByStyle("Heading");
        Assert.Equal(3, headingIndices.Count);

        // Verify the headings can be retrieved by index
        var paragraphs = doc.Paragraphs;
        foreach (var idx in headingIndices)
        {
            Assert.True(paragraphs[idx].IsHeading);
        }

        // Verify the word frequency excludes style matching
        var freq = doc.GetWordFrequency(minLength: 4);
        Assert.True(freq.Count > 0);
    }
}
