// Tests for FodtDocument.RemoveParagraph dedicated coverage.
// Sprint: ff-sprint-s152-dotnet-deepening-20260628
// Ledger: PC-FODT-R161

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R161: Dedicated tests for FodtDocument.RemoveParagraph(int index).
/// RemoveParagraph removes the paragraph at the given zero-based index.
/// Throws ArgumentOutOfRangeException for negative index or index >= ParagraphCount.
/// Covers: negative index throws; index at ParagraphCount throws; index beyond count throws;
/// paragraph count decreases after remove; remaining paragraphs shift correctly;
/// text of remaining paragraphs unchanged; first paragraph removable;
/// last paragraph removable;
/// dogfood AppendParagraph->RemoveParagraph->ParagraphCount pipeline;
/// dogfood remove middle paragraph shifts subsequent texts.
/// </summary>
public class FodtR161RemoveParagraphDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveParagraph_NegativeIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.RemoveParagraph(-1));
    }

    [Fact]
    public void RemoveParagraph_IndexAtParagraphCount_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Only paragraph");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.RemoveParagraph(1));
    }

    [Fact]
    public void RemoveParagraph_IndexBeyondCount_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para 0");
        doc.AppendParagraph("Para 1");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.RemoveParagraph(5));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveParagraph_CountDecreases()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        var before = doc.ParagraphCount;
        doc.RemoveParagraph(0);
        Assert.Equal(before - 1, doc.ParagraphCount);
    }

    [Fact]
    public void RemoveParagraph_RemainingParagraphsShift()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        doc.AppendParagraph("Third");
        doc.RemoveParagraph(0); // remove "First"
        Assert.Equal("Second", doc.GetParagraphText(0));
    }

    [Fact]
    public void RemoveParagraph_FirstParagraph_Removable()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Remove me");
        doc.AppendParagraph("Keep me");
        doc.RemoveParagraph(0);
        Assert.Equal(1, doc.ParagraphCount);
        Assert.Equal("Keep me", doc.GetParagraphText(0));
    }

    [Fact]
    public void RemoveParagraph_LastParagraph_Removable()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Keep me");
        doc.AppendParagraph("Remove me");
        doc.RemoveParagraph(1);
        Assert.Equal(1, doc.ParagraphCount);
        Assert.Equal("Keep me", doc.GetParagraphText(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendParagraph_RemoveParagraph_Count()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        doc.AppendParagraph("B");
        doc.AppendParagraph("C");
        doc.RemoveParagraph(1); // remove "B"
        doc.RemoveParagraph(1); // remove "C" (now at index 1)
        Assert.Equal(1, doc.ParagraphCount);
        Assert.Equal("A", doc.GetParagraphText(0));
    }

    [Fact]
    public void DogfoodPipeline_RemoveMiddle_ShiftsSubsequent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para 0");
        doc.AppendParagraph("Para 1");
        doc.AppendParagraph("Para 2");
        doc.RemoveParagraph(1); // remove "Para 1"
        Assert.Equal(2, doc.ParagraphCount);
        Assert.Equal("Para 0", doc.GetParagraphText(0));
        Assert.Equal("Para 2", doc.GetParagraphText(1));
    }
}
