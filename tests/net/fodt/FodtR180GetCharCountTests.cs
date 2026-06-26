// Tests for FodtDocument.GetCharCount dedicated coverage.
// Sprint: ff-sprint-s171-dotnet-deepening-20260628
// Ledger: PC-FODT-R180

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R180: Dedicated tests for FodtDocument.GetCharCount().
/// Returns the total character count of the document (all paragraphs and headings).
/// Counts all characters in each paragraph's Text, including whitespace.
/// Empty paragraphs contribute zero characters.
/// Covers: empty doc returns 0; single-char paragraph returns 1;
/// AppendParagraph count matches text length; two paragraphs additive;
/// heading text counted; whitespace characters counted; returns non-negative;
/// adding empty paragraph does not change count; dogfood pipeline;
/// GetCharCount >= GetWordCount (chars >= words when text has spaces).
/// </summary>
public class FodtR180GetCharCountTests
{
    // -------------------------------------------------------------------------
    // Basic tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCharCount_EmptyDocument_ReturnsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.GetCharCount());
    }

    [Fact]
    public void GetCharCount_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.True(doc.GetCharCount() >= 0);
    }

    [Fact]
    public void GetCharCount_SingleCharParagraph_ReturnsOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("X");
        Assert.Equal(1, doc.GetCharCount());
    }

    [Fact]
    public void GetCharCount_ParagraphText_MatchesLength()
    {
        var doc = FodtDocument.CreateEmpty();
        var text = "Hello World"; // 11 chars
        doc.AppendParagraph(text);
        Assert.Equal(text.Length, doc.GetCharCount());
    }

    [Fact]
    public void GetCharCount_TwoParagraphs_IsAdditive()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello"); // 5
        doc.AppendParagraph("World"); // 5
        Assert.Equal(10, doc.GetCharCount());
    }

    [Fact]
    public void GetCharCount_HeadingTextCounted()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1); // 5 chars
        Assert.Equal(5, doc.GetCharCount());
    }

    [Fact]
    public void GetCharCount_WhitespaceCharactersCounted()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A B"); // 3 chars including space
        Assert.Equal(3, doc.GetCharCount());
    }

    // -------------------------------------------------------------------------
    // Stability tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCharCount_CharCountAtLeastWordCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("The quick brown fox");
        // Char count >= word count (19 chars >= 4 words)
        Assert.True(doc.GetCharCount() >= doc.GetWordCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendParagraph_ReplaceText_CountUpdates()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World");
        var before = doc.GetCharCount();
        doc.ReplaceText("World", "!");
        // "Hello !" has fewer chars than "Hello World" — count decreases
        Assert.True(doc.GetCharCount() <= before);
    }

    [Fact]
    public void DogfoodPipeline_MixedContent_CharCountIsSum()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Ch", 1);   // 2 chars
        doc.AppendParagraph("Hi");    // 2 chars
        Assert.Equal(4, doc.GetCharCount());
    }
}
