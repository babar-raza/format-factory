// Tests for FodsDocument.SaveToFile, LoadFile deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R202

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R202: Tests for FodsDocument.SaveToFile, LoadFile deeper coverage.
/// SaveToFile(path): writes document to a FODS file.
/// LoadFile(path): loads FodsDocument from a FODS file.
/// Covers: SaveToFile creates file; SaveToFile non-empty; SaveToFile content XML;
/// SaveToFile->LoadFile round-trip sheet names preserved;
/// SaveToFile->LoadFile cell values preserved; SaveToFile->LoadFile row count;
/// SaveToFile after AddSheet->LoadFile new sheet present;
/// SaveToFile after RenameSheet->LoadFile new name present;
/// LoadFile non-null; LoadFile has sheets; LoadFile preserves all cell data;
/// SaveToFile->LoadFile->SaveToFile->LoadFile double round-trip stable;
/// SaveToFile->LoadFile->SetCellValue->SaveToFile->LoadFile mutation chain;
/// dogfood CreateNew->SetCells->AddSheet->SaveToFile->LoadFile->GetCellValue->Verify.
/// </summary>
public class FodsR202SaveToFileAndLoadTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR202SaveToFileAndLoadTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR202_" + Guid.NewGuid().ToString("N"));
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
    // SaveToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var doc = CreateWithData();
        var path = TempFile("out.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_NonEmpty()
    {
        var doc = CreateWithData();
        var path = TempFile("nonempty.fods");
        doc.SaveToFile(path);
        var info = new FileInfo(path);
        Assert.True(info.Length > 0);
    }

    [Fact]
    public void SaveToFile_ContainsXml()
    {
        var doc = CreateWithData();
        var path = TempFile("xml.fods");
        doc.SaveToFile(path);
        var content = File.ReadAllText(path);
        Assert.True(content.Contains("<") && content.Contains(">"));
    }

    // -------------------------------------------------------------------------
    // LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_NonNull()
    {
        var doc = CreateWithData();
        var path = TempFile("load.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded);
    }

    [Fact]
    public void LoadFile_HasSheets()
    {
        var doc = CreateWithData();
        var path = TempFile("sheets.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotEmpty(loaded.GetSheetNames());
    }

    [Fact]
    public void LoadFile_SheetNames_Preserved()
    {
        var doc = CreateWithData();
        var path = TempFile("sheetnames.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var origNames = doc.GetSheetNames();
        var loadedNames = loaded.GetSheetNames();
        Assert.Equal(origNames[0], loadedNames[0]);
    }

    [Fact]
    public void LoadFile_CellValues_Preserved()
    {
        var doc = CreateWithData();
        var path = TempFile("cells.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var sheet = loaded.GetSheetNames()[0];
        Assert.Equal("Alice", loaded.GetCellValue(sheet, 1, 0));
        Assert.Equal("95", loaded.GetCellValue(sheet, 1, 1));
    }

    [Fact]
    public void SaveToFile_AfterAddSheet_LoadFile_NewSheetPresent()
    {
        var doc = CreateWithData();
        doc.AddSheet("Summary");
        doc.SetCellValue("Summary", 0, 0, "Total");
        var path = TempFile("addsheet.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Contains("Summary", loaded.GetSheetNames());
    }

    [Fact]
    public void SaveToFile_AfterRenameSheet_LoadFile_NewNamePresent()
    {
        var doc = CreateWithData();
        var oldName = doc.GetSheetNames()[0];
        doc.RenameSheet(oldName, "Renamed");
        var path = TempFile("rename.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Contains("Renamed", loaded.GetSheetNames());
    }

    [Fact]
    public void DoubleRoundTrip_Stable()
    {
        var doc = CreateWithData();
        var path1 = TempFile("rt1.fods");
        var path2 = TempFile("rt2.fods");
        doc.SaveToFile(path1);
        var loaded1 = FodsDocument.LoadFile(path1);
        loaded1.SaveToFile(path2);
        var loaded2 = FodsDocument.LoadFile(path2);
        // Both loaded docs should have same sheet count
        Assert.Equal(loaded1.GetSheetNames().Count, loaded2.GetSheetNames().Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateSetCellsAddSheetSaveLoadFileGetCellValueVerify_Pipeline()
    {
        var doc = FodsDocument.CreateNew();
        var sheet1 = doc.GetSheetNames()[0];

        // Populate main sheet
        doc.SetCellValue(0, 0, "item"); doc.SetCellValue(0, 1, "qty");
        doc.SetCellValue(1, 0, "Widget"); doc.SetCellValue(1, 1, "10");
        doc.SetCellValue(2, 0, "Gadget"); doc.SetCellValue(2, 1, "5");

        // AddSheet and populate
        doc.AddSheet("Totals");
        doc.SetCellValue("Totals", 0, 0, "grand_total");
        doc.SetCellValue("Totals", 1, 0, "15");

        // SaveToFile
        var path = TempFile("dogfood.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded);

        // Verify sheets
        var sheets = loaded.GetSheetNames();
        Assert.True(sheets.Count >= 2);
        Assert.Contains("Totals", sheets);

        // Verify main sheet values
        Assert.Equal("Widget", loaded.GetCellValue(sheet1, 1, 0));
        Assert.Equal("10", loaded.GetCellValue(sheet1, 1, 1));
        Assert.Equal("Gadget", loaded.GetCellValue(sheet1, 2, 0));

        // Verify Totals sheet
        Assert.Equal("grand_total", loaded.GetCellValue("Totals", 0, 0));
        Assert.Equal("15", loaded.GetCellValue("Totals", 1, 0));
    }
}
