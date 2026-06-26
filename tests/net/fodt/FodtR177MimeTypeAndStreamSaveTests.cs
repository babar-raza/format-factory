// Tests for FodtDocument.MimeType, OdfVersion, Load(Stream), and Save round-trip.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R177

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R177: Tests for FodtDocument.MimeType, OdfVersion, Load(Stream), ExportToPlainTextFile.
/// MimeType: returns ODF text MIME type string.
/// OdfVersion: returns ODF version string.
/// Load(Stream): loads FODT from memory stream.
/// ExportToPlainTextFile/ExportToMarkdownFile/ExportToHtmlFile: export to files.
/// Covers: MimeType is non-null; MimeType contains 'opendocument';
/// OdfVersion is non-null; Load(Stream) returns document; Load(Stream) paragraph count;
/// Load(Stream) GetPlainText non-empty; ExportToPlainTextFile creates file;
/// ExportToMarkdownFile creates file; ExportToHtmlFile creates file;
/// exported plain text file is non-empty; exported markdown contains content;
/// exported HTML contains html tag; dogfood Load->Edit->Export files pipeline.
/// </summary>
public class FodtR177MimeTypeAndStreamSaveTests : IDisposable
{
    private readonly string _tempDir;
    private static readonly string FodtFixturePath =
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "..", "..",
            "samples", "by-format", "fodt", "valid", "two-paragraphs.fodt");

    public FodtR177MimeTypeAndStreamSaveTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR177_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private FodtDocument LoadFixture()
    {
        var path = Path.GetFullPath(FodtFixturePath);
        return FodtDocument.Load(path);
    }

    // -------------------------------------------------------------------------
    // MimeType
    // -------------------------------------------------------------------------

    [Fact]
    public void MimeType_IsNotNull()
    {
        var doc = LoadFixture();
        Assert.NotNull(doc.MimeType);
    }

    [Fact]
    public void MimeType_ContainsOpendocument()
    {
        var doc = LoadFixture();
        Assert.Contains("opendocument", doc.MimeType, StringComparison.OrdinalIgnoreCase);
    }

    // -------------------------------------------------------------------------
    // OdfVersion
    // -------------------------------------------------------------------------

    [Fact]
    public void OdfVersion_IsNotNull()
    {
        var doc = LoadFixture();
        Assert.NotNull(doc.OdfVersion);
    }

    [Fact]
    public void OdfVersion_IsNonEmpty()
    {
        var doc = LoadFixture();
        Assert.False(string.IsNullOrEmpty(doc.OdfVersion));
    }

    // -------------------------------------------------------------------------
    // Load(Stream)
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadStream_ReturnsDocument()
    {
        var path = Path.GetFullPath(FodtFixturePath);
        using var stream = File.OpenRead(path);
        var doc = FodtDocument.Load(stream);
        Assert.NotNull(doc);
    }

    [Fact]
    public void LoadStream_ParagraphCountPositive()
    {
        var path = Path.GetFullPath(FodtFixturePath);
        using var stream = File.OpenRead(path);
        var doc = FodtDocument.Load(stream);
        Assert.True(doc.ParagraphCount > 0);
    }

    [Fact]
    public void LoadStream_GetPlainTextNonEmpty()
    {
        var path = Path.GetFullPath(FodtFixturePath);
        using var stream = File.OpenRead(path);
        var doc = FodtDocument.Load(stream);
        Assert.False(string.IsNullOrEmpty(doc.GetPlainText()));
    }

    // -------------------------------------------------------------------------
    // ExportToPlainTextFile / ExportToMarkdownFile / ExportToHtmlFile
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPlainTextFile_CreatesFile()
    {
        var doc = LoadFixture();
        var path = TempFile("doc.txt");
        doc.ExportToPlainTextFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToPlainTextFile_IsNonEmpty()
    {
        var doc = LoadFixture();
        var path = TempFile("content.txt");
        doc.ExportToPlainTextFile(path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void ExportToMarkdownFile_CreatesFile()
    {
        var doc = LoadFixture();
        var path = TempFile("doc.md");
        doc.ExportToMarkdownFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToMarkdownFile_ContentNonEmpty()
    {
        var doc = LoadFixture();
        var path = TempFile("content.md");
        doc.ExportToMarkdownFile(path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void ExportToHtmlFile_CreatesFile()
    {
        var doc = LoadFixture();
        var path = TempFile("doc.html");
        doc.ExportToHtmlFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToHtmlFile_ContainsHtmlTag()
    {
        var doc = LoadFixture();
        var path = TempFile("tagged.html");
        doc.ExportToHtmlFile(path);
        var content = File.ReadAllText(path);
        Assert.Contains("html", content, StringComparison.OrdinalIgnoreCase);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->AppendParagraph->ExportToPlainTextFile->ReadBack
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadEditExportFiles_Pipeline()
    {
        var doc = LoadFixture();
        var initialCount = doc.ParagraphCount;

        // Edit
        doc.AppendParagraph("Dogfood export paragraph R177.");
        Assert.Equal(initialCount + 1, doc.ParagraphCount);

        // Export to txt
        var txtPath = TempFile("dogfood.txt");
        doc.ExportToPlainTextFile(txtPath);
        var txtContent = File.ReadAllText(txtPath);
        Assert.Contains("Dogfood", txtContent);

        // Export to markdown
        var mdPath = TempFile("dogfood.md");
        doc.ExportToMarkdownFile(mdPath);
        Assert.True(new FileInfo(mdPath).Length > 0);

        // Export to html
        var htmlPath = TempFile("dogfood.html");
        doc.ExportToHtmlFile(htmlPath);
        var htmlContent = File.ReadAllText(htmlPath);
        Assert.Contains("Dogfood", htmlContent);
    }
}
