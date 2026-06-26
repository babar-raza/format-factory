// Tests for FodsDocument.InsertRow dedicated coverage.
// Sprint: ff-sprint-s187-dotnet-deepening-20260628
// Ledger: PC-FODS-R194

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R194: Dedicated tests for FodsDocument.InsertRow(string sheetName, int rowIndex).
/// Inserts an empty row at the specified index in the named sheet.
/// null/whitespace sheetName throws ArgumentException.
/// Nonexistent sheet throws InvalidOperationException.
/// Negative rowIndex throws ArgumentOutOfRangeException.
/// rowIndex > rowCount throws ArgumentOutOfRangeException.
/// Valid insert: GetRowCount increases by 1.
/// Insert at 0 shifts all existing rows down.
/// Insert at count appends to end.
/// Cell values in shifted rows are preserved.
/// Covers: null sheetName throws; whitespace sheetName throws;
/// nonexistent sheet throws; negative rowIndex throws; rowIndex > count throws;
/// valid insert increments row count; insert at 0 shifts existing rows;
/// insert at count appends; dogfood insert-then-verify row count;
/// dogfood insert preserves existing cell data.
/// </summary>
public class FodsR194InsertRowDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertRow_NullSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() => doc.InsertRow(null!, 0));
    }

    [Fact]
    public void InsertRow_WhitespaceSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() => doc.InsertRow("   ", 0));
    }

    [Fact]
    public void InsertRow_NonexistentSheet_ThrowsInvalidOperationException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<InvalidOperationException>(() => doc.InsertRow("NoSuchSheet", 0));
    }

    [Fact]
    public void InsertRow_NegativeRowIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        var sheetName = doc.Sheets[0].Name;
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.InsertRow(sheetName, -1));
    }

    [Fact]
    public void InsertRow_RowIndexAboveCount_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        var sheetName = doc.Sheets[0].Name;
        // No rows exist, so index > 0 is OOB
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.InsertRow(sheetName, 5));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertRow_ValidInsert_IncrementsRowCount()
    {
        var doc = FodsDocument.CreateNew();
        var sheetName = doc.Sheets[0].Name;
        doc.SetCellValue(0, 0, "A");
        var before = doc.GetRowCount(sheetName);
        doc.InsertRow(sheetName, 0);
        Assert.Equal(before + 1, doc.GetRowCount(sheetName));
    }

    [Fact]
    public void InsertRow_AtZero_ShiftsExistingRowsDown()
    {
        var doc = FodsDocument.CreateNew();
        var sheetName = doc.Sheets[0].Name;
        doc.SetCellValue(0, 0, "OriginalRow");
        doc.InsertRow(sheetName, 0);
        // Original row should now be at index 1
        Assert.Equal("OriginalRow", doc.GetCellValue(sheetName, 1, 0));
    }

    [Fact]
    public void InsertRow_AtCount_AppendsRow()
    {
        var doc = FodsDocument.CreateNew();
        var sheetName = doc.Sheets[0].Name;
        doc.SetCellValue(0, 0, "Existing");
        var count = doc.GetRowCount(sheetName);
        doc.InsertRow(sheetName, count); // append
        Assert.Equal(count + 1, doc.GetRowCount(sheetName));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_InsertThenVerify_RowCountIncremented()
    {
        var doc = FodsDocument.CreateNew();
        var sheetName = doc.Sheets[0].Name;
        doc.SetCellValue(0, 0, "Header");
        doc.SetCellValue(1, 0, "Data");
        var before = doc.GetRowCount(sheetName);
        doc.InsertRow(sheetName, 1); // insert between header and data
        Assert.Equal(before + 1, doc.GetRowCount(sheetName));
    }

    [Fact]
    public void DogfoodPipeline_InsertPreservesExistingCellData()
    {
        var doc = FodsDocument.CreateNew();
        var sheetName = doc.Sheets[0].Name;
        doc.SetCellValue(0, 0, "Row0Data");
        doc.InsertRow(sheetName, 0); // push existing to index 1
        Assert.Equal("Row0Data", doc.GetCellValue(sheetName, 1, 0));
    }
}
