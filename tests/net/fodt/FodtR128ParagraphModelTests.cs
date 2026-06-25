// Tests for FodtParagraph model properties: Text, IsHeading, OutlineLevel.
// Sprint: FORMAT-FACTORY-FODT-PARAGRAPH-MODEL-20260626
// Ledger: R128-GOVERNED-DOTNET-FODT-PARAGRAPH-MODEL-001

using System;
using System.Linq;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R128: FodtParagraph model accessed via FodtDocument.Paragraphs collection.
/// FodtParagraph.Text returns the paragraph content string.
/// FodtParagraph.IsHeading is true only for heading elements.
/// FodtParagraph.OutlineLevel returns the heading level (1–6) or 0 for body paragraphs.
/// </summary>
public class FodtR128ParagraphModelTests
{
    // ---- Text property ----

    [Fact]
    public void ParagraphText_AppendedParagraph_MatchesOriginal()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello, world!");

        var para = doc.Paragraphs[0];
        Assert.Equal("Hello, world!", para.Text);
    }

    [Fact]
    public void ParagraphText_MultipleAppends_AllTextCorrect()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        doc.AppendParagraph("Third");

        Assert.Equal("First", doc.Paragraphs[0].Text);
        Assert.Equal("Second", doc.Paragraphs[1].Text);
        Assert.Equal("Third", doc.Paragraphs[2].Text);
    }

    [Fact]
    public void ParagraphText_AfterSetParagraphText_Reflects()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Original text");
        doc.SetParagraphText(0, "Updated text");

        Assert.Equal("Updated text", doc.Paragraphs[0].Text);
    }

    // ---- IsHeading property ----

    [Fact]
    public void IsHeading_BodyParagraph_IsFalse()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Body paragraph");

        Assert.False(doc.Paragraphs[0].IsHeading);
    }

    [Fact]
    public void IsHeading_HeadingParagraph_IsTrue()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("My Heading", level: 1);

        Assert.True(doc.Paragraphs[0].IsHeading);
    }

    [Fact]
    public void IsHeading_MixedContent_CorrectForEach()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("H1", level: 1);
        doc.AppendParagraph("Body");
        doc.AppendHeading("H2", level: 2);

        Assert.True(doc.Paragraphs[0].IsHeading);
        Assert.False(doc.Paragraphs[1].IsHeading);
        Assert.True(doc.Paragraphs[2].IsHeading);
    }

    // ---- OutlineLevel property ----

    [Fact]
    public void OutlineLevel_BodyParagraph_IsZeroOrNegative()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Body text");

        // Non-heading paragraphs have no outline level (0 or -1 by convention)
        var level = doc.Paragraphs[0].OutlineLevel;
        Assert.True(level <= 0,
            $"Body paragraph OutlineLevel should be 0 or negative, got {level}");
    }

    [Fact]
    public void OutlineLevel_H1Heading_IsOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Level 1", level: 1);

        Assert.Equal(1, doc.Paragraphs[0].OutlineLevel);
    }

    [Fact]
    public void OutlineLevel_H2Heading_IsTwo()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Level 2", level: 2);

        Assert.Equal(2, doc.Paragraphs[0].OutlineLevel);
    }

    [Fact]
    public void OutlineLevel_H3Heading_IsThree()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Level 3", level: 3);

        Assert.Equal(3, doc.Paragraphs[0].OutlineLevel);
    }

    // ---- Dogfood: iterate Paragraphs and inspect model ----

    [Fact]
    public void DogfoodPipeline_IterateParagraphs_HeadingsMatchGetHeadingTexts()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", level: 1);
        doc.AppendParagraph("Introduction.");
        doc.AppendHeading("Section A", level: 2);
        doc.AppendParagraph("Content A.");

        // Collect heading texts via model iteration
        var headingTextsViaModel = doc.Paragraphs
            .Where(p => p.IsHeading)
            .Select(p => p.Text)
            .ToList();

        // Compare with GetHeadingTexts()
        var headingTextsViaApi = doc.GetHeadingTexts();

        Assert.Equal(headingTextsViaApi.Count, headingTextsViaModel.Count);
        for (int i = 0; i < headingTextsViaApi.Count; i++)
            Assert.Equal(headingTextsViaApi[i], headingTextsViaModel[i]);
    }
}
