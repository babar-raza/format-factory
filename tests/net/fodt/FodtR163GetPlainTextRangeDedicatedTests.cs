// Tests for FodtDocument.GetPlainTextRange dedicated coverage.
// Sprint: ff-sprint-s154-dotnet-deepening-20260628
// Ledger: PC-FODT-R163

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R163: Dedicated tests for FodtDocument.GetPlainTextRange(int startIndex, int endIndex).
/// GetPlainTextRange returns the concatenated text of paragraphs [startIndex, endIndex) joined by newline.
/// Throws ArgumentOutOfRangeException if startIndex < 0 or endIndex > ParagraphCount.
/// Returns empty string if startIndex >= endIndex.
/// Covers: negative startIndex throws; endIndex beyond count throws; startIndex==endIndex returns empty;
/// startIndex>endIndex returns empty; single paragraph range returns its text;
/// two-paragraph range joined by newline; full range returns all text;
/// startIndex=0 endIndex=1 returns first paragraph only;
/// dogfood AppendParagraph->GetPlainTextRange pipeline;
/// dogfood range mid-document returns correct subset.
/// </summary>
public class FodtR163GetPlainTextRangeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPlainTextRange_NegativeStartIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para 0");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.GetPlainTextRange(-1, 1));
    }

    [Fact]
    public void GetPlainTextRange_EndIndexBeyondCount_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para 0");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.GetPlainTextRange(0, 5));
    }

    // -------------------------------------------------------------------------
    // Empty range tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPlainTextRange_StartEqualsEnd_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para 0");
        var result = doc.GetPlainTextRange(0, 0);
        Assert.Equal(string.Empty, result);
    }

    [Fact]
    public void GetPlainTextRange_StartGreaterThanEnd_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para 0");
        doc.AppendParagraph("Para 1");
        var result = doc.GetPlainTextRange(1, 0);
        Assert.Equal(string.Empty, result);
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPlainTextRange_SingleParagraph_ReturnsItsText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world");
        var result = doc.GetPlainTextRange(0, 1);
        Assert.Equal("Hello world", result);
    }

    [Fact]
    public void GetPlainTextRange_TwoParagraphs_JoinedByNewline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        var result = doc.GetPlainTextRange(0, 2);
        Assert.Equal("First\nSecond", result);
    }

    [Fact]
    public void GetPlainTextRange_FullRange_ReturnsAllText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        doc.AppendParagraph("B");
        doc.AppendParagraph("C");
        var result = doc.GetPlainTextRange(0, 3);
        Assert.Equal("A\nB\nC", result);
    }

    [Fact]
    public void GetPlainTextRange_FirstParagraphOnly_ReturnsFirstText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Only first");
        doc.AppendParagraph("Not included");
        var result = doc.GetPlainTextRange(0, 1);
        Assert.Equal("Only first", result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendParagraph_GetPlainTextRange()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Intro");
        doc.AppendParagraph("Body");
        doc.AppendParagraph("Conclusion");
        var result = doc.GetPlainTextRange(0, doc.ParagraphCount);
        Assert.Contains("Intro", result);
        Assert.Contains("Body", result);
        Assert.Contains("Conclusion", result);
    }

    [Fact]
    public void DogfoodPipeline_MidDocumentRange_ReturnsCorrectSubset()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Middle");
        doc.AppendParagraph("Last");
        var result = doc.GetPlainTextRange(1, 2); // only "Middle"
        Assert.Equal("Middle", result);
        Assert.DoesNotContain("First", result);
        Assert.DoesNotContain("Last", result);
    }
}
