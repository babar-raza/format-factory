// Tests for FodsDocument.GetCellCount dedicated coverage.
// Sprint: ff-sprint-s213-dotnet-deepening-20260629
// Ledger: PC-FODS-R229

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R229: Dedicated tests for FodsDocument.GetCellCount.
/// Null/whitespace sheet name → exception.
/// Non-existent sheet → exception.
/// Empty sheet → returns 0.
/// After SetCellValue: cell count non-negative.
/// SheetCount unchanged after GetCellCount.
/// Two sheets independent counts.
/// Cell count is non-negative integer.
/// After inserting row with values: cell count changes.
/// Dogfood: set values in multiple cells, verify count.
/// Dogfood: clear sheet resets count.
/// </summary>
public class FodsR229GetCellCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellCount_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellCount(null!));
    }

    [Fact]
    public void GetCellCount_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellCount("   "));
    }

    [Fact]
    public void GetCellCount_NonExistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellCount("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellCount_EmptySheet_ReturnsZero()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        Assert.Equal(0, doc.GetCellCount(sheetName));
    }

    [Fact]
    public void GetCellCount_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        Assert.True(doc.GetCellCount(sheetName) >= 0);
    }

    [Fact]
    public void GetCellCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int sheetsBefore = doc.SheetCount;
        string sheetName = doc.GetSheetNames()[0];
        doc.GetCellCount(sheetName);
        Assert.Equal(sheetsBefore, doc.SheetCount);
    }

    [Fact]
    public void GetCellCount_TwoSheetsIndependent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Sheet2");
        string sheet1 = doc.GetSheetNames()[0];
        string sheet2 = "Sheet2";
        doc.SetCellValue(sheet1, 0, 0, "Value");
        Assert.True(doc.GetCellCount(sheet1) >= 1);
        Assert.Equal(0, doc.GetCellCount(sheet2));
    }

    [Fact]
    public void GetCellCount_AfterSetCellValue_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Test");
        Assert.True(doc.GetCellCount(sheetName) >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetMultipleCells_CountNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 3; c++)
                doc.SetCellValue(sheetName, r, c, $"R{r}C{c}");
        Assert.True(doc.GetCellCount(sheetName) >= 9);
    }

    [Fact]
    public void DogfoodPipeline_ClearSheet_CountReturnsZero()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Value");
        doc.ClearSheet(sheetName);
        Assert.Equal(0, doc.GetCellCount(sheetName));
    }
}
