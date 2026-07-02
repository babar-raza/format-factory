// Tests for FodsDocument.MimeType, OdfVersion, Load(Stream), GetSheetByIndex.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R178

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R178: Tests for FodsDocument.MimeType, OdfVersion, Load(Stream), GetSheetByIndex.
/// MimeType: returns ODF spreadsheet MIME type.
/// OdfVersion: returns ODF version string.
/// Load(Stream): loads from memory stream.
/// GetSheetByIndex(index): gets sheet by numeric index.
/// GetSheetByName(name): gets sheet by name.
/// Covers: MimeType is non-null; MimeType contains 'spreadsheet';
/// OdfVersion non-null; Load(Stream) returns document; Load(Stream) sheet count;
/// GetSheetByIndex 0 returns first sheet; GetSheetByIndex out-of-range returns null;
/// GetSheetByName valid returns sheet; GetSheetByName invalid returns null;
/// SheetCount positive; SheetCount after AddSheet; GetSheetNames count matches SheetCount;
/// Save then Load(Stream) round-trip; dogfood CreateNew->Save->Load(Stream)->verify.
/// </summary>
public class FodsR178MimeTypeAndStreamLoadTests : IDisposable
{
    private readonly string _tempDir;
    private static readonly string FodsFixturePath =
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "..", "..",
            "samples", "by-format", "fods", "valid", "two-sheets.fods");

    public FodsR178MimeTypeAndStreamLoadTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR178_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private FodsDocument LoadFixture()
    {
        var path = Path.GetFullPath(FodsFixturePath);
        if (!File.Exists(path))
        {
            // Fall back to a created doc if fixture doesn't exist
            var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
            return doc;
        }
        return FodsDocument.Load(path);
    }

    // -------------------------------------------------------------------------
    // MimeType
    // -------------------------------------------------------------------------

    [Fact]
    public void MimeType_IsNotNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.NotNull(doc.MimeType);
    }

    [Fact]
    public void MimeType_ContainsSpreadsheet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Contains("spreadsheet", doc.MimeType, StringComparison.OrdinalIgnoreCase);
    }

    // -------------------------------------------------------------------------
    // OdfVersion
    // -------------------------------------------------------------------------

    [Fact]
    public void OdfVersion_IsNotNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.NotNull(doc.OdfVersion);
    }

    [Fact]
    public void OdfVersion_IsNonEmpty()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.False(string.IsNullOrEmpty(doc.OdfVersion));
    }

    // -------------------------------------------------------------------------
    // Load(Stream)
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadStream_FromSavedFile_ReturnsDocument()
    {
        var orig = FodsDocument.CreateNew();
        orig.AddSheet("Sheet1");
        orig.InsertRowWithValues(
            orig.GetSheetNames()[0], 0, new[] { "Name", "Score" });

        var path = TempFile("saved.fods");
        orig.Save(path);

        using var stream = File.OpenRead(path);
        var doc = FodsDocument.Load(stream);
        Assert.NotNull(doc);
    }

    [Fact]
    public void LoadStream_SheetCountPositive()
    {
        var orig = FodsDocument.CreateNew();
        orig.AddSheet("Sheet1");
        var path = TempFile("sheets.fods");
        orig.Save(path);

        using var stream = File.OpenRead(path);
        var doc = FodsDocument.Load(stream);
        Assert.True(doc.SheetCount > 0);
    }

    // -------------------------------------------------------------------------
    // GetSheetByIndex
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetByIndex_Zero_ReturnsFirstSheet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.GetSheetByIndex(0);
        Assert.NotNull(sheet);
    }

    [Fact]
    public void GetSheetByIndex_OutOfRange_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.GetSheetByIndex(999);
        Assert.Null(sheet);
    }

    // -------------------------------------------------------------------------
    // GetSheetByName
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetByName_ValidName_ReturnsSheet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var firstName = doc.GetSheetNames()[0];
        var sheet = doc.GetSheetByName(firstName);
        Assert.NotNull(sheet);
    }

    [Fact]
    public void GetSheetByName_InvalidName_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.GetSheetByName("NoSuchSheet_XYZ");
        Assert.Null(sheet);
    }

    // -------------------------------------------------------------------------
    // SheetCount / GetSheetNames
    // -------------------------------------------------------------------------

    [Fact]
    public void SheetCount_PositiveForNewDoc()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.True(doc.SheetCount > 0);
    }

    [Fact]
    public void SheetCount_AfterAddSheet_Increases()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var before = doc.SheetCount;
        doc.AddSheet("NewSheet");
        Assert.Equal(before + 1, doc.SheetCount);
    }

    [Fact]
    public void GetSheetNames_CountMatchesSheetCount()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Extra");
        Assert.Equal(doc.SheetCount, doc.GetSheetNames().Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew->InsertRows->Save->Load(Stream)->verify
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateSaveLoadStreamVerify()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheetName = doc.GetSheetNames()[0];

        doc.InsertRowWithValues(sheetName, 0, new[] { "Product", "Qty", "Price" });
        doc.InsertRowWithValues(sheetName, 1, new[] { "Widget", "10", "9.99" });
        doc.InsertRowWithValues(sheetName, 2, new[] { "Gadget", "5", "19.99" });

        // Save and reload via stream
        var path = TempFile("dogfood.fods");
        doc.Save(path);

        using var stream = File.OpenRead(path);
        var reloaded = FodsDocument.Load(stream);

        // Verify
        Assert.NotNull(reloaded);
        Assert.True(reloaded.SheetCount > 0);

        // MimeType and OdfVersion accessible
        Assert.NotNull(reloaded.MimeType);
        Assert.NotNull(reloaded.OdfVersion);

        // Sheet accessible
        var sheet = reloaded.GetSheetByIndex(0);
        Assert.NotNull(sheet);
    }
}
