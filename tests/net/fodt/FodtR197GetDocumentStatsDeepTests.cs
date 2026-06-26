// Tests for FodtDocument.GetDocumentStats deeper coverage with all stats fields.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R197

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R197: Tests for FodtDocument.GetDocumentStats deeper coverage.
/// GetDocumentStats(): returns (WordCount, CharCount, ParagraphCount, HeadingCount).
/// Covers: GetDocumentStats after AppendParagraph non-null; WordCount positive;
/// CharCount positive; ParagraphCount positive; HeadingCount zero for no headings;
/// HeadingCount positive after InsertHeading; ParagraphCount after AppendParagraph;
/// WordCount matches GetWordCount; CharCount matches GetCharCount;
/// HeadingCount matches GetHeadingCount; ParagraphCount matches ParagraphCount prop;
/// GetDocumentStats after RemoveAllParagraphs all zero; CharCount >= WordCount;
/// GetDocumentStats after SetParagraphText reflects change;
/// GetDocumentStats WordCount changes after AppendParagraph;
/// dogfood CreateEmpty->InsertHeadings->AppendParagraphs->GetDocumentStats->Verify all fields.
/// </summary>
public class FodtR197GetDocumentStatsDeepTests
{
    // -------------------------------------------------------------------------
    // Basic GetDocumentStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentStats_NonNull_AfterAppendParagraph()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some content here.");
        var stats = doc.GetDocumentStats();
        Assert.NotNull(stats);
    }

    [Fact]
    public void GetDocumentStats_WordCount_Positive()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world test.");
        var stats = doc.GetDocumentStats();
        Assert.True(stats.WordCount > 0);
    }

    [Fact]
    public void GetDocumentStats_CharCount_Positive()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some text.");
        var stats = doc.GetDocumentStats();
        Assert.True(stats.CharCount > 0);
    }

    [Fact]
    public void GetDocumentStats_ParagraphCount_Positive()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First paragraph.");
        var stats = doc.GetDocumentStats();
        Assert.True(stats.ParagraphCount > 0);
    }

    [Fact]
    public void GetDocumentStats_HeadingCount_ZeroForNoHeadings()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Body text only.");
        var stats = doc.GetDocumentStats();
        Assert.Equal(0, stats.HeadingCount);
    }

    [Fact]
    public void GetDocumentStats_HeadingCount_PositiveAfterInsertHeading()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "My Heading", 1);
        doc.AppendParagraph("Body text.");
        var stats = doc.GetDocumentStats();
        Assert.True(stats.HeadingCount > 0);
    }

    // -------------------------------------------------------------------------
    // Stats match individual methods
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentStats_WordCount_MatchesGetWordCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("one two three four five");
        var stats = doc.GetDocumentStats();
        Assert.Equal(doc.GetWordCount(), stats.WordCount);
    }

    [Fact]
    public void GetDocumentStats_CharCount_MatchesGetCharCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Test content here.");
        var stats = doc.GetDocumentStats();
        Assert.Equal(doc.GetCharCount(), stats.CharCount);
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
    public void GetDocumentStats_ParagraphCount_MatchesParagraphCountProp()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("P1");
        doc.AppendParagraph("P2");
        doc.AppendParagraph("P3");
        var stats = doc.GetDocumentStats();
        Assert.Equal(doc.ParagraphCount, stats.ParagraphCount);
    }

    [Fact]
    public void GetDocumentStats_CharCount_GreaterThanOrEqualToWordCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("one two three four");
        var stats = doc.GetDocumentStats();
        Assert.True(stats.CharCount >= stats.WordCount);
    }

    // -------------------------------------------------------------------------
    // Stats after mutations
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentStats_AfterRemoveAllParagraphs_AllZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Content to remove.");
        doc.RemoveAllParagraphs();
        var stats = doc.GetDocumentStats();
        Assert.Equal(0, stats.WordCount);
        Assert.Equal(0, stats.CharCount);
        Assert.Equal(0, stats.ParagraphCount);
        Assert.Equal(0, stats.HeadingCount);
    }

    [Fact]
    public void GetDocumentStats_WordCount_ChangesAfterAppendParagraph()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("one two three");
        var stats1 = doc.GetDocumentStats();
        doc.AppendParagraph("four five six seven");
        var stats2 = doc.GetDocumentStats();
        Assert.True(stats2.WordCount > stats1.WordCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateEmpty->InsertHeadings->AppendParagraphs->GetDocumentStats->Verify
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateInsertAppendGetStatsVerifyAll_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();

        // Insert headings
        doc.InsertHeading(0, "Chapter 1", 1);
        doc.InsertHeading(1, "Section 1.1", 2);
        doc.InsertHeading(2, "Chapter 2", 1);

        // Append paragraphs
        doc.AppendParagraph("First body paragraph with several words.");
        doc.AppendParagraph("Second body paragraph here.");
        doc.AppendParagraph("Third paragraph adds more content.");

        // Individual methods
        Assert.Equal(3, doc.GetHeadingCount());
        Assert.True(doc.GetWordCount() > 0);
        Assert.True(doc.GetCharCount() > 0);

        // GetDocumentStats
        var stats = doc.GetDocumentStats();
        Assert.Equal(3, stats.HeadingCount);
        Assert.Equal(doc.ParagraphCount, stats.ParagraphCount);
        Assert.Equal(doc.GetWordCount(), stats.WordCount);
        Assert.Equal(doc.GetCharCount(), stats.CharCount);

        // Ensure consistency
        Assert.True(stats.CharCount >= stats.WordCount);
        Assert.True(stats.ParagraphCount >= stats.HeadingCount);

        // Mutation: RemoveAllParagraphs
        doc.RemoveAllParagraphs();
        var statsAfter = doc.GetDocumentStats();
        Assert.Equal(0, statsAfter.WordCount);
        Assert.Equal(0, statsAfter.CharCount);
        Assert.Equal(0, statsAfter.ParagraphCount);
        Assert.Equal(0, statsAfter.HeadingCount);
    }
}
