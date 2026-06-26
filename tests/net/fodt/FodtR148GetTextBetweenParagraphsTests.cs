// Tests for FodtDocument.GetTextBetweenParagraphs(int startIndex, int endIndex).
// Sprint: ff-sprint-s133-dotnet-deepening-20260627
// Ledger: PC-FODT-R148

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R148: Tests for FodtDocument.GetTextBetweenParagraphs(int startIndex, int endIndex).
/// Returns a string joining paragraph texts from [startIndex, endIndex) separated by '\n'.
/// Returns null for invalid ranges (startIndex &lt; 0, endIndex > Count, startIndex >= endIndex).
/// Covers: valid range returns joined text; single-range (0,1)=first para; full range
/// returns all texts; invalid range startIndex>=endIndex returns null; negative startIndex
/// returns null; endIndex>count returns null; zero-para doc valid range returns null;
/// separator is newline; dogfood AppendParagraph×3 then GetTextBetween all.
/// </summary>
public class FodtR148GetTextBetweenParagraphsTests
{
    private static FodtDocument ThreeParagraphDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First paragraph");
        doc.AppendParagraph("Second paragraph");
        doc.AppendParagraph("Third paragraph");
        return doc;
    }

    // -------------------------------------------------------------------------
    // Valid ranges
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTextBetweenParagraphs_SingleRange_ReturnsFirstParagraph()
    {
        var doc = ThreeParagraphDoc();
        var result = doc.GetTextBetweenParagraphs(0, 1);
        Assert.Equal("First paragraph", result);
    }

    [Fact]
    public void GetTextBetweenParagraphs_TwoParas_ReturnsNewlineSeparated()
    {
        var doc = ThreeParagraphDoc();
        var result = doc.GetTextBetweenParagraphs(0, 2);
        Assert.Equal("First paragraph\nSecond paragraph", result);
    }

    [Fact]
    public void GetTextBetweenParagraphs_FullRange_ReturnsAllThree()
    {
        var doc = ThreeParagraphDoc();
        var result = doc.GetTextBetweenParagraphs(0, 3);
        Assert.Equal("First paragraph\nSecond paragraph\nThird paragraph", result);
    }

    [Fact]
    public void GetTextBetweenParagraphs_MiddleRange_ReturnsCorrectSlice()
    {
        var doc = ThreeParagraphDoc();
        var result = doc.GetTextBetweenParagraphs(1, 3);
        Assert.Equal("Second paragraph\nThird paragraph", result);
    }

    [Fact]
    public void GetTextBetweenParagraphs_LastParagraph_ReturnsSingleText()
    {
        var doc = ThreeParagraphDoc();
        var result = doc.GetTextBetweenParagraphs(2, 3);
        Assert.Equal("Third paragraph", result);
    }

    // -------------------------------------------------------------------------
    // Invalid ranges → null
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTextBetweenParagraphs_StartEqualEnd_ReturnsNull()
    {
        var doc = ThreeParagraphDoc();
        var result = doc.GetTextBetweenParagraphs(1, 1);
        Assert.Null(result);
    }

    [Fact]
    public void GetTextBetweenParagraphs_NegativeStart_ReturnsNull()
    {
        var doc = ThreeParagraphDoc();
        var result = doc.GetTextBetweenParagraphs(-1, 2);
        Assert.Null(result);
    }

    [Fact]
    public void GetTextBetweenParagraphs_EndExceedsCount_ReturnsNull()
    {
        var doc = ThreeParagraphDoc();
        var result = doc.GetTextBetweenParagraphs(0, 99);
        Assert.Null(result);
    }

    // -------------------------------------------------------------------------
    // Empty document
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTextBetweenParagraphs_EmptyDoc_ZeroToZero_ReturnsNull()
    {
        var doc = FodtDocument.CreateEmpty();
        var result = doc.GetTextBetweenParagraphs(0, 0);
        Assert.Null(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood: AppendParagraph×3 then GetTextBetween
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendThree_GetTextBetweenAll_ContainsAllTexts()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        doc.AppendParagraph("Gamma");

        var result = doc.GetTextBetweenParagraphs(0, 3);

        Assert.NotNull(result);
        Assert.Contains("Alpha", result!);
        Assert.Contains("Beta", result);
        Assert.Contains("Gamma", result);
        Assert.Equal("Alpha\nBeta\nGamma", result);
    }
}
