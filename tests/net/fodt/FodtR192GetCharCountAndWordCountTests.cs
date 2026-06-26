// Tests for FodtDocument.GetCharCount, GetWordCount, GetHeadingCount, GetParagraphCount.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R192

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R192: Tests for FodtDocument.GetCharCount, GetWordCount, GetHeadingCount, GetDocumentStats.
/// GetCharCount(): total character count.
/// GetWordCount(): total word count.
/// GetHeadingCount(): number of headings.
/// GetDocumentStats(): returns (WordCount, CharCount, ParagraphCount, HeadingCount).
/// Covers: GetCharCount positive after AppendParagraph; GetCharCount increases with more text;
/// GetWordCount positive after AppendParagraph; GetWordCount known value;
/// GetHeadingCount 0 for no headings; GetHeadingCount increments after InsertHeading;
/// GetHeadingCount after RemoveHeading; GetDocumentStats all positive;
/// GetDocumentStats WordCount matches GetWordCount; GetDocumentStats HeadingCount matches;
/// GetDocumentStats ParagraphCount matches; CharCount matches WordCount context;
/// WordCount after RemoveAllParagraphs is zero; CharCount after RemoveAllParagraphs;
/// dogfood CreateEmpty->Headings->Paragraphs->GetDocumentStats verify.
/// </summary>
public class FodtR192GetCharCountAndWordCountTests
{
    // -------------------------------------------------------------------------
    // GetCharCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCharCount_PositiveAfterAppendParagraph()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some text here.");
        Assert.True(doc.GetCharCount() > 0);
    }

    [Fact]
    public void GetCharCount_IncreasesWithMoreText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Short.");
        var c1 = doc.GetCharCount();
        doc.AppendParagraph("A much longer paragraph with many more characters to count.");
        var c2 = doc.GetCharCount();
        Assert.True(c2 > c1);
    }

    [Fact]
    public void GetCharCount_AfterRemoveAllParagraphs_IsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Text to be removed.");
        doc.RemoveAllParagraphs();
        Assert.Equal(0, doc.GetCharCount());
    }

    // -------------------------------------------------------------------------
    // GetWordCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWordCount_PositiveAfterAppendParagraph()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world test.");
        Assert.True(doc.GetWordCount() > 0);
    }

    [Fact]
    public void GetWordCount_KnownValue()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("one two three four five");
        Assert.Equal(5, doc.GetWordCount());
    }

    [Fact]
    public void GetWordCount_AfterRemoveAllParagraphs_IsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Words to remove.");
        doc.RemoveAllParagraphs();
        Assert.Equal(0, doc.GetWordCount());
    }

    // -------------------------------------------------------------------------
    // GetHeadingCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeadingCount_ZeroForNoParagraphs()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_IncrementsAfterInsertHeading()
    {
        var doc = FodtDocument.CreateEmpty();
        var before = doc.GetHeadingCount();
        doc.InsertHeading(0, "A Heading", 1);
        Assert.Equal(before + 1, doc.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_AfterRemoveHeading_Decrements()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "First Heading", 1);
        doc.InsertHeading(1, "Second Heading", 2);
        var before = doc.GetHeadingCount();
        doc.RemoveHeading(0);
        Assert.Equal(before - 1, doc.GetHeadingCount());
    }

    // -------------------------------------------------------------------------
    // GetDocumentStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentStats_AllPositiveAfterContent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Chapter", 1);
        doc.AppendParagraph("Some paragraph content here.");
        var stats = doc.GetDocumentStats();
        Assert.True(stats.WordCount > 0);
        Assert.True(stats.CharCount > 0);
        Assert.True(stats.ParagraphCount > 0);
        Assert.True(stats.HeadingCount > 0);
    }

    [Fact]
    public void GetDocumentStats_WordCount_MatchesGetWordCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("word1 word2 word3");
        var stats = doc.GetDocumentStats();
        Assert.Equal(doc.GetWordCount(), stats.WordCount);
    }

    [Fact]
    public void GetDocumentStats_HeadingCount_MatchesGetHeadingCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "H1", 1);
        doc.InsertHeading(1, "H2", 2);
        var stats = doc.GetDocumentStats();
        Assert.Equal(doc.GetHeadingCount(), stats.HeadingCount);
    }

    [Fact]
    public void GetDocumentStats_ParagraphCount_MatchesParagraphCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("P1");
        doc.AppendParagraph("P2");
        var stats = doc.GetDocumentStats();
        Assert.Equal(doc.ParagraphCount, stats.ParagraphCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateEmpty->Headings->Paragraphs->GetDocumentStats
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateHeadingsParagraphsGetDocumentStats_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();

        // Add headings
        doc.InsertHeading(0, "Introduction", 1);
        doc.InsertHeading(1, "Methods", 1);
        doc.InsertHeading(2, "Subsection A", 2);

        // Add paragraphs
        doc.AppendParagraph("First paragraph content.");
        doc.AppendParagraph("Second paragraph content here.");
        doc.AppendParagraph("Third paragraph for testing.");

        // Verify counts
        Assert.Equal(3, doc.GetHeadingCount());
        Assert.True(doc.GetWordCount() > 0);
        Assert.True(doc.GetCharCount() > 0);

        // GetDocumentStats
        var stats = doc.GetDocumentStats();
        Assert.Equal(3, stats.HeadingCount);
        Assert.Equal(doc.ParagraphCount, stats.ParagraphCount);
        Assert.Equal(doc.GetWordCount(), stats.WordCount);
        Assert.Equal(doc.GetCharCount(), stats.CharCount);

        // CharCount is always >= WordCount (has spaces)
        Assert.True(stats.CharCount >= stats.WordCount);
    }
}
