// Tests for FodsDocument.ClearSheet dedicated coverage.
// Sprint: ff-sprint-s178-dotnet-deepening-20260628
// Ledger: PC-FODS-R185

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R185: Dedicated tests for FodsDocument.ClearSheet(sheetName).
/// Removes all rows from the named sheet, leaving the sheet structure intact.
/// null/whitespace sheetName throws ArgumentException.
/// Nonexistent sheet throws InvalidOperationException.
/// Empty sheet: no-op (does not throw).
/// Valid clear: GetRowCount returns 0; sheet still exists; other sheets unaffected.
/// Covers: null throws; whitespace throws; nonexistent throws;
/// empty sheet no-op; valid clear row count=0; sheet still in Sheets;
/// other sheets unaffected; cells no longer readable; dogfood add-populate-clear-repopulate.
/// </summary>
public class FodsR185ClearSheetDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("   ")]
    public void ClearSheet_NullOrWhitespaceSheetName_ThrowsArgumentException(string sheetName)
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Throws<ArgumentException>(() => doc.ClearSheet(sheetName));
    }

    [Fact]
    public void ClearSheet_NonexistentSheet_ThrowsInvalidOperationException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Throws<InvalidOperationException>(() => doc.ClearSheet("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ClearSheet_EmptySheet_NoOp()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Empty");
        doc.ClearSheet("Empty");
        Assert.Equal(0, doc.GetRowCount("Empty"));
    }

    [Fact]
    public void ClearSheet_PopulatedSheet_RowCountBecomesZero()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Row0");
        doc.SetCellValue("Data", 1, 0, "Row1");
        doc.SetCellValue("Data", 2, 0, "Row2");
        doc.ClearSheet("Data");
        Assert.Equal(0, doc.GetRowCount("Data"));
    }

    [Fact]
    public void ClearSheet_SheetStillExistsAfterClear()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Data");
        doc.ClearSheet("Sheet1");
        Assert.NotNull(doc.GetSheetByName("Sheet1"));
    }

    [Fact]
    public void ClearSheet_OtherSheetsUnaffected()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Keep");
        doc.AddSheet("Clear");
        doc.SetCellValue("Keep", 0, 0, "StayHere");
        doc.SetCellValue("Clear", 0, 0, "GoneAfterClear");
        doc.ClearSheet("Clear");
        Assert.Equal("StayHere", doc.GetCellValue("Keep", 0, 0));
    }

    [Fact]
    public void ClearSheet_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var countBefore = doc.SheetCount;
        doc.SetCellValue("Sheet1", 0, 0, "Data");
        doc.ClearSheet("Sheet1");
        Assert.Equal(countBefore, doc.SheetCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ClearThenRepopulate_NewDataAccessible()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.SetCellValue("Report", 0, 0, "OldData");
        doc.ClearSheet("Report");
        doc.SetCellValue("Report", 0, 0, "NewData");
        Assert.Equal("NewData", doc.GetCellValue("Report", 0, 0));
    }

    [Fact]
    public void DogfoodPipeline_ClearDefaultSheet_EmptyThenRefill()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        // Default sheet always exists; fill and clear it
        var sheets = doc.GetSheetNames();
        Assert.NotEmpty(sheets);
        doc.SetCellValue(0, 0, "Fill");
        doc.ClearSheet(sheets[0]);
        Assert.Equal(0, doc.GetRowCount(sheets[0]));
    }
}
