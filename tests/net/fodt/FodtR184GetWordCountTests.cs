// Tests for FodtDocument.GetWordCount dedicated coverage.
// Sprint: ff-sprint-s175-dotnet-deepening-20260628
// Ledger: PC-FODT-R184

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R184: Dedicated tests for FodtDocument.GetWordCount().
/// Returns total word count across all paragraphs and headings.
/// Words are sequences of non-whitespace characters (Split on whitespace).
/// Empty paragraphs and whitespace-only paragraphs contribute zero.
/// Headings (text:h) are included in the count.
/// Covers: empty doc=0; single paragraph single word; multi-word paragraph;
/// headings included; whitespace-only paragraph excluded;
/// multiple paragraphs sum; empty paragraph excluded;
/// word count matches manual count; dogfood AppendHeading+AppendParagraph;
/// dogfood multiple paragraphs pipeline.
/// </summary>
public class FodtR184GetWordCountTests
{
    // -------------------------------------------------------------------------
    // Basic tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWordCount_EmptyDocument_ReturnsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.GetWordCount());
    }

    [Fact]
    public void GetWordCount_SingleWordParagraph_ReturnsOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.Equal(1, doc.GetWordCount());
    }

    [Fact]
    public void GetWordCount_MultiWordParagraph_ReturnsCorrectCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World Test");
        Assert.Equal(3, doc.GetWordCount());
    }

    [Fact]
    public void GetWordCount_HeadingsIncluded_CountedInTotal()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Introduction Section", 1);
        // heading has 2 words
        Assert.Equal(2, doc.GetWordCount());
    }

    [Fact]
    public void GetWordCount_WhitespaceOnlyParagraph_ContributesZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("   ");
        Assert.Equal(0, doc.GetWordCount());
    }

    [Fact]
    public void GetWordCount_EmptyParagraph_ContributesZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("");
        Assert.Equal(0, doc.GetWordCount());
    }

    [Fact]
    public void GetWordCount_MultipleParagraphs_SumsAll()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("One two three"); // 3
        doc.AppendParagraph("Four five");     // 2
        Assert.Equal(5, doc.GetWordCount());
    }

    [Fact]
    public void GetWordCount_MatchesManualCount()
    {
        var doc = FodtDocument.CreateEmpty();
        var text = "The quick brown fox";
        doc.AppendParagraph(text);
        var expected = text.Split(' ').Length;
        Assert.Equal(expected, doc.GetWordCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MixedContent_HeadingsAndParagraphsBothCounted()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter One", 1);      // 2 words
        doc.AppendParagraph("Body text here.");    // 3 words
        doc.AppendHeading("Chapter Two", 2);      // 2 words
        doc.AppendParagraph("More content.");      // 2 words
        Assert.Equal(9, doc.GetWordCount());
    }

    [Fact]
    public void DogfoodPipeline_AppendParagraph_IncrementsWordCount()
    {
        var doc = FodtDocument.CreateEmpty();
        var before = doc.GetWordCount();
        doc.AppendParagraph("New words added here"); // 4 words
        Assert.Equal(before + 4, doc.GetWordCount());
    }
}
