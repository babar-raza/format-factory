// Tests for FodtDocument export to file paths, MimeType, OdfVersion, MaxFileSizeBytes.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R196

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R196: Tests for FodtDocument export to files, MimeType, OdfVersion, MaxFileSizeBytes.
/// ExportToPlainTextFile(path): writes plain text to file.
/// ExportToMarkdownFile(path): writes markdown to file.
/// ExportToHtmlFile(path): writes HTML to file.
/// MimeType: static MIME type string.
/// OdfVersion: static ODF version string.
/// MaxFileSizeBytes: static max file size.
/// Covers: ExportToPlainTextFile creates file; ExportToPlainTextFile content has text;
/// ExportToMarkdownFile creates file; ExportToMarkdownFile content has text;
/// ExportToHtmlFile creates file; ExportToHtmlFile content has HTML tags;
/// MimeType non-null; MimeType contains text or document;
/// OdfVersion non-null; OdfVersion non-empty; MaxFileSizeBytes positive;
/// MaxFileSizeBytes greater than 1MB; ExportToPlainTextFile contains paragraph text;
/// ExportToMarkdownFile contains heading text;
/// dogfood CreateEmpty->AppendContent->ExportToPlainText->ExportToMarkdown->ExportToHtml verify.
/// </summary>
public class FodtR196ExportToFilesAndMimeTypeTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR196ExportToFilesAndMimeTypeTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR196_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Chapter One", 1);
        doc.AppendParagraph("This is the first paragraph of the document.");
        doc.AppendParagraph("Second paragraph with more content.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // ExportToPlainTextFile
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPlainTextFile_CreatesFile()
    {
        var doc = CreateWithContent();
        var path = TempFile("output.txt");
        doc.ExportToPlainTextFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToPlainTextFile_ContentHasParagraphText()
    {
        var doc = CreateWithContent();
        var path = TempFile("plain.txt");
        doc.ExportToPlainTextFile(path);
        var content = File.ReadAllText(path);
        Assert.Contains("first paragraph", content);
    }

    [Fact]
    public void ExportToPlainTextFile_ContentHasHeadingText()
    {
        var doc = CreateWithContent();
        var path = TempFile("headings.txt");
        doc.ExportToPlainTextFile(path);
        var content = File.ReadAllText(path);
        Assert.Contains("Chapter One", content);
    }

    // -------------------------------------------------------------------------
    // ExportToMarkdownFile
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToMarkdownFile_CreatesFile()
    {
        var doc = CreateWithContent();
        var path = TempFile("output.md");
        doc.ExportToMarkdownFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToMarkdownFile_ContentHasText()
    {
        var doc = CreateWithContent();
        var path = TempFile("content.md");
        doc.ExportToMarkdownFile(path);
        var content = File.ReadAllText(path);
        Assert.Contains("Chapter One", content);
    }

    [Fact]
    public void ExportToMarkdownFile_ContentHasMarkdownHeading()
    {
        var doc = CreateWithContent();
        var path = TempFile("heading.md");
        doc.ExportToMarkdownFile(path);
        var content = File.ReadAllText(path);
        // Markdown heading should use # prefix
        Assert.Contains("#", content);
    }

    // -------------------------------------------------------------------------
    // ExportToHtmlFile
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToHtmlFile_CreatesFile()
    {
        var doc = CreateWithContent();
        var path = TempFile("output.html");
        doc.ExportToHtmlFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToHtmlFile_ContentHasHtmlTags()
    {
        var doc = CreateWithContent();
        var path = TempFile("tags.html");
        doc.ExportToHtmlFile(path);
        var content = File.ReadAllText(path);
        Assert.Contains("<", content);
    }

    [Fact]
    public void ExportToHtmlFile_ContentHasText()
    {
        var doc = CreateWithContent();
        var path = TempFile("text.html");
        doc.ExportToHtmlFile(path);
        var content = File.ReadAllText(path);
        Assert.Contains("Chapter One", content);
    }

    // -------------------------------------------------------------------------
    // MimeType / OdfVersion / MaxFileSizeBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void MimeType_NonNull()
    {
        Assert.NotNull(FodtDocument.MimeType);
    }

    [Fact]
    public void MimeType_ContainsTextOrDocument()
    {
        var mimeType = FodtDocument.MimeType.ToLower();
        Assert.True(
            mimeType.Contains("text") || mimeType.Contains("document") || mimeType.Contains("opendocument"),
            $"MimeType '{FodtDocument.MimeType}' should contain relevant text");
    }

    [Fact]
    public void OdfVersion_NonNull()
    {
        Assert.NotNull(FodtDocument.OdfVersion);
    }

    [Fact]
    public void OdfVersion_NonEmpty()
    {
        Assert.NotEmpty(FodtDocument.OdfVersion);
    }

    [Fact]
    public void MaxFileSizeBytes_Positive()
    {
        Assert.True(FodtDocument.MaxFileSizeBytes > 0);
    }

    [Fact]
    public void MaxFileSizeBytes_GreaterThanOneMegabyte()
    {
        Assert.True(FodtDocument.MaxFileSizeBytes > 1024 * 1024);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateEmpty->AppendContent->ExportToPlainText->ExportToMarkdown->ExportToHtml
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateAppendExportAllFormatsVerify_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "My Report", 1);
        doc.AppendParagraph("Introduction paragraph with key findings.");
        doc.AppendParagraph("Methods and analysis section.");

        // MimeType and OdfVersion
        Assert.NotNull(FodtDocument.MimeType);
        Assert.NotNull(FodtDocument.OdfVersion);
        Assert.True(FodtDocument.MaxFileSizeBytes > 0);

        // ExportToPlainTextFile
        var txtPath = TempFile("report.txt");
        doc.ExportToPlainTextFile(txtPath);
        Assert.True(File.Exists(txtPath));
        var txtContent = File.ReadAllText(txtPath);
        Assert.Contains("My Report", txtContent);
        Assert.Contains("Introduction paragraph", txtContent);

        // ExportToMarkdownFile
        var mdPath = TempFile("report.md");
        doc.ExportToMarkdownFile(mdPath);
        Assert.True(File.Exists(mdPath));
        var mdContent = File.ReadAllText(mdPath);
        Assert.Contains("My Report", mdContent);

        // ExportToHtmlFile
        var htmlPath = TempFile("report.html");
        doc.ExportToHtmlFile(htmlPath);
        Assert.True(File.Exists(htmlPath));
        var htmlContent = File.ReadAllText(htmlPath);
        Assert.Contains("My Report", htmlContent);
        Assert.Contains("<", htmlContent);
    }
}
