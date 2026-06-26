// Tests for FodtDocument.WordCount, CharCount properties and SearchText method.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R164

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R164: Tests for FodtDocument.WordCount, CharCount properties and SearchText.
/// WordCount: count of whitespace-split tokens across all paragraphs (property, not method).
/// CharCount: sum of all paragraph text lengths including spaces (property, not method).
/// SearchText(query): finds all occurrences of query; returns list of (ParagraphIndex, Position).
/// SearchText(query, comparison): with explicit StringComparison.
/// Covers: WordCount empty doc is 0; WordCount single word is 1; WordCount multiple paragraphs accumulates;
/// CharCount empty doc is 0; CharCount single char is 1; CharCount includes spaces;
/// WordCount consistent with GetDocumentStats; CharCount consistent with GetDocumentStats;
/// SearchText single match found; SearchText no match returns empty; SearchText multiple matches;
/// SearchText case-insensitive with OrdinalIgnoreCase; SearchText returns ParagraphIndex correctly;
/// dogfood CreateEmpty->InsertHeading->AppendParagraph->WordCount->CharCount->SearchText pipeline.
/// </summary>
public class FodtR164WordCountCharCountAndSearchTextTests
{
    // -------------------------------------------------------------------------
    // WordCount property
    // -------------------------------------------------------------------------

    [Fact]
    public void WordCount_EmptyDoc_IsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.WordCount);
    }

    [Fact]
    public void WordCount_SingleWord_IsOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.Equal(1, doc.WordCount);
    }

    [Fact]
    public void WordCount_MultipleParagraphs_Accumulates()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("alpha beta");      // 2
        doc.AppendParagraph("gamma delta epsilon"); // 3
        Assert.Equal(5, doc.WordCount);
    }

    [Fact]
    public void WordCount_ConsistentWithGetDocumentStats()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Introduction", 1);
        doc.AppendParagraph("The quick brown fox.");
        var stats = doc.GetDocumentStats();
        Assert.Equal(stats.WordCount, doc.WordCount);
    }

    // -------------------------------------------------------------------------
    // CharCount property
    // -------------------------------------------------------------------------

    [Fact]
    public void CharCount_EmptyDoc_IsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.CharCount);
    }

    [Fact]
    public void CharCount_SingleChar_IsOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("X");
        Assert.Equal(1, doc.CharCount);
    }

    [Fact]
    public void CharCount_IncludesSpaces()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hi there"); // 8 chars
        Assert.Equal(8, doc.CharCount);
    }

    [Fact]
    public void CharCount_ConsistentWithGetDocumentStats()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Test content here.");
        var stats = doc.GetDocumentStats();
        Assert.Equal(stats.CharCount, doc.CharCount);
    }

    // -------------------------------------------------------------------------
    // SearchText
    // -------------------------------------------------------------------------

    [Fact]
    public void SearchText_SingleMatch_ReturnsOneResult()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world.");
        var results = doc.SearchText("world");
        Assert.Single(results);
    }

    [Fact]
    public void SearchText_NoMatch_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world.");
        var results = doc.SearchText("missing");
        Assert.Empty(results);
    }

    [Fact]
    public void SearchText_MultipleMatches_ReturnsAll()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("foo bar foo"); // 2 occurrences
        doc.AppendParagraph("foo qux");     // 1 occurrence
        var results = doc.SearchText("foo");
        Assert.Equal(3, results.Count);
    }

    [Fact]
    public void SearchText_CaseSensitiveDefault_CaseMismatchNotFound()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World.");
        var results = doc.SearchText("hello");
        Assert.Empty(results);
    }

    [Fact]
    public void SearchText_CaseInsensitive_FindsMatch()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World.");
        var results = doc.SearchText("hello", StringComparison.OrdinalIgnoreCase);
        Assert.Single(results);
    }

    [Fact]
    public void SearchText_ReturnsParagraphIndex()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First paragraph.");
        doc.AppendParagraph("Second paragraph with target.");
        var results = doc.SearchText("target");
        Assert.Single(results);
        Assert.Equal(1, results[0].ParagraphIndex);
    }

    [Fact]
    public void SearchText_ReturnsPosition()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Find me here.");
        var results = doc.SearchText("me");
        Assert.Single(results);
        Assert.True(results[0].Position >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateEmpty->InsertHeading->AppendParagraph->WordCount->CharCount->SearchText
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WordCountCharCountSearchText_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Overview", 1);          // 1 word, 8 chars
        doc.AppendParagraph("The quick brown fox.");   // 4 words, 20 chars
        doc.AppendParagraph("The lazy dog.");          // 3 words, 13 chars

        Assert.Equal(8, doc.WordCount); // 1+4+3
        Assert.True(doc.CharCount > 0);

        // Consistent with GetDocumentStats
        var stats = doc.GetDocumentStats();
        Assert.Equal(stats.WordCount, doc.WordCount);
        Assert.Equal(stats.CharCount, doc.CharCount);

        // Search across paragraphs
        var theResults = doc.SearchText("The");
        Assert.Equal(2, theResults.Count); // In two paragraphs
    }
}
