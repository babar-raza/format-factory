// Tests for FodtDocument.GetHeadingParagraphs, GetParagraphTexts, SaveToFile deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R223

using System;
using System.IO;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R223: Tests for FodtDocument.GetHeadingParagraphs, GetParagraphTexts, SaveToFile deeper.
/// GetHeadingParagraphs(): returns all paragraph objects that are headings.
/// GetParagraphTexts(): returns all paragraph text strings.
/// SaveToFile(path): saves the document to file.
/// Covers: GetHeadingParagraphs non-null; GetHeadingParagraphs count equals GetHeadingCount;
/// GetHeadingParagraphs texts match GetDocumentOutline; GetHeadingParagraphs levels correct;
/// GetHeadingParagraphs after InsertHeading increases count;
/// GetParagraphTexts non-null; GetParagraphTexts count equals GetParagraphCount;
/// GetParagraphTexts contains expected heading texts; GetParagraphTexts after AppendParagraph increases;
/// GetParagraphTexts after RemoveAllParagraphs decreases;
/// SaveToFile then LoadFile GetHeadingParagraphs match;
/// SaveToFile then LoadFile GetParagraphTexts match;
/// dogfood CreateDoc->GetHeadingParagraphs->GetParagraphTexts->SaveToFile->LoadFile->Verify pipeline.
/// </summary>
public class FodtR223GetHeadingParagraphsAndSaveDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR223GetHeadingParagraphsAndSaveDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR223_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Chapter One", 1);
        doc.AppendParagraph("The first chapter begins with context.");
        doc.InsertHeading(2, "Section 1.1", 2);
        doc.AppendParagraph("This section explores the first sub-topic.");
        doc.InsertHeading(4, "Chapter Two", 1);
        doc.AppendParagraph("The second chapter introduces new material.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetHeadingParagraphs
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeadingParagraphs_NonNull()
    {
        var doc = CreateStructuredDoc();
        Assert.NotNull(doc.GetHeadingParagraphs());
    }

    [Fact]
    public void GetHeadingParagraphs_CountEqualsGetHeadingCount()
    {
        var doc = CreateStructuredDoc();
        Assert.Equal(doc.GetHeadingCount(), doc.GetHeadingParagraphs().Count);
    }

    [Fact]
    public void GetHeadingParagraphs_TextsMatchOutline()
    {
        var doc = CreateStructuredDoc();
        var headings = doc.GetHeadingParagraphs();
        var outline = doc.GetDocumentOutline();
        for (var i = 0; i < headings.Count; i++)
            Assert.Equal(outline[i].Text, headings[i].Text);
    }

    [Fact]
    public void GetHeadingParagraphs_LevelsCorrect()
    {
        var doc = CreateStructuredDoc();
        var headings = doc.GetHeadingParagraphs();
        Assert.Equal(1, headings[0].Level);
        Assert.Equal(2, headings[1].Level);
        Assert.Equal(1, headings[2].Level);
    }

    [Fact]
    public void GetHeadingParagraphs_AfterInsertHeading_IncreasesCount()
    {
        var doc = CreateStructuredDoc();
        var before = doc.GetHeadingParagraphs().Count;
        doc.InsertHeading(doc.GetParagraphCount(), "Appendix", 1);
        Assert.Equal(before + 1, doc.GetHeadingParagraphs().Count);
    }

    [Fact]
    public void GetHeadingParagraphs_EmptyDoc_EmptyOrNull()
    {
        var doc = FodtDocument.CreateEmpty();
        var headings = doc.GetHeadingParagraphs();
        Assert.True(headings == null || headings.Count == 0);
    }

    [Fact]
    public void GetHeadingParagraphs_ContainsExpectedTexts()
    {
        var doc = CreateStructuredDoc();
        var texts = new List<string>();
        foreach (var h in doc.GetHeadingParagraphs())
            texts.Add(h.Text);
        Assert.Contains("Chapter One", texts);
        Assert.Contains("Chapter Two", texts);
        Assert.Contains("Section 1.1", texts);
    }

    // -------------------------------------------------------------------------
    // GetParagraphTexts
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphTexts_NonNull()
    {
        var doc = CreateStructuredDoc();
        Assert.NotNull(doc.GetParagraphTexts());
    }

    [Fact]
    public void GetParagraphTexts_CountEqualsParagraphCount()
    {
        var doc = CreateStructuredDoc();
        Assert.Equal(doc.GetParagraphCount(), doc.GetParagraphTexts().Count);
    }

    [Fact]
    public void GetParagraphTexts_ContainsHeadingTexts()
    {
        var doc = CreateStructuredDoc();
        var texts = doc.GetParagraphTexts();
        Assert.Contains("Chapter One", texts);
        Assert.Contains("Chapter Two", texts);
    }

    [Fact]
    public void GetParagraphTexts_ContainsBodyParaTexts()
    {
        var doc = CreateStructuredDoc();
        var texts = doc.GetParagraphTexts();
        Assert.True(texts.Exists(t => t.Contains("first chapter")));
    }

    [Fact]
    public void GetParagraphTexts_AfterAppendParagraph_IncreasesCount()
    {
        var doc = CreateStructuredDoc();
        var before = doc.GetParagraphTexts().Count;
        doc.AppendParagraph("New paragraph appended here.");
        var after = doc.GetParagraphTexts().Count;
        Assert.Equal(before + 1, after);
    }

    [Fact]
    public void GetParagraphTexts_AfterRemoveAllParagraphs_DecreasesCount()
    {
        var doc = CreateStructuredDoc();
        var before = doc.GetParagraphTexts().Count;
        doc.RemoveAllParagraphs();
        var after = doc.GetParagraphTexts().Count;
        Assert.True(after < before);
    }

    // -------------------------------------------------------------------------
    // SaveToFile round-trip
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_ThenLoadFile_GetHeadingParagraphsMatch()
    {
        var doc = CreateStructuredDoc();
        var path = TempFile("headings.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(doc.GetHeadingCount(), loaded.GetHeadingParagraphs().Count);
    }

    [Fact]
    public void SaveToFile_ThenLoadFile_GetParagraphTextsCountMatch()
    {
        var doc = CreateStructuredDoc();
        var path = TempFile("para_texts.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(doc.GetParagraphTexts().Count, loaded.GetParagraphTexts().Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_GetHeadingParagraphs_GetParagraphTexts_SaveToFile_LoadFile_Verify_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Introduction", 1);
        doc.AppendParagraph("Introduction text provides context for the reader.");
        doc.AppendParagraph("Second paragraph gives more context.");
        doc.InsertHeading(3, "Methods", 2);
        doc.AppendParagraph("Methods section describes the approach.");
        doc.InsertHeading(5, "Conclusion", 1);
        doc.AppendParagraph("Conclusion summarizes key findings.");

        // GetHeadingParagraphs
        var headings = doc.GetHeadingParagraphs();
        Assert.Equal(3, headings.Count);
        Assert.Equal("Introduction", headings[0].Text);
        Assert.Equal(1, headings[0].Level);
        Assert.Equal("Methods", headings[1].Text);
        Assert.Equal(2, headings[1].Level);
        Assert.Equal("Conclusion", headings[2].Text);

        // GetParagraphTexts
        var texts = doc.GetParagraphTexts();
        Assert.Equal(7, texts.Count);
        Assert.Contains("Introduction", texts);
        Assert.Contains("Conclusion", texts);
        Assert.True(texts.Exists(t => t.Contains("context for the reader")));

        // SaveToFile
        var path = TempFile("dogfood_structure.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile
        var loaded = FodtDocument.LoadFile(path);
        Assert.NotNull(loaded);

        // GetHeadingParagraphs after load
        var loadedHeadings = loaded.GetHeadingParagraphs();
        Assert.Equal(3, loadedHeadings.Count);
        Assert.Equal("Introduction", loadedHeadings[0].Text);

        // GetParagraphTexts after load
        var loadedTexts = loaded.GetParagraphTexts();
        Assert.Equal(7, loadedTexts.Count);

        // InsertHeading after load
        loaded.InsertHeading(loaded.GetParagraphCount(), "References", 1);
        Assert.Equal(4, loaded.GetHeadingParagraphs().Count);
        Assert.Equal(4, loaded.GetHeadingCount());
    }
}
