// Tests for FodtDocument.RemoveHeading dedicated coverage.
// Sprint: ff-sprint-s160-dotnet-deepening-20260628
// Ledger: PC-FODT-R169

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R169: Dedicated tests for FodtDocument.RemoveHeading(int index).
/// RemoveHeading removes the element at the given index if it is a heading (text:h).
/// Throws ArgumentOutOfRangeException for negative index or index >= ParagraphCount.
/// Throws InvalidOperationException if element at index is not a heading.
/// Covers: negative index throws ArgumentOutOfRangeException; index at ParagraphCount throws;
/// index beyond count throws; non-heading index throws InvalidOperationException;
/// valid removal decreases count; removed heading not in GetHeadingTexts;
/// remaining headings shift; paragraph count decreases after removal;
/// dogfood AppendHeading->RemoveHeading pipeline;
/// dogfood remove-all-headings leaves only paragraphs.
/// </summary>
public class FodtR169RemoveHeadingDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveHeading_NegativeIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Section 1", 1);
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.RemoveHeading(-1));
    }

    [Fact]
    public void RemoveHeading_IndexAtParagraphCount_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Section 1", 1);
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.RemoveHeading(1));
    }

    [Fact]
    public void RemoveHeading_IndexBeyondCount_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Section 1", 1);
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.RemoveHeading(10));
    }

    [Fact]
    public void RemoveHeading_IndexPointsToParagraph_ThrowsInvalidOperationException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Body text"); // index 0 — not a heading
        Assert.Throws<InvalidOperationException>(() => doc.RemoveHeading(0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveHeading_ValidRemoval_DecreasesCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Section 1", 1);
        doc.AppendHeading("Section 2", 1);
        var before = doc.ParagraphCount;
        doc.RemoveHeading(0);
        Assert.Equal(before - 1, doc.ParagraphCount);
    }

    [Fact]
    public void RemoveHeading_RemovedHeading_NotInGetHeadingTexts()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Gone", 1);
        doc.AppendHeading("Kept", 1);
        doc.RemoveHeading(0); // remove "Gone"
        var texts = doc.GetHeadingTexts();
        Assert.DoesNotContain("Gone", texts);
    }

    [Fact]
    public void RemoveHeading_RemoveFirst_RemainingShifts()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("First", 1);
        doc.AppendHeading("Second", 2);
        doc.RemoveHeading(0); // remove "First"
        Assert.Equal(1, doc.ParagraphCount);
        Assert.Equal("Second", doc.GetHeadingTexts()[0]);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendHeading_RemoveHeading()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter 1", 1);
        doc.AppendHeading("Chapter 2", 1);
        doc.RemoveHeading(0);
        var texts = doc.GetHeadingTexts();
        Assert.Single(texts);
        Assert.Equal("Chapter 2", texts[0]);
    }

    [Fact]
    public void DogfoodPipeline_RemoveAllHeadings_LeavesOnlyParagraphs()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Intro");
        doc.AppendHeading("Title", 1);
        // Remove at index 1 (the heading)
        doc.RemoveHeading(1);
        Assert.Equal(1, doc.ParagraphCount);
        Assert.Empty(doc.GetHeadingTexts());
        Assert.Equal("Intro", doc.GetParagraphText(0));
    }
}
