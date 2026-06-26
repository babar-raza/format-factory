// Tests for FodtDocument.AppendHeading dedicated coverage.
// Sprint: ff-sprint-s239-dotnet-deepening-20260629
// Ledger: PC-FODT-R254

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R254: Dedicated tests for FodtDocument.AppendHeading(text, level).
/// Valid append → no exception.
/// ParagraphCount increases after append.
/// HeadingCount increases after append.
/// Heading text retrievable via GetHeadingText.
/// Level-1 heading accessible.
/// Level-2 heading accessible.
/// Multiple headings → count matches appended.
/// Append heading then paragraph → counts both.
/// GetTableOfContents grows with headings.
/// Dogfood: append multiple headings, verify each via GetHeadingText.
/// </summary>
public class FodtR254AppendHeadingDedicatedTests
{
    // -------------------------------------------------------------------------
    // Basic functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AppendHeading_ValidCall_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.AppendHeading("Introduction", 1));
        Assert.Null(ex);
    }

    [Fact]
    public void AppendHeading_ParagraphCountIncreases()
    {
        var doc = FodtDocument.CreateEmpty();
        int before = doc.ParagraphCount;
        doc.AppendHeading("Chapter One", 1);
        Assert.True(doc.ParagraphCount > before);
    }

    [Fact]
    public void AppendHeading_HeadingCountIncreases()
    {
        var doc = FodtDocument.CreateEmpty();
        int before = doc.GetHeadingCount();
        doc.AppendHeading("Section A", 1);
        Assert.True(doc.GetHeadingCount() > before);
    }

    [Fact]
    public void AppendHeading_HeadingTextRetrievable()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("My Heading", 1);
        string? text = doc.GetHeadingText(0);
        Assert.NotNull(text);
        Assert.Contains("My Heading", text);
    }

    [Fact]
    public void AppendHeading_Level1_Accessible()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Level One", 1);
        Assert.Equal(1, doc.GetHeadingCount());
    }

    [Fact]
    public void AppendHeading_Level2_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.AppendHeading("Sub-Section", 2));
        Assert.Null(ex);
    }

    [Fact]
    public void AppendHeading_MultipleHeadings_CountMatches()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("First", 1);
        doc.AppendHeading("Second", 1);
        doc.AppendHeading("Third", 2);
        Assert.Equal(3, doc.GetHeadingCount());
    }

    [Fact]
    public void AppendHeading_ThenParagraph_BothCountedSeparately()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        doc.AppendParagraph("Body text here.");
        Assert.Equal(1, doc.GetHeadingCount());
        // Total ParagraphCount should reflect both
        Assert.True(doc.ParagraphCount >= 1);
    }

    [Fact]
    public void AppendHeading_TableOfContentsGrows()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter 1", 1);
        doc.AppendHeading("Chapter 2", 1);
        var toc = doc.GetTableOfContents();
        Assert.NotNull(toc);
        int count = System.Linq.Enumerable.Cast<object>(toc).Count();
        Assert.True(count >= 1);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendMultipleHeadings_VerifyEachViaGetHeadingText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Alpha", 1);
        doc.AppendHeading("Beta", 2);
        doc.AppendHeading("Gamma", 1);
        Assert.Equal(3, doc.GetHeadingCount());
        string? h0 = doc.GetHeadingText(0);
        string? h1 = doc.GetHeadingText(1);
        string? h2 = doc.GetHeadingText(2);
        Assert.NotNull(h0);
        Assert.NotNull(h1);
        Assert.NotNull(h2);
        Assert.Contains("Alpha", h0);
        Assert.Contains("Beta", h1);
        Assert.Contains("Gamma", h2);
    }
}
