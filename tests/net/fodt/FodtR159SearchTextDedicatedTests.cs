// Tests for FodtDocument.SearchText dedicated coverage.
// Sprint: ff-sprint-s150-dotnet-deepening-20260628
// Ledger: PC-FODT-R159

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R159: Dedicated tests for FodtDocument.SearchText.
/// SearchText(query, comparison) returns a list of (ParagraphIndex, Position) tuples.
/// Throws ArgumentException for null or empty query.
/// Covers: null query throws; empty query throws; empty document returns empty;
/// query not found returns empty; single match returns one result;
/// paragraph index correct; position within paragraph correct;
/// multiple matches in same paragraph; case-insensitive comparison;
/// dogfood AppendParagraph->SearchText pipeline;
/// dogfood multiple paragraphs SearchText finds correct paragraph index.
/// </summary>
public class FodtR159SearchTextDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SearchText_NullQuery_ThrowsArgumentException()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Throws<ArgumentException>(() => doc.SearchText(null!));
    }

    [Fact]
    public void SearchText_EmptyQuery_ThrowsArgumentException()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Throws<ArgumentException>(() => doc.SearchText(string.Empty));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SearchText_EmptyDocument_ReturnsEmptyList()
    {
        var doc = FodtDocument.CreateEmpty();
        var results = doc.SearchText("hello");
        Assert.Empty(results);
    }

    [Fact]
    public void SearchText_QueryNotFound_ReturnsEmptyList()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("This is a sentence.");
        var results = doc.SearchText("missing");
        Assert.Empty(results);
    }

    [Fact]
    public void SearchText_SingleMatch_ReturnsOneResult()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world.");
        var results = doc.SearchText("world");
        Assert.Single(results);
    }

    [Fact]
    public void SearchText_SingleMatch_ParagraphIndexCorrect()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First paragraph.");
        doc.AppendParagraph("Hello world here.");
        var results = doc.SearchText("world");
        Assert.Equal(1, results[0].ParagraphIndex); // second paragraph (index 1)
    }

    [Fact]
    public void SearchText_SingleMatch_PositionCorrect()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world.");
        var results = doc.SearchText("world");
        Assert.Equal(6, results[0].Position); // "world" starts at index 6
    }

    [Fact]
    public void SearchText_MultipleMatchesInSameParagraph_ReturnsBoth()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("cat and cat and cat");
        var results = doc.SearchText("cat");
        Assert.Equal(3, results.Count);
    }

    [Fact]
    public void SearchText_CaseInsensitive_FindsMatch()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World.");
        var results = doc.SearchText("world", System.StringComparison.OrdinalIgnoreCase);
        Assert.Single(results);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendParagraph_SearchText_Found()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("The quick brown fox.");
        var results = doc.SearchText("quick");
        Assert.Single(results);
        Assert.Equal(0, results[0].ParagraphIndex);
        Assert.Equal(4, results[0].Position); // "quick" at index 4
    }

    [Fact]
    public void DogfoodPipeline_MultipleParagraphs_SearchFindsCorrectIndex()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Introduction");
        doc.AppendParagraph("Main body with keyword.");
        doc.AppendParagraph("Conclusion");
        var results = doc.SearchText("keyword");
        Assert.Single(results);
        Assert.Equal(1, results[0].ParagraphIndex);
    }
}
