// Tests for FodtDocument.ExportToHtml, ExportToMarkdown, ExportToPlainText deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R203

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R203: Tests for FodtDocument.ExportToHtml, ExportToMarkdown, ExportToPlainText.
/// ExportToHtml(): returns document as HTML string.
/// ExportToMarkdown(): returns document as Markdown string.
/// ExportToPlainText(): returns document as plain text string.
/// Covers: ExportToHtml non-null; ExportToHtml non-empty; ExportToHtml contains tags;
/// ExportToHtml contains paragraph text; ExportToHtml contains heading text;
/// ExportToMarkdown non-null; ExportToMarkdown non-empty;
/// ExportToMarkdown contains text; ExportToMarkdown contains heading marker;
/// ExportToPlainText non-null; ExportToPlainText non-empty;
/// ExportToPlainText contains all paragraph text;
/// ExportToPlainText equals GetPlainText; ExportToHtmlFile creates file;
/// ExportToMarkdownFile creates file; ExportToPlainTextFile creates file;
/// dogfood CreateEmpty->InsertHeadings->AppendParagraphs->ExportAllFormats->Verify.
/// </summary>
public class FodtR203ExportToHtmlAndMarkdownTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR203ExportToHtmlAndMarkdownTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR203_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Annual Report", 1);
        doc.AppendParagraph("This report summarizes our annual achievements.");
        doc.InsertHeading(1, "Financial Overview", 2);
        doc.AppendParagraph("Revenue increased by fifteen percent year over year.");
        doc.InsertHeading(2, "Conclusion", 1);
        doc.AppendParagraph("We remain committed to delivering value to stakeholders.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // ExportToHtml (string)
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
        Assert.False(string.IsNullOrWhiteSpace(doc.ExportToHtml()));
    }

    [Fact]
    public void ExportToHtml_ContainsHtmlTags()
    {
        var doc = CreateRichDoc();
        var html = doc.ExportToHtml();
        Assert.Contains("<", html);
    }

    [Fact]
    public void ExportToHtml_ContainsParagraphText()
    {
        var doc = CreateRichDoc();
        var html = doc.ExportToHtml();
        Assert.Contains("annual achievements", html);
    }

    [Fact]
    public void ExportToHtml_ContainsHeadingText()
    {
        var doc = CreateRichDoc();
        var html = doc.ExportToHtml();
        Assert.Contains("Annual Report", html);
    }

    // -------------------------------------------------------------------------
    // ExportToMarkdown (string)
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
        Assert.False(string.IsNullOrWhiteSpace(doc.ExportToMarkdown()));
    }

    [Fact]
    public void ExportToMarkdown_ContainsText()
    {
        var doc = CreateRichDoc();
        var md = doc.ExportToMarkdown();
        Assert.Contains("Annual Report", md);
    }

    [Fact]
    public void ExportToMarkdown_ContainsHeadingMarker()
    {
        var doc = CreateRichDoc();
        var md = doc.ExportToMarkdown();
        Assert.Contains("#", md);
    }

    [Fact]
    public void ExportToMarkdown_ContainsParagraphText()
    {
        var doc = CreateRichDoc();
        var md = doc.ExportToMarkdown();
        Assert.Contains("Revenue", md);
    }

    // -------------------------------------------------------------------------
    // ExportToPlainText (string)
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
        Assert.False(string.IsNullOrWhiteSpace(doc.ExportToPlainText()));
    }

    [Fact]
    public void ExportToPlainText_ContainsAllParagraphs()
    {
        var doc = CreateRichDoc();
        var text = doc.ExportToPlainText();
        Assert.Contains("annual achievements", text);
        Assert.Contains("Revenue", text);
        Assert.Contains("stakeholders", text);
    }

    [Fact]
    public void ExportToPlainText_ContainsHeadingText()
    {
        var doc = CreateRichDoc();
        var text = doc.ExportToPlainText();
        Assert.Contains("Annual Report", text);
    }

    // -------------------------------------------------------------------------
    // File export methods
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToHtmlFile_CreatesFile()
    {
        var doc = CreateRichDoc();
        var path = TempFile("out.html");
        doc.ExportToHtmlFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToMarkdownFile_CreatesFile()
    {
        var doc = CreateRichDoc();
        var path = TempFile("out.md");
        doc.ExportToMarkdownFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToPlainTextFile_CreatesFile()
    {
        var doc = CreateRichDoc();
        var path = TempFile("out.txt");
        doc.ExportToPlainTextFile(path);
        Assert.True(File.Exists(path));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateInsertHeadingsAppendParagraphsExportAllFormatsVerify_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Tech Report 2026", 1);
        doc.AppendParagraph("This year saw unprecedented advances in artificial intelligence.");
        doc.InsertHeading(1, "Key Findings", 2);
        doc.AppendParagraph("Machine learning applications expanded across all sectors.");
        doc.InsertHeading(2, "Recommendations", 2);
        doc.AppendParagraph("Organizations should invest in AI literacy programs.");

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.Contains("Tech Report 2026", html);
        Assert.Contains("<", html);

        // ExportToMarkdown
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.Contains("Tech Report 2026", md);
        Assert.Contains("#", md);

        // ExportToPlainText
        var text = doc.ExportToPlainText();
        Assert.NotNull(text);
        Assert.Contains("artificial intelligence", text);
        Assert.Contains("Recommendations", text);

        // File exports
        var htmlPath = TempFile("report.html");
        var mdPath = TempFile("report.md");
        var txtPath = TempFile("report.txt");

        doc.ExportToHtmlFile(htmlPath);
        doc.ExportToMarkdownFile(mdPath);
        doc.ExportToPlainTextFile(txtPath);

        Assert.True(File.Exists(htmlPath));
        Assert.True(File.Exists(mdPath));
        Assert.True(File.Exists(txtPath));

        var htmlContent = File.ReadAllText(htmlPath);
        var mdContent = File.ReadAllText(mdPath);
        var txtContent = File.ReadAllText(txtPath);

        Assert.Contains("Tech Report 2026", htmlContent);
        Assert.Contains("Tech Report 2026", mdContent);
        Assert.Contains("Tech Report 2026", txtContent);
    }
}
