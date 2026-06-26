// Tests for FodtDocument.GetTextBetweenParagraphs dedicated coverage.
// Sprint: ff-sprint-s158-dotnet-deepening-20260628
// Ledger: PC-FODT-R167

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R167: Dedicated tests for FodtDocument.GetTextBetweenParagraphs(int startIndex, int endIndex).
/// Returns null if startIndex < 0, endIndex > ParagraphCount, or startIndex >= endIndex.
/// Returns text of paragraphs [startIndex, endIndex) joined by newlines.
/// Covers: negative startIndex returns null; endIndex beyond count returns null;
/// startIndex==endIndex returns null; startIndex>endIndex returns null;
/// single paragraph range returns its text; two paragraphs joined by newline;
/// full range returns all paragraphs; first-only range returns first text only;
/// dogfood AppendParagraph->GetTextBetweenParagraphs pipeline;
/// dogfood mid-document range excludes surrounding paragraphs.
/// </summary>
public class FodtR167GetTextBetweenParagraphsDedicatedTests
{
    // -------------------------------------------------------------------------
    // Returns-null tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTextBetweenParagraphs_NegativeStartIndex_ReturnsNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para 0");
        var result = doc.GetTextBetweenParagraphs(-1, 1);
        Assert.Null(result);
    }

    [Fact]
    public void GetTextBetweenParagraphs_EndIndexBeyondCount_ReturnsNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para 0");
        var result = doc.GetTextBetweenParagraphs(0, 5);
        Assert.Null(result);
    }

    [Fact]
    public void GetTextBetweenParagraphs_StartEqualsEnd_ReturnsNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para 0");
        var result = doc.GetTextBetweenParagraphs(0, 0);
        Assert.Null(result);
    }

    [Fact]
    public void GetTextBetweenParagraphs_StartGreaterThanEnd_ReturnsNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para 0");
        doc.AppendParagraph("Para 1");
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
        doc.AppendParagraph("Hello");
        var result = doc.GetTextBetweenParagraphs(0, 1);
        Assert.Equal("Hello", result);
    }

    [Fact]
    public void GetTextBetweenParagraphs_TwoParagraphs_JoinedByNewline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        var result = doc.GetTextBetweenParagraphs(0, 2);
        Assert.Equal("First\nSecond", result);
    }

    [Fact]
    public void GetTextBetweenParagraphs_FullRange_ReturnsAll()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        doc.AppendParagraph("B");
        doc.AppendParagraph("C");
        var result = doc.GetTextBetweenParagraphs(0, 3);
        Assert.Equal("A\nB\nC", result);
    }

    [Fact]
    public void GetTextBetweenParagraphs_FirstOnly_ReturnsFirstText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        var result = doc.GetTextBetweenParagraphs(0, 1);
        Assert.Equal("First", result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendParagraph_GetTextBetweenParagraphs()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Intro");
        doc.AppendParagraph("Body");
        doc.AppendParagraph("Conclusion");
        var result = doc.GetTextBetweenParagraphs(0, doc.ParagraphCount);
        Assert.NotNull(result);
        Assert.Contains("Body", result);
    }

    [Fact]
    public void DogfoodPipeline_MidDocumentRange_ExcludesSurrounding()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Before");
        doc.AppendParagraph("Middle");
        doc.AppendParagraph("After");
        var result = doc.GetTextBetweenParagraphs(1, 2);
        Assert.Equal("Middle", result);
        Assert.DoesNotContain("Before", result!);
        Assert.DoesNotContain("After", result!);
    }
}
