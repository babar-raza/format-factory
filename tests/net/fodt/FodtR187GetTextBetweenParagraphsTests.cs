// Tests for FodtDocument.GetTextBetweenParagraphs dedicated coverage.
// Sprint: ff-sprint-s178-dotnet-deepening-20260628
// Ledger: PC-FODT-R187

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R187: Dedicated tests for FodtDocument.GetTextBetweenParagraphs(int startIndex, int endIndex).
/// Returns text of paragraphs [startIndex, endIndex) joined by newlines, or null if invalid range.
/// Unlike GetPlainTextRange, invalid args return null (no throw).
/// Valid range: paragraphs joined by '\n'.
/// Null returned when: startIndex &lt; 0, endIndex &gt; ParagraphCount, startIndex &gt;= endIndex.
/// Covers: negative startIndex returns null; endIndex over count returns null;
/// start==end returns null; start>end returns null; single paragraph returns text;
/// multiple paragraphs joined with newline; partial range correct;
/// headings included in range; dogfood mixed content; dogfood range roundtrip.
/// </summary>
public class FodtR187GetTextBetweenParagraphsTests
{
    // -------------------------------------------------------------------------
    // Invalid range returns null (no throw)
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTextBetweenParagraphs_NegativeStartIndex_ReturnsNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        var result = doc.GetTextBetweenParagraphs(-1, 1);
        Assert.Null(result);
    }

    [Fact]
    public void GetTextBetweenParagraphs_EndIndexOverCount_ReturnsNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        var result = doc.GetTextBetweenParagraphs(0, 5);
        Assert.Null(result);
    }

    [Fact]
    public void GetTextBetweenParagraphs_StartEqualsEnd_ReturnsNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        var result = doc.GetTextBetweenParagraphs(0, 0);
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
    public void GetTextBetweenParagraphs_SingleParagraph_ReturnsItsText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Just one");
        var result = doc.GetTextBetweenParagraphs(0, 1);
        Assert.Equal("Just one", result);
    }

    [Fact]
    public void GetTextBetweenParagraphs_MultipleParagraphs_JoinedWithNewline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        doc.AppendParagraph("Third");
        var result = doc.GetTextBetweenParagraphs(0, 3);
        Assert.NotNull(result);
        Assert.Contains("First", result);
        Assert.Contains("Second", result);
        Assert.Contains("\n", result);
    }

    [Fact]
    public void GetTextBetweenParagraphs_PartialRange_ExcludesOutsideParagraphs()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        doc.AppendParagraph("B");
        doc.AppendParagraph("C");
        var result = doc.GetTextBetweenParagraphs(1, 2);
        Assert.NotNull(result);
        Assert.Contains("B", result);
        Assert.DoesNotContain("A", result);
        Assert.DoesNotContain("C", result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_HeadingIncludedInRange()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("My Heading", 1);
        doc.AppendParagraph("Body text");
        var result = doc.GetTextBetweenParagraphs(0, 2);
        Assert.NotNull(result);
        Assert.Contains("My Heading", result);
        Assert.Contains("Body text", result);
    }

    [Fact]
    public void DogfoodPipeline_ValidRange_NonNullNonEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Content here");
        doc.AppendParagraph("More content");
        var result = doc.GetTextBetweenParagraphs(0, doc.ParagraphCount);
        Assert.NotNull(result);
        Assert.NotEmpty(result);
    }
}
