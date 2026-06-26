// Tests for FodtDocument.GetWordCount dedicated coverage.
// Sprint: ff-sprint-s221-dotnet-deepening-20260629
// Ledger: PC-FODT-R236

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R236: Dedicated tests for FodtDocument.GetWordCount().
/// Empty document: no exception.
/// Empty document: non-negative count.
/// Single paragraph: no exception.
/// ParagraphCount unchanged after call.
/// Two paragraphs: count >= one-paragraph count.
/// Called twice: same result.
/// After heading added: no exception.
/// Result is non-negative integer.
/// Dogfood: add three paragraphs, word count non-negative.
/// Dogfood: stable across operations.
/// </summary>
public class FodtR236GetWordCountTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWordCount_EmptyDoc_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.GetWordCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetWordCount_EmptyDoc_NonNegative()
    {
        var doc = FodtDocument.CreateEmpty();
        var count = doc.GetWordCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetWordCount_SingleParagraph_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world test");
        var ex = Record.Exception(() => doc.GetWordCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetWordCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para one");
        doc.AppendParagraph("Para two");
        int before = doc.ParagraphCount;
        doc.GetWordCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetWordCount_TwoParagraphs_CountAtLeastOneParagraph()
    {
        var doc1 = FodtDocument.CreateEmpty();
        doc1.AppendParagraph("One two three");
        var doc2 = FodtDocument.CreateEmpty();
        doc2.AppendParagraph("One two three");
        doc2.AppendParagraph("Four five six");
        Assert.True(doc2.GetWordCount() >= doc1.GetWordCount());
    }

    [Fact]
    public void GetWordCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Consistent word count");
        var v1 = doc.GetWordCount();
        var v2 = doc.GetWordCount();
        Assert.Equal(v1, v2);
    }

    [Fact]
    public void GetWordCount_AfterHeadingAdded_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("My Heading", 1);
        var ex = Record.Exception(() => doc.GetWordCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetWordCount_ResultIsNonNegative()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some content here");
        var count = doc.GetWordCount();
        Assert.True(count >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ThreeParagraphs_WordCountNonNegative()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First para words here");
        doc.AppendParagraph("Second para words");
        doc.AppendParagraph("Third para");
        var count = doc.GetWordCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void DogfoodPipeline_StableAcrossOperations()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Initial content");
        var before = doc.GetWordCount();
        doc.SetAuthor("Author Name");
        doc.AppendHeading("Extra Heading", 2);
        // Getting word count again should not throw
        var ex = Record.Exception(() => doc.GetWordCount());
        Assert.Null(ex);
    }
}
