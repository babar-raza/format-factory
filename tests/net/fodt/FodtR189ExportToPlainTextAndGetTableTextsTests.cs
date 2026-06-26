// Tests for FodtDocument.ExportToPlainTextFile, GetPlainText, Tables, GetParagraphCount.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R189

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R189: Tests for FodtDocument.ExportToPlainTextFile, GetPlainText, Tables, GetParagraphCount.
/// ExportToPlainTextFile(path): writes plain text to disk.
/// GetPlainText(): returns full document as plain text string.
/// Tables: returns list of FodtTable objects.
/// GetParagraphCount: number of paragraphs including headings.
/// Covers: ExportToPlainTextFile creates file; ExportToPlainTextFile content has text;
/// GetPlainText is non-empty; GetPlainText contains paragraph text;
/// GetPlainText contains all paragraphs; Tables non-null; Tables count;
/// GetParagraphCount after AppendParagraph; GetParagraphCount matches ParagraphCount;
/// GetParagraphCount includes headings; ExportToMarkdownFile creates file;
/// ExportToHtmlFile creates file; ExportToMarkdownFile contains heading markers;
/// ExportToHtmlFile contains HTML tags;
/// dogfood CreateEmpty->AppendParagraphs->GetPlainText->ExportFiles pipeline.
/// </summary>
public class FodtR189ExportToPlainTextAndGetTableTextsTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR189ExportToPlainTextAndGetTableTextsTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR189_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateWithContent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Chapter 1", 1);
        doc.AppendParagraph("First paragraph with some content.");
        doc.AppendParagraph("Second paragraph with more content.");
        doc.InsertHeading(3, "Chapter 2", 1);
        doc.AppendParagraph("Third paragraph at the end.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // ExportToPlainTextFile
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPlainTextFile_CreatesFile()
    {
        var doc = CreateWithContent();
        var path = TempFile("doc.txt");
        doc.ExportToPlainTextFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToPlainTextFile_ContentHasText()
    {
        var doc = CreateWithContent();
        var path = TempFile("doc2.txt");
        doc.ExportToPlainTextFile(path);
        var content = File.ReadAllText(path);
        Assert.Contains("Chapter 1", content);
    }

    [Fact]
    public void ExportToPlainTextFile_ContentHasAllParagraphs()
    {
        var doc = CreateWithContent();
        var path = TempFile("doc3.txt");
        doc.ExportToPlainTextFile(path);
        var content = File.ReadAllText(path);
        Assert.Contains("First paragraph", content);
        Assert.Contains("Second paragraph", content);
    }

    // -------------------------------------------------------------------------
    // GetPlainText
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPlainText_IsNonEmpty()
    {
        var doc = CreateWithContent();
        var text = doc.GetPlainText();
        Assert.False(string.IsNullOrEmpty(text));
    }

    [Fact]
    public void GetPlainText_ContainsParagraphText()
    {
        var doc = CreateWithContent();
        var text = doc.GetPlainText();
        Assert.Contains("First paragraph", text);
    }

    [Fact]
    public void GetPlainText_ContainsAllParagraphs()
    {
        var doc = CreateWithContent();
        var text = doc.GetPlainText();
        Assert.Contains("Chapter 1", text);
        Assert.Contains("Third paragraph", text);
    }

    // -------------------------------------------------------------------------
    // Tables
    // -------------------------------------------------------------------------

    [Fact]
    public void Tables_IsNonNull()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.NotNull(doc.Tables);
    }

    [Fact]
    public void Tables_EmptyDocHasZeroTables()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.Tables.Count);
    }

    // -------------------------------------------------------------------------
    // GetParagraphCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphCount_AfterAppendParagraph_Increments()
    {
        var doc = FodtDocument.CreateEmpty();
        var before = doc.GetParagraphCount();
        doc.AppendParagraph("New paragraph.");
        Assert.Equal(before + 1, doc.GetParagraphCount());
    }

    [Fact]
    public void GetParagraphCount_MatchesParagraphCount()
    {
        var doc = CreateWithContent();
        Assert.Equal(doc.ParagraphCount, doc.GetParagraphCount());
    }

    // -------------------------------------------------------------------------
    // ExportToMarkdownFile / ExportToHtmlFile
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToMarkdownFile_CreatesFile()
    {
        var doc = CreateWithContent();
        var path = TempFile("doc.md");
        doc.ExportToMarkdownFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToMarkdownFile_ContainsHeadingMarkers()
    {
        var doc = CreateWithContent();
        var path = TempFile("headings.md");
        doc.ExportToMarkdownFile(path);
        var content = File.ReadAllText(path);
        Assert.Contains("#", content);
    }

    [Fact]
    public void ExportToHtmlFile_CreatesFile()
    {
        var doc = CreateWithContent();
        var path = TempFile("doc.html");
        doc.ExportToHtmlFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToHtmlFile_ContainsHtmlTags()
    {
        var doc = CreateWithContent();
        var path = TempFile("tags.html");
        doc.ExportToHtmlFile(path);
        var content = File.ReadAllText(path);
        Assert.Contains("<", content);
        Assert.Contains(">", content);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateEmpty->AppendParagraphs->GetPlainText->ExportFiles
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateAppendGetPlainTextExportFiles_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Summary", 1);
        doc.AppendParagraph("This is the summary section content.");
        doc.AppendParagraph("And here is more content for testing.");

        // GetPlainText
        var text = doc.GetPlainText();
        Assert.NotNull(text);
        Assert.Contains("Summary", text);
        Assert.Contains("summary section", text);

        // ParagraphCount
        Assert.Equal(3, doc.GetParagraphCount()); // 1 heading + 2 paragraphs

        // Tables (empty doc)
        Assert.NotNull(doc.Tables);

        // ExportToPlainTextFile
        var txtPath = TempFile("dogfood.txt");
        doc.ExportToPlainTextFile(txtPath);
        Assert.True(File.Exists(txtPath));
        var txtContent = File.ReadAllText(txtPath);
        Assert.Contains("Summary", txtContent);

        // ExportToMarkdownFile
        var mdPath = TempFile("dogfood.md");
        doc.ExportToMarkdownFile(mdPath);
        Assert.True(File.Exists(mdPath));

        // ExportToHtmlFile
        var htmlPath = TempFile("dogfood.html");
        doc.ExportToHtmlFile(htmlPath);
        Assert.True(File.Exists(htmlPath));
        var htmlContent = File.ReadAllText(htmlPath);
        Assert.Contains("Summary", htmlContent);
    }
}
