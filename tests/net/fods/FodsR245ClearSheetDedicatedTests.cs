// Tests for FodsDocument.ClearSheet dedicated coverage.
// Sprint: ff-sprint-s227-dotnet-deepening-20260629
// Ledger: PC-FODS-R245

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R245: Dedicated tests for FodsDocument.ClearSheet(sheetName).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet → throws exception.
/// Empty sheet clear → no exception.
/// After clear: row count is 0.
/// After clear: cell count is 0.
/// SheetCount unchanged after clear.
/// Data not accessible after clear.
/// Second sheet unaffected by clear of first.
/// Dogfood: add data, clear, verify empty.
/// </summary>
public class FodsR245ClearSheetDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ClearSheet_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.ClearSheet(null!));
    }

    [Fact]
    public void ClearSheet_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.ClearSheet("   "));
    }

    [Fact]
    public void ClearSheet_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.ClearSheet("Ghost"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ClearSheet_EmptySheet_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        var ex = Record.Exception(() => doc.ClearSheet(sheetName));
        Assert.Null(ex);
    }

    [Fact]
    public void ClearSheet_AfterClear_RowCountIsZero()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "A", "B" });
        doc.AddRow(sheetName, new[] { "C", "D" });
        doc.ClearSheet(sheetName);
        Assert.Equal(0, doc.GetRowCount(sheetName));
    }

    [Fact]
    public void ClearSheet_AfterClear_CellCountIsZero()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Value");
        doc.ClearSheet(sheetName);
        Assert.Equal(0, doc.GetCellCount(sheetName));
    }

    [Fact]
    public void ClearSheet_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetNames()[0];
        doc.ClearSheet(sheetName);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void ClearSheet_SecondSheetUnaffected()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("SecondSheet");
        string sheet1 = doc.GetSheetNames()[0];
        doc.SetCellValue(sheet1, 0, 0, "Sheet1Data");
        doc.SetCellValue("SecondSheet", 0, 0, "Sheet2Data");
        doc.ClearSheet(sheet1);
        // Sheet2 data should still be there
        var v = doc.GetCellValue("SecondSheet", 0, 0);
        Assert.Equal("Sheet2Data", v);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddDataClearVerifyEmpty()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Val1");
        doc.SetCellValue(sheetName, 1, 0, "Val2");
        doc.SetCellValue(sheetName, 2, 0, "Val3");
        doc.ClearSheet(sheetName);
        Assert.Equal(0, doc.GetRowCount(sheetName));
        Assert.Equal(0, doc.GetCellCount(sheetName));
    }
}
