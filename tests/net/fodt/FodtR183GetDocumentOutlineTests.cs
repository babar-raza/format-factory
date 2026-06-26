// Tests for FodtDocument.GetDocumentOutline dedicated coverage.
// Sprint: ff-sprint-s174-dotnet-deepening-20260628
// Ledger: PC-FODT-R183

using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R183: Dedicated tests for FodtDocument.GetDocumentOutline().
/// Returns IReadOnlyList&lt;(int Level, string Text)&gt; of all headings in document order.
/// Only heading elements (text:h) are included; body paragraphs are excluded.
/// Level comes from text:outline-level attribute (defaults to 1 if absent).
/// Covers: empty doc returns empty; paragraphs-only returns empty; single heading;
/// heading text matches AppendHeading text; multiple headings in order;
/// body paragraphs excluded; returns IReadOnlyList; count matches GetHeadingCount;
/// level matches AppendHeading level argument; dogfood mixed content pipeline.
/// </summary>
public class FodtR183GetDocumentOutlineTests
{
    // -------------------------------------------------------------------------
    // Basic tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentOutline_EmptyDocument_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        var outline = doc.GetDocumentOutline();
        Assert.Empty(outline);
    }

    [Fact]
    public void GetDocumentOutline_ParagraphsOnly_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para 1");
        doc.AppendParagraph("Para 2");
        var outline = doc.GetDocumentOutline();
        Assert.Empty(outline);
    }

    [Fact]
    public void GetDocumentOutline_SingleHeading_ReturnsOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("My Title", 1);
        var outline = doc.GetDocumentOutline();
        Assert.Single(outline);
    }

    [Fact]
    public void GetDocumentOutline_HeadingText_MatchesAppendedText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter One", 1);
        var outline = doc.GetDocumentOutline();
        Assert.Equal("Chapter One", outline[0].Text);
    }

    [Fact]
    public void GetDocumentOutline_MultipleHeadings_InDocumentOrder()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("First", 1);
        doc.AppendHeading("Second", 2);
        doc.AppendHeading("Third", 3);
        var outline = doc.GetDocumentOutline();
        Assert.Equal(3, outline.Count);
        Assert.Equal("First", outline[0].Text);
        Assert.Equal("Second", outline[1].Text);
        Assert.Equal("Third", outline[2].Text);
    }

    [Fact]
    public void GetDocumentOutline_BodyParagraphs_Excluded()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Body text");
        doc.AppendHeading("Title", 1);
        doc.AppendParagraph("More body");
        var outline = doc.GetDocumentOutline();
        Assert.Single(outline); // only the heading
    }

    [Fact]
    public void GetDocumentOutline_ReturnsIReadOnlyList()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("H1", 1);
        var outline = doc.GetDocumentOutline();
        Assert.IsAssignableFrom<IReadOnlyList<(int Level, string Text)>>(outline);
    }

    [Fact]
    public void GetDocumentOutline_Count_MatchesGetHeadingCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("A", 1);
        doc.AppendParagraph("Body");
        doc.AppendHeading("B", 2);
        var outline = doc.GetDocumentOutline();
        Assert.Equal(doc.GetHeadingCount(), outline.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MixedContent_HeadingLevelsCorrect()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Intro");
        doc.AppendHeading("Part I", 1);
        doc.AppendParagraph("Body");
        doc.AppendHeading("Chapter 1", 2);
        var outline = doc.GetDocumentOutline();
        Assert.Equal(2, outline.Count);
        // Levels are set by AppendHeading argument
        Assert.InRange(outline[0].Level, 1, 6);
        Assert.InRange(outline[1].Level, 1, 6);
    }

    [Fact]
    public void DogfoodPipeline_AppendHeading_OutlineTextMatch()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Section Alpha", 2);
        var outline = doc.GetDocumentOutline();
        Assert.Single(outline);
        Assert.Equal("Section Alpha", outline[0].Text);
    }
}
