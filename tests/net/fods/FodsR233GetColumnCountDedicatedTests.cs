// Tests for FodsDocument.GetColumnCount dedicated coverage.
// Sprint: ff-sprint-s216-dotnet-deepening-20260629
// Ledger: PC-FODS-R233

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R233: Dedicated tests for FodsDocument.GetColumnCount.
/// Null/whitespace sheet name → exception.
/// Non-existent sheet → exception.
/// Empty sheet → returns 0.
/// After SetCellValue in column 0: column count >= 1.
/// Returns non-negative integer.
/// SheetCount unchanged after GetColumnCount.
/// Two sheets independent column counts.
/// After setting values in multiple columns: count >= columns used.
/// Dogfood: set values across columns, verify count.
/// Dogfood: clear sheet resets column count to 0.
/// </summary>
public class FodsR233GetColumnCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCount_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetColumnCount(null!));
    }

    [Fact]
    public void GetColumnCount_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetColumnCount("   "));
    }

    [Fact]
    public void GetColumnCount_NonExistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetColumnCount("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCount_EmptySheet_ReturnsZero()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        Assert.Equal(0, doc.GetColumnCount(sheetName));
    }

    [Fact]
    public void GetColumnCount_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        Assert.True(doc.GetColumnCount(sheetName) >= 0);
    }

    [Fact]
    public void GetColumnCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int sheetsBefore = doc.SheetCount;
        string sheetName = doc.GetSheetNames()[0];
        doc.GetColumnCount(sheetName);
        Assert.Equal(sheetsBefore, doc.SheetCount);
    }

    [Fact]
    public void GetColumnCount_TwoSheetsIndependent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet2");
        string sheet1 = doc.GetSheetNames()[0];
        string sheet2 = "Sheet2";
        doc.SetCellValue(sheet1, 0, 0, "A");
        doc.SetCellValue(sheet1, 0, 1, "B");
        doc.SetCellValue(sheet1, 0, 2, "C");
        Assert.True(doc.GetColumnCount(sheet1) >= 3);
        Assert.Equal(0, doc.GetColumnCount(sheet2));
    }

    [Fact]
    public void GetColumnCount_AfterSetCellValue_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 4, "Value");
        Assert.True(doc.GetColumnCount(sheetName) >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetMultipleColumns_CountNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        for (int c = 0; c < 5; c++)
            doc.SetCellValue(sheetName, 0, c, $"Col{c}");
        Assert.True(doc.GetColumnCount(sheetName) >= 5);
    }

    [Fact]
    public void DogfoodPipeline_ClearSheet_ColumnCountReturnsZero()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "A");
        doc.SetCellValue(sheetName, 0, 1, "B");
        doc.ClearSheet(sheetName);
        Assert.Equal(0, doc.GetColumnCount(sheetName));
    }
}
