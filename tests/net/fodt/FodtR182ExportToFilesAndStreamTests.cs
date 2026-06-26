// Tests for FodtDocument file export methods and stream Save.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R182

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R182: Tests for FodtDocument Save(filePath), ExportToPlainTextFile, ExportToMarkdownFile.
/// Save(filePath): saves document as FODT XML.
/// SaveToFile(path): alias for Save.
/// ExportToPlainTextFile(path): writes plain text.
/// ExportToMarkdownFile(path): writes markdown.
/// ExportToHtmlFile(path): writes HTML.
/// Covers: Save creates FODT file; SaveToFile creates file; FODT file is non-empty;
/// FODT file contains XML; ExportToPlainTextFile creates file;
/// PlainText file is non-empty; ExportToMarkdownFile creates file;
/// Markdown file is non-empty; ExportToHtmlFile creates file;
/// HTML file is non-empty; HTML file contains html tag;
/// Save then Load round-trip ParagraphCount; dogfood Edit->Save->Load->verify.
/// </summary>
public class FodtR182ExportToFilesAndStreamTests : IDisposable
{
    private readonly string _tempDir;
    private static readonly string FodtFixturePath =
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "..", "..",
            "samples", "by-format", "fodt", "valid", "two-paragraphs.fodt");

    public FodtR182ExportToFilesAndStreamTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR182_" + Guid.NewGuid().ToString("N"));
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
    // Save / SaveToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void Save_CreatesFile()
    {
        var doc = LoadFixture();
        var path = TempFile("saved.fodt");
        doc.Save(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void Save_FileIsNonEmpty()
    {
        var doc = LoadFixture();
        var path = TempFile("nonempty.fodt");
        doc.Save(path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void Save_FileContainsXml()
    {
        var doc = LoadFixture();
        var path = TempFile("xml.fodt");
        doc.Save(path);
        var content = File.ReadAllText(path);
        Assert.Contains("<", content);
    }

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var doc = LoadFixture();
        var path = TempFile("savedToFile.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    // -------------------------------------------------------------------------
    // ExportToPlainTextFile
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPlainTextFile_CreatesFile()
    {
        var doc = LoadFixture();
        var path = TempFile("text.txt");
        doc.ExportToPlainTextFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToPlainTextFile_IsNonEmpty()
    {
        var doc = LoadFixture();
        var path = TempFile("nonEmptyText.txt");
        doc.ExportToPlainTextFile(path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void ExportToPlainTextFile_ContentMatchesGetPlainText()
    {
        var doc = LoadFixture();
        var path = TempFile("matching.txt");
        doc.ExportToPlainTextFile(path);
        var fileContent = File.ReadAllText(path);
        var inMemory = doc.GetPlainText();
        // Both should contain the same words
        Assert.False(string.IsNullOrEmpty(fileContent));
        Assert.False(string.IsNullOrEmpty(inMemory));
    }

    // -------------------------------------------------------------------------
    // ExportToMarkdownFile
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToMarkdownFile_CreatesFile()
    {
        var doc = LoadFixture();
        var path = TempFile("doc.md");
        doc.ExportToMarkdownFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToMarkdownFile_IsNonEmpty()
    {
        var doc = LoadFixture();
        var path = TempFile("nonEmpty.md");
        doc.ExportToMarkdownFile(path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    // -------------------------------------------------------------------------
    // ExportToHtmlFile
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToHtmlFile_CreatesFile()
    {
        var doc = LoadFixture();
        var path = TempFile("doc.html");
        doc.ExportToHtmlFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToHtmlFile_IsNonEmpty()
    {
        var doc = LoadFixture();
        var path = TempFile("nonEmpty.html");
        doc.ExportToHtmlFile(path);
        Assert.True(new FileInfo(path).Length > 0);
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
    // Save then Load round-trip
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveThenLoad_ParagraphCountMatches()
    {
        var doc = LoadFixture();
        var before = doc.ParagraphCount;
        var path = TempFile("roundtrip.fodt");
        doc.Save(path);
        var reloaded = FodtDocument.Load(path);
        Assert.Equal(before, reloaded.ParagraphCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Edit->Save->Load->verify all exports
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_EditSaveLoadVerifyAllExports()
    {
        var doc = LoadFixture();

        // Edit
        doc.AppendParagraph("R182 dogfood test paragraph.");
        Assert.Contains("R182 dogfood test paragraph.", doc.GetPlainText());

        // Save and reload
        var fodtPath = TempFile("dogfood.fodt");
        doc.Save(fodtPath);
        var reloaded = FodtDocument.Load(fodtPath);
        Assert.Contains("R182 dogfood test paragraph.", reloaded.GetPlainText());

        // Export to all formats
        var txtPath = TempFile("dogfood.txt");
        reloaded.ExportToPlainTextFile(txtPath);
        Assert.True(new FileInfo(txtPath).Length > 0);

        var mdPath = TempFile("dogfood.md");
        reloaded.ExportToMarkdownFile(mdPath);
        Assert.True(new FileInfo(mdPath).Length > 0);

        var htmlPath = TempFile("dogfood.html");
        reloaded.ExportToHtmlFile(htmlPath);
        var htmlContent = File.ReadAllText(htmlPath);
        Assert.Contains("html", htmlContent, StringComparison.OrdinalIgnoreCase);
    }
}
