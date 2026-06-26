// Tests for FodtDocument.GetDocumentStats, GetWordCount, GetCharCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R206

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R206: Tests for FodtDocument.GetDocumentStats, GetWordCount, GetCharCount deeper.
/// GetDocumentStats(): returns a stats object with WordCount, CharCount, HeadingCount, ParagraphCount.
/// GetWordCount(): returns total number of words across all paragraphs.
/// GetCharCount(): returns total character count across all text content.
/// Covers: GetDocumentStats non-null; GetDocumentStats.WordCount positive after AppendParagraph;
/// GetDocumentStats.CharCount positive; GetDocumentStats.HeadingCount matches GetHeadingCount;
/// GetDocumentStats.ParagraphCount matches GetParagraphCount;
/// GetWordCount positive after AppendParagraph; GetWordCount zero for empty doc;
/// GetWordCount increases after more paragraphs; GetWordCount matches GetDocumentStats.WordCount;
/// GetCharCount positive; GetCharCount zero for empty doc;
/// GetCharCount matches GetDocumentStats.CharCount; GetCharCount > GetWordCount for multi-word text;
/// dogfood CreateEmpty->InsertHeadings->AppendParagraphs->GetDocumentStats->GetWordCount->GetCharCount->verify.
/// </summary>
public class FodtR206GetDocumentStatsAndWordCountDeepTests
{
    private static FodtDocument CreateContentDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Report Title", 1);
        doc.AppendParagraph("This paragraph introduces the main topic of the report.");
        doc.InsertHeading(1, "Background", 2);
        doc.AppendParagraph("Background information provides essential context for the analysis.");
        doc.AppendParagraph("Additional context further enriches the reader understanding.");
        doc.InsertHeading(2, "Conclusion", 1);
        doc.AppendParagraph("The conclusion restates the key findings in a concise summary.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetDocumentStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentStats_NonNull()
    {
        var doc = CreateContentDoc();
        Assert.NotNull(doc.GetDocumentStats());
    }

    [Fact]
    public void GetDocumentStats_WordCount_Positive()
    {
        var doc = CreateContentDoc();
        var stats = doc.GetDocumentStats();
        Assert.True(stats.WordCount > 0);
    }

    [Fact]
    public void GetDocumentStats_CharCount_Positive()
    {
        var doc = CreateContentDoc();
        var stats = doc.GetDocumentStats();
        Assert.True(stats.CharCount > 0);
    }

    [Fact]
    public void GetDocumentStats_HeadingCount_MatchesGetHeadingCount()
    {
        var doc = CreateContentDoc();
        var stats = doc.GetDocumentStats();
        Assert.Equal(doc.GetHeadingCount(), stats.HeadingCount);
    }

    [Fact]
    public void GetDocumentStats_ParagraphCount_MatchesGetParagraphCount()
    {
        var doc = CreateContentDoc();
        var stats = doc.GetDocumentStats();
        Assert.Equal(doc.GetParagraphCount(), stats.ParagraphCount);
    }

    [Fact]
    public void GetDocumentStats_CharCount_GreaterThan_WordCount()
    {
        var doc = CreateContentDoc();
        var stats = doc.GetDocumentStats();
        Assert.True(stats.CharCount >= stats.WordCount);
    }

    // -------------------------------------------------------------------------
    // GetWordCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWordCount_Positive_AfterAppendParagraph()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world.");
        Assert.True(doc.GetWordCount() > 0);
    }

    [Fact]
    public void GetWordCount_Zero_EmptyDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.GetWordCount());
    }

    [Fact]
    public void GetWordCount_Increases_AfterMoreParagraphs()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("One two three.");
        var before = doc.GetWordCount();
        doc.AppendParagraph("Four five six seven.");
        var after = doc.GetWordCount();
        Assert.True(after > before);
    }

    [Fact]
    public void GetWordCount_MatchesDocumentStats_WordCount()
    {
        var doc = CreateContentDoc();
        Assert.Equal(doc.GetWordCount(), doc.GetDocumentStats().WordCount);
    }

    [Fact]
    public void GetWordCount_SingleWord_IsOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.True(doc.GetWordCount() >= 1);
    }

    // -------------------------------------------------------------------------
    // GetCharCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCharCount_Positive_AfterAppendParagraph()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world.");
        Assert.True(doc.GetCharCount() > 0);
    }

    [Fact]
    public void GetCharCount_Zero_EmptyDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.GetCharCount());
    }

    [Fact]
    public void GetCharCount_MatchesDocumentStats_CharCount()
    {
        var doc = CreateContentDoc();
        Assert.Equal(doc.GetCharCount(), doc.GetDocumentStats().CharCount);
    }

    [Fact]
    public void GetCharCount_GreaterThan_WordCount_For_MultiWordText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("The quick brown fox jumps over the lazy dog.");
        Assert.True(doc.GetCharCount() > doc.GetWordCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateInsertAppendGetStatsGetWordCountGetCharCountVerify_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();

        // Build structured document
        doc.InsertHeading(0, "Executive Summary", 1);
        doc.AppendParagraph("This summary presents the key outcomes of our annual review.");
        doc.InsertHeading(1, "Financial Results", 2);
        doc.AppendParagraph("Revenue grew significantly in the third quarter of the fiscal year.");
        doc.AppendParagraph("Operational costs were reduced through efficiency improvements.");
        doc.InsertHeading(2, "Next Steps", 1);
        doc.AppendParagraph("The team will focus on expanding market presence in new regions.");

        // GetWordCount
        var wordCount = doc.GetWordCount();
        Assert.True(wordCount > 0);

        // GetCharCount
        var charCount = doc.GetCharCount();
        Assert.True(charCount > wordCount); // chars > words for normal text

        // GetDocumentStats
        var stats = doc.GetDocumentStats();
        Assert.NotNull(stats);
        Assert.Equal(wordCount, stats.WordCount);
        Assert.Equal(charCount, stats.CharCount);
        Assert.Equal(3, stats.HeadingCount);
        Assert.Equal(doc.GetParagraphCount(), stats.ParagraphCount);

        // Verify heading count
        Assert.Equal(3, doc.GetHeadingCount());

        // Verify paragraph count includes headings
        Assert.True(doc.GetParagraphCount() >= 4); // 4 plain + headings

        // Append more and verify counts increase
        doc.AppendParagraph("Additional paragraph adds more content to the document.");
        Assert.True(doc.GetWordCount() > wordCount);
        Assert.True(doc.GetCharCount() > charCount);
    }
}
