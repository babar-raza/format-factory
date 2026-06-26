// Tests for FodsDocument.SetCellNumberFormat dedicated coverage.
// Sprint: ff-sprint-s278-dotnet-deepening-20260630
// Ledger: PC-FODS-R306

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R306: Dedicated tests for FodsDocument.SetCellNumberFormat(sheetName, row, col, format).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet name throws exception.
/// Negative row throws exception.
/// Negative col throws exception.
/// Valid currency format no exception.
/// Valid percentage format no exception.
/// SheetCount unchanged after SetCellNumberFormat.
/// Set twice no exception.
/// Dogfood: set format on multiple cells no exception.
/// </summary>
public class FodsR306SetCellNumberFormatDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellNumberFormat_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetCellNumberFormat(null!, 0, 0, "#,##0.00"));
    }

    [Fact]
    public void SetCellNumberFormat_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetCellNumberFormat("   ", 0, 0, "#,##0.00"));
    }

    [Fact]
    public void SetCellNumberFormat_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetCellNumberFormat("NoSuchSheet", 0, 0, "#,##0.00"));
    }

    [Fact]
    public void SetCellNumberFormat_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellNumberFormat("Sheet1", -1, 0, "#,##0.00"));
    }

    [Fact]
    public void SetCellNumberFormat_NegativeCol_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellNumberFormat("Sheet1", 0, -1, "#,##0.00"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellNumberFormat_CurrencyFormat_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var ex = Record.Exception(() => doc.SetCellNumberFormat("Sheet1", 0, 0, "#,##0.00"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellNumberFormat_PercentageFormat_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var ex = Record.Exception(() => doc.SetCellNumberFormat("Sheet1", 0, 0, "0.00%"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellNumberFormat_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        doc.SetCellNumberFormat("Sheet1", 0, 0, "0.00");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SetCellNumberFormat_SetTwice_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellNumberFormat("Sheet1", 0, 0, "#,##0.00");
        var ex = Record.Exception(() => doc.SetCellNumberFormat("Sheet1", 0, 0, "0%"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetFormatOnMultipleCells_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Financials");
        var ex = Record.Exception(() =>
        {
            doc.SetCellNumberFormat("Financials", 0, 0, "#,##0.00");
            doc.SetCellNumberFormat("Financials", 0, 1, "0.00%");
            doc.SetCellNumberFormat("Financials", 1, 0, "0");
            doc.SetCellValue("Financials", 0, 0, "1234.56");
        });
        Assert.Null(ex);
    }
}
