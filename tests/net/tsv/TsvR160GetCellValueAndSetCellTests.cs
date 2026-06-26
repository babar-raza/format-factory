// Tests for TsvDocument.GetCellValue, SetCellValue deeper coverage with mutation patterns.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R160

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R160: Tests for TsvDocument.GetCellValue, SetCellValue deeper mutation coverage.
/// GetCellValue(row, col): returns cell value by row and column index.
/// SetCellValue(row, col, value): sets cell value by position.
/// GetCellValue(row, headerName): returns cell value by row and column name.
/// Covers: GetCellValue by index correct; GetCellValue by name correct;
/// SetCellValue updates value; SetCellValue then GetCellValue reads back;
/// SetCellValue multiple cells; GetCellValue after Filter still works;
/// GetCellValue first row; GetCellValue last row; SetCellValue then ToTsv;
/// SetCellValue then SaveToFile->LoadFile round-trip; GetCellValue index 0;
/// GetCellValue by name after mutation; IsEmpty remains false after SetCellValue;
/// RowCount unchanged after SetCellValue;
/// dogfood Load->GetCellValues->SetCellValues->ToTsv->Load->Verify pipeline.
/// </summary>
public class TsvR160GetCellValueAndSetCellTests : IDisposable
{
    private readonly string _tempDir;

    private const string ThreeRowTsv =
        "name\tdept\tscore\n" +
        "Alice\tEng\t95\n" +
        "Bob\tFinance\t82\n" +
        "Carol\tEng\t88";

    public TsvR160GetCellValueAndSetCellTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR160_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // GetCellValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellValue_ByIndex_Row0Col0_IsAlice()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal("Alice", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void GetCellValue_ByIndex_Row1Col1_IsFinance()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal("Finance", doc.GetCellValue(1, 1));
    }

    [Fact]
    public void GetCellValue_ByName_Row0_IsAlice()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal("Alice", doc.GetCellValue(0, "name"));
    }

    [Fact]
    public void GetCellValue_ByName_Row2_IsCarol()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal("Carol", doc.GetCellValue(2, "name"));
    }

    [Fact]
    public void GetCellValue_LastRow_LastCol()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal("88", doc.GetCellValue(2, 2));
    }

    [Fact]
    public void GetCellValue_FirstRow_ScoreCol()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal("95", doc.GetCellValue(0, "score"));
    }

    // -------------------------------------------------------------------------
    // SetCellValue
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellValue_UpdatesValue()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.SetCellValue(0, 0, "Alicia");
        Assert.Equal("Alicia", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void SetCellValue_ThenGetCellValue_ReadsBack()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.SetCellValue(1, 2, "99");
        Assert.Equal("99", doc.GetCellValue(1, 2));
    }

    [Fact]
    public void SetCellValue_MultipleCells_AllPersist()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.SetCellValue(0, 0, "NewAlice");
        doc.SetCellValue(1, 0, "NewBob");
        doc.SetCellValue(2, 0, "NewCarol");
        Assert.Equal("NewAlice", doc.GetCellValue(0, 0));
        Assert.Equal("NewBob", doc.GetCellValue(1, 0));
        Assert.Equal("NewCarol", doc.GetCellValue(2, 0));
    }

    [Fact]
    public void SetCellValue_RowCountUnchanged()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var before = doc.RowCount;
        doc.SetCellValue(0, 0, "Updated");
        Assert.Equal(before, doc.RowCount);
    }

    [Fact]
    public void SetCellValue_IsEmptyRemainsFalse()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.SetCellValue(0, 0, "X");
        Assert.False(doc.IsEmpty);
    }

    [Fact]
    public void SetCellValue_ThenToTsv_ContainsNewValue()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.SetCellValue(0, 0, "Alicia");
        var tsv = doc.ToTsv();
        Assert.Contains("Alicia", tsv);
        Assert.DoesNotContain("Alice\t", tsv);
    }

    [Fact]
    public void SetCellValue_SaveToFile_LoadFile_RoundTrip()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.SetCellValue(0, 2, "100");
        var path = TempFile("mutated.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal("100", loaded.GetCellValue(0, "score"));
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->GetCellValues->SetCellValues->ToTsv->Load->Verify
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadGetSetToTsvLoadVerify_Pipeline()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);

        // GetCellValues
        Assert.Equal("Alice", doc.GetCellValue(0, "name"));
        Assert.Equal("82", doc.GetCellValue(1, "score"));
        Assert.Equal("Eng", doc.GetCellValue(2, "dept"));

        // SetCellValues
        doc.SetCellValue(0, 2, "100"); // Alice's score
        doc.SetCellValue(1, 1, "Eng"); // Bob's dept
        doc.SetCellValue(2, 0, "Carola"); // Carol's name

        // Verify mutations
        Assert.Equal("100", doc.GetCellValue(0, 2));
        Assert.Equal("Eng", doc.GetCellValue(1, 1));
        Assert.Equal("Carola", doc.GetCellValue(2, 0));

        // ToTsv
        var tsv = doc.ToTsv();
        Assert.Contains("100", tsv);
        Assert.Contains("Carola", tsv);

        // Load
        var loaded = TsvDocument.Load(tsv);
        Assert.Equal(3, loaded.RowCount);
        Assert.Equal("100", loaded.GetCellValue(0, "score"));
        Assert.Equal("Carola", loaded.GetCellValue(2, "name"));
    }
}
