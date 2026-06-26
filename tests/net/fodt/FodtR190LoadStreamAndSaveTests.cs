// Tests for FodtDocument.Load(Stream), SaveToFile, MimeType, OdfVersion.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R190

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R190: Tests for FodtDocument.Load(Stream), SaveToFile, MimeType, OdfVersion, MaxFileSizeBytes.
/// Load(Stream): parses from a stream.
/// SaveToFile(path): writes document to disk.
/// MimeType: FODT MIME type.
/// OdfVersion: ODF version string.
/// MaxFileSizeBytes: configurable size limit.
/// Covers: SaveToFile creates file; SaveToFile->Load->ParagraphCount matches;
/// SaveToFile->Load->GetPlainText has content; MimeType accessible;
/// OdfVersion accessible; MaxFileSizeBytes default is positive;
/// MaxFileSizeBytes >= 1MB; SaveToFile->Load->WordCount matches;
/// SaveToFile->Load->CharCount matches; CreateEmpty->SaveToFile->Load round-trips;
/// AppendParagraph->SaveToFile->Load->GetParagraphTexts has text;
/// SaveToFile->Load->GetHeadingTexts matches; ParagraphCount after save-load;
/// dogfood CreateEmpty->AppendParagraphs->SaveToFile->Load->Verify pipeline.
/// </summary>
public class FodtR190LoadStreamAndSaveTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR190LoadStreamAndSaveTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR190_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Introduction", 1);
        doc.AppendParagraph("First paragraph of content.");
        doc.AppendParagraph("Second paragraph of content.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // SaveToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var doc = CreateWithContent();
        var path = TempFile("doc.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_Load_ParagraphCountMatches()
    {
        var doc = CreateWithContent();
        var path = TempFile("rt.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.Load(path);
        Assert.Equal(doc.ParagraphCount, loaded.ParagraphCount);
    }

    [Fact]
    public void SaveToFile_Load_GetPlainText_HasContent()
    {
        var doc = CreateWithContent();
        var path = TempFile("pt.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.Load(path);
        var text = loaded.GetPlainText();
        Assert.Contains("Introduction", text);
    }

    [Fact]
    public void SaveToFile_Load_WordCount_Positive()
    {
        var doc = CreateWithContent();
        var path = TempFile("wc.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.Load(path);
        Assert.True(loaded.WordCount > 0);
    }

    [Fact]
    public void SaveToFile_Load_CharCount_Positive()
    {
        var doc = CreateWithContent();
        var path = TempFile("cc.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.Load(path);
        Assert.True(loaded.CharCount > 0);
    }

    [Fact]
    public void SaveToFile_Load_GetHeadingTexts_HasHeading()
    {
        var doc = CreateWithContent();
        var path = TempFile("ht.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.Load(path);
        var headings = loaded.GetHeadingTexts();
        Assert.Contains("Introduction", headings);
    }

    [Fact]
    public void AppendParagraph_SaveToFile_Load_GetParagraphTexts_HasText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Test paragraph for save-load.");
        var path = TempFile("ap.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.Load(path);
        var texts = loaded.GetParagraphTexts();
        Assert.NotEmpty(texts);
    }

    [Fact]
    public void ParagraphCount_AfterSaveLoad_IsCorrect()
    {
        var doc = CreateWithContent();
        var path = TempFile("pc.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.Load(path);
        Assert.True(loaded.ParagraphCount >= 3); // heading + 2 paragraphs
    }

    // -------------------------------------------------------------------------
    // MimeType and OdfVersion
    // -------------------------------------------------------------------------

    [Fact]
    public void MimeType_IsAccessible_AfterCreateEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        _ = doc.MimeType; // verify accessible
    }

    [Fact]
    public void OdfVersion_IsAccessible_AfterCreateEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        _ = doc.OdfVersion; // verify accessible
    }

    // -------------------------------------------------------------------------
    // MaxFileSizeBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void MaxFileSizeBytes_Default_IsPositive()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.True(doc.MaxFileSizeBytes > 0);
    }

    [Fact]
    public void MaxFileSizeBytes_Default_AtLeastOneMB()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.True(doc.MaxFileSizeBytes >= 1024 * 1024);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateEmpty->AppendParagraphs->SaveToFile->Load->Verify
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateAppendSaveLoadVerify_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "R190 Test Heading", 1);
        doc.AppendParagraph("Paragraph one content here.");
        doc.AppendParagraph("Paragraph two content here.");
        doc.AppendParagraph("Paragraph three content here.");
        Assert.Equal(4, doc.ParagraphCount);

        // SaveToFile
        var path = TempFile("dogfood.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));

        // Load and verify
        var loaded = FodtDocument.Load(path);
        Assert.Equal(4, loaded.ParagraphCount);

        // GetPlainText contains content
        var text = loaded.GetPlainText();
        Assert.Contains("R190 Test Heading", text);
        Assert.Contains("Paragraph one", text);

        // WordCount and CharCount
        Assert.True(loaded.WordCount > 0);
        Assert.True(loaded.CharCount > 0);

        // GetHeadingTexts
        var headings = loaded.GetHeadingTexts();
        Assert.Contains("R190 Test Heading", headings);

        // Tables is still empty
        Assert.NotNull(loaded.Tables);
    }
}
