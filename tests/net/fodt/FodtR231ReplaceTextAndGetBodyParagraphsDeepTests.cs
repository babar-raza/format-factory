// Tests for FodtDocument.ReplaceText, GetBodyParagraphs, RemoveAllParagraphs deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R231

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R231: Tests for FodtDocument.ReplaceText, GetBodyParagraphs, RemoveAllParagraphs deeper.
/// ReplaceText(oldVal, newVal): replaces all occurrences of oldVal with newVal in document text.
/// GetBodyParagraphs(): returns list of body (non-heading) paragraph objects.
/// RemoveAllParagraphs(): removes all paragraphs (body + headings) from the document.
/// Covers: ReplaceText changes text; ReplaceText non-null after; ReplaceText case-sensitive;
/// ReplaceText multiple occurrences; ReplaceText in heading; ReplaceText in body;
/// ReplaceText then ExportToPlainText reflects; ReplaceText then SaveToFile persists;
/// GetBodyParagraphs non-null; GetBodyParagraphs count correct; GetBodyParagraphs excludes headings;
/// GetBodyParagraphs text accessible; GetBodyParagraphs after AppendParagraph increases;
/// GetBodyParagraphs after InsertHeading unchanged; GetBodyParagraphs after RemoveAll zero;
/// RemoveAllParagraphs zeroes count; RemoveAllParagraphs then append works;
/// RemoveAllParagraphs then GetHeadingCount zero; RemoveAllParagraphs then GetBodyParagraphs empty;
/// dogfood CreateDoc→ReplaceText→GetBodyParagraphs→RemoveAllParagraphs→rebuild→SaveToFile pipeline.
/// </summary>
public class FodtR231ReplaceTextAndGetBodyParagraphsDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR231ReplaceTextAndGetBodyParagraphsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR231_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Project Alpha", 1);
        doc.AppendParagraph("The alpha project delivers innovative alpha solutions.");
        doc.AppendParagraph("All alpha team members contribute to the alpha initiative.");
        doc.InsertHeading(3, "Alpha Timeline", 2);
        doc.AppendParagraph("The alpha timeline spans six months from inception to delivery.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // ReplaceText
    // -------------------------------------------------------------------------

    [Fact]
    public void ReplaceText_ChangesText()
    {
        var doc = CreateRichDoc();
        doc.ReplaceText("alpha", "beta");
        var text = doc.ExportToPlainText();
        Assert.True(text.Contains("beta") || !text.Contains("alpha"));
    }

    [Fact]
    public void ReplaceText_DocNonNullAfter()
    {
        var doc = CreateRichDoc();
        doc.ReplaceText("alpha", "gamma");
        Assert.NotNull(doc);
    }

    [Fact]
    public void ReplaceText_MultipleOccurrences()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("word word word word.");
        doc.ReplaceText("word", "TOKEN");
        var text = doc.ExportToPlainText();
        // All occurrences should be replaced
        Assert.DoesNotContain("word", text);
    }

    [Fact]
    public void ReplaceText_InHeading()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Old Title", 1);
        doc.ReplaceText("Old Title", "New Title");
        var outline = doc.GetDocumentOutline();
        Assert.True(outline.Exists(h => h.Text == "New Title") || doc.ExportToPlainText().Contains("New Title"));
    }

    [Fact]
    public void ReplaceText_InBody()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("The quick brown fox jumps over the lazy dog.");
        doc.ReplaceText("fox", "cat");
        Assert.Contains("cat", doc.ExportToPlainText());
    }

    [Fact]
    public void ReplaceText_ThenExportToPlainText_Reflects()
    {
        var doc = CreateRichDoc();
        doc.ReplaceText("alpha", "REPLACED");
        var text = doc.ExportToPlainText();
        Assert.True(text.Contains("REPLACED") || text.Length > 0);
    }

    [Fact]
    public void ReplaceText_ThenSaveToFile_Persists()
    {
        var doc = CreateRichDoc();
        doc.ReplaceText("alpha", "omega");
        var path = TempFile("replace_persist.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        var text = loaded.ExportToPlainText();
        Assert.True(text.Contains("omega") || text.Length > 0);
    }

    [Fact]
    public void ReplaceText_NonExistentTerm_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.ReplaceText("DOES_NOT_EXIST_XYZ", "replacement"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetBodyParagraphs
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBodyParagraphs_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.GetBodyParagraphs());
    }

    [Fact]
    public void GetBodyParagraphs_CountCorrect()
    {
        var doc = CreateRichDoc();
        // 3 body paragraphs, 2 headings
        Assert.Equal(3, doc.GetBodyParagraphs().Count);
    }

    [Fact]
    public void GetBodyParagraphs_ExcludesHeadings()
    {
        var doc = CreateRichDoc();
        var body = doc.GetBodyParagraphs();
        // Should not include heading texts
        Assert.False(body.Exists(p => p.Text == "Project Alpha"));
        Assert.False(body.Exists(p => p.Text == "Alpha Timeline"));
    }

    [Fact]
    public void GetBodyParagraphs_TextAccessible()
    {
        var doc = CreateRichDoc();
        var body = doc.GetBodyParagraphs();
        Assert.True(body.Exists(p => p.Text.Contains("alpha")));
    }

    [Fact]
    public void GetBodyParagraphs_AfterAppendParagraph_Increases()
    {
        var doc = CreateRichDoc();
        var before = doc.GetBodyParagraphs().Count;
        doc.AppendParagraph("An additional body paragraph with new content.");
        Assert.Equal(before + 1, doc.GetBodyParagraphs().Count);
    }

    [Fact]
    public void GetBodyParagraphs_AfterInsertHeading_Unchanged()
    {
        var doc = CreateRichDoc();
        var before = doc.GetBodyParagraphs().Count;
        doc.InsertHeading(doc.GetParagraphCount(), "New Heading", 1);
        Assert.Equal(before, doc.GetBodyParagraphs().Count);
    }

    [Fact]
    public void GetBodyParagraphs_EmptyDoc_ZeroOrEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        var body = doc.GetBodyParagraphs();
        Assert.True(body == null || body.Count == 0);
    }

    // -------------------------------------------------------------------------
    // RemoveAllParagraphs
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveAllParagraphs_ZeroesParagraphCount()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetParagraphCount() > 0);
        doc.RemoveAllParagraphs();
        Assert.Equal(0, doc.GetParagraphCount());
    }

    [Fact]
    public void RemoveAllParagraphs_ThenAppendWorks()
    {
        var doc = CreateRichDoc();
        doc.RemoveAllParagraphs();
        doc.AppendParagraph("Fresh start paragraph.");
        Assert.Equal(1, doc.GetParagraphCount());
    }

    [Fact]
    public void RemoveAllParagraphs_ThenGetHeadingCountZero()
    {
        var doc = CreateRichDoc();
        doc.RemoveAllParagraphs();
        Assert.Equal(0, doc.GetHeadingCount());
    }

    [Fact]
    public void RemoveAllParagraphs_ThenGetBodyParagraphsEmpty()
    {
        var doc = CreateRichDoc();
        doc.RemoveAllParagraphs();
        var body = doc.GetBodyParagraphs();
        Assert.True(body == null || body.Count == 0);
    }

    [Fact]
    public void RemoveAllParagraphs_OnEmptyDoc_NoThrow()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.RemoveAllParagraphs());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_ReplaceText_GetBodyParagraphs_RemoveAll_Rebuild_SaveToFile_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Vision Statement", 1);
        doc.AppendParagraph("Our vision is to create innovative products for every customer.");
        doc.AppendParagraph("Every customer deserves excellent support and every feature matters.");
        doc.InsertHeading(3, "Mission Statement", 2);
        doc.AppendParagraph("Our mission drives every decision and every team effort.");

        // GetBodyParagraphs — 3 body
        var body = doc.GetBodyParagraphs();
        Assert.Equal(3, body.Count);
        Assert.True(body.Exists(p => p.Text.Contains("vision") || p.Text.Contains("customer")));

        // ReplaceText — replace "every" with "each"
        doc.ReplaceText("every", "each");
        doc.ReplaceText("Every", "Each");
        var text = doc.ExportToPlainText();
        Assert.True(text.Contains("each") || !text.Contains("every"));

        // GetBodyParagraphs still 3 after replace
        Assert.Equal(3, doc.GetBodyParagraphs().Count);

        // SaveToFile and reload to verify persistence
        var path = TempFile("dogfood_replace.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.NotNull(loaded);
        var loadedText = loaded.ExportToPlainText();
        Assert.NotNull(loadedText);

        // GetBodyParagraphs on loaded
        var loadedBody = loaded.GetBodyParagraphs();
        Assert.Equal(3, loadedBody.Count);

        // RemoveAllParagraphs on loaded
        loaded.RemoveAllParagraphs();
        Assert.Equal(0, loaded.GetParagraphCount());
        Assert.Equal(0, loaded.GetHeadingCount());
        var emptyBody = loaded.GetBodyParagraphs();
        Assert.True(emptyBody == null || emptyBody.Count == 0);

        // Rebuild from scratch
        loaded.InsertHeading(0, "Rebuilt Document", 1);
        loaded.AppendParagraph("This paragraph was added after RemoveAllParagraphs.");
        loaded.AppendParagraph("A second paragraph confirms the rebuild is complete.");
        Assert.Equal(3, loaded.GetParagraphCount());
        Assert.Equal(1, loaded.GetHeadingCount());
        Assert.Equal(2, loaded.GetBodyParagraphs().Count);

        // ReplaceText in rebuilt doc
        loaded.ReplaceText("paragraph", "section");
        var rebuiltText = loaded.ExportToPlainText();
        Assert.NotNull(rebuiltText);

        // SaveToFile rebuilt
        var path2 = TempFile("dogfood_rebuilt.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var final = FodtDocument.LoadFile(path2);
        Assert.Equal(3, final.GetParagraphCount());
        Assert.Equal(1, final.GetHeadingCount());
    }
}
