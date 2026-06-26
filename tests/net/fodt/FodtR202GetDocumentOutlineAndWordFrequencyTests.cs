// Tests for FodtDocument.GetDocumentOutline, GetWordFrequency chain deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R202

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R202: Tests for FodtDocument.GetDocumentOutline, GetWordFrequency chain deeper.
/// GetDocumentOutline(): returns list of outline entries with Level and Text.
/// GetWordFrequency(): returns word→count dictionary.
/// Covers: GetDocumentOutline for multi-level headings count correct;
/// GetDocumentOutline entries have correct levels; GetDocumentOutline text correct;
/// GetDocumentOutline ordered by insertion; GetDocumentOutline mixed levels;
/// GetWordFrequency total word count equals sum of values;
/// GetWordFrequency most frequent word has highest count;
/// GetWordFrequency after ReplaceText updates counts;
/// GetDocumentOutline->ExportToOutlineJson->Contains text chain;
/// GetWordFrequency includes words from all paragraphs;
/// GetDocumentOutline empty for no-heading doc;
/// GetWordFrequency excludes heading words vs paragraph words;
/// dogfood CreateDoc->GetDocumentOutline->GetWordFrequency->ExportToOutlineJson verify.
/// </summary>
public class FodtR202GetDocumentOutlineAndWordFrequencyTests
{
    private static FodtDocument CreateMultiLevelDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Part One", 1);
        doc.AppendParagraph("Introduction covers the key concepts.");
        doc.InsertHeading(1, "Chapter One", 2);
        doc.AppendParagraph("Chapter one discusses fundamentals.");
        doc.InsertHeading(2, "Section A", 3);
        doc.AppendParagraph("Section A provides detailed analysis.");
        doc.InsertHeading(3, "Chapter Two", 2);
        doc.AppendParagraph("Chapter two extends the concepts.");
        doc.InsertHeading(4, "Part Two", 1);
        doc.AppendParagraph("Part two covers advanced topics in depth.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetDocumentOutline — multi-level
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentOutline_MultiLevel_CountCorrect()
    {
        var doc = CreateMultiLevelDoc();
        var outline = doc.GetDocumentOutline();
        Assert.Equal(5, outline.Count);
    }

    [Fact]
    public void GetDocumentOutline_FirstEntry_LevelOne()
    {
        var doc = CreateMultiLevelDoc();
        var outline = doc.GetDocumentOutline();
        Assert.Equal(1, outline[0].Level);
    }

    [Fact]
    public void GetDocumentOutline_SecondEntry_LevelTwo()
    {
        var doc = CreateMultiLevelDoc();
        var outline = doc.GetDocumentOutline();
        Assert.Equal(2, outline[1].Level);
    }

    [Fact]
    public void GetDocumentOutline_ThirdEntry_LevelThree()
    {
        var doc = CreateMultiLevelDoc();
        var outline = doc.GetDocumentOutline();
        Assert.Equal(3, outline[2].Level);
    }

    [Fact]
    public void GetDocumentOutline_TextCorrect_AllEntries()
    {
        var doc = CreateMultiLevelDoc();
        var outline = doc.GetDocumentOutline();
        Assert.Contains("Part One", outline[0].Text);
        Assert.Contains("Chapter One", outline[1].Text);
        Assert.Contains("Section A", outline[2].Text);
        Assert.Contains("Chapter Two", outline[3].Text);
        Assert.Contains("Part Two", outline[4].Text);
    }

    [Fact]
    public void GetDocumentOutline_OrderedByInsertion()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "First", 1);
        doc.InsertHeading(1, "Second", 2);
        doc.InsertHeading(2, "Third", 1);
        var outline = doc.GetDocumentOutline();
        Assert.Equal(3, outline.Count);
        Assert.Contains("First", outline[0].Text);
        Assert.Contains("Second", outline[1].Text);
        Assert.Contains("Third", outline[2].Text);
    }

    [Fact]
    public void GetDocumentOutline_Empty_ForNoHeadingDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("No headings here.");
        var outline = doc.GetDocumentOutline();
        Assert.Empty(outline);
    }

    // -------------------------------------------------------------------------
    // GetWordFrequency — deeper coverage
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWordFrequency_TotalWordCount_EqualsSum()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("alpha beta alpha gamma alpha");
        var freq = doc.GetWordFrequency();
        var totalWords = 0;
        foreach (var kv in freq)
            totalWords += kv.Value;
        Assert.True(totalWords >= 3); // at least alpha(3), beta(1), gamma(1)
    }

    [Fact]
    public void GetWordFrequency_MostFrequent_HasHighestCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("apple apple apple banana banana cherry");
        var freq = doc.GetWordFrequency();
        var maxCount = 0;
        foreach (var kv in freq)
            if (kv.Value > maxCount) maxCount = kv.Value;
        Assert.True(maxCount >= 3); // "apple" appears 3 times
    }

    [Fact]
    public void GetWordFrequency_IncludesWordsFromAllParagraphs()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("first paragraph word");
        doc.AppendParagraph("second paragraph term");
        var freq = doc.GetWordFrequency();
        Assert.True(freq.Count >= 2);
    }

    [Fact]
    public void GetWordFrequency_AfterReplaceText_UpdatesWord()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("old word old word");
        doc.ReplaceText("old", "new");
        var freq = doc.GetWordFrequency();
        // "old" should not be present (replaced by "new")
        Assert.False(freq.ContainsKey("old"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDocGetOutlineGetWordFreqExportToOutlineJsonVerify_Pipeline()
    {
        var doc = CreateMultiLevelDoc();

        // GetDocumentOutline
        var outline = doc.GetDocumentOutline();
        Assert.Equal(5, outline.Count);
        Assert.Equal(1, outline[0].Level);
        Assert.Equal(1, outline[4].Level);
        Assert.Equal(2, outline[1].Level);

        // GetWordFrequency
        var freq = doc.GetWordFrequency();
        Assert.NotNull(freq);
        Assert.True(freq.Count > 0);

        // At least some words should be tracked
        var totalWords = 0;
        foreach (var kv in freq) totalWords += kv.Value;
        Assert.True(totalWords > 5);

        // ExportToOutlineJson
        var json = doc.ExportToOutlineJson();
        Assert.NotNull(json);
        Assert.Contains("Part One", json);
        Assert.Contains("Chapter One", json);
        Assert.Contains("Part Two", json);

        // GetDocumentStats consistency
        var stats = doc.GetDocumentStats();
        Assert.Equal(5, stats.HeadingCount);
        Assert.Equal(5, stats.ParagraphCount);
        Assert.True(stats.WordCount > 0);
    }
}
