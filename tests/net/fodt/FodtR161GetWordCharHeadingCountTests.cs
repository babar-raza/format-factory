// Tests for FodtDocument.GetWordCount, GetCharCount, GetHeadingCount, GetParagraphCount.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R161

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R161: Tests for FodtDocument scalar count methods:
/// GetWordCount, GetCharCount, GetHeadingCount, GetParagraphCount.
/// GetWordCount: whitespace-split tokens across all paragraphs; skips whitespace-only paragraphs.
/// GetCharCount: total Length of all paragraph Text strings (including spaces).
/// GetHeadingCount: count of text:h elements (paragraphs with IsHeading=true).
/// GetParagraphCount: total paragraph count (heading + body).
/// Covers: all four return 0 on empty doc; GetWordCount single word = 1;
/// GetWordCount multiple paragraphs accumulate; GetCharCount single char = 1;
/// GetCharCount includes spaces; GetHeadingCount counts only headings;
/// GetParagraphCount equals ParagraphCount property;
/// GetWordCount consistent with GetDocumentStats;
/// dogfood CreateEmpty->InsertHeading->AppendParagraph->all-four-counts.
/// </summary>
public class FodtR161GetWordCharHeadingCountTests
{
    // -------------------------------------------------------------------------
    // Empty doc baseline
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWordCount_EmptyDoc_IsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.GetWordCount());
    }

    [Fact]
    public void GetCharCount_EmptyDoc_IsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.GetCharCount());
    }

    [Fact]
    public void GetHeadingCount_EmptyDoc_IsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.GetHeadingCount());
    }

    [Fact]
    public void GetParagraphCount_EmptyDoc_IsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.GetParagraphCount());
    }

    // -------------------------------------------------------------------------
    // GetWordCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWordCount_SingleWord_IsOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.Equal(1, doc.GetWordCount());
    }

    [Fact]
    public void GetWordCount_MultipleWordsInOneParagraph_CorrectCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("one two three four five");
        Assert.Equal(5, doc.GetWordCount());
    }

    [Fact]
    public void GetWordCount_MultipleParagraphs_Accumulates()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("alpha beta");     // 2
        doc.AppendParagraph("gamma delta epsilon"); // 3
        Assert.Equal(5, doc.GetWordCount());
    }

    [Fact]
    public void GetWordCount_EmptyParagraph_DoesNotCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("");
        Assert.Equal(0, doc.GetWordCount());
    }

    // -------------------------------------------------------------------------
    // GetCharCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCharCount_SingleCharWord_IsOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("X");
        Assert.Equal(1, doc.GetCharCount());
    }

    [Fact]
    public void GetCharCount_IncludesSpaces()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hi there"); // 8 chars including space
        Assert.Equal(8, doc.GetCharCount());
    }

    // -------------------------------------------------------------------------
    // GetHeadingCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeadingCount_BodyParagraphOnly_IsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Body text.");
        Assert.Equal(0, doc.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_OneHeading_IsOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Chapter 1", 1);
        Assert.Equal(1, doc.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_MixedParagraphs_CountsOnlyHeadings()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "H1", 1);
        doc.AppendParagraph("Body.");
        doc.InsertHeading(2, "H2", 2);
        Assert.Equal(2, doc.GetHeadingCount());
    }

    // -------------------------------------------------------------------------
    // GetParagraphCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphCount_MatchesParagraphCountProperty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("One.");
        doc.InsertHeading(1, "Two", 1);
        Assert.Equal(doc.ParagraphCount, doc.GetParagraphCount());
    }

    // -------------------------------------------------------------------------
    // Consistency: GetWordCount vs GetDocumentStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWordCount_ConsistentWithGetDocumentStats()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Introduction", 1);
        doc.AppendParagraph("The quick brown fox.");
        var stats = doc.GetDocumentStats();
        Assert.Equal(stats.WordCount, doc.GetWordCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood: all four counts together
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AllFourCountMethods_Consistent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Title", 1);       // 1 word, 5 chars, 1 heading
        doc.AppendParagraph("Hello world.");     // 2 words, 12 chars, 0 headings
        doc.InsertHeading(2, "Appendix", 2);    // 1 word, 8 chars, 1 heading
        doc.AppendParagraph("Done.");            // 1 word, 5 chars, 0 headings

        Assert.Equal(4, doc.GetParagraphCount());
        Assert.Equal(2, doc.GetHeadingCount());
        Assert.Equal(5, doc.GetWordCount()); // Title+Hello+world+Appendix+Done
        Assert.True(doc.GetCharCount() > 0);
    }
}
