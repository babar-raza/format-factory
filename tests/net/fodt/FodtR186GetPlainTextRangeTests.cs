// Tests for FodtDocument.GetPlainTextRange dedicated coverage.
// Sprint: ff-sprint-s177-dotnet-deepening-20260628
// Ledger: PC-FODT-R186

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R186: Dedicated tests for FodtDocument.GetPlainTextRange(int startIndex, int endIndex).
/// Returns text of paragraphs [startIndex, endIndex) joined by newlines.
/// startIndex &lt; 0 throws ArgumentOutOfRangeException.
/// endIndex &gt; ParagraphCount throws ArgumentOutOfRangeException.
/// startIndex &gt;= endIndex returns empty string.
/// Valid range: paragraphs joined by '\n'.
/// Covers: negative startIndex throws; endIndex over count throws;
/// startIndex==endIndex returns empty; startIndex>endIndex returns empty;
/// single paragraph; multiple paragraphs joined with newlines;
/// full range matches count; dogfood AppendParagraph then range retrieval;
/// dogfood partial range.
/// </summary>
public class FodtR186GetPlainTextRangeTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPlainTextRange_NegativeStartIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.GetPlainTextRange(-1, 1));
    }

    [Fact]
    public void GetPlainTextRange_EndIndexOverCount_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.GetPlainTextRange(0, 5));
    }

    // -------------------------------------------------------------------------
    // Empty / degenerate cases
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPlainTextRange_StartEqualsEnd_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        var result = doc.GetPlainTextRange(0, 0);
        Assert.Equal(string.Empty, result);
    }

    [Fact]
    public void GetPlainTextRange_StartGreaterThanEnd_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        doc.AppendParagraph("B");
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
        doc.AppendParagraph("Only paragraph");
        var result = doc.GetPlainTextRange(0, 1);
        Assert.Equal("Only paragraph", result);
    }

    [Fact]
    public void GetPlainTextRange_MultipleParagraphs_JoinedWithNewline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        doc.AppendParagraph("Third");
        var result = doc.GetPlainTextRange(0, 3);
        Assert.Contains("First", result);
        Assert.Contains("Second", result);
        Assert.Contains("Third", result);
        // Paragraphs joined by newline
        Assert.Contains("\n", result);
    }

    [Fact]
    public void GetPlainTextRange_PartialRange_OnlySelectedParagraphs()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        doc.AppendParagraph("B");
        doc.AppendParagraph("C");
        var result = doc.GetPlainTextRange(1, 2);
        Assert.Contains("B", result);
        Assert.DoesNotContain("A", result);
        Assert.DoesNotContain("C", result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendThenRange_AllTextPresent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Introduction");
        doc.AppendHeading("Chapter 1", 1);
        doc.AppendParagraph("Body text.");
        var result = doc.GetPlainTextRange(0, doc.ParagraphCount);
        Assert.NotNull(result);
        Assert.Contains("Introduction", result);
        Assert.Contains("Body text.", result);
    }

    [Fact]
    public void DogfoodPipeline_RangeLength_MatchesParagraphCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para one");
        doc.AppendParagraph("Para two");
        var result = doc.GetPlainTextRange(0, 2);
        // Result should have one newline separator between 2 paragraphs
        Assert.Equal(1, result.Split('\n').Length - 1);
    }
}
