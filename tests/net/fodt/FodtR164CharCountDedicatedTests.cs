// Tests for FodtDocument.CharCount dedicated coverage.
// Sprint: ff-sprint-s155-dotnet-deepening-20260628
// Ledger: PC-FODT-R164

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R164: Dedicated tests for FodtDocument.CharCount property.
/// CharCount returns the total number of characters across all paragraphs (sum of text lengths).
/// Empty paragraphs contribute 0. Null paragraph text contributes 0.
/// Covers: empty document returns 0; single paragraph length matches; two paragraphs sum correctly;
/// paragraph with spaces counted; CharCount is non-negative always; CharCount is idempotent;
/// CharCount increases after AppendParagraph; empty paragraph contributes 0;
/// dogfood AppendParagraph->CharCount pipeline; dogfood multi-paragraph total sum.
/// </summary>
public class FodtR164CharCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Zero tests
    // -------------------------------------------------------------------------

    [Fact]
    public void CharCount_EmptyDocument_ReturnsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.CharCount);
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void CharCount_SingleParagraph_MatchesTextLength()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.Equal(5, doc.CharCount);
    }

    [Fact]
    public void CharCount_TwoParagraphs_SumsCorrectly()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hi");    // 2 chars
        doc.AppendParagraph("World"); // 5 chars
        Assert.Equal(7, doc.CharCount);
    }

    [Fact]
    public void CharCount_ParagraphWithSpaces_SpacesIncluded()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World"); // 11 chars (includes space)
        Assert.Equal(11, doc.CharCount);
    }

    [Fact]
    public void CharCount_IsNonNegative()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.True(doc.CharCount >= 0);
    }

    [Fact]
    public void CharCount_IsIdempotent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Test text");
        var first = doc.CharCount;
        var second = doc.CharCount;
        Assert.Equal(first, second);
    }

    [Fact]
    public void CharCount_IncreasesAfterAppendParagraph()
    {
        var doc = FodtDocument.CreateEmpty();
        var before = doc.CharCount;
        doc.AppendParagraph("New paragraph");
        Assert.True(doc.CharCount > before);
    }

    [Fact]
    public void CharCount_EmptyParagraphTextContributesZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph(string.Empty);
        Assert.Equal(0, doc.CharCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendParagraph_CharCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("abc"); // 3
        doc.AppendParagraph("de");  // 2
        Assert.Equal(5, doc.CharCount);
    }

    [Fact]
    public void DogfoodPipeline_MultiParagraph_TotalSum()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("The");    // 3
        doc.AppendParagraph("quick");  // 5
        doc.AppendParagraph("brown");  // 5
        doc.AppendParagraph("fox");    // 3
        Assert.Equal(16, doc.CharCount);
    }
}
