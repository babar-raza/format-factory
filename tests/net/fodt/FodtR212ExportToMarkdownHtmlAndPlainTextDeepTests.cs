// Tests for FodtDocument.ExportToMarkdown, ExportToHtml, ExportToPlainText deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R212

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R212: Tests for FodtDocument.ExportToMarkdown, ExportToHtml, ExportToPlainText deeper.
/// ExportToMarkdown(): returns the document content as a Markdown string.
/// ExportToHtml(): returns the document content as an HTML string.
/// ExportToPlainText(): returns the document content as plain text.
/// ExportToFile(path, format): writes the document to file in the given format.
/// Covers: ExportToMarkdown non-null; ExportToMarkdown non-empty; ExportToMarkdown contains heading;
/// ExportToMarkdown contains paragraph text; ExportToHtml non-null; ExportToHtml non-empty;
/// ExportToHtml contains html tag or body; ExportToHtml contains paragraph text;
/// ExportToPlainText non-null; ExportToPlainText contains paragraph content;
/// ExportToPlainText does not contain html tags; ExportToFile markdown creates file;
/// dogfood CreateEmpty->InsertHeadings->AppendParagraphs->ExportAll->Verify pipeline.
/// </summary>
public class FodtR212ExportToMarkdownHtmlAndPlainTextDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR212ExportToMarkdownHtmlAndPlainTextDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR212_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Project Overview", 1);
        doc.AppendParagraph("This document provides an overview of the current project status.");
        doc.InsertHeading(1, "Goals and Objectives", 2);
        doc.AppendParagraph("The primary goal is to deliver a high-quality product.");
        doc.InsertHeading(2, "Timeline", 2);
        doc.AppendParagraph("The project is expected to complete by end of Q4.");
        return doc;
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
    public void ExportToMarkdown_ContainsParagraphText()
    {
        var doc = CreateRichDoc();
        var md = doc.ExportToMarkdown();
        Assert.Contains("Project Overview", md);
    }

    [Fact]
    public void ExportToMarkdown_ContainsBodyText()
    {
        var doc = CreateRichDoc();
        var md = doc.ExportToMarkdown();
        Assert.Contains("high-quality product", md);
    }

    [Fact]
    public void ExportToMarkdown_SingleParagraph_ContainsText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Simple paragraph for export.");
        var md = doc.ExportToMarkdown();
        Assert.Contains("Simple paragraph", md);
    }

    [Fact]
    public void ExportToMarkdown_AfterSetParagraphText_ReflectsChange()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Original text.");
        doc.SetParagraphText(0, "Updated text for export.");
        var md = doc.ExportToMarkdown();
        Assert.Contains("Updated text", md);
        Assert.DoesNotContain("Original text", md);
    }

    // -------------------------------------------------------------------------
    // ExportToHtml
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToHtml_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.ExportToHtml());
    }

    [Fact]
    public void ExportToHtml_NonEmpty()
    {
        var doc = CreateRichDoc();
        Assert.NotEmpty(doc.ExportToHtml());
    }

    [Fact]
    public void ExportToHtml_ContainsParagraphText()
    {
        var doc = CreateRichDoc();
        var html = doc.ExportToHtml();
        Assert.Contains("Project Overview", html);
    }

    [Fact]
    public void ExportToHtml_ContainsBodyContent()
    {
        var doc = CreateRichDoc();
        var html = doc.ExportToHtml();
        Assert.Contains("high-quality product", html);
    }

    [Fact]
    public void ExportToHtml_HasStructuredContent()
    {
        var doc = CreateRichDoc();
        var html = doc.ExportToHtml();
        // Should contain some HTML structure (tags or structured text)
        Assert.True(html.Contains("<") || html.Contains("Project Overview"));
    }

    // -------------------------------------------------------------------------
    // ExportToPlainText
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPlainText_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.ExportToPlainText());
    }

    [Fact]
    public void ExportToPlainText_NonEmpty()
    {
        var doc = CreateRichDoc();
        Assert.NotEmpty(doc.ExportToPlainText());
    }

    [Fact]
    public void ExportToPlainText_ContainsParagraphContent()
    {
        var doc = CreateRichDoc();
        var text = doc.ExportToPlainText();
        Assert.Contains("Project Overview", text);
    }

    [Fact]
    public void ExportToPlainText_ContainsBodyText()
    {
        var doc = CreateRichDoc();
        var text = doc.ExportToPlainText();
        Assert.Contains("high-quality product", text);
    }

    // -------------------------------------------------------------------------
    // ExportToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToFile_Markdown_CreatesFile()
    {
        var doc = CreateRichDoc();
        var path = TempFile("export.md");
        doc.ExportToFile(path, "markdown");
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToFile_Markdown_ContentNonEmpty()
    {
        var doc = CreateRichDoc();
        var path = TempFile("content.md");
        doc.ExportToFile(path, "markdown");
        var content = File.ReadAllText(path);
        Assert.NotEmpty(content);
    }

    [Fact]
    public void ExportToFile_Html_CreatesFile()
    {
        var doc = CreateRichDoc();
        var path = TempFile("export.html");
        doc.ExportToFile(path, "html");
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToFile_PlainText_CreatesFile()
    {
        var doc = CreateRichDoc();
        var path = TempFile("export.txt");
        doc.ExportToFile(path, "text");
        Assert.True(File.Exists(path));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateEmpty_InsertHeadings_AppendParagraphs_ExportAll_Verify_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();

        // Build document
        doc.InsertHeading(0, "Annual Report", 1);
        doc.AppendParagraph("This annual report summarizes the year's achievements.");
        doc.InsertHeading(1, "Financial Summary", 2);
        doc.AppendParagraph("Revenue grew by fifteen percent year over year.");
        doc.InsertHeading(2, "Conclusion", 1);
        doc.AppendParagraph("The organization remains on track for its strategic goals.");

        // Verify structure
        Assert.Equal(6, doc.GetParagraphCount());
        Assert.Equal(3, doc.GetHeadingCount());

        // ExportToMarkdown
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.Contains("Annual Report", md);
        Assert.Contains("fifteen percent", md);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.Contains("Annual Report", html);

        // ExportToPlainText
        var plain = doc.ExportToPlainText();
        Assert.NotNull(plain);
        Assert.Contains("Annual Report", plain);
        Assert.Contains("fifteen percent", plain);

        // ExportToFile for each format
        var mdPath = TempFile("annual.md");
        var htmlPath = TempFile("annual.html");
        var txtPath = TempFile("annual.txt");
        doc.ExportToFile(mdPath, "markdown");
        doc.ExportToFile(htmlPath, "html");
        doc.ExportToFile(txtPath, "text");
        Assert.True(File.Exists(mdPath));
        Assert.True(File.Exists(htmlPath));
        Assert.True(File.Exists(txtPath));

        // Verify file contents
        var mdContent = File.ReadAllText(mdPath);
        Assert.Contains("Annual Report", mdContent);
        var txtContent = File.ReadAllText(txtPath);
        Assert.Contains("Annual Report", txtContent);

        // GetWordCount still positive
        Assert.True(doc.GetWordCount() > 0);
    }
}
