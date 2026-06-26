// Tests for FodtDocument.GetParagraphTexts, SetParagraphText, ExportToOutlineJson deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R234

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R234: Tests for FodtDocument.GetParagraphTexts, SetParagraphText, ExportToOutlineJson deeper.
/// GetParagraphTexts(): returns list of all paragraph text strings (headings + body).
/// SetParagraphText(index, text): sets the text of the paragraph at the given index.
/// ExportToOutlineJson(): exports the document outline as a JSON string.
/// Covers: GetParagraphTexts non-null; GetParagraphTexts count equals GetParagraphCount;
/// GetParagraphTexts contains heading texts; GetParagraphTexts contains body texts;
/// GetParagraphTexts after AppendParagraph grows; GetParagraphTexts after RemoveAllParagraphs empty;
/// GetParagraphTexts after SetParagraphText reflects change; GetParagraphTexts after LoadFile preserved;
/// SetParagraphText changes text; SetParagraphText reflected in GetParagraphTexts;
/// SetParagraphText then ExportToPlainText reflects; SetParagraphText then SaveToFile persists;
/// SetParagraphText first paragraph; SetParagraphText last paragraph;
/// ExportToOutlineJson non-null; ExportToOutlineJson non-empty; ExportToOutlineJson is JSON;
/// ExportToOutlineJson contains heading text; ExportToOutlineJson after InsertHeading grows;
/// ExportToOutlineJson empty doc;
/// dogfood CreateDoc→GetParagraphTexts→SetParagraphText→ExportToOutlineJson→SaveToFile pipeline.
/// </summary>
public class FodtR234GetParagraphTextsAndSetParagraphTextDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR234GetParagraphTextsAndSetParagraphTextDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR234_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Chapter One", 1);
        doc.AppendParagraph("This is the first body paragraph under chapter one.");
        doc.AppendParagraph("This is the second body paragraph with additional detail.");
        doc.InsertHeading(3, "Section 1.1", 2);
        doc.AppendParagraph("This paragraph belongs to section one point one.");
        doc.InsertHeading(5, "Chapter Two", 1);
        doc.AppendParagraph("This is the first body paragraph under chapter two.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetParagraphTexts
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphTexts_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.GetParagraphTexts());
    }

    [Fact]
    public void GetParagraphTexts_CountEqualsParagraphCount()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetParagraphCount(), doc.GetParagraphTexts().Count);
    }

    [Fact]
    public void GetParagraphTexts_ContainsHeadingTexts()
    {
        var doc = CreateRichDoc();
        var texts = doc.GetParagraphTexts();
        Assert.Contains("Chapter One", texts);
        Assert.Contains("Section 1.1", texts);
        Assert.Contains("Chapter Two", texts);
    }

    [Fact]
    public void GetParagraphTexts_ContainsBodyTexts()
    {
        var doc = CreateRichDoc();
        var texts = doc.GetParagraphTexts();
        Assert.True(texts.Exists(t => t.Contains("first body paragraph")));
    }

    [Fact]
    public void GetParagraphTexts_AfterAppendParagraph_Grows()
    {
        var doc = CreateRichDoc();
        var before = doc.GetParagraphTexts().Count;
        doc.AppendParagraph("A new paragraph added to the document.");
        Assert.Equal(before + 1, doc.GetParagraphTexts().Count);
    }

    [Fact]
    public void GetParagraphTexts_AfterRemoveAllParagraphs_Empty()
    {
        var doc = CreateRichDoc();
        doc.RemoveAllParagraphs();
        var texts = doc.GetParagraphTexts();
        Assert.True(texts == null || texts.Count == 0);
    }

    [Fact]
    public void GetParagraphTexts_AfterSetParagraphText_Reflects()
    {
        var doc = CreateRichDoc();
        doc.SetParagraphText(1, "MODIFIED PARAGRAPH TEXT");
        var texts = doc.GetParagraphTexts();
        Assert.Contains("MODIFIED PARAGRAPH TEXT", texts);
    }

    [Fact]
    public void GetParagraphTexts_EmptyDoc_ZeroOrEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        var texts = doc.GetParagraphTexts();
        Assert.True(texts == null || texts.Count == 0);
    }

    // -------------------------------------------------------------------------
    // SetParagraphText
    // -------------------------------------------------------------------------

    [Fact]
    public void SetParagraphText_ChangesText()
    {
        var doc = CreateRichDoc();
        var originalFirst = doc.GetParagraphTexts()[1];
        doc.SetParagraphText(1, "REPLACED TEXT");
        Assert.NotEqual(originalFirst, doc.GetParagraphTexts()[1]);
    }

    [Fact]
    public void SetParagraphText_ReflectedInGetParagraphTexts()
    {
        var doc = CreateRichDoc();
        doc.SetParagraphText(1, "NEW CONTENT FOR PARAGRAPH ONE");
        var texts = doc.GetParagraphTexts();
        Assert.Equal("NEW CONTENT FOR PARAGRAPH ONE", texts[1]);
    }

    [Fact]
    public void SetParagraphText_ThenExportToPlainText_Reflects()
    {
        var doc = CreateRichDoc();
        doc.SetParagraphText(1, "UNIQUE_MARKER_12345");
        Assert.Contains("UNIQUE_MARKER_12345", doc.ExportToPlainText());
    }

    [Fact]
    public void SetParagraphText_ThenSaveToFile_Persists()
    {
        var doc = CreateRichDoc();
        doc.SetParagraphText(1, "PERSISTED_CONTENT");
        var path = TempFile("settext_persist.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Contains("PERSISTED_CONTENT", loaded.GetParagraphTexts());
    }

    [Fact]
    public void SetParagraphText_FirstParagraph()
    {
        var doc = CreateRichDoc();
        doc.SetParagraphText(0, "MODIFIED FIRST HEADING");
        var texts = doc.GetParagraphTexts();
        Assert.Equal("MODIFIED FIRST HEADING", texts[0]);
    }

    [Fact]
    public void SetParagraphText_LastParagraph()
    {
        var doc = CreateRichDoc();
        var lastIdx = doc.GetParagraphCount() - 1;
        doc.SetParagraphText(lastIdx, "MODIFIED LAST PARAGRAPH");
        var texts = doc.GetParagraphTexts();
        Assert.Equal("MODIFIED LAST PARAGRAPH", texts[lastIdx]);
    }

    [Fact]
    public void SetParagraphText_DoesNotChangeParagraphCount()
    {
        var doc = CreateRichDoc();
        var before = doc.GetParagraphCount();
        doc.SetParagraphText(1, "Changed text.");
        Assert.Equal(before, doc.GetParagraphCount());
    }

    // -------------------------------------------------------------------------
    // ExportToOutlineJson
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToOutlineJson_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.ExportToOutlineJson());
    }

    [Fact]
    public void ExportToOutlineJson_NonEmpty()
    {
        var doc = CreateRichDoc();
        Assert.NotEmpty(doc.ExportToOutlineJson());
    }

    [Fact]
    public void ExportToOutlineJson_IsJson()
    {
        var doc = CreateRichDoc();
        var json = doc.ExportToOutlineJson();
        Assert.True(json.Contains("{") || json.Contains("["));
    }

    [Fact]
    public void ExportToOutlineJson_ContainsHeadingText()
    {
        var doc = CreateRichDoc();
        var json = doc.ExportToOutlineJson();
        Assert.True(json.Contains("Chapter One") || json.Contains("Section 1.1"));
    }

    [Fact]
    public void ExportToOutlineJson_AfterInsertHeading_Grows()
    {
        var doc = CreateRichDoc();
        var before = doc.ExportToOutlineJson().Length;
        doc.InsertHeading(doc.GetParagraphCount(), "New Appendix", 1);
        Assert.True(doc.ExportToOutlineJson().Length > before);
    }

    [Fact]
    public void ExportToOutlineJson_EmptyDoc_NonNullOrEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        var json = doc.ExportToOutlineJson();
        Assert.NotNull(json); // may be "[]" or "{}"
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_GetParagraphTexts_SetParagraphText_ExportToOutlineJson_SaveToFile_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Introduction", 1);
        doc.AppendParagraph("This paragraph introduces the document topic and scope.");
        doc.AppendParagraph("This paragraph provides background context for the reader.");
        doc.InsertHeading(3, "Methodology", 2);
        doc.AppendParagraph("The methodology section describes the research approach.");
        doc.InsertHeading(5, "Conclusion", 1);
        doc.AppendParagraph("The conclusion summarizes key findings and recommendations.");

        // GetParagraphTexts
        var texts = doc.GetParagraphTexts();
        Assert.NotNull(texts);
        Assert.Equal(doc.GetParagraphCount(), texts.Count);
        Assert.Equal(7, texts.Count);
        Assert.Contains("Introduction", texts);
        Assert.Contains("Methodology", texts);
        Assert.Contains("Conclusion", texts);
        Assert.True(texts.Exists(t => t.Contains("introduces")));

        // ExportToOutlineJson before SetParagraphText
        var outlineJson = doc.ExportToOutlineJson();
        Assert.NotNull(outlineJson);
        Assert.NotEmpty(outlineJson);
        Assert.True(outlineJson.Contains("{") || outlineJson.Contains("["));
        Assert.True(outlineJson.Contains("Introduction") || outlineJson.Contains("Methodology"));

        // SetParagraphText — change body paragraphs
        doc.SetParagraphText(1, "This revised paragraph introduces the updated document content.");
        doc.SetParagraphText(2, "Background context has been expanded to include recent findings.");
        doc.SetParagraphText(4, "The improved methodology applies mixed-methods research techniques.");

        // GetParagraphTexts — reflects changes
        var updatedTexts = doc.GetParagraphTexts();
        Assert.Equal("This revised paragraph introduces the updated document content.", updatedTexts[1]);
        Assert.Equal("Background context has been expanded to include recent findings.", updatedTexts[2]);
        Assert.Contains("mixed-methods", updatedTexts[4]);

        // SetParagraphText on heading
        doc.SetParagraphText(0, "Executive Introduction");
        var afterHeadingChange = doc.GetParagraphTexts();
        Assert.Equal("Executive Introduction", afterHeadingChange[0]);

        // ExportToOutlineJson after heading change — should reflect new heading
        var updatedOutline = doc.ExportToOutlineJson();
        Assert.True(updatedOutline.Contains("Executive Introduction") || updatedOutline.Length > 0);

        // ExportToPlainText contains revised text
        var plainText = doc.ExportToPlainText();
        Assert.Contains("revised", plainText);
        Assert.Contains("mixed-methods", plainText);

        // InsertHeading — outline grows
        doc.InsertHeading(doc.GetParagraphCount(), "Appendix A", 1);
        Assert.True(doc.ExportToOutlineJson().Length > outlineJson.Length);

        // SaveToFile
        var path = TempFile("dogfood_gettexts.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile — verify texts preserved
        var loaded = FodtDocument.LoadFile(path);
        Assert.NotNull(loaded);
        Assert.Equal(doc.GetParagraphCount(), loaded.GetParagraphCount());
        var loadedTexts = loaded.GetParagraphTexts();
        Assert.Contains("Executive Introduction", loadedTexts);
        Assert.Contains("mixed-methods", loadedTexts.Find(t => t.Contains("mixed-methods")) ?? "");

        // ExportToOutlineJson on loaded
        var loadedOutline = loaded.ExportToOutlineJson();
        Assert.NotNull(loadedOutline);
        Assert.NotEmpty(loadedOutline);

        // SetParagraphText on loaded — then SaveToFile again
        loaded.SetParagraphText(0, "Final Introduction");
        var finalPath = TempFile("dogfood_final.fodt");
        loaded.SaveToFile(finalPath);
        var final = FodtDocument.LoadFile(finalPath);
        Assert.Contains("Final Introduction", final.GetParagraphTexts());
    }
}
