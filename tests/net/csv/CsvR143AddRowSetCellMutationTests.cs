// Tests for CsvDocument.AddRow, SetCell, RemoveRow mutation methods.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R143

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R143: Tests for CsvDocument.AddRow, SetCell, RemoveRow mutation methods.
/// AddRow(IEnumerable): appends a row; RowCount increases by 1.
/// SetCell(row, col, value): sets value at (row, col); GetCellValue reflects it.
/// RemoveRow(index): removes row at index; RowCount decreases; subsequent rows shift.
/// Covers: AddRow increases RowCount; AddRow accessible via GetCellValue;
/// AddRow multiple times; SetCell valid cell reflected; SetCell other cells unchanged;
/// SetCell last row; RemoveRow decreases RowCount; RemoveRow shifts subsequent rows;
/// RemoveRow first row; RemoveRow preserves other data; ToCsv after mutation includes changes;
/// dogfood Load->AddRow->SetCell->RemoveRow->ToCsv->Load pipeline.
/// </summary>
public class CsvR143AddRowSetCellMutationTests
{
    private const string TwoRowCsv =
        "Name,Score\n" +
        "Alice,95\n" +
        "Bob,82";

    // -------------------------------------------------------------------------
    // AddRow
    // -------------------------------------------------------------------------

    [Fact]
    public void AddRow_IncreasesRowCount()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        var before = doc.RowCount;
        doc.AddRow(new[] { "Carol", "88" });
        Assert.Equal(before + 1, doc.RowCount);
    }

    [Fact]
    public void AddRow_AccessibleViaGetCellValue()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        doc.AddRow(new[] { "Carol", "88" });
        Assert.Equal("Carol", doc.GetCellValue(doc.RowCount - 1, 0));
    }

    [Fact]
    public void AddRow_MultipleTimes_RowCountIncrements()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        var before = doc.RowCount;
        doc.AddRow(new[] { "Carol", "88" });
        doc.AddRow(new[] { "Dave", "91" });
        doc.AddRow(new[] { "Eve", "77" });
        Assert.Equal(before + 3, doc.RowCount);
    }

    [Fact]
    public void AddRow_WithList_Works()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        var row = new List<string> { "Frank", "66" };
        doc.AddRow(row);
        Assert.Equal("Frank", doc.GetCellValue(doc.RowCount - 1, 0));
    }

    // -------------------------------------------------------------------------
    // SetCell
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCell_ValidCell_ReflectedInGetCellValue()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        doc.SetCell(0, 0, "AliceUpdated");
        Assert.Equal("AliceUpdated", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void SetCell_DoesNotAffectOtherCells()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        doc.SetCell(0, 0, "NewName");
        Assert.Equal("95", doc.GetCellValue(0, 1)); // Score unchanged
        Assert.Equal("Bob", doc.GetCellValue(1, 0)); // Second row unchanged
    }

    [Fact]
    public void SetCell_SecondColumn_Works()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        doc.SetCell(1, 1, "100");
        Assert.Equal("100", doc.GetCellValue(1, 1));
    }

    [Fact]
    public void SetCell_AfterAddRow_Works()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        doc.AddRow(new[] { "Carol", "88" });
        doc.SetCell(doc.RowCount - 1, 1, "90");
        Assert.Equal("90", doc.GetCellValue(doc.RowCount - 1, 1));
    }

    // -------------------------------------------------------------------------
    // RemoveRow
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveRow_DecreasesRowCount()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        var before = doc.RowCount;
        doc.RemoveRow(0);
        Assert.Equal(before - 1, doc.RowCount);
    }

    [Fact]
    public void RemoveRow_FirstRow_SubsequentRowShiftsUp()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        doc.RemoveRow(0); // Remove Alice
        Assert.Equal("Bob", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void RemoveRow_LastRow_RowCountDecreases()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        doc.RemoveRow(doc.RowCount - 1);
        Assert.Equal(1, doc.RowCount);
        Assert.Equal("Alice", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void RemoveRow_MiddleRow_OtherRowsPreserved()
    {
        var csv = "Name,Score\nAlice,95\nBob,82\nCarol,88";
        var doc = CsvDocument.Load(csv);
        doc.RemoveRow(1); // Remove Bob
        Assert.Equal("Alice", doc.GetCellValue(0, 0));
        Assert.Equal("Carol", doc.GetCellValue(1, 0));
        Assert.Equal(2, doc.RowCount);
    }

    // -------------------------------------------------------------------------
    // ToCsv after mutation
    // -------------------------------------------------------------------------

    [Fact]
    public void ToCsv_AfterAddRow_IncludesNewData()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        doc.AddRow(new[] { "Dave", "99" });
        var csv = doc.ToCsv();
        Assert.Contains("Dave", csv);
        Assert.Contains("99", csv);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->AddRow->SetCell->RemoveRow->ToCsv->Load
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddSetRemoveToCsvLoad_Pipeline()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        Assert.Equal(2, doc.RowCount);

        // Add Carol
        doc.AddRow(new[] { "Carol", "88" });
        Assert.Equal(3, doc.RowCount);

        // Update Carol's score
        doc.SetCell(2, 1, "92");
        Assert.Equal("92", doc.GetCellValue(2, 1));

        // Remove Alice (index 0)
        doc.RemoveRow(0);
        Assert.Equal(2, doc.RowCount);
        Assert.Equal("Bob", doc.GetCellValue(0, 0));

        // Serialize and reload
        var csv = doc.ToCsv();
        Assert.Contains("Bob", csv);
        Assert.Contains("Carol", csv);
        Assert.DoesNotContain("Alice", csv);

        var reloaded = CsvDocument.Load(csv, hasHeaders: false);
        Assert.Equal(2, reloaded.RowCount);
    }
}
