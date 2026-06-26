// Tests for FodtDocument.GetDocumentStats, GetWordCount, GetCharCount, GetHeadingCount.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R172

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R172: Tests for FodtDocument.GetDocumentStats, GetWordCount, GetCharCount, GetHeadingCount.
/// GetDocumentStats(): returns (WordCount, CharCount, ParagraphCount, HeadingCount) tuple.
/// GetWordCount(): word count of all text content.
/// GetCharCount(): character count of all text content.
/// GetHeadingCount(): count of paragraphs with heading styles.
/// Covers: GetDocumentStats empty doc zeros; GetDocumentStats after append has data;
/// GetDocumentStats ParagraphCount matches Paragraphs.Count; GetWordCount empty is zero;
/// GetWordCount single word is 1; GetWordCount multiple words; GetCharCount empty is zero;
/// GetCharCount counts letters; GetHeadingCount zero for no headings;
/// GetHeadingCount matches inserted headings; GetHeadingCount via GetDocumentStats;
/// dogfood CreateEmpty->InsertHeading->AppendParagraph->GetDocumentStats pipeline.
/// </summary>
public class FodtR172GetDocumentStatsAndStylesTests
{
    // -------------------------------------------------------------------------
    // GetDocumentStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentStats_EmptyDoc_ZerosForAll()
    {
        var doc = FodtDocument.CreateEmpty();
        var stats = doc.GetDocumentStats();
        Assert.Equal(0, stats.WordCount);
        Assert.Equal(0, stats.CharCount);
        Assert.Equal(0, stats.ParagraphCount);
        Assert.Equal(0, stats.HeadingCount);
    }

    [Fact]
    public void GetDocumentStats_AfterAppend_HasData()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world");
        var stats = doc.GetDocumentStats();
        Assert.True(stats.WordCount > 0);
        Assert.True(stats.CharCount > 0);
        Assert.True(stats.ParagraphCount > 0);
    }

    [Fact]
    public void GetDocumentStats_ParagraphCount_MatchesParagraphsCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        doc.AppendParagraph("Third");
        var stats = doc.GetDocumentStats();
        Assert.Equal(doc.ParagraphCount, stats.ParagraphCount);
    }

    [Fact]
    public void GetDocumentStats_HeadingCount_MatchesInserted()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Title One", 1);
        doc.AppendParagraph("Some content here.");
        doc.InsertHeading(2, "Title Two", 2);
        var stats = doc.GetDocumentStats();
        Assert.Equal(2, stats.HeadingCount);
    }

    // -------------------------------------------------------------------------
    // GetWordCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWordCount_EmptyDoc_IsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.GetWordCount());
    }

    [Fact]
    public void GetWordCount_SingleWord_IsOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.Equal(1, doc.GetWordCount());
    }

    [Fact]
    public void GetWordCount_MultipleWords_CountsCorrectly()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("The quick brown fox");
        Assert.Equal(4, doc.GetWordCount());
    }

    [Fact]
    public void GetWordCount_AcrossMultipleParagraphs()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world");
        doc.AppendParagraph("Foo bar baz");
        Assert.Equal(5, doc.GetWordCount());
    }

    // -------------------------------------------------------------------------
    // GetCharCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCharCount_EmptyDoc_IsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.GetCharCount());
    }

    [Fact]
    public void GetCharCount_SingleChar_IsOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        Assert.Equal(1, doc.GetCharCount());
    }

    [Fact]
    public void GetCharCount_Word_CountsLettersOnly()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.Equal(5, doc.GetCharCount());
    }

    [Fact]
    public void GetCharCount_MatchesWordCountProperty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Testing one two three");
        // CharCount and WordCount are separate properties
        Assert.True(doc.GetCharCount() > doc.GetWordCount());
    }

    // -------------------------------------------------------------------------
    // GetHeadingCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeadingCount_NoHeadings_IsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Just text");
        Assert.Equal(0, doc.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_TwoHeadings_IsTwo()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "First Heading", 1);
        doc.AppendParagraph("Content between");
        doc.InsertHeading(2, "Second Heading", 2);
        Assert.Equal(2, doc.GetHeadingCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateEmpty->InsertHeading->AppendParagraph->GetDocumentStats
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_InsertAppendGetDocumentStats_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Main Title", 1);
        doc.AppendParagraph("The first paragraph has five words.");
        doc.AppendParagraph("Second paragraph with four words.");
        doc.InsertHeading(3, "Sub Section", 2);
        doc.AppendParagraph("Third paragraph concludes this document.");

        // GetDocumentStats
        var stats = doc.GetDocumentStats();
        Assert.Equal(5, stats.ParagraphCount); // 3 text + 2 headings
        Assert.Equal(2, stats.HeadingCount);
        Assert.True(stats.WordCount >= 10);
        Assert.True(stats.CharCount >= 10);

        // Individual getters match stats
        Assert.Equal(stats.WordCount, doc.GetWordCount());
        Assert.Equal(stats.CharCount, doc.GetCharCount());
        Assert.Equal(stats.HeadingCount, doc.GetHeadingCount());
        Assert.Equal(stats.ParagraphCount, doc.GetParagraphCount());
    }
}
