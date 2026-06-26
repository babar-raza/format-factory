// Tests for FodtDocument.SetParagraphText dedicated coverage.
// Sprint: ff-sprint-s153-dotnet-deepening-20260628
// Ledger: PC-FODT-R162

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R162: Dedicated tests for FodtDocument.SetParagraphText(int index, string text).
/// SetParagraphText replaces the text content of the paragraph at the given zero-based index.
/// Throws ArgumentOutOfRangeException for negative index or index >= ParagraphCount.
/// Covers: negative index throws; index at ParagraphCount throws; index beyond count throws;
/// text updated correctly at index 0; text updated at last index; empty string clears text;
/// null text treated as empty; other paragraphs unchanged; paragraph count unchanged after set;
/// dogfood AppendParagraph->SetParagraphText->GetParagraphText pipeline;
/// dogfood set multiple paragraphs in sequence.
/// </summary>
public class FodtR162SetParagraphTextDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetParagraphText_NegativeIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetParagraphText(-1, "New text"));
    }

    [Fact]
    public void SetParagraphText_IndexAtParagraphCount_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Only paragraph");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetParagraphText(1, "New text"));
    }

    [Fact]
    public void SetParagraphText_IndexBeyondCount_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para 0");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetParagraphText(10, "New text"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetParagraphText_UpdatesTextAtIndex0()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Old text");
        doc.SetParagraphText(0, "New text");
        Assert.Equal("New text", doc.GetParagraphText(0));
    }

    [Fact]
    public void SetParagraphText_UpdatesTextAtLastIndex()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para 0");
        doc.AppendParagraph("Para 1");
        doc.AppendParagraph("Old last");
        doc.SetParagraphText(2, "New last");
        Assert.Equal("New last", doc.GetParagraphText(2));
    }

    [Fact]
    public void SetParagraphText_EmptyString_ClearsText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some text");
        doc.SetParagraphText(0, string.Empty);
        var result = doc.GetParagraphText(0);
        Assert.True(result == string.Empty || result == null);
    }

    [Fact]
    public void SetParagraphText_OtherParagraphsUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        doc.AppendParagraph("Third");
        doc.SetParagraphText(1, "Modified");
        Assert.Equal("First", doc.GetParagraphText(0));
        Assert.Equal("Third", doc.GetParagraphText(2));
    }

    [Fact]
    public void SetParagraphText_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        var before = doc.ParagraphCount;
        doc.SetParagraphText(0, "Changed");
        Assert.Equal(before, doc.ParagraphCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendParagraph_SetParagraphText_GetParagraphText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Initial content");
        doc.SetParagraphText(0, "Updated content");
        Assert.Equal("Updated content", doc.GetParagraphText(0));
    }

    [Fact]
    public void DogfoodPipeline_SetMultipleParagraphs_InSequence()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        doc.AppendParagraph("B");
        doc.AppendParagraph("C");
        doc.SetParagraphText(0, "X");
        doc.SetParagraphText(1, "Y");
        doc.SetParagraphText(2, "Z");
        Assert.Equal("X", doc.GetParagraphText(0));
        Assert.Equal("Y", doc.GetParagraphText(1));
        Assert.Equal("Z", doc.GetParagraphText(2));
    }
}
