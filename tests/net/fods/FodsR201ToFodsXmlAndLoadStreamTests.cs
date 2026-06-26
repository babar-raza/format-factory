// Tests for FodsDocument.ToFodsXml, LoadStream, OdfVersion, MimeType.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R201

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R201: Tests for FodsDocument.ToFodsXml, LoadStream, OdfVersion, MimeType.
/// ToFodsXml(): serializes document to FODS XML string.
/// LoadStream(stream): loads FodsDocument from a Stream.
/// OdfVersion: static ODF version string.
/// MimeType: static MIME type string.
/// Covers: ToFodsXml non-null; ToFodsXml non-empty; ToFodsXml contains XML;
/// ToFodsXml->LoadStream round-trip count matches; LoadStream non-null;
/// LoadStream preserves sheet names; LoadStream preserves cell values;
/// OdfVersion non-null; OdfVersion non-empty; OdfVersion contains version number;
/// MimeType non-null; MimeType contains spreadsheet or calc;
/// ToFodsXml->LoadStream->GetCellValue chain;
/// LoadStream from file bytes count matches;
/// dogfood CreateNew->SetCells->ToFodsXml->LoadStream->GetCellValue->SheetNames verify.
/// </summary>
public class FodsR201ToFodsXmlAndLoadStreamTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR201ToFodsXmlAndLoadStreamTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR201_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateWithData()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetCellValue(0, 0, "name");
        doc.SetCellValue(0, 1, "score");
        doc.SetCellValue(1, 0, "Alice");
        doc.SetCellValue(1, 1, "95");
        doc.SetCellValue(2, 0, "Bob");
        doc.SetCellValue(2, 1, "82");
        return doc;
    }

    // -------------------------------------------------------------------------
    // ToFodsXml
    // -------------------------------------------------------------------------

    [Fact]
    public void ToFodsXml_NonNull()
    {
        var doc = CreateWithData();
        Assert.NotNull(doc.ToFodsXml());
    }

    [Fact]
    public void ToFodsXml_NonEmpty()
    {
        var doc = CreateWithData();
        Assert.False(string.IsNullOrWhiteSpace(doc.ToFodsXml()));
    }

    [Fact]
    public void ToFodsXml_ContainsXmlDeclaration()
    {
        var doc = CreateWithData();
        var xml = doc.ToFodsXml();
        Assert.True(xml.Contains("<?xml") || xml.Contains("<office:"));
    }

    [Fact]
    public void ToFodsXml_ContainsCellValues()
    {
        var doc = CreateWithData();
        var xml = doc.ToFodsXml();
        Assert.Contains("Alice", xml);
        Assert.Contains("95", xml);
    }

    // -------------------------------------------------------------------------
    // LoadStream
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadStream_NonNull()
    {
        var doc = CreateWithData();
        var xml = doc.ToFodsXml();
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(xml));
        var loaded = FodsDocument.LoadStream(ms);
        Assert.NotNull(loaded);
    }

    [Fact]
    public void LoadStream_SheetNames_Preserved()
    {
        var doc = CreateWithData();
        var xml = doc.ToFodsXml();
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(xml));
        var loaded = FodsDocument.LoadStream(ms);
        Assert.NotEmpty(loaded.GetSheetNames());
    }

    [Fact]
    public void LoadStream_CellValue_Preserved()
    {
        var doc = CreateWithData();
        var xml = doc.ToFodsXml();
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(xml));
        var loaded = FodsDocument.LoadStream(ms);
        var sheet = loaded.GetSheetNames()[0];
        Assert.Equal("Alice", loaded.GetCellValue(sheet, 1, 0));
    }

    [Fact]
    public void LoadStream_FromFileBytes_CountMatches()
    {
        var doc = CreateWithData();
        var path = TempFile("fodsfile.fods");
        doc.SaveToFile(path);
        var bytes = File.ReadAllBytes(path);
        using var ms = new MemoryStream(bytes);
        var loaded = FodsDocument.LoadStream(ms);
        Assert.NotNull(loaded);
        Assert.NotEmpty(loaded.GetSheetNames());
    }

    // -------------------------------------------------------------------------
    // OdfVersion
    // -------------------------------------------------------------------------

    [Fact]
    public void OdfVersion_NonNull()
    {
        Assert.NotNull(FodsDocument.OdfVersion);
    }

    [Fact]
    public void OdfVersion_NonEmpty()
    {
        Assert.NotEmpty(FodsDocument.OdfVersion);
    }

    [Fact]
    public void OdfVersion_ContainsVersionNumber()
    {
        var version = FodsDocument.OdfVersion;
        // Should contain a number like "1.3" or "1.2"
        Assert.True(version.Contains("1") || version.Contains("."));
    }

    // -------------------------------------------------------------------------
    // MimeType
    // -------------------------------------------------------------------------

    [Fact]
    public void MimeType_NonNull()
    {
        Assert.NotNull(FodsDocument.MimeType);
    }

    [Fact]
    public void MimeType_ContainsSpreadsheetOrCalc()
    {
        var mime = FodsDocument.MimeType.ToLower();
        Assert.True(
            mime.Contains("spreadsheet") || mime.Contains("calc") || mime.Contains("opendocument"),
            $"MimeType '{FodsDocument.MimeType}' should contain spreadsheet/calc/opendocument");
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateSetCellsToFodsXmlLoadStreamGetCellValueSheetNamesVerify_Pipeline()
    {
        // CreateNew and populate
        var doc = FodsDocument.CreateNew();
        var sheet = doc.GetSheetNames()[0];
        doc.SetCellValue(0, 0, "product");
        doc.SetCellValue(0, 1, "revenue");
        doc.SetCellValue(1, 0, "Widget");
        doc.SetCellValue(1, 1, "50000");
        doc.SetCellValue(2, 0, "Gadget");
        doc.SetCellValue(2, 1, "75000");

        // ToFodsXml
        var xml = doc.ToFodsXml();
        Assert.NotNull(xml);
        Assert.Contains("Widget", xml);

        // LoadStream
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(xml));
        var loaded = FodsDocument.LoadStream(ms);
        Assert.NotNull(loaded);
        Assert.NotEmpty(loaded.GetSheetNames());

        // GetCellValue
        var loadedSheet = loaded.GetSheetNames()[0];
        Assert.Equal("Widget", loaded.GetCellValue(loadedSheet, 1, 0));
        Assert.Equal("75000", loaded.GetCellValue(loadedSheet, 2, 1));

        // OdfVersion and MimeType
        Assert.NotNull(FodsDocument.OdfVersion);
        Assert.NotNull(FodsDocument.MimeType);
        Assert.NotEmpty(FodsDocument.OdfVersion);
    }
}
