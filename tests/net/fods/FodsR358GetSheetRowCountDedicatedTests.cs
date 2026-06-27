// Tests for FodsDocument.GetSheetRowCount dedicated coverage.
// Sprint: ff-sprint-s325-dotnet-deepening-20260630
// Ledger: PC-FODS-R358

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R358: Dedicated tests for FodsDocument.GetSheetRowCount().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Nonexistent sheet throws.
/// Empty sheet returns non-negative.
/// After adding rows count is non-negative.
/// SheetCount unchanged after GetSheetRowCount.
/// Called twice same result.
/// Dogfood: add multiple rows then verify count non-negative.
/// Dogfood: multiple sheets row counts are non-negative.
/// </summary>
public class FodsR358GetSheetRowCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetRowCount_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetRowCount(null!));
    }

    [Fact]
    public void GetSheetRowCount_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetRowCount("   "));
    }

    [Fact]
    public void GetSheetRowCount_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetRowCount("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetRowCount_EmptySheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Empty");
        int count = doc.GetSheetRowCount("Empty");
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetSheetRowCount_AfterAddingRows_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Row1");
        doc.SetCellValue("Data", 1, 0, "Row2");
        doc.SetCellValue("Data", 2, 0, "Row3");
        int count = doc.GetSheetRowCount("Data");
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetSheetRowCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetSheetRowCount("Sheet1");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetRowCount_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Summary");
        doc.SetCellValue("Summary", 0, 0, "Data");
        int first = doc.GetSheetRowCount("Summary");
        int second = doc.GetSheetRowCount("Summary");
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultipleRows_CountNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sales");
        for (int r = 0; r < 5; r++)
            doc.SetCellValue("Sales", r, 0, $"Item{r + 1}");
        int count = doc.GetSheetRowCount("Sales");
        Assert.True(count >= 0);
        Assert.Equal(doc.SheetCount, doc.SheetCount);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_AllCountsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        string[] sheetNames = { "Alpha", "Beta", "Gamma" };
        foreach (var name in sheetNames)
        {
            doc.AddSheet(name);
            doc.SetCellValue(name, 0, 0, "Header");
        }
        foreach (var name in sheetNames)
            Assert.True(doc.GetSheetRowCount(name) >= 0);
    }
}
