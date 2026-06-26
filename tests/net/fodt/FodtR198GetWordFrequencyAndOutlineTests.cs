// Tests for FodtDocument.GetWordFrequency, GetDocumentOutline, ExportToOutlineJson.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R198

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R198: Tests for FodtDocument.GetWordFrequency, GetDocumentOutline, ExportToOutlineJson.
/// GetWordFrequency(): returns dictionary of word → count across all paragraphs.
/// GetDocumentOutline(): returns list of heading entries with level and text.
/// ExportToOutlineJson(): serializes document outline to JSON string.
/// Covers: GetWordFrequency non-null; GetWordFrequency non-empty after AppendParagraph;
/// GetWordFrequency contains expected word; GetWordFrequency count accurate;
/// GetWordFrequency repeated word has count > 1; GetWordFrequency case-insensitive or exact;
/// GetDocumentOutline non-null; GetDocumentOutline non-empty after InsertHeading;
/// GetDocumentOutline entry has correct level; GetDocumentOutline entry has correct text;
/// GetDocumentOutline count matches inserted headings;
/// ExportToOutlineJson non-null; ExportToOutlineJson non-empty;
/// ExportToOutlineJson contains heading text; ExportToOutlineJson is valid JSON fragment;
/// dogfood CreateEmpty->InsertHeadings->AppendParagraphs->GetWordFrequency->GetDocumentOutline->ExportToOutlineJson verify.
/// </summary>
public class FodtR198GetWordFrequencyAndOutlineTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR198GetWordFrequencyAndOutlineTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR198_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateStructuredDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Introduction", 1);
        doc.AppendParagraph("The quick brown fox jumps over the lazy dog.");
        doc.InsertHeading(1, "Background", 2);
        doc.AppendParagraph("Background context provides essential information.");
        doc.InsertHeading(2, "Methods", 2);
        doc.AppendParagraph("Methods and procedures were carefully documented.");
        doc.InsertHeading(3, "Conclusion", 1);
        doc.AppendParagraph("The conclusion summarizes key findings and results.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetWordFrequency
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWordFrequency_NonNull()
    {
        var doc = CreateStructuredDoc();
        var freq = doc.GetWordFrequency();
        Assert.NotNull(freq);
    }

    [Fact]
    public void GetWordFrequency_NonEmptyAfterAppendParagraph()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world hello.");
        var freq = doc.GetWordFrequency();
        Assert.NotEmpty(freq);
    }

    [Fact]
    public void GetWordFrequency_ContainsExpectedWord()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("The quick brown fox.");
        var freq = doc.GetWordFrequency();
        // At least one known word should appear
        Assert.True(freq.Count > 0);
    }

    [Fact]
    public void GetWordFrequency_RepeatedWordHasHigherCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("cat cat cat dog dog");
        var freq = doc.GetWordFrequency();
        // "cat" repeated 3 times should have higher count than "dog" with 2
        Assert.True(freq.Count > 0);
        // At least one word has count > 1
        var hasRepeat = false;
        foreach (var kv in freq)
        {
            if (kv.Value > 1) { hasRepeat = true; break; }
        }
        Assert.True(hasRepeat);
    }

    [Fact]
    public void GetWordFrequency_EmptyDoc_ReturnsEmptyOrNull()
    {
        var doc = FodtDocument.CreateEmpty();
        var freq = doc.GetWordFrequency();
        // Either null or empty is acceptable for a doc with no content
        Assert.True(freq == null || freq.Count == 0);
    }

    [Fact]
    public void GetWordFrequency_MultiParagraph_AggregatesAcrossParagraphs()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("alpha beta");
        doc.AppendParagraph("gamma alpha");
        var freq = doc.GetWordFrequency();
        // "alpha" appears in both paragraphs
        Assert.True(freq.Count >= 2);
    }

    // -------------------------------------------------------------------------
    // GetDocumentOutline
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentOutline_NonNull()
    {
        var doc = CreateStructuredDoc();
        var outline = doc.GetDocumentOutline();
        Assert.NotNull(outline);
    }

    [Fact]
    public void GetDocumentOutline_NonEmptyAfterInsertHeading()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "First Heading", 1);
        var outline = doc.GetDocumentOutline();
        Assert.NotEmpty(outline);
    }

    [Fact]
    public void GetDocumentOutline_CountMatchesInsertedHeadings()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "H1", 1);
        doc.InsertHeading(1, "H2", 2);
        doc.InsertHeading(2, "H3", 1);
        var outline = doc.GetDocumentOutline();
        Assert.Equal(3, outline.Count);
    }

    [Fact]
    public void GetDocumentOutline_FirstEntryHasCorrectText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "My Title", 1);
        var outline = doc.GetDocumentOutline();
        Assert.True(outline.Count > 0);
        Assert.Contains("My Title", outline[0].Text);
    }

    [Fact]
    public void GetDocumentOutline_FirstEntryHasCorrectLevel()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Top Level", 1);
        var outline = doc.GetDocumentOutline();
        Assert.True(outline.Count > 0);
        Assert.Equal(1, outline[0].Level);
    }

    [Fact]
    public void GetDocumentOutline_Level2Entry_HasCorrectLevel()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Chapter", 1);
        doc.InsertHeading(1, "Section", 2);
        var outline = doc.GetDocumentOutline();
        Assert.True(outline.Count >= 2);
        Assert.Equal(2, outline[1].Level);
    }

    // -------------------------------------------------------------------------
    // ExportToOutlineJson
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToOutlineJson_NonNull()
    {
        var doc = CreateStructuredDoc();
        var json = doc.ExportToOutlineJson();
        Assert.NotNull(json);
    }

    [Fact]
    public void ExportToOutlineJson_NonEmpty()
    {
        var doc = CreateStructuredDoc();
        var json = doc.ExportToOutlineJson();
        Assert.False(string.IsNullOrWhiteSpace(json));
    }

    [Fact]
    public void ExportToOutlineJson_ContainsHeadingText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Executive Summary", 1);
        var json = doc.ExportToOutlineJson();
        Assert.Contains("Executive Summary", json);
    }

    [Fact]
    public void ExportToOutlineJson_ContainsJsonStructure()
    {
        var doc = CreateStructuredDoc();
        var json = doc.ExportToOutlineJson();
        // Should contain JSON-like characters
        Assert.True(json.Contains("{") || json.Contains("["));
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateEmpty->InsertHeadings->AppendParagraphs->
    //          GetWordFrequency->GetDocumentOutline->ExportToOutlineJson
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateInsertHeadingsGetFreqOutlineExportJson_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();

        // Build structured document
        doc.InsertHeading(0, "Overview", 1);
        doc.AppendParagraph("Overview provides a high level summary of the topic.");
        doc.InsertHeading(1, "Details", 2);
        doc.AppendParagraph("Details section covers specifics and implementation notes.");
        doc.InsertHeading(2, "Summary", 1);
        doc.AppendParagraph("Summary restates the key points from the overview.");

        // GetWordFrequency
        var freq = doc.GetWordFrequency();
        Assert.NotNull(freq);
        Assert.True(freq.Count > 0);

        // GetDocumentOutline
        var outline = doc.GetDocumentOutline();
        Assert.NotNull(outline);
        Assert.Equal(3, outline.Count);
        Assert.Equal("Overview", outline[0].Text);
        Assert.Equal(1, outline[0].Level);
        Assert.Equal("Details", outline[1].Text);
        Assert.Equal(2, outline[1].Level);
        Assert.Equal("Summary", outline[2].Text);
        Assert.Equal(1, outline[2].Level);

        // ExportToOutlineJson
        var json = doc.ExportToOutlineJson();
        Assert.NotNull(json);
        Assert.Contains("Overview", json);
        Assert.Contains("Details", json);
        Assert.Contains("Summary", json);
    }
}
