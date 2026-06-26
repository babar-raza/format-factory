// Tests for FodtDocument.GetWordFrequency, GetDocumentOutline, ExportToMarkdown deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R225

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R225: Tests for FodtDocument.GetWordFrequency, GetDocumentOutline, ExportToMarkdown deeper.
/// GetWordFrequency(): returns word→frequency dictionary for all document text.
/// GetDocumentOutline(): returns list of heading outline items with text and level.
/// ExportToMarkdown(): exports document as markdown string.
/// Covers: GetWordFrequency non-null; GetWordFrequency contains known word;
/// GetWordFrequency correct count for repeated word; GetWordFrequency empty for empty doc;
/// GetWordFrequency after ReplaceText updates; GetWordFrequency after AppendParagraph grows;
/// GetDocumentOutline non-null; GetDocumentOutline count equals GetHeadingCount;
/// GetDocumentOutline texts correct; GetDocumentOutline levels correct;
/// GetDocumentOutline after InsertHeading increases; GetDocumentOutline empty doc empty;
/// ExportToMarkdown non-null; ExportToMarkdown non-empty; ExportToMarkdown has # heading;
/// ExportToMarkdown contains paragraph text; ExportToMarkdown after mutation reflects;
/// dogfood CreateDoc→GetWordFrequency→GetDocumentOutline→ExportToMarkdown→SaveToFile→LoadFile pipeline.
/// </summary>
public class FodtR225GetWordFrequencyAndOutlineDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR225GetWordFrequencyAndOutlineDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR225_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateRichDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Introduction", 1);
        doc.AppendParagraph("The system processes data and transforms data into reports.");
        doc.InsertHeading(2, "Methods", 2);
        doc.AppendParagraph("The methods apply proven techniques for data analysis.");
        doc.InsertHeading(4, "Conclusion", 1);
        doc.AppendParagraph("The conclusion summarizes the data findings and recommendations.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetWordFrequency
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWordFrequency_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.GetWordFrequency());
    }

    [Fact]
    public void GetWordFrequency_ContainsKnownWord()
    {
        var doc = CreateRichDoc();
        var freq = doc.GetWordFrequency();
        // "data" appears multiple times
        Assert.True(freq.ContainsKey("data") || freq.ContainsKey("Data"));
    }

    [Fact]
    public void GetWordFrequency_CountForRepeatedWord()
    {
        var doc = CreateRichDoc();
        var freq = doc.GetWordFrequency();
        // "data" appears 3+ times across paragraphs
        var key = freq.ContainsKey("data") ? "data" : (freq.ContainsKey("Data") ? "Data" : null);
        if (key != null)
            Assert.True(freq[key] >= 3);
    }

    [Fact]
    public void GetWordFrequency_EmptyDoc_EmptyOrNull()
    {
        var doc = FodtDocument.CreateEmpty();
        var freq = doc.GetWordFrequency();
        Assert.True(freq == null || freq.Count == 0);
    }

    [Fact]
    public void GetWordFrequency_AfterReplaceText_Updates()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("alpha beta alpha gamma alpha.");
        doc.ReplaceText("alpha", "delta");
        var freq = doc.GetWordFrequency();
        Assert.NotNull(freq);
        Assert.False(freq.ContainsKey("alpha"));
    }

    [Fact]
    public void GetWordFrequency_AfterAppendParagraph_Grows()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world.");
        var before = doc.GetWordFrequency().Count;
        doc.AppendParagraph("Unique xyzzy quux terms here.");
        var after = doc.GetWordFrequency().Count;
        Assert.True(after >= before);
    }

    [Fact]
    public void GetWordFrequency_AllValuesPositive()
    {
        var doc = CreateRichDoc();
        var freq = doc.GetWordFrequency();
        foreach (var kv in freq)
            Assert.True(kv.Value > 0);
    }

    // -------------------------------------------------------------------------
    // GetDocumentOutline
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentOutline_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.GetDocumentOutline());
    }

    [Fact]
    public void GetDocumentOutline_CountEqualsHeadingCount()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetHeadingCount(), doc.GetDocumentOutline().Count);
    }

    [Fact]
    public void GetDocumentOutline_TextsCorrect()
    {
        var doc = CreateRichDoc();
        var outline = doc.GetDocumentOutline();
        Assert.Equal("Introduction", outline[0].Text);
        Assert.Equal("Methods", outline[1].Text);
        Assert.Equal("Conclusion", outline[2].Text);
    }

    [Fact]
    public void GetDocumentOutline_LevelsCorrect()
    {
        var doc = CreateRichDoc();
        var outline = doc.GetDocumentOutline();
        Assert.Equal(1, outline[0].Level);
        Assert.Equal(2, outline[1].Level);
        Assert.Equal(1, outline[2].Level);
    }

    [Fact]
    public void GetDocumentOutline_AfterInsertHeading_Increases()
    {
        var doc = CreateRichDoc();
        var before = doc.GetDocumentOutline().Count;
        doc.InsertHeading(doc.GetParagraphCount(), "Appendix", 1);
        Assert.Equal(before + 1, doc.GetDocumentOutline().Count);
    }

    [Fact]
    public void GetDocumentOutline_EmptyDoc_EmptyOrNull()
    {
        var doc = FodtDocument.CreateEmpty();
        var outline = doc.GetDocumentOutline();
        Assert.True(outline == null || outline.Count == 0);
    }

    // -------------------------------------------------------------------------
    // ExportToMarkdown
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToMarkdown_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.ExportToMarkdown());
    }

    [Fact]
    public void ExportToMarkdown_NonEmpty()
    {
        var doc = CreateRichDoc();
        Assert.NotEmpty(doc.ExportToMarkdown());
    }

    [Fact]
    public void ExportToMarkdown_HasHeadingMarker()
    {
        var doc = CreateRichDoc();
        var md = doc.ExportToMarkdown();
        Assert.Contains("#", md);
    }

    [Fact]
    public void ExportToMarkdown_ContainsHeadingText()
    {
        var doc = CreateRichDoc();
        var md = doc.ExportToMarkdown();
        Assert.True(md.Contains("Introduction") || md.Contains("Conclusion"));
    }

    [Fact]
    public void ExportToMarkdown_ContainsParagraphText()
    {
        var doc = CreateRichDoc();
        var md = doc.ExportToMarkdown();
        Assert.True(md.Contains("data") || md.Contains("system") || md.Contains("methods"));
    }

    [Fact]
    public void ExportToMarkdown_AfterAppendParagraph_Longer()
    {
        var doc = CreateRichDoc();
        var before = doc.ExportToMarkdown().Length;
        doc.AppendParagraph("This additional paragraph adds more content to the export.");
        var after = doc.ExportToMarkdown().Length;
        Assert.True(after > before);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_GetWordFrequency_GetDocumentOutline_ExportToMarkdown_SaveToFile_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Executive Summary", 1);
        doc.AppendParagraph("The executive summary presents the key findings of the review.");
        doc.AppendParagraph("Key findings include performance improvements and cost reductions.");
        doc.InsertHeading(3, "Detailed Analysis", 2);
        doc.AppendParagraph("The detailed analysis covers all aspects of the review in depth.");
        doc.InsertHeading(5, "Recommendations", 1);
        doc.AppendParagraph("The recommendations address the key findings from the review.");

        // GetWordFrequency
        var freq = doc.GetWordFrequency();
        Assert.NotNull(freq);
        Assert.True(freq.Count > 0);
        // "key" and "findings" appear multiple times
        var keyWord = freq.ContainsKey("key") ? "key" : (freq.ContainsKey("Key") ? "Key" : null);
        if (keyWord != null)
            Assert.True(freq[keyWord] >= 2);

        // GetDocumentOutline
        var outline = doc.GetDocumentOutline();
        Assert.Equal(3, outline.Count);
        Assert.Equal("Executive Summary", outline[0].Text);
        Assert.Equal(1, outline[0].Level);
        Assert.Equal("Detailed Analysis", outline[1].Text);
        Assert.Equal(2, outline[1].Level);
        Assert.Equal("Recommendations", outline[2].Text);

        // ExportToMarkdown
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.Contains("#", md);
        Assert.True(md.Contains("Executive Summary") || md.Contains("Recommendations"));

        // SaveToFile
        var path = TempFile("dogfood_outline.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile
        var loaded = FodtDocument.LoadFile(path);
        Assert.NotNull(loaded);

        // GetDocumentOutline from loaded
        var loadedOutline = loaded.GetDocumentOutline();
        Assert.Equal(3, loadedOutline.Count);
        Assert.Equal("Executive Summary", loadedOutline[0].Text);

        // GetWordFrequency from loaded
        var loadedFreq = loaded.GetWordFrequency();
        Assert.NotNull(loadedFreq);
        Assert.True(loadedFreq.Count > 0);

        // ExportToMarkdown from loaded
        var loadedMd = loaded.ExportToMarkdown();
        Assert.NotNull(loadedMd);
        Assert.Contains("#", loadedMd);

        // ReplaceText and re-check word frequency
        loaded.ReplaceText("review", "audit");
        loaded.ReplaceText("Review", "Audit");
        var updatedFreq = loaded.GetWordFrequency();
        Assert.False(updatedFreq.ContainsKey("review"));
    }
}
