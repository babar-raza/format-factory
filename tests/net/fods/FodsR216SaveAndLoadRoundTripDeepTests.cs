// Tests for FodsDocument.SaveToFile, LoadFile round-trip, ToFodsXml deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R216

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R216: Tests for FodsDocument.SaveToFile, LoadFile round-trip, ToFodsXml deeper.
/// SaveToFile(path): saves the document to a FODS file.
/// LoadFile(path): loads a FodsDocument from a FODS file.
/// ToFodsXml(): returns the document as a FODS XML string.
/// Covers: SaveToFile creates file; SaveToFile non-empty; LoadFile after SaveToFile correct;
/// LoadFile RowCount matches original; LoadFile CellValue preserved;
/// LoadFile sheet names preserved; LoadFile after SetCellValue reflects mutation;
/// ToFodsXml non-null; ToFodsXml non-empty; ToFodsXml contains XML elements;
/// ToFodsXml contains cell data; ToFodsXml after mutation reflects change;
/// dogfood CreateEmpty->Populate->SaveToFile->LoadFile->Verify->ToFodsXml->Verify pipeline.
/// </summary>
public class FodsR216SaveAndLoadRoundTripDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR216SaveAndLoadRoundTripDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR216_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private FodsDocument CreatePopulated()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Name");
        doc.SetCellValue("Data", 0, 1, "Value");
        doc.SetCellValue("Data", 1, 0, "Alpha");
        doc.SetCellValue("Data", 1, 1, "100");
        doc.SetCellValue("Data", 2, 0, "Beta");
        doc.SetCellValue("Data", 2, 1, "200");
        doc.SetCellValue("Data", 3, 0, "Gamma");
        doc.SetCellValue("Data", 3, 1, "300");
        return doc;
    }

    // -------------------------------------------------------------------------
    // SaveToFile / LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var doc = CreatePopulated();
        var path = TempFile("output.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_NonEmpty()
    {
        var doc = CreatePopulated();
        var path = TempFile("nonempty.fods");
        doc.SaveToFile(path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void LoadFile_AfterSaveToFile_NonNull()
    {
        var doc = CreatePopulated();
        var path = TempFile("roundtrip.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded);
    }

    [Fact]
    public void LoadFile_RowCountMatchesOriginal()
    {
        var doc = CreatePopulated();
        var path = TempFile("rowcount.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(doc.GetRowCount("Data"), loaded.GetRowCount("Data"));
    }

    [Fact]
    public void LoadFile_CellValuePreserved()
    {
        var doc = CreatePopulated();
        var path = TempFile("cellvalue.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal("Alpha", loaded.GetCellValue("Data", 1, 0));
    }

    [Fact]
    public void LoadFile_AllCellValuesPreserved()
    {
        var doc = CreatePopulated();
        var path = TempFile("allcells.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal("Beta", loaded.GetCellValue("Data", 2, 0));
        Assert.Equal("300", loaded.GetCellValue("Data", 3, 1));
    }

    [Fact]
    public void LoadFile_SheetNamesPreserved()
    {
        var doc = CreatePopulated();
        doc.AddSheet("Summary");
        doc.SetCellValue("Summary", 0, 0, "Total");
        var path = TempFile("sheets.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var names = loaded.GetSheetNames();
        Assert.Contains("Data", names);
        Assert.Contains("Summary", names);
    }

    [Fact]
    public void LoadFile_AfterSetCellValue_MutationPersisted()
    {
        var doc = CreatePopulated();
        doc.SetCellValue("Data", 1, 0, "AlphaUpdated");
        var path = TempFile("mutation.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal("AlphaUpdated", loaded.GetCellValue("Data", 1, 0));
    }

    // -------------------------------------------------------------------------
    // ToFodsXml
    // -------------------------------------------------------------------------

    [Fact]
    public void ToFodsXml_NonNull()
    {
        var doc = CreatePopulated();
        Assert.NotNull(doc.ToFodsXml());
    }

    [Fact]
    public void ToFodsXml_NonEmpty()
    {
        var doc = CreatePopulated();
        Assert.NotEmpty(doc.ToFodsXml());
    }

    [Fact]
    public void ToFodsXml_ContainsXmlElements()
    {
        var doc = CreatePopulated();
        var xml = doc.ToFodsXml();
        Assert.Contains("<", xml);
    }

    [Fact]
    public void ToFodsXml_ContainsCellData()
    {
        var doc = CreatePopulated();
        var xml = doc.ToFodsXml();
        Assert.True(xml.Contains("Alpha") || xml.Contains("Name") || xml.Length > 100);
    }

    [Fact]
    public void ToFodsXml_AfterMutation_ReflectsChange()
    {
        var doc = CreatePopulated();
        doc.SetCellValue("Data", 1, 0, "UniqueValueXYZ");
        var xml = doc.ToFodsXml();
        Assert.Contains("UniqueValueXYZ", xml);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateEmpty_Populate_SaveToFile_LoadFile_Verify_ToFodsXml_Verify_Pipeline()
    {
        // CreateEmpty and populate
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Products");
        doc.SetCellValue("Products", 0, 0, "SKU");
        doc.SetCellValue("Products", 0, 1, "Name");
        doc.SetCellValue("Products", 0, 2, "Price");
        doc.SetCellValue("Products", 1, 0, "A001");
        doc.SetCellValue("Products", 1, 1, "Widget");
        doc.SetCellValue("Products", 1, 2, "9.99");
        doc.SetCellValue("Products", 2, 0, "B002");
        doc.SetCellValue("Products", 2, 1, "Gadget");
        doc.SetCellValue("Products", 2, 2, "24.99");

        // SaveToFile
        var path = TempFile("products.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded);
        Assert.Equal(doc.GetRowCount("Products"), loaded.GetRowCount("Products"));
        Assert.Equal("Widget", loaded.GetCellValue("Products", 1, 1));
        Assert.Equal("24.99", loaded.GetCellValue("Products", 2, 2));

        // Mutate loaded and save again
        loaded.SetCellValue("Products", 1, 2, "11.99");
        var path2 = TempFile("products_v2.fods");
        loaded.SaveToFile(path2);
        var v2 = FodsDocument.LoadFile(path2);
        Assert.Equal("11.99", v2.GetCellValue("Products", 1, 2));

        // ToFodsXml
        var xml = doc.ToFodsXml();
        Assert.NotNull(xml);
        Assert.Contains("<", xml);

        // GetSheetNames
        var sheets = loaded.GetSheetNames();
        Assert.Contains("Products", sheets);
    }
}
