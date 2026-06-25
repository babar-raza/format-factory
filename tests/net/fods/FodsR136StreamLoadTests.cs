// Tests for FodsDocument.Load(Stream stream) — stream-based FODS loading.
// Sprint: FORMAT-FACTORY-FODS-R136-20260627
// Ledger: R136-GOVERNED-DOTNET-FODS-STREAM-LOAD-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R136: Tests for FodsDocument.Load(Stream stream) overload.
/// Verifies that stream-based loading produces the same document as file-based loading,
/// handles null input, and correctly sets SheetCount and cell values.
/// ODF spec basis: §3.7 office:spreadsheet root element.
/// </summary>
public class FodsR136StreamLoadTests
{
    private static readonly string FixturesDir =
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "fods", "Fixtures");

    private static string FixturePath(string name) =>
        Path.GetFullPath(Path.Combine(FixturesDir, name));

    private static Stream OpenFixtureStream(string name) =>
        new FileStream(FixturePath(name), FileMode.Open, FileAccess.Read, FileShare.Read);

    // -------------------------------------------------------------------------
    // Stream load produces a valid document
    // -------------------------------------------------------------------------

    [Fact]
    public void Load_Stream_DocumentIsNotNull()
    {
        using var stream = OpenFixtureStream("fods-minimal-roundtrip.fods");
        var doc = FodsDocument.Load(stream);
        Assert.NotNull(doc);
    }

    [Fact]
    public void Load_Stream_SheetCountAtLeastOne()
    {
        using var stream = OpenFixtureStream("fods-minimal-roundtrip.fods");
        var doc = FodsDocument.Load(stream);
        Assert.True(doc.SheetCount >= 1, $"Expected SheetCount >= 1, got {doc.SheetCount}");
    }

    [Fact]
    public void Load_Stream_SheetNamesNonEmpty()
    {
        using var stream = OpenFixtureStream("fods-minimal-roundtrip.fods");
        var doc = FodsDocument.Load(stream);
        var names = doc.GetSheetNames();
        Assert.NotEmpty(names);
    }

    // -------------------------------------------------------------------------
    // Parity with file-based Load
    // -------------------------------------------------------------------------

    [Fact]
    public void Load_Stream_SheetCountMatchesFileBased()
    {
        var filePath = FixturePath("fods-minimal-roundtrip.fods");
        var fileDoc = FodsDocument.Load(filePath);
        using var stream = OpenFixtureStream("fods-minimal-roundtrip.fods");
        var streamDoc = FodsDocument.Load(stream);
        Assert.Equal(fileDoc.SheetCount, streamDoc.SheetCount);
    }

    [Fact]
    public void Load_Stream_SheetNamesMatchFileBased()
    {
        var filePath = FixturePath("fods-minimal-roundtrip.fods");
        var fileDoc = FodsDocument.Load(filePath);
        using var stream = OpenFixtureStream("fods-minimal-roundtrip.fods");
        var streamDoc = FodsDocument.Load(stream);
        Assert.Equal(fileDoc.GetSheetNames(), streamDoc.GetSheetNames());
    }

    [Fact]
    public void Load_Stream_MultiSheet_SheetCountMatchesFileBased()
    {
        var filePath = FixturePath("fods-multi-sheet.fods");
        var fileDoc = FodsDocument.Load(filePath);
        using var stream = OpenFixtureStream("fods-multi-sheet.fods");
        var streamDoc = FodsDocument.Load(stream);
        Assert.Equal(fileDoc.SheetCount, streamDoc.SheetCount);
    }

    // -------------------------------------------------------------------------
    // Stream from MemoryStream with inline XML
    // -------------------------------------------------------------------------

    [Fact]
    public void Load_MemoryStream_ValidFodsXml_Succeeds()
    {
        // Read fixture bytes, convert to MemoryStream
        var bytes = File.ReadAllBytes(FixturePath("fods-minimal-roundtrip.fods"));
        using var ms = new MemoryStream(bytes);
        var doc = FodsDocument.Load(ms);
        Assert.NotNull(doc);
        Assert.True(doc.SheetCount >= 1);
    }

    // -------------------------------------------------------------------------
    // Null guard
    // -------------------------------------------------------------------------

    [Fact]
    public void Load_NullStream_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => FodsDocument.Load((Stream)null!));
    }

    // -------------------------------------------------------------------------
    // Stream with invalid XML throws FodsDocumentException
    // -------------------------------------------------------------------------

    [Fact]
    public void Load_InvalidXmlStream_ThrowsFodsDocumentException()
    {
        var badXml = Encoding.UTF8.GetBytes("NOT XML AT ALL <<<!!");
        using var ms = new MemoryStream(badXml);
        Assert.Throws<FodsDocumentException>(() => FodsDocument.Load(ms));
    }

    // -------------------------------------------------------------------------
    // Dogfood: stream → mutate → save pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_StreamLoad_MutateSave_Roundtrip()
    {
        var bytes = File.ReadAllBytes(FixturePath("fods-minimal-roundtrip.fods"));
        using var ms = new MemoryStream(bytes);
        var doc = FodsDocument.Load(ms);

        // Verify load succeeded
        var sheetNames = doc.GetSheetNames();
        Assert.NotEmpty(sheetNames);

        // Set a cell value and save to temp path
        var tmpPath = Path.Combine(Path.GetTempPath(), $"fods_r136_{Guid.NewGuid():N}.fods");
        try
        {
            doc.SetCellValue(0, 0, "STREAM_LOAD_PROOF");
            doc.Save(tmpPath);

            // Reload from file and verify
            var reloaded = FodsDocument.Load(tmpPath);
            Assert.Equal(doc.SheetCount, reloaded.SheetCount);
            Assert.Equal("STREAM_LOAD_PROOF", reloaded.GetCellValue(0, 0));
        }
        finally
        {
            if (File.Exists(tmpPath)) File.Delete(tmpPath);
        }
    }
}
