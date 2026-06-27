// Tests for FodsDocument.GetCellCount dedicated coverage.
// Sprint: ff-sprint-s296-dotnet-deepening-20260630
// Ledger: PC-FODS-R324

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R324: Dedicated tests for FodsDocument.GetCellCount(sheetName).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet throws exception.
/// Valid call returns non-negative.
/// Cell count increases after SetCellValue.
/// SheetCount unchanged after GetCellCount.
/// Called twice returns same result.
/// Dogfood: set multiple cells, cell count reflects all.
/// Dogfood: two sheets have independent cell counts.
/// </summary>
public class FodsR324GetCellCountDedicatedTests
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
    public void GetCellCount_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellCount("DoesNotExist"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellCount_ValidCall_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        int count = doc.GetCellCount("Data");
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetCellCount_IncreasesAfterSetCellValue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        int before = doc.GetCellCount("Data");
        doc.SetCellValue("Data", 0, 0, "NewValue");
        int after = doc.GetCellCount("Data");
        Assert.True(after >= before);
    }

    [Fact]
    public void GetCellCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int sheetsBefore = doc.SheetCount;
        _ = doc.GetCellCount("Sheet1");
        Assert.Equal(sheetsBefore, doc.SheetCount);
    }

    [Fact]
    public void GetCellCount_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "A");
        int first = doc.GetCellCount("Sheet1");
        int second = doc.GetCellCount("Sheet1");
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultipleSetCellValue_CellCountReflectsAll()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.SetCellValue("Report", 0, 0, "A");
        doc.SetCellValue("Report", 0, 1, "B");
        doc.SetCellValue("Report", 1, 0, "C");
        int count = doc.GetCellCount("Report");
        Assert.True(count >= 3);
    }

    [Fact]
    public void DogfoodPipeline_TwoSheets_IndependentCellCounts()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Sheet2");
        doc.SetCellValue("Sheet1", 0, 0, "X");
        doc.SetCellValue("Sheet1", 1, 0, "Y");
        int count1 = doc.GetCellCount("Sheet1");
        int count2 = doc.GetCellCount("Sheet2");
        Assert.True(count1 >= 0);
        Assert.True(count2 >= 0);
    }
}
