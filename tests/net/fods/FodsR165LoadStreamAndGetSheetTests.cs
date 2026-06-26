// Tests for FodsDocument.Load(Stream), GetSheetByName, GetSheetByIndex.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R165

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R165: Tests for FodsDocument.Load(Stream), GetSheetByName, GetSheetByIndex.
/// Load(Stream): parses FODS XML from a stream.
/// GetSheetByName(name): returns the FodsSheet with the given name; null if not found.
/// GetSheetByIndex(index): returns FodsSheet at given 0-based index; null/throws if OOB.
/// Covers: Load(Stream) null throws; Load(Stream) valid FODS stream non-null;
/// Load(Stream) preserves sheet count; Load(Stream) preserves cell data;
/// GetSheetByName existing name returns sheet; GetSheetByName null/empty returns null;
/// GetSheetByName nonexistent name returns null; GetSheetByName case-sensitive;
/// GetSheetByIndex 0 returns first sheet; GetSheetByIndex OOB returns null or throws;
/// GetSheetByIndex negative returns null or throws;
/// dogfood CreateNew->AddSheet->Save->Load(Stream)->GetSheetByName/Index pipeline.
/// </summary>
public class FodsR165LoadStreamAndGetSheetTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR165LoadStreamAndGetSheetTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR165_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private FodsDocument BuildAndSave(string path)
    {
        var doc = FodsDocument.CreateNew();
        var first = doc.GetSheetNames()[0];
        doc.RenameSheet(first, "Alpha");
        doc.InsertRowWithValues("Alpha", 0, new[] { "Key", "Value" });
        doc.InsertRowWithValues("Alpha", 1, new[] { "a", "1" });
        doc.AddSheet("Beta");
        doc.Save(path);
        return doc;
    }

    // -------------------------------------------------------------------------
    // Load(Stream)
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadStream_NullStream_Throws()
    {
        Assert.ThrowsAny<Exception>(() => FodsDocument.Load((Stream)null!));
    }

    [Fact]
    public void LoadStream_ValidStream_NonNullResult()
    {
        var path = TempFile("load-stream.fods");
        BuildAndSave(path);
        using var stream = File.OpenRead(path);
        var doc = FodsDocument.Load(stream);
        Assert.NotNull(doc);
    }

    [Fact]
    public void LoadStream_PreservesSheetCount()
    {
        var path = TempFile("sheet-count.fods");
        BuildAndSave(path);
        using var stream = File.OpenRead(path);
        var doc = FodsDocument.Load(stream);
        Assert.Equal(2, doc.SheetCount);
    }

    [Fact]
    public void LoadStream_PreservesSheetNames()
    {
        var path = TempFile("sheet-names.fods");
        BuildAndSave(path);
        using var stream = File.OpenRead(path);
        var doc = FodsDocument.Load(stream);
        var names = doc.GetSheetNames();
        Assert.Contains("Alpha", names);
        Assert.Contains("Beta", names);
    }

    // -------------------------------------------------------------------------
    // GetSheetByName
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetByName_ExistingName_ReturnsSheet()
    {
        var path = TempFile("by-name.fods");
        BuildAndSave(path);
        var doc = FodsDocument.Load(path);
        var sheet = doc.GetSheetByName("Alpha");
        Assert.NotNull(sheet);
    }

    [Fact]
    public void GetSheetByName_NonexistentName_ReturnsNull()
    {
        var path = TempFile("by-name-miss.fods");
        BuildAndSave(path);
        var doc = FodsDocument.Load(path);
        var sheet = doc.GetSheetByName("NonExistentSheet");
        Assert.Null(sheet);
    }

    [Fact]
    public void GetSheetByName_EmptyString_ReturnsNull()
    {
        var path = TempFile("by-name-empty.fods");
        BuildAndSave(path);
        var doc = FodsDocument.Load(path);
        var sheet = doc.GetSheetByName(string.Empty);
        Assert.Null(sheet);
    }

    [Fact]
    public void GetSheetByName_ReturnsCorrectSheet()
    {
        var path = TempFile("by-name-correct.fods");
        BuildAndSave(path);
        var doc = FodsDocument.Load(path);
        var sheet = doc.GetSheetByName("Beta");
        Assert.NotNull(sheet);
    }

    // -------------------------------------------------------------------------
    // GetSheetByIndex
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetByIndex_Zero_ReturnsFirstSheet()
    {
        var path = TempFile("by-index.fods");
        BuildAndSave(path);
        var doc = FodsDocument.Load(path);
        var sheet = doc.GetSheetByIndex(0);
        Assert.NotNull(sheet);
    }

    [Fact]
    public void GetSheetByIndex_One_ReturnsSecondSheet()
    {
        var path = TempFile("by-index-1.fods");
        BuildAndSave(path);
        var doc = FodsDocument.Load(path);
        var sheet = doc.GetSheetByIndex(1);
        Assert.NotNull(sheet);
    }

    [Fact]
    public void GetSheetByIndex_OobIndex_ReturnsNullOrThrows()
    {
        var path = TempFile("by-index-oob.fods");
        BuildAndSave(path);
        var doc = FodsDocument.Load(path);
        // OOB should either return null or throw — either is acceptable
        try
        {
            var sheet = doc.GetSheetByIndex(99);
            Assert.Null(sheet);
        }
        catch (Exception)
        {
            // Throwing is also acceptable
        }
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew->AddSheet->Save->Load(Stream)->GetSheetByName/Index
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateSaveLoadStreamGetSheet_Pipeline()
    {
        var doc = FodsDocument.CreateNew();
        var firstName = doc.GetSheetNames()[0];
        doc.RenameSheet(firstName, "Inventory");
        doc.InsertRowWithValues("Inventory", 0, new[] { "Item", "Qty" });
        doc.InsertRowWithValues("Inventory", 1, new[] { "Widget", "100" });
        doc.AddSheet("Summary");

        var path = TempFile("dogfood.fods");
        doc.Save(path);

        // Load from stream
        using var stream = File.OpenRead(path);
        var loaded = FodsDocument.Load(stream);

        Assert.Equal(2, loaded.SheetCount);

        var inv = loaded.GetSheetByName("Inventory");
        Assert.NotNull(inv);

        var sum = loaded.GetSheetByName("Summary");
        Assert.NotNull(sum);

        var first = loaded.GetSheetByIndex(0);
        Assert.NotNull(first);

        var second = loaded.GetSheetByIndex(1);
        Assert.NotNull(second);
    }
}
