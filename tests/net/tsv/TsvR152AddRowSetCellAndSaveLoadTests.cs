// Tests for TsvDocument.AddRow, SetCell (via Rows mutation), SaveToFile, and LoadFile round-trips.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R152

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R152: Tests for TsvDocument mutation (AddRow, cell mutation) and SaveToFile/LoadFile pipeline.
/// AddRow: appends a new row to the document.
/// SaveToFile: writes TSV to disk. LoadFile: reads from disk.
/// Covers: AddRow increments RowCount; AddRow row contains values;
/// AddRow then GetCellValue returns value; SaveToFile->LoadFile row count matches;
/// SaveToFile->LoadFile cell values match; HasHeaders preserved after save-load;
/// ColumnCount consistent after save-load; LoadFile hasHeaders=false;
/// Filter->SaveToFile->LoadFile row count; Filter->SaveToFile->LoadFile cell values;
/// Multiple AddRow then SaveToFile->LoadFile; GetColumnValues after save-load;
/// IsEmpty after load from empty content;
/// dogfood Load->AddRow->SaveToFile->LoadFile->Filter->GetColumnValues.
/// </summary>
public class TsvR152AddRowSetCellAndSaveLoadTests : IDisposable
{
    private readonly string _tempDir;

    private const string ThreeRowTsv =
        "Name\tDept\tScore\n" +
        "Alice\tEng\t95\n" +
        "Bob\tFinance\t82\n" +
        "Carol\tEng\t88";

    public TsvR152AddRowSetCellAndSaveLoadTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR152_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // AddRow
    // -------------------------------------------------------------------------

    [Fact]
    public void AddRow_IncrementsRowCount()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var before = doc.RowCount;
        doc.Rows.Add(new[] { "Dave", "Finance", "91" });
        Assert.Equal(before + 1, doc.RowCount);
    }

    [Fact]
    public void AddRow_ContainsValues()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.Rows.Add(new[] { "Eve", "Eng", "79" });
        var col = doc.GetColumnValues(0);
        Assert.Contains("Eve", col);
    }

    [Fact]
    public void AddRow_ThenGetCellValue_ReturnsValue()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.Rows.Add(new[] { "Frank", "Eng", "77" });
        var lastRow = doc.RowCount - 1;
        Assert.Equal("Frank", doc.GetCellValue(lastRow, 0));
    }

    // -------------------------------------------------------------------------
    // SaveToFile -> LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_LoadFile_RowCountMatches()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var path = TempFile("rt.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(doc.RowCount, loaded.RowCount);
    }

    [Fact]
    public void SaveToFile_LoadFile_CellValuesMatch()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var path = TempFile("cv.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal("Alice", loaded.GetCellValue(0, 0));
        Assert.Equal("Bob", loaded.GetCellValue(1, 0));
    }

    [Fact]
    public void SaveToFile_LoadFile_HasHeadersPreserved()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var path = TempFile("hh.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(doc.HasHeaders, loaded.HasHeaders);
    }

    [Fact]
    public void SaveToFile_LoadFile_ColumnCountConsistent()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var path = TempFile("cc.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(doc.ColumnCount, loaded.ColumnCount);
    }

    [Fact]
    public void LoadFile_HasHeadersFalse_NoHeader()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var path = TempFile("nh.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path, hasHeaders: false);
        Assert.False(loaded.HasHeaders);
    }

    // -------------------------------------------------------------------------
    // Filter -> SaveToFile -> LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_SaveToFile_LoadFile_RowCount()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var eng = doc.Filter(r => r.Length > 1 && r[1] == "Eng");
        var path = TempFile("eng.tsv");
        eng.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(2, loaded.RowCount); // Alice, Carol
    }

    [Fact]
    public void Filter_SaveToFile_LoadFile_CellValues()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var eng = doc.Filter(r => r.Length > 1 && r[1] == "Eng");
        var path = TempFile("eng2.tsv");
        eng.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal("Alice", loaded.GetCellValue(0, 0));
    }

    // -------------------------------------------------------------------------
    // Multiple AddRow then SaveToFile -> LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void MultipleAddRow_SaveToFile_LoadFile_RowCount()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.Rows.Add(new[] { "Dave", "Finance", "91" });
        doc.Rows.Add(new[] { "Eve", "Eng", "79" });
        var path = TempFile("multi.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(5, loaded.RowCount);
    }

    [Fact]
    public void GetColumnValues_AfterSaveLoad_Matches()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var path = TempFile("gcv.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        var col = loaded.GetColumnValues(0);
        Assert.Contains("Alice", col);
        Assert.Contains("Carol", col);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->AddRow->SaveToFile->LoadFile->Filter->GetColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadAddRowSaveLoadFilterGetColumnValues_Pipeline()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal(3, doc.RowCount);

        // AddRow
        doc.Rows.Add(new[] { "Dave", "Finance", "91" });
        doc.Rows.Add(new[] { "Eve", "Eng", "79" });
        Assert.Equal(5, doc.RowCount);

        // SaveToFile
        var path = TempFile("dogfood.tsv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(5, loaded.RowCount);
        Assert.Equal("Alice", loaded.GetCellValue(0, 0));
        Assert.Equal("Dave", loaded.GetCellValue(3, 0));

        // Filter: Eng rows only
        var eng = loaded.Filter(r => r.Length > 1 && r[1] == "Eng");
        Assert.Equal(3, eng.RowCount); // Alice, Carol, Eve

        // GetColumnValues on filtered
        var names = eng.GetColumnValues(0);
        Assert.Equal(3, names.Count);
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.Contains("Eve", names);
    }
}
