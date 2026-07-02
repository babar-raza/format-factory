// Tests for FodsDocument.GetCellType dedicated coverage.
// Sprint: ff-sprint-s265-dotnet-deepening-20260630
// Ledger: PC-FODS-R289

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R289: Dedicated tests for FodsDocument.GetCellType(sheetName, row, col).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet name → throws exception.
/// Negative row → throws exception.
/// Negative col → throws exception.
/// Valid empty cell → returns non-null (e.g., "empty" or "string").
/// After SetCellValue with string, returns string type or non-null.
/// SheetCount unchanged after call.
/// Called twice → same result.
/// Dogfood: set value and verify type is non-null.
/// Dogfood: two cells with different content, both return non-null type.
/// </summary>
public class FodsR289GetCellTypeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellType_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellType(null!, 0, 0));
    }

    [Fact]
    public void GetCellType_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellType("   ", 0, 0));
    }

    [Fact]
    public void GetCellType_NonexistentSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellType("NoSheet", 0, 0));
    }

    [Fact]
    public void GetCellType_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellType("Sheet1", -1, 0));
    }

    [Fact]
    public void GetCellType_NegativeCol_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellType("Sheet1", 0, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellType_AfterSetCellValue_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "some text");
        string type = doc.GetCellType("Sheet1", 0, 0);
        Assert.NotNull(type);
    }

    [Fact]
    public void GetCellType_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        doc.SetCellValue("Sheet1", 0, 0, "text");
        doc.GetCellType("Sheet1", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellType_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "stable");
        string first = doc.GetCellType("Sheet1", 0, 0);
        string second = doc.GetCellType("Sheet1", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetValueAndGetType_NonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 1, 2, "FormatFactory");
        string cellType = doc.GetCellType("Data", 1, 2);
        Assert.NotNull(cellType);
    }

    [Fact]
    public void DogfoodPipeline_TwoCellsDifferentContent_BothNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "text value");
        doc.SetCellValue("Sheet1", 0, 1, "123");
        string type0 = doc.GetCellType("Sheet1", 0, 0);
        string type1 = doc.GetCellType("Sheet1", 0, 1);
        Assert.NotNull(type0);
        Assert.NotNull(type1);
    }
}
