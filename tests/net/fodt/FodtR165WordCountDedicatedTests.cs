// Tests for FodtDocument.WordCount dedicated coverage.
// Sprint: ff-sprint-s156-dotnet-deepening-20260628
// Ledger: PC-FODT-R165

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R165: Dedicated tests for FodtDocument.WordCount property.
/// WordCount returns the number of whitespace-separated tokens across all paragraphs.
/// Uses GetPlainText() then splits on whitespace with RemoveEmptyEntries.
/// Empty document returns 0. Whitespace-only returns 0.
/// Covers: empty document returns 0; single word returns 1; two words returns 2;
/// multiple words across one paragraph; WordCount is non-negative; WordCount is idempotent;
/// WordCount increases after AppendParagraph with text; whitespace-only paragraph returns 0;
/// dogfood AppendParagraph->WordCount pipeline; dogfood multi-paragraph word count sums correctly.
/// </summary>
public class FodtR165WordCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Zero tests
    // -------------------------------------------------------------------------

    [Fact]
    public void WordCount_EmptyDocument_ReturnsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.WordCount);
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void WordCount_SingleWord_ReturnsOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.Equal(1, doc.WordCount);
    }

    [Fact]
    public void WordCount_TwoWords_ReturnsTwo()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World");
        Assert.Equal(2, doc.WordCount);
    }

    [Fact]
    public void WordCount_MultipleWords_CountedCorrectly()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("The quick brown fox");
        Assert.Equal(4, doc.WordCount);
    }

    [Fact]
    public void WordCount_IsNonNegative()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.True(doc.WordCount >= 0);
    }

    [Fact]
    public void WordCount_IsIdempotent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Test paragraph");
        var first = doc.WordCount;
        var second = doc.WordCount;
        Assert.Equal(first, second);
    }

    [Fact]
    public void WordCount_IncreasesAfterAppendParagraph()
    {
        var doc = FodtDocument.CreateEmpty();
        var before = doc.WordCount;
        doc.AppendParagraph("New words added");
        Assert.True(doc.WordCount > before);
    }

    [Fact]
    public void WordCount_WhitespaceOnlyParagraph_ReturnsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("   ");
        Assert.Equal(0, doc.WordCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendParagraph_WordCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("one two three");
        Assert.Equal(3, doc.WordCount);
    }

    [Fact]
    public void DogfoodPipeline_MultiParagraph_WordCountSumsCorrectly()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World");   // 2 words
        doc.AppendParagraph("foo bar baz");   // 3 words
        Assert.Equal(5, doc.WordCount);
    }
}
