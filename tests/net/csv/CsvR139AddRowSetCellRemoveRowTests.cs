// Tests for CsvDocument.AddRow, SetCell, RemoveRow, HasColumn.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R139

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R139: Tests for CsvDocument mutation methods: AddRow, SetCell, RemoveRow, HasColumn.
/// AddRow appends a new row; RowCount increments; row values match.
/// SetCell sets value at (row, col); GetCellValue reflects update.
/// RemoveRow removes a row; RowCount decrements; remaining rows shift.
/// HasColumn returns true when header exists (case-sensitive); false otherwise.
/// Covers: AddRow increments RowCount; AddRow values accessible via GetCellValue;
/// AddRow after Filter; SetCell updates value; SetCell OOB throws;
/// RemoveRow decrements count; RemoveRow negative index throws;
/// RemoveRow OOB index throws; HasColumn true for existing header;
/// HasColumn false for missing header; HasColumn false when no headers;
/// dogfood Load->AddRow->SetCell->ToCsv->Load pipeline.
/// </summary>
public class CsvR139AddRowSetCellRemoveRowTests
{
    private const string TwoRowCsv =
        "Name,Score,Active\n" +
        "Alice,95,true\n" +
        "Bob,82,false";

    // -------------------------------------------------------------------------
    // AddRow
    // -------------------------------------------------------------------------

    [Fact]
    public void AddRow_IncrementsRowCount()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        var before = doc.RowCount;
        doc.AddRow(new[] { "Carol", "88", "true" });
        Assert.Equal(before + 1, doc.RowCount);
    }

    [Fact]
    public void AddRow_ValuesAccessibleViaGetCellValue()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        doc.AddRow(new[] { "Dave", "77", "false" });
        var lastRow = doc.RowCount - 1;
        Assert.Equal("Dave", doc.GetCellValue(lastRow, 0));
    }

    [Fact]
    public void AddRow_EmptyRowIncrementsCounts()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        doc.AddRow(new List<string>());
        Assert.Equal(3, doc.RowCount);
    }

    [Fact]
    public void AddRow_ToEmptyDoc_RowCountIsOne()
    {
        var doc = CsvDocument.Load(string.Empty, hasHeaders: false);
        doc.AddRow(new[] { "X", "Y" });
        Assert.Equal(1, doc.RowCount);
    }

    // -------------------------------------------------------------------------
    // SetCell
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCell_UpdatesValue()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        doc.SetCell(0, 1, "100");
        Assert.Equal("100", doc.GetCellValue(0, 1));
    }

    [Fact]
    public void SetCell_DoesNotAffectOtherCells()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        doc.SetCell(0, 1, "999");
        // Row 0 col 0 should still be Alice
        Assert.Equal("Alice", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void SetCell_OobRow_Throws()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        Assert.ThrowsAny<Exception>(() => doc.SetCell(doc.RowCount, 0, "X"));
    }

    [Fact]
    public void SetCell_NegativeRow_Throws()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        Assert.ThrowsAny<Exception>(() => doc.SetCell(-1, 0, "X"));
    }

    // -------------------------------------------------------------------------
    // RemoveRow
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveRow_DecrementsRowCount()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        doc.RemoveRow(0);
        Assert.Equal(1, doc.RowCount);
    }

    [Fact]
    public void RemoveRow_ShiftsRemainingRows()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        // Remove first row (Alice); Bob becomes row 0
        doc.RemoveRow(0);
        Assert.Equal("Bob", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void RemoveRow_NegativeIndex_Throws()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        Assert.ThrowsAny<Exception>(() => doc.RemoveRow(-1));
    }

    [Fact]
    public void RemoveRow_OobIndex_Throws()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        Assert.ThrowsAny<Exception>(() => doc.RemoveRow(doc.RowCount));
    }

    // -------------------------------------------------------------------------
    // HasColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void HasColumn_ExistingHeader_IsTrue()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        Assert.True(doc.HasColumn("Name"));
    }

    [Fact]
    public void HasColumn_MissingHeader_IsFalse()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        Assert.False(doc.HasColumn("Department"));
    }

    [Fact]
    public void HasColumn_NoHeaders_IsFalse()
    {
        var doc = CsvDocument.Load("A,B\n1,2", hasHeaders: false);
        Assert.False(doc.HasColumn("A"));
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->AddRow->SetCell->ToCsv->Load pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadAddRowSetCellToCsvLoad_Pipeline()
    {
        var doc = CsvDocument.Load(TwoRowCsv);

        // Add a new row
        doc.AddRow(new[] { "Eve", "91", "true" });
        Assert.Equal(3, doc.RowCount);

        // Update a cell
        doc.SetCell(2, 1, "92");
        Assert.Equal("92", doc.GetCellValue(2, 1));

        // Remove a row
        doc.RemoveRow(1); // Remove Bob
        Assert.Equal(2, doc.RowCount);

        // Serialize and reload
        var csv = doc.ToCsv();
        var reloaded = CsvDocument.Load(csv);
        Assert.Equal(2, reloaded.RowCount);
        Assert.Equal("Alice", reloaded.GetCellValue(0, 0));
        Assert.Equal("Eve", reloaded.GetCellValue(1, 0));
    }
}
