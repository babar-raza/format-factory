// Tests for FodtDocument.GetCharacterCount dedicated coverage.
// Sprint: ff-sprint-s222-dotnet-deepening-20260629
// Ledger: PC-FODT-R237

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R237: Dedicated tests for FodtDocument.GetCharacterCount().
/// Empty document: no exception.
/// Empty document: non-negative count.
/// Single paragraph: no exception.
/// ParagraphCount unchanged after call.
/// Longer paragraph: count >= shorter paragraph count.
/// Called twice: same result.
/// After heading added: no exception.
/// Result is non-negative integer.
/// Dogfood: add multiple paragraphs, char count non-negative.
/// Dogfood: stable across set-author and heading operations.
/// </summary>
public class FodtR237GetCharacterCountTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCharacterCount_EmptyDoc_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.GetCharacterCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCharacterCount_EmptyDoc_NonNegative()
    {
        var doc = FodtDocument.CreateEmpty();
        var count = doc.GetCharacterCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetCharacterCount_SingleParagraph_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello character count");
        var ex = Record.Exception(() => doc.GetCharacterCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCharacterCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para A");
        doc.AppendParagraph("Para B");
        int before = doc.ParagraphCount;
        doc.GetCharacterCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetCharacterCount_LongerParagraph_CountAtLeastShorter()
    {
        var doc1 = FodtDocument.CreateEmpty();
        doc1.AppendParagraph("Hi");
        var doc2 = FodtDocument.CreateEmpty();
        doc2.AppendParagraph("Hello World This Is A Longer Paragraph");
        Assert.True(doc2.GetCharacterCount() >= doc1.GetCharacterCount());
    }

    [Fact]
    public void GetCharacterCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Consistent character count test");
        var v1 = doc.GetCharacterCount();
        var v2 = doc.GetCharacterCount();
        Assert.Equal(v1, v2);
    }

    [Fact]
    public void GetCharacterCount_AfterHeadingAdded_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("A Heading", 1);
        var ex = Record.Exception(() => doc.GetCharacterCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCharacterCount_ResultIsNonNegative()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some text content");
        var count = doc.GetCharacterCount();
        Assert.True(count >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultipleParagraphs_NonNegative()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First paragraph of content");
        doc.AppendParagraph("Second paragraph of content");
        doc.AppendParagraph("Third paragraph");
        var count = doc.GetCharacterCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void DogfoodPipeline_StableAcrossOperations()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Initial content here");
        doc.SetAuthor("Test Author");
        doc.AppendHeading("Section 1", 2);
        var ex = Record.Exception(() => doc.GetCharacterCount());
        Assert.Null(ex);
    }
}
