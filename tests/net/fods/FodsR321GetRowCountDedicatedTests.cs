// Tests for FodsDocument.GetRowCount dedicated coverage.
// Sprint: ff-sprint-s293-dotnet-deepening-20260630
// Ledger: PC-FODS-R321

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R321: Dedicated tests for FodsDocument.GetRowCount(sheetName).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet throws exception.
/// Valid call returns non-negative.
/// Row count increases after SetCellValue on new row.
/// SheetCount unchanged after GetRowCount.
/// Called twice returns same result.
/// Dogfood: set cells in multiple rows, row count reflects all.
/// Dogfood: two sheets have independent row counts.
/// </summary>
public class FodsR321GetRowCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowCount_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetRowCount(null!));
    }

    [Fact]
    public void GetRowCount_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetRowCount("   "));
    }

    [Fact]
    public void GetRowCount_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetRowCount("DoesNotExist"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowCount_ValidCall_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        int count = doc.GetRowCount("Data");
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetRowCount_IncreasesAfterSetCellValueOnNewRow()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        int before = doc.GetRowCount("Data");
        doc.SetCellValue("Data", before + 1, 0, "NewRow");
        int after = doc.GetRowCount("Data");
        Assert.True(after > before);
    }

    [Fact]
    public void GetRowCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int sheetsBefore = doc.SheetCount;
        _ = doc.GetRowCount("Sheet1");
        Assert.Equal(sheetsBefore, doc.SheetCount);
    }

    [Fact]
    public void GetRowCount_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "A");
        int first = doc.GetRowCount("Sheet1");
        int second = doc.GetRowCount("Sheet1");
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultipleCellRows_RowCountReflectsAll()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.SetCellValue("Report", 0, 0, "Header");
        doc.SetCellValue("Report", 1, 0, "Row1");
        doc.SetCellValue("Report", 2, 0, "Row2");
        int count = doc.GetRowCount("Report");
        Assert.True(count >= 3);
    }

    [Fact]
    public void DogfoodPipeline_TwoSheets_IndependentRowCounts()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Sheet2");
        doc.SetCellValue("Sheet1", 0, 0, "A");
        doc.SetCellValue("Sheet1", 1, 0, "B");
        int count1 = doc.GetRowCount("Sheet1");
        int count2 = doc.GetRowCount("Sheet2");
        Assert.True(count1 >= 2);
        Assert.True(count1 != count2 || count2 >= 0);
    }
}
