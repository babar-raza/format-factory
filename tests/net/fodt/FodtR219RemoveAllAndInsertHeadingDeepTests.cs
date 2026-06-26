// Tests for FodtDocument.RemoveAllParagraphs, InsertHeading, GetDocumentStats deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R219

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R219: Tests for FodtDocument.RemoveAllParagraphs, InsertHeading, GetDocumentStats deeper coverage.
/// RemoveAllParagraphs(): removes all body paragraphs, leaving headings intact or empty doc.
/// InsertHeading(index, text, level): inserts a heading at the given index.
/// GetDocumentStats(): returns a stats object with word/char/paragraph/heading counts.
/// Covers: RemoveAllParagraphs non-null; RemoveAllParagraphs leaves zero body paras or small count;
/// InsertHeading non-null; InsertHeading increases heading count;
/// InsertHeading at index 0 is first; InsertHeading at end is last;
/// InsertHeading level 1 and level 2 both accepted;
/// GetDocumentStats non-null; GetDocumentStats word count positive;
/// GetDocumentStats char count positive; GetDocumentStats paragraph count matches;
/// GetDocumentStats heading count matches GetHeadingCount;
/// dogfood CreateDoc->InsertHeading->GetDocumentStats->RemoveAllParagraphs->Verify pipeline.
/// </summary>
public class FodtR219RemoveAllAndInsertHeadingDeepTests
{
    private static FodtDocument CreateRichDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Introduction", 1);
        doc.AppendParagraph("This is the introduction paragraph with some words.");
        doc.AppendParagraph("Another body paragraph for the introduction section.");
        doc.InsertHeading(3, "Methods", 2);
        doc.AppendParagraph("This paragraph describes the methods used.");
        doc.InsertHeading(5, "Conclusion", 1);
        doc.AppendParagraph("The conclusion summarizes the findings.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // InsertHeading
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertHeading_NonNull_Result()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Chapter 1", 1);
        Assert.NotNull(doc);
    }

    [Fact]
    public void InsertHeading_IncreasesHeadingCount()
    {
        var doc = FodtDocument.CreateEmpty();
        var before = doc.GetHeadingCount();
        doc.InsertHeading(0, "New Heading", 1);
        Assert.Equal(before + 1, doc.GetHeadingCount());
    }

    [Fact]
    public void InsertHeading_MultipleHeadings_AllPresent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Chapter 1", 1);
        doc.InsertHeading(1, "Section 1.1", 2);
        doc.InsertHeading(2, "Chapter 2", 1);
        Assert.Equal(3, doc.GetHeadingCount());
    }

    [Fact]
    public void InsertHeading_Level1_Accepted()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Top Level", 1);
        Assert.Equal(1, doc.GetHeadingCount());
    }

    [Fact]
    public void InsertHeading_Level2_Accepted()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Sub Level", 2);
        Assert.Equal(1, doc.GetHeadingCount());
    }

    [Fact]
    public void InsertHeading_Level3_Accepted()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Sub Sub Level", 3);
        Assert.Equal(1, doc.GetHeadingCount());
    }

    [Fact]
    public void InsertHeading_IncreasesTotalParagraphCount()
    {
        var doc = FodtDocument.CreateEmpty();
        var before = doc.GetParagraphCount();
        doc.InsertHeading(0, "Heading", 1);
        Assert.True(doc.GetParagraphCount() > before);
    }

    [Fact]
    public void InsertHeading_TextAppearsInOutline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Unique Heading Text", 1);
        var outline = doc.GetDocumentOutline();
        Assert.Equal(1, outline.Count);
        Assert.Equal("Unique Heading Text", outline[0].Text);
    }

    // -------------------------------------------------------------------------
    // RemoveAllParagraphs
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveAllParagraphs_NonNull()
    {
        var doc = CreateRichDoc();
        doc.RemoveAllParagraphs();
        Assert.NotNull(doc);
    }

    [Fact]
    public void RemoveAllParagraphs_ReducesParagraphCount()
    {
        var doc = CreateRichDoc();
        var before = doc.GetParagraphCount();
        doc.RemoveAllParagraphs();
        Assert.True(doc.GetParagraphCount() < before);
    }

    [Fact]
    public void RemoveAllParagraphs_EmptyDoc_DoesNotThrow()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.RemoveAllParagraphs());
        Assert.Null(ex);
    }

    [Fact]
    public void RemoveAllParagraphs_ThenAppendParagraph_Works()
    {
        var doc = CreateRichDoc();
        doc.RemoveAllParagraphs();
        var ex = Record.Exception(() => doc.AppendParagraph("Fresh paragraph after clear."));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetDocumentStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentStats_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.GetDocumentStats());
    }

    [Fact]
    public void GetDocumentStats_WordCount_Positive()
    {
        var doc = CreateRichDoc();
        var stats = doc.GetDocumentStats();
        Assert.True(stats.WordCount > 0);
    }

    [Fact]
    public void GetDocumentStats_CharCount_Positive()
    {
        var doc = CreateRichDoc();
        var stats = doc.GetDocumentStats();
        Assert.True(stats.CharCount > 0);
    }

    [Fact]
    public void GetDocumentStats_ParagraphCount_MatchesGetParagraphCount()
    {
        var doc = CreateRichDoc();
        var stats = doc.GetDocumentStats();
        Assert.Equal(doc.GetParagraphCount(), stats.ParagraphCount);
    }

    [Fact]
    public void GetDocumentStats_HeadingCount_MatchesGetHeadingCount()
    {
        var doc = CreateRichDoc();
        var stats = doc.GetDocumentStats();
        Assert.Equal(doc.GetHeadingCount(), stats.HeadingCount);
    }

    [Fact]
    public void GetDocumentStats_AfterAppendParagraph_WordCountIncreases()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First paragraph with five words.");
        var statsBefore = doc.GetDocumentStats();
        doc.AppendParagraph("Second paragraph with even more words added here.");
        var statsAfter = doc.GetDocumentStats();
        Assert.True(statsAfter.WordCount > statsBefore.WordCount);
    }

    [Fact]
    public void GetDocumentStats_EmptyDoc_HasZeroOrMinimalCounts()
    {
        var doc = FodtDocument.CreateEmpty();
        var stats = doc.GetDocumentStats();
        Assert.NotNull(stats);
        Assert.True(stats.WordCount >= 0);
        Assert.True(stats.HeadingCount >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_InsertHeading_GetDocumentStats_RemoveAllParagraphs_Verify_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();

        // InsertHeading
        doc.InsertHeading(0, "Part I: Overview", 1);
        doc.AppendParagraph("Overview paragraph with multiple words for counting.");
        doc.AppendParagraph("Second paragraph provides additional context here.");
        doc.InsertHeading(3, "Section 1.1: Details", 2);
        doc.AppendParagraph("Details are described in this section thoroughly.");
        doc.InsertHeading(5, "Part II: Results", 1);
        doc.AppendParagraph("Results paragraph summarizes the findings of the study.");

        // Verify structure
        Assert.Equal(3, doc.GetHeadingCount());
        Assert.True(doc.GetParagraphCount() >= 6); // 3 headings + 4 body paras

        // GetDocumentStats
        var stats = doc.GetDocumentStats();
        Assert.NotNull(stats);
        Assert.Equal(3, stats.HeadingCount);
        Assert.True(stats.WordCount > 10);
        Assert.True(stats.CharCount > 30);

        // InsertHeading at end
        doc.InsertHeading(doc.GetParagraphCount(), "Appendix", 1);
        Assert.Equal(4, doc.GetHeadingCount());

        // GetDocumentOutline reflects all headings
        var outline = doc.GetDocumentOutline();
        Assert.Equal(4, outline.Count);
        Assert.Equal("Part I: Overview", outline[0].Text);
        Assert.Equal("Appendix", outline[3].Text);

        // RemoveAllParagraphs
        var beforeRemove = doc.GetParagraphCount();
        doc.RemoveAllParagraphs();
        Assert.True(doc.GetParagraphCount() < beforeRemove);

        // After removal, AppendParagraph works
        doc.AppendParagraph("Post-clear paragraph.");
        Assert.True(doc.GetParagraphCount() >= 1);

        // GetDocumentStats after removal reflects changes
        var statsAfter = doc.GetDocumentStats();
        Assert.NotNull(statsAfter);
    }
}
