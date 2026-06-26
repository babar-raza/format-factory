// Tests for FodsDocument.InsertRow dedicated coverage.
// Sprint: ff-sprint-s174-dotnet-deepening-20260628
// Ledger: PC-FODS-R181

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R181: Dedicated tests for FodsDocument.InsertRow(string sheetName, int rowIndex).
/// Inserts an empty row at the specified index, shifting existing rows down.
/// rowIndex 0..rowCount inclusive are valid.
/// Throws ArgumentException for null/whitespace sheetName.
/// Throws InvalidOperationException for nonexistent sheet.
/// Throws ArgumentOutOfRangeException for negative or beyond-count rowIndex.
/// Covers: null sheetName throws ArgumentException; whitespace sheetName throws;
/// nonexistent sheet throws InvalidOperationException;
/// negative rowIndex throws ArgumentOutOfRangeException;
/// rowIndex beyond count throws ArgumentOutOfRangeException;
/// valid insert at 0 increments row count; valid insert at count appends;
/// insert preserves existing cell values at shifted positions;
/// dogfood AddSheet->SetCells->InsertRow->GetRowCount; inserted row is empty.
/// </summary>
public class FodsR181InsertRowDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests — throws
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertRow_NullSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.Throws<ArgumentException>(() => doc.InsertRow(null!, 0));
    }

    [Fact]
    public void InsertRow_WhitespaceSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.Throws<ArgumentException>(() => doc.InsertRow("   ", 0));
    }

    [Fact]
    public void InsertRow_NonexistentSheet_ThrowsInvalidOperationException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.Throws<InvalidOperationException>(() => doc.InsertRow("NoSuchSheet", 0));
    }

    [Fact]
    public void InsertRow_NegativeRowIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "Header");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.InsertRow("Data", -1));
    }

    [Fact]
    public void InsertRow_RowIndexBeyondCount_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "Header"); // 1 row
        var count = doc.GetRowCount("Data");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.InsertRow("Data", count + 1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertRow_AtZero_IncrementsRowCount()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "Header");
        var before = doc.GetRowCount("Data");
        doc.InsertRow("Data", 0);
        Assert.Equal(before + 1, doc.GetRowCount("Data"));
    }

    [Fact]
    public void InsertRow_AtCount_AppendRow()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "Header");
        var count = doc.GetRowCount("Data");
        doc.InsertRow("Data", count); // insert at end
        Assert.Equal(count + 1, doc.GetRowCount("Data"));
    }

    [Fact]
    public void InsertRow_ShiftsExistingRows()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "Row0");
        doc.InsertRow("Data", 0); // insert before row 0
        // "Row0" should now be at row 1
        var vals = doc.GetRowValues("Data", 1);
        Assert.Contains("Row0", vals);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddSheet_SetCells_InsertRow_GetRowCount()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.SetCellValue(0, 0, "Header");
        doc.SetCellValue(1, 0, "Data1");
        doc.SetCellValue(2, 0, "Data2");
        var before = doc.GetRowCount("Report");
        doc.InsertRow("Report", 1); // insert after header
        Assert.Equal(before + 1, doc.GetRowCount("Report"));
    }

    [Fact]
    public void DogfoodPipeline_InsertedRow_IsEmpty()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "Header");
        doc.InsertRow("Data", 0);
        // Row 0 is now the newly inserted empty row
        var vals = doc.GetRowValues("Data", 0);
        Assert.True(vals.Count == 0 || vals.All(v => v == null || v == ""));
    }
}
