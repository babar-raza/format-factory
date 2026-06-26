// Tests for CsvDocument.Filter + SaveToFile + LoadFile pipeline, and IsEmpty edge cases.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R154

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R154: Tests for CsvDocument.Filter -> SaveToFile -> LoadFile round-trip.
/// Filter: produces subset document; SaveToFile: writes CSV to disk; LoadFile: reads from disk.
/// Covers: Filter->SaveToFile->LoadFile count matches; Filter->SaveToFile->LoadFile cell values;
/// Filter-none->IsEmpty after SaveLoad; Filter-all->SaveToFile->LoadFile row count;
/// LoadFile hasHeaders=false uses no header; HasColumn after save-load round-trip;
/// GetColumn after save-load; ColumnCount after save-load; SaveToFile->LoadFile headers;
/// Filter->SaveToFile->LoadFile->GetColumn; AddRow->SaveToFile->LoadFile->RowCount;
/// SetCell->SaveToFile->LoadFile->GetCellValue; RemoveRow->SaveToFile->LoadFile->RowCount;
/// dogfood Filter->SaveToFile->LoadFile->Filter->GetColumn pipeline.
/// </summary>
public class CsvR154FilterSaveAndLoadFileTests : IDisposable
{
    private readonly string _tempDir;

    private const string FiveRowCsv =
        "Name,Dept,Score\n" +
        "Alice,Eng,95\n" +
        "Bob,Finance,82\n" +
        "Carol,Eng,88\n" +
        "Dave,Finance,91\n" +
        "Eve,Eng,79";

    public CsvR154FilterSaveAndLoadFileTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR154_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // Filter -> SaveToFile -> LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_SaveToFile_LoadFile_CountMatches()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var eng = doc.Filter(r => r.Length > 1 && r[1] == "Eng");
        var path = TempFile("eng.csv");
        eng.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(3, loaded.RowCount); // Alice, Carol, Eve
    }

    [Fact]
    public void Filter_SaveToFile_LoadFile_CellValues()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var finance = doc.Filter(r => r.Length > 1 && r[1] == "Finance");
        var path = TempFile("finance.csv");
        finance.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal("Bob", loaded.GetCellValue(0, 0));
        Assert.Equal("Dave", loaded.GetCellValue(1, 0));
    }

    [Fact]
    public void Filter_None_SaveToFile_LoadFile_IsEmpty()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var none = doc.Filter(_ => false);
        var path = TempFile("none.csv");
        none.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.True(loaded.IsEmpty);
    }

    [Fact]
    public void Filter_All_SaveToFile_LoadFile_RowCountUnchanged()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var all = doc.Filter(_ => true);
        var path = TempFile("all.csv");
        all.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(doc.RowCount, loaded.RowCount);
    }

    // -------------------------------------------------------------------------
    // LoadFile hasHeaders=false
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_HasHeadersFalse_NoHeaderRow()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var path = TempFile("noheader.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path, hasHeaders: false);
        Assert.False(loaded.HasHeaders);
    }

    // -------------------------------------------------------------------------
    // HasColumn + GetColumn after save-load
    // -------------------------------------------------------------------------

    [Fact]
    public void HasColumn_AfterSaveLoadRoundTrip_True()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var path = TempFile("rt.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.True(loaded.HasColumn("Dept"));
    }

    [Fact]
    public void GetColumn_AfterSaveLoad_ContainsValues()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var path = TempFile("gc.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        var col = loaded.GetColumn("Name");
        Assert.Contains("Alice", col);
        Assert.Contains("Bob", col);
    }

    [Fact]
    public void ColumnCount_AfterSaveLoad_Unchanged()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var path = TempFile("cc.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(doc.ColumnCount, loaded.ColumnCount);
    }

    // -------------------------------------------------------------------------
    // Mutation -> SaveToFile -> LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void AddRow_SaveToFile_LoadFile_RowCount()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        doc.AddRow(new[] { "Frank", "Eng", "77" });
        var path = TempFile("addrow.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(6, loaded.RowCount);
    }

    [Fact]
    public void SetCell_SaveToFile_LoadFile_GetCellValue()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        doc.SetCell(0, 2, "100");
        var path = TempFile("setcell.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal("100", loaded.GetCellValue(0, 2));
    }

    [Fact]
    public void RemoveRow_SaveToFile_LoadFile_RowCount()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        doc.RemoveRow(0);
        var path = TempFile("removerow.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(4, loaded.RowCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Filter->SaveToFile->LoadFile->Filter->GetColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_FilterSaveLoadFilterGetColumn_Pipeline()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        Assert.Equal(5, doc.RowCount);

        // First filter: Eng department
        var eng = doc.Filter(r => r.Length > 1 && r[1] == "Eng");
        Assert.Equal(3, eng.RowCount);

        // Save and reload
        var path = TempFile("dogfood.csv");
        eng.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(3, loaded.RowCount);
        Assert.True(loaded.HasHeaders);

        // Second filter: score >= 85
        var highEng = loaded.Filter(r => r.Length > 2 && int.TryParse(r[2], out var s) && s >= 85);
        Assert.Equal(2, highEng.RowCount); // Alice=95, Carol=88

        // GetColumn on final result
        var names = highEng.GetColumn("Name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Eve", names);
    }
}
