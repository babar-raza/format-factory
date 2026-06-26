// Tests for FodtDocument.WordCount dedicated coverage.
// Sprint: ff-sprint-s197-dotnet-deepening-20260629
// Ledger: PC-FODT-R211

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R211: Dedicated tests for FodtDocument.WordCount property.
/// Returns total whitespace-delimited word count across all paragraphs.
/// Empty document returns 0.
/// Whitespace-only paragraph returns 0.
/// Single word returns 1.
/// Two words in one paragraph returns 2.
/// Words across multiple paragraphs are summed.
/// Headings contribute their words.
/// After adding a paragraph, WordCount increases.
/// After removing a paragraph, WordCount decreases.
/// Punctuation attached to word (no space) counts as one word.
/// Covers: empty=0; whitespace-only=0; single word=1; two words=2;
/// two paras summed; heading counted; after-append increases; after-remove decreases;
/// punctuation-attached counts; dogfood three paras total; dogfood add-remove.
/// </summary>
public class FodtR211WordCountTests
{
    // -------------------------------------------------------------------------
    // Basic tests
    // -------------------------------------------------------------------------

    [Fact]
    public void WordCount_EmptyDocument_ReturnsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.WordCount);
    }

    [Fact]
    public void WordCount_WhitespaceOnlyParagraph_ReturnsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("   ");
        Assert.Equal(0, doc.WordCount);
    }

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
    public void WordCount_TwoParagraphs_Summed()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World");  // 2
        doc.AppendParagraph("Foo Bar Baz");  // 3
        Assert.Equal(5, doc.WordCount);
    }

    [Fact]
    public void WordCount_HeadingCounted()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("My Title", 1); // 2 words
        Assert.Equal(2, doc.WordCount);
    }

    [Fact]
    public void WordCount_AfterAppend_Increases()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("One");
        var before = doc.WordCount;
        doc.AppendParagraph("Two Three");
        Assert.Equal(before + 2, doc.WordCount);
    }

    [Fact]
    public void WordCount_AfterRemove_Decreases()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("One Two");
        doc.AppendParagraph("Three");
        doc.RemoveParagraph(1);
        Assert.Equal(2, doc.WordCount);
    }

    [Fact]
    public void WordCount_PunctuationAttached_CountedAsOneWord()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello, World!");  // "Hello," and "World!" are 2 tokens
        Assert.Equal(2, doc.WordCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ThreeParagraphs_TotalWords()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha Beta");    // 2
        doc.AppendParagraph("Gamma");         // 1
        doc.AppendParagraph("Delta Epsilon"); // 2
        Assert.Equal(5, doc.WordCount);
    }

    [Fact]
    public void DogfoodPipeline_AddAndRemove_CountAccurate()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("One Two Three"); // 3
        Assert.Equal(3, doc.WordCount);
        doc.AppendParagraph("Four Five");     // 2 more = 5
        Assert.Equal(5, doc.WordCount);
        doc.RemoveParagraph(1);               // remove "Four Five"
        Assert.Equal(3, doc.WordCount);
    }
}
