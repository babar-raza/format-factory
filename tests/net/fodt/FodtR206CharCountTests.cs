// Tests for FodtDocument.CharCount dedicated coverage.
// Sprint: ff-sprint-s193-dotnet-deepening-20260629
// Ledger: PC-FODT-R206

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R206: Dedicated tests for FodtDocument.CharCount property.
/// Returns the total character count across all paragraphs (including headings).
/// Empty document returns 0.
/// Empty paragraph contributes 0 characters.
/// Single word paragraph returns its length.
/// Multiple paragraphs sum their character counts.
/// Headings are counted the same as body paragraphs.
/// After adding a paragraph, CharCount increases by that paragraph's length.
/// After removing a paragraph, CharCount decreases.
/// CharCount includes spaces and punctuation.
/// Covers: empty doc 0; empty para 0; single word length; two paras sum;
/// heading counted; added para increases count; removed para decreases count;
/// spaces counted; dogfood three paras total length; dogfood add and remove.
/// </summary>
public class FodtR206CharCountTests
{
    // -------------------------------------------------------------------------
    // Basic tests
    // -------------------------------------------------------------------------

    [Fact]
    public void CharCount_EmptyDocument_ReturnsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.CharCount);
    }

    [Fact]
    public void CharCount_EmptyParagraph_ReturnsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph(string.Empty);
        Assert.Equal(0, doc.CharCount);
    }

    [Fact]
    public void CharCount_SingleWord_ReturnsWordLength()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.Equal(5, doc.CharCount);
    }

    [Fact]
    public void CharCount_TwoParagraphs_ReturnsSumOfLengths()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");   // 5
        doc.AppendParagraph("World");   // 5
        Assert.Equal(10, doc.CharCount);
    }

    [Fact]
    public void CharCount_HeadingCounted()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1); // 5 chars
        Assert.Equal(5, doc.CharCount);
    }

    [Fact]
    public void CharCount_AfterAppend_IncreasedByParaLength()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("ABC");
        var before = doc.CharCount;
        doc.AppendParagraph("XY");
        Assert.Equal(before + 2, doc.CharCount);
    }

    [Fact]
    public void CharCount_AfterRemoveParagraph_DecreasedByParaLength()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("ABC");   // 3
        doc.AppendParagraph("DE");    // 2
        doc.RemoveParagraph(1);
        Assert.Equal(3, doc.CharCount);
    }

    [Fact]
    public void CharCount_SpacesAndPunctuationCounted()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hi, World!");  // 10
        Assert.Equal(10, doc.CharCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ThreeParagraphs_TotalLength()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("One");    // 3
        doc.AppendParagraph("Two");    // 3
        doc.AppendParagraph("Three"); // 5
        Assert.Equal(11, doc.CharCount);
    }

    [Fact]
    public void DogfoodPipeline_AddAndRemove_CountAccurate()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");  // 5
        doc.AppendParagraph("Beta");   // 4
        Assert.Equal(9, doc.CharCount);
        doc.RemoveParagraph(0);
        Assert.Equal(4, doc.CharCount);
    }
}
