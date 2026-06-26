// Tests for FodtDocument.FindParagraph dedicated coverage.
// Sprint: ff-sprint-s201-dotnet-deepening-20260629
// Ledger: PC-FODT-R216

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R216: Dedicated tests for FodtDocument.FindParagraph(string searchText).
/// null searchText → ArgumentNullException.
/// Empty document → returns -1 (not found).
/// Text not present → returns -1.
/// Single paragraph match → returns 0.
/// Match in second paragraph → returns 1.
/// Partial match (substring) → returns index.
/// Case-sensitive: different case returns -1.
/// First occurrence: if text in two paragraphs, returns first index.
/// ParagraphCount unchanged after find.
/// Dogfood: add paragraphs, find each.
/// </summary>
public class FodtR216FindParagraphTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FindParagraph_NullSearchText_ThrowsArgumentNullException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.Throws<ArgumentNullException>(() => doc.FindParagraph(null!));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FindParagraph_EmptyDocument_ReturnsMinusOne()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(-1, doc.FindParagraph("anything"));
    }

    [Fact]
    public void FindParagraph_TextNotPresent_ReturnsMinusOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World");
        Assert.Equal(-1, doc.FindParagraph("NotHere"));
    }

    [Fact]
    public void FindParagraph_FirstParagraphMatch_ReturnsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World");
        Assert.Equal(0, doc.FindParagraph("Hello"));
    }

    [Fact]
    public void FindParagraph_SecondParagraphMatch_ReturnsOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        Assert.Equal(1, doc.FindParagraph("Beta"));
    }

    [Fact]
    public void FindParagraph_SubstringMatch_ReturnsIndex()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("The quick brown fox");
        Assert.Equal(0, doc.FindParagraph("quick"));
    }

    [Fact]
    public void FindParagraph_CaseSensitive_DifferentCaseReturnsMinusOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("hello world");
        Assert.Equal(-1, doc.FindParagraph("Hello"));
    }

    [Fact]
    public void FindParagraph_FirstOccurrence_ReturnsSmallestIndex()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Match here");
        doc.AppendParagraph("Also Match here");
        // Should return 0, the first match
        Assert.Equal(0, doc.FindParagraph("Match"));
    }

    [Fact]
    public void FindParagraph_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        doc.AppendParagraph("B");
        int before = doc.ParagraphCount;
        doc.FindParagraph("A");
        Assert.Equal(before, doc.ParagraphCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FindEachParagraph()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First paragraph");
        doc.AppendParagraph("Second paragraph");
        doc.AppendParagraph("Third paragraph");
        Assert.Equal(0, doc.FindParagraph("First"));
        Assert.Equal(1, doc.FindParagraph("Second"));
        Assert.Equal(2, doc.FindParagraph("Third"));
    }

    [Fact]
    public void DogfoodPipeline_HeadingSearchable()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Document Title", 1);
        doc.AppendParagraph("Body content");
        // Heading should be findable
        var idx = doc.FindParagraph("Document Title");
        Assert.True(idx >= 0, "Heading text should be findable by FindParagraph");
    }
}
