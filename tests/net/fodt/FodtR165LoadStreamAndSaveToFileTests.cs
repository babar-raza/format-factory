// Tests for FodtDocument.Load(Stream) and Save/SaveToFile.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R165

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R165: Tests for FodtDocument.Load(Stream) and Save/SaveToFile.
/// Load(Stream): parses FODT XML from a stream.
/// Save(filePath): writes the document back to disk as FODT XML.
/// SaveToFile(path): alias for Save(path).
/// Covers: Load(Stream) null stream throws; Load(Stream) empty stream is non-null;
/// SaveToFile creates file; SaveToFile file is not empty; SaveToFile round-trip after AppendParagraph;
/// SaveToFile round-trip ParagraphCount preserved; SaveToFile and Save are equivalent;
/// SaveToFile CreateEmpty then AppendParagraph then save then Load round-trip;
/// ExportToPlainTextFile creates file; ExportToMarkdownFile creates file;
/// ExportToHtmlFile creates file; dogfood CreateEmpty->Append->Save->Load->GetPlainText pipeline.
/// </summary>
public class FodtR165LoadStreamAndSaveToFileTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR165LoadStreamAndSaveToFileTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR165_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // Load(Stream)
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadStream_NullStream_Throws()
    {
        Assert.ThrowsAny<Exception>(() => FodtDocument.Load((Stream)null!));
    }

    [Fact]
    public void LoadStream_ValidFodtStream_NonNullResult()
    {
        // Build and save a document, then load from stream
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Stream test paragraph.");
        var path = TempFile("stream-test.fodt");
        doc.Save(path);

        using var stream = File.OpenRead(path);
        var loaded = FodtDocument.Load(stream);
        Assert.NotNull(loaded);
    }

    [Fact]
    public void LoadStream_PreservesParagraphCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para 1.");
        doc.AppendParagraph("Para 2.");
        var path = TempFile("para-count.fodt");
        doc.Save(path);

        using var stream = File.OpenRead(path);
        var loaded = FodtDocument.Load(stream);
        Assert.Equal(2, loaded.ParagraphCount);
    }

    // -------------------------------------------------------------------------
    // SaveToFile / Save
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Test content.");
        var path = TempFile("created.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_FileNotEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Non-empty content.");
        var path = TempFile("nonempty.fodt");
        doc.SaveToFile(path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void Save_RoundTrip_ParagraphCountPreserved()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Chapter 1", 1);
        doc.AppendParagraph("Body text here.");
        var path = TempFile("roundtrip.fodt");
        doc.Save(path);
        var reloaded = FodtDocument.Load(path);
        Assert.Equal(2, reloaded.ParagraphCount);
    }

    [Fact]
    public void Save_RoundTrip_ParagraphTextPreserved()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Preserved text.");
        var path = TempFile("text-preserved.fodt");
        doc.Save(path);
        var reloaded = FodtDocument.Load(path);
        Assert.Equal("Preserved text.", reloaded.GetParagraphText(0));
    }

    [Fact]
    public void SaveAndSaveToFile_SameFileSize()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Same content.");

        var path1 = TempFile("save1.fodt");
        var path2 = TempFile("save2.fodt");
        doc.Save(path1);
        doc.SaveToFile(path2);

        Assert.Equal(new FileInfo(path1).Length, new FileInfo(path2).Length);
    }

    // -------------------------------------------------------------------------
    // ExportTo*File methods
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPlainTextFile_CreatesFile()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Plain text export.");
        var path = TempFile("export.txt");
        doc.ExportToPlainTextFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToMarkdownFile_CreatesFile()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Markdown export.");
        var path = TempFile("export.md");
        doc.ExportToMarkdownFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToHtmlFile_CreatesFile()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("HTML export.");
        var path = TempFile("export.html");
        doc.ExportToHtmlFile(path);
        Assert.True(File.Exists(path));
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateEmpty->Append->Save->Load->GetPlainText
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateAppendSaveLoadGetPlainText_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Title", 1);
        doc.AppendParagraph("This is the introduction.");
        doc.AppendParagraph("This is the conclusion.");

        // Save
        var path = TempFile("dogfood.fodt");
        doc.Save(path);
        Assert.True(File.Exists(path));

        // Load from file path
        var reloaded = FodtDocument.Load(path);
        Assert.Equal(3, reloaded.ParagraphCount);

        // Load from stream
        using var stream = File.OpenRead(path);
        var streamLoaded = FodtDocument.Load(stream);
        Assert.Equal(3, streamLoaded.ParagraphCount);

        // GetPlainText
        var text = reloaded.GetPlainText();
        Assert.Contains("Title", text);
        Assert.Contains("introduction", text);
    }
}
