// Tests for FodtDocument.GetTextBetweenParagraphs dedicated coverage.
// Sprint: ff-sprint-s194-dotnet-deepening-20260629
// Ledger: PC-FODT-R207

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R207: Dedicated tests for FodtDocument.GetTextBetweenParagraphs(int startIndex, int endIndex).
/// Returns the text of paragraphs [startIndex, endIndex) joined by newlines.
/// Returns null if startIndex &lt; 0.
/// Returns null if endIndex &gt; ParagraphCount.
/// Returns null if startIndex >= endIndex.
/// Single paragraph range returns that paragraph's text.
/// Multi-paragraph range joins with '\n'.
/// Headings are included.
/// Covers: negative start returns null; end above count returns null; start==end null;
/// start>end null; single para text; two paras joined; heading text present;
/// middle range correct; dogfood three paras; dogfood full range all present.
/// </summary>
public class FodtR207GetTextBetweenParagraphsTests
{
    // -------------------------------------------------------------------------
    // Null return guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTextBetweenParagraphs_NegativeStart_ReturnsNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        var result = doc.GetTextBetweenParagraphs(-1, 1);
        Assert.Null(result);
    }

    [Fact]
    public void GetTextBetweenParagraphs_EndAboveCount_ReturnsNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        var result = doc.GetTextBetweenParagraphs(0, 2);
        Assert.Null(result);
    }

    [Fact]
    public void GetTextBetweenParagraphs_StartEqualsEnd_ReturnsNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        var result = doc.GetTextBetweenParagraphs(1, 1);
        Assert.Null(result);
    }

    [Fact]
    public void GetTextBetweenParagraphs_StartGreaterThanEnd_ReturnsNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        doc.AppendParagraph("B");
        var result = doc.GetTextBetweenParagraphs(1, 0);
        Assert.Null(result);
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTextBetweenParagraphs_SingleParagraph_ReturnsText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("OnlyOne");
        var result = doc.GetTextBetweenParagraphs(0, 1);
        Assert.Equal("OnlyOne", result);
    }

    [Fact]
    public void GetTextBetweenParagraphs_TwoParagraphs_JoinedByNewline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        var result = doc.GetTextBetweenParagraphs(0, 2);
        Assert.Contains("First", result);
        Assert.Contains("Second", result);
        Assert.Contains("\n", result);
    }

    [Fact]
    public void GetTextBetweenParagraphs_HeadingIncluded()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        var result = doc.GetTextBetweenParagraphs(0, 1);
        Assert.Contains("Title", result);
    }

    [Fact]
    public void GetTextBetweenParagraphs_MiddleRange_CorrectText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        doc.AppendParagraph("B");
        doc.AppendParagraph("C");
        var result = doc.GetTextBetweenParagraphs(1, 2);
        Assert.Equal("B", result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ThreeParagraphs_MiddleRange()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        doc.AppendParagraph("Gamma");
        var result = doc.GetTextBetweenParagraphs(1, 3);
        Assert.NotNull(result);
        Assert.Contains("Beta", result);
        Assert.Contains("Gamma", result);
        Assert.DoesNotContain("Alpha", result);
    }

    [Fact]
    public void DogfoodPipeline_FullRange_AllTextsPresent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("X");
        doc.AppendParagraph("Y");
        doc.AppendParagraph("Z");
        var result = doc.GetTextBetweenParagraphs(0, 3);
        Assert.NotNull(result);
        Assert.Contains("X", result);
        Assert.Contains("Y", result);
        Assert.Contains("Z", result);
    }
}
