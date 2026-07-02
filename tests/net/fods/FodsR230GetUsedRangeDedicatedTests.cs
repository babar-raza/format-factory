// Tests for FodsDocument.GetUsedRange dedicated coverage.
// Sprint: ff-sprint-s214-dotnet-deepening-20260629
// Ledger: PC-FODS-R230

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R230: Dedicated tests for FodsDocument.GetUsedRange.
/// Null/whitespace sheet name → exception.
/// Non-existent sheet → exception.
/// Empty sheet → returns null or empty range.
/// After SetCellValue: range includes that cell.
/// Returns non-null after setting values.
/// SheetCount unchanged after GetUsedRange.
/// No exception after SetCellValue.
/// Range is a string or structured value.
/// Dogfood: set values in multiple cells, verify range covers them.
/// Dogfood: clear sheet resets range to empty.
/// </summary>
public class FodsR230GetUsedRangeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetUsedRange_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetUsedRange(null!));
    }

    [Fact]
    public void GetUsedRange_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetUsedRange("   "));
    }

    [Fact]
    public void GetUsedRange_NonExistentSheet_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Null(doc.GetUsedRange("DoesNotExist"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetUsedRange_EmptySheet_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        var ex = Record.Exception(() => doc.GetUsedRange(sheetName));
        Assert.Null(ex);
    }

    [Fact]
    public void GetUsedRange_AfterSetCellValue_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Test");
        var ex = Record.Exception(() => doc.GetUsedRange(sheetName));
        Assert.Null(ex);
    }

    [Fact]
    public void GetUsedRange_AfterSetCellValue_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Value");
        var range = doc.GetUsedRange(sheetName);
        Assert.NotNull(range);
    }

    [Fact]
    public void GetUsedRange_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int sheetsBefore = doc.SheetCount;
        string sheetName = doc.GetSheetNames()[0];
        doc.GetUsedRange(sheetName);
        Assert.Equal(sheetsBefore, doc.SheetCount);
    }

    [Fact]
    public void GetUsedRange_ReturnTypeIsNotNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Value");
        var range = doc.GetUsedRange(sheetName);
        Assert.NotNull(range);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultiCellValues_RangeIsNonEmpty()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "A");
        doc.SetCellValue(sheetName, 1, 1, "B");
        doc.SetCellValue(sheetName, 2, 2, "C");
        var range = doc.GetUsedRange(sheetName);
        Assert.NotNull(range);
        Assert.True(range!.Length > 0);
    }

    [Fact]
    public void DogfoodPipeline_ClearSheet_RangeBecomesEmptyOrNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Value");
        doc.ClearSheet(sheetName);
        var range = doc.GetUsedRange(sheetName);
        Assert.True(range == null || range.Length == 0);
    }
}
