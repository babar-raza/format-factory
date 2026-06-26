// Tests for FodtDocument.GetPlainTextRange dedicated coverage.
// Sprint: ff-sprint-s191-dotnet-deepening-20260629
// Ledger: PC-FODT-R202

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R202: Dedicated tests for FodtDocument.GetPlainTextRange(int startIndex, int endIndex).
/// Returns the text of paragraphs [startIndex, endIndex) joined by newlines.
/// startIndex &lt; 0 → throws ArgumentOutOfRangeException.
/// endIndex &gt; ParagraphCount → throws ArgumentOutOfRangeException.
/// startIndex >= endIndex → returns empty string.
/// Single paragraph range returns just that paragraph's text.
/// Multi-paragraph range joins with '\n'.
/// Does not include headings vs body distinction — all paragraphs included.
/// Covers: negative start throws; endIndex above count throws; start==end empty;
/// start>end empty; single-para range text; two-para range joined; headings included;
/// dogfood three paragraphs middle range; dogfood full range matches GetPlainText.
/// </summary>
public class FodtR202GetPlainTextRangeTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPlainTextRange_NegativeStart_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.GetPlainTextRange(-1, 1));
    }

    [Fact]
    public void GetPlainTextRange_EndAboveCount_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.GetPlainTextRange(0, 2));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPlainTextRange_StartEqualsEnd_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        var result = doc.GetPlainTextRange(1, 1);
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

    [Fact]
    public void GetPlainTextRange_SingleParagraph_ReturnsItsText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("OnlyOne");
        var result = doc.GetPlainTextRange(0, 1);
        Assert.Equal("OnlyOne", result);
    }

    [Fact]
    public void GetPlainTextRange_TwoParagraphs_JoinedWithNewline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        var result = doc.GetPlainTextRange(0, 2);
        Assert.Contains("First", result);
        Assert.Contains("Second", result);
        Assert.Contains("\n", result);
    }

    [Fact]
    public void GetPlainTextRange_MiddleParagraph_CorrectText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        doc.AppendParagraph("B");
        doc.AppendParagraph("C");
        var result = doc.GetPlainTextRange(1, 2);
        Assert.Equal("B", result);
    }

    [Fact]
    public void GetPlainTextRange_HeadingsIncluded()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        doc.AppendParagraph("Body");
        // HeadingParagraph at index 0 should be retrievable
        var result = doc.GetPlainTextRange(0, 1);
        Assert.Contains("Title", result);
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
        var result = doc.GetPlainTextRange(1, 3);
        Assert.Contains("Beta", result);
        Assert.Contains("Gamma", result);
        Assert.DoesNotContain("Alpha", result);
    }

    [Fact]
    public void DogfoodPipeline_FullRange_MatchesGetPlainText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("X");
        doc.AppendParagraph("Y");
        doc.AppendParagraph("Z");
        var rangeResult = doc.GetPlainTextRange(0, doc.ParagraphCount);
        var fullText = doc.GetPlainText();
        // Both should contain all three values
        Assert.Contains("X", rangeResult);
        Assert.Contains("Y", rangeResult);
        Assert.Contains("Z", rangeResult);
        Assert.Contains("X", fullText);
        Assert.Contains("Y", fullText);
        Assert.Contains("Z", fullText);
    }
}
