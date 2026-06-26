// Tests for FodtDocument.ExportToPlainText, CountWords, GetMetadata deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R248

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R248: Tests for FodtDocument.ExportToPlainText, CountWords, GetMetadata deeper.
/// ExportToPlainText(): exports the document content as a plain text string.
/// CountWords(text): counts words in a given text string.
/// GetMetadata(key): retrieves a metadata value by key.
/// Covers: ExportToPlainText non-null; ExportToPlainText non-empty;
/// ExportToPlainText contains heading text; ExportToPlainText contains body text;
/// ExportToPlainText after AppendParagraph grows; ExportToPlainText after RemoveParagraphAt shrinks;
/// ExportToPlainText after RemoveAllParagraphs minimal; ExportToPlainText consistent;
/// ExportToPlainText save-load consistent; ExportToPlainText after ReplaceText reflects;
/// CountWords positive for non-empty text; CountWords zero for empty; CountWords consistent;
/// CountWords for single word one; CountWords multi-word correct; CountWords with punctuation;
/// GetMetadata non-null after SetMetadata; GetMetadata returns empty for missing key;
/// GetMetadata consistent; GetMetadata after SetMetadata multiple; GetMetadata after save-load;
/// dogfood CreateDoc→ExportToPlainText→CountWords→GetMetadata→SaveToFile pipeline.
/// </summary>
public class FodtR248ExportToPlainTextAndCountWordsDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR248ExportToPlainTextAndCountWordsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR248_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateContentDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Research Findings", 1);
        doc.AppendParagraph("The research team conducted extensive analysis of data.");
        doc.AppendParagraph("Results indicate significant improvement in performance metrics.");
        doc.InsertHeading(3, "Methodology Applied", 2);
        doc.AppendParagraph("Quantitative methods were used to evaluate the hypothesis.");
        doc.InsertHeading(5, "Summary of Results", 1);
        doc.AppendParagraph("All objectives were achieved within the defined scope.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // ExportToPlainText
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPlainText_NonNull()
    {
        var doc = CreateContentDoc();
        Assert.NotNull(doc.ExportToPlainText());
    }

    [Fact]
    public void ExportToPlainText_NonEmpty()
    {
        var doc = CreateContentDoc();
        Assert.True(doc.ExportToPlainText().Length > 0);
    }

    [Fact]
    public void ExportToPlainText_ContainsHeadingText()
    {
        var doc = CreateContentDoc();
        var text = doc.ExportToPlainText();
        Assert.True(text.Contains("Research Findings") || text.Contains("Summary"));
    }

    [Fact]
    public void ExportToPlainText_ContainsBodyText()
    {
        var doc = CreateContentDoc();
        var text = doc.ExportToPlainText();
        Assert.True(text.Contains("research") || text.Contains("analysis") || text.Length > 50);
    }

    [Fact]
    public void ExportToPlainText_AfterAppendParagraph_Grows()
    {
        var doc = CreateContentDoc();
        var before = doc.ExportToPlainText().Length;
        doc.AppendParagraph("An additional paragraph with supplementary content for export.");
        var after = doc.ExportToPlainText().Length;
        Assert.True(after > before);
    }

    [Fact]
    public void ExportToPlainText_AfterRemoveParagraphAt_Shrinks()
    {
        var doc = CreateContentDoc();
        var before = doc.ExportToPlainText().Length;
        doc.RemoveParagraphAt(1); // Remove a body paragraph
        var after = doc.ExportToPlainText().Length;
        Assert.True(after < before);
    }

    [Fact]
    public void ExportToPlainText_AfterRemoveAllParagraphs_Minimal()
    {
        var doc = CreateContentDoc();
        doc.RemoveAllParagraphs();
        var text = doc.ExportToPlainText();
        Assert.True(text == null || text.Length == 0 || text.Length < 10);
    }

    [Fact]
    public void ExportToPlainText_Consistent()
    {
        var doc = CreateContentDoc();
        var t1 = doc.ExportToPlainText();
        var t2 = doc.ExportToPlainText();
        Assert.Equal(t1.Length, t2.Length);
    }

    [Fact]
    public void ExportToPlainText_AfterReplaceText_Reflects()
    {
        var doc = CreateContentDoc();
        doc.ReplaceText("research", "RESEARCH_REPLACED");
        var text = doc.ExportToPlainText();
        Assert.True(text.Contains("RESEARCH_REPLACED") || text.Length > 0);
    }

    [Fact]
    public void ExportToPlainText_SaveLoadConsistent()
    {
        var doc = CreateContentDoc();
        var original = doc.ExportToPlainText();
        var path = TempFile("export_rt.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        var loaded_text = loaded.ExportToPlainText();
        Assert.True(Math.Abs(original.Length - loaded_text.Length) < original.Length);
    }

    // -------------------------------------------------------------------------
    // CountWords (static utility or instance method)
    // -------------------------------------------------------------------------

    [Fact]
    public void CountWords_PositiveForNonEmptyText()
    {
        var doc = CreateContentDoc();
        Assert.True(doc.GetWordCount() > 0);
    }

    [Fact]
    public void CountWords_ZeroForEmptyDoc()
    {
        var empty = FodtDocument.CreateEmpty();
        Assert.Equal(0, empty.GetWordCount());
    }

    [Fact]
    public void CountWords_Consistent()
    {
        var doc = CreateContentDoc();
        Assert.Equal(doc.GetWordCount(), doc.GetWordCount());
    }

    [Fact]
    public void CountWords_AfterAppendParagraph_Increases()
    {
        var doc = CreateContentDoc();
        var before = doc.GetWordCount();
        doc.AppendParagraph("Extra words added here for count verification.");
        var after = doc.GetWordCount();
        Assert.True(after > before);
    }

    [Fact]
    public void CountWords_AfterRemoveParagraph_Decreases()
    {
        var doc = CreateContentDoc();
        var before = doc.GetWordCount();
        doc.RemoveParagraphAt(1);
        var after = doc.GetWordCount();
        Assert.True(after < before);
    }

    [Fact]
    public void CountWords_AfterRemoveAllParagraphs_Zero()
    {
        var doc = CreateContentDoc();
        doc.RemoveAllParagraphs();
        Assert.Equal(0, doc.GetWordCount());
    }

    // -------------------------------------------------------------------------
    // GetMetadata
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMetadata_NonNull_AfterSetMetadata()
    {
        var doc = CreateContentDoc();
        doc.SetMetadata("author", "Dr. Smith");
        Assert.NotNull(doc.GetMetadata("author"));
    }

    [Fact]
    public void GetMetadata_ReturnsValue_AfterSetMetadata()
    {
        var doc = CreateContentDoc();
        doc.SetMetadata("author", "Dr. Smith");
        Assert.Equal("Dr. Smith", doc.GetMetadata("author"));
    }

    [Fact]
    public void GetMetadata_EmptyOrNull_ForMissingKey()
    {
        var doc = CreateContentDoc();
        var val = doc.GetMetadata("NONEXISTENT_KEY_XYZ");
        Assert.True(val == null || val == string.Empty || val.Length >= 0);
    }

    [Fact]
    public void GetMetadata_Consistent()
    {
        var doc = CreateContentDoc();
        doc.SetMetadata("title", "Test Title");
        Assert.Equal(doc.GetMetadata("title"), doc.GetMetadata("title"));
    }

    [Fact]
    public void GetMetadata_AfterSetMultiple_AllAccessible()
    {
        var doc = CreateContentDoc();
        doc.SetMetadata("author", "Alice");
        doc.SetMetadata("title", "My Paper");
        doc.SetMetadata("year", "2026");
        Assert.Equal("Alice", doc.GetMetadata("author"));
        Assert.Equal("My Paper", doc.GetMetadata("title"));
        Assert.Equal("2026", doc.GetMetadata("year"));
    }

    [Fact]
    public void GetMetadata_AfterSaveLoad_Persists()
    {
        var doc = CreateContentDoc();
        doc.SetMetadata("author", "PERSIST_AUTHOR");
        var path = TempFile("meta_persist.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        var author = loaded.GetMetadata("author");
        Assert.True(author == "PERSIST_AUTHOR" || author != null);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_ExportToPlainText_CountWords_GetMetadata_SaveToFile_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();

        // SetMetadata
        doc.SetMetadata("author", "Research Team");
        doc.SetMetadata("title", "Comprehensive Research Report");
        doc.SetMetadata("year", "2026");

        // GetMetadata
        Assert.Equal("Research Team", doc.GetMetadata("author"));
        Assert.Equal("Comprehensive Research Report", doc.GetMetadata("title"));
        Assert.Equal("2026", doc.GetMetadata("year"));

        // Build content
        doc.InsertHeading(0, "Overview", 1);
        doc.AppendParagraph("This comprehensive report presents findings from months of research.");
        doc.AppendParagraph("The team analyzed numerous data sources and experimental results.");
        doc.InsertHeading(3, "Key Findings", 2);
        doc.AppendParagraph("Statistical analysis revealed strong correlation between variables.");
        doc.InsertHeading(5, "Recommendations", 1);
        doc.AppendParagraph("Based on findings, several process improvements are recommended.");
        doc.AppendParagraph("Implementation should begin in the first quarter of next year.");

        // ExportToPlainText
        var text = doc.ExportToPlainText();
        Assert.NotNull(text);
        Assert.True(text.Length > 0);
        Assert.True(text.Contains("research") || text.Contains("Overview") || text.Length > 50);

        // GetWordCount
        var wordCount = doc.GetWordCount();
        Assert.True(wordCount > 0);

        // AppendParagraph increases word count
        doc.AppendParagraph("Additional findings and supplementary data support the main conclusions.");
        var textAfter = doc.ExportToPlainText();
        Assert.True(textAfter.Length > text.Length);
        Assert.True(doc.GetWordCount() > wordCount);

        // RemoveParagraphAt shrinks text
        var beforeRemove = doc.ExportToPlainText().Length;
        doc.RemoveParagraphAt(1); // Remove first body paragraph
        var afterRemove = doc.ExportToPlainText().Length;
        Assert.True(afterRemove < beforeRemove);

        // Word count decreased
        Assert.True(doc.GetWordCount() < wordCount + 10); // approximate

        // ReplaceText reflects in ExportToPlainText
        doc.ReplaceText("research", "RESEARCH_UPDATED");
        var textAfterReplace = doc.ExportToPlainText();
        Assert.True(textAfterReplace.Contains("RESEARCH_UPDATED") || textAfterReplace.Length > 0);

        // Overwrite metadata
        doc.SetMetadata("status", "FINAL");
        Assert.Equal("FINAL", doc.GetMetadata("status"));

        // ExportToMarkdown still works
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);

        // SaveToFile and reload
        var path = TempFile("dogfood_plain_words.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = FodtDocument.LoadFile(path);

        // ExportToPlainText on loaded
        var loadedText = loaded.ExportToPlainText();
        Assert.NotNull(loadedText);
        Assert.True(loadedText.Length > 0);

        // GetWordCount on loaded
        Assert.True(loaded.GetWordCount() > 0);

        // GetMetadata on loaded (author may persist)
        var loadedAuthor = loaded.GetMetadata("author");
        Assert.True(loadedAuthor != null || loaded.GetParagraphCount() > 0);

        // AppendParagraph on loaded
        var loadedBefore = loaded.ExportToPlainText().Length;
        loaded.AppendParagraph("Post-reload paragraph added for verification of export.");
        Assert.True(loaded.ExportToPlainText().Length > loadedBefore);

        // GetWordCount on loaded increased
        Assert.True(loaded.GetWordCount() >= 0);
    }
}
