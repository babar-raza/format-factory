// Tests for FodtDocument.SearchText dedicated coverage.
// Sprint: ff-sprint-s164-dotnet-deepening-20260628
// Ledger: PC-FODT-R173

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R173: Dedicated tests for FodtDocument.SearchText(string query, StringComparison comparison).
/// SearchText returns all (ParagraphIndex, Position) matches of the query string.
/// Throws ArgumentException if query is null or empty.
/// Empty document returns empty list. No matches returns empty list.
/// Covers: null query throws ArgumentException; empty query throws ArgumentException;
/// empty document returns empty; no match returns empty; single match returns one result;
/// paragraph index correct; position correct within paragraph;
/// multiple occurrences in same paragraph; match across multiple paragraphs;
/// dogfood AppendParagraph->SearchText pipeline; dogfood case-insensitive comparison.
/// </summary>
public class FodtR173SearchTextDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SearchText_NullQuery_ThrowsArgumentException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some text");
        Assert.Throws<ArgumentException>(() => doc.SearchText(null!));
    }

    [Fact]
    public void SearchText_EmptyQuery_ThrowsArgumentException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some text");
        Assert.Throws<ArgumentException>(() => doc.SearchText(string.Empty));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SearchText_EmptyDocument_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Empty(doc.SearchText("hello"));
    }

    [Fact]
    public void SearchText_NoMatch_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World");
        Assert.Empty(doc.SearchText("xyz"));
    }

    [Fact]
    public void SearchText_SingleMatch_ReturnsOneResult()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World");
        var results = doc.SearchText("World");
        Assert.Single(results);
    }

    [Fact]
    public void SearchText_ParagraphIndexCorrect()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First para");
        doc.AppendParagraph("Second para with target");
        var results = doc.SearchText("target");
        Assert.Single(results);
        Assert.Equal(1, results[0].ParagraphIndex);
    }

    [Fact]
    public void SearchText_PositionCorrect()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World");
        var results = doc.SearchText("World");
        Assert.Equal(6, results[0].Position);
    }

    [Fact]
    public void SearchText_MultipleOccurrencesInOneParagraph_AllReturned()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("cat and cat and cat");
        var results = doc.SearchText("cat");
        Assert.Equal(3, results.Count);
    }

    [Fact]
    public void SearchText_MatchAcrossMultipleParagraphs_AllReturned()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("word here");
        doc.AppendParagraph("another word");
        var results = doc.SearchText("word");
        Assert.Equal(2, results.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendParagraph_SearchText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Introduction section");
        doc.AppendParagraph("Main content section");
        var results = doc.SearchText("section");
        Assert.Equal(2, results.Count);
        Assert.Equal(0, results[0].ParagraphIndex);
        Assert.Equal(1, results[1].ParagraphIndex);
    }

    [Fact]
    public void DogfoodPipeline_CaseInsensitiveComparison()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello WORLD");
        var results = doc.SearchText("world", StringComparison.OrdinalIgnoreCase);
        Assert.Single(results);
        Assert.Equal(6, results[0].Position);
    }
}
