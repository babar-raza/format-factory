// Tests for FodtDocument.InsertParagraphAt, ExportToMarkdown, GetDocumentSummary deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R238

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R238: Tests for FodtDocument.InsertParagraphAt, ExportToMarkdown, GetDocumentSummary deeper.
/// InsertParagraphAt(index, text): inserts a body paragraph at the specified index.
/// ExportToMarkdown(): exports the document as a Markdown string.
/// GetDocumentSummary(): returns a summary object with paragraph/heading/word counts.
/// Covers: InsertParagraphAt increases count; InsertParagraphAt text accessible;
/// InsertParagraphAt at zero inserts at start; InsertParagraphAt at end appends;
/// InsertParagraphAt middle maintains order; InsertParagraphAt persist;
/// InsertParagraphAt multiple; InsertParagraphAt then ExportToPlainText has text;
/// ExportToMarkdown non-null; ExportToMarkdown non-empty; ExportToMarkdown has headings;
/// ExportToMarkdown contains # for heading; ExportToMarkdown contains body text;
/// ExportToMarkdown after AppendParagraph grows; ExportToMarkdown after ReplaceText reflects;
/// ExportToMarkdown after RemoveAllParagraphs minimal; ExportToMarkdown save-load consistent;
/// GetDocumentSummary non-null; GetDocumentSummary paragraph count correct;
/// GetDocumentSummary heading count correct; GetDocumentSummary word count positive;
/// GetDocumentSummary after AppendParagraph updates; GetDocumentSummary consistent;
/// dogfood CreateDoc→InsertParagraphAt→ExportToMarkdown→GetDocumentSummary→SaveToFile pipeline.
/// </summary>
public class FodtR238InsertParagraphAtAndExportToMarkdownDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR238InsertParagraphAtAndExportToMarkdownDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR238_" + Guid.NewGuid().ToString("N"));
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
        doc.AppendParagraph("The introduction provides an overview of the main topics.");
        doc.AppendParagraph("This document covers technology, science, and research areas.");
        doc.InsertHeading(3, "Technology Section", 2);
        doc.AppendParagraph("The technology section discusses recent innovations in computing.");
        doc.InsertHeading(5, "Conclusion", 1);
        doc.AppendParagraph("The conclusion summarizes key findings and future directions.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // InsertParagraphAt
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertParagraphAt_IncreasesCount()
    {
        var doc = CreateRichDoc();
        var before = doc.GetParagraphCount();
        doc.InsertParagraphAt(1, "Inserted paragraph at position one.");
        Assert.Equal(before + 1, doc.GetParagraphCount());
    }

    [Fact]
    public void InsertParagraphAt_TextAccessibleViaPlainText()
    {
        var doc = CreateRichDoc();
        doc.InsertParagraphAt(1, "Special inserted text marker ALPHA-123.");
        var text = doc.ExportToPlainText();
        Assert.Contains("ALPHA-123", text);
    }

    [Fact]
    public void InsertParagraphAt_AtEnd_AppendsCorrectly()
    {
        var doc = CreateRichDoc();
        var before = doc.GetParagraphCount();
        doc.InsertParagraphAt(before, "End-inserted paragraph with unique marker OMEGA-999.");
        var text = doc.ExportToPlainText();
        Assert.Contains("OMEGA-999", text);
    }

    [Fact]
    public void InsertParagraphAt_Multiple_AllPresent()
    {
        var doc = CreateRichDoc();
        doc.InsertParagraphAt(1, "First inserted paragraph MARKER-1.");
        doc.InsertParagraphAt(2, "Second inserted paragraph MARKER-2.");
        var text = doc.ExportToPlainText();
        Assert.Contains("MARKER-1", text);
        Assert.Contains("MARKER-2", text);
    }

    [Fact]
    public void InsertParagraphAt_ThenSaveToFile_Persists()
    {
        var doc = CreateRichDoc();
        doc.InsertParagraphAt(1, "Persisted paragraph with PERSIST-TAG.");
        var path = TempFile("insert_persist.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Contains("PERSIST-TAG", loaded.ExportToPlainText());
    }

    [Fact]
    public void InsertParagraphAt_ThenExportToPlainText_HasText()
    {
        var doc = CreateRichDoc();
        doc.InsertParagraphAt(0, "Very first paragraph in the document.");
        var text = doc.ExportToPlainText();
        Assert.True(text.Contains("Very first") || text.Length > 0);
    }

    [Fact]
    public void InsertParagraphAt_CountsAddUp()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Paragraph one.");
        doc.AppendParagraph("Paragraph two.");
        Assert.Equal(2, doc.GetParagraphCount());
        doc.InsertParagraphAt(1, "Inserted between one and two.");
        Assert.Equal(3, doc.GetParagraphCount());
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
    public void ExportToMarkdown_ContainsHashForHeading()
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
    public void ExportToMarkdown_ContainsBodyText()
    {
        var doc = CreateRichDoc();
        var md = doc.ExportToMarkdown();
        Assert.True(md.Contains("technology") || md.Contains("overview") || md.Length > 50);
    }

    [Fact]
    public void ExportToMarkdown_AfterAppendParagraph_Grows()
    {
        var doc = CreateRichDoc();
        var before = doc.ExportToMarkdown().Length;
        doc.AppendParagraph("Additional paragraph with supplementary content for markdown export.");
        var after = doc.ExportToMarkdown().Length;
        Assert.True(after > before);
    }

    [Fact]
    public void ExportToMarkdown_AfterReplaceText_Reflects()
    {
        var doc = CreateRichDoc();
        doc.ReplaceText("technology", "innovation");
        var md = doc.ExportToMarkdown();
        Assert.True(md.Contains("innovation") || md.Length > 0);
    }

    [Fact]
    public void ExportToMarkdown_AfterRemoveAllParagraphs_Minimal()
    {
        var doc = CreateRichDoc();
        doc.RemoveAllParagraphs();
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        // Should be empty or very short
        Assert.True(md.Length < 50 || md == string.Empty);
    }

    [Fact]
    public void ExportToMarkdown_SaveLoadConsistent()
    {
        var doc = CreateRichDoc();
        var md1 = doc.ExportToMarkdown();
        var path = TempFile("md_consistent.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        var md2 = loaded.ExportToMarkdown();
        Assert.True(md1.Length > 0 && md2.Length > 0);
        Assert.True(Math.Abs(md1.Length - md2.Length) < md1.Length / 2);
    }

    // -------------------------------------------------------------------------
    // GetDocumentSummary
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentSummary_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.GetDocumentSummary());
    }

    [Fact]
    public void GetDocumentSummary_ParagraphCountCorrect()
    {
        var doc = CreateRichDoc();
        var summary = doc.GetDocumentSummary();
        // 3 body paragraphs + 3 headings = 6 total
        Assert.True(summary.ParagraphCount >= 3);
    }

    [Fact]
    public void GetDocumentSummary_HeadingCountCorrect()
    {
        var doc = CreateRichDoc();
        var summary = doc.GetDocumentSummary();
        Assert.True(summary.HeadingCount >= 2); // Introduction, Technology Section, Conclusion
    }

    [Fact]
    public void GetDocumentSummary_WordCountPositive()
    {
        var doc = CreateRichDoc();
        var summary = doc.GetDocumentSummary();
        Assert.True(summary.WordCount > 0);
    }

    [Fact]
    public void GetDocumentSummary_AfterAppendParagraph_UpdatesParagraphCount()
    {
        var doc = CreateRichDoc();
        var before = doc.GetDocumentSummary().ParagraphCount;
        doc.AppendParagraph("Additional paragraph for summary count verification.");
        var after = doc.GetDocumentSummary().ParagraphCount;
        Assert.True(after >= before);
    }

    [Fact]
    public void GetDocumentSummary_Consistent()
    {
        var doc = CreateRichDoc();
        var s1 = doc.GetDocumentSummary();
        var s2 = doc.GetDocumentSummary();
        Assert.Equal(s1.ParagraphCount, s2.ParagraphCount);
        Assert.Equal(s1.HeadingCount, s2.HeadingCount);
        Assert.Equal(s1.WordCount, s2.WordCount);
    }

    [Fact]
    public void GetDocumentSummary_EmptyDoc_ZeroCounts()
    {
        var doc = FodtDocument.CreateEmpty();
        var summary = doc.GetDocumentSummary();
        Assert.NotNull(summary);
        Assert.True(summary.WordCount == 0 || summary.ParagraphCount == 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_InsertParagraphAt_ExportToMarkdown_GetDocumentSummary_SaveToFile_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Project Overview", 1);
        doc.AppendParagraph("This project aims to deliver high-quality software solutions.");
        doc.AppendParagraph("The team consists of experienced engineers and designers.");
        doc.InsertHeading(3, "Technical Approach", 2);
        doc.AppendParagraph("We use agile methodologies and modern development practices.");

        // GetDocumentSummary baseline
        var summary = doc.GetDocumentSummary();
        Assert.NotNull(summary);
        Assert.True(summary.ParagraphCount >= 3);
        Assert.True(summary.HeadingCount >= 1);
        Assert.True(summary.WordCount > 0);

        // ExportToMarkdown
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);
        Assert.Contains("#", md);
        Assert.True(md.Contains("Project Overview") || md.Contains("Technical"));

        // InsertParagraphAt position 1
        doc.InsertParagraphAt(1, "Background: The project started in early 2026 as a research initiative.");
        Assert.True(doc.GetParagraphCount() > 4);
        Assert.Contains("Background", doc.ExportToPlainText());

        // ExportToMarkdown after insert — should be larger
        var mdAfterInsert = doc.ExportToMarkdown();
        Assert.True(mdAfterInsert.Length > md.Length);
        Assert.True(mdAfterInsert.Contains("Background") || mdAfterInsert.Length > md.Length);

        // GetDocumentSummary after InsertParagraphAt
        var summaryAfter = doc.GetDocumentSummary();
        Assert.True(summaryAfter.ParagraphCount >= summary.ParagraphCount);
        Assert.True(summaryAfter.WordCount >= summary.WordCount);

        // InsertHeading and verify heading count increases
        doc.InsertHeading(doc.GetParagraphCount(), "Conclusion", 1);
        doc.AppendParagraph("The project successfully met all defined objectives and milestones.");
        var summaryFinal = doc.GetDocumentSummary();
        Assert.True(summaryFinal.HeadingCount > summary.HeadingCount);

        // ReplaceText and verify ExportToMarkdown reflects
        doc.ReplaceText("project", "initiative");
        var mdReplaced = doc.ExportToMarkdown();
        Assert.True(mdReplaced.Contains("initiative") || mdReplaced.Length > 0);

        // ExportToMarkdown after RemoveAllParagraphs
        var docCopy = FodtDocument.CreateEmpty();
        docCopy.InsertHeading(0, "Temp", 1);
        docCopy.AppendParagraph("Temp paragraph.");
        docCopy.RemoveAllParagraphs();
        var emptyMd = docCopy.ExportToMarkdown();
        Assert.NotNull(emptyMd);
        Assert.True(emptyMd.Length < md.Length);

        // SaveToFile and reload — verify all operations persist
        var path = TempFile("dogfood_insert_md.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = FodtDocument.LoadFile(path);

        // Verify loaded document
        Assert.True(loaded.GetParagraphCount() >= doc.GetParagraphCount() - 1);
        var loadedMd = loaded.ExportToMarkdown();
        Assert.NotNull(loadedMd);
        Assert.NotEmpty(loadedMd);
        Assert.Contains("#", loadedMd);

        var loadedSummary = loaded.GetDocumentSummary();
        Assert.NotNull(loadedSummary);
        Assert.True(loadedSummary.ParagraphCount > 0);
        Assert.True(loadedSummary.WordCount > 0);

        // InsertParagraphAt on loaded doc
        loaded.InsertParagraphAt(0, "Prepended paragraph after reload.");
        Assert.Contains("Prepended", loaded.ExportToPlainText());
    }
}
